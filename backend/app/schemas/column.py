from pydantic import BaseModel, Field
from typing import Optional, List

# Base schema with common column fields
class BoardColumnBase(BaseModel):
    """Base column schema with common fields."""
    name: str = Field(..., min_length=1, max_length=50)
    position: int = Field(..., ge=0)

# Schema for creating a new column
class BoardColumnCreate(BoardColumnBase):
    """Schema for creating a new column."""
    project_id: int

# Schema for updating column information
class BoardColumnUpdate(BaseModel):
    """Schema for updating column details."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    position: Optional[int] = Field(None, ge=0)

# Schema for column without tasks
class BoardColumn(BoardColumnBase):
    """Schema for column in API responses."""
    id: int
    project_id: int
    
    class Config:
        from_attributes = True

# Schema for column with tasks (detailed view)
class BoardColumnWithTasks(BoardColumn):
    """Schema for column including all tasks."""
    tasks: List['Task'] = []

# Forward reference resolution
from app.schemas.task import Task
BoardColumnWithTasks.model_rebuild()
