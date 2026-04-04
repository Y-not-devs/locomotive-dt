from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..db.repository import TelemetryRepository
from ..models.schemas import TelemetryIn, TelemetryOut
from ..services.health_engine import HealthEngine
from ..services.processor import TelemetryProcessor

router = APIRouter()
repository = TelemetryRepository()


@router.websocket("/telemetry")
async def telemetry_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    processor = TelemetryProcessor()
    engine = HealthEngine()

    try:
        while True:
            payload = await websocket.receive_json()
            telemetry_in = TelemetryIn(**payload)
            processed = processor.process(telemetry_in)
            health = engine.compute(processed)
            telemetry_out = TelemetryOut.from_parts(processed, health)
            repository.save(telemetry_out)
            await websocket.send_json(telemetry_out.model_dump())
    except WebSocketDisconnect:
        return
