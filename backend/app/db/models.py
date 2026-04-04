from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class TelemetryPointRecord(Base):
    __tablename__ = "telemetry_points"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    locomotive_id: Mapped[str] = mapped_column(String(64), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), index=True)
    speed_kph: Mapped[float] = mapped_column(Float)
    fuel_level_pct: Mapped[float] = mapped_column(Float)
    traction_current_a: Mapped[float] = mapped_column(Float)
    battery_voltage_v: Mapped[float] = mapped_column(Float)
    brake_pressure_bar: Mapped[float] = mapped_column(Float)
    engine_temp_c: Mapped[float] = mapped_column(Float)
    route_section: Mapped[str] = mapped_column(String(128))
    position_km: Mapped[float] = mapped_column(Float)


class AlertEventRecord(Base):
    __tablename__ = "alert_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    locomotive_id: Mapped[str] = mapped_column(String(64), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), index=True)
    code: Mapped[str] = mapped_column(String(64))
    severity: Mapped[str] = mapped_column(String(32))
    message: Mapped[str] = mapped_column(Text)
    source_metric: Mapped[str | None] = mapped_column(String(64), nullable=True)


class HealthSnapshotRecord(Base):
    __tablename__ = "health_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    locomotive_id: Mapped[str] = mapped_column(String(64), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), index=True)
    score: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String(32))
    top_factors: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
