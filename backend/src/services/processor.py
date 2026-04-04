from ..models.schemas import TelemetryIn, TelemetryProcessed


class TelemetryProcessor:
    def __init__(self, alpha: float = 0.4) -> None:
        self.alpha = alpha
        self._last_values: dict[str, float] = {}

    def process(self, telemetry: TelemetryIn) -> TelemetryProcessed:
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
        return TelemetryProcessed(**data)

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
