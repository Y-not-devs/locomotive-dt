from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.models import AlertSeverity, HealthCategory


class HealthFactorDTO(BaseModel):
    key: str
    label: str
    weight: float
    normalized_value: float = Field(ge=0.0, le=1.0)
    contribution: float = Field(ge=0.0)


class HealthSnapshotDTO(BaseModel):
    score: float = Field(ge=0.0, le=100.0)
    category: HealthCategory
    top_factors: list[HealthFactorDTO]


class TelemetryPointDTO(BaseModel):
    id: UUID
    locomotive_id: str
    recorded_at: datetime
    speed_kph: float
    fuel_level_pct: float
    traction_current_a: float
    battery_voltage_v: float
    brake_pressure_bar: float
    engine_temp_c: float
    route_section: str
    position_km: float


class AlertDTO(BaseModel):
    id: UUID
    code: str
    severity: AlertSeverity
    message: str
    recorded_at: datetime
    source_metric: str | None = None


class LiveTelemetryEnvelopeDTO(BaseModel):
    telemetry: TelemetryPointDTO
    health: HealthSnapshotDTO
    alerts: list[AlertDTO] = Field(default_factory=list)
    replay_available_seconds: int = 0


class ReplayWindowDTO(BaseModel):
    locomotive_id: str
    seconds: int
    items: list[LiveTelemetryEnvelopeDTO]


class HealthMetricConfigDTO(BaseModel):
    label: str
    weight: float = Field(gt=0.0)
    min_value: float
    max_value: float
    target_direction: Literal["high", "low", "band"]
    optimal_min: float | None = None
    optimal_max: float | None = None


class HealthIndexConfigDTO(BaseModel):
    thresholds: dict[str, float]
    metrics: dict[str, HealthMetricConfigDTO]
    alert_penalties: dict[str, float]
