"""Controlled metadata endpoints for processed raster artifacts."""

from io import BytesIO
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import rasterio
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from PIL import Image
from rasterio.enums import Resampling
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds

from backend.core.config import settings
from backend.core.security import require_api_key
from backend.schemas.raster import RasterBandMetadata, RasterMetadata
from geospatial.cog import validate_cog

router = APIRouter(prefix="/rasters", tags=["Raster Data"])

_RASTER_CATALOG: Dict[str, Dict[str, str]] = {
    "feature-stack-10band": {
        "filename": "ml_feature_stack_10band.tif",
        "source": "AvalancheVision multimodal feature stack",
    },
    "risk-probability": {
        "filename": "avalanche_risk_map.tif",
        "source": "U-Net avalanche deposit probability output",
    },
    "automated-labels": {
        "filename": "automated_labels.tif",
        "source": "Automated research labels",
    },
    "sar-pre-event": {
        "filename": "S1A_IW_ARD_1SDV_20240103T053521_20240103T053546_051938_06467F_D006.tif",
        "source": "Sentinel-1 pre-event ARD raster",
        "acquisition_date": "2024-01-03",
    },
    "sar-post-event": {
        "filename": "S1A_IW_ARD_1SDV_20240110T052708_20240110T052733_052040_064A04_2459.tif",
        "source": "Sentinel-1 post-event ARD raster",
        "acquisition_date": "2024-01-10",
    },
}


def _metadata(raster_id: str, entry: Dict[str, str], path: Path) -> RasterMetadata:
    with rasterio.open(path) as dataset:
        source_bounds = [dataset.bounds.left, dataset.bounds.bottom, dataset.bounds.right, dataset.bounds.top]
        geographic_bounds = None
        if dataset.crs:
            geographic_bounds = list(transform_bounds(dataset.crs, "EPSG:4326", *source_bounds))
        bands = []
        for index in range(1, dataset.count + 1):
            tags = dataset.tags(index)
            bands.append(RasterBandMetadata(
                index=index,
                name=tags.get("name", f"band_{index}"),
                units=tags.get("units"),
                dtype=dataset.dtypes[index - 1],
                nodata=dataset.nodatavals[index - 1],
            ))
        cog_status = "COG_READY" if validate_cog(path)["is_cog_ready"] else "NOT_VALIDATED"
        return RasterMetadata(
            raster_id=raster_id,
            source=entry["source"],
            acquisition_date=entry.get("acquisition_date"),
            crs=dataset.crs.to_string() if dataset.crs else None,
            bounds=source_bounds,
            bounds_wgs84=geographic_bounds,
            width=dataset.width,
            height=dataset.height,
            resolution_m=[abs(dataset.transform.a), abs(dataset.transform.e)],
            band_count=dataset.count,
            bands=bands,
            driver=dataset.driver,
            cog_status=cog_status,
        )


def _parse_requested_bounds(
    bbox: Optional[str],
    min_lon: Optional[float],
    min_lat: Optional[float],
    max_lon: Optional[float],
    max_lat: Optional[float],
) -> list[float]:
    if bbox:
        bounds = [float(value.strip()) for value in bbox.split(",")]
    elif None not in (min_lon, min_lat, max_lon, max_lat):
        bounds = [float(min_lon), float(min_lat), float(max_lon), float(max_lat)]
    else:
        raise ValueError("bbox or min/max coordinate parameters are required")

    if len(bounds) != 4 or bounds[0] >= bounds[2] or bounds[1] >= bounds[3]:
        raise ValueError("invalid bounds")
    return bounds


def _looks_like_wgs84(bounds: list[float]) -> bool:
    return -180.0 <= bounds[0] <= 180.0 and -90.0 <= bounds[1] <= 90.0 and -180.0 <= bounds[2] <= 180.0 and -90.0 <= bounds[3] <= 90.0


@router.get("", response_model=list[RasterMetadata])
def list_rasters() -> list[RasterMetadata]:
    """List metadata for approved raster artifacts that currently exist."""
    results = []
    for raster_id, entry in _RASTER_CATALOG.items():
        path = settings.DATA_PROCESSED_DIR / entry["filename"]
        if path.is_file():
            results.append(_metadata(raster_id, entry, path))
    return results


@router.get("/{raster_id}", response_model=RasterMetadata)
def get_raster_metadata(raster_id: str) -> RasterMetadata:
    """Return metadata for one approved raster without exposing its filesystem path."""
    entry = _RASTER_CATALOG.get(raster_id)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Raster '{raster_id}' is not registered.")
    path = settings.DATA_PROCESSED_DIR / entry["filename"]
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"Raster '{raster_id}' is currently unavailable.")
    try:
        return _metadata(raster_id, entry, path)
    except (rasterio.errors.RasterioIOError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="Raster metadata could not be read.") from exc


@router.get("/window/{raster_id}", dependencies=[Depends(require_api_key)])
def get_raster_window(
    raster_id: str,
    bbox: Optional[str] = Query(default=None, description="Bounds as left,bottom,right,top in WGS84 or source CRS"),
    min_lon: Optional[float] = Query(default=None, description="Minimum longitude when bbox is not supplied"),
    min_lat: Optional[float] = Query(default=None, description="Minimum latitude when bbox is not supplied"),
    max_lon: Optional[float] = Query(default=None, description="Maximum longitude when bbox is not supplied"),
    max_lat: Optional[float] = Query(default=None, description="Maximum latitude when bbox is not supplied"),
    width: int = Query(default=512, ge=32, le=2048),
    height: int = Query(default=512, ge=32, le=2048),
) -> Response:
    """Return a bounded first-band PNG window without loading the full raster."""
    entry = _RASTER_CATALOG.get(raster_id)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Raster '{raster_id}' is not registered.")
    path = settings.DATA_PROCESSED_DIR / entry["filename"]
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"Raster '{raster_id}' is currently unavailable.")
    try:
        requested_bounds = _parse_requested_bounds(bbox, min_lon, min_lat, max_lon, max_lat)
        with rasterio.open(path) as dataset:
            source_bounds = requested_bounds
            if dataset.crs and dataset.crs.to_epsg() != 4326 and _looks_like_wgs84(requested_bounds):
                source_bounds = list(transform_bounds("EPSG:4326", dataset.crs, *requested_bounds, densify_pts=21))
            window = from_bounds(*source_bounds, transform=dataset.transform)
            values = dataset.read(
                1,
                window=window,
                out_shape=(height, width),
                resampling=Resampling.bilinear,
                masked=True,
            ).filled(np.nan).astype(np.float32)
        valid = np.isfinite(values)
        if not valid.any():
            pixels = np.zeros((height, width), dtype=np.uint8)
        else:
            low, high = np.nanpercentile(values, [2, 98])
            scale = max(float(high - low), 1e-6)
            pixels = np.clip((values - low) * 255 / scale, 0, 255)
            pixels[~valid] = 0
            pixels = pixels.astype(np.uint8)
        output = BytesIO()
        Image.fromarray(pixels, mode="L").save(output, format="PNG", optimize=True)
        return Response(content=output.getvalue(), media_type="image/png")
    except (ValueError, rasterio.errors.RasterioIOError) as exc:
        raise HTTPException(status_code=422, detail="Raster window could not be read.") from exc