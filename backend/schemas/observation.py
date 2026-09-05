"""Pydantic schemas for Sentinel-1 SAR observations and STAC catalog granules."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SARObservation(BaseModel):
    id: str = Field(..., description="Unique SAR Granule Product ID")
    scene_name: str = Field(..., description="Sentinel-1 SAFE package title")
    satellite: str = Field(default="Sentinel-1A")
    instrument: str = Field(default="C-SAR")
    sensor_mode: str = Field(default="IW", description="Interferometric Wide Swath")
    product_type: str = Field(default="GRD", description="Ground Range Detected")
    polarization: List[str] = Field(default_factory=lambda: ["VV", "VH"])
    acquisition_date: str = Field(..., description="Acquisition datetime ISO8601")
    orbit_direction: str = Field(..., description="ASCENDING or DESCENDING")
    relative_orbit: Optional[int] = Field(default=None, description="Track / Relative Orbit Number")
    absolute_orbit: Optional[int] = Field(default=None)
    pixel_spacing_m: float = Field(default=10.0)
    status: str = Field(default="AVAILABLE", description="AVAILABLE, DOWNLOADED, PROCESSED")
    file_size_gb: float = Field(default=1.6)
    local_path: Optional[str] = None
    bbox: List[float] = Field(..., description="[min_lon, min_lat, max_lon, max_lat]")
    footprint_geojson: Optional[Dict[str, Any]] = None


class ObservationListResponse(BaseModel):
    total_count: int
    observations: List[SARObservation]
    active_aoi: str
    last_catalog_sync: str


class CoRegisteredPairResponse(BaseModel):
    pair_id: str
    event_reference_date: str
    pre_event_scene: SARObservation
    post_event_scene: SARObservation
    temporal_baseline_days: int
    coregistration_status: str
