# orchestration/assets.py
from dagster import asset, AssetExecutionContext
from pathlib import Path
from pipeline.spatial_processor import process_and_ingest_raster

DB_CONFIG = {
    "dbname": "avalanche_vision",
    "user": "gis_admin",
    "password": "enterprise_secure_password",
    "host": "localhost",
    "port": 5432
}

@asset(group_name="ingestion")
def raw_sar_data():
    """Validates presence of raw Sentinel-1 SAR input files."""
    path = Path("data/processed/ml_feature_stack_10band.tif")
    assert path.exists(), f"Feature stack not found at {path}"
    return str(path)

@asset(deps=[raw_sar_data], group_name="postgis_vectorization")
def vectorized_postgis_layer(context: AssetExecutionContext):
    """Orchestrates raster vectorization and stream ingestion to PostgreSQL/PostGIS."""
    risk_map = Path("data/processed/avalanche_risk_map.tif")
    feature_stack = Path("data/processed/ml_feature_stack_10band.tif")
    
    count = process_and_ingest_raster(
        feature_stack_path=feature_stack,
        risk_map_path=risk_map,
        db_config=DB_CONFIG,
        threshold=0.50
    )
    
    context.add_output_metadata({"ingested_polygons": count})
    return count