# Backend Skeleton

This FastAPI service exposes:

- REST endpoints for health, recent telemetry, replay, and health-index config
- WebSocket endpoint for live telemetry
- simulator-driven live data for demo mode
- SQLite-ready schema and SQLAlchemy bootstrap

The current repository uses an in-memory repository on the hot path so the demo can run before persistence is fully wired.
