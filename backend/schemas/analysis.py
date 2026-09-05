"""Schemas for raster-backed scientific transect analysis."""

from typing import Dict, List
from pydantic import BaseModel, Field


class ProfileRequest(BaseModel):
    raster_id: str = Field(..., description="Registered raster to sample")
    start: List[float] = Field(..., min_length=2, max_length=2)
    end: List[float] = Field(..., min_length=2, max_length=2)
    samples: int = Field(default=128, ge=2, le=2048)


class ProfilePoint(BaseModel):
    distance_m: float
    longitude: float
    latitude: float
    values: Dict[str, float | None]


class TerrainProfileResponse(BaseModel):
    raster_id: str
    source_crs: str | None
    sample_count: int
    start: List[float]
    end: List[float]
    points: List[ProfilePoint]
