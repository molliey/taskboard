"""
Task service layer module
Provides all business logic for task operations including CRUD, position management, status changes
Core business logic layer for task management system
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from app.models.task import Task, TaskStatus as DBTaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskMove, TaskStatus
from typing import Optional, List
from datetime import datetime

class TaskService:
    """
    Task service class - handles all task-related business logic
    
    Main responsibilities:
    - Task CRUD operations
    - Task position management (drag-drop sorting)
    - Task status changes
    - Task search and filtering
    """
    
    @staticmethod
    def create_task(db: Session, task: TaskCreate) -> Task:
        """
        Create a new task - core business logic
        
        Key features:
        - Automatically adjusts existing task positions
        - Creates task record
        - Returns complete task object
        """
        # Position management: make space for new task
        existing_tasks = db.query(Task).filter(
            and_(
                Task.column_id == task.column_id,
                Task.position >= task.position
            )
        ).all()
        
        # Increment positions of tasks at and after new position
        for t in existing_tasks:
            t.position += 1
        
        # Create new task record
        db_task = Task(
            title=task.title,
            description=task.description,
            status=DBTaskStatus[task.status.value.upper()],
            position=task.position,
            column_id=task.column_id,
            assignee_id=task.assignee_id,
            due_date=task.due_date
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def get_task(db: Session, task_id: int) -> Optional[Task]:
        """
        Get task by ID with optimized query using joinedload
        """
        return db.query(Task).options(
            joinedload(Task.assignee)  # Preload assignee info to avoid N+1 queries
        ).filter(Task.id == task_id).first()
    
    @staticmethod
    def get_column_tasks(db: Session, column_id: int) -> List[Task]:
        """
        Get all tasks in a column
        
        Key features:
        - Ordered by position (supports drag-drop)
        - Preloads assignee info (performance optimization)
        """
        return db.query(Task).options(
            joinedload(Task.assignee)  # Avoid N+1 query problem
        ).filter(
            Task.column_id == column_id
        ).order_by(Task.position).all()  # Order by position for drag-drop
    
    @staticmethod
    def get_user_tasks(db: Session, user_id: int, status: Optional[str] = None) -> List[Task]:
        """
        Get tasks assigned to a user
        
        Supports:
        - Status filtering (personal workload management)
        - Preloaded related data (performance optimization)
        """
        query = db.query(Task).options(
            joinedload(Task.assignee),
            joinedload(Task.column)  # Preload column info
        ).filter(Task.assignee_id == user_id)
        
        if status:
            query = query.filter(Task.status == DBTaskStatus[status.upper()])
        
        return query.order_by(Task.created_at.desc()).all()
    
    @staticmethod
    def update_task(db: Session, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
        """
        Update task information
        
        Supports partial field updates, automatic position changes and status conversion
        """
        db_task = db.query(Task).filter(Task.id == task_id).first()
        if not db_task:
            return None
        
        update_data = task_update.model_dump(exclude_unset=True)
        
        # Convert status enum if present
        if "status" in update_data:
            update_data["status"] = DBTaskStatus[update_data["status"].upper()]
        
        # Handle position change within the same column
        if "position" in update_data and "column_id" not in update_data:
            if update_data["position"] != db_task.position:
                TaskService._reorder_tasks_in_column(
                    db, db_task.column_id, db_task.id, 
                    db_task.position, update_data["position"]
                )
        
        # Update task fields
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def move_task(db: Session, task_move: TaskMove) -> Optional[Task]:
        """
        Move a task to a different column and/or position
        
        Core functionality: Supports cross-column drag-drop and position adjustment
        """
        db_task = db.query(Task).filter(Task.id == task_move.task_id).first()
        if not db_task:
            return None
        
        old_column_id = db_task.column_id
        old_position = db_task.position
        
        # Remove from old position
        if old_column_id == task_move.column_id:
            # Moving within the same column
            TaskService._reorder_tasks_in_column(
                db, old_column_id, task_move.task_id,
                old_position, task_move.position
            )
        else:
            # Moving to a different column
            # First, close gap in old column
            old_column_tasks = db.query(Task).filter(
                and_(
                    Task.column_id == old_column_id,
                    Task.position > old_position
                )
            ).all()
            
            for t in old_column_tasks:
                t.position -= 1
            
            # Then, make space in new column
            new_column_tasks = db.query(Task).filter(
                and_(
                    Task.column_id == task_move.column_id,
                    Task.position >= task_move.position
                )
            ).all()
            
            for t in new_column_tasks:
                t.position += 1
        
        # Update the task
        db_task.column_id = task_move.column_id
        db_task.position = task_move.position
        
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        """
        Delete a task
        
        Automatically reorders remaining tasks to maintain position continuity
        """
        db_task = db.query(Task).filter(Task.id == task_id).first()
        if not db_task:
            return False
        
        # Reorder remaining tasks
        following_tasks = db.query(Task).filter(
            and_(
                Task.column_id == db_task.column_id,
                Task.position > db_task.position
            )
        ).all()
        
        for t in following_tasks:
            t.position -= 1
        
        db.delete(db_task)
        db.commit()
        return True
    
    @staticmethod
    def search_tasks(db: Session, project_id: int, query: str) -> List[Task]:
        """
        Search tasks within a project
        
        Supports fuzzy search on title and description using LIKE queries
        """
        from app.models.column import BoardColumn
        
        search = f"%{query}%"
        return db.query(Task).join(BoardColumn).options(
            joinedload(Task.assignee)
        ).filter(
            and_(
                BoardColumn.project_id == project_id,
                or_(
                    Task.title.ilike(search),
                    Task.description.ilike(search)
                )
            )
        ).all()
    
    @staticmethod
    def _reorder_tasks_in_column(
        db: Session, 
        column_id: int, 
        task_id: int, 
        old_position: int, 
        new_position: int
    ):
        """
        Helper method to reorder tasks within a column
        
        Core algorithm: Adjust positions of affected tasks based on movement direction
        """
        if new_position > old_position:
            # Moving down: decrement positions of tasks in between
            affected_tasks = db.query(Task).filter(
                and_(
                    Task.column_id == column_id,
                    Task.position > old_position,
                    Task.position <= new_position,
                    Task.id != task_id
                )
            ).all()
            for t in affected_tasks:
                t.position -= 1
        elif new_position < old_position:
            # Moving up: increment positions of tasks in between
            affected_tasks = db.query(Task).filter(
                and_(
                    Task.column_id == column_id,
                    Task.position >= new_position,
                    Task.position < old_position,
                    Task.id != task_id
                )
            ).all()
            for t in affected_tasks:
                t.position += 1