"""Cloud Optimized GeoTIFF creation and structural validation."""

from pathlib import Path
from typing import Dict

import rasterio
from rasterio.enums import Resampling


def create_cog(source_path: Path, destination_path: Path, overview_levels=(2, 4, 8, 16)) -> Path:
    """Create a tiled, compressed GeoTIFF with internal overviews for range reads."""
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(source_path) as source:
        profile = source.profile.copy()
        profile.update(
            driver="GTiff",
            tiled=True,
            blockxsize=256,
            blockysize=256,
            compress="deflate",
            predictor=2 if source.dtypes[0].startswith("int") else 3,
            BIGTIFF="IF_SAFER",
        )
        with rasterio.open(destination_path, "w", **profile) as destination:
            destination.write(source.read())
            valid_levels = [level for level in overview_levels if min(source.width, source.height) // level >= 1]
            if valid_levels:
                destination.build_overviews(valid_levels, Resampling.nearest)
            destination.update_tags(ns="rio_overview", resampling="nearest")
    return destination_path


def validate_cog(path: Path) -> Dict[str, object]:
    """Return structural COG checks without claiming full validator certification."""
    with rasterio.open(path) as dataset:
        tiled = all(dataset.block_shapes) and all(
            shape[0] <= 512 and shape[1] <= 512 for shape in dataset.block_shapes
        )
        overview_count = len(dataset.overviews(1)) if dataset.count else 0
        return {
            "tiled": tiled,
            "has_overviews": overview_count > 0,
            "overview_count": overview_count,
            "compression": dataset.compression.value if dataset.compression else None,
            "driver": dataset.driver,
            "is_cog_ready": tiled and overview_count > 0 and dataset.driver == "GTiff",
        }
