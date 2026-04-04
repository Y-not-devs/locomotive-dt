from fastapi import APIRouter

from app.api.routes.config import router as config_router
from app.api.routes.health import router as health_router
from app.api.routes.history import router as history_router
from app.api.routes.track_map import router as track_map_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(history_router, tags=["telemetry"])
api_router.include_router(config_router, tags=["config"])
api_router.include_router(track_map_router, tags=["track-map"])
