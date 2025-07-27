from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[user_id] = websocket
        
        # Notify all users about the new connection
        await self.broadcast_user_count()
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket, user_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
        logger.info(f"User {user_id} disconnected. Total connections: {len(self.active_connections)}")
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            
    async def broadcast(self, message: str, exclude: WebSocket = None):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            if connection != exclude:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Failed to broadcast to connection: {e}")
                    disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)
                
    async def broadcast_user_count(self):
        """Broadcast current user count to all connections"""
        message = {
            "type": "user_count",
            "payload": {
                "count": len(self.active_connections),
                "timestamp": datetime.now().isoformat()
            }
        }
        await self.broadcast(json.dumps(message))

# Global connection manager instance
manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, user_id: str = "anonymous"):
    """Main WebSocket endpoint for real-time communication"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_websocket_message(message, websocket, user_id)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from {user_id}: {data}")
                await manager.send_personal_message(
                    json.dumps({"type": "error", "message": "Invalid JSON format"}),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        await manager.broadcast_user_count()
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)

async def handle_websocket_message(message: dict, websocket: WebSocket, user_id: str):
    """Handle different types of WebSocket messages"""
    message_type = message.get("type")
    payload = message.get("payload", {})
    
    logger.info(f"Received {message_type} from {user_id}: {payload}")
    
    if message_type == "create_task":
        await handle_create_task(payload, websocket, user_id)
    elif message_type == "move_task":
        await handle_move_task(payload, websocket, user_id)
    elif message_type == "update_task":
        await handle_update_task(payload, websocket, user_id)
    elif message_type == "delete_task":
        await handle_delete_task(payload, websocket, user_id)
    elif message_type == "request_board_sync":
        await handle_board_sync_request(payload, websocket, user_id)
    else:
        logger.warning(f"Unknown message type: {message_type}")

async def handle_create_task(payload: dict, websocket: WebSocket, user_id: str):
    """Handle task creation"""
    task = payload.get("task")
    column = payload.get("column")
    
    if not task or not column:
        await manager.send_personal_message(
            json.dumps({"type": "error", "message": "Missing task or column"}),
            websocket
        )
        return
    
    # Broadcast to all other clients
    broadcast_message = {
        "type": "task_created",
        "payload": {
            "task": task,
            "column": column,
            "created_by": user_id,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    await manager.broadcast(json.dumps(broadcast_message), exclude=websocket)

async def handle_move_task(payload: dict, websocket: WebSocket, user_id: str):
    """Handle task movement between columns"""
    task_id = payload.get("taskId")
    from_column = payload.get("fromColumn")
    to_column = payload.get("toColumn")
    position = payload.get("position", 0)
    
    if not all([task_id, from_column, to_column]):
        await manager.send_personal_message(
            json.dumps({"type": "error", "message": "Missing required fields for task move"}),
            websocket
        )
        return
    
    # Broadcast to all other clients
    broadcast_message = {
        "type": "task_moved",
        "payload": {
            "taskId": task_id,
            "fromColumn": from_column,
            "toColumn": to_column,
            "position": position,
            "moved_by": user_id,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    await manager.broadcast(json.dumps(broadcast_message), exclude=websocket)

async def handle_update_task(payload: dict, websocket: WebSocket, user_id: str):
    """Handle task updates"""
    task_id = payload.get("taskId")
    updates = payload.get("updates")
    
    if not task_id or not updates:
        await manager.send_personal_message(
            json.dumps({"type": "error", "message": "Missing taskId or updates"}),
            websocket
        )
        return
    
    # Broadcast to all other clients
    broadcast_message = {
        "type": "task_updated",
        "payload": {
            "taskId": task_id,
            "updates": updates,
            "updated_by": user_id,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    await manager.broadcast(json.dumps(broadcast_message), exclude=websocket)

async def handle_delete_task(payload: dict, websocket: WebSocket, user_id: str):
    """Handle task deletion"""
    task_id = payload.get("taskId")
    column = payload.get("column")
    
    if not task_id or not column:
        await manager.send_personal_message(
            json.dumps({"type": "error", "message": "Missing taskId or column"}),
            websocket
        )
        return
    
    # Broadcast to all other clients
    broadcast_message = {
        "type": "task_deleted",
        "payload": {
            "taskId": task_id,
            "column": column,
            "deleted_by": user_id,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    await manager.broadcast(json.dumps(broadcast_message), exclude=websocket)

async def handle_board_sync_request(payload: dict, websocket: WebSocket, user_id: str):
    """Handle board synchronization request"""
    project_id = payload.get("projectId")
    
    # For now, return sample data - in a real app, this would fetch from database
    sample_columns = {
        "TO DO": [
            {
                "id": "SMS-5",
                "title": "(Sample) Payment Processing Integration",
                "tag": "(SAMPLE) BILLING AND INVOICING",
                "description": "Integrate payment processing system with billing module",
                "due_date": "2024-02-15",
                "assignee_id": 1
            }
        ],
        "IN PROGRESS": [
            {
                "id": "SMS-6",
                "title": "(Sample) Update User Subscription",
                "tag": "(SAMPLE) USER SUBSCRIPTION MANAGEMENT",
                "description": "Update user subscription management system",
                "due_date": "2024-02-20",
                "assignee_id": 2
            }
        ],
        "IN REVIEW": [
            {
                "id": "SMS-4",
                "title": "(Sample) Create User Subscription",
                "tag": "(SAMPLE) USER SUBSCRIPTION MANAGEMENT",
                "description": "Create new user subscription functionality",
                "due_date": "2024-02-25",
                "assignee_id": 1
            }
        ],
        "DONE": []
    }
    
    sync_message = {
        "type": "board_sync",
        "payload": {
            "columns": sample_columns,
            "project_id": project_id,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    await manager.send_personal_message(json.dumps(sync_message), websocket)