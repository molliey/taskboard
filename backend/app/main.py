"""
FastAPI application main entry point
Handles app initialization, middleware configuration, route registration and WebSocket endpoints
"""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.api import user, project, column, task
from app.api.websocket import websocket_endpoint
from app.database.base import Base
from app.database.session import engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Board API",
    description="Collaborative task management system with real-time updates",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(user.router, prefix="/api")
app.include_router(project.router, prefix="/api")
app.include_router(column.router, prefix="/api")
app.include_router(task.router, prefix="/api")

# WebSocket endpoint for real-time communication
@app.websocket("/ws/{project_id}")
async def websocket_route(websocket: WebSocket, project_id: int, token: str = None):
    await websocket_endpoint(websocket, project_id, token)

@app.get("/")
def read_root():
    return {
        "message": "Task Board API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}