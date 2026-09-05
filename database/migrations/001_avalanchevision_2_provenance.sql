-- AvalancheVision 2.0 initial lineage migration.
-- Apply with a migration runner after the baseline schema is backed up.

CREATE TABLE IF NOT EXISTS provenance_events (
    id BIGSERIAL PRIMARY KEY,
    job_id VARCHAR(64),
    event_type VARCHAR(64) NOT NULL,
    stage VARCHAR(64),
    source_id VARCHAR(256),
    artifact_id VARCHAR(256),
    model_version VARCHAR(64),
    parameters_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_provenance_events_job_created
    ON provenance_events (job_id, created_at);

COMMENT ON TABLE provenance_events IS
    'Immutable lineage events for AvalancheVision processing and scientific outputs';
