from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.models.column import BoardColumn
from app.schemas.column import BoardColumnCreate, BoardColumnUpdate
from typing import Optional, List

class ColumnService:
    """Service class for column-related business logic."""
    
    @staticmethod
    def create_column(db: Session, column: BoardColumnCreate) -> BoardColumn:
        """
        Create a new column in a project.
        
        Args:
            db: Database session
            column: Column creation data
            
        Returns:
            Created column object
        """
        # Adjust positions of existing columns if necessary
        existing_columns = db.query(BoardColumn).filter(
            and_(
                BoardColumn.project_id == column.project_id,
                BoardColumn.position >= column.position
            )
        ).all()
        
        for col in existing_columns:
            col.position += 1
        
        # Create the new column
        db_column = BoardColumn(
            name=column.name,
            position=column.position,
            project_id=column.project_id
        )
        db.add(db_column)
        db.commit()
        db.refresh(db_column)
        return db_column
    
    @staticmethod
    def get_column(db: Session, column_id: int) -> Optional[BoardColumn]:
        """
        Get a column by ID with its tasks.
        
        Args:
            db: Database session
            column_id: Column ID
            
        Returns:
            Column object with tasks or None
        """
        return db.query(BoardColumn).options(
            joinedload(BoardColumn.tasks)
        ).filter(BoardColumn.id == column_id).first()
    
    @staticmethod
    def get_project_columns(db: Session, project_id: int) -> List[BoardColumn]:
        """
        Get all columns for a project, ordered by position.
        
        Args:
            db: Database session
            project_id: Project ID
            
        Returns:
            List of columns with their tasks
        """
        return db.query(BoardColumn).options(
            joinedload(BoardColumn.tasks)
        ).filter(
            BoardColumn.project_id == project_id
        ).order_by(BoardColumn.position).all()
    
    @staticmethod
    def update_column(db: Session, column_id: int, column_update: BoardColumnUpdate) -> Optional[BoardColumn]:
        """
        Update column information.
        
        Args:
            db: Database session
            column_id: Column ID
            column_update: Update data
            
        Returns:
            Updated column object or None
        """
        db_column = db.query(BoardColumn).filter(BoardColumn.id == column_id).first()
        if not db_column:
            return None
        
        update_data = column_update.model_dump(exclude_unset=True)
        
        # Handle position change
        if "position" in update_data and update_data["position"] != db_column.position:
            old_position = db_column.position
            new_position = update_data["position"]
            
            # Reorder other columns
            if new_position > old_position:
                # Moving down
                affected_columns = db.query(BoardColumn).filter(
                    and_(
                        BoardColumn.project_id == db_column.project_id,
                        BoardColumn.position > old_position,
                        BoardColumn.position <= new_position,
                        BoardColumn.id != column_id
                    )
                ).all()
                for col in affected_columns:
                    col.position -= 1
            else:
                # Moving up
                affected_columns = db.query(BoardColumn).filter(
                    and_(
                        BoardColumn.project_id == db_column.project_id,
                        BoardColumn.position >= new_position,
                        BoardColumn.position < old_position,
                        BoardColumn.id != column_id
                    )
                ).all()
                for col in affected_columns:
                    col.position += 1
        
        # Update the column
        for field, value in update_data.items():
            setattr(db_column, field, value)
        
        db.commit()
        db.refresh(db_column)
        return db_column
    
    @staticmethod
    def delete_column(db: Session, column_id: int) -> bool:
        """
        Delete a column and all its tasks.
        
        Args:
            db: Database session
            column_id: Column ID
            
        Returns:
            True if deleted, False if not found
        """
        db_column = db.query(BoardColumn).filter(BoardColumn.id == column_id).first()
        if not db_column:
            return False
        
        # Reorder remaining columns
        following_columns = db.query(BoardColumn).filter(
            and_(
                BoardColumn.project_id == db_column.project_id,
                BoardColumn.position > db_column.position
            )
        ).all()
        
        for col in following_columns:
            col.position -= 1
        
        db.delete(db_column)
        db.commit()
        return True
    
    @staticmethod
    def reorder_columns(db: Session, project_id: int, column_order: List[int]) -> bool:
        """
        Reorder all columns in a project.
        
        Args:
            db: Database session
            project_id: Project ID
            column_order: List of column IDs in desired order
            
        Returns:
            True if successful, False otherwise
        """
        columns = db.query(BoardColumn).filter(
            BoardColumn.project_id == project_id
        ).all()
        
        if len(columns) != len(column_order):
            return False
        
        column_map = {col.id: col for col in columns}
        
        for position, column_id in enumerate(column_order):
            if column_id in column_map:
                column_map[column_id].position = position
            else:
                return False
        
        db.commit()
        return True
