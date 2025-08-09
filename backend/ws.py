from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import Set
import asyncio

ws_router = APIRouter()
active_connections: Set[WebSocket] = set()

@ws_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # 保持连接
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_event(event: dict):
    to_remove = set()
    for ws in list(active_connections):
        try:
            await ws.send_json(event)
        except Exception:
            to_remove.add(ws)
    for ws in to_remove:
        active_connections.discard(ws) 