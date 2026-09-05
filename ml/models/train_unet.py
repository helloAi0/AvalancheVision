"""PyTorch U-Net training pipeline for 10-band multimodal satellite avalanche deposit segmentation.

Integrates Sentinel-1 SAR backscatter (T1/T2 VV/VH), Copernicus DEM terrain (elevation, slope, aspect),
and ERA5 atmospheric features with a combined Weighted BCE + Soft Dice loss function.
"""

import logging
from pathlib import Path
from typing import Tuple
import numpy as np
import rasterio
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AvalancheVision.TrainUNet")


class DiceLoss(nn.Module):
    """Soft Dice Loss for highly imbalanced binary spatial segmentation."""

    def __init__(self, smooth: float = 1.0):
        super().__init__()
        self.smooth = smooth

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        probs = torch.sigmoid(logits)
        probs_flat = probs.view(-1)
        targets_flat = targets.view(-1)

        intersection = (probs_flat * targets_flat).sum()
        dice = (2.0 * intersection + self.smooth) / (probs_flat.sum() + targets_flat.sum() + self.smooth)
        return 1.0 - dice


class CombinedBCEDiceLoss(nn.Module):
    """Combined weighted BCE + Soft Dice Loss."""

    def __init__(self, pos_weight: float = 8.0, dice_weight: float = 0.5):
        super().__init__()
        self.bce = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([pos_weight]))
        self.dice = DiceLoss()
        self.dice_weight = dice_weight

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        bce_loss = self.bce(logits, targets)
        dice_loss = self.dice(logits, targets)
        return (1.0 - self.dice_weight) * bce_loss + self.dice_weight * dice_loss


class AvalanchePatchDataset(Dataset):
    """Stratified patch extractor providing balanced positive and background training crops."""

    def __init__(
        self,
        features_path: Path,
        labels_path: Path,
        patch_size: int = 256,
        num_patches: int = 400,
        positive_ratio: float = 0.50
    ):
        self.patch_size = patch_size
        self.num_patches = num_patches
        self.positive_ratio = positive_ratio

        logger.info(f"Loading 10-band feature stack: {features_path.name}")
        with rasterio.open(features_path) as src_feat:
            self.features = src_feat.read().astype(np.float32)  # Shape: (10, H, W)
            self.height, self.width = self.features.shape[1], self.features.shape[2]

        with rasterio.open(labels_path) as src_label:
            self.labels = src_label.read(1).astype(np.float32)  # Shape: (H, W)

        self._normalize_features()

        # Locate positive pixel coordinates to guide stratified sampling
        pos_y, pos_x = np.where(self.labels == 1)
        # Filter coords that fit within patch boundaries
        valid_pos = (
            (pos_y >= self.patch_size // 2) &
            (pos_y < self.height - self.patch_size // 2) &
            (pos_x >= self.patch_size // 2) &
            (pos_x < self.width - self.patch_size // 2)
        )
        self.pos_coords = list(zip(pos_y[valid_pos], pos_x[valid_pos]))
        logger.info(f"Identified {len(self.pos_coords)} valid positive patch centroid candidates.")

    def _normalize_features(self):
        for i in range(self.features.shape[0]):
            band = self.features[i]
            valid_mask = ~np.isnan(band) & (band != 0.0)
            if valid_mask.any():
                mean = float(band[valid_mask].mean())
                std = float(band[valid_mask].std())
                self.features[i] = np.where(valid_mask, (band - mean) / (std + 1e-6), 0.0)
            else:
                self.features[i] = np.zeros_like(band)

    def __len__(self) -> int:
        return self.num_patches

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        # Stratified sampling: 50% positive crops centered on known avalanche deposits, 50% random background
        if len(self.pos_coords) > 0 and np.random.rand() < self.positive_ratio:
            cy, cx = self.pos_coords[np.random.randint(0, len(self.pos_coords))]
            y = max(0, min(self.height - self.patch_size, cy - self.patch_size // 2 + np.random.randint(-32, 33)))
            x = max(0, min(self.width - self.patch_size, cx - self.patch_size // 2 + np.random.randint(-32, 33)))
        else:
            y = np.random.randint(0, max(1, self.height - self.patch_size))
            x = np.random.randint(0, max(1, self.width - self.patch_size))

        feat_patch = self.features[:, y : y + self.patch_size, x : x + self.patch_size]
        label_patch = self.labels[y : y + self.patch_size, x : x + self.patch_size]

        # Random horizontal and vertical flips for data augmentation
        if np.random.rand() > 0.5:
            feat_patch = np.flip(feat_patch, axis=2).copy()
            label_patch = np.flip(label_patch, axis=1).copy()
        if np.random.rand() > 0.5:
            feat_patch = np.flip(feat_patch, axis=1).copy()
            label_patch = np.flip(label_patch, axis=0).copy()

        return torch.from_numpy(feat_patch), torch.from_numpy(label_patch).unsqueeze(0)


class DoubleConv(nn.Module):
    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(x)


class UNet(nn.Module):
    """Standard U-Net configured for 10-channel multimodal input and 1-channel binary logits output."""

    def __init__(self, in_channels: int = 10, out_channels: int = 1):
        super().__init__()
        self.down1 = DoubleConv(in_channels, 64)
        self.down2 = DoubleConv(64, 128)
        self.down3 = DoubleConv(128, 256)
        self.pool = nn.MaxPool2d(2)

        self.up1 = nn.ConvTranspose2d(256, 128, 2, stride=2)
        self.conv_up1 = DoubleConv(256, 128)
        self.up2 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        self.conv_up2 = DoubleConv(128, 64)

        self.out_conv = nn.Conv2d(64, out_channels, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x1 = self.down1(x)
        x2 = self.down2(self.pool(x1))
        x3 = self.down3(self.pool(x2))

        x = self.up1(x3)
        x = torch.cat([x, x2], dim=1)
        x = self.conv_up1(x)

        x = self.up2(x)
        x = torch.cat([x, x1], dim=1)
        x = self.conv_up2(x)

        return self.out_conv(x)


def train_model(
    epochs: int = 5,
    batch_size: int = 8,
    lr: float = 2e-4,
    checkpoint_path: Path = Path("data/processed/unet_avalanche.pth")
):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Training U-Net on computation device: {device}")

    features_path = Path("data/processed/ml_feature_stack_10band.tif")
    labels_path = Path("data/processed/automated_labels.tif")

    dataset = AvalanchePatchDataset(
        features_path=features_path,
        labels_path=labels_path,
        patch_size=256,
        num_patches=400,
        positive_ratio=0.50
    )
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = UNet(in_channels=10, out_channels=1).to(device)
    criterion = CombinedBCEDiceLoss(pos_weight=6.0, dice_weight=0.5).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0

        for batch_idx, (features, labels) in enumerate(dataloader):
            features, labels = features.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(features)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        scheduler.step()
        avg_loss = epoch_loss / len(dataloader)
        logger.info(f"Epoch [{epoch+1:02d}/{epochs:02d}] - Combined BCE+Dice Loss: {avg_loss:.4f}")

    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), checkpoint_path)
    logger.info(f"Training successfully completed. Model checkpoint saved to: {checkpoint_path}")


if __name__ == "__main__":
    train_model(epochs=5, batch_size=8, lr=2e-4)