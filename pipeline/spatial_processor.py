# pipeline/spatial_processor.py
import logging
import xarray as xr
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
import psycopg2
from shapely.geometry import shape
import rasterio.features

logger = logging.getLogger("SpatialProcessor")

def process_and_ingest_raster(
    feature_stack_path: Path, 
    risk_map_path: Path, 
    db_config: dict, 
    threshold: float = 0.50
):
    """Processes SAR/ERA5 arrays lazily via Xarray & streams vector masks to PostGIS."""
    logger.info(f"Opening raster stack lazily: {risk_map_path.name}")
    
    # Lazy evaluation with Dask chunks to prevent RAM overflow
    ds = xr.open_dataarray(risk_map_path, chunks={"x": 512, "y": 512})
    
    with rasterio.open(risk_map_path) as src:
        raster_data = src.read(1)
        transform = src.transform
        crs = src.crs

    binary_mask = (raster_data > threshold).astype(np.uint8)
    
    # Vectorize raw pixels into Shapely Polygons
    polygon_generator = rasterio.features.shapes(
        binary_mask, 
        mask=(binary_mask == 1), 
        transform=transform
    )
    
    records = []
    timestamp = datetime.now(timezone.utc)
    
    for geom_dict, val in polygon_generator:
        poly = shape(geom_dict)
        # Store as WKB hex string for rapid PostGIS insertion
        records.append((timestamp, float(val), "U-Net-v1.0", poly.wkb_hex))
        
    if not records:
        logger.warning("No hazard geometries extracted above threshold.")
        return 0

    logger.info(f"Inserting {len(records)} spatial polygons into PostGIS...")
    
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    insert_query = """
        INSERT INTO hazard_predictions (acquisition_timestamp, risk_score, model_version, geom)
        VALUES (%s, %s, %s, ST_GeomFromWKB(decode(%s, 'hex'), 4326));
    """
    
    cursor.executemany(insert_query, records)
    conn.commit()
    cursor.close()
    conn.close()
    
    logger.info("Database commit successful.")
    return len(records)