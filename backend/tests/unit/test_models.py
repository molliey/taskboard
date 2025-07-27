import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime

# Add the parent directory to the path to import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.base import Base
from app.models.user import User
from app.models.project import Project, ProjectMember
from app.models.column import BoardColumn
from app.models.task import Task, TaskStatus

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_models.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

class TestUserModel:
    """Test User model validation and constraints"""

    def test_create_valid_user(self, db_session):
        """Test creating a valid user"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            full_name="Test User"
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True  # Default value
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_unique_username(self, db_session):
        """Test that usernames must be unique"""
        user1 = User(
            username="testuser",
            email="test1@example.com",
            hashed_password="hashed_password"
        )
        user2 = User(
            username="testuser",  # Same username
            email="test2@example.com",
            hashed_password="hashed_password"
        )
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_unique_email(self, db_session):
        """Test that emails must be unique"""
        user1 = User(
            username="testuser1",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        user2 = User(
            username="testuser2",
            email="test@example.com",  # Same email
            hashed_password="hashed_password"
        )
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_required_fields(self, db_session):
        """Test that required fields cannot be null"""
        # Missing username
        user1 = User(
            email="test@example.com",
            hashed_password="hashed_password"
        )
        
        db_session.add(user1)
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Missing email
        user2 = User(
            username="testuser",
            hashed_password="hashed_password"
        )
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_repr(self, db_session):
        """Test user string representation"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        
        assert repr(user) == "<User testuser>"

class TestProjectModel:
    """Test Project model validation and constraints"""

    def test_create_valid_project(self, db_session):
        """Test creating a valid project"""
        # Create user first
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        project = Project(
            name="Test Project",
            description="Test description",
            owner_id=user.id
        )
        
        db_session.add(project)
        db_session.commit()
        
        assert project.id is not None
        assert project.name == "Test Project"
        assert project.description == "Test description"
        assert project.owner_id == user.id
        assert project.created_at is not None
        assert project.updated_at is not None

    def test_project_required_fields(self, db_session):
        """Test that required fields cannot be null"""
        # Missing name
        project1 = Project(
            description="Test description",
            owner_id=1
        )
        
        db_session.add(project1)
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Missing owner_id
        project2 = Project(
            name="Test Project",
            description="Test description"
        )
        
        db_session.add(project2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_project_foreign_key_constraint(self, db_session):
        """Test foreign key constraint to user"""
        from sqlalchemy import text
        # Enable foreign key constraints for SQLite
        db_session.execute(text("PRAGMA foreign_keys=ON"))
        
        project = Project(
            name="Test Project",
            description="Test description",
            owner_id=999  # Non-existent user
        )
        
        db_session.add(project)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_project_repr(self, db_session):
        """Test project string representation"""
        project = Project(
            name="Test Project",
            description="Test description",
            owner_id=1
        )
        
        assert repr(project) == "<Project Test Project>"

class TestProjectMemberModel:
    """Test ProjectMember model validation and constraints"""

    def test_create_valid_project_member(self, db_session):
        """Test creating a valid project member"""
        # Create user and project first
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        project = Project(
            name="Test Project",
            description="Test description",
            owner_id=user.id
        )
        db_session.add(project)
        db_session.commit()
        
        member = ProjectMember(
            project_id=project.id,
            user_id=user.id,
            role="admin"
        )
        
        db_session.add(member)
        db_session.commit()
        
        assert member.id is not None
        assert member.project_id == project.id
        assert member.user_id == user.id
        assert member.role == "admin"
        assert member.joined_at is not None

    def test_project_member_unique_constraint(self, db_session):
        """Test that user can only be member of project once"""
        # Create user and project
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        project = Project(
            name="Test Project",
            description="Test description",
            owner_id=user.id
        )
        db_session.add(project)
        db_session.commit()
        
        # Add first membership
        member1 = ProjectMember(
            project_id=project.id,
            user_id=user.id,
            role="admin"
        )
        db_session.add(member1)
        db_session.commit()
        
        # Try to add duplicate membership
        member2 = ProjectMember(
            project_id=project.id,
            user_id=user.id,
            role="member"
        )
        db_session.add(member2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_project_member_default_role(self, db_session):
        """Test default role for project member"""
        # Create user and project
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        project = Project(
            name="Test Project",
            description="Test description",
            owner_id=user.id
        )
        db_session.add(project)
        db_session.commit()
        
        member = ProjectMember(
            project_id=project.id,
            user_id=user.id
            # No role specified - should default to "member"
        )
        
        db_session.add(member)
        db_session.commit()
        
        assert member.role == "member"

class TestColumnModel:
    """Test BoardColumn model validation and constraints"""

    def test_create_valid_column(self, db_session):
        """Test creating a valid column"""
        # Create user and project first
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        project = Project(
            name="Test Project",
            description="Test description",
            owner_id=user.id
        )
        db_session.add(project)
        db_session.commit()
        
        column = BoardColumn(
            name="To Do",
            position=0,
            project_id=project.id
        )
        
        db_session.add(column)
        db_session.commit()
        
        assert column.id is not None
        assert column.name == "To Do"
        assert column.position == 0
        assert column.project_id == project.id

    def test_column_unique_position_constraint(self, db_session):
        """Test that position must be unique within project"""
        # Create user and project
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        project = Project(
            name="Test Project",
            description="Test description",
            owner_id=user.id
        )
        db_session.add(project)
        db_session.commit()
        
        # Add first column
        column1 = BoardColumn(
            name="To Do",
            position=0,
            project_id=project.id
        )
        db_session.add(column1)
        db_session.commit()
        
        # Try to add column with same position in same project
        column2 = BoardColumn(
            name="In Progress",
            position=0,  # Same position
            project_id=project.id
        )
        db_session.add(column2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_column_different_projects_same_position(self, db_session):
        """Test that columns in different projects can have same position"""
        # Create user and projects
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        project1 = Project(
            name="Test Project 1",
            description="Test description",
            owner_id=user.id
        )
        project2 = Project(
            name="Test Project 2",
            description="Test description",
            owner_id=user.id
        )
        db_session.add_all([project1, project2])
        db_session.commit()
        
        # Add columns with same position in different projects
        column1 = BoardColumn(
            name="To Do",
            position=0,
            project_id=project1.id
        )
        column2 = BoardColumn(
            name="To Do",
            position=0,  # Same position, different project
            project_id=project2.id
        )
        
        db_session.add_all([column1, column2])
        db_session.commit()  # Should not raise error
        
        assert column1.position == column2.position
        assert column1.project_id != column2.project_id

class TestTaskModel:
    """Test Task model validation and constraints"""

    def test_create_valid_task(self, db_session):
        """Test creating a valid task"""
        # Create user, project, and column first
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        project = Project(
            name="Test Project",
            description="Test description",
            owner_id=user.id
        )
        db_session.add(project)
        db_session.commit()
        
        column = BoardColumn(
            name="To Do",
            position=0,
            project_id=project.id
        )
        db_session.add(column)
        db_session.commit()
        
        task = Task(
            title="Test Task",
            description="Test description",
            status=TaskStatus.TODO,
            position=0,
            column_id=column.id,
            assignee_id=user.id
        )
        
        db_session.add(task)
        db_session.commit()
        
        assert task.id is not None
        assert task.title == "Test Task"
        assert task.description == "Test description"
        assert task.status == TaskStatus.TODO
        assert task.position == 0
        assert task.column_id == column.id
        assert task.assignee_id == user.id
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_task_required_fields(self, db_session):
        """Test that required fields cannot be null"""
        # Missing title
        task1 = Task(
            description="Test description",
            status=TaskStatus.TODO,
            position=0,
            column_id=1
        )
        
        db_session.add(task1)
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Missing column_id
        task2 = Task(
            title="Test Task",
            description="Test description",
            status=TaskStatus.TODO,
            position=0
        )
        
        db_session.add(task2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_task_status_enum(self, db_session):
        """Test task status enum values"""
        # Test all valid enum values
        valid_statuses = [TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.DONE]
        
        for status in valid_statuses:
            # Create basic dependencies
            user = User(
                username=f"user_{status.value}",
                email=f"user_{status.value}@example.com",
                hashed_password="hashed_password"
            )
            db_session.add(user)
            db_session.commit()
            
            project = Project(
                name=f"Project {status.value}",
                description="Test description",
                owner_id=user.id
            )
            db_session.add(project)
            db_session.commit()
            
            column = BoardColumn(
                name=f"Column {status.value}",
                position=0,
                project_id=project.id
            )
            db_session.add(column)
            db_session.commit()
            
            task = Task(
                title=f"Task {status.value}",
                description="Test description",
                status=status,
                position=0,
                column_id=column.id
            )
            
            db_session.add(task)
            db_session.commit()
            
            assert task.status == status

    def test_task_foreign_key_constraints(self, db_session):
        """Test foreign key constraints"""
        from sqlalchemy import text
        # Enable foreign key constraints for SQLite
        db_session.execute(text("PRAGMA foreign_keys=ON"))
        
        # Invalid column_id
        task1 = Task(
            title="Test Task",
            description="Test description",
            status=TaskStatus.TODO,
            position=0,
            column_id=999  # Non-existent column
        )
        
        db_session.add(task1)
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Invalid assignee_id
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        project = Project(
            name="Test Project",
            description="Test description",
            owner_id=user.id
        )
        db_session.add(project)
        db_session.commit()
        
        column = BoardColumn(
            name="To Do",
            position=0,
            project_id=project.id
        )
        db_session.add(column)
        db_session.commit()
        
        task2 = Task(
            title="Test Task",
            description="Test description",
            status=TaskStatus.TODO,
            position=0,
            column_id=column.id,
            assignee_id=999  # Non-existent user
        )
        
        db_session.add(task2)
        with pytest.raises(IntegrityError):
            db_session.commit()

class TestModelRelationships:
    """Test relationships between models"""

    def test_user_owned_projects_relationship(self, db_session):
        """Test user to owned projects relationship"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        project1 = Project(
            name="Project 1",
            description="Description 1",
            owner_id=user.id
        )
        project2 = Project(
            name="Project 2",
            description="Description 2",
            owner_id=user.id
        )
        
        db_session.add_all([project1, project2])
        db_session.commit()
        
        # Test relationship
        db_session.refresh(user)
        assert len(user.owned_projects) == 2
        assert project1 in user.owned_projects
        assert project2 in user.owned_projects

    def test_project_columns_relationship(self, db_session):
        """Test project to columns relationship"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        project = Project(
            name="Test Project",
            description="Test description",
            owner_id=user.id
        )
        db_session.add(project)
        db_session.commit()
        
        column1 = BoardColumn(
            name="To Do",
            position=0,
            project_id=project.id
        )
        column2 = BoardColumn(
            name="In Progress",
            position=1,
            project_id=project.id
        )
        
        db_session.add_all([column1, column2])
        db_session.commit()
        
        # Test relationship
        db_session.refresh(project)
        assert len(project.columns) == 2
        assert column1 in project.columns
        assert column2 in project.columns

    def test_column_tasks_relationship(self, db_session):
        """Test column to tasks relationship"""
        # Create dependencies
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        project = Project(
            name="Test Project",
            description="Test description",
            owner_id=user.id
        )
        db_session.add(project)
        db_session.commit()
        
        column = BoardColumn(
            name="To Do",
            position=0,
            project_id=project.id
        )
        db_session.add(column)
        db_session.commit()
        
        task1 = Task(
            title="Task 1",
            description="Description 1",
            status=TaskStatus.TODO,
            position=0,
            column_id=column.id
        )
        task2 = Task(
            title="Task 2",
            description="Description 2",
            status=TaskStatus.TODO,
            position=1,
            column_id=column.id
        )
        
        db_session.add_all([task1, task2])
        db_session.commit()
        
        # Test relationship
        db_session.refresh(column)
        assert len(column.tasks) == 2
        assert task1 in column.tasks
        assert task2 in column.tasks

    def test_cascade_deletion(self, db_session):
        """Test cascade deletion behavior"""
        # Create user with project
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        project = Project(
            name="Test Project",
            description="Test description",
            owner_id=user.id
        )
        db_session.add(project)
        db_session.commit()
        
        column = BoardColumn(
            name="To Do",
            position=0,
            project_id=project.id
        )
        db_session.add(column)
        db_session.commit()
        
        task = Task(
            title="Test Task",
            description="Test description",
            status=TaskStatus.TODO,
            position=0,
            column_id=column.id
        )
        db_session.add(task)
        db_session.commit()
        
        # Delete project - should cascade to columns and tasks
        db_session.delete(project)
        db_session.commit()
        
        # Verify cascade deletion
        assert db_session.query(BoardColumn).filter_by(project_id=project.id).first() is None
        assert db_session.query(Task).filter_by(column_id=column.id).first() is None