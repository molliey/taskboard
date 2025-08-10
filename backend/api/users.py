from fastapi import APIRouter, HTTPException, Header
from models import UserRegisterRequest, UserLoginRequest, UserUpdateRequest
from redis_client import get_redis
import time, uuid

router = APIRouter()

def get_next_user_id(r):
    return r.incr("user:id:seq")

def get_user_by_token(token: str):
    r = get_redis()
    session_id = r.get(f"token:{token}")
    if not session_id:
        return None
    user_id = r.hget(f"session:{session_id}", "user_id")
    user = r.hgetall(f"user:{user_id}")
    return user

@router.post("/register")
def register_user(req: UserRegisterRequest):
    r = get_redis()
    if r.exists(f"email:{req.email}"):
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = get_next_user_id(r)
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    avatar = "👤"
    user_data = {
        "id": user_id,
        "name": req.name,
        "email": req.email,
        "password_hash": req.password,  # Should be hashed in production
        "avatar": avatar,
        "role": req.role,
        "is_active": "true",
        "created_at": now,
        "updated_at": now,
    }
    r.hset(f"user:{user_id}", mapping=user_data)
    r.set(f"email:{req.email}", user_id)
    r.sadd("users:all", user_id)
    r.sadd("users:active", user_id)
    return {
        "id": user_id,
        "name": req.name,
        "email": req.email,
        "avatar": avatar,
        "role": req.role,
        "is_active": True,
        "created_at": now,
    }

@router.post("/login")
def login_user(req: UserLoginRequest):
    r = get_redis()
    user_id = r.get(f"email:{req.email}")
    if not user_id:
        # Return 200 with structured error for better frontend handling
        return {"success": False, "error": "User not found"}
    user = r.hgetall(f"user:{user_id}")
    if not user or user.get("password_hash") != req.password:
        return {"success": False, "error": "Incorrect password"}
    token = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    r.hset(f"session:{session_id}", mapping={
        "user_id": user_id,
        "token_hash": token,
        "expires_at": "2099-12-31T23:59:59Z",
        "created_at": now,
    })
    r.sadd(f"user:{user_id}:sessions", session_id)
    r.set(f"token:{token}", session_id)
    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": int(user["id"]),
            "name": user["name"],
            "email": user["email"],
            "avatar": user["avatar"],
            "role": user["role"],
            "is_active": user["is_active"] == "true",
            "created_at": user["created_at"],
        }
    }

@router.get("/me")
def get_me(Authorization: str = Header(...)):
    token = Authorization.replace("Bearer ", "")
    r = get_redis()
    session_id = r.get(f"token:{token}")
    if not session_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = r.hget(f"session:{session_id}", "user_id")
    user = r.hgetall(f"user:{user_id}")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": int(user["id"]),
        "name": user["name"],
        "email": user["email"],
        "avatar": user["avatar"],
        "role": user["role"],
        "is_active": user["is_active"] == "true",
        "created_at": user["created_at"],
    }

@router.get("/")
def get_all_users(Authorization: str = Header(...)):
    r = get_redis()
    user_ids = r.smembers("users:all")
    users = []
    for uid in user_ids:
        user = r.hgetall(f"user:{uid}")
        if user:
            users.append({
                "id": int(user["id"]),
                "name": user["name"],
                "email": user["email"],
                "avatar": user["avatar"],
                "role": user["role"],
                "is_active": user["is_active"] == "true",
                "created_at": user["created_at"],
            })
    return users

@router.get("/{user_id}")
def get_user_by_id(user_id: int, Authorization: str = Header(...)):
    r = get_redis()
    user = r.hgetall(f"user:{user_id}")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": int(user["id"]),
        "name": user["name"],
        "email": user["email"],
        "avatar": user["avatar"],
        "role": user["role"],
        "is_active": user["is_active"] == "true",
        "created_at": user["created_at"],
    }

@router.put("/{user_id}")
def update_user(user_id: int, req: UserUpdateRequest, Authorization: str = Header(...)):
    r = get_redis()
    user = r.hgetall(f"user:{user_id}")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = {}
    if req.name:
        update_data["name"] = req.name
    if req.email:
        update_data["email"] = req.email
    if req.role:
        update_data["role"] = req.role
    update_data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    r.hset(f"user:{user_id}", mapping=update_data)
    user.update(update_data)
    return {
        "id": int(user["id"]),
        "name": user["name"],
        "email": user["email"],
        "avatar": user["avatar"],
        "role": user["role"],
        "is_active": user["is_active"] == "true",
        "updated_at": user["updated_at"],
    } 