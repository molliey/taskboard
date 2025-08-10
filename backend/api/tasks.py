from fastapi import APIRouter, HTTPException, Header
from models import TaskCreateRequest, TaskUpdateRequest, MoveTaskRequest
from redis_client import get_redis
import uuid, time, json
import asyncio
from ws import broadcast_event

router = APIRouter()

def get_next_task_id(r):
    return f"task-{r.incr('task:id:seq')}"

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

@router.post("/{project_id}/tasks")
async def create_task(project_id: int, req: TaskCreateRequest, Authorization: str = Header(...)):
    r = get_redis()
    task_id = get_next_task_id(r)
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    task_data = {
        "id": task_id,
        "project_id": project_id,
        "title": req.title,
        "description": req.description,
        "tag": req.tag,
        "due_date": req.due_date,
        "assignee_id": req.assignee_id,
        "column_name": req.column_name,
        "created_at": now,
        "updated_at": now,
    }
    r.hset(f"task:{task_id}", mapping=task_data)
    r.sadd(f"project:{project_id}:tasks", task_id)
    # Board column (as JSON list)
    col_tasks = json.loads(r.hget(f"project:{project_id}:board", req.column_name) or "[]")
    col_tasks.append(task_data)
    r.hset(f"project:{project_id}:board", req.column_name, json.dumps(col_tasks))
    # Column index (list of task ids)
    r.rpush(f"project:{project_id}:column:{req.column_name}:tasks", task_id)
    r.sadd(f"user:{req.assignee_id}:assigned_tasks", task_id)
    # Broadcast WebSocket event
    await broadcast_event({"type": "task_created", "payload": task_data})
    return {
        "id": task_id,
        "title": req.title,
        "description": req.description,
        "tag": req.tag,
        "due_date": req.due_date,
        "assignee_id": req.assignee_id,
        "column_name": req.column_name,
        "created_at": now,
        "updated_at": now,
    }

@router.get("/{project_id}/board")
def get_project_board(project_id: int, Authorization: str = Header(...)):
    r = get_redis()
    columns = {}
    for col in ["TO DO", "IN PROGRESS", "IN REVIEW", "DONE"]:
        col_json = r.hget(f"project:{project_id}:board", col)
        columns[col] = json.loads(col_json) if col_json else []
    return {"project_id": project_id, "columns": columns}

@router.put("/{project_id}/tasks/{task_id}")
async def update_task(project_id: int, task_id: str, req: TaskUpdateRequest, Authorization: str = Header(...)):
    r = get_redis()
    task = r.hgetall(f"task:{task_id}")
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    update_data = {}
    if req.title:
        update_data["title"] = req.title
    if req.description:
        update_data["description"] = req.description
    if req.tag:
        update_data["tag"] = req.tag
    if req.due_date:
        update_data["due_date"] = req.due_date
    if req.assignee_id is not None:
        update_data["assignee_id"] = req.assignee_id
    update_data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    r.hset(f"task:{task_id}", mapping=update_data)
    # Update task in board column
    col = task["column_name"]
    col_tasks = json.loads(r.hget(f"project:{project_id}:board", col) or "[]")
    for t in col_tasks:
        if t["id"] == task_id:
            t.update(update_data)
    r.hset(f"project:{project_id}:board", col, json.dumps(col_tasks))
    # Broadcast WebSocket event
    updated_task = r.hgetall(f"task:{task_id}")
    await broadcast_event({"type": "task_updated", "payload": updated_task})
    return {
        "id": task_id,
        **task,
        **update_data,
    }

@router.put("/{project_id}/tasks/{task_id}/move")
async def move_task(project_id: int, task_id: str, req: MoveTaskRequest, Authorization: str = Header(...)):
    r = get_redis()
    task = r.hgetall(f"task:{task_id}")
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # Remove from old column
    from_col_tasks = json.loads(r.hget(f"project:{project_id}:board", req.from_column) or "[]")
    from_col_tasks = [t for t in from_col_tasks if t["id"] != task_id]
    r.hset(f"project:{project_id}:board", req.from_column, json.dumps(from_col_tasks))
    # Add to new column
    to_col_tasks = json.loads(r.hget(f"project:{project_id}:board", req.to_column) or "[]")
    task_data = r.hgetall(f"task:{task_id}")
    task_data["column_name"] = req.to_column
    to_col_tasks.insert(req.position, task_data)
    r.hset(f"project:{project_id}:board", req.to_column, json.dumps(to_col_tasks))
    # Update task's column_name
    r.hset(f"task:{task_id}", "column_name", req.to_column)
    # Update column index (fix: use lrange to get, insert, rebuild)
    col_key = f"project:{project_id}:column:{req.to_column}:tasks"
    task_ids = r.lrange(col_key, 0, -1)
    # Remove task_id if exists
    task_ids = [tid for tid in task_ids if tid != task_id]
    # Boundary check
    pos = req.position
    if pos < 0 or pos > len(task_ids):
        pos = len(task_ids)
    task_ids.insert(pos, task_id)
    r.delete(col_key)
    if task_ids:
        r.rpush(col_key, *task_ids)
    # Remove from old column index
    r.lrem(f"project:{project_id}:column:{req.from_column}:tasks", 0, task_id)
    await broadcast_event({
        "type": "task_moved",
        "payload": {
            "task_id": task_id,
            "from_column": req.from_column,
            "to_column": req.to_column,
            "project_id": project_id
        }
    })
    return {"success": True, "message": "Task moved successfully"}

@router.delete("/{project_id}/tasks/{task_id}")
async def delete_task(project_id: int, task_id: str, Authorization: str = Header(...)):
    r = get_redis()
    task = r.hgetall(f"task:{task_id}")
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    col = task["column_name"]
    # Remove from board
    col_tasks = json.loads(r.hget(f"project:{project_id}:board", col) or "[]")
    col_tasks = [t for t in col_tasks if t["id"] != task_id]
    r.hset(f"project:{project_id}:board", col, json.dumps(col_tasks))
    # Remove from project tasks set
    r.srem(f"project:{project_id}:tasks", task_id)
    # Remove from column index
    r.lrem(f"project:{project_id}:column:{col}:tasks", 0, task_id)
    # Remove from user assigned tasks
    if "assignee_id" in task:
        r.srem(f"user:{task['assignee_id']}:assigned_tasks", task_id)
    r.delete(f"task:{task_id}")
    # Broadcast WebSocket event
    await broadcast_event({
        "type": "task_deleted",
        "payload": {
            "task_id": task_id,
            "column_name": col,
            "project_id": project_id
        }
    })
    return {"success": True, "message": "Task deleted successfully"} 