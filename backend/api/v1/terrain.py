from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
from backend.services.terrain_service import TerrainService

router = APIRouter(prefix="/terrain", tags=["Terrain & Geomorphology"])

# Explicitly instantiate the service class to avoid module name collisions
terrain_svc = TerrainService()

class TransectRequest(BaseModel):
    coordinates: List[List[float]] = Field(
        ...,
        description="List of [longitude, latitude] points forming the transect line",
        example=[[9.812, 46.810], [9.835, 46.825]],
    )
    samples: int = Field(default=100, ge=10, le=500, description="Sampling density along profile")

class TransectPoint(BaseModel):
    distance_m: float
    longitude: float
    latitude: float
    elevation_m: float
    slope_degrees: float
    delta_vh_db: float

class TransectResponse(BaseModel):
    total_distance_m: float
    sample_count: int
    profile: List[TransectPoint]

@router.post(
    "/profile",
    response_model=TransectResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate 2D Cross-Sectional Terrain & SAR Profile",
)
async def generate_terrain_profile(payload: TransectRequest):
    """
    Extracts elevation (m), slope angle (degrees), and radar backscatter drop
    along a user-defined transect path across mountain slopes.
    """
    try:
        # Reference the explicitly initialized class instance here
        profile = terrain_svc.extract_transect_profile(
            coordinates=payload.coordinates, num_samples=payload.samples
        )
        total_dist = profile[-1]["distance_m"] if profile else 0.0

        return TransectResponse(
            total_distance_m=total_dist, sample_count=len(profile), profile=profile
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transect processing failed: {str(err)}",
        )