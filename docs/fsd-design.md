# FSD Design For The Locomotive Digital Twin

## Why This Structure

The case requires a single cockpit-style dashboard, live telemetry delivery, a transparent health score, historical replay, and short-term storage. The project is split into a dashboard-centric frontend and a domain-oriented backend so the demo can evolve into a production-grade system without a rewrite.

## Frontend FSD Mapping

### `app`

Application bootstrap, providers, routes, global theme, and layout policy.

### `pages`

Route-level compositions. The first page is `cabin`, which assembles the real-time dashboard.

### `widgets`

Large business blocks that match the spec:

- `health-overview`: health index, category, top factors
- `telemetry-grid`: speed, fuel or energy, pressure, temperature, electric state, active alerts
- `route-monitor`: current section, restriction markers, route overview
- `replay-timeline`: replay range, playback status, report export entry

### `features`

Actions initiated by the operator:

- `connection-status`: reconnect and offline state presentation
- `threshold-settings`: edit thresholds and weights without redeploy
- `export-report`: start report export for the selected replay window

### `entities`

Core domain types used across widgets and features:

- `telemetry`
- `health-index`
- `alert`
- `route`

### `shared`

Reusable api contracts, config, and lightweight helpers. No business logic should leak upward from `shared`.

## Backend Contexts

The backend is organized by business capabilities instead of technical layers only:

- `api`: REST and WebSocket entry points
- `core`: config, db, logging
- `domain`: domain entities and enums
- `schemas`: public request and response contracts
- `repositories`: persistence interfaces and adapters
- `services`: telemetry hub, simulator, health index, replay orchestration
- `db`: persistence models and bootstrap for PostgreSQL

## Realtime Flow

1. Simulator or upstream source pushes telemetry samples.
2. Sample is normalized and validated.
3. Health index service calculates score, category, and factor contributions.
4. Snapshot is buffered for short replay windows.
5. WebSocket hub broadcasts live updates to dashboard clients.
6. REST endpoints expose history, configuration, and health checks.

## Core Domain Decisions

- Health index is explicit and explainable.
- Thresholds and weights are configuration-driven.
- Replay is based on short-lived recent history first.
- PostgreSQL stores telemetry, alerts, and health snapshots.
- WebSocket is the primary real-time transport.

## Health Index Skeleton

The initial formula is intentionally transparent:

- normalize each metric to a `0..1` quality score
- apply business weights from config
- subtract alert penalties
- clamp the final score to `0..100`
- map score to `normal`, `warning`, or `critical`

## Suggested Near-Term Roadmap

1. Wire PostgreSQL repositories into the live path.
2. Replace placeholder widgets with charting and map libraries.
3. Add auth for settings and report endpoints.
4. Add replay queries and export jobs.
5. Add metrics, tracing, and load-test scenario automation.
