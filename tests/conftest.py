import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
from backend.core.config import settings

@pytest.fixture
def synthetic_risk_raster(tmp_path, monkeypatch):
    """Stand-in for 'avalanche_risk_map.tif', which .gitignore excludes
    (*.tif, data/processed/*) and is therefore never present in CI."""
    monkeypatch.setattr(settings, "DATA_PROCESSED_DIR", tmp_path)

    data = np.random.default_rng(42).random((1, 32, 32)).astype("float32")
    transform = from_origin(west=545000, north=5205000, xsize=10, ysize=10)
    raster_path = tmp_path / "avalanche_risk_map.tif"
    with rasterio.open(
        raster_path, "w", driver="GTiff", height=32, width=32, count=1,
        dtype="float32", crs="EPSG:32632", transform=transform, nodata=-9999,
    ) as dst:
        dst.write(data)
        dst.update_tags(1, name="avalanche_probability", units="probability")
    return raster_path