from sqlalchemy.orm import Session, joinedload
from app.models.project import Project, ProjectMember
from app.models.column import BoardColumn
from app.schemas.project import ProjectCreate, ProjectUpdate
from typing import Optional, List

class ProjectService:
    """Service class for project-related business logic."""
    
    @staticmethod
    def create_project(db: Session, project: ProjectCreate, owner_id: int) -> Project:
        """
        Create a new project with default columns.
        
        Args:
            db: Database session
            project: Project creation data
            owner_id: ID of the project owner
            
        Returns:
            Created project object
        """
        # Create the project
        db_project = Project(
            name=project.name,
            description=project.description,
            owner_id=owner_id
        )
        db.add(db_project)
        db.flush()  # Get the project ID without committing
        
        # Add owner as the first member
        owner_member = ProjectMember(
            project_id=db_project.id,
            user_id=owner_id,
            role="owner"
        )
        db.add(owner_member)
        
        # Create default columns
        default_columns = [
            {"name": "To Do", "position": 0},
            {"name": "In Progress", "position": 1},
            {"name": "Done", "position": 2}
        ]
        
        for col_data in default_columns:
            db_column = BoardColumn(
                name=col_data["name"],
                position=col_data["position"],
                project_id=db_project.id
            )
            db.add(db_column)
        
        db.commit()
        db.refresh(db_project)
        return db_project
    
    @staticmethod
    def get_project(db: Session, project_id: int) -> Optional[Project]:
        """
        Get a project by ID with all related data.
        
        Args:
            db: Database session
            project_id: Project ID
            
        Returns:
            Project object with members and columns or None
        """
        return db.query(Project).options(
            joinedload(Project.owner),
            joinedload(Project.members).joinedload(ProjectMember.user),
            joinedload(Project.columns)
        ).filter(Project.id == project_id).first()
    
    @staticmethod
    def get_user_projects(db: Session, user_id: int) -> List[Project]:
        """
        Get all projects where a user is a member.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of projects
        """
        return db.query(Project).join(ProjectMember).options(
            joinedload(Project.owner),
            joinedload(Project.members).joinedload(ProjectMember.user)
        ).filter(ProjectMember.user_id == user_id).all()
    
    @staticmethod
    def update_project(db: Session, project_id: int, project_update: ProjectUpdate) -> Optional[Project]:
        """
        Update project information.
        
        Args:
            db: Database session
            project_id: Project ID
            project_update: Update data
            
        Returns:
            Updated project object or None
        """
        db_project = db.query(Project).filter(Project.id == project_id).first()
        if not db_project:
            return None
        
        update_data = project_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)
        
        db.commit()
        db.refresh(db_project)
        return db_project
    
    @staticmethod
    def delete_project(db: Session, project_id: int) -> bool:
        """
        Delete a project and all related data.
        
        Args:
            db: Database session
            project_id: Project ID
            
        Returns:
            True if deleted, False if not found
        """
        db_project = db.query(Project).filter(Project.id == project_id).first()
        if not db_project:
            return False
        
        db.delete(db_project)
        db.commit()
        return True
    
    @staticmethod
    def add_member(db: Session, project_id: int, user_id: int, role: str = "member") -> Optional[ProjectMember]:
        """
        Add a member to a project.
        
        Args:
            db: Database session
            project_id: Project ID
            user_id: User ID to add
            role: Member role (owner, admin, member)
            
        Returns:
            ProjectMember object or None if already exists
        """
        # Check if member already exists
        existing = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        ).first()
        
        if existing:
            # Update role if different
            if existing.role != role:
                existing.role = role
                db.commit()
                db.refresh(existing)
            return existing
        
        # Create new member
        db_member = ProjectMember(
            project_id=project_id,
            user_id=user_id,
            role=role
        )
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member
    
    @staticmethod
    def remove_member(db: Session, project_id: int, user_id: int) -> bool:
        """
        Remove a member from a project.
        
        Args:
            db: Database session
            project_id: Project ID
            user_id: User ID to remove
            
        Returns:
            True if removed, False if not found
        """
        db_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        ).first()
        
        if not db_member:
            return False
        
        db.delete(db_member)
        db.commit()
        return True
    
    @staticmethod
    def get_project_members(db: Session, project_id: int) -> List[ProjectMember]:
        """
        Get all members of a project.
        
        Args:
            db: Database session
            project_id: Project ID
            
        Returns:
            List of project members
        """
        return db.query(ProjectMember).options(
            joinedload(ProjectMember.user)
        ).filter(ProjectMember.project_id == project_id).all()
    
    @staticmethod
    def is_project_member(db: Session, project_id: int, user_id: int) -> bool:
        """
        Check if a user is a member of a project.
        
        Args:
            db: Database session
            project_id: Project ID
            user_id: User ID
            
        Returns:
            True if member, False otherwise
        """
        return db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        ).first() is not None