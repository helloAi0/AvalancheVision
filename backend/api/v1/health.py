"""FastAPI health check, diagnostics, and Region of Interest metadata endpoints."""

import torch
from fastapi import APIRouter
from backend.core.config import settings
from backend.repositories.database import check_connection, is_sqlite_mode
from backend.schemas.system import SystemHealthResponse, RegionOfInterest

router = APIRouter(tags=["System Health & Diagnostics"])

_ACTIVE_AOI = RegionOfInterest(
    id="davos-fluela",
    name="Davos Flüela Pass, Swiss Alps",
    country="Switzerland",
    mountain_range="Graubünden Alps",
    center_lon=9.83,
    center_lat=46.80,
    default_zoom=12,
    bbox_wgs84=[9.75, 46.75, 9.90, 46.88],
    utm_epsg=32632,
    dem_coverage=True,
    sar_coverage=True,
    era5_coverage=True,
)


@router.get("/health", response_model=SystemHealthResponse)
def get_system_health():
    """Liveness probe returning system status, device info, database connection state, and storage checks."""
    cuda = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if cuda else "CPU"
    database_connected = check_connection()

    storage_checks = {
        "raw_dir_exists": settings.DATA_RAW_DIR.exists(),
        "processed_dir_exists": settings.DATA_PROCESSED_DIR.exists(),
        "feature_stack_exists": (settings.DATA_PROCESSED_DIR / "ml_feature_stack_10band.tif").exists(),
        "checkpoint_exists": (settings.DATA_PROCESSED_DIR / "unet_avalanche.pth").exists(),
        "geojson_exists": (settings.DATA_PROCESSED_DIR / "high_risk_zones.geojson").exists(),
    }

    return SystemHealthResponse(
        status="HEALTHY" if database_connected else "DEGRADED",
        version=settings.VERSION,
        pytorch_version=torch.__version__,
        device=str(device_name),
        cuda_available=cuda,
        database_status="CONNECTED" if database_connected else "UNAVAILABLE",
        database_type="SQLite (Standalone Mode)" if is_sqlite_mode() else "PostgreSQL / PostGIS",
        active_aoi=_ACTIVE_AOI,
        storage_status=storage_checks,
        active_model="U-Net-10Band-v1.0"
    )


@router.get("/health/aoi", response_model=RegionOfInterest)
def get_active_aoi():
    """Returns spatial bounding box and metadata for the active Region of Interest."""
    return _ACTIVE_AOI
