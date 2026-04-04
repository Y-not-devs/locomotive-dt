CREATE TABLE IF NOT EXISTS telemetry_points (
    id UUID PRIMARY KEY,
    locomotive_id VARCHAR(64) NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    speed_kph DOUBLE PRECISION NOT NULL,
    fuel_level_pct DOUBLE PRECISION NOT NULL,
    traction_current_a DOUBLE PRECISION NOT NULL,
    battery_voltage_v DOUBLE PRECISION NOT NULL,
    brake_pressure_bar DOUBLE PRECISION NOT NULL,
    engine_temp_c DOUBLE PRECISION NOT NULL,
    route_section VARCHAR(128) NOT NULL,
    position_km DOUBLE PRECISION NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_telemetry_points_locomotive_recorded_at
    ON telemetry_points (locomotive_id, recorded_at DESC);

CREATE TABLE IF NOT EXISTS alert_events (
    id UUID PRIMARY KEY,
    locomotive_id VARCHAR(64) NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    code VARCHAR(64) NOT NULL,
    severity VARCHAR(32) NOT NULL,
    message TEXT NOT NULL,
    source_metric VARCHAR(64)
);

CREATE INDEX IF NOT EXISTS idx_alert_events_locomotive_recorded_at
    ON alert_events (locomotive_id, recorded_at DESC);

CREATE TABLE IF NOT EXISTS health_snapshots (
    id UUID PRIMARY KEY,
    locomotive_id VARCHAR(64) NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    score DOUBLE PRECISION NOT NULL,
    category VARCHAR(32) NOT NULL,
    top_factors JSONB NOT NULL DEFAULT '[]'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_health_snapshots_locomotive_recorded_at
    ON health_snapshots (locomotive_id, recorded_at DESC);

CREATE TABLE IF NOT EXISTS health_index_configs (
    key VARCHAR(64) PRIMARY KEY,
    payload JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
