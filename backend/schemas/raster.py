"""Schemas for controlled raster metadata access."""

from typing import List, Optional
from pydantic import BaseModel


class RasterBandMetadata(BaseModel):
    index: int
    name: str
    units: Optional[str] = None
    dtype: str
    nodata: Optional[float] = None


class RasterMetadata(BaseModel):
    raster_id: str
    source: str
    acquisition_date: Optional[str] = None
    crs: Optional[str] = None
    bounds: List[float]
    bounds_wgs84: Optional[List[float]] = None
    width: int
    height: int
    resolution_m: List[float]
    band_count: int
    bands: List[RasterBandMetadata]
    driver: str
    cog_status: str
