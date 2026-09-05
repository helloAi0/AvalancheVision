"""Detection service providing spatial query coordination, validation, and analytics summarization."""

import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from backend.repositories.spatial_repository import spatial_repo
from backend.schemas.detection import (
    DetectionFeature,
    DetectionGeoJSON,
    DetectionSummaryStats,
    DetectionFilterParams,
)

logger = logging.getLogger("AvalancheVision.DetectionService")


class DetectionService:
    def __init__(self):
        self.repo = spatial_repo

    def get_geojson(
        self,
        filters: Optional[DetectionFilterParams] = None,
        db: Optional[Session] = None
    ) -> DetectionGeoJSON:
        """Retrieves WGS84 GeoJSON collection filtered by confidence, area, slope, aspect, or bbox."""
        return self.repo.query_detections(filters=filters, db=db)

    def get_detection_detail(self, detection_id: str, db: Optional[Session] = None) -> Optional[DetectionFeature]:
        """Retrieves single detection polygon feature with complete provenance and environmental telemetry."""
        return self.repo.get_detection_by_id(detection_id)

    def get_stats(self, db: Optional[Session] = None) -> DetectionSummaryStats:
        """Retrieves aggregate metrics across all current detections in the active region."""
        return self.repo.get_summary_statistics(db=db)


detection_service = DetectionService()
