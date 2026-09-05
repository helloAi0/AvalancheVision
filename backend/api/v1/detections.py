"""FastAPI endpoints for querying and inspecting avalanche deposit detection polygons."""

import logging
from typing import Literal, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

# Import your new high-performance async database dependency hook
from backend.repositories.database import get_async_db
from backend.services.detection_service import detection_service
from backend.schemas.detection import (
    DetectionGeoJSON,
    DetectionFeature,
    DetectionSummaryStats,
    DetectionFilterParams,
)
from backend.services.export_service import export_service

logger = logging.getLogger("AvalancheVision.API.Detections")
router = APIRouter(prefix="/detections", tags=["Detections & Spatial Mapping"])


@router.get("/export")
def export_detection_vector(
    format: Literal["geojson", "kml", "shapefile"] = Query(default="geojson")
):
    """Exports current detection vectors for agency GIS workflows."""
    exporters = {
        "geojson": (export_service.export_geojson_bytes, "application/geo+json", "detections.geojson"),
        "kml": (export_service.export_kml_bytes, "application/vnd.google-earth.kml+xml", "detections.kml"),
        "shapefile": (export_service.export_shapefile_zip, "application/zip", "detections_shapefile.zip"),
    }
    exporter, media_type, filename = exporters[format]
    return Response(
        content=exporter(),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/geojson", response_model=DetectionGeoJSON, status_code=status.HTTP_200_OK)
async def get_detections_geojson(
    min_confidence: Optional[float] = Query(default=0.45, ge=0.0, le=1.0, description="Minimum confidence filter"),
    min_area_ha: Optional[float] = Query(default=0.0, ge=0.0, description="Minimum area in hectares"),
    min_slope_deg: Optional[float] = Query(default=None, ge=0.0, le=90.0, description="Minimum slope angle"),
    max_slope_deg: Optional[float] = Query(default=None, ge=0.0, le=90.0, description="Maximum slope angle"),
    aspect: Optional[str] = Query(default=None, description="Compass aspect filter (e.g., N, NE, E, SE, S, SW, W, NW)"),
    bbox: Optional[str] = Query(default=None, description="Bounding box filter as 'min_lon,min_lat,max_lon,max_lat'"),
    start_date: Optional[str] = Query(default=None, description="Inclusive T1 acquisition date"),
    end_date: Optional[str] = Query(default=None, description="Inclusive T2 acquisition date"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Streams standards-compliant WGS84 GeoJSON FeatureCollection of avalanche deposit polygons 
    with rich zonal statistics out of the production spatial database.
    """
    filters = DetectionFilterParams(
        min_confidence=min_confidence,
        min_area_ha=min_area_ha,
        min_slope_deg=min_slope_deg,
        max_slope_deg=max_slope_deg,
        aspect=aspect,
        bbox=bbox,
        start_date=start_date,
        end_date=end_date,
    )
    
    # Non-blocking async execution layer using your real data service
    # (Note: if your detection_service isn't fully async yet, remove the await keyword)
    return detection_service.get_geojson(filters=filters, db=db)


@router.get("/stats", response_model=DetectionSummaryStats, status_code=status.HTTP_200_OK)
async def get_detection_summary_statistics(db: AsyncSession = Depends(get_async_db)):
    """Returns aggregated scientific statistics across the active Region of Interest (ROI) asynchronously."""
    return detection_service.get_stats(db=db)


@router.get("/{detection_id}", response_model=DetectionFeature, status_code=status.HTTP_200_OK)
async def get_single_detection_detail(detection_id: str, db: AsyncSession = Depends(get_async_db)):
    """
    Fetches detailed geometry, SAR backscatter drop, DEM terrain metrics, and 
    ERA5 weather context for a specific detection.
    """
    feature = await detection_service.get_detection_detail(detection_id, db=db)
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Detection with ID '{detection_id}' not found."
        )
    return feature
