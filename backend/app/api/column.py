from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.column import BoardColumn, BoardColumnCreate, BoardColumnUpdate, BoardColumnWithTasks
from app.schemas.user import User
from app.services.column_service import ColumnService
from app.services.project_service import ProjectService
from app.utils.auth import get_current_user

router = APIRouter(prefix="/columns", tags=["columns"])

@router.post("/", response_model=BoardColumn, status_code=201)
def create_column(
    column: BoardColumnCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new column in a project.
    
    - **name**: Column name
    - **position**: Order position (0-based)
    - **project_id**: Project to add column to
    """
    # Check if user has access to the project
    db_project = ProjectService.get_project(db, project_id=column.project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    is_member = any(member.user_id == current_user.id for member in db_project.members)
    if not is_member:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to create columns in this project"
        )
    
    return ColumnService.create_column(db=db, column=column)

@router.get("/project/{project_id}", response_model=List[BoardColumnWithTasks])
def read_project_columns(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all columns for a project with their tasks.
    
    Returns columns ordered by position, each with its tasks.
    """
    # Check if user has access to the project
    db_project = ProjectService.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    is_member = any(member.user_id == current_user.id for member in db_project.members)
    if not is_member:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this project"
        )
    
    return ColumnService.get_project_columns(db, project_id=project_id)

@router.get("/{column_id}", response_model=BoardColumnWithTasks)
def read_column(
    column_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific column with all its tasks.
    """
    db_column = ColumnService.get_column(db, column_id=column_id)
    if db_column is None:
        raise HTTPException(status_code=404, detail="Column not found")
    
    # Check if user has access to the project
    db_project = ProjectService.get_project(db, project_id=db_column.project_id)
    is_member = any(member.user_id == current_user.id for member in db_project.members)
    if not is_member:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this column"
        )
    
    return db_column

@router.put("/{column_id}", response_model=BoardColumn)
def update_column(
    column_id: int,
    column_update: BoardColumnUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update column properties.
    
    - Can update name and/or position
    - Reordering handled automatically
    """
    db_column = ColumnService.get_column(db, column_id=column_id)
    if db_column is None:
        raise HTTPException(status_code=404, detail="Column not found")
    
    # Check if user has access to the project
    db_project = ProjectService.get_project(db, project_id=db_column.project_id)
    is_member = any(member.user_id == current_user.id for member in db_project.members)
    if not is_member:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this column"
        )
    
    return ColumnService.update_column(db, column_id=column_id, column_update=column_update)

@router.delete("/{column_id}")
def delete_column(
    column_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a column and all its tasks.
    
    Only project owner or admin can delete columns.
    """
    db_column = ColumnService.get_column(db, column_id=column_id)
    if db_column is None:
        raise HTTPException(status_code=404, detail="Column not found")
    
    # Check if user has admin access to the project
    db_project = ProjectService.get_project(db, project_id=db_column.project_id)
    member = next((m for m in db_project.members if m.user_id == current_user.id), None)
    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete columns"
        )
    
    # Prevent deleting if it's the only column
    columns = ColumnService.get_project_columns(db, project_id=db_column.project_id)
    if len(columns) <= 1:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the last column in a project"
        )
    
    success = ColumnService.delete_column(db, column_id=column_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete column")
    
    return {"detail": "Column deleted successfully"}