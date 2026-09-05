"""Main API router aggregating all API version sub-routers."""

from fastapi import APIRouter
from backend.api.v1.router import api_v1_router
from backend.core.config import settings

api_router = APIRouter()

# Keep it clean. Only mount the unified API v1 router here.
api_router.include_router(api_v1_router, prefix=settings.API_V1_STR)
