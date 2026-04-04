from typing import List

from pydantic import BaseModel, Field


class TelemetryIn(BaseModel):
    timestamp: int = Field(ge=0)
    speed: float = Field(ge=0, le=200)
    traction_force: float = Field(ge=0, le=600)
    brake_pressure: float = Field(ge=0, le=12)
    fuel_level: float = Field(ge=0, le=12000)
    voltage: float = Field(ge=0, le=1200)
    current: float = Field(ge=0, le=1200)
    temp_oil: float = Field(ge=-20, le=160)
    temp_engine: float = Field(ge=-20, le=180)
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
