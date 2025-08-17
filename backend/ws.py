from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import Set, Dict
import asyncio
import json
import time

ws_router = APIRouter()
active_connections: Set[WebSocket] = set()
user_connections: Dict[str, WebSocket] = {}  # user_id -> websocket
editing_tasks: Dict[str, Dict] = {}  # task_id -> {user_id, user_name, timestamp}

@ws_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: str = "anonymous"):
    await websocket.accept()
    active_connections.add(websocket)
    user_connections[user_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_websocket_message(websocket, user_id, message)
            except json.JSONDecodeError:
                # Keep connection alive for non-JSON messages
                pass
    except WebSocketDisconnect:
        active_connections.discard(websocket)
        user_connections.pop(user_id, None)
        # Clean up editing states for this user
        await cleanup_user_editing_state(user_id)

async def handle_websocket_message(websocket: WebSocket, user_id: str, message: dict):
    """Handle incoming WebSocket messages from clients"""
    message_type = message.get("type")
    payload = message.get("payload", {})
    
    if message_type == "task_edit_start":
        await handle_task_edit_start(user_id, payload)
    elif message_type == "task_edit_end":
        await handle_task_edit_end(user_id, payload)

async def handle_task_edit_start(user_id: str, payload: dict):
    """Handle when a user starts editing a task"""
    task_id = payload.get("taskId")
    project_id = payload.get("projectId")
    user_name = payload.get("userName", f"User {user_id}")
    
    if not task_id:
        return
    
    # Store editing state
    editing_tasks[task_id] = {
        "userId": user_id,
        "userName": user_name,
        "projectId": project_id,
        "timestamp": time.time()
    }
    
    # Broadcast to other users
    await broadcast_event({
        "type": "task_edit_start",
        "payload": {
            "taskId": task_id,
            "userId": user_id,
            "userName": user_name,
            "project_id": project_id
        }
    })

async def handle_task_edit_end(user_id: str, payload: dict):
    """Handle when a user stops editing a task"""
    task_id = payload.get("taskId")
    project_id = payload.get("projectId")
    
    if not task_id:
        return
    
    # Remove editing state
    if task_id in editing_tasks and editing_tasks[task_id]["userId"] == user_id:
        del editing_tasks[task_id]
        
        # Broadcast to other users
        await broadcast_event({
            "type": "task_edit_end",
            "payload": {
                "taskId": task_id,
                "userId": user_id,
                "project_id": project_id
            }
        })

async def cleanup_user_editing_state(user_id: str):
    """Clean up all editing states for a disconnected user"""
    tasks_to_remove = []
    
    for task_id, edit_info in editing_tasks.items():
        if edit_info["userId"] == user_id:
            tasks_to_remove.append(task_id)
    
    for task_id in tasks_to_remove:
        project_id = editing_tasks[task_id]["projectId"]
        del editing_tasks[task_id]
        
        # Broadcast edit end for each task
        await broadcast_event({
            "type": "task_edit_end",
            "payload": {
                "taskId": task_id,
                "userId": user_id,
                "project_id": project_id
            }
        })

async def broadcast_event(event: dict):
    to_remove = set()
    for ws in list(active_connections):
        try:
            await ws.send_json(event)
        except Exception:
            to_remove.add(ws)
    for ws in to_remove:
        active_connections.discard(ws)