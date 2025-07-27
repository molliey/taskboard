from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, List
import json
import asyncio
from app.database.session import get_db
from app.services.project_service import ProjectService
from app.services.user_service import UserService
from app.utils.auth import decode_access_token
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 存储连接：{project_id: {user_id: websocket}}
        self.project_connections: Dict[int, Dict[int, WebSocket]] = {}
        # 存储用户到项目的映射
        self.user_projects: Dict[int, List[int]] = {}
    
    async def connect(self, websocket: WebSocket, project_id: int, user_id: int):
        """添加新连接"""
        await websocket.accept()
        
        if project_id not in self.project_connections:
            self.project_connections[project_id] = {}
        
        self.project_connections[project_id][user_id] = websocket
        
        if user_id not in self.user_projects:
            self.user_projects[user_id] = []
        if project_id not in self.user_projects[user_id]:
            self.user_projects[user_id].append(project_id)
        
        logger.info(f"User {user_id} connected to project {project_id}")
        
        # 通知其他用户有新用户加入
        await self.broadcast_to_project(
            project_id, 
            {
                "type": "user_joined",
                "user_id": user_id,
                "project_id": project_id
            },
            exclude_user=user_id
        )
    
    def disconnect(self, project_id: int, user_id: int):
        """移除连接"""
        if project_id in self.project_connections:
            if user_id in self.project_connections[project_id]:
                del self.project_connections[project_id][user_id]
                
                # 如果项目没有连接了，清理项目
                if not self.project_connections[project_id]:
                    del self.project_connections[project_id]
        
        if user_id in self.user_projects:
            if project_id in self.user_projects[user_id]:
                self.user_projects[user_id].remove(project_id)
            
            # 如果用户没有项目连接了，清理用户
            if not self.user_projects[user_id]:
                del self.user_projects[user_id]
        
        logger.info(f"User {user_id} disconnected from project {project_id}")
    
    async def send_personal_message(self, message: dict, user_id: int, project_id: int):
        """发送个人消息"""
        if (project_id in self.project_connections and 
            user_id in self.project_connections[project_id]):
            websocket = self.project_connections[project_id][user_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                self.disconnect(project_id, user_id)
    
    async def broadcast_to_project(self, project_id: int, message: dict, exclude_user: int = None):
        """向项目所有成员广播消息"""
        if project_id not in self.project_connections:
            return
        
        message_str = json.dumps(message)
        disconnect_users = []
        
        for user_id, websocket in self.project_connections[project_id].items():
            if exclude_user and user_id == exclude_user:
                continue
                
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {e}")
                disconnect_users.append(user_id)
        
        # 清理断开的连接
        for user_id in disconnect_users:
            self.disconnect(project_id, user_id)
    
    def get_project_users(self, project_id: int) -> List[int]:
        """获取项目在线用户列表"""
        if project_id in self.project_connections:
            return list(self.project_connections[project_id].keys())
        return []

# 全局连接管理器实例
manager = ConnectionManager()

async def get_current_user_from_token(token: str, db: Session):
    """从WebSocket token获取当前用户"""
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = UserService.get_user_by_username(db, username=username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")

async def websocket_endpoint(
    websocket: WebSocket,
    project_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """WebSocket端点处理项目实时更新"""
    try:
        # 验证用户和项目权限
        user = await get_current_user_from_token(token, db)
        
        # 检查用户是否有权限访问该项目
        project = ProjectService.get_project(db, project_id=project_id)
        if not project:
            await websocket.close(code=4004, reason="Project not found")
            return
        
        is_member = any(member.user_id == user.id for member in project.members)
        if not is_member:
            await websocket.close(code=4003, reason="Access denied")
            return
        
        # 建立连接
        await manager.connect(websocket, project_id, user.id)
        
        try:
            while True:
                # 接收客户端消息
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    await handle_websocket_message(message, project_id, user.id, db)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received from user {user.id}")
                except Exception as e:
                    logger.error(f"Error handling message from user {user.id}: {e}")
                    
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user.id} in project {project_id}")
        except Exception as e:
            logger.error(f"WebSocket error for user {user.id}: {e}")
        finally:
            manager.disconnect(project_id, user.id)
            # 通知其他用户该用户离开
            await manager.broadcast_to_project(
                project_id,
                {
                    "type": "user_left", 
                    "user_id": user.id,
                    "project_id": project_id
                },
                exclude_user=user.id
            )
            
    except HTTPException as e:
        await websocket.close(code=4001, reason=str(e.detail))
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        await websocket.close(code=5000, reason="Internal server error")

async def handle_websocket_message(message: dict, project_id: int, user_id: int, db: Session):
    """处理WebSocket消息"""
    message_type = message.get("type")
    
    if message_type == "ping":
        # 心跳检测
        await manager.send_personal_message(
            {"type": "pong", "timestamp": message.get("timestamp")},
            user_id,
            project_id
        )
    
    elif message_type == "user_typing":
        # 用户正在输入
        await manager.broadcast_to_project(
            project_id,
            {
                "type": "user_typing",
                "user_id": user_id,
                "task_id": message.get("task_id"),
                "is_typing": message.get("is_typing", True)
            },
            exclude_user=user_id
        )

# 在其他API中调用的通知函数
async def notify_task_created(project_id: int, task_data: dict, creator_id: int):
    """通知任务创建"""
    await manager.broadcast_to_project(
        project_id,
        {
            "type": "task_created",
            "task": task_data,
            "creator_id": creator_id,
            "timestamp": asyncio.get_event_loop().time()
        },
        exclude_user=creator_id
    )

async def notify_task_updated(project_id: int, task_data: dict, updater_id: int):
    """通知任务更新"""
    await manager.broadcast_to_project(
        project_id,
        {
            "type": "task_updated", 
            "task": task_data,
            "updater_id": updater_id,
            "timestamp": asyncio.get_event_loop().time()
        },
        exclude_user=updater_id
    )

async def notify_task_moved(project_id: int, task_data: dict, mover_id: int):
    """通知任务移动"""
    await manager.broadcast_to_project(
        project_id,
        {
            "type": "task_moved",
            "task": task_data,
            "mover_id": mover_id, 
            "timestamp": asyncio.get_event_loop().time()
        },
        exclude_user=mover_id
    )

async def notify_task_deleted(project_id: int, task_id: int, deleter_id: int):
    """通知任务删除"""
    await manager.broadcast_to_project(
        project_id,
        {
            "type": "task_deleted",
            "task_id": task_id,
            "deleter_id": deleter_id,
            "timestamp": asyncio.get_event_loop().time()
        },
        exclude_user=deleter_id
    )