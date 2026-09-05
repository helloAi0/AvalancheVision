# AvalancheVision

AvalancheVision is a research-oriented platform for post-event avalanche deposit detection and mapping using multimodal satellite observations. The system fuses Sentinel-1 SAR backscatter change, Copernicus DEM terrain derivatives, and ERA5-Land meteorological context to generate a high-confidence map of avalanche debris polygons.

## Scientific scope

This project is intentionally scoped to avalanche deposit detection and mapping. It is not a real-time avalanche forecast or warning system.

The core signal is based on radar change between a pre-event and post-event Sentinel-1 observation, measured using delta backscatter in dB and conditioned by terrain slope, elevation, and meteorological context.

## Architecture overview

- Backend: FastAPI service with science-focused endpoints for detections, observations, analytics, model metadata, jobs, exports, and health
- Durable local job records: processing submissions and stage transitions are persisted through SQLAlchemy; PostgreSQL remains available for production configuration
- Raster metadata API: approved processed artifacts expose Rasterio-derived CRS, bounds, dimensions, resolution, bands, nodata, and driver metadata without filesystem paths
- Mission Workspace controls: the existing GIS workspace can select available raster artifacts, render CRS-correct bounded windows, inspect metadata, and adjust visibility/opacity
- Explicit live catalogue mode: observation sync can query the Copernicus STAC adapter and labels the returned source; local inventory remains available for offline development
- Raster processing utilities create tiled, compressed GeoTIFFs with internal overviews and expose structural `COG_READY` validation status
- Optional `API_KEY` protection is available for job submission and raster window delivery in staging/production
- Frontend: React + Vite interface with GIS workspace, summary dashboard, analytics, model explorer, and pipeline console
- Geospatial layer: CRS management, morphological filtering, geometry and zonal statistics handling
- Machine learning: 10-band U-Net segmentation model and inference pipeline
- Data stores: SQLite fallback for local use and PostGIS-ready schema support for production deployments

## Local development

### Backend

```bash
python -m venv .venv
. .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

### Optional Docker stack

```bash
copy .env.example .env
# Set POSTGRES_PASSWORD and API_KEY in .env before deployment.
docker compose up --build
```

The Compose stack exposes the frontend at `http://localhost:8080`. Nginx proxies `/api/` and the job WebSocket path to the backend. The backend and worker share PostgreSQL metadata and Redis queue state; large raster/model artifacts should be mounted or provided through the configured artifact store before processing production scenes.

For a production deployment, use a managed PostgreSQL/PostGIS instance, private Redis, TLS termination, a secret manager, restricted `FRONTEND_ORIGINS`, and a non-empty `API_KEY`. The included Compose file is a reproducible single-host deployment baseline, not a claim of high availability or disaster recovery.

## Key API routes

- GET /api/v1/health
- GET /api/v1/detections/geojson
- GET /api/v1/detections/stats
- GET /api/v1/observations
- GET /api/v1/models/current
- GET /api/v1/rasters
- GET /api/v1/rasters/{raster_id}
- GET /api/v1/provenance/{job_id}
- POST /api/v1/analysis/profile
- GET /api/v1/analytics/distributions
- POST /api/v1/jobs/submit
- WS /api/v1/jobs/ws/{job_id}
- GET /api/v1/export/geojson
- GET /api/v1/export/csv

## Research note

The system is designed for reproducible scientific evaluation, with transparent metrics and explicit operational limitations. Outputs are best used in a geospatial review workflow for alpine avalanche deposit mapping rather than in a real-time hazard decision context.

Database migration scripts are stored in `database/migrations/`. The current 2.0 migration adds immutable processing lineage records; production deployments should apply migrations with a reviewed migration runner before starting workers.

## License

MIT
