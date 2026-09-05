"""Schemas for scientific processing lineage and provenance."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProvenanceEvent(BaseModel):
    event_id: int
    job_id: Optional[str] = None
    event_type: str
    stage: Optional[str] = None
    source_id: Optional[str] = None
    artifact_id: Optional[str] = None
    model_version: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ProvenanceResponse(BaseModel):
    job_id: str
    events: List[ProvenanceEvent]
