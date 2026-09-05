-- database/init_schema.sql
CREATE EXTENSION IF NOT EXISTS postgis;

-- Vectorized Avalanche Hazard Polygons
CREATE TABLE IF NOT EXISTS hazard_predictions (
    id BIGSERIAL PRIMARY KEY,
    acquisition_timestamp TIMESTAMPTZ NOT NULL,
    risk_score FLOAT NOT NULL,
    model_version VARCHAR(32) NOT NULL,
    geom GEOMETRY(Polygon, 4326) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Spatial GiST Index for bounding-box intersecting sub-millisecond queries
CREATE INDEX IF NOT EXISTS idx_hazard_predictions_geom 
ON hazard_predictions USING GIST (geom);

-- Temporal Index for tile slicing
CREATE INDEX IF NOT EXISTS idx_hazard_predictions_time 
ON hazard_predictions (acquisition_timestamp DESC);