import json
from typing import Any

from fastapi import WebSocket

from app.application.interfaces.event_publisher import EventPublisher


class EventConnectionManager(EventPublisher):
    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)

    async def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        message = json.dumps({"type": event_type, "data": payload}, default=str)
        stale: list[WebSocket] = []
        for connection in self._connections:
            try:
                await connection.send_text(message)
            except Exception:
                stale.append(connection)
        for connection in stale:
            self.disconnect(connection)


event_manager = EventConnectionManager()
