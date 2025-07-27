from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base
import enum

class TaskStatus(enum.Enum):
    """
    Enum for task status values.
    Represents the three states of task progression.
    """
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class Task(Base):
    """
    Task model representing an individual task in a column.
    Tasks can be assigned to users and moved between columns.
    """
    __tablename__ = "tasks"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Task details
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    position = Column(Integer, nullable=False)
    
    # Foreign keys
    column_id = Column(Integer, ForeignKey("columns.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Optional fields
    due_date = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    column = relationship("BoardColumn", back_populates="tasks")
    assignee = relationship(
        "User", 
        back_populates="assigned_tasks",
        foreign_keys=[assignee_id]
    )
    
    def __repr__(self):
        return f"<Task {self.title} status={self.status.value}>"
    
    @property
    def status_value(self):
        """Get the string value of the status enum."""
        return self.status.value if self.status else None

