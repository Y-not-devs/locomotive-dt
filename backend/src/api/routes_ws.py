from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..core.config import settings
from ..services.ingest_buffer import ingest_buffer
from ..models.schemas import TelemetryIn, TelemetryOut
from ..services.health_engine import HealthEngine
from ..services.processor import TelemetryProcessor
from ..services.telemetry_hub import telemetry_hub

router = APIRouter()


@router.websocket("/telemetry")
async def telemetry_ws(websocket: WebSocket) -> None:
    api_key = websocket.headers.get("x-api-key") or websocket.query_params.get(
        "api_key"
    )
    if not api_key or api_key != settings.api_key:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    processor = TelemetryProcessor()
    engine = HealthEngine()

    try:
        while True:
            payload = await websocket.receive_json()
            telemetry_in = TelemetryIn(**payload)
            processed, is_duplicate = processor.process(telemetry_in)
            health = engine.compute(processed)
            telemetry_out = TelemetryOut.from_parts(processed, health)
            if not is_duplicate:
                await ingest_buffer.enqueue(telemetry_out)
            payload = telemetry_out.model_dump()
            await telemetry_hub.broadcast(payload)
            await websocket.send_json(payload)
    except WebSocketDisconnect:
        return


@router.websocket("/telemetry/stream")
async def telemetry_stream(websocket: WebSocket) -> None:
    api_key = websocket.headers.get("x-api-key") or websocket.query_params.get(
        "api_key"
    )
    if not api_key or api_key != settings.api_key:
        await websocket.close(code=1008)
        return

    await telemetry_hub.connect(websocket)
    try:
        while True:
            await websocket.receive()
    except (WebSocketDisconnect, RuntimeError):
        telemetry_hub.disconnect(websocket)
