"""Inference service executing sliding-window U-Net segmentation over 10-band satellite raster tiles."""

import logging
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
import rasterio
import torch
from ml.models.train_unet import UNet
from backend.core.config import settings
from geospatial.raster_contract import validate_model_stack

logger = logging.getLogger("AvalancheVision.InferenceService")


class InferenceService:
    def __init__(self, checkpoint_path: Optional[Path] = None):
        self.checkpoint_path = checkpoint_path or (settings.DATA_PROCESSED_DIR / "unet_avalanche.pth")
        self._model: Optional[UNet] = None
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def _get_model(self) -> UNet:
        if self._model is None:
            logger.info(f"Loading U-Net weights from {self.checkpoint_path} on {self._device}...")
            model = UNet(in_channels=10, out_channels=1).to(self._device)
            if self.checkpoint_path.exists():
                state = torch.load(self.checkpoint_path, map_location=self._device)
                model.load_state_dict(state)
            model.eval()
            self._model = model
        return self._model

    def run_sliding_window_inference(
        self,
        feature_stack_path: Path,
        output_risk_map_path: Path,
        patch_size: int = 256,
        overlap: int = 32
    ) -> Path:
        """Executes sliding-window inference with spatial overlap blending to eliminate edge seam artifacts."""
        contract = validate_model_stack(feature_stack_path, expected_bands=10)
        model = self._get_model()
        logger.info("Executing tile inference on %s (%sx%s, %s bands)", feature_stack_path.name, contract["width"], contract["height"], contract["bands"])

        with rasterio.open(feature_stack_path) as src:
            meta = src.meta.copy()
            features = src.read().astype(np.float32)  # Shape: (10, H, W)
            height, width = features.shape[1], features.shape[2]

        # Standardize non-zero features per-band
        for i in range(features.shape[0]):
            band = features[i]
            valid = ~np.isnan(band) & (band != 0.0)
            if valid.any():
                m, s = float(band[valid].mean()), float(band[valid].std())
                features[i] = np.where(valid, (band - m) / (s + 1e-6), 0.0)

        pred_accumulator = np.zeros((height, width), dtype=np.float32)
        count_accumulator = np.zeros((height, width), dtype=np.float32)

        stride = patch_size - overlap

        with torch.no_grad():
            for y in range(0, height, stride):
                for x in range(0, width, stride):
                    y_end = min(y + patch_size, height)
                    x_end = min(x + patch_size, width)
                    y_start = max(0, y_end - patch_size)
                    x_start = max(0, x_end - patch_size)

                    patch = features[:, y_start:y_end, x_start:x_end]

                    # Pad if smaller than patch size
                    pad_y = patch_size - patch.shape[1]
                    pad_x = patch_size - patch.shape[2]
                    if pad_y > 0 or pad_x > 0:
                        patch = np.pad(patch, ((0, 0), (0, pad_y), (0, pad_x)), mode="reflect")

                    patch_tensor = torch.from_numpy(patch).unsqueeze(0).to(self._device)
                    logits = model(patch_tensor)
                    probs = torch.sigmoid(logits).squeeze().cpu().numpy()

                    valid_probs = probs[: (patch_size - pad_y), : (patch_size - pad_x)]
                    pred_accumulator[y_start:y_end, x_start:x_end] += valid_probs
                    count_accumulator[y_start:y_end, x_start:x_end] += 1.0

        # Average overlapping windows
        count_accumulator = np.maximum(count_accumulator, 1.0)
        final_risk_map = pred_accumulator / count_accumulator

        # Write output raster GeoTIFF
        meta.update(count=1, dtype=rasterio.float32, nodata=0.0)
        output_risk_map_path.parent.mkdir(parents=True, exist_ok=True)

        with rasterio.open(output_risk_map_path, "w", **meta) as dst:
            dst.write(final_risk_map.astype(np.float32), 1)

        logger.info(f"Inference complete. Risk map written to: {output_risk_map_path}")
        return output_risk_map_path


inference_service = InferenceService()
