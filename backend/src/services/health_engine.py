from ..models.schemas import HealthFactor, HealthIndex, TelemetryProcessed


class HealthEngine:
    def __init__(self) -> None:
        self.weights = {
            "speed": 1.0,
            "traction_force": 1.2,
            "brake_pressure": 1.1,
            "fuel_level": 1.0,
            "voltage": 1.0,
            "current": 1.0,
            "temp_oil": 1.3,
            "temp_engine": 1.5,
        }
        self.normals = {
            "speed": (0, 120),
            "traction_force": (0, 400),
            "brake_pressure": (3, 8),
            "fuel_level": (2000, 10000),
            "voltage": (600, 900),
            "current": (100, 700),
            "temp_oil": (60, 100),
            "temp_engine": (70, 110),
        }

    def compute(self, telemetry: TelemetryProcessed) -> HealthIndex:
        penalties: list[HealthFactor] = []
        weighted_score = 0.0
        total_weight = 0.0

        for key, weight in self.weights.items():
            value = getattr(telemetry, key)
            low, high = self.normals[key]
            score, penalty = self._score_range(value, low, high)
            weighted_score += score * weight
            total_weight += weight
            if penalty > 0:
                penalties.append(HealthFactor(name=key, impact=penalty))

        score = weighted_score / total_weight if total_weight else 0.0
        alert_penalty = min(len(telemetry.alerts) * 5.0, 30.0)
        if alert_penalty:
            penalties.append(HealthFactor(name="alerts", impact=alert_penalty))
        score = max(score - alert_penalty, 0.0)

        status = self._status(score)
        top_factors = sorted(penalties, key=lambda p: p.impact, reverse=True)[:5]

        return HealthIndex(score=round(score, 2), status=status, top_factors=top_factors)

    @staticmethod
    def _score_range(value: float, low: float, high: float) -> tuple[float, float]:
        if low <= value <= high:
            return 100.0, 0.0
        if value < low:
            penalty = min((low - value) / low * 100.0, 100.0)
        else:
            penalty = min((value - high) / high * 100.0, 100.0)
        return max(100.0 - penalty, 0.0), penalty

    @staticmethod
    def _status(score: float) -> str:
        if score >= 80:
            return "normal"
        if score >= 60:
            return "attention"
        return "critical"
