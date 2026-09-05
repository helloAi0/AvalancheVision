"""Physics-informed morphological filtering for avalanche deposit mapping.

Applies scientific domain constraints based on mountain topology,
slope inclination thresholds, and cluster area minimums to suppress
SAR speckle artifacts and false-positive backscatter anomalies.
"""

import logging
from typing import List, Optional, Tuple, Union
import numpy as np
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

logger = logging.getLogger("AvalancheVision.Geospatial.Morphology")


def apply_physical_slope_filter(
    mean_slope_deg: float,
    min_slope_deg: float = 14.0,
    max_slope_deg: float = 62.0
) -> bool:
    """Evaluates whether a candidate detection polygon adheres to physical slope boundaries for avalanche runout/debris zones.
    
    Avalanche deposits typically accumulate in track and runout zones with slope
    angles between 15° and 55°. Flat agricultural plains (<14°) and vertical rock
    faces (>62°) are physically inconsistent with debris accumulation fans.
    
    Args:
        mean_slope_deg: Mean slope angle across the polygon in degrees
        min_slope_deg: Minimum physical threshold (default: 14.0°)
        max_slope_deg: Maximum physical threshold (default: 62.0°)
        
    Returns:
        True if valid physical slope, False otherwise
    """
    return min_slope_deg <= mean_slope_deg <= max_slope_deg


def filter_avalanche_geometries(
    geometries: List[Union[Polygon, MultiPolygon]],
    min_area_m2: float = 300.0,
    max_area_m2: float = 5_000_000.0,
    simplify_tolerance_m: float = 2.0
) -> List[Polygon]:
    """Filters and cleans candidate avalanche deposit geometries.
    
    1. Removes isolated single-pixel SAR speckle clusters (< min_area_m2).
    2. Explodes MultiPolygons into independent deposit polygons.
    3. Simplifies boundary geometries using Douglas-Peucker to remove raster stair-stepping.
    4. Validates and fixes self-intersecting polygon topologies.
    
    Args:
        geometries: List of candidate Shapely geometries in a metric CRS (e.g. UTM)
        min_area_m2: Minimum contiguous surface area in square meters (default: 300 m²)
        max_area_m2: Maximum plausible single avalanche deposit area in m²
        simplify_tolerance_m: Geometry simplification tolerance in meters (default: 2.0m)
        
    Returns:
        Filtered list of clean, topologically valid Shapely Polygons
    """
    cleaned_polygons: List[Polygon] = []
    
    for geom in geometries:
        if geom is None or geom.is_empty:
            continue
            
        # Ensure valid geometry
        if not geom.is_valid:
            geom = geom.buffer(0)
            
        if isinstance(geom, MultiPolygon):
            polys = list(geom.geoms)
        elif isinstance(geom, Polygon):
            polys = [geom]
        else:
            continue
            
        for poly in polys:
            if not poly.is_valid or poly.is_empty:
                poly = poly.buffer(0)
                
            area = poly.area
            if min_area_m2 <= area <= max_area_m2:
                if simplify_tolerance_m > 0:
                    simplified = poly.simplify(simplify_tolerance_m, preserve_topology=True)
                    if isinstance(simplified, Polygon) and not simplified.is_empty:
                        cleaned_polygons.append(simplified)
                    else:
                        cleaned_polygons.append(poly)
                else:
                    cleaned_polygons.append(poly)
                    
    logger.info(
        f"Morphological filtering: {len(geometries)} raw shapes -> {len(cleaned_polygons)} physically consistent deposit polygons."
    )
    return cleaned_polygons
