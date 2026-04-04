# Locomotive Digital Twin

Initial project skeleton for the case "Visual locomotive digital twin with health index and streaming telemetry".

The repository is split into a frontend built with Feature-Sliced Design and a backend built around FastAPI, WebSocket streaming, OpenAPI, and SQLite persistence.

## Stack

- Frontend: React + TypeScript + Vite
- Realtime: WebSocket
- Backend: FastAPI + Python
- API docs: Swagger / OpenAPI
- Storage: SQLite
- Infra: Docker Compose

## Product Scope From The Spec

- Live telemetry dashboard with speed, fuel or energy, pressure, temperature, electrical values, and alerts
- Health index with transparent scoring and top contributing factors
- Route or section overview
- Short-term replay window and report export entry points
- Low-latency data delivery with reconnect support and simulator-based demo mode

## Repository Layout

```text
.
|-- backend/                 # FastAPI service, WebSocket hub, domain services
|-- docs/                    # Architecture and FSD notes
|-- frontend/                # React app structured with Feature-Sliced Design
|-- infra/                   # Infrastructure notes
|-- docker-compose.yml
`-- .env.example
```

## FSD Frontend Layers

- `app`: application bootstrap, providers, routes, global styles
- `pages`: route-level pages
- `widgets`: large dashboard blocks such as health, telemetry grid, route monitor, replay
- `features`: user actions such as export, thresholds editing, connection state handling
- `entities`: domain models for telemetry, alerts, route sections, health index
- `shared`: api client, config, utilities, reusable primitives

More detail lives in [docs/fsd-design.md](docs/fsd-design.md).

## Quick Start

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.

Local development flow after installing toolchains:

```bash
# backend
cd backend
copy ..\.env.example .env
python -m venv .venv
.venv\Scripts\activate
pip install -r ..\requirements.txt
uvicorn backend.src.main:app --reload

# frontend
cd frontend
copy .env.example .env
npm install
npm run dev
```

## Current State

This is an initial skeleton:

- FastAPI app exposes REST and WebSocket entry points
- health index calculation and simulator are scaffolded
- SQLite persistence is enabled and ready for demo data
- React FSD structure is in place with dashboard-oriented widgets and domain entities

## Next Implementation Steps

1. Replace placeholder UI with real charts and route visualization.
2. Extend telemetry persistence and retention policies in SQLite.
3. Add auth for settings routes and report export.
4. Add replay queries and CSV or PDF export implementation.
