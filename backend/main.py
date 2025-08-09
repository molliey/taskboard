from fastapi import FastAPI
from api import users, projects, tasks
from ws import ws_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(tasks.router, prefix="/api/projects", tags=["tasks"])
app.include_router(ws_router, tags=["websocket"]) 