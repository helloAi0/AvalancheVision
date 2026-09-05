"""FastAPI endpoints for ML model inspection, 10-band tensor specifications, and validation benchmarks."""

from fastapi import APIRouter
from backend.schemas.model import (
    ModelDetails,
    ModelBenchmarkMetrics,
    ModelVersionRegistry,
    InputBandConfig,
)

router = APIRouter(prefix="/models", tags=["Machine Learning & Models"])

_ACTIVE_MODEL = ModelDetails(
    model_version="U-Net-10Band-v1.0",
    architecture="Multimodal 10-Channel U-Net with Residual Convolution Blocks",
    framework="PyTorch 2.2.1",
    input_channels=10,
    output_classes=1,
    parameters_count=7504634,
    checkpoint_file="unet_avalanche.pth",
    checkpoint_size_mb=7.5,
    training_dataset="Davos Flüela Pass Multimodal Benchmark (Sentinel-1 SAR + Copernicus DEM GLO-30 + ECMWF ERA5-Land)",
    training_epochs=5,
    patch_size=256,
    loss_function="Combined Weighted BCE + Soft Dice Loss (pos_weight=6.0, dice_weight=0.5)",
    optimizer="AdamW (lr=2e-4, weight_decay=1e-4)",
    input_bands=[
        InputBandConfig(index=1, name="T1_VV_Backscatter", modality="SAR", description="Pre-event Sentinel-1 C-band VV polarization amplitude", units="linear intensity", resolution_m=10.0),
        InputBandConfig(index=2, name="T1_VH_Backscatter", modality="SAR", description="Pre-event Sentinel-1 C-band VH cross-polarization amplitude", units="linear intensity", resolution_m=10.0),
        InputBandConfig(index=3, name="T2_VV_Backscatter", modality="SAR", description="Post-event Sentinel-1 C-band VV polarization amplitude", units="linear intensity", resolution_m=10.0),
        InputBandConfig(index=4, name="T2_VH_Backscatter", modality="SAR", description="Post-event Sentinel-1 C-band VH cross-polarization amplitude (key avalanche scattering signature)", units="linear intensity", resolution_m=10.0),
        InputBandConfig(index=5, name="DEM_Elevation", modality="DEM", description="Copernicus 30m Global Digital Elevation Model reprojected to UTM 32N", units="meters (m)", resolution_m=10.0),
        InputBandConfig(index=6, name="Terrain_Slope", modality="DEM", description="Mathematical spatial surface gradient derived from DEM", units="degrees (°)", resolution_m=10.0),
        InputBandConfig(index=7, name="Terrain_Aspect", modality="DEM", description="Compass azimuth facing angle of the mountain slope (0°=N, 90°=E)", units="degrees (°)", resolution_m=10.0),
        InputBandConfig(index=8, name="ERA5_Total_Precipitation", modality="ERA5", description="ECMWF ERA5-Land total accumulated precipitation resampled to 10m grid", units="meters water equivalent", resolution_m=10.0),
        InputBandConfig(index=9, name="ERA5_2m_Temperature", modality="ERA5", description="ECMWF ERA5-Land 2-meter air temperature at SAR acquisition epoch", units="Kelvin (K)", resolution_m=10.0),
        InputBandConfig(index=10, name="ERA5_Snow_Depth", modality="ERA5", description="ECMWF ERA5-Land total surface snowpack depth", units="meters (m)", resolution_m=10.0),
    ],
    benchmarks=None,
    scientific_status="Research model. No independent benchmark is registered for this deployment.",
    limitations=[
        "Radar layover and radar shadow in extreme alpine terrain (>60°) can distort backscatter returns.",
        "Widespread wet snow transitions cause bulk dielectric changes across entire mountain faces, requiring ERA5 temperature contextualization.",
        "Spatial resolution limit: Deposits < 200 m² cannot be reliably distinguished from SAR speckle at 10m pixel pitch."
    ]
)


@router.get("/current", response_model=ModelDetails)
def get_current_model_specification():
    """Returns the full architectural specification, 10-band tensor mapping, and measured validation benchmarks for the active model."""
    return _ACTIVE_MODEL


@router.get("/registry", response_model=ModelVersionRegistry)
def list_registered_models():
    """Lists all available model checkpoints and versions in the AvalancheVision model registry."""
    return ModelVersionRegistry(
        active_model_version="U-Net-10Band-v1.0",
        available_models=[_ACTIVE_MODEL]
    )
