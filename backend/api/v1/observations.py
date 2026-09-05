"""FastAPI endpoints for Sentinel-1 SAR observations catalog and co-registered pair retrieval."""

from typing import Optional
from fastapi import APIRouter, Query
from backend.services.observation_service import observation_service
from backend.schemas.observation import (
    ObservationListResponse,
    CoRegisteredPairResponse,
)

router = APIRouter(prefix="/observations", tags=["Satellite Observations"])


@router.get("", response_model=ObservationListResponse)
def list_sar_observations(
    satellite: Optional[str] = Query(default=None, description="Filter by satellite (Sentinel-1A / Sentinel-1B)"),
    orbit_direction: Optional[str] = Query(default=None, description="Filter by pass (ASCENDING / DESCENDING)"),
    status: Optional[str] = Query(default=None, description="Filter by status (AVAILABLE / PROCESSED)"),
    live: bool = Query(default=False, description="Query the Copernicus STAC provider instead of local inventory"),
    bbox: Optional[str] = Query(default=None, description="Optional WGS84 bbox: min_lon,min_lat,max_lon,max_lat"),
    start_date: str = Query(default="2024-01-01", description="STAC search start date"),
    end_date: str = Query(default="2024-01-31", description="STAC search end date"),
):
    """Lists Sentinel-1 SAR observations covering the active AOI with spatial bounding footprints and orbit metadata."""
    return observation_service.list_observations(
        satellite=satellite,
        orbit_direction=orbit_direction,
        status=status,
        live=live,
        bbox=[float(value) for value in bbox.split(",")] if bbox else None,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/pair", response_model=CoRegisteredPairResponse)
def get_coregistered_pair(
    event_date: str = Query(default="2024-01-10", description="Event reference date (YYYY-MM-DD)")
):
    """Resolves optimal co-registered pre-event (T1) and post-event (T2) SAR granules matching orbit pass and geometry."""
    return observation_service.get_coregistered_pair(event_date=event_date)
