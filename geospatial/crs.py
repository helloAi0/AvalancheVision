"""CRS transformation utilities for AvalancheVision.

Manages conversions between metric projected coordinate reference systems
(e.g., UTM Zone 32N / EPSG:32632 for accurate spatial/area calculations)
and geographic coordinates (WGS84 / EPSG:4326 for GeoJSON web standard).
"""

import json
import logging
from typing import Any, Dict, List, Tuple, Union
import pyproj
from pyproj import Transformer
from shapely.geometry import shape, mapping
from shapely.ops import transform

logger = logging.getLogger("AvalancheVision.Geospatial.CRS")

# Pre-instantiate standard transformers for Swiss Alps / Central Europe
_transformer_utm32_to_wgs84 = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)
_transformer_wgs84_to_utm32 = Transformer.from_crs("EPSG:4326", "EPSG:32632", always_xy=True)


def utm_to_wgs84(x: float, y: float, source_epsg: int = 32632) -> Tuple[float, float]:
    """Converts metric UTM coordinates (easting, northing) to geographic (longitude, latitude).
    
    Args:
        x: Easting in meters
        y: Northing in meters
        source_epsg: Projected CRS EPSG code (default: 32632 for UTM Zone 32N)
        
    Returns:
        Tuple of (longitude, latitude) in WGS84 decimal degrees
    """
    if source_epsg == 32632:
        lon, lat = _transformer_utm32_to_wgs84.transform(x, y)
    else:
        t = Transformer.from_crs(f"EPSG:{source_epsg}", "EPSG:4326", always_xy=True)
        lon, lat = t.transform(x, y)
    return float(lon), float(lat)


def wgs84_to_utm(lon: float, lat: float, target_epsg: int = 32632) -> Tuple[float, float]:
    """Converts geographic (longitude, latitude) to metric UTM coordinates (easting, northing).
    
    Args:
        lon: Longitude in WGS84 decimal degrees
        lat: Latitude in WGS84 decimal degrees
        target_epsg: Target projected CRS EPSG code (default: 32632)
        
    Returns:
        Tuple of (easting, northing) in meters
    """
    if target_epsg == 32632:
        x, y = _transformer_wgs84_to_utm32.transform(lon, lat)
    else:
        t = Transformer.from_crs("EPSG:4326", f"EPSG:{target_epsg}", always_xy=True)
        x, y = t.transform(lon, lat)
    return float(x), float(y)


def reproject_geometry(geom: Any, from_crs: str = "EPSG:32632", to_crs: str = "EPSG:4326") -> Any:
    """Reprojects a Shapely geometry between coordinate reference systems.
    
    Args:
        geom: Shapely geometry instance (Polygon, MultiPolygon, Point, etc.)
        from_crs: Source CRS string (e.g. 'EPSG:32632')
        to_crs: Destination CRS string (e.g. 'EPSG:4326')
        
    Returns:
        Reprojected Shapely geometry
    """
    if from_crs.upper() == to_crs.upper():
        return geom

    transformer = Transformer.from_crs(from_crs, to_crs, always_xy=True)
    return transform(transformer.transform, geom)


def reproject_geojson(
    geojson_data: Dict[str, Any],
    from_crs: str = "EPSG:32632",
    to_crs: str = "EPSG:4326"
) -> Dict[str, Any]:
    """Reprojects all feature geometries in a GeoJSON dictionary to the target CRS.
    
    Args:
        geojson_data: GeoJSON FeatureCollection or Feature dictionary
        from_crs: Source CRS (default: 'EPSG:32632')
        to_crs: Target CRS (default: 'EPSG:4326')
        
    Returns:
        New GeoJSON dictionary with reprojected coordinates and standardized WGS84 CRS header
    """
    if geojson_data.get("type") == "FeatureCollection":
        features = geojson_data.get("features", [])
        reprojected_features = []
        
        for feat in features:
            geom_dict = feat.get("geometry")
            if not geom_dict:
                continue
            geom = shape(geom_dict)
            if not geom.is_valid:
                geom = geom.buffer(0)
            
            reprojected_geom = reproject_geometry(geom, from_crs, to_crs)
            
            new_feat = dict(feat)
            new_feat["geometry"] = mapping(reprojected_geom)
            reprojected_features.append(new_feat)
            
        return {
            "type": "FeatureCollection",
            "crs": {
                "type": "name",
                "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
            },
            "features": reprojected_features
        }
    elif geojson_data.get("type") == "Feature":
        geom = shape(geojson_data["geometry"])
        reprojected_geom = reproject_geometry(geom, from_crs, to_crs)
        new_feat = dict(geojson_data)
        new_feat["geometry"] = mapping(reprojected_geom)
        return new_feat
        
    return geojson_data
