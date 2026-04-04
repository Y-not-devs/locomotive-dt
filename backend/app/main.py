from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.ws import router as ws_router
from app.core.config import get_settings
from app.dependencies import create_container


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = create_container()
    app.state.container = container

    if container.settings.simulator_enabled:
        container.simulator_task = asyncio.create_task(container.simulator.run())

    try:
        yield
    finally:
        await container.shutdown()


settings = get_settings()
app = FastAPI(
    title=settings.app_title,
    version="0.1.0",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)
app.include_router(ws_router)
