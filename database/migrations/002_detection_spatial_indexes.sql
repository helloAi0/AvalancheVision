-- Production spatial indexes for hazard polygon filtering and temporal SAR slicing.
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE INDEX IF NOT EXISTS idx_hazard_predictions_geom_gist
    ON hazard_predictions USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_hazard_predictions_acquisition_timestamp
    ON hazard_predictions (acquisition_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_hazard_predictions_risk_score
    ON hazard_predictions (risk_score DESC);

COMMENT ON INDEX idx_hazard_predictions_geom_gist IS
    'PostGIS bounding-box and spatial predicate index for agency GIS workloads';