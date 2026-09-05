import logging
import torch
import rasterio
import numpy as np
from pathlib import Path

# Import the U-Net architecture from your training script
from ml.models.train_unet import UNet

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def generate_prediction_map(feature_path: Path, model_path: Path, output_path: Path, patch_size: int = 256):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Executing inference on device: {device}")

    # Initialize model and load trained weights
    model = UNet(in_channels=10, out_channels=1).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval() # Set to evaluation mode

    logger.info(f"Loading full region feature stack: {feature_path.name}")
    with rasterio.open(feature_path) as src:
        meta = src.meta.copy()
        img_data = src.read() 
        _, height, width = img_data.shape

    # Clean any NaN values introduced during reprojection
    img_data = np.nan_to_num(img_data, nan=0.0).astype(np.float32)
    pred_map = np.zeros((height, width), dtype=np.float32)
    
    logger.info("Running sliding window inference...")
    
    # Process the image in chunks to prevent memory overload
    with torch.no_grad():
        for y in range(0, height, patch_size):
            for x in range(0, width, patch_size):
                
                y_end = min(y + patch_size, height)
                x_end = min(x + patch_size, width)
                
                patch = img_data[:, y:y_end, x:x_end]
                
                # Pad edges if the patch is smaller than the required 256x256 window
                pad_y = patch_size - patch.shape[1]
                pad_x = patch_size - patch.shape[2]
                
                if pad_y > 0 or pad_x > 0:
                    patch = np.pad(patch, ((0, 0), (0, pad_y), (0, pad_x)), mode='reflect')
                    
                # Convert to tensor and add batch dimension: Shape (1, 10, 256, 256)
                patch_tensor = torch.from_numpy(patch).unsqueeze(0).to(device)
                
                # Forward pass and apply sigmoid to convert logits to probabilities
                output = model(patch_tensor)
                prob = torch.sigmoid(output).squeeze().cpu().numpy()
                
                # Crop padded areas out of the result
                valid_prob = prob[:(patch_size - pad_y), :(patch_size - pad_x)]
                
                # Stitch back into the master prediction map
                pred_map[y:y_end, x:x_end] = valid_prob

    # Update metadata for a single-band probability output
    meta.update(count=1, dtype=rasterio.float32)
    
    logger.info(f"Saving avalanche risk map to: {output_path}")
    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(pred_map, 1)
        
    logger.info("Inference complete! Map ready for GIS visualization.")

if __name__ == "__main__":
    feature_tif = Path("data/processed/ml_feature_stack_10band.tif")
    model_weights = Path("data/processed/unet_avalanche.pth")
    output_pred = Path("data/processed/avalanche_risk_map.tif")
    
    # Ensure the output directory exists
    output_pred.parent.mkdir(parents=True, exist_ok=True)
    
    generate_prediction_map(feature_tif, model_weights, output_pred)