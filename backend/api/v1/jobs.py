"""FastAPI endpoints for asynchronous jobs and live persisted telemetry."""

import asyncio
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from backend.core.security import require_api_key
from backend.services.pipeline_service import pipeline_service
from backend.schemas.job import (
    JobCreateRequest,
    ProcessingJob,
    JobListResponse,
)

router = APIRouter(prefix="/jobs", tags=["Processing Jobs & Orchestration"])


@router.get("", response_model=JobListResponse)
def list_processing_jobs():
    """Lists all submitted, running, and completed data processing and inference jobs."""
    return pipeline_service.list_jobs()


@router.get("/{job_id}", response_model=ProcessingJob)
def get_job_status(job_id: str):
    """Fetches real-time status, active pipeline stage, progress percentage, and log console output for a specific job."""
    job = pipeline_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Processing job '{job_id}' not found.")
    return job


@router.post("/submit", response_model=ProcessingJob, dependencies=[Depends(require_api_key)])
def submit_new_processing_job(request: JobCreateRequest):
    """Submits a new asynchronous processing pipeline run (SAR Ingestion -> DEM Extraction -> ERA5 Stacking -> U-Net Inference -> Vectorization)."""
    return pipeline_service.submit_job(request)


@router.websocket("/ws/{job_id}")
async def stream_job_status(websocket: WebSocket, job_id: str):
    """Stream database-backed job snapshots until the job reaches a terminal state."""
    await websocket.accept()
    try:
        last_snapshot = None
        while True:
            job = pipeline_service.get_job(job_id)
            if job is None:
                await websocket.send_json({"error": "JOB_NOT_FOUND", "job_id": job_id})
                await websocket.close(code=1008)
                return

            snapshot = job.model_dump(mode="json")
            if snapshot != last_snapshot:
                await websocket.send_json(snapshot)
                last_snapshot = snapshot
            if job.status in {"COMPLETED", "FAILED", "CANCELLED"}:
                await websocket.close(code=1000)
                return
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        return
