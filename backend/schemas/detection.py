"""Pydantic v2 schemas for AvalancheVision detection features and spatial queries."""

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class DetectionProperties(BaseModel):
    detection_id: str = Field(..., description="Unique detection identifier")
    risk_level: str = Field(..., description="Categorical risk tier: Moderate, High, or Very High")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Mean model confidence probability")
    confidence_max: float = Field(..., ge=0.0, le=1.0, description="Peak pixel confidence probability")
    confidence_min: float = Field(..., ge=0.0, le=1.0, description="Minimum pixel confidence probability")
    area_ha: float = Field(..., ge=0.0, description="Surface area in hectares")
    area_m2: float = Field(..., ge=0.0, description="Surface area in square meters")
    perimeter_m: float = Field(..., ge=0.0, description="Perimeter in meters")
    elevation_mean_m: float = Field(..., description="Mean elevation above sea level in meters")
    elevation_min_m: float = Field(..., description="Minimum elevation in meters")
    elevation_max_m: float = Field(..., description="Maximum elevation in meters")
    slope_mean_deg: float = Field(..., description="Mean terrain slope inclination in degrees")
    aspect_cardinal: str = Field(..., description="Dominant compass aspect orientation (e.g., N, NE, E, SE, S, SW, W, NW)")
    aspect_mean_deg: float = Field(..., description="Mean aspect angle in degrees (0-360)")
    delta_vv_db: float = Field(..., description="SAR VV backscatter log-ratio change in dB")
    delta_vh_db: float = Field(..., description="SAR VH backscatter log-ratio change in dB")
    era5_temperature_c: float = Field(..., description="ERA5 2m air temperature at acquisition in Celsius")
    era5_precip_mm: float = Field(..., description="ERA5 total precipitation in mm")
    era5_snow_depth_m: float = Field(..., description="ERA5 snow depth in meters")
    acquisition_t1: str = Field(..., description="Pre-event Sentinel-1 acquisition timestamp ISO8601")
    acquisition_t2: str = Field(..., description="Post-event Sentinel-1 acquisition timestamp ISO8601")
    model_version: str = Field(..., description="Model version and tensor specification")
    sensor: str = Field(..., description="Satellite sensor mode (e.g. Sentinel-1A IW GRD)")
    region: str = Field(..., description="Geographic region of interest name")


class GeoJSONGeometry(BaseModel):
    type: str = Field(..., description="Geometry type: Polygon or MultiPolygon")
    coordinates: List[Any] = Field(..., description="WGS84 lon/lat coordinate hierarchy")


class DetectionFeature(BaseModel):
    type: str = Field(default="Feature")
    id: str
    properties: DetectionProperties
    geometry: GeoJSONGeometry


class DetectionGeoJSON(BaseModel):
    type: str = Field(default="FeatureCollection")
    name: str = Field(default="avalanche_deposit_detections")
    crs: Dict[str, Any] = Field(
        default_factory=lambda: {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)
    features: List[DetectionFeature] = Field(default_factory=list)


class DetectionSummaryStats(BaseModel):
    total_detections: int
    total_area_ha: float
    mean_confidence: float
    mean_slope_deg: float
    mean_elevation_m: float
    mean_delta_vh_db: float
    high_risk_count: int
    very_high_risk_count: int
    region: str
    acquisition_window: Dict[str, str]
    model_version: str


class DetectionFilterParams(BaseModel):
    min_confidence: Optional[float] = Field(default=0.40, ge=0.0, le=1.0)
    min_area_ha: Optional[float] = Field(default=0.0, ge=0.0)
    min_slope_deg: Optional[float] = Field(default=None, ge=0.0, le=90.0)
    max_slope_deg: Optional[float] = Field(default=None, ge=0.0, le=90.0)
    aspect: Optional[str] = Field(default=None)
    bbox: Optional[str] = Field(default=None, description="Bounding box as 'min_lon,min_lat,max_lon,max_lat'")
    start_date: Optional[str] = Field(default=None, description="Inclusive T1 acquisition date in ISO-8601 format")
    end_date: Optional[str] = Field(default=None, description="Inclusive T2 acquisition date in ISO-8601 format")
