from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.infrastructure.websockets.manager import event_manager

router = APIRouter(tags=["Tiempo real"])


@router.websocket("/ws/eventos")
async def websocket_eventos(websocket: WebSocket) -> None:
    await event_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        event_manager.disconnect(websocket)
