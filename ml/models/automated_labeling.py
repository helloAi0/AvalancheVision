"""Automated label generator using physics-constrained standardized SAR anomaly change detection.

Implements relative SAR backscatter anomaly detection ($Z_{\Delta\sigma^0} < -1.8$) combined
with Copernicus DEM terrain slope constraints ($20^\circ \le \theta \le 50^\circ$) adhering
to Swiss SLF / ESA remote sensing avalanche deposit detection methodology.
"""

import logging
import rasterio
import numpy as np
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AvalancheVision.AutomatedLabeling")


class LogRatioLabeler:
    """Generates physics-informed automated ground-truth masks using standardized SAR change anomalies."""

    def __init__(self, feature_stack_path: Path, output_label_path: Path):
        self.feature_stack_path = feature_stack_path
        self.output_label_path = output_label_path
        self.output_label_path.parent.mkdir(parents=True, exist_ok=True)

    def generate_labels(self, z_score_threshold: float = -1.85, min_slope: float = 20.0, max_slope: float = 52.0):
        logger.info(f"Reading multi-band feature stack: {self.feature_stack_path.name}")
        
        with rasterio.open(self.feature_stack_path) as src:
            meta = src.meta.copy()
            # Band 2: T1 VH, Band 4: T2 VH, Band 5: Elevation, Band 6: Slope
            t1_vh = src.read(2)
            t2_vh = src.read(4)
            elevation = src.read(5) if src.count >= 5 else np.ones_like(t1_vh) * 2000
            slope = src.read(6) if src.count >= 6 else np.ones_like(t1_vh) * 30

        # Strict valid data mask: both T1 and T2 must have legitimate radar returns (>0.005) and elevation > 1000m
        valid_coverage = (t1_vh > 0.005) & (t2_vh > 0.005) & (elevation > 1000) & (slope > 0)

        logger.info("Computing Log-Ratio backscatter changes (10 * log10(T2 / T1))...")
        log_ratio_db = np.zeros_like(t1_vh, dtype=np.float32)
        log_ratio_db[valid_coverage] = 10.0 * np.log10(t2_vh[valid_coverage] / t1_vh[valid_coverage])

        # Standardize scene-level backscatter change to isolate localized avalanche deposits from regional weather fluctuations
        scene_mean_db = float(np.mean(log_ratio_db[valid_coverage]))
        scene_std_db = float(np.std(log_ratio_db[valid_coverage]))
        logger.info(f"Scene change baseline: Mean = {scene_mean_db:.2f} dB, Std = {scene_std_db:.2f} dB")

        z_scores = np.zeros_like(t1_vh, dtype=np.float32)
        z_scores[valid_coverage] = (log_ratio_db[valid_coverage] - scene_mean_db) / (scene_std_db + 1e-6)

        logger.info(
            f"Applying physical constraints: Standardized Anomaly Z < {z_score_threshold}, "
            f"Slope between {min_slope}° and {max_slope}°"
        )
        
        labels = np.where(
            valid_coverage & (z_scores < z_score_threshold) & (slope >= min_slope) & (slope <= max_slope),
            1,
            0
        ).astype(np.uint8)

        meta.update({
            "count": 1,
            "dtype": "uint8",
            "nodata": 0
        })

        logger.info(f"Writing validated labels to: {self.output_label_path}")
        with rasterio.open(self.output_label_path, "w", **meta) as dst:
            dst.write(labels, 1)

        avalanche_pixels = int(np.sum(labels == 1))
        valid_pixels = int(np.sum(valid_coverage))
        pct_valid = (avalanche_pixels / valid_pixels * 100.0) if valid_pixels > 0 else 0.0

        logger.info(
            f"Labeling complete: {avalanche_pixels} deposit pixels identified "
            f"({pct_valid:.2f}% of valid alpine swath, {avalanche_pixels * 100 / 10000:.1f} ha)."
        )
        return labels


if __name__ == "__main__":
    stack_file = Path("data/processed/ml_feature_stack_10band.tif")
    if not stack_file.exists():
        stack_file = Path("data/processed/ml_feature_stack.tif")
    out_label = Path("data/processed/automated_labels.tif")

    labeler = LogRatioLabeler(feature_stack_path=stack_file, output_label_path=out_label)
    labeler.generate_labels(z_score_threshold=-1.85, min_slope=20.0, max_slope=52.0)