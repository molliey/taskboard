from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum
from app.schemas.user import User
from typing import List
from typing import List, Optional, Union, Dict


# Task status enum
class TaskStatus(str, Enum):
    """Enum for task status values."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

# Base schema with common task fields
class TaskBase(BaseModel):
    """Base task schema with common fields."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: TaskStatus = TaskStatus.TODO
    position: int = Field(..., ge=0)
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None

# Schema for creating a new task
class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    column_id: int

# Schema for updating task information
class TaskUpdate(BaseModel):
    """Schema for updating task details."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[TaskStatus] = None
    position: Optional[int] = Field(None, ge=0)
    column_id: Optional[int] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None

# Schema for task in API responses
class Task(TaskBase):
    """Schema for task in API responses."""
    id: int
    column_id: int
    created_at: datetime
    updated_at: datetime
    assignee: Optional[User] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

# Schema for moving a task (drag and drop)
class TaskMove(BaseModel):
    """Schema for moving a task to a different position or column."""
    task_id: int
    column_id: int
    position: int = Field(..., ge=0)

# Schema for bulk task operations (optional, for future use)
class TaskBulkUpdate(BaseModel):
    """Schema for bulk updating multiple tasks."""
    task_ids: List[int]
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = None
    column_id: Optional[int] = None

# Schema for task filters (optional, for search/filter functionality)
class TaskFilter(BaseModel):
    """Schema for filtering tasks."""
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = None
    column_id: Optional[int] = None
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None