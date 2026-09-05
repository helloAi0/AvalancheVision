"""Persistence service for scientific lineage events."""

import json
from backend.repositories.database import SessionLocal
from backend.repositories.models import ProvenanceEventRecord


def record_provenance_event(
    event_type: str,
    job_id: str | None = None,
    stage: str | None = None,
    source_id: str | None = None,
    artifact_id: str | None = None,
    model_version: str | None = None,
    parameters: dict | None = None,
) -> None:
    with SessionLocal() as db:
        db.add(ProvenanceEventRecord(
            job_id=job_id,
            event_type=event_type,
            stage=stage,
            source_id=source_id,
            artifact_id=artifact_id,
            model_version=model_version,
            parameters_json=json.dumps(parameters or {}),
        ))
        db.commit()
