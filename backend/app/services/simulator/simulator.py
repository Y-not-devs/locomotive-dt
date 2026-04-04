from __future__ import annotations

import asyncio
import random
from datetime import UTC, datetime

from app.domain.models import AlertEvent, AlertSeverity, TelemetrySample
from backend.app.services.telemetry_hub.telemetry_hub import TelemetryHub


class TelemetrySimulator:
    def __init__(self, *, interval_ms: int, locomotive_id: str, telemetry_hub: TelemetryHub) -> None:
        self._interval_seconds = interval_ms / 1000
        self._locomotive_id = locomotive_id
        self._telemetry_hub = telemetry_hub
        self._random = random.Random(26)
        self._position_km = 0.0
        self._fuel_level_pct = 82.0
        self._route_sections = ("Depot", "North-Yard", "Mainline-A", "Mainline-B", "Station-3")
        self._stop_event = asyncio.Event()

    async def run(self) -> None:
        while not self._stop_event.is_set():
            sample = self._build_sample()
            alerts = self._build_alerts(sample)
            await self._telemetry_hub.ingest(sample=sample, alerts=alerts)
            await asyncio.sleep(self._interval_seconds)

    def stop(self) -> None:
        self._stop_event.set()

    def _build_sample(self) -> TelemetrySample:
        now = datetime.now(UTC)
        speed = max(0.0, min(120.0, 70 + self._random.uniform(-12, 14)))
        self._position_km += speed / 3600
        self._fuel_level_pct = max(5.0, self._fuel_level_pct - self._random.uniform(0.02, 0.06))
        engine_temp = 78 + self._random.uniform(-3, 18)
        brake_pressure = 6.2 + self._random.uniform(-1.8, 0.4)
        traction_current = 420 + self._random.uniform(-120, 130)
        battery_voltage = 104 + self._random.uniform(-6, 4)
        route_section = self._route_sections[int(self._position_km // 10) % len(self._route_sections)]

        return TelemetrySample(
            locomotive_id=self._locomotive_id,
            recorded_at=now,
            speed_kph=round(speed, 2),
            fuel_level_pct=round(self._fuel_level_pct, 2),
            traction_current_a=round(traction_current, 2),
            battery_voltage_v=round(battery_voltage, 2),
            brake_pressure_bar=round(brake_pressure, 2),
            engine_temp_c=round(engine_temp, 2),
            route_section=route_section,
            position_km=round(self._position_km, 3),
        )

    def _build_alerts(self, sample: TelemetrySample) -> list[AlertEvent]:
        alerts: list[AlertEvent] = []

        if sample.engine_temp_c >= 92:
            alerts.append(
                AlertEvent(
                    code="ENGINE_TEMP_HIGH",
                    severity=AlertSeverity.CRITICAL,
                    message="Engine temperature is above the critical threshold.",
                    recorded_at=sample.recorded_at,
                    source_metric="engine_temp_c",
                )
            )

        if sample.fuel_level_pct <= 18:
            alerts.append(
                AlertEvent(
                    code="FUEL_LOW",
                    severity=AlertSeverity.WARNING,
                    message="Fuel level is below the warning threshold.",
                    recorded_at=sample.recorded_at,
                    source_metric="fuel_level_pct",
                )
            )

        if sample.brake_pressure_bar <= 4.8:
            alerts.append(
                AlertEvent(
                    code="BRAKE_PRESSURE_LOW",
                    severity=AlertSeverity.CRITICAL,
                    message="Brake pressure dropped below the safe operating range.",
                    recorded_at=sample.recorded_at,
                    source_metric="brake_pressure_bar",
                )
            )

        return alerts
