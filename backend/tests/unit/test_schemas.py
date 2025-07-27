import pytest
import sys
import os
from datetime import datetime
from pydantic import ValidationError

# Add the parent directory to the path to import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.schemas.user import UserCreate, UserUpdate, User
from app.schemas.project import ProjectCreate, ProjectUpdate, Project
from app.schemas.column import BoardColumnCreate, BoardColumnUpdate, BoardColumn
from app.schemas.task import TaskCreate, TaskUpdate, TaskMove, Task, TaskStatus

# ====== USER SCHEMA TESTS ======

class TestUserSchemas:
    """Test user schema validation"""

    def test_user_create_valid(self):
        """Test valid user creation data"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User"
        }
        
        user = UserCreate(**user_data)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "password123"
        assert user.full_name == "Test User"

    def test_user_create_required_fields(self):
        """Test that required fields are enforced"""
        # Missing username
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password="password123")
        assert "username" in str(exc_info.value)
        
        # Missing email
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(username="testuser", password="password123")
        assert "email" in str(exc_info.value)
        
        # Missing password
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(username="testuser", email="test@example.com")
        assert "password" in str(exc_info.value)

    def test_user_create_email_validation(self):
        """Test email format validation"""
        # Invalid email format
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="invalid-email",
                password="password123"
            )
        assert "email" in str(exc_info.value).lower()

    def test_user_create_username_length(self):
        """Test username length constraints"""
        # Username too short
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="ab",  # Less than 3 characters
                email="test@example.com",
                password="password123"
            )
        assert "at least 3 characters" in str(exc_info.value)
        
        # Username too long
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="a" * 51,  # More than 50 characters
                email="test@example.com",
                password="password123"
            )
        assert "at most 50 characters" in str(exc_info.value)

    def test_user_create_password_length(self):
        """Test password length constraints"""
        # Password too short
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="123"  # Less than 6 characters
            )
        assert "at least 6 characters" in str(exc_info.value)

    def test_user_update_optional_fields(self):
        """Test that all fields are optional in UserUpdate"""
        # All fields optional
        user_update = UserUpdate()
        assert user_update.model_dump(exclude_unset=True) == {}
        
        # Partial update
        user_update = UserUpdate(username="newname")
        update_data = user_update.model_dump(exclude_unset=True)
        assert update_data == {"username": "newname"}

    def test_user_response_schema(self):
        """Test user response schema excludes sensitive data"""
        user_data = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        user = User(**user_data)
        assert user.id == 1
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        # Note: hashed_password should not be included in response schema

# ====== PROJECT SCHEMA TESTS ======

class TestProjectSchemas:
    """Test project schema validation"""

    def test_project_create_valid(self):
        """Test valid project creation data"""
        project_data = {
            "name": "Test Project",
            "description": "Test project description"
        }
        
        project = ProjectCreate(**project_data)
        assert project.name == "Test Project"
        assert project.description == "Test project description"

    def test_project_create_required_fields(self):
        """Test that required fields are enforced"""
        # Missing name
        with pytest.raises(ValidationError) as exc_info:
            ProjectCreate(description="Test description")
        assert "name" in str(exc_info.value)

    def test_project_create_name_length(self):
        """Test project name length constraints"""
        # Name too short (empty string)
        with pytest.raises(ValidationError) as exc_info:
            ProjectCreate(name="")  # Less than 1 character
        assert "at least 1 character" in str(exc_info.value)
        
        # Name too long
        with pytest.raises(ValidationError) as exc_info:
            ProjectCreate(name="a" * 101)  # More than 100 characters
        assert "at most 100 characters" in str(exc_info.value)

    def test_project_update_optional_fields(self):
        """Test that all fields are optional in ProjectUpdate"""
        # All fields optional
        project_update = ProjectUpdate()
        assert project_update.model_dump(exclude_unset=True) == {}
        
        # Partial update
        project_update = ProjectUpdate(name="New Name")
        update_data = project_update.model_dump(exclude_unset=True)
        assert update_data == {"name": "New Name"}

    def test_project_response_schema(self):
        """Test project response schema structure"""
        owner_data = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True
        }
        
        project_data = {
            "id": 1,
            "name": "Test Project",
            "description": "Test description",
            "owner_id": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "owner": owner_data,
            "members": []
        }
        
        project = Project(**project_data)
        assert project.id == 1
        assert project.name == "Test Project"
        assert project.owner_id == 1

# ====== COLUMN SCHEMA TESTS ======

class TestColumnSchemas:
    """Test column schema validation"""

    def test_column_create_valid(self):
        """Test valid column creation data"""
        column_data = {
            "name": "To Do",
            "position": 0,
            "project_id": 1
        }
        
        column = BoardColumnCreate(**column_data)
        assert column.name == "To Do"
        assert column.position == 0
        assert column.project_id == 1

    def test_column_create_required_fields(self):
        """Test that required fields are enforced"""
        # Missing name
        with pytest.raises(ValidationError) as exc_info:
            BoardColumnCreate(position=0, project_id=1)
        assert "name" in str(exc_info.value)
        
        # Missing position
        with pytest.raises(ValidationError) as exc_info:
            BoardColumnCreate(name="To Do", project_id=1)
        assert "position" in str(exc_info.value)
        
        # Missing project_id
        with pytest.raises(ValidationError) as exc_info:
            BoardColumnCreate(name="To Do", position=0)
        assert "project_id" in str(exc_info.value)

    def test_column_position_validation(self):
        """Test position field validation"""
        # Negative position should be invalid
        with pytest.raises(ValidationError) as exc_info:
            BoardColumnCreate(
                name="To Do",
                position=-1,
                project_id=1
            )
        assert "greater than or equal to 0" in str(exc_info.value)

    def test_column_name_length(self):
        """Test column name length constraints"""
        # Name too short
        with pytest.raises(ValidationError) as exc_info:
            BoardColumnCreate(name="", position=0, project_id=1)
        assert "at least 1 character" in str(exc_info.value)
        
        # Name too long
        with pytest.raises(ValidationError) as exc_info:
            BoardColumnCreate(
                name="a" * 51,  # More than 50 characters
                position=0,
                project_id=1
            )
        assert "at most 50 characters" in str(exc_info.value)

    def test_column_update_optional_fields(self):
        """Test that all fields are optional in BoardColumnUpdate"""
        # All fields optional
        column_update = BoardColumnUpdate()
        assert column_update.model_dump(exclude_unset=True) == {}
        
        # Partial update
        column_update = BoardColumnUpdate(name="New Name", position=1)
        update_data = column_update.model_dump(exclude_unset=True)
        assert update_data == {"name": "New Name", "position": 1}

# ====== TASK SCHEMA TESTS ======

class TestTaskSchemas:
    """Test task schema validation"""

    def test_task_create_valid(self):
        """Test valid task creation data"""
        task_data = {
            "title": "Test Task",
            "description": "Test task description",
            "status": TaskStatus.TODO,
            "position": 0,
            "column_id": 1,
            "assignee_id": 1
        }
        
        task = TaskCreate(**task_data)
        assert task.title == "Test Task"
        assert task.description == "Test task description"
        assert task.status == TaskStatus.TODO
        assert task.position == 0
        assert task.column_id == 1
        assert task.assignee_id == 1

    def test_task_create_required_fields(self):
        """Test that required fields are enforced"""
        # Missing title
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(position=0, column_id=1)
        assert "title" in str(exc_info.value)
        
        # Missing position
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Test Task", column_id=1)
        assert "position" in str(exc_info.value)
        
        # Missing column_id
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Test Task", position=0)
        assert "column_id" in str(exc_info.value)

    def test_task_title_length(self):
        """Test task title length constraints"""
        # Title too short
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="", position=0, column_id=1)
        assert "at least 1 character" in str(exc_info.value)
        
        # Title too long
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(
                title="a" * 201,  # More than 200 characters
                position=0,
                column_id=1
            )
        assert "at most 200 characters" in str(exc_info.value)

    def test_task_description_length(self):
        """Test task description length constraints"""
        # Description too long
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(
                title="Test Task",
                description="a" * 2001,  # More than 2000 characters
                position=0,
                column_id=1
            )
        assert "at most 2000 characters" in str(exc_info.value)

    def test_task_status_enum(self):
        """Test task status enum validation"""
        # Valid enum values
        valid_statuses = [TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.DONE]
        
        for status in valid_statuses:
            task = TaskCreate(
                title="Test Task",
                status=status,
                position=0,
                column_id=1
            )
            assert task.status == status

    def test_task_position_validation(self):
        """Test position field validation"""
        # Negative position should be invalid
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(
                title="Test Task",
                position=-1,
                column_id=1
            )
        assert "greater than or equal to 0" in str(exc_info.value)

    def test_task_update_optional_fields(self):
        """Test that all fields are optional in TaskUpdate"""
        # All fields optional
        task_update = TaskUpdate()
        assert task_update.model_dump(exclude_unset=True) == {}
        
        # Partial update
        task_update = TaskUpdate(title="New Title", status=TaskStatus.IN_PROGRESS)
        update_data = task_update.model_dump(exclude_unset=True)
        assert update_data == {"title": "New Title", "status": TaskStatus.IN_PROGRESS}

    def test_task_move_schema(self):
        """Test task move schema validation"""
        move_data = {
            "task_id": 1,
            "column_id": 2,
            "position": 3
        }
        
        task_move = TaskMove(**move_data)
        assert task_move.task_id == 1
        assert task_move.column_id == 2
        assert task_move.position == 3

    def test_task_move_required_fields(self):
        """Test that all fields are required in TaskMove"""
        # Missing task_id
        with pytest.raises(ValidationError) as exc_info:
            TaskMove(column_id=2, position=3)
        assert "task_id" in str(exc_info.value)
        
        # Missing column_id
        with pytest.raises(ValidationError) as exc_info:
            TaskMove(task_id=1, position=3)
        assert "column_id" in str(exc_info.value)
        
        # Missing position
        with pytest.raises(ValidationError) as exc_info:
            TaskMove(task_id=1, column_id=2)
        assert "position" in str(exc_info.value)

    def test_task_response_schema(self):
        """Test task response schema structure"""
        task_data = {
            "id": 1,
            "title": "Test Task",
            "description": "Test description",
            "status": TaskStatus.TODO,
            "position": 0,
            "column_id": 1,
            "assignee_id": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        task = Task(**task_data)
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.status == TaskStatus.TODO
        assert task.column_id == 1

# ====== VALIDATION EDGE CASES ======

class TestSchemaEdgeCases:
    """Test edge cases in schema validation"""

    def test_unicode_characters(self):
        """Test handling of unicode characters"""
        # User with unicode username
        user = UserCreate(
            username="用户名",
            email="test@example.com",
            password="password123"
        )
        assert user.username == "用户名"
        
        # Project with unicode name
        project = ProjectCreate(
            name="测试项目",
            description="项目描述"
        )
        assert project.name == "测试项目"
        
        # Task with unicode title
        task = TaskCreate(
            title="任务标题",
            description="任务描述",
            position=0,
            column_id=1
        )
        assert task.title == "任务标题"

    def test_special_characters(self):
        """Test handling of special characters"""
        # Username with allowed special characters
        user = UserCreate(
            username="user_123",
            email="test@example.com",
            password="password123"
        )
        assert user.username == "user_123"
        
        # Project name with special characters
        project = ProjectCreate(
            name="Project & Development #1",
            description="Description with symbols: @#$%"
        )
        assert project.name == "Project & Development #1"

    def test_whitespace_handling(self):
        """Test handling of whitespace"""
        # Leading/trailing whitespace should be preserved for titles
        task = TaskCreate(
            title="  Task with spaces  ",
            position=0,
            column_id=1
        )
        assert task.title == "  Task with spaces  "

    def test_none_optional_fields(self):
        """Test None values for optional fields"""
        # Optional fields can be None
        task = TaskCreate(
            title="Test Task",
            description=None,  # Optional field
            position=0,
            column_id=1,
            assignee_id=None  # Optional field
        )
        assert task.description is None
        assert task.assignee_id is None

    def test_default_values(self):
        """Test schema default values"""
        # Task status defaults to TODO
        task = TaskCreate(
            title="Test Task",
            position=0,
            column_id=1
        )
        assert task.status == TaskStatus.TODO

    def test_datetime_fields(self):
        """Test datetime field handling in response schemas"""
        now = datetime.now()
        
        # Test User schema (public) - doesn't have datetime fields
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            full_name="Test User"
        )
        
        assert user.id == 1
        assert user.username == "testuser"
        
        # Test UserInDB schema - has datetime fields
        from app.schemas.user import UserInDB
        user_in_db = UserInDB(
            id=1,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            is_active=True,
            created_at=now,
            updated_at=now,
            hashed_password="hashedpassword"
        )
        
        assert user_in_db.created_at == now
        assert user_in_db.updated_at == now

    def test_model_serialization(self):
        """Test model serialization to dict"""
        task = TaskCreate(
            title="Test Task",
            description="Test description",
            status=TaskStatus.IN_PROGRESS,
            position=1,
            column_id=2,
            assignee_id=3
        )
        
        task_dict = task.model_dump()
        expected = {
            "title": "Test Task",
            "description": "Test description",
            "status": TaskStatus.IN_PROGRESS,
            "position": 1,
            "column_id": 2,
            "assignee_id": 3,
            "due_date": None
        }
        
        assert task_dict == expected

    def test_exclude_unset_serialization(self):
        """Test serialization excluding unset fields"""
        task_update = TaskUpdate(title="New Title")
        
        # Only include fields that were actually set
        update_dict = task_update.model_dump(exclude_unset=True)
        assert update_dict == {"title": "New Title"}

# ====== SCHEMA COMPOSITION TESTS ======

class TestSchemaComposition:
    """Test complex schema relationships and compositions"""

    def test_nested_schema_validation(self):
        """Test validation of schemas with nested objects"""
        # This would test schemas that include other schemas
        # For example, if we had a ProjectWithDetails schema that includes columns
        pass

    def test_conditional_validation(self):
        """Test conditional validation rules"""
        # This would test custom validators that depend on other fields
        pass