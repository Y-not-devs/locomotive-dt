import csv
import io
import json
import time

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..db.repository import TelemetryRepository
from ..core.config import settings
from ..models.schemas import TelemetryIn, TelemetryOut
from ..services.ingest_buffer import ingest_buffer
from ..services.health_engine import HealthEngine
from ..services.processor import TelemetryProcessor

repository = TelemetryRepository()
processor = TelemetryProcessor()
engine = HealthEngine()

router = APIRouter()
STARTED_AT = time.time()


def _require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


def _to_csv_rows(items: list[TelemetryOut]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in items:
        telemetry = item.telemetry.model_dump()
        health = item.health.model_dump()
        row = {
            **telemetry,
            "health_score": health["score"],
            "health_status": health["status"],
            "health_top_factors": json.dumps(health["top_factors"]),
        }
        rows.append(row)
    return rows


def _stream_csv(rows: list[dict[str, object]]) -> StreamingResponse:
    if not rows:
        rows = []

    output = io.StringIO()
    fieldnames = list(rows[0].keys()) if rows else []
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    if fieldnames:
        writer.writeheader()
        writer.writerows(rows)

    output.seek(0)
    return StreamingResponse(
        iter([output.read()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=telemetry.csv"},
    )


def _build_pdf(items: list[TelemetryOut]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    total = len(items)
    avg_score = (
        sum(item.health.score for item in items) / total if total else 0.0
    )
    factor_totals: dict[str, float] = {}
    for item in items:
        for factor in item.health.top_factors:
            factor_totals[factor.name] = factor_totals.get(factor.name, 0.0) + factor.impact
    top_factors = sorted(
        factor_totals.items(), key=lambda entry: entry[1], reverse=True
    )[:5]

    elements = [
        Paragraph("Telemetry Report", styles["Title"]),
        Spacer(1, 8),
        Paragraph(f"Records: {total}", styles["Normal"]),
        Paragraph(f"Avg health score: {avg_score:.2f}", styles["Normal"]),
        Paragraph(
            "Top factors: "
            + ", ".join(
                f"{name} ({impact:.1f})" for name, impact in top_factors
            )
            if top_factors
            else "Top factors: n/a",
            styles["Normal"],
        ),
        Spacer(1, 6),
        Paragraph("Status legend:", styles["Normal"]),
        Paragraph("- normal: score >= 80", styles["Normal"]),
        Paragraph("- attention: score >= 60", styles["Normal"]),
        Paragraph("- critical: score < 60", styles["Normal"]),
        Spacer(1, 12),
    ]

    data = [
        [
            "timestamp",
            "speed",
            "fuel_level",
            "temp_engine",
            "health_score",
            "health_status",
        ]
    ]
    for item in items:
        telemetry = item.telemetry
        health = item.health
        data.append(
            [
                telemetry.timestamp,
                round(telemetry.speed, 2),
                round(telemetry.fuel_level, 2),
                round(telemetry.temp_engine, 2),
                round(health.score, 2),
                health.status,
            ]
        )

    table = Table(data, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    elements.append(table)
    doc.build(elements)
    return buffer.getvalue()


@router.get("/health", dependencies=[Depends(_require_api_key)])
def health() -> dict:
    return {"status": "ok"}


@router.get("/metrics", dependencies=[Depends(_require_api_key)])
def metrics() -> dict:
    counts = repository.get_counts()
    latest = repository.get_latest()
    now = int(time.time())
    driver_view = None
    if latest:
        driver_view = {
            "speed": latest.telemetry.speed,
            "traction_force": latest.telemetry.traction_force,
            "brake_pressure": latest.telemetry.brake_pressure,
            "fuel_level": latest.telemetry.fuel_level,
            "voltage": latest.telemetry.voltage,
            "current": latest.telemetry.current,
            "temp_engine": latest.telemetry.temp_engine,
            "temp_oil": latest.telemetry.temp_oil,
            "alerts": latest.telemetry.alerts,
            "health_score": latest.health.score,
            "health_status": latest.health.status,
            "health_top_factors": [
                factor.model_dump() for factor in latest.health.top_factors
            ],
        }

    return {
        "uptime_sec": int(now - STARTED_AT),
        "records_total": counts["total"],
        "latest_ts": counts["latest_ts"],
        "last_ingest_age_sec": now - counts["latest_ts"] if counts["latest_ts"] else None,
        "latest": latest.model_dump() if latest else None,
        "driver_view": driver_view,
    }


@router.get("/history", dependencies=[Depends(_require_api_key)])
def history(minutes: int = Query(default=10, ge=1, le=60)) -> dict:
    items = [item.model_dump() for item in repository.get_history(minutes)]
    return {"items": items}


@router.get("/history/range", dependencies=[Depends(_require_api_key)])
def history_range(
    start_ts: int = Query(..., description="Unix timestamp (seconds)"),
    end_ts: int = Query(..., description="Unix timestamp (seconds)"),
    limit: int = Query(default=1000, ge=1, le=5000),
    offset: int = Query(default=0, ge=0),
) -> dict:
    items = [
        item.model_dump()
        for item in repository.get_range(start_ts, end_ts, limit, offset)
    ]
    return {"items": items}


@router.post("/telemetry", dependencies=[Depends(_require_api_key)])
async def ingest_telemetry(payload: TelemetryIn) -> dict:
    processed, is_duplicate = processor.process(payload)
    health = engine.compute(processed)
    telemetry_out = TelemetryOut.from_parts(processed, health)
    if not is_duplicate:
        await ingest_buffer.enqueue(telemetry_out)
    return telemetry_out.model_dump()


@router.get("/history/export/csv", dependencies=[Depends(_require_api_key)])
def export_history_csv(
    start_ts: int | None = Query(default=None),
    end_ts: int | None = Query(default=None),
    minutes: int | None = Query(default=10, ge=1, le=60),
    limit: int = Query(default=1000, ge=1, le=5000),
    offset: int = Query(default=0, ge=0),
) -> StreamingResponse:
    if start_ts is not None and end_ts is not None:
        items = repository.get_range(start_ts, end_ts, limit, offset)
    else:
        items = repository.get_history(minutes=minutes or 10)
    rows = _to_csv_rows(items)
    return _stream_csv(rows)


@router.get("/history/export", dependencies=[Depends(_require_api_key)])
def export_history_csv_legacy(
    start_ts: int | None = Query(default=None),
    end_ts: int | None = Query(default=None),
    minutes: int | None = Query(default=10, ge=1, le=60),
    limit: int = Query(default=1000, ge=1, le=5000),
    offset: int = Query(default=0, ge=0),
) -> StreamingResponse:
    return export_history_csv(start_ts, end_ts, minutes, limit, offset)


@router.get("/history/export/pdf", dependencies=[Depends(_require_api_key)])
def export_history_pdf(
    start_ts: int | None = Query(default=None),
    end_ts: int | None = Query(default=None),
    minutes: int | None = Query(default=10, ge=1, le=60),
    limit: int = Query(default=1000, ge=1, le=5000),
    offset: int = Query(default=0, ge=0),
) -> StreamingResponse:
    if start_ts is not None and end_ts is not None:
        items = repository.get_range(start_ts, end_ts, limit, offset)
    else:
        items = repository.get_history(minutes=minutes or 10)

    pdf_bytes = _build_pdf(items)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=telemetry.pdf"},
    )
