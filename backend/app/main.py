from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import user, project, task  # 导入你写的模块

app = FastAPI()

# 跨域中间件设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由模块
app.include_router(user.router, prefix="/api", tags=["User"])
app.include_router(project.router, prefix="/api", tags=["Project"])
app.include_router(task.router, prefix="/api", tags=["Task"])

# 健康检查接口
@app.get("/health")
def health_check():
    return {"status": "ok"}

