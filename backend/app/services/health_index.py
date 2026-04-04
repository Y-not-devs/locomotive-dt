from __future__ import annotations

from app.domain.models import AlertEvent, HealthCategory, HealthFactor, HealthSnapshot, TelemetrySample
from app.schemas.contracts import HealthIndexConfigDTO
from app.services.health_config_store import HealthConfigStore


class HealthIndexService:
    def __init__(self, config_store: HealthConfigStore) -> None:
        self._config_store = config_store

    def evaluate(self, sample: TelemetrySample, alerts: list[AlertEvent]) -> HealthSnapshot:
        config = self._config_store.get()
        quality_points = 0.0
        total_weight = 0.0
        factors: list[HealthFactor] = []

        for metric_name, metric_config in config.metrics.items():
            current_value = getattr(sample, metric_name)
            normalized = self._normalize_value(
                value=current_value,
                minimum=metric_config.min_value,
                maximum=metric_config.max_value,
                target_direction=metric_config.target_direction,
                optimal_min=metric_config.optimal_min,
                optimal_max=metric_config.optimal_max,
            )
            total_weight += metric_config.weight
            quality_points += normalized * metric_config.weight * 100.0
            factors.append(
                HealthFactor(
                    key=metric_name,
                    label=metric_config.label,
                    weight=metric_config.weight,
                    normalized_value=round(normalized, 3),
                    contribution=round((1.0 - normalized) * metric_config.weight * 100.0, 2),
                )
            )

        base_score = quality_points / total_weight if total_weight else 100.0
        penalty = sum(config.alert_penalties.get(alert.severity.value, 0.0) for alert in alerts)
        score = max(0.0, min(100.0, round(base_score - penalty, 2)))
        category = self._categorize(score=score, config=config)
        top_factors = sorted(factors, key=lambda item: item.contribution, reverse=True)[:5]

        return HealthSnapshot(
            locomotive_id=sample.locomotive_id,
            recorded_at=sample.recorded_at,
            score=score,
            category=category,
            top_factors=top_factors,
        )

    def _categorize(self, score: float, config: HealthIndexConfigDTO) -> HealthCategory:
        normal_threshold = config.thresholds.get("normal", 80)
        warning_threshold = config.thresholds.get("warning", 55)

        if score >= normal_threshold:
            return HealthCategory.NORMAL
        if score >= warning_threshold:
            return HealthCategory.WARNING
        return HealthCategory.CRITICAL

    @staticmethod
    def _normalize_value(
        *,
        value: float,
        minimum: float,
        maximum: float,
        target_direction: str,
        optimal_min: float | None,
        optimal_max: float | None,
    ) -> float:
        span = maximum - minimum
        if span <= 0:
            return 1.0

        clamped = max(minimum, min(maximum, value))

        if target_direction == "high":
            return (clamped - minimum) / span

        if target_direction == "low":
            return (maximum - clamped) / span

        if optimal_min is None or optimal_max is None:
            return 1.0

        if optimal_min <= clamped <= optimal_max:
            return 1.0

        if clamped < optimal_min:
            distance = optimal_min - clamped
            penalty_span = max(optimal_min - minimum, 1e-6)
            return max(0.0, 1.0 - distance / penalty_span)

        distance = clamped - optimal_max
        penalty_span = max(maximum - optimal_max, 1e-6)
        return max(0.0, 1.0 - distance / penalty_span)
