from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base

class Project(Base):
    """
    Project model representing a task board project.
    Each project has columns and tasks.
    """
    __tablename__ = "projects"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Project details
    name = Column(String, nullable=False)
    description = Column(String)
    
    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="owned_projects")
    columns = relationship(
        "BoardColumn", 
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="BoardColumn.position"
    )
    members = relationship(
        "ProjectMember", 
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Project {self.name}>"

class ProjectMember(Base):
    """
    Many-to-many relationship between Project and User.
    Includes role information for access control.
    """
    __tablename__ = "project_members"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Member details
    role = Column(String, default="member")  # owner, admin, member
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_members")
    
    # Ensure unique project-user combination
    __table_args__ = (
        UniqueConstraint('project_id', 'user_id', name='_project_user_uc'),
    )
    
    def __repr__(self):
        return f"<ProjectMember project_id={self.project_id} user_id={self.user_id} role={self.role}>"