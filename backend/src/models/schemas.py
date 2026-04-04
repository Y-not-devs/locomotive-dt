from typing import List

from pydantic import BaseModel, Field


class TelemetryIn(BaseModel):
    timestamp: int
    speed: float
    traction_force: float
    brake_pressure: float
    fuel_level: float
    voltage: float
    current: float
    temp_oil: float
    temp_engine: float
    alerts: List[str] = Field(default_factory=list)


class TelemetryProcessed(TelemetryIn):
    pass


class HealthFactor(BaseModel):
    name: str
    impact: float


class HealthIndex(BaseModel):
    score: float
    status: str
    top_factors: List[HealthFactor]


class TelemetryOut(BaseModel):
    telemetry: TelemetryProcessed
    health: HealthIndex

    @classmethod
    def from_parts(
        cls, telemetry: TelemetryProcessed, health: HealthIndex
    ) -> "TelemetryOut":
        return cls(telemetry=telemetry, health=health)
