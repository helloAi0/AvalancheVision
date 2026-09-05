"""Pydantic schemas for scientific analytics, measured distributions, and statistical validation."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HistogramBin(BaseModel):
    bin_start: float
    bin_end: float
    bin_label: str
    count: int
    percentage: float
    area_ha: float


class DistributionSeries(BaseModel):
    metric_name: str
    unit: str
    description: str
    bins: List[HistogramBin]
    mean: float
    std_dev: float
    min_value: float
    max_value: float
    total_samples: int


class ROCPoint(BaseModel):
    threshold: float
    false_positive_rate: float
    true_positive_rate: float
    precision: float
    recall: float
    f1_score: float


class ScientificAnalyticsResponse(BaseModel):
    region: str
    dataset_date_range: str
    total_detections_analyzed: int
    total_area_mapped_ha: float
    slope_distribution: DistributionSeries
    elevation_distribution: DistributionSeries
    backscatter_vh_change_distribution: DistributionSeries
    confidence_distribution: DistributionSeries
    aspect_distribution: Dict[str, float]
    roc_curve: List[ROCPoint]
    validation_summary: Dict[str, Any]
