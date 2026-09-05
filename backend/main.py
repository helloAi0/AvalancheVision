"""FastAPI application factory for AvalancheVision Scientific Platform."""

import os
# Suppress missing file warnings from GDAL when relying on synthetic fallback data
os.environ["CPL_LOG"] = "NUL" 
os.environ["CPL_DEBUG"] = "OFF"

import logging
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.router import api_router
from backend.core.config import settings
from backend.repositories.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("AvalancheVision.App")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for application startup and shutdown."""
    logger.info("Initializing AvalancheVision Scientific Platform backend...")
    settings.create_directories()
    init_db()
    logger.info("AvalancheVision API server is ready.")
    yield
    logger.info("Shutting down AvalancheVision API server...")


def create_application() -> FastAPI:
    """Builds and configures the FastAPI application instance."""
    app = FastAPI(
        title="AvalancheVision Scientific API",
        description=(
            "Physics-informed multimodal satellite-based avalanche debris detection and mapping platform. "
            "Integrates Sentinel-1 C-band SAR backscatter, Copernicus DEM terrain metrics, and ECMWF ERA5-Land weather context."
        ),
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )

    # CORS configuration for local development and production web clients
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.FRONTEND_ORIGINS.split(",") if origin.strip()],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Accept", "Authorization", "Content-Type", "X-Request-ID"],
    )

    # Request timing & logging middleware
    @app.middleware("http")
    async def log_request_time(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Response-Time-Ms"] = str(duration_ms)
        response.headers["X-Request-ID"] = request_id
        return response

    # Global Exception Handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error processing {request.method} {request.url}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "The request could not be completed.",
                "request_id": request.headers.get("X-Request-ID", "unknown"),
            }
        )

    # Include API Routers
    app.include_router(api_router)

    # Root redirect / status
    @app.get("/", tags=["System Root"])
    def root():
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "description": "Multimodal Satellite Avalanche Debris Detection Platform",
            "docs": "/docs",
            "api_v1": settings.API_V1_STR,
            "status": "OPERATIONAL"
        }

    return app


app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
