from __future__ import annotations

import asyncio
from contextlib import suppress
from dataclasses import dataclass

from fastapi import Request
from starlette.requests import HTTPConnection

from app.core.config import AppSettings, get_settings
from app.repositories.telemetry import InMemoryTelemetryRepository
from app.services.health_config_store import HealthConfigStore
from app.services.health_index import HealthIndexService
from app.services.simulator import TelemetrySimulator
from app.services.telemetry_hub import TelemetryHub


@dataclass(slots=True)
class ApplicationContainer:
    settings: AppSettings
    config_store: HealthConfigStore
    repository: InMemoryTelemetryRepository
    health_index_service: HealthIndexService
    telemetry_hub: TelemetryHub
    simulator: TelemetrySimulator
    simulator_task: asyncio.Task | None = None

    async def shutdown(self) -> None:
        self.simulator.stop()
        if self.simulator_task is not None:
            self.simulator_task.cancel()
            with suppress(asyncio.CancelledError):
                await self.simulator_task


def create_container() -> ApplicationContainer:
    settings = get_settings()
    config_store = HealthConfigStore(settings.health_index_config_path)
    repository = InMemoryTelemetryRepository(max_items=settings.history_buffer_size)
    health_index_service = HealthIndexService(config_store=config_store)
    telemetry_hub = TelemetryHub(
        repository=repository,
        health_index_service=health_index_service,
        replay_available_seconds=settings.history_buffer_size,
    )
    simulator = TelemetrySimulator(
        interval_ms=settings.simulator_interval_ms,
        locomotive_id=settings.simulator_locomotive_id,
        telemetry_hub=telemetry_hub,
    )

    return ApplicationContainer(
        settings=settings,
        config_store=config_store,
        repository=repository,
        health_index_service=health_index_service,
        telemetry_hub=telemetry_hub,
        simulator=simulator,
    )


def get_container(connection: HTTPConnection) -> ApplicationContainer:
    return connection.app.state.container


def get_config_store(request: Request) -> HealthConfigStore:
    return get_container(request).config_store


def get_repository(request: Request) -> InMemoryTelemetryRepository:
    return get_container(request).repository
