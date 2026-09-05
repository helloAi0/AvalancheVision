"""Celery application and GIS task definitions."""

from celery import Celery

from backend.core.config import settings

celery_app = Celery(
    "avalanchevision",
    broker=settings.resolved_celery_broker_url,
    backend=settings.resolved_celery_result_backend,
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    task_track_started=True,
    broker_connection_retry_on_startup=True,
)


@celery_app.task(name="avalanchevision.calculate_raster_statistics")
def calculate_raster_statistics(raster_id: str, bbox: list[float] | None = None) -> dict:
    """Run a raster calculation outside the FastAPI request thread."""
    from backend.services.analytics_service import analytics_service

    # Keep the task boundary serializable; the domain service owns data access.
    result = analytics_service.get_scientific_analytics()
    if hasattr(result, "model_dump"):
        result = result.model_dump()
    return {"raster_id": raster_id, "bbox": bbox, "result": result}


@celery_app.task(name="avalanchevision.execute_pipeline")
def execute_pipeline(job_id: str, request_payload: dict) -> str:
    """Execute the existing pipeline service from a Celery worker."""
    from backend.schemas.job import JobCreateRequest
    from backend.services.pipeline_service import pipeline_service

    pipeline_service._execute_pipeline(job_id, JobCreateRequest.model_validate(request_payload))
    return job_id
