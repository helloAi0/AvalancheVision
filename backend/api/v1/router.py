"""Aggregation router for API version 1."""

from fastapi import APIRouter
from backend.api.v1.detections import router as detections_router
from backend.api.v1.observations import router as observations_router
from backend.api.v1.models import router as models_router
from backend.api.v1.jobs import router as jobs_router
from backend.api.v1.analytics import router as analytics_router
from backend.api.v1.export import router as export_router
from backend.api.v1.health import router as health_router
from backend.api.v1.rasters import router as rasters_router
from backend.api.v1.provenance import router as provenance_router
from backend.api.v1.analysis import router as analysis_router
from backend.api.v1.terrain import router as terrain_router # <-- ADD THIS IMPORT

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(rasters_router)
api_v1_router.include_router(provenance_router)
api_v1_router.include_router(analysis_router)
api_v1_router.include_router(detections_router)
api_v1_router.include_router(observations_router)
api_v1_router.include_router(models_router)
api_v1_router.include_router(jobs_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(export_router)
api_v1_router.include_router(terrain_router) # <-- ADD THIS ROUTER INCLUDE
