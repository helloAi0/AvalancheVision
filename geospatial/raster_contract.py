"""Validation rules for model-ready geospatial raster inputs."""

from pathlib import Path
from typing import Dict

import rasterio


class RasterContractError(ValueError):
    """Raised when a raster cannot satisfy a processing contract."""


def validate_model_stack(path: Path, expected_bands: int = 10) -> Dict[str, object]:
    """Validate the structural contract required by the multimodal U-Net."""
    if not path.is_file():
        raise RasterContractError(f"Raster input does not exist: {path.name}")
    with rasterio.open(path) as dataset:
        if dataset.count != expected_bands:
            raise RasterContractError(
                f"Expected {expected_bands} input bands, received {dataset.count}."
            )
        if not dataset.crs:
            raise RasterContractError("Raster input has no CRS.")
        if dataset.width < 1 or dataset.height < 1:
            raise RasterContractError("Raster input has invalid dimensions.")
        if any(not all(abs(value) < float("inf") for value in transform) for transform in [dataset.transform]):
            raise RasterContractError("Raster transform contains non-finite values.")
        return {
            "bands": dataset.count,
            "width": dataset.width,
            "height": dataset.height,
            "crs": dataset.crs.to_string(),
            "dtype": dataset.dtypes[0],
            "nodata": dataset.nodata,
        }
