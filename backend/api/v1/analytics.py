"""FastAPI endpoints for scientific data visualization, distributions, and empirical validation."""

from fastapi import APIRouter
from backend.services.analytics_service import analytics_service
from backend.schemas.analytics import ScientificAnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["Scientific Analytics & Visualization"])


@router.get("/distributions", response_model=ScientificAnalyticsResponse)
def get_scientific_distributions():
    """Returns empirical distributions (slope, elevation, SAR Δσ° drop, confidence) and validation performance curves."""
    return analytics_service.get_scientific_analytics()
