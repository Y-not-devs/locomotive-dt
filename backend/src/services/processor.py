from ..models.schemas import TelemetryIn, TelemetryProcessed


class TelemetryProcessor:
    def __init__(self, alpha: float = 0.4) -> None:
        self.alpha = alpha
        self._last_values: dict[str, float] = {}
        self._last_signature: tuple[object, ...] | None = None
        self._last_processed: TelemetryProcessed | None = None

    def process(self, telemetry: TelemetryIn) -> tuple[TelemetryProcessed, bool]:
        signature = self._signature(telemetry)
        if signature == self._last_signature and self._last_processed:
            return self._last_processed, True

        data = telemetry.model_dump()
        for field in self._numeric_fields():
            current = data[field]
            previous = self._last_values.get(field)
            if previous is None:
                smoothed = current
            else:
                smoothed = self.alpha * current + (1 - self.alpha) * previous
            self._last_values[field] = smoothed
            data[field] = smoothed
        processed = TelemetryProcessed(**data)
        self._last_signature = signature
        self._last_processed = processed
        return processed, False

    @staticmethod
    def _numeric_fields() -> list[str]:
        return [
            "speed",
            "traction_force",
            "brake_pressure",
            "fuel_level",
            "voltage",
            "current",
            "temp_oil",
            "temp_engine",
        ]

    @staticmethod
    def _signature(telemetry: TelemetryIn) -> tuple[object, ...]:
        return (
            telemetry.timestamp,
            telemetry.speed,
            telemetry.traction_force,
            telemetry.brake_pressure,
            telemetry.fuel_level,
            telemetry.voltage,
            telemetry.current,
            telemetry.temp_oil,
            telemetry.temp_engine,
            tuple(telemetry.alerts),
        )
