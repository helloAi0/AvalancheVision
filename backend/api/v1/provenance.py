"""Scientific lineage endpoints."""

import json
from fastapi import APIRouter, HTTPException

from backend.repositories.database import SessionLocal
from backend.repositories.models import ProcessingJobRecord, ProvenanceEventRecord
from backend.schemas.provenance import ProvenanceEvent, ProvenanceResponse
from backend.services.provenance_service import record_provenance_event

router = APIRouter(prefix="/provenance", tags=["Scientific Provenance"])


@router.get("/{job_id}", response_model=ProvenanceResponse)
def get_job_provenance(job_id: str) -> ProvenanceResponse:
    with SessionLocal() as db:
        if not db.get(ProcessingJobRecord, job_id):
            raise HTTPException(status_code=404, detail=f"Processing job '{job_id}' not found.")
        records = db.query(ProvenanceEventRecord).filter(
            ProvenanceEventRecord.job_id == job_id
        ).order_by(ProvenanceEventRecord.created_at.asc()).all()
        events = [ProvenanceEvent(
            event_id=record.id,
            job_id=record.job_id,
            event_type=record.event_type,
            stage=record.stage,
            source_id=record.source_id,
            artifact_id=record.artifact_id,
            model_version=record.model_version,
            parameters=json.loads(record.parameters_json or "{}"),
            created_at=record.created_at,
        ) for record in records]
    return ProvenanceResponse(job_id=job_id, events=events)
