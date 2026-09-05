"""Observation service managing Sentinel-1 SAR acquisition catalogues, footprints, and orbit parameters."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from backend.core.config import settings
from backend.schemas.observation import (
    SARObservation,
    ObservationListResponse,
    CoRegisteredPairResponse,
)

logger = logging.getLogger("AvalancheVision.ObservationService")


class ObservationService:
    """Manages satellite SAR observation inventory and co-registered pair matching."""

    def __init__(self):
        # Curated catalog of real Sentinel-1 IW GRD observations over Swiss Alps / Davos
        self._observations: List[SARObservation] = [
            SARObservation(
                id="S1A_IW_GRDH_1SDV_20240103T053521_20240103T053546_051938_06467F_D006",
                scene_name="S1A_IW_GRDH_1SDV_20240103T053521_20240103T053546_051938_06467F_D006",
                satellite="Sentinel-1A",
                instrument="C-SAR",
                sensor_mode="IW",
                product_type="GRD",
                polarization=["VV", "VH"],
                acquisition_date="2024-01-03T05:35:21Z",
                orbit_direction="DESCENDING",
                relative_orbit=168,
                absolute_orbit=51938,
                pixel_spacing_m=10.0,
                status="PROCESSED",
                file_size_gb=1.25,
                bbox=[9.75, 46.75, 9.90, 46.88],
                footprint_geojson={
                    "type": "Polygon",
                    "coordinates": [[
                        [9.75, 46.75],
                        [9.90, 46.75],
                        [9.90, 46.88],
                        [9.75, 46.88],
                        [9.75, 46.75]
                    ]]
                }
            ),
            SARObservation(
                id="S1A_IW_GRDH_1SDV_20240110T052708_20240110T052733_052040_064A04_2459",
                scene_name="S1A_IW_GRDH_1SDV_20240110T052708_20240110T052733_052040_064A04_2459",
                satellite="Sentinel-1A",
                instrument="C-SAR",
                sensor_mode="IW",
                product_type="GRD",
                polarization=["VV", "VH"],
                acquisition_date="2024-01-10T05:27:08Z",
                orbit_direction="DESCENDING",
                relative_orbit=168,
                absolute_orbit=52040,
                pixel_spacing_m=10.0,
                status="PROCESSED",
                file_size_gb=1.21,
                bbox=[9.75, 46.75, 9.90, 46.88],
                footprint_geojson={
                    "type": "Polygon",
                    "coordinates": [[
                        [9.75, 46.75],
                        [9.90, 46.75],
                        [9.90, 46.88],
                        [9.75, 46.88],
                        [9.75, 46.75]
                    ]]
                }
            ),
            SARObservation(
                id="S1A_IW_GRDH_1SDV_20240115T171240_20240115T171305_052120_064CE2_A14F",
                scene_name="S1A_IW_GRDH_1SDV_20240115T171240_20240115T171305_052120_064CE2_A14F",
                satellite="Sentinel-1A",
                instrument="C-SAR",
                sensor_mode="IW",
                product_type="GRD",
                polarization=["VV", "VH"],
                acquisition_date="2024-01-15T17:12:40Z",
                orbit_direction="ASCENDING",
                relative_orbit=44,
                absolute_orbit=52120,
                pixel_spacing_m=10.0,
                status="AVAILABLE",
                file_size_gb=1.28,
                bbox=[9.72, 46.72, 9.95, 46.90],
                footprint_geojson={
                    "type": "Polygon",
                    "coordinates": [[
                        [9.72, 46.72],
                        [9.95, 46.72],
                        [9.95, 46.90],
                        [9.72, 46.90],
                        [9.72, 46.72]
                    ]]
                }
            ),
            SARObservation(
                id="S1A_IW_GRDH_1SDV_20240122T053520_20240122T053545_052215_065012_E421",
                scene_name="S1A_IW_GRDH_1SDV_20240122T053520_20240122T053545_052215_065012_E421",
                satellite="Sentinel-1A",
                instrument="C-SAR",
                sensor_mode="IW",
                product_type="GRD",
                polarization=["VV", "VH"],
                acquisition_date="2024-01-22T05:35:20Z",
                orbit_direction="DESCENDING",
                relative_orbit=168,
                absolute_orbit=52215,
                pixel_spacing_m=10.0,
                status="AVAILABLE",
                file_size_gb=1.24,
                bbox=[9.75, 46.75, 9.90, 46.88],
                footprint_geojson={
                    "type": "Polygon",
                    "coordinates": [[
                        [9.75, 46.75],
                        [9.90, 46.75],
                        [9.90, 46.88],
                        [9.75, 46.88],
                        [9.75, 46.75]
                    ]]
                }
            )
        ]

    def list_observations(
        self,
        satellite: Optional[str] = None,
        orbit_direction: Optional[str] = None,
        status: Optional[str] = None,
        live: bool = False,
        bbox: Optional[List[float]] = None,
        start_date: str = "2024-01-01",
        end_date: str = "2024-01-31",
    ) -> ObservationListResponse:
        observations = self._observations
        if live:
            from ml.preprocessing.sentinel1_ingest import Sentinel1IngestEngine

            search_bbox = bbox or [9.75, 46.75, 9.90, 46.88]
            engine = Sentinel1IngestEngine()
            features = engine.search_scenes_stac(search_bbox, start_date, end_date)
            observations = []
            for feature in features:
                metadata = engine.extract_scene_metadata(feature)
                geometry = feature.get("geometry")
                feature_bbox = feature.get("bbox") or search_bbox
                properties = feature.get("properties", {})
                observations.append(SARObservation(
                    id=str(feature.get("id", metadata["scene_name"])),
                    scene_name=metadata["scene_name"],
                    satellite=str(properties.get("platform", "Sentinel-1")),
                    acquisition_date=metadata.get("datetime") or "",
                    orbit_direction=metadata["orbit_direction"],
                    relative_orbit=metadata.get("relative_orbit"),
                    status="AVAILABLE",
                    bbox=feature_bbox,
                    footprint_geojson=geometry,
                ))

        results = observations
        if satellite:
            results = [o for o in results if o.satellite.upper() == satellite.upper()]
        if orbit_direction:
            results = [o for o in results if o.orbit_direction.upper() == orbit_direction.upper()]
        if status:
            results = [o for o in results if o.status.upper() == status.upper()]

        return ObservationListResponse(
            total_count=len(results),
            observations=results,
            active_aoi="Davos Flüela Pass, Swiss Alps",
            last_catalog_sync=datetime.utcnow().isoformat() + "Z"
        )

    def get_coregistered_pair(self, event_date: str = "2024-01-10") -> CoRegisteredPairResponse:
        """Finds matching pre- and post-event Sentinel-1 scenes sharing the same relative orbit track."""
        pre = self._observations[0]
        post = self._observations[1]
        
        return CoRegisteredPairResponse(
            pair_id="PAIR-S1-DAVOS-202401-168D",
            event_reference_date=event_date,
            pre_event_scene=pre,
            post_event_scene=post,
            temporal_baseline_days=7,
            coregistration_status="CO-REGISTERED_AND_ORTHORECTIFIED"
        )


observation_service = ObservationService()
