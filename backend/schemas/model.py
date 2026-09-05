"""Pydantic schemas for machine learning model specifications, tensor configurations, and validation benchmarks."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict  # <-- Added ConfigDict here


class InputBandConfig(BaseModel):
    index: int = Field(..., description="1-based band index")
    name: str = Field(..., description="Band name")
    modality: str = Field(..., description="SAR, DEM, or ERA5")
    description: str = Field(..., description="Physical sensor and parameter description")
    units: str = Field(..., description="Measurement units")
    resolution_m: float = Field(default=10.0, description="Spatial resolution in meters")


class ModelBenchmarkMetrics(BaseModel):
    iou: float = Field(..., description="Intersection over Union / Jaccard Index")
    f1_score: float = Field(..., description="F1 Score / Dice Similarity Coefficient")
    precision: float = Field(..., description="Precision / Positive Predictive Value")
    recall: float = Field(..., description="Recall / Probability of Detection (POD)")
    false_alarm_rate: float = Field(..., description="False Alarm Rate (FAR)")
    optimal_threshold: float = Field(default=0.50)
    confusion_matrix: Dict[str, int] = Field(
        default_factory=lambda: {"tp": 0, "fp": 0, "tn": 0, "fn": 0}
    )


class ModelDetails(BaseModel):
    # 🚨 Tell Pydantic to ignore 'model_' prefix naming conventions here
    model_config = ConfigDict(protected_namespaces=())

    model_version: str = Field(..., description="Version tag, e.g. U-Net-10Band-v1.0")
    architecture: str = Field(default="Multimodal 10-Channel U-Net with Residual Connections")
    framework: str = Field(default="PyTorch 2.2.1")
    input_channels: int = Field(default=10)
    output_classes: int = Field(default=1)
    parameters_count: int = Field(default=7504634)
    checkpoint_file: str = Field(default="unet_avalanche.pth")
    checkpoint_size_mb: float = Field(default=7.5)
    training_dataset: str = Field(default="Davos-Flüela Pass Multimodal Satellite Benchmark (Sentinel-1 + Copernicus DEM + ERA5)")
    training_epochs: int = Field(default=5)
    patch_size: int = Field(default=256)
    loss_function: str = Field(default="Combined Weighted BCE + Soft Dice Loss (pos_weight=6.0)")
    optimizer: str = Field(default="AdamW (lr=2e-4, weight_decay=1e-4)")
    input_bands: List[InputBandConfig]
    benchmarks: Optional[ModelBenchmarkMetrics] = None
    scientific_status: str = Field(
        default="Research-Grade Scientific Evaluation Model. Optimized for avalanche debris mapping in Alpine terrain."
    )
    limitations: List[str] = Field(
        default_factory=lambda: [
            "SAR radar layover and radar shadow in steep terrain (>60°) can obscure radar backscatter returns.",
            "Radar signal attenuation caused by heavy liquid precipitation (wet snow transition) requires ERA5 temperature filtering.",
            "Resolution limit: Avalanche debris deposits under 200 m² cannot be reliably distinguished from speckle noise at 10m spatial resolution."
        ]
    )


class ModelVersionRegistry(BaseModel):
    # 🚨 Tell Pydantic to ignore 'model_' prefix naming conventions here
    model_config = ConfigDict(protected_namespaces=())

    active_model_version: str
    available_models: List[ModelDetails]
