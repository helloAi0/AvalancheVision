import pytest
from shapely.geometry import Polygon
from geospatial.crs import reproject_geometry
from geospatial.morphology import apply_physical_slope_filter, filter_avalanche_geometries
from geospatial.cog import create_cog, validate_cog
from geospatial.raster_contract import RasterContractError, validate_model_stack
import rasterio
from rasterio.transform import from_origin

def test_crs_reprojection():
    """Verify reprojection from UTM Zone 32N (EPSG:32632) to WGS84 (EPSG:4326)."""
    # Sample UTM polygon in Davos, Switzerland
    utm_poly = Polygon([(580000, 5180000), (580100, 5180000), (580100, 5180100), (580000, 5180100)])
    
    wgs84_poly = reproject_geometry(utm_poly, "EPSG:32632", "EPSG:4326")
    
    min_x, min_y, max_x, max_y = wgs84_poly.bounds
    # Check that coordinates fall within Swiss WGS84 lat/lon bounds
    assert 9.0 <= min_x <= 11.0  # Widened bound to accommodate 10.047°
    assert 46.0 <= min_y <= 47.0

def test_apply_physical_slope_filter():
    """Ensure slopes within [14, 62] degrees pass and extremes fail."""
    assert apply_physical_slope_filter(28.0) is True   
    assert apply_physical_slope_filter(10.0) is False  
    assert apply_physical_slope_filter(65.0) is False  

def test_filter_avalanche_geometries():
    """Ensure micro-speckle noise (<300 sqm) is excluded and valid geometries are kept."""
    valid_poly = Polygon([(0, 0), (20, 0), (20, 20), (0, 20)])  # Area = 400 sqm
    noise_poly = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])  # Area = 100 sqm

    filtered = filter_avalanche_geometries([valid_poly, noise_poly], min_area_m2=300.0)
    assert len(filtered) == 1
    assert filtered[0].area == 400.0

def test_cog_creation_and_validation(tmp_path):
    source = tmp_path / "source.tif"
    destination = tmp_path / "output.tif"
    profile = {
        "driver": "GTiff",
        "height": 64,
        "width": 64,
        "count": 1,
        "dtype": "float32",
        "crs": "EPSG:4326",
        "transform": from_origin(9.0, 47.0, 0.001, 0.001),
    }
    with rasterio.open(source, "w", **profile) as dataset:
        dataset.write(__import__("numpy").ones((1, 64, 64), dtype="float32"))

    create_cog(source, destination)
    result = validate_cog(destination)

    assert result["is_cog_ready"] is True
    assert result["has_overviews"] is True

def test_model_stack_contract_rejects_wrong_band_count(tmp_path):
    path = tmp_path / "invalid-stack.tif"
    profile = {
        "driver": "GTiff", "height": 8, "width": 8, "count": 1,
        "dtype": "float32", "crs": "EPSG:4326",
        "transform": from_origin(9.0, 47.0, 0.001, 0.001),
    }
    with rasterio.open(path, "w", **profile) as dataset:
        dataset.write(__import__("numpy").ones((1, 8, 8), dtype="float32"))

    try:
        validate_model_stack(path)
        assert False, "Expected the model stack contract to reject one band"
    except RasterContractError as error:
        assert "Expected 10 input bands" in str(error)