"""
Task management API module
Provides complete CRUD operations for tasks including create, read, update, delete and move
Includes permission validation, business logic validation and error handling
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database.session import get_db
from app.schemas.task import Task, TaskCreate, TaskUpdate, TaskMove
from app.schemas.user import User
from app.services.task_service import TaskService
from app.services.column_service import ColumnService
from app.services.project_service import ProjectService
from app.utils.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=Task, status_code=201)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new task
    
    Permission checks:
    - User must be a project member
    - If assignee is specified, they must be a project member
    """
    # Check if user has permission to create tasks in the specified column
    db_column = ColumnService.get_column(db, column_id=task.column_id)
    if not db_column:
        raise HTTPException(status_code=404, detail="Column not found")
    
    # Get project info and check user membership
    db_project = ProjectService.get_project(db, project_id=db_column.project_id)
    is_member = any(member.user_id == current_user.id for member in db_project.members)
    if not is_member:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to create tasks in this project"
        )
    
    # Validate assignee permissions
    if task.assignee_id:
        is_assignee_member = any(
            member.user_id == task.assignee_id for member in db_project.members
        )
        if not is_assignee_member:
            raise HTTPException(
                status_code=400,
                detail="Assignee must be a project member"
            )
    
    return TaskService.create_task(db=db, task=task)

@router.get("/column/{column_id}", response_model=List[Task])
def read_column_tasks(
    column_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all tasks in a specific column
    
    Permission check: User must be a project member to view tasks
    """
    # Check if user has permission to view tasks in the specified column
    db_column = ColumnService.get_column(db, column_id=column_id)
    if not db_column:
        raise HTTPException(status_code=404, detail="Column not found")
    
    # Check project membership
    db_project = ProjectService.get_project(db, project_id=db_column.project_id)
    is_member = any(member.user_id == current_user.id for member in db_project.members)
    if not is_member:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view tasks in this project"
        )
    
    return TaskService.get_column_tasks(db, column_id=column_id)

@router.get("/my-tasks", response_model=List[Task])
def read_my_tasks(
    status: Optional[str] = Query(None, pattern="^(todo|in_progress|done)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get tasks assigned to current user
    
    Optional parameter:
    - status: Filter by status (todo|in_progress|done)
    """
    return TaskService.get_user_tasks(db, user_id=current_user.id, status=status)

@router.get("/{task_id}", response_model=Task)
def read_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific task by ID
    
    Permission check: User must be a project member to view the task
    """
    db_task = TaskService.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if user has access to the task's project
    db_column = ColumnService.get_column(db, column_id=db_task.column_id)
    db_project = ProjectService.get_project(db, project_id=db_column.project_id)
    is_member = any(member.user_id == current_user.id for member in db_project.members)
    if not is_member:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this task"
        )
    
    return db_task

@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update task details
    
    All fields are optional - only provided fields will be updated
    """
    db_task = TaskService.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if user has access to the task's project
    db_column = ColumnService.get_column(db, column_id=db_task.column_id)
    db_project = ProjectService.get_project(db, project_id=db_column.project_id)
    is_member = any(member.user_id == current_user.id for member in db_project.members)
    if not is_member:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this task"
        )
    
    # If changing assignee, verify they're a project member
    if task_update.assignee_id is not None:
        if task_update.assignee_id:
            is_assignee_member = any(
                member.user_id == task_update.assignee_id for member in db_project.members
            )
            if not is_assignee_member:
                raise HTTPException(
                    status_code=400,
                    detail="Assignee must be a project member"
                )
    
    return TaskService.update_task(db, task_id=task_id, task_update=task_update)

@router.post("/move", response_model=Task)
def move_task(
    task_move: TaskMove,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Move a task to a different column
    
    Core functionality: Supports drag-drop sorting with automatic position adjustment
    """
    db_task = TaskService.get_task(db, task_id=task_move.task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if user has permission to move the task
    db_column = ColumnService.get_column(db, column_id=db_task.column_id)
    db_project = ProjectService.get_project(db, project_id=db_column.project_id)
    is_member = any(member.user_id == current_user.id for member in db_project.members)
    if not is_member:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to move this task"
        )
    
    # Validate target column exists and is in the same project
    target_column = ColumnService.get_column(db, column_id=task_move.column_id)
    if not target_column:
        raise HTTPException(status_code=404, detail="Target column not found")
    
    if target_column.project_id != db_column.project_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot move task to column in different project"
        )
    
    return TaskService.move_task(db, task_move=task_move)

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a task
    
    Permission check: User must be a project member to delete the task
    """
    db_task = TaskService.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if user has permission to delete the task
    db_column = ColumnService.get_column(db, column_id=db_task.column_id)
    db_project = ProjectService.get_project(db, project_id=db_column.project_id)
    is_member = any(member.user_id == current_user.id for member in db_project.members)
    if not is_member:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this task"
        )
    
    success = TaskService.delete_task(db, task_id=task_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete task")
    
    return {"message": "Task deleted successfully"}