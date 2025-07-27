from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.schemas.project import Project, ProjectCreate, ProjectUpdate, ProjectWithColumns
from app.schemas.user import User
from app.services.project_service import ProjectService
from app.utils.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=Project)
def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project.
    
    - Creates default columns: "To Do", "In Progress", "Done"
    - Current user becomes the project owner
    """
    return ProjectService.create_project(db=db, project=project, owner_id=current_user.id)

@router.get("/", response_model=List[Project])
def read_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all projects where the current user is a member.
    
    Returns projects with basic info and member list.
    """
    return ProjectService.get_user_projects(db, user_id=current_user.id)

@router.get("/{project_id}", response_model=ProjectWithColumns)
def read_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed project information including all columns.
    
    User must be a project member to access.
    """
    db_project = ProjectService.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user is a member
    is_member = any(member.user_id == current_user.id for member in db_project.members)
    if not is_member:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this project"
        )
    
    return db_project

@router.put("/{project_id}", response_model=Project)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update project details.
    
    Only project owner or admin can update.
    """
    db_project = ProjectService.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check permissions
    member = next((m for m in db_project.members if m.user_id == current_user.id), None)
    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this project"
        )
    
    return ProjectService.update_project(
        db, project_id=project_id, project_update=project_update
    )

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a project and all associated data.
    
    Only project owner can delete.
    """
    db_project = ProjectService.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user is owner
    if db_project.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only project owner can delete the project"
        )
    
    success = ProjectService.delete_project(db, project_id=project_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete project")
    
    return {"detail": "Project deleted successfully"}

@router.post("/{project_id}/members/{user_id}")
def add_member(
    project_id: int,
    user_id: int,
    role: str = Query("member", pattern="^(admin|member)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a member to the project.
    
    - **role**: "admin" or "member" (owner role is assigned only on project creation)
    - Only owner or admin can add members
    """
    db_project = ProjectService.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check permissions
    member = next((m for m in db_project.members if m.user_id == current_user.id), None)
    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to add members"
        )
    
    # Check if user exists
    from app.services.user_service import UserService
    user = UserService.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = ProjectService.add_member(db, project_id=project_id, user_id=user_id, role=role)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to add member")
    
    return {"detail": f"Member added successfully with {role} role"}

@router.delete("/{project_id}/members/{user_id}")
def remove_member(
    project_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a member from the project.
    
    - Owner cannot be removed
    - Only owner or admin can remove members
    - Members can remove themselves
    """
    db_project = ProjectService.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check permissions
    member = next((m for m in db_project.members if m.user_id == current_user.id), None)
    if not member:
        raise HTTPException(status_code=403, detail="Not a project member")
    
    # Allow self-removal or admin/owner removing others
    if user_id != current_user.id and member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to remove members"
        )
    
    # Don't allow removing the owner
    target_member = next((m for m in db_project.members if m.user_id == user_id), None)
    if target_member and target_member.role == "owner":
        raise HTTPException(status_code=400, detail="Cannot remove project owner")
    
    success = ProjectService.remove_member(db, project_id=project_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Member not found")
    
    return {"detail": "Member removed successfully"}