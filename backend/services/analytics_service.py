"""Scientific analytics service calculating empirical distributions, terrain histograms, and model validation curves."""

import logging
from typing import Any, Dict, List, Optional
import numpy as np
from backend.repositories.spatial_repository import spatial_repo
from backend.schemas.analytics import (
    HistogramBin,
    DistributionSeries,
    ROCPoint,
    ScientificAnalyticsResponse,
)

logger = logging.getLogger("AvalancheVision.AnalyticsService")


class AnalyticsService:
    def __init__(self):
        self.repo = spatial_repo

    def get_scientific_analytics(self) -> ScientificAnalyticsResponse:
        """Computes empirical data distributions and scientific charts from active detections."""
        raw_data = self.repo._load_geojson()
        features = raw_data.get("features", [])

        if not features:
            return self._build_empty_analytics()

        slopes = [float(f.get("properties", {}).get("slope_mean_deg", 28.0)) for f in features]
        elevations = [float(f.get("properties", {}).get("elevation_mean_m", 2150.0)) for f in features]
        delta_vhs = [float(f.get("properties", {}).get("delta_vh_db", -4.0)) for f in features]
        confidences = [float(f.get("properties", {}).get("confidence_score", 0.75)) for f in features]
        areas = [float(f.get("properties", {}).get("area_ha", 0.5)) for f in features]
        aspects = [str(f.get("properties", {}).get("aspect_cardinal", "SE")) for f in features]

        total_area_ha = round(sum(areas), 2)
        n_samples = len(features)

        # 1. Slope Distribution (Bins of 5 degrees from 15° to 60°)
        slope_bins_def = [
            (15.0, 20.0, "15° - 20° (Runout Zone)"),
            (20.0, 25.0, "20° - 25° (Lower Track)"),
            (25.0, 30.0, "25° - 30° (Track / Debris Fan)"),
            (30.0, 35.0, "30° - 35° (Mid Track)"),
            (35.0, 40.0, "35° - 40° (Steep Track)"),
            (40.0, 45.0, "40° - 45° (Starting Zone Margin)"),
            (45.0, 50.0, "45° - 50° (Steep Couloir)"),
            (50.0, 60.0, "50° - 60° (Extreme Face)"),
        ]
        slope_bins = self._compute_bins(slopes, areas, slope_bins_def, n_samples)
        slope_series = DistributionSeries(
            metric_name="Terrain Slope Inclination",
            unit="degrees (°)",
            description="Mean terrain slope angle measured by Copernicus DEM across detected avalanche deposit polygons.",
            bins=slope_bins,
            mean=round(float(np.mean(slopes)), 1),
            std_dev=round(float(np.std(slopes)), 1),
            min_value=round(float(np.min(slopes)), 1),
            max_value=round(float(np.max(slopes)), 1),
            total_samples=n_samples,
        )

        # 2. Elevation Distribution (Bins of 250m from 1500m to 3000m)
        elev_bins_def = [
            (1500.0, 1750.0, "1500m - 1750m (Valley Floor)"),
            (1750.0, 2000.0, "1750m - 2000m (Lower Subalpine)"),
            (2000.0, 2250.0, "2000m - 2250m (Mid Subalpine)"),
            (2250.0, 2500.0, "2250m - 2500m (Upper Alpine)"),
            (2500.0, 2750.0, "2500m - 2750m (High Alpine)"),
            (2750.0, 3100.0, "2750m - 3100m (Peak Ridge)"),
        ]
        elev_bins = self._compute_bins(elevations, areas, elev_bins_def, n_samples)
        elev_series = DistributionSeries(
            metric_name="Elevation Profile",
            unit="meters (m)",
            description="Mean altitude above sea level derived from Copernicus 30m Global DEM.",
            bins=elev_bins,
            mean=round(float(np.mean(elevations)), 1),
            std_dev=round(float(np.std(elevations)), 1),
            min_value=round(float(np.min(elevations)), 1),
            max_value=round(float(np.max(elevations)), 1),
            total_samples=n_samples,
        )

        # 3. SAR Backscatter VH Change (Δσ° drop in dB)
        sar_bins_def = [
            (-1.5, 0.0, "0 to -1.5 dB (Subtle Change)"),
            (-3.0, -1.5, "-1.5 to -3.0 dB (Moderate Anomaly)"),
            (-4.5, -3.0, "-3.0 to -4.5 dB (Strong Signature)"),
            (-6.0, -4.5, "-4.5 to -6.0 dB (Severe Drop)"),
            (-12.0, -6.0, "< -6.0 dB (Extreme Scattering Loss)"),
        ]
        sar_bins = self._compute_bins_inverted(delta_vhs, areas, sar_bins_def, n_samples)
        sar_series = DistributionSeries(
            metric_name="SAR VH Backscatter Ratio Drop (Δσ°)",
            unit="decibels (dB)",
            description="Log-ratio radar backscatter change between T1 (pre-event) and T2 (post-event) Sentinel-1 C-band SAR.",
            bins=sar_bins,
            mean=round(float(np.mean(delta_vhs)), 2),
            std_dev=round(float(np.std(delta_vhs)), 2),
            min_value=round(float(np.min(delta_vhs)), 2),
            max_value=round(float(np.max(delta_vhs)), 2),
            total_samples=n_samples,
        )

        # 4. Confidence Distribution
        conf_bins_def = [
            (0.40, 0.50, "0.40 - 0.50 (Marginal)"),
            (0.50, 0.60, "0.50 - 0.60 (Moderate)"),
            (0.60, 0.70, "0.60 - 0.70 (Substantial)"),
            (0.70, 0.80, "0.70 - 0.80 (High)"),
            (0.80, 0.90, "0.80 - 0.90 (Very High)"),
            (0.90, 1.00, "0.90 - 1.00 (Extreme)"),
        ]
        conf_bins = self._compute_bins(confidences, areas, conf_bins_def, n_samples)
        conf_series = DistributionSeries(
            metric_name="Model Probability Confidence",
            unit="probability (0 - 1)",
            description="U-Net segmentation sigmoid output calibrated across the multi-band feature stack.",
            bins=conf_bins,
            mean=round(float(np.mean(confidences)), 3),
            std_dev=round(float(np.std(confidences)), 3),
            min_value=round(float(np.min(confidences)), 3),
            max_value=round(float(np.max(confidences)), 3),
            total_samples=n_samples,
        )

        # 5. Aspect Breakdown
        aspect_counts = {}
        for card in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]:
            aspect_counts[card] = round(aspects.count(card) / n_samples * 100.0, 1) if n_samples > 0 else 0.0

        # No independent benchmark record is available for this deployment.
        roc_points = []
        validation_summary = {
            "status": "UNAVAILABLE",
            "reason": "No independent, versioned benchmark is registered for the active model.",
        }

        return ScientificAnalyticsResponse(
            region="Davos Flüela Pass, Swiss Alps",
            dataset_date_range="2024-01-03 to 2024-01-10",
            total_detections_analyzed=n_samples,
            total_area_mapped_ha=total_area_ha,
            slope_distribution=slope_series,
            elevation_distribution=elev_series,
            backscatter_vh_change_distribution=sar_series,
            confidence_distribution=conf_series,
            aspect_distribution=aspect_counts,
            roc_curve=roc_points,
            validation_summary=validation_summary,
        )

    def _compute_bins(
        self, values: List[float], areas: List[float], bin_defs: List[tuple], total: int
    ) -> List[HistogramBin]:
        bins = []
        for low, high, label in bin_defs:
            indices = [i for i, v in enumerate(values) if low <= v < high]
            count = len(indices)
            pct = round(count / total * 100.0, 1) if total > 0 else 0.0
            area = round(sum(areas[i] for i in indices), 2)
            bins.append(
                HistogramBin(
                    bin_start=low,
                    bin_end=high,
                    bin_label=label,
                    count=count,
                    percentage=pct,
                    area_ha=area,
                )
            )
        return bins

    def _compute_bins_inverted(
        self, values: List[float], areas: List[float], bin_defs: List[tuple], total: int
    ) -> List[HistogramBin]:
        bins = []
        for low, high, label in bin_defs:
            indices = [i for i, v in enumerate(values) if low <= v < high]
            count = len(indices)
            pct = round(count / total * 100.0, 1) if total > 0 else 0.0
            area = round(sum(areas[i] for i in indices), 2)
            bins.append(
                HistogramBin(
                    bin_start=low,
                    bin_end=high,
                    bin_label=label,
                    count=count,
                    percentage=pct,
                    area_ha=area,
                )
            )
        return bins

    def _build_empty_analytics(self) -> ScientificAnalyticsResponse:
        empty_series = DistributionSeries(
            metric_name="N/A", unit="", description="", bins=[], mean=0, std_dev=0, min_value=0, max_value=0, total_samples=0
        )
        return ScientificAnalyticsResponse(
            region="Davos Flüela Pass, Swiss Alps",
            dataset_date_range="N/A",
            total_detections_analyzed=0,
            total_area_mapped_ha=0,
            slope_distribution=empty_series,
            elevation_distribution=empty_series,
            backscatter_vh_change_distribution=empty_series,
            confidence_distribution=empty_series,
            aspect_distribution={},
            roc_curve=[],
            validation_summary={},
        )


analytics_service = AnalyticsService()
