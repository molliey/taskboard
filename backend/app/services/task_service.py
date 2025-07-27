from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from app.models.task import Task, TaskStatus as DBTaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskMove, TaskStatus
from typing import Optional, List
from datetime import datetime

class TaskService:
    """Service class for task-related business logic."""
    
    @staticmethod
    def create_task(db: Session, task: TaskCreate) -> Task:
        """
        Create a new task in a column.
        
        Args:
            db: Database session
            task: Task creation data
            
        Returns:
            Created task object
        """
        # Adjust positions of existing tasks if necessary
        existing_tasks = db.query(Task).filter(
            and_(
                Task.column_id == task.column_id,
                Task.position >= task.position
            )
        ).all()
        
        for t in existing_tasks:
            t.position += 1
        
        # Create the new task
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
        Get a task by ID with assignee information.
        
        Args:
            db: Database session
            task_id: Task ID
            
        Returns:
            Task object with assignee or None
        """
        return db.query(Task).options(
            joinedload(Task.assignee)
        ).filter(Task.id == task_id).first()
    
    @staticmethod
    def get_column_tasks(db: Session, column_id: int) -> List[Task]:
        """
        Get all tasks in a column, ordered by position.
        
        Args:
            db: Database session
            column_id: Column ID
            
        Returns:
            List of tasks with assignee information
        """
        return db.query(Task).options(
            joinedload(Task.assignee)
        ).filter(
            Task.column_id == column_id
        ).order_by(Task.position).all()
    
    @staticmethod
    def get_user_tasks(db: Session, user_id: int, status: Optional[str] = None) -> List[Task]:
        """
        Get all tasks assigned to a user, optionally filtered by status.
        
        Args:
            db: Database session
            user_id: User ID
            status: Optional status filter
            
        Returns:
            List of tasks assigned to the user
        """
        query = db.query(Task).options(
            joinedload(Task.assignee),
            joinedload(Task.column)
        ).filter(Task.assignee_id == user_id)
        
        if status:
            query = query.filter(Task.status == DBTaskStatus[status.upper()])
        
        return query.order_by(Task.created_at.desc()).all()
    
    @staticmethod
    def update_task(db: Session, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
        """
        Update task information.
        
        Args:
            db: Database session
            task_id: Task ID
            task_update: Update data
            
        Returns:
            Updated task object or None
        """
        db_task = db.query(Task).filter(Task.id == task_id).first()
        if not db_task:
            return None
        
        update_data = task_update.dict(exclude_unset=True)
        
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
        
        # Update the task
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def move_task(db: Session, task_move: TaskMove) -> Optional[Task]:
        """
        Move a task to a different column and/or position.
        
        Args:
            db: Database session
            task_move: Move operation data
            
        Returns:
            Moved task object or None
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
        Delete a task.
        
        Args:
            db: Database session
            task_id: Task ID
            
        Returns:
            True if deleted, False if not found
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
        Search tasks within a project.
        
        Args:
            db: Database session
            project_id: Project ID
            query: Search query
            
        Returns:
            List of matching tasks
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
        Helper method to reorder tasks within a column.
        
        Args:
            db: Database session
            column_id: Column ID
            task_id: Task being moved
            old_position: Current position
            new_position: Target position
        """
        if new_position > old_position:
            # Moving down
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
            # Moving up
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