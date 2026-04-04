from __future__ import annotations

import json
from pathlib import Path

from app.schemas.contracts import HealthIndexConfigDTO


class HealthConfigStore:
    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config = self._load()

    def _load(self) -> HealthIndexConfigDTO:
        if not self._config_path.exists():
            default_config = HealthIndexConfigDTO(
                thresholds={"normal": 80, "warning": 55, "critical": 0},
                metrics={},
                alert_penalties={},
            )
            self.update(default_config)
            return default_config

        payload = json.loads(self._config_path.read_text(encoding="utf-8"))
        return HealthIndexConfigDTO.model_validate(payload)

    def get(self) -> HealthIndexConfigDTO:
        return self._config

    def update(self, config: HealthIndexConfigDTO) -> HealthIndexConfigDTO:
        self._config = config
        self._config_path.write_text(
            config.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return self._config
