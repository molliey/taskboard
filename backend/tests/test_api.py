import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path to import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database.base import Base
from app.database.session import get_db
from app.models.user import User as UserModel
from app.models.project import Project as ProjectModel, ProjectMember
from app.models.column import BoardColumn
from app.utils.auth import get_password_hash

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Setup test database for each test"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create test data
    db = TestingSessionLocal()
    try:
        # Create test user
        user = UserModel(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("testpass123")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create second test user
        user2 = UserModel(
            username="testuser2",
            email="test2@example.com",
            hashed_password=get_password_hash("testpass123")
        )
        db.add(user2)
        db.commit()
        db.refresh(user2)
        
        # Create test project
        project = ProjectModel(
            name="Test Project",
            description="A test project",
            owner_id=user.id
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # Create test column
        column = BoardColumn(
            name="Test Column",
            position=0,
            project_id=project.id
        )
        db.add(column)
        db.commit()
        db.refresh(column)
        
        # Create project membership for users
        membership = ProjectMember(
            project_id=project.id,
            user_id=user.id,
            role="admin"
        )
        db.add(membership)
        
        membership2 = ProjectMember(
            project_id=project.id,
            user_id=user2.id,
            role="member"
        )
        db.add(membership2)
        db.commit()
        
    finally:
        db.close()
    
    yield
    
    # Cleanup after each test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers():
    """Get authentication headers for testuser"""
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = client.post("/users/login", data=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {}

@pytest.fixture
def auth_headers_user2():
    """Get authentication headers for testuser2"""
    login_data = {
        "username": "testuser2",
        "password": "testpass123"
    }
    response = client.post("/users/login", data=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {}

# ====== USER TESTS ======

class TestUserAPI:
    """Test user authentication and management endpoints"""
    
    def test_user_registration(self):
        """Test user registration with valid data"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123"
        }
        response = client.post("/users/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "hashed_password" not in data

    def test_user_registration_duplicate_email(self):
        """Test registration fails with duplicate email"""
        user_data = {
            "username": "anotheruser",
            "email": "test@example.com",  # Already exists
            "password": "password123"
        }
        response = client.post("/users/register", json=user_data)
        assert response.status_code == 400

    def test_user_login(self):
        """Test successful user login"""
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = client.post("/users/login", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_user_login_invalid_credentials(self):
        """Test login fails with wrong password"""
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = client.post("/users/login", data=login_data)
        assert response.status_code == 401

    def test_get_current_user(self, auth_headers):
        """Test getting current user info"""
        response = client.get("/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    def test_get_users_list(self, auth_headers):
        """Test getting list of all users"""
        response = client.get("/users/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # At least our two test users

    def test_get_user_by_id(self):
        """Test getting specific user by ID"""
        response = client.get("/users/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["username"] == "testuser"

    def test_unauthorized_access(self):
        """Test that endpoints require authentication"""
        response = client.get("/users/me")
        assert response.status_code == 401

# ====== PROJECT TESTS ======

class TestProjectAPI:
    """Test project management endpoints"""
    
    def test_create_project(self, auth_headers):
        """Test creating a new project"""
        project_data = {
            "name": "New Test Project",
            "description": "A new test project"
        }
        response = client.post("/projects/", json=project_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == project_data["name"]
        assert data["description"] == project_data["description"]
        assert "id" in data
        assert "created_at" in data

    def test_get_projects(self, auth_headers):
        """Test getting list of projects"""
        response = client.get("/projects/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least our test project

    def test_get_single_project(self, auth_headers):
        """Test getting specific project by ID"""
        response = client.get("/projects/1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Test Project"

    def test_update_project(self, auth_headers):
        """Test updating project details"""
        update_data = {
            "name": "Updated Project Name",
            "description": "Updated description"
        }
        response = client.put("/projects/1", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    def test_delete_project(self, auth_headers):
        """Test deleting a project"""
        # Create a project to delete
        project_data = {
            "name": "Project to Delete",
            "description": "This will be deleted"
        }
        create_resp = client.post("/projects/", json=project_data, headers=auth_headers)
        project_id = create_resp.json()["id"]
        
        # Delete the project
        response = client.delete(f"/projects/{project_id}", headers=auth_headers)
        assert response.status_code == 200
        
        # Verify it's deleted
        get_resp = client.get(f"/projects/{project_id}", headers=auth_headers)
        assert get_resp.status_code == 404

    def test_get_project_members(self, auth_headers):
        """Test getting project members via project details"""
        response = client.get("/projects/1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "members" in data
        assert isinstance(data["members"], list)
        assert len(data["members"]) >= 2  # At least our two test users

    def test_unauthorized_project_access(self):
        """Test unauthorized access to projects"""
        response = client.get("/projects/")
        assert response.status_code == 401

# ====== COLUMN TESTS ======

class TestColumnAPI:
    """Test column management endpoints"""
    
    def test_create_column(self, auth_headers):
        """Test creating a new column"""
        column_data = {
            "name": "New Column",
            "position": 1,
            "project_id": 1
        }
        response = client.post("/columns/", json=column_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == column_data["name"]
        assert data["position"] == column_data["position"]
        assert data["project_id"] == 1

    def test_get_project_columns(self, auth_headers):
        """Test getting columns for a project via project details"""
        response = client.get("/projects/1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "columns" in data
        assert isinstance(data["columns"], list)
        assert len(data["columns"]) >= 1  # At least our test column

    def test_update_column(self, auth_headers):
        """Test updating column details"""
        update_data = {
            "name": "Updated Column Name",
            "position": 0
        }
        response = client.put("/columns/1", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]

    def test_delete_column(self, auth_headers):
        """Test deleting a column"""
        # Create a column to delete
        column_data = {
            "name": "Column to Delete",
            "position": 2,
            "project_id": 1
        }
        create_resp = client.post("/columns/", json=column_data, headers=auth_headers)
        column_id = create_resp.json()["id"]
        
        # Delete the column
        response = client.delete(f"/columns/{column_id}", headers=auth_headers)
        assert response.status_code == 200

# ====== TASK TESTS ======

class TestTaskAPI:
    """Test task management endpoints"""
    
    @pytest.fixture
    def task_data(self):
        """Sample task data for testing"""
        return {
            "title": "Test Task",
            "description": "A test task.",
            "status": "todo",
            "column_id": 1,
            "position": 0
        }

    def test_create_task(self, task_data, auth_headers):
        """Test creating a new task"""
        response = client.post("/tasks/", json=task_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["status"] == task_data["status"]
        assert data["column_id"] == task_data["column_id"]
        assert "id" in data

    def test_get_column_tasks(self, auth_headers):
        """Test getting tasks in a column"""
        response = client.get("/tasks/column/1", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_single_task(self, task_data, auth_headers):
        """Test getting a specific task"""
        # Create a task first
        create_resp = client.post("/tasks/", json=task_data, headers=auth_headers)
        task_id = create_resp.json()["id"]
        
        # Get the task
        response = client.get(f"/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == task_data["title"]

    def test_update_task(self, task_data, auth_headers):
        """Test updating task details"""
        # Create a task first
        create_resp = client.post("/tasks/", json=task_data, headers=auth_headers)
        task_id = create_resp.json()["id"]
        
        # Update the task
        update_data = {
            "title": "Updated Task",
            "description": "Updated desc.",
            "status": "in_progress"
        }
        response = client.put(f"/tasks/{task_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["status"] == update_data["status"]

    def test_delete_task(self, task_data, auth_headers):
        """Test deleting a task"""
        # Create a task first
        create_resp = client.post("/tasks/", json=task_data, headers=auth_headers)
        task_id = create_resp.json()["id"]
        
        # Delete the task
        response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 200
        
        # Verify it's deleted
        get_resp = client.get(f"/tasks/{task_id}", headers=auth_headers)
        assert get_resp.status_code == 404

    def test_move_task(self, task_data, auth_headers):
        """Test moving a task to different position/column"""
        # Create a task first
        create_resp = client.post("/tasks/", json=task_data, headers=auth_headers)
        task_id = create_resp.json()["id"]
        
        # Move the task
        move_data = {
            "task_id": task_id,
            "column_id": 1,
            "position": 1
        }
        response = client.post("/tasks/move", json=move_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["position"] == 1

    def test_get_my_tasks(self, task_data, auth_headers):
        """Test getting tasks assigned to current user"""
        # Create a task and assign it to current user
        task_data["assignee_id"] = 1
        client.post("/tasks/", json=task_data, headers=auth_headers)
        
        # Get my tasks
        response = client.get("/tasks/my-tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_assign_task_to_user(self, task_data, auth_headers):
        """Test assigning a task to another user"""
        # Create a task
        create_resp = client.post("/tasks/", json=task_data, headers=auth_headers)
        task_id = create_resp.json()["id"]
        
        # Assign to user 2
        update_data = {
            "assignee_id": 2
        }
        response = client.put(f"/tasks/{task_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["assignee"]["id"] == 2

    def test_unauthorized_task_access(self):
        """Test unauthorized access to tasks"""
        response = client.get("/tasks/column/1")
        assert response.status_code == 401

# ====== PERMISSION TESTS ======

class TestPermissions:
    """Test access control and permissions"""
    
    def test_member_cannot_delete_project(self, auth_headers_user2):
        """Test that project members cannot delete projects"""
        response = client.delete("/projects/1", headers=auth_headers_user2)
        assert response.status_code == 403

    def test_member_can_create_tasks(self, auth_headers_user2):
        """Test that project members can create tasks"""
        task_data = {
            "title": "Member Task",
            "description": "Task created by member",
            "status": "todo",
            "column_id": 1,
            "position": 0
        }
        response = client.post("/tasks/", json=task_data, headers=auth_headers_user2)
        assert response.status_code == 200

    def test_member_can_update_tasks(self, auth_headers, auth_headers_user2):
        """Test that project members can update tasks"""
        # Admin creates a task
        task_data = {
            "title": "Shared Task",
            "description": "Task for testing permissions",
            "status": "todo",
            "column_id": 1,
            "position": 0
        }
        create_resp = client.post("/tasks/", json=task_data, headers=auth_headers)
        task_id = create_resp.json()["id"]
        
        # Member updates the task
        update_data = {"status": "in_progress"}
        response = client.put(f"/tasks/{task_id}", json=update_data, headers=auth_headers_user2)
        assert response.status_code == 200

# ====== INTEGRATION TESTS ======

class TestIntegrationWorkflows:
    """Test complete workflows and user scenarios"""
    
    def test_full_project_workflow(self, auth_headers):
        """Test complete project creation and management workflow"""
        
        # 1. Create a new project
        project_data = {
            "name": "Workflow Project",
            "description": "Testing full workflow"
        }
        project_resp = client.post("/projects/", json=project_data, headers=auth_headers)
        assert project_resp.status_code == 200
        project_id = project_resp.json()["id"]
        
        # 2. Get existing default columns (created automatically with project)
        project_details = client.get(f"/projects/{project_id}", headers=auth_headers)
        assert project_details.status_code == 200
        columns = project_details.json()["columns"]
        assert len(columns) >= 3  # Should have default columns
        
        # Sort by position to get them in order
        columns.sort(key=lambda x: x["position"])
        column1_id = columns[0]["id"]  # To Do
        column2_id = columns[1]["id"]  # In Progress
        column3_id = columns[2]["id"]  # Done
        
        # 3. Create tasks in first column
        task1_data = {
            "title": "Task 1",
            "description": "First task",
            "status": "todo",
            "column_id": column1_id,
            "position": 0
        }
        task1_resp = client.post("/tasks/", json=task1_data, headers=auth_headers)
        assert task1_resp.status_code == 200
        task1_id = task1_resp.json()["id"]
        
        task2_data = {
            "title": "Task 2",
            "description": "Second task",
            "status": "todo",
            "column_id": column1_id,
            "position": 1
        }
        task2_resp = client.post("/tasks/", json=task2_data, headers=auth_headers)
        assert task2_resp.status_code == 200
        task2_id = task2_resp.json()["id"]
        
        # 4. Move first task to In Progress
        move_data = {
            "task_id": task1_id,
            "column_id": column2_id,
            "position": 0
        }
        move_resp = client.post("/tasks/move", json=move_data, headers=auth_headers)
        assert move_resp.status_code == 200
        
        # 5. Update task status
        update_data = {"status": "in_progress"}
        update_resp = client.put(f"/tasks/{task1_id}", json=update_data, headers=auth_headers)
        assert update_resp.status_code == 200
        
        # 6. Complete the task
        complete_move = {
            "task_id": task1_id,
            "column_id": column3_id,
            "position": 0
        }
        complete_resp = client.post("/tasks/move", json=complete_move, headers=auth_headers)
        assert complete_resp.status_code == 200
        
        complete_update = {"status": "done"}
        final_resp = client.put(f"/tasks/{task1_id}", json=complete_update, headers=auth_headers)
        assert final_resp.status_code == 200
        
        # 7. Verify final state
        final_task = client.get(f"/tasks/{task1_id}", headers=auth_headers)
        assert final_task.status_code == 200
        task_data = final_task.json()
        assert task_data["column_id"] == column3_id
        assert task_data["status"] == "done"
        assert task_data["position"] == 0

    def test_collaborative_workflow(self, auth_headers, auth_headers_user2):
        """Test collaboration between multiple users"""
        
        # 1. Admin creates a task
        task_data = {
            "title": "Collaborative Task",
            "description": "Task for collaboration testing",
            "status": "todo",
            "column_id": 1,
            "position": 0
        }
        task_resp = client.post("/tasks/", json=task_data, headers=auth_headers)
        assert task_resp.status_code == 200
        task_id = task_resp.json()["id"]
        
        # 2. Admin assigns task to User 2
        assign_data = {"assignee_id": 2}
        assign_resp = client.put(f"/tasks/{task_id}", json=assign_data, headers=auth_headers)
        assert assign_resp.status_code == 200
        
        # 3. User 2 checks their assigned tasks
        my_tasks_resp = client.get("/tasks/my-tasks", headers=auth_headers_user2)
        assert my_tasks_resp.status_code == 200
        my_tasks = my_tasks_resp.json()
        task_ids = [task["id"] for task in my_tasks]
        assert task_id in task_ids
        
        # 4. User 2 updates the task
        update_data = {
            "status": "in_progress",
            "description": "Working on this collaborative task"
        }
        update_resp = client.put(f"/tasks/{task_id}", json=update_data, headers=auth_headers_user2)
        assert update_resp.status_code == 200
        
        # 5. User 2 completes the task
        complete_data = {"status": "done"}
        complete_resp = client.put(f"/tasks/{task_id}", json=complete_data, headers=auth_headers_user2)
        assert complete_resp.status_code == 200
        
        # 6. Admin verifies the completed task
        final_check = client.get(f"/tasks/{task_id}", headers=auth_headers)
        assert final_check.status_code == 200
        final_data = final_check.json()
        assert final_data["status"] == "done"
        assert final_data["assignee"]["id"] == 2

    def test_project_member_management(self, auth_headers, auth_headers_user2):
        """Test adding and managing project members"""
        
        # 1. Create a new project
        project_data = {
            "name": "Team Project",
            "description": "Project for testing member management"
        }
        project_resp = client.post("/projects/", json=project_data, headers=auth_headers)
        assert project_resp.status_code == 200
        project_id = project_resp.json()["id"]
        
        # 2. Add a member to the project
        member_resp = client.post(f"/projects/{project_id}/members/2", headers=auth_headers)
        # Note: This might return 400 if user is already a member, which is fine
        assert member_resp.status_code in [200, 400]
        
        # 3. Check project members via project details
        members_resp = client.get(f"/projects/{project_id}", headers=auth_headers)
        assert members_resp.status_code == 200
        project_data = members_resp.json()
        assert "members" in project_data
        members = project_data["members"]
        assert isinstance(members, list)
        
        # 4. Verify both users can access the project
        user2_project_resp = client.get(f"/projects/{project_id}", headers=auth_headers_user2)
        assert user2_project_resp.status_code == 200

# ====== EDGE CASES AND ERROR HANDLING ======

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_invalid_task_data(self, auth_headers):
        """Test creating task with invalid data"""
        invalid_data = {
            "title": "",  # Empty title should fail
            "column_id": 1,
            "position": 0
        }
        response = client.post("/tasks/", json=invalid_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error

    def test_nonexistent_resource_access(self, auth_headers):
        """Test accessing resources that don't exist"""
        response = client.get("/tasks/99999", headers=auth_headers)
        assert response.status_code == 404
        
        response = client.get("/projects/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_move_task_to_invalid_column(self, auth_headers):
        """Test moving task to non-existent column"""
        # Create a task first
        task_data = {
            "title": "Test Task",
            "description": "A test task",
            "status": "todo",
            "column_id": 1,
            "position": 0
        }
        task_resp = client.post("/tasks/", json=task_data, headers=auth_headers)
        task_id = task_resp.json()["id"]
        
        # Try to move to invalid column
        move_data = {
            "task_id": task_id,
            "column_id": 99999,  # Non-existent column
            "position": 0
        }
        response = client.post("/tasks/move", json=move_data, headers=auth_headers)
        assert response.status_code == 404

    def test_assign_task_to_non_member(self, auth_headers):
        """Test assigning task to user who is not a project member"""
        # Create a new user who is not a project member
        new_user_data = {
            "username": "outsideuser",
            "email": "outside@example.com",
            "password": "password123"
        }
        client.post("/users/register", json=new_user_data)
        
        # Create a task
        task_data = {
            "title": "Test Task",
            "description": "A test task",
            "status": "todo",
            "column_id": 1,
            "position": 0
        }
        task_resp = client.post("/tasks/", json=task_data, headers=auth_headers)
        task_id = task_resp.json()["id"]
        
        # Try to assign to non-member (user ID 3)
        assign_data = {"assignee_id": 3}
        response = client.put(f"/tasks/{task_id}", json=assign_data, headers=auth_headers)
        assert response.status_code == 400  # Should fail