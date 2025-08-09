from fastapi import APIRouter, HTTPException, Header
from models import ProjectCreateRequest, ProjectUpdateRequest, AddProjectMemberRequest, AddProjectMemberByEmailRequest
from redis_client import get_redis
import time
from ws import broadcast_event

router = APIRouter()

def get_next_project_id(r):
    return r.incr("project:id:seq")

def get_user_id_from_token(Authorization: str):
    token = Authorization.replace("Bearer ", "")
    r = get_redis()
    session_id = r.get(f"token:{token}")
    if not session_id:
        return None
    session = r.hgetall(f"session:{session_id}")
    if not session:
        return None
    return session.get("user_id")

def _to_int(value):
    try:
        if isinstance(value, bytes):
            return int(value.decode())
        return int(value)
    except Exception:
        return value

@router.post("/")
async def create_project(req: ProjectCreateRequest, Authorization: str = Header(...)):
    r = get_redis()
    user_id = get_user_id_from_token(Authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    project_id = get_next_project_id(r)
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    project_data = {
        "id": project_id,
        "name": req.name,
        "description": req.description,
        "is_active": str(req.is_active).lower(),
        "created_at": now,
        "updated_at": now,
    }
    r.hset(f"project:{project_id}", mapping=project_data)
    r.sadd("projects:all", project_id)
    if req.is_active:
        r.sadd("projects:active", project_id)
    r.sadd(f"user:{user_id}:projects", project_id)
    r.sadd(f"project:{project_id}:members", user_id)
    r.hset(f"project:{project_id}:roles", user_id, r.hget(f"user:{user_id}", "role"))
    await broadcast_event({"type": "project_created", "payload": project_data})
    return {
        "id": project_id,
        "name": req.name,
        "description": req.description,
        "is_active": req.is_active,
        "created_at": now,
        "updated_at": now,
    }

@router.get("/my-projects")
def get_my_projects(Authorization: str = Header(...)):
    r = get_redis()
    user_id = get_user_id_from_token(Authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    project_ids = r.smembers(f"user:{user_id}:projects")
    projects = []
    for pid_raw in project_ids:
        pid = _to_int(pid_raw)
        p = r.hgetall(f"project:{pid}")
        if p:
            projects.append({
                "id": int(p["id"]),
                "name": p["name"],
                "description": p["description"],
                "is_active": p["is_active"] == "true",
                "created_at": p["created_at"],
                "updated_at": p["updated_at"],
            })
    return projects

@router.get("/{project_id}")
def get_project(project_id: int, Authorization: str = Header(...)):
    r = get_redis()
    p = r.hgetall(f"project:{project_id}")
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "id": int(p["id"]),
        "name": p["name"],
        "description": p["description"],
        "is_active": p["is_active"] == "true",
        "created_at": p["created_at"],
        "updated_at": p["updated_at"],
    }

@router.put("/{project_id}")
async def update_project(project_id: int, req: ProjectUpdateRequest, Authorization: str = Header(...)):
    r = get_redis()
    p = r.hgetall(f"project:{project_id}")
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    update_data = {}
    if req.name:
        update_data["name"] = req.name
    if req.description:
        update_data["description"] = req.description
    if req.is_active is not None:
        update_data["is_active"] = str(req.is_active).lower()
        if req.is_active:
            r.sadd("projects:active", project_id)
        else:
            r.srem("projects:active", project_id)
    update_data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    r.hset(f"project:{project_id}", mapping=update_data)
    p.update(update_data)
    updated_project = r.hgetall(f"project:{project_id}")
    await broadcast_event({"type": "project_updated", "payload": updated_project})
    return {
        "id": int(p["id"]),
        "name": p["name"],
        "description": p["description"],
        "is_active": p["is_active"] == "true",
        "updated_at": p["updated_at"],
    }

@router.delete("/{project_id}")
async def delete_project(project_id: int, Authorization: str = Header(...)):
    r = get_redis()
    p = r.hgetall(f"project:{project_id}")
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    r.srem("projects:all", project_id)
    r.srem("projects:active", project_id)
    members = r.smembers(f"project:{project_id}:members")
    for uid_raw in members:
        uid = _to_int(uid_raw)
        r.srem(f"user:{uid}:projects", project_id)
    r.delete(f"project:{project_id}")
    r.delete(f"project:{project_id}:members")
    r.delete(f"project:{project_id}:roles")
    await broadcast_event({"type": "project_deleted", "payload": {"project_id": project_id}})
    return {"success": True, "message": "Project deleted successfully"}

@router.get("/{project_id}/members")
def get_project_members(project_id: int, Authorization: str = Header(...)):
    r = get_redis()
    member_ids = r.smembers(f"project:{project_id}:members")
    members = []
    for uid_raw in member_ids:
        uid = _to_int(uid_raw)
        user = r.hgetall(f"user:{uid}")
        if user:
            members.append({
                "id": int(user["id"]),
                "name": user["name"],
                "email": user["email"],
                "avatar": user["avatar"],
                "role": user["role"],
                "is_active": user["is_active"] == "true",
                "joined_at": user["created_at"],
            })
    return members

@router.post("/{project_id}/members")
async def add_project_member(project_id: int, req: AddProjectMemberRequest, Authorization: str = Header(...)):
    r = get_redis()
    user = r.hgetall(f"user:{req.user_id}")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    r.sadd(f"project:{project_id}:members", req.user_id)
    r.hset(f"project:{project_id}:roles", req.user_id, req.role)
    r.sadd(f"user:{req.user_id}:projects", project_id)
    member_data = {
        "id": int(user["id"]),
        "name": user["name"],
        "email": user["email"],
        "avatar": user["avatar"],
        "role": req.role,
        "is_active": user["is_active"] == "true",
        "joined_at": user["created_at"],
        "project_id": project_id,
    }
    await broadcast_event({"type": "member_added", "payload": member_data})
    return member_data

@router.post("/{project_id}/members/by-email")
async def add_project_member_by_email(project_id: int, req: AddProjectMemberByEmailRequest, Authorization: str = Header(...)):
    r = get_redis()
    user_id = r.get(f"email:{req.email}")
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")
    user = r.hgetall(f"user:{user_id}")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    r.sadd(f"project:{project_id}:members", user_id)
    r.hset(f"project:{project_id}:roles", user_id, req.role)
    r.sadd(f"user:{user_id}:projects", project_id)
    member_data = {
        "id": int(user["id"]),
        "name": user["name"],
        "email": user["email"],
        "avatar": user["avatar"],
        "role": req.role,
        "is_active": user["is_active"] == "true",
        "joined_at": user["created_at"],
        "project_id": project_id,
    }
    await broadcast_event({"type": "member_added", "payload": member_data})
    return member_data

@router.delete("/{project_id}/members/{user_id}")
async def remove_project_member(project_id: int, user_id: int, Authorization: str = Header(...)):
    r = get_redis()
    r.srem(f"project:{project_id}:members", user_id)
    r.hdel(f"project:{project_id}:roles", user_id)
    r.srem(f"user:{user_id}:projects", project_id)
    await broadcast_event({"type": "member_removed", "payload": {"user_id": user_id, "project_id": project_id}})
    return {"success": True, "message": "Member removed successfully"}

@router.get("/{project_id}/workload")
def get_project_workload(project_id: int, Authorization: str = Header(...)):
    r = get_redis()
    member_ids = r.smembers(f"project:{project_id}:members")
    result = []
    for uid_raw in member_ids:
        uid = _to_int(uid_raw)
        user = r.hgetall(f"user:{uid}")
        if user:
            result.append({
                "user_id": int(user["id"]),
                "name": user["name"],
                "avatar": user["avatar"],
                "total_tasks": 0,
                "completed_tasks": 0,
                "in_progress_tasks": 0,
                "todo_tasks": 0,
            })
    return result 