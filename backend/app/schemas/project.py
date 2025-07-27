from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.schemas.user import User

# Base schema with common project fields
class ProjectBase(BaseModel):
    """Base project schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

# Schema for creating a new project
class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass

# Schema for updating project information
class ProjectUpdate(BaseModel):
    """Schema for updating project details."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

# Schema for project member
class ProjectMemberBase(BaseModel):
    """Base schema for project member."""
    user_id: int
    role: str = Field("member", pattern="^(owner|admin|member)$")

class ProjectMember(ProjectMemberBase):
    """Schema for project member with full details."""
    id: int
    joined_at: datetime
    user: User
    
    class Config:
        from_attributes = True

# Schema for project without nested data
class Project(ProjectBase):
    """Schema for project in API responses."""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    owner: User
    members: List[ProjectMember] = []
    
    class Config:
        from_attributes = True

# Schema for project with columns (detailed view)
class ProjectWithColumns(Project):
    """Schema for project including all columns."""
    columns: List['BoardColumn'] = []

# Forward reference resolution
from app.schemas.column import BoardColumn
ProjectWithColumns.model_rebuild()