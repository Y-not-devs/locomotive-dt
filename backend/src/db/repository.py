import json
import sqlite3
import time
from pathlib import Path

from ..core.config import settings
from ..models.schemas import HealthIndex, TelemetryOut, TelemetryProcessed


class TelemetryRepository:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = Path(db_path or settings.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def save(self, payload: TelemetryOut) -> None:
        self.save_many([payload])

    def save_many(self, payloads: list[TelemetryOut]) -> None:
        if not payloads:
            return

        rows: list[tuple[int, str, str]] = []
        for payload in payloads:
            telemetry_json = payload.telemetry.model_dump_json()
            health_json = payload.health.model_dump_json()
            timestamp = payload.telemetry.timestamp
            rows.append((timestamp, telemetry_json, health_json))

        with self._connect() as connection:
            connection.executemany(
                """
                INSERT INTO telemetry_records (ts, telemetry_json, health_json)
                VALUES (?, ?, ?)
                """,
                rows,
            )
            connection.commit()

    def get_history(self, minutes: int = 10) -> list[TelemetryOut]:
        since = int(time.time()) - max(minutes, 1) * 60

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT ts, telemetry_json, health_json
                FROM telemetry_records
                WHERE ts >= ?
                ORDER BY ts ASC
                """,
                (since,),
            ).fetchall()

        history: list[TelemetryOut] = []
        for row in rows:
            telemetry = TelemetryProcessed(**json.loads(row[1]))
            health = HealthIndex(**json.loads(row[2]))
            history.append(TelemetryOut(telemetry=telemetry, health=health))
        return history

    def get_range(
        self, start_ts: int, end_ts: int, limit: int = 1000, offset: int = 0
    ) -> list[TelemetryOut]:
        if end_ts < start_ts:
            return []

        safe_limit = max(1, min(limit, 5000))
        safe_offset = max(0, offset)

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT ts, telemetry_json, health_json
                FROM telemetry_records
                WHERE ts BETWEEN ? AND ?
                ORDER BY ts ASC
                LIMIT ? OFFSET ?
                """,
                (start_ts, end_ts, safe_limit, safe_offset),
            ).fetchall()

        history: list[TelemetryOut] = []
        for row in rows:
            telemetry = TelemetryProcessed(**json.loads(row[1]))
            health = HealthIndex(**json.loads(row[2]))
            history.append(TelemetryOut(telemetry=telemetry, health=health))
        return history

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def get_counts(self) -> dict[str, int]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COUNT(1), COALESCE(MAX(ts), 0) FROM telemetry_records"
            ).fetchone()
        return {"total": int(row[0]), "latest_ts": int(row[1])}

    def get_latest(self) -> TelemetryOut | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT ts, telemetry_json, health_json
                FROM telemetry_records
                ORDER BY ts DESC
                LIMIT 1
                """
            ).fetchone()

        if not row:
            return None

        telemetry = TelemetryProcessed(**json.loads(row[1]))
        health = HealthIndex(**json.loads(row[2]))
        return TelemetryOut(telemetry=telemetry, health=health)

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS telemetry_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts INTEGER NOT NULL,
                    telemetry_json TEXT NOT NULL,
                    health_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_telemetry_ts ON telemetry_records (ts)"
            )
            connection.commit()
