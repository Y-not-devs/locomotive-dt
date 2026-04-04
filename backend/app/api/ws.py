from fastapi import APIRouter, WebSocket

from app.dependencies import get_container

router = APIRouter()


@router.websocket("/ws/telemetry/live")
async def telemetry_live(websocket: WebSocket) -> None:
    container = get_container(websocket)
    await container.telemetry_hub.serve(websocket)
