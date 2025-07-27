from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.api import user, project, column, task
from app.api.websocket import websocket_endpoint
from app.database.base import Base
from app.database.session import engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Board API",
    description="Collaborative task management system with real-time updates",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],  # Your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user.router)
app.include_router(project.router)
app.include_router(column.router)
app.include_router(task.router)

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket, user_id: str = "anonymous"):
    await websocket_endpoint(websocket, user_id)

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