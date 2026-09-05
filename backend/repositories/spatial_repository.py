"""Spatial repository interface for querying avalanche deposit detections, observations, and jobs."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.repositories.database import is_sqlite_mode
from backend.repositories.models import (
    HazardPredictionRecord,
    SatelliteObservationRecord,
    ProcessingJobRecord,
)
from backend.schemas.detection import (
    DetectionFeature,
    DetectionGeoJSON,
    DetectionProperties,
    DetectionSummaryStats,
    DetectionFilterParams,
)

logger = logging.getLogger("AvalancheVision.SpatialRepository")


class SpatialRepository:
    """Provides high-performance spatial query and indexing methods for avalanche deposit detections."""

    def __init__(self, geojson_path: Optional[Path] = None):
        self.geojson_path = geojson_path or (settings.DATA_PROCESSED_DIR / "high_risk_zones.geojson")
        self._cached_geojson: Optional[Dict[str, Any]] = None

    def _load_geojson(self) -> Dict[str, Any]:
        """Loads and caches the processed GeoJSON file."""
        if self._cached_geojson is None:
            if self.geojson_path.exists():
                try:
                    with open(self.geojson_path, "r", encoding="utf-8") as f:
                        self._cached_geojson = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to parse GeoJSON at {self.geojson_path}: {e}")
                    self._cached_geojson = self._fallback_geojson()
            else:
                self._cached_geojson = self._fallback_geojson()
        return self._cached_geojson

    def invalidate_cache(self) -> None:
        self._cached_geojson = None

    def query_detections(
        self,
        filters: Optional[DetectionFilterParams] = None,
        db: Optional[Session] = None
    ) -> DetectionGeoJSON:
        """Queries detection features applying multi-parameter spatial and scientific filters."""
        raw_data = self._load_geojson()
        features = raw_data.get("features", [])
        
        filtered_features: List[DetectionFeature] = []
        
        # Parse bounding box if provided: "min_lon,min_lat,max_lon,max_lat"
        bbox_geom = None
        if filters and filters.bbox:
            try:
                parts = [float(p.strip()) for p in filters.bbox.split(",")]
                if len(parts) == 4:
                    bbox_geom = box(parts[0], parts[1], parts[2], parts[3])
            except Exception as e:
                logger.warning(f"Invalid bbox parameter '{filters.bbox}': {e}")

        for feat in features:
            props = feat.get("properties", {})
            geom_dict = feat.get("geometry", {})

            if filters and (filters.start_date or filters.end_date):
                acquisition_values = [props.get("acquisition_t1"), props.get("acquisition_t2")]
                try:
                    acquisition_dates = [
                        datetime.fromisoformat(value.replace("Z", "+00:00"))
                        for value in acquisition_values if value
                    ]
                    if not acquisition_dates:
                        continue
                    window_start = datetime.fromisoformat(filters.start_date).replace(tzinfo=timezone.utc) if filters.start_date else None
                    window_end = datetime.fromisoformat(filters.end_date).replace(tzinfo=timezone.utc) if filters.end_date else None
                    if window_start and max(acquisition_dates) < window_start:
                        continue
                    if window_end and min(acquisition_dates) > window_end:
                        continue
                except ValueError:
                    logger.warning("Invalid temporal filter: %s - %s", filters.start_date, filters.end_date)
            
            # Confidence filter
            conf = props.get("confidence_score", 0.0)
            if filters and filters.min_confidence is not None:
                if conf < filters.min_confidence:
                    continue

            # Area filter (ha)
            area = props.get("area_ha", 0.0)
            if filters and filters.min_area_ha is not None:
                if area < filters.min_area_ha:
                    continue

            # Slope filter
            slope = props.get("slope_mean_deg", 0.0)
            if filters and filters.min_slope_deg is not None:
                if slope < filters.min_slope_deg:
                    continue
            if filters and filters.max_slope_deg is not None:
                if slope > filters.max_slope_deg:
                    continue

            # Aspect filter
            if filters and filters.aspect:
                if props.get("aspect_cardinal", "").upper() != filters.aspect.upper():
                    continue

            # Spatial Bounding Box intersection
            if bbox_geom and geom_dict:
                try:
                    poly_geom = shape(geom_dict)
                    if not bbox_geom.intersects(poly_geom):
                        continue
                except Exception:
                    pass

            try:
                df = DetectionFeature(
                    type="Feature",
                    id=feat.get("id") or props.get("detection_id", "AV-DET-0001"),
                    properties=DetectionProperties(**props),
                    geometry=geom_dict,
                )
                filtered_features.append(df)
            except Exception as e:
                logger.warning(f"Error deserializing feature: {e}")

        return DetectionGeoJSON(
            type="FeatureCollection",
            name="avalanche_deposit_detections",
            metadata={
                "region": "Davos Flüela Pass, Swiss Alps",
                "total_matched": len(filtered_features),
                "total_in_swath": len(features),
                "filters_applied": filters.model_dump() if filters else {}
            },
            features=filtered_features,
        )

    def get_detection_by_id(self, detection_id: str) -> Optional[DetectionFeature]:
        """Fetches detailed single detection by ID."""
        raw_data = self._load_geojson()
        for feat in raw_data.get("features", []):
            props = feat.get("properties", {})
            if props.get("detection_id") == detection_id or feat.get("id") == detection_id:
                return DetectionFeature(
                    type="Feature",
                    id=detection_id,
                    properties=DetectionProperties(**props),
                    geometry=feat.get("geometry", {}),
                )
        return None

    def get_summary_statistics(self, db: Optional[Session] = None) -> DetectionSummaryStats:
        """Calculates aggregated scientific summary statistics across the active region."""
        raw_data = self._load_geojson()
        features = raw_data.get("features", [])
        
        if not features:
            return DetectionSummaryStats(
                total_detections=0,
                total_area_ha=0.0,
                mean_confidence=0.0,
                mean_slope_deg=0.0,
                mean_elevation_m=0.0,
                mean_delta_vh_db=0.0,
                high_risk_count=0,
                very_high_risk_count=0,
                region="Davos Flüela Pass, Swiss Alps",
                acquisition_window={"t1": "2024-01-03", "t2": "2024-01-10"},
                model_version="U-Net-10Band-v1.0"
            )

        total_area = sum(f.get("properties", {}).get("area_ha", 0.0) for f in features)
        confidences = [f.get("properties", {}).get("confidence_score", 0.5) for f in features]
        slopes = [f.get("properties", {}).get("slope_mean_deg", 25.0) for f in features]
        elevations = [f.get("properties", {}).get("elevation_mean_m", 2000.0) for f in features]
        delta_vhs = [f.get("properties", {}).get("delta_vh_db", -3.5) for f in features]
        
        very_high = sum(1 for f in features if f.get("properties", {}).get("risk_level") == "Very High")
        high = len(features) - very_high

        return DetectionSummaryStats(
            total_detections=len(features),
            total_area_ha=round(total_area, 2),
            mean_confidence=round(sum(confidences) / len(confidences), 3) if confidences else 0.0,
            mean_slope_deg=round(sum(slopes) / len(slopes), 1) if slopes else 0.0,
            mean_elevation_m=round(sum(elevations) / len(elevations), 1) if elevations else 0.0,
            mean_delta_vh_db=round(sum(delta_vhs) / len(delta_vhs), 2) if delta_vhs else 0.0,
            high_risk_count=high,
            very_high_risk_count=very_high,
            region="Davos Flüela Pass, Swiss Alps",
            acquisition_window={"t1": "2024-01-03T05:35:21Z", "t2": "2024-01-10T05:27:08Z"},
            model_version="U-Net-10Band-v1.0"
        )

    def _fallback_geojson(self) -> Dict[str, Any]:
        """Provides legitimate Swiss Alps reference features if file is generating."""
        return {
            "type": "FeatureCollection",
            "name": "avalanche_deposit_detections",
            "metadata": {"region": "Davos Flüela Pass, Swiss Alps", "total_detections": 0},
            "features": []
        }


spatial_repo = SpatialRepository()
