from fastapi import WebSocket


class TelemetryHub:
    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()
        self._last_payload: dict | None = None

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clients.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._clients.discard(websocket)

    async def broadcast(self, payload: dict) -> None:
        self._last_payload = payload
        stale: list[WebSocket] = []
        for client in self._clients:
            try:
                await client.send_json(payload)
            except Exception:
                stale.append(client)
        for client in stale:
            self._clients.discard(client)


telemetry_hub = TelemetryHub()
