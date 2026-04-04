from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta

from app.schemas.contracts import AlertDTO, LiveTelemetryEnvelopeDTO


class InMemoryTelemetryRepository:
    def __init__(self, max_items: int = 900) -> None:
        self._items: deque[LiveTelemetryEnvelopeDTO] = deque(maxlen=max_items)

    async def save_live_envelope(self, envelope: LiveTelemetryEnvelopeDTO) -> None:
        self._items.append(envelope)

    async def list_recent(self, locomotive_id: str, limit: int) -> list[LiveTelemetryEnvelopeDTO]:
        matching = [item for item in self._items if item.telemetry.locomotive_id == locomotive_id]
        return matching[-limit:]

    async def replay_window(self, locomotive_id: str, seconds: int) -> list[LiveTelemetryEnvelopeDTO]:
        cutoff = datetime.now(UTC) - timedelta(seconds=seconds)
        return [
            item
            for item in self._items
            if item.telemetry.locomotive_id == locomotive_id and item.telemetry.recorded_at >= cutoff
        ]

    async def list_active_alerts(self, locomotive_id: str) -> list[AlertDTO]:
        recent_items = await self.list_recent(locomotive_id=locomotive_id, limit=20)
        seen: dict[str, AlertDTO] = {}
        for item in recent_items:
            for alert in item.alerts:
                seen[alert.code] = alert
        return list(seen.values())

    async def latest(self) -> LiveTelemetryEnvelopeDTO | None:
        if not self._items:
            return None
        return self._items[-1]

    async def latest_for_locomotive(self, locomotive_id: str) -> LiveTelemetryEnvelopeDTO | None:
        for item in reversed(self._items):
            if item.telemetry.locomotive_id == locomotive_id:
                return item
        return None

    def __iter__(self) -> Iterable[LiveTelemetryEnvelopeDTO]:
        return iter(self._items)
