"""Geospatial module for AvalancheVision.

Provides CRS transformations, physics-informed morphology filters,
and zonal statistics extraction for satellite SAR avalanche deposit mapping.
"""

from geospatial.crs import reproject_geometry, reproject_geojson, utm_to_wgs84, wgs84_to_utm
from geospatial.morphology import filter_avalanche_geometries, apply_physical_slope_filter
from geospatial.zonal_stats import extract_polygon_zonal_stats

__all__ = [
    "reproject_geometry",
    "reproject_geojson",
    "utm_to_wgs84",
    "wgs84_to_utm",
    "filter_avalanche_geometries",
    "apply_physical_slope_filter",
    "extract_polygon_zonal_stats",
]
