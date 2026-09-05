"""Pydantic schemas for system health, AOI definitions, and capabilities."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RegionOfInterest(BaseModel):
    id: str = Field(..., description="AOI key, e.g. davos-fluela")
    name: str = Field(..., description="Full region title")
    country: str = Field(default="Switzerland")
    mountain_range: str = Field(default="Alps (Graubünden)")
    center_lon: float = Field(default=9.83)
    center_lat: float = Field(default=46.80)
    default_zoom: int = Field(default=12)
    bbox_wgs84: List[float] = Field(default_factory=lambda: [9.75, 46.75, 9.90, 46.88])
    utm_epsg: int = Field(default=32632)
    dem_coverage: bool = Field(default=True)
    sar_coverage: bool = Field(default=True)
    era5_coverage: bool = Field(default=True)


class SystemHealthResponse(BaseModel):
    status: str = Field(default="HEALTHY")
    version: str = Field(default="1.0.0")
    pytorch_version: str
    device: str
    cuda_available: bool
    database_status: str
    database_type: str
    active_aoi: RegionOfInterest
    storage_status: Dict[str, bool]
    active_model: str
