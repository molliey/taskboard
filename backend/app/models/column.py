from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.base import Base

class BoardColumn(Base):
    """
    Column model representing a column in a project board.
    Each column contains tasks and has a position for ordering.
    """
    __tablename__ = "columns"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Column details
    name = Column(String, nullable=False)
    position = Column(Integer, nullable=False)
    
    # Foreign key to project
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="columns")
    tasks = relationship(
        "Task", 
        back_populates="column",
        cascade="all, delete-orphan",
        order_by="Task.position"
    )
    
    # Ensure unique position within project
    __table_args__ = (
        UniqueConstraint('project_id', 'position', name='_project_position_uc'),
    )
    
    def __repr__(self):
        return f"<BoardColumn {self.name} position={self.position}>"

