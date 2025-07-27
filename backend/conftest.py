import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base
from app.main import app
from app.database.session import get_db
from app.models.user import User
from app.models.project import Project, ProjectMember
from app.models.column import BoardColumn
from app.models.task import Task, TaskStatus
from app.utils.auth import get_password_hash, create_access_token

# Simple test database configuration
def create_test_engine():
    """Create a test database engine with unique name for each test"""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    return engine, db_path

@pytest.fixture(scope="function")
def db_engine():
    """Create test database engine"""
    engine, db_path = create_test_engine()
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def db_session(db_engine):
    """Create test database session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.close()

@pytest.fixture
def client(db_session):
    """Create test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# ====== USER FIXTURES ======

@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_user2(db_session):
    """Create a second test user for multi-user tests"""
    user = User(
        username="testuser2",
        email="test2@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User 2",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_token(test_user):
    """Create authentication token for test user"""
    return create_access_token({"sub": test_user.username})

@pytest.fixture
def auth_headers(auth_token):
    """Create authentication headers for test user"""
    return {"Authorization": f"Bearer {auth_token}"}

# ====== PROJECT FIXTURES ======

@pytest.fixture
def test_project(db_session, test_user):
    """Create a test project with default columns"""
    project = Project(
        name="Test Project",
        description="Test project description",
        owner_id=test_user.id
    )
    db_session.add(project)
    db_session.flush()
    
    # Add project member
    member = ProjectMember(
        project_id=project.id,
        user_id=test_user.id,
        role="admin"
    )
    db_session.add(member)
    
    # Add default columns
    columns = [
        BoardColumn(name="To Do", position=0, project_id=project.id),
        BoardColumn(name="In Progress", position=1, project_id=project.id),
        BoardColumn(name="Done", position=2, project_id=project.id)
    ]
    db_session.add_all(columns)
    db_session.commit()
    db_session.refresh(project)
    return project

@pytest.fixture
def test_column(db_session, test_project):
    """Get the first column from test project"""
    return db_session.query(BoardColumn).filter(
        BoardColumn.project_id == test_project.id
    ).first()

@pytest.fixture
def test_task(db_session, test_column):
    """Create a test task"""
    task = Task(
        title="Test Task",
        description="Test task description",
        status=TaskStatus.TODO,
        position=0,
        column_id=test_column.id
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task

# ====== DATA FIXTURES ======

@pytest.fixture
def sample_user_data():
    """Sample user data for creation"""
    return {
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123",
        "full_name": "New User"
    }

@pytest.fixture
def sample_project_data():
    """Sample project data for creation"""
    return {
        "name": "New Project",
        "description": "A new project for testing"
    }

@pytest.fixture
def sample_task_data(test_column):
    """Sample task data for creation"""
    return {
        "title": "New Task",
        "description": "A new task",
        "status": "todo",
        "position": 0,
        "column_id": test_column.id
    }

@pytest.fixture
def sample_column_data(test_project):
    """Sample column data for creation"""
    return {
        "name": "New Column",
        "position": 3,
        "project_id": test_project.id
    }

# ====== COLLECTION FIXTURES ======

@pytest.fixture
def multiple_users(db_session):
    """Create multiple test users"""
    users = []
    for i in range(3):
        user = User(
            username=f"user{i}",
            email=f"user{i}@example.com",
            hashed_password=get_password_hash("password123"),
            full_name=f"User {i}",
            is_active=True
        )
        db_session.add(user)
        users.append(user)
    
    db_session.commit()
    for user in users:
        db_session.refresh(user)
    return users

@pytest.fixture
def multiple_projects(db_session, test_user):
    """Create multiple test projects"""
    projects = []
    for i in range(3):
        project = Project(
            name=f"Project {i}",
            description=f"Test project {i}",
            owner_id=test_user.id
        )
        db_session.add(project)
        projects.append(project)
    
    db_session.commit()
    for project in projects:
        db_session.refresh(project)
    return projects

@pytest.fixture
def multiple_tasks(db_session, test_column):
    """Create multiple test tasks"""
    tasks = []
    for i in range(5):
        task = Task(
            title=f"Task {i}",
            description=f"Test task {i}",
            status=TaskStatus.TODO,
            position=i,
            column_id=test_column.id
        )
        db_session.add(task)
        tasks.append(task)
    
    db_session.commit()
    for task in tasks:
        db_session.refresh(task)
    return tasks

# ====== PYTEST MARKERS ======

def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "websocket: WebSocket tests")
    config.addinivalue_line("markers", "slow: Slow running tests")

# ====== COLLECTION CONFIGURATION ======

def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location"""
    for item in items:
        # Mark unit tests
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Mark e2e tests
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        
        # Mark websocket tests
        if "websocket" in str(item.fspath):
            item.add_marker(pytest.mark.websocket)
        
        # Mark integration tests
        if "integration" in str(item.fspath) or "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.integration)