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


class MapPointDTO(BaseModel):
    x: float
    y: float


class TrackMapTemplateDTO(BaseModel):
    id: str
    label: str
    description: str


class TrackMapSectionInputDTO(BaseModel):
    id: str
    name: str
    length_km: float = Field(gt=0.0)
    curve: Literal["straight", "arc_up", "arc_down"] = "straight"
    restricted: bool = False
    speed_limit_kph: int | None = Field(default=None, ge=1)
    station_name: str | None = None


class TrackMapSegmentDTO(BaseModel):
    id: str
    name: str
    start_km: float
    end_km: float
    restricted: bool = False
    speed_limit_kph: int | None = None
    curve: Literal["straight", "arc_up", "arc_down"]
    start: MapPointDTO
    end: MapPointDTO
    control1: MapPointDTO | None = None
    control2: MapPointDTO | None = None
    path: str


class TrackMapStationDTO(BaseModel):
    id: str
    name: str
    km: float
    segment_id: str
    point: MapPointDTO
    angle_deg: float


class TrackMapRestrictionDTO(BaseModel):
    id: str
    label: str
    km: float
    segment_id: str
    point: MapPointDTO
    severity: Literal["warning", "critical"]
    speed_limit_kph: int


class TrackMapLocomotiveDTO(BaseModel):
    segment_id: str
    progress: float = Field(ge=0.0, le=1.0)
    position_km: float = Field(ge=0.0)
    heading_deg: float
    point: MapPointDTO


class TrackMapLayoutDTO(BaseModel):
    template_id: str
    template_label: str
    current_section: str
    viewport_width: int = Field(ge=320)
    viewport_height: int = Field(ge=200)
    total_distance_km: float = Field(ge=0.0)
    templates: list[TrackMapTemplateDTO]
    segments: list[TrackMapSegmentDTO]
    stations: list[TrackMapStationDTO]
    restrictions: list[TrackMapRestrictionDTO]
    locomotive: TrackMapLocomotiveDTO


class TrackMapBuilderRequestDTO(BaseModel):
    template_id: str | None = None
    template_label: str | None = None
    position_km: float = Field(default=0.0, ge=0.0)
    current_section: str | None = None
    sections: list[TrackMapSectionInputDTO]
