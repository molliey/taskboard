from pydantic import BaseModel
from typing import Optional

class UserRegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

class ProjectCreateRequest(BaseModel):
    name: str
    description: str
    is_active: bool

class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class AddProjectMemberRequest(BaseModel):
    user_id: int
    role: str

class AddProjectMemberByEmailRequest(BaseModel):
    email: str
    role: str

class TaskCreateRequest(BaseModel):
    title: str
    description: str
    tag: str
    due_date: str
    assignee_id: int
    column_name: str

class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tag: Optional[str] = None
    due_date: Optional[str] = None
    assignee_id: Optional[int] = None

class MoveTaskRequest(BaseModel):
    from_column: str
    to_column: str
    position: int 