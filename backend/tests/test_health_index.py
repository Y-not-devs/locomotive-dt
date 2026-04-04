from datetime import UTC, datetime
from pathlib import Path

from app.domain.models import AlertEvent, AlertSeverity, TelemetrySample
from backend.app.services.health_config_store.health_config_store import HealthConfigStore
from backend.app.services.health_index.health_index import HealthIndexService


def _build_service() -> HealthIndexService:
    config_store = HealthConfigStore(
        config_path=Path(__file__).resolve().parents[1] / "app" / "config" / "health_index.json"
    )
    return HealthIndexService(config_store=config_store)


def test_health_index_penalizes_alerts() -> None:
    service = _build_service()
    sample = TelemetrySample(
        locomotive_id="KZ-LOC-001",
        recorded_at=datetime.now(UTC),
        speed_kph=70,
        fuel_level_pct=65,
        traction_current_a=430,
        battery_voltage_v=106,
        brake_pressure_bar=6.1,
        engine_temp_c=82,
        route_section="Mainline-A",
        position_km=14.2,
    )
    healthy = service.evaluate(sample=sample, alerts=[])
    degraded = service.evaluate(
        sample=sample,
        alerts=[
            AlertEvent(
                code="ENGINE_TEMP_HIGH",
                severity=AlertSeverity.CRITICAL,
                message="Critical engine temperature",
                recorded_at=sample.recorded_at,
                source_metric="engine_temp_c",
            )
        ],
    )

    assert degraded.score < healthy.score
