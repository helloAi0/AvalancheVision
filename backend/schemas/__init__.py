"""Pydantic schemas package for AvalancheVision API."""

from backend.schemas.detection import (
    DetectionProperties,
    DetectionFeature,
    DetectionGeoJSON,
    DetectionSummaryStats,
    DetectionFilterParams,
)
from backend.schemas.observation import (
    SARObservation,
    ObservationListResponse,
    CoRegisteredPairResponse,
)
from backend.schemas.model import (
    InputBandConfig,
    ModelBenchmarkMetrics,
    ModelDetails,
    ModelVersionRegistry,
)
from backend.schemas.job import (
    JobStageLog,
    JobCreateRequest,
    ProcessingJob,
    JobListResponse,
)
from backend.schemas.analytics import (
    HistogramBin,
    DistributionSeries,
    ROCPoint,
    ScientificAnalyticsResponse,
)
from backend.schemas.system import (
    RegionOfInterest,
    SystemHealthResponse,
)

__all__ = [
    "DetectionProperties",
    "DetectionFeature",
    "DetectionGeoJSON",
    "DetectionSummaryStats",
    "DetectionFilterParams",
    "SARObservation",
    "ObservationListResponse",
    "CoRegisteredPairResponse",
    "InputBandConfig",
    "ModelBenchmarkMetrics",
    "ModelDetails",
    "ModelVersionRegistry",
    "JobStageLog",
    "JobCreateRequest",
    "ProcessingJob",
    "JobListResponse",
    "HistogramBin",
    "DistributionSeries",
    "ROCPoint",
    "ScientificAnalyticsResponse",
    "RegionOfInterest",
    "SystemHealthResponse",
]
