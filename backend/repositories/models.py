"""SQLAlchemy ORM models for AvalancheVision."""

import json
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    Float,
    String,
    Text,
    DateTime,
    Boolean,
    Index,
)
from backend.repositories.database import Base


class HazardPredictionRecord(Base):
    """Stores vectorized avalanche deposit polygon detections."""
    __tablename__ = "hazard_predictions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    detection_id = Column(String(64), unique=True, index=True, nullable=False)
    acquisition_timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    risk_score = Column(Float, nullable=False, index=True)
    risk_level = Column(String(32), default="High")
    area_ha = Column(Float, default=0.0)
    area_m2 = Column(Float, default=0.0)
    perimeter_m = Column(Float, default=0.0)
    mean_elevation_m = Column(Float, default=2100.0)
    mean_slope_deg = Column(Float, default=28.0)
    dominant_aspect = Column(String(16), default="SE")
    delta_vv_db = Column(Float, default=-3.5)
    delta_vh_db = Column(Float, default=-4.2)
    model_version = Column(String(64), nullable=False, default="U-Net-10Band-v1.0")
    sensor = Column(String(64), default="Sentinel-1A IW GRD")
    region = Column(String(128), default="Davos Flüela Pass, Swiss Alps")
    geom_wkt = Column(Text, nullable=False)
    geom_geojson_json = Column(Text, nullable=False)
    properties_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SatelliteObservationRecord(Base):
    """Tracks ingested Sentinel-1 SAR scenes."""
    __tablename__ = "satellite_observations"

    id = Column(String(64), primary_key=True)
    scene_name = Column(String(256), unique=True, nullable=False, index=True)
    satellite = Column(String(32), default="Sentinel-1A")
    sensor_mode = Column(String(16), default="IW")
    product_type = Column(String(16), default="GRD")
    polarization = Column(String(32), default="VV,VH")
    acquisition_date = Column(DateTime, nullable=False, index=True)
    orbit_direction = Column(String(16), default="DESCENDING")
    relative_orbit = Column(Integer, nullable=True)
    status = Column(String(32), default="PROCESSED")
    file_size_gb = Column(Float, default=1.6)
    bbox_json = Column(String(128), nullable=False)
    footprint_geojson = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ProcessingJobRecord(Base):
    """Tracks asynchronous processing jobs and stage logs."""
    __tablename__ = "processing_jobs"

    job_id = Column(String(64), primary_key=True)
    job_type = Column(String(64), default="AVALANCHE_DETECTION_PIPELINE")
    aoi_id = Column(String(64), default="davos-fluela")
    aoi_name = Column(String(128), default="Davos Flüela Pass, Swiss Alps")
    status = Column(String(32), default="QUEUED", index=True)
    current_stage = Column(String(64), default="INITIALIZING")
    progress_percentage = Column(Integer, default=0)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    execution_duration_sec = Column(Float, nullable=True)
    model_version = Column(String(64), default="U-Net-10Band-v1.0")
    confidence_threshold = Column(Float, default=0.50)
    output_detections_count = Column(Integer, nullable=True)
    output_area_ha = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    stages_json = Column(Text, default="[]")
    logs_json = Column(Text, default="[]")


class ProvenanceEventRecord(Base):
    """Immutable lineage event linking inputs, processing stages, and outputs."""
    __tablename__ = "provenance_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(64), index=True, nullable=True)
    event_type = Column(String(64), nullable=False)
    stage = Column(String(64), nullable=True)
    source_id = Column(String(256), nullable=True)
    artifact_id = Column(String(256), nullable=True)
    model_version = Column(String(64), nullable=True)
    parameters_json = Column(Text, default="{}", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("idx_provenance_job_created", "job_id", "created_at"),
    )


class ModelBenchmarkRecord(Base):
    """Stores validated model benchmark results."""
    __tablename__ = "model_benchmarks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_version = Column(String(64), unique=True, nullable=False)
    architecture = Column(String(128), default="Multimodal 10-Band U-Net")
    iou = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    false_alarm_rate = Column(Float, nullable=False)
    optimal_threshold = Column(Float, default=0.50)
    confusion_matrix_json = Column(Text, nullable=False)
    tested_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
