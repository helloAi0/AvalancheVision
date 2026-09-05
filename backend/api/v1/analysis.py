"""Raster-backed analysis endpoints."""

from math import asin, cos, radians, sin, sqrt
import numpy as np
import rasterio
from fastapi import APIRouter, HTTPException
from pyproj import Transformer

from backend.api.v1.rasters import _RASTER_CATALOG
from backend.core.config import settings
from backend.schemas.analysis import ProfilePoint, ProfileRequest, TerrainProfileResponse

router = APIRouter(prefix="/analysis", tags=["Scientific Analysis"])


def _distance_m(first: tuple[float, float], second: tuple[float, float]) -> float:
    earth_radius_m = 6_371_000.0
    lon1, lat1 = map(radians, first)
    lon2, lat2 = map(radians, second)
    delta_lon = lon2 - lon1
    delta_lat = lat2 - lat1
    value = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    return 2 * earth_radius_m * asin(sqrt(value))


@router.post("/profile", response_model=TerrainProfileResponse)
def sample_raster_profile(request: ProfileRequest) -> TerrainProfileResponse:
    """Sample a registered raster along a WGS84 transect without loading the full dataset."""
    entry = _RASTER_CATALOG.get(request.raster_id)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Raster '{request.raster_id}' is not registered.")
    path = settings.DATA_PROCESSED_DIR / entry["filename"]
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"Raster '{request.raster_id}' is currently unavailable.")

    start = (float(request.start[0]), float(request.start[1]))
    end = (float(request.end[0]), float(request.end[1]))
    fractions = np.linspace(0.0, 1.0, request.samples)
    coordinates = [(start[0] + fraction * (end[0] - start[0]), start[1] + fraction * (end[1] - start[1])) for fraction in fractions]

    with rasterio.open(path) as dataset:
        if not dataset.crs:
            raise HTTPException(status_code=422, detail="Raster has no CRS and cannot be sampled geographically.")
        transformer = Transformer.from_crs("EPSG:4326", dataset.crs, always_xy=True)
        source_coordinates = [transformer.transform(lon, lat) for lon, lat in coordinates]
        samples = list(dataset.sample(source_coordinates, indexes=list(range(1, dataset.count + 1)), masked=True))
        names = [dataset.tags(index).get("name", f"band_{index}") for index in range(1, dataset.count + 1)]
        points = []
        total_distance = _distance_m(start, end)
        for index, (coordinate, values) in enumerate(zip(coordinates, samples)):
            values_dict = {}
            for band_name, value in zip(names, values):
                values_dict[band_name] = None if np.ma.is_masked(value) else float(value)
            points.append(ProfilePoint(
                distance_m=total_distance * float(fractions[index]),
                longitude=coordinate[0],
                latitude=coordinate[1],
                values=values_dict,
            ))
        source_crs = dataset.crs.to_string()

    return TerrainProfileResponse(
        raster_id=request.raster_id,
        source_crs=source_crs,
        sample_count=len(points),
        start=list(start),
        end=list(end),
        points=points,
    )
