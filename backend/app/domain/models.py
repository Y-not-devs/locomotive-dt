from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4


class HealthCategory(StrEnum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(slots=True)
class TelemetrySample:
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
    id: UUID = field(default_factory=uuid4)


@dataclass(slots=True)
class AlertEvent:
    code: str
    severity: AlertSeverity
    message: str
    recorded_at: datetime
    source_metric: str | None = None
    id: UUID = field(default_factory=uuid4)


@dataclass(slots=True)
class HealthFactor:
    key: str
    label: str
    weight: float
    normalized_value: float
    contribution: float


@dataclass(slots=True)
class HealthSnapshot:
    locomotive_id: str
    recorded_at: datetime
    score: float
    category: HealthCategory
    top_factors: list[HealthFactor]
