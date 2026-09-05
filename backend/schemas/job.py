"""Pydantic schemas for asynchronous processing jobs, pipeline triggers, and live stage logs."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class JobStageLog(BaseModel):
    stage_name: str = Field(..., description="Stage identifier")
    display_title: str = Field(..., description="Human readable title")
    status: str = Field(default="PENDING", description="PENDING, RUNNING, COMPLETED, FAILED, SKIPPED")
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    details: Optional[str] = None


class JobCreateRequest(BaseModel):
    aoi_id: str = Field(default="davos-fluela", description="Region of interest identifier")
    pre_event_date: str = Field(default="2024-01-03", description="YYYY-MM-DD")
    post_event_date: str = Field(default="2024-01-10", description="YYYY-MM-DD")
    model_version: str = Field(default="U-Net-10Band-v1.0")
    confidence_threshold: float = Field(default=0.50, ge=0.1, le=0.9)
    min_cluster_area_m2: float = Field(default=300.0, ge=50.0)
    apply_physics_filter: bool = Field(default=True)


class ProcessingJob(BaseModel):
    job_id: str = Field(..., description="Unique UUID job identifier")
    job_type: str = Field(default="AVALANCHE_DETECTION_PIPELINE")
    aoi_id: str
    aoi_name: str
    status: str = Field(default="QUEUED", description="QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED")
    current_stage: str = Field(default="INITIALIZING")
    progress_percentage: int = Field(default=0, ge=0, le=100)
    submitted_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    execution_duration_sec: Optional[float] = None
    model_version: str
    confidence_threshold: float
    output_detections_count: Optional[int] = None
    output_area_ha: Optional[float] = None
    error_message: Optional[str] = None
    stages: List[JobStageLog] = Field(default_factory=list)
    raw_logs: List[str] = Field(default_factory=list)


class JobListResponse(BaseModel):
    total_jobs: int
    jobs: List[ProcessingJob]
