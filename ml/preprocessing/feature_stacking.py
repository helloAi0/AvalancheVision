import logging
import rasterio
import numpy as np
from pathlib import Path
from rasterio.enums import Resampling
from rasterio.warp import reproject

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class FeatureStacker:
    """Coregisters and stacks SAR and terrain features into a single ML-ready array."""

    def __init__(self, sar_dir: Path, terrain_dir: Path, output_dir: Path):
        self.sar_dir = sar_dir
        self.terrain_dir = terrain_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def stack_features(self):
        # Locate SAR files and sort them chronologically (T1 then T2)
        sar_files = sorted(list(self.sar_dir.glob("*_ARD_*.tif")))
        if len(sar_files) != 2:
            logger.error(f"Expected exactly 2 SAR ARD files (T1 and T2). Found {len(sar_files)}.")
            return

        t1_sar_path, t2_sar_path = sar_files
        dem_path = self.terrain_dir / "davos_dem_utm.tif"
        slope_path = self.terrain_dir / "davos_slope.tif"
        aspect_path = self.terrain_dir / "davos_aspect.tif"

        # Use T2 SAR as the spatial anchor
        logger.info(f"Using {t2_sar_path.name} as the master grid.")
        with rasterio.open(t2_sar_path) as master:
            master_meta = master.meta.copy()
            t2_data = master.read()
            
        bands = []
        
        def resample_to_master(src_path: Path, resampling_method=Resampling.bilinear) -> np.ndarray:
            logger.info(f"Resampling {src_path.name} to master grid...")
            with rasterio.open(src_path) as src:
                # Initialize empty array matching the master spatial dimensions
                dest_array = np.empty(
                    (src.count, master_meta['height'], master_meta['width']), 
                    dtype=np.float32
                )
                
                reproject(
                    source=rasterio.band(src, list(range(1, src.count + 1))),
                    destination=dest_array,
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=master_meta['transform'],
                    dst_crs=master_meta['crs'],
                    resampling=resampling_method
                )
            return dest_array

        # Band 1 & 2: Pre-Event Backscatter (VV, VH)
        t1_data = resample_to_master(t1_sar_path)
        bands.extend([t1_data[0], t1_data[1]])
        
        # Band 3 & 4: Post-Event Backscatter (VV, VH)
        bands.extend([t2_data[0], t2_data[1]])

        # Band 5, 6, & 7: Terrain Features (Elevation, Slope, Aspect)
        dem_data = resample_to_master(dem_path)
        slope_data = resample_to_master(slope_path)
        aspect_data = resample_to_master(aspect_path)
        
        bands.append(dem_data[0])
        bands.append(slope_data[0])
        bands.append(aspect_data[0])

        # Configure metadata for the final multi-band stack
        stack_path = self.output_dir / "ml_feature_stack.tif"
        master_meta.update({
            "count": len(bands),
            "dtype": 'float32',
            "nodata": 0.0
        })

        logger.info(f"Writing 7-band ML feature stack to {stack_path}...")
        with rasterio.open(stack_path, 'w', **master_meta) as dst:
            for idx, band in enumerate(bands, start=1):
                # Replace inf/-inf and severe outliers with nodata representations
                band = np.nan_to_num(band, nan=0.0, posinf=0.0, neginf=0.0)
                dst.write(band.astype('float32'), idx)
                
        logger.info("Stacking complete. Dataset is ready for machine learning.")

if __name__ == "__main__":
    stacker = FeatureStacker(
        sar_dir=Path("data/interim/sar"),
        terrain_dir=Path("data/interim/terrain"),
        output_dir=Path("data/processed")
    )
    stacker.stack_features()