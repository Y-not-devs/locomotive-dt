from __future__ import annotations

from collections.abc import Iterable

from fastapi import WebSocket, WebSocketDisconnect

from app.domain.models import AlertEvent, HealthSnapshot, TelemetrySample
from app.repositories.telemetry import InMemoryTelemetryRepository
from app.schemas.contracts import AlertDTO, HealthFactorDTO, HealthSnapshotDTO, LiveTelemetryEnvelopeDTO, TelemetryPointDTO
from backend.app.services.health_index.health_index import HealthIndexService


class TelemetryHub:
    def __init__(
        self,
        *,
        repository: InMemoryTelemetryRepository,
        health_index_service: HealthIndexService,
        replay_available_seconds: int,
    ) -> None:
        self._repository = repository
        self._health_index_service = health_index_service
        self._replay_available_seconds = replay_available_seconds
        self._connections: set[WebSocket] = set()

    async def serve(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

        latest = await self._repository.latest()
        if latest is not None:
            await websocket.send_json(latest.model_dump(mode="json"))

        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            self._connections.discard(websocket)

    async def ingest(self, sample: TelemetrySample, alerts: list[AlertEvent]) -> LiveTelemetryEnvelopeDTO:
        snapshot = self._health_index_service.evaluate(sample=sample, alerts=alerts)
        envelope = self._build_envelope(sample=sample, health=snapshot, alerts=alerts)
        await self._repository.save_live_envelope(envelope)
        await self._broadcast(envelope)
        return envelope

    async def _broadcast(self, envelope: LiveTelemetryEnvelopeDTO) -> None:
        stale_connections: list[WebSocket] = []
        payload = envelope.model_dump(mode="json")

        for connection in self._connections:
            try:
                await connection.send_json(payload)
            except RuntimeError:
                stale_connections.append(connection)

        for connection in stale_connections:
            self._connections.discard(connection)

    def _build_envelope(
        self,
        *,
        sample: TelemetrySample,
        health: HealthSnapshot,
        alerts: Iterable[AlertEvent],
    ) -> LiveTelemetryEnvelopeDTO:
        telemetry_payload = TelemetryPointDTO(
            id=sample.id,
            locomotive_id=sample.locomotive_id,
            recorded_at=sample.recorded_at,
            speed_kph=sample.speed_kph,
            fuel_level_pct=sample.fuel_level_pct,
            traction_current_a=sample.traction_current_a,
            battery_voltage_v=sample.battery_voltage_v,
            brake_pressure_bar=sample.brake_pressure_bar,
            engine_temp_c=sample.engine_temp_c,
            route_section=sample.route_section,
            position_km=sample.position_km,
        )
        health_payload = HealthSnapshotDTO(
            score=health.score,
            category=health.category,
            top_factors=[
                HealthFactorDTO(
                    key=factor.key,
                    label=factor.label,
                    weight=factor.weight,
                    normalized_value=factor.normalized_value,
                    contribution=factor.contribution,
                )
                for factor in health.top_factors
            ],
        )
        alerts_payload = [
            AlertDTO(
                id=alert.id,
                code=alert.code,
                severity=alert.severity,
                message=alert.message,
                recorded_at=alert.recorded_at,
                source_metric=alert.source_metric,
            )
            for alert in alerts
        ]

        return LiveTelemetryEnvelopeDTO(
            telemetry=telemetry_payload,
            health=health_payload,
            alerts=alerts_payload,
            replay_available_seconds=self._replay_available_seconds,
        )
