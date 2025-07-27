import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.user import User
from app.models.project import Project, ProjectMember
from app.models.column import BoardColumn
from app.models.task import Task, TaskStatus
from app.utils.auth import get_password_hash, create_access_token

# ====== Core Business Process Tests ======

class TestProjectCreationWorkflow:
    """Test complete project setup workflow"""
    
    def test_complete_project_setup_workflow(self, client, db_session):
        """Test the complete project creation workflow"""
        
        # 1. Register user
        user_data = {
            "username": "projectowner",
            "email": "owner@example.com",
            "password": "password123",
            "full_name": "Project Owner"
        }
        register_response = client.post("/api/users/register", json=user_data)
        assert register_response.status_code == 201
        user_info = register_response.json()
        
        # 2. User login
        login_data = {
            "username": "projectowner",
            "password": "password123"
        }
        login_response = client.post("/api/users/login", data=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Create project
        project_data = {
            "name": "Team Task Board",
            "description": "Project for team collaboration"
        }
        project_response = client.post("/api/projects/", json=project_data, headers=headers)
        assert project_response.status_code == 201
        project = project_response.json()
        
        # 4. Verify project details include default columns
        project_detail_response = client.get(f"/api/projects/{project['id']}", headers=headers)
        assert project_detail_response.status_code == 200
        project_detail = project_detail_response.json()
        
        assert len(project_detail["columns"]) == 3
        column_names = [col["name"] for col in project_detail["columns"]]
        assert "To Do" in column_names
        assert "In Progress" in column_names
        assert "Done" in column_names

class TestTaskManagementWorkflow:
    """Test task lifecycle workflow"""
    
    def test_task_lifecycle_workflow(self, client, db_session):
        """Test complete task lifecycle from creation to completion"""
        
        # Setup: Create user and project
        user = User(
            username="taskmanager",
            email="task@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Task Manager"
        )
        db_session.add(user)
        db_session.commit()
        
        project = Project(
            name="Task Management Project",
            description="For testing task workflows",
            owner_id=user.id
        )
        db_session.add(project)
        db_session.flush()
        
        # Add project members and default columns
        member = ProjectMember(project_id=project.id, user_id=user.id, role="owner")
        columns = [
            BoardColumn(name="To Do", position=0, project_id=project.id),
            BoardColumn(name="In Progress", position=1, project_id=project.id),
            BoardColumn(name="Done", position=2, project_id=project.id)
        ]
        db_session.add(member)
        db_session.add_all(columns)
        db_session.commit()
        
        token = create_access_token({"sub": user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Create task
        todo_column = columns[0]
        task_data = {
            "title": "Implement user authentication",
            "description": "Add JWT-based authentication system",
            "status": "todo",
            "position": 0,
            "column_id": todo_column.id
        }
        create_response = client.post("/api/tasks/", json=task_data, headers=headers)
        assert create_response.status_code == 201
        task = create_response.json()
        
        # 2. Update task information
        update_data = {
            "title": "Implement user authentication system",
            "description": "Add JWT-based authentication with refresh tokens",
            "status": "todo"
        }
        update_response = client.put(f"/api/tasks/{task['id']}", json=update_data, headers=headers)
        assert update_response.status_code == 200
        updated_task = update_response.json()
        assert updated_task["title"] == update_data["title"]
        assert updated_task["description"] == update_data["description"]
        
        # 3. Move task to In Progress column
        in_progress_column = columns[1]
        move_data = {
            "task_id": task["id"],
            "column_id": in_progress_column.id,
            "position": 0
        }
        move_response = client.post("/api/tasks/move", json=move_data, headers=headers)
        assert move_response.status_code == 200
        moved_task = move_response.json()
        assert moved_task["column_id"] == in_progress_column.id
        
        # 4. Update task status to in_progress
        status_update = {
            "status": "in_progress"
        }
        status_response = client.put(f"/api/tasks/{task['id']}", json=status_update, headers=headers)
        assert status_response.status_code == 200
        assert status_response.json()["status"] == "in_progress"
        
        # 5. Move task to Done column and complete
        done_column = columns[2]
        final_move_data = {
            "task_id": task["id"],
            "column_id": done_column.id,
            "position": 0
        }
        final_move_response = client.post("/api/tasks/move", json=final_move_data, headers=headers)
        assert final_move_response.status_code == 200
        
        completion_update = {
            "status": "done"
        }
        completion_response = client.put(f"/api/tasks/{task['id']}", json=completion_update, headers=headers)
        assert completion_response.status_code == 200
        assert completion_response.json()["status"] == "done"
        
        # 6. Verify task is in correct column
        get_task_response = client.get(f"/api/tasks/{task['id']}", headers=headers)
        assert get_task_response.status_code == 200
        final_task = get_task_response.json()
        assert final_task["column_id"] == done_column.id
        assert final_task["status"] == "done"

class TestTeamCollaborationWorkflow:
    """Test team project collaboration workflow"""
    
    def test_team_project_collaboration_workflow(self, client, db_session):
        """Test team collaboration on a project"""
        
        # Create project owner
        owner = User(
            username="teamowner",
            email="owner@team.com",
            hashed_password=get_password_hash("password123"),
            full_name="Team Owner"
        )
        db_session.add(owner)
        
        # Create team member
        member = User(
            username="teammember",
            email="member@team.com", 
            hashed_password=get_password_hash("password123"),
            full_name="Team Member"
        )
        db_session.add(member)
        db_session.commit()
        
        # Project owner login
        owner_token = create_access_token({"sub": owner.username})
        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        
        # Team member login
        member_token = create_access_token({"sub": member.username})
        member_headers = {"Authorization": f"Bearer {member_token}"}
        
        # 1. Owner creates project
        project_data = {
            "name": "Team Collaboration Project",
            "description": "Testing team collaboration features"
        }
        project_response = client.post("/api/projects/", json=project_data, headers=owner_headers)
        assert project_response.status_code == 201
        project = project_response.json()
        
        # 2. Owner adds member to project
        add_member_response = client.post(
            f"/api/projects/{project['id']}/members/{member.id}?role=member",
            headers=owner_headers
        )
        assert add_member_response.status_code == 200
        
        # 3. Verify member can access project
        member_project_response = client.get(f"/api/projects/{project['id']}", headers=member_headers)
        assert member_project_response.status_code == 200
        
        # 4. Member creates task
        project_detail = member_project_response.json()
        todo_column = next(col for col in project_detail["columns"] if col["name"] == "To Do")
        
        task_data = {
            "title": "Setup development environment",
            "description": "Configure local development environment",
            "status": "todo",
            "position": 0,
            "column_id": todo_column["id"],
            "assignee_id": member.id
        }
        task_response = client.post("/api/tasks/", json=task_data, headers=member_headers)
        assert task_response.status_code == 201
        task = task_response.json()
        
        # 5. Owner can see member's task
        owner_task_response = client.get(f"/api/tasks/{task['id']}", headers=owner_headers)
        assert owner_task_response.status_code == 200
        owner_viewed_task = owner_task_response.json()
        assert owner_viewed_task["id"] == task["id"]
        
        # 6. Member completes task - move to completion status
        in_progress_column = next(col for col in project_detail["columns"] if col["name"] == "In Progress")
        done_column = next(col for col in project_detail["columns"] if col["name"] == "Done")
        
        # Move to in progress
        move_to_progress = {
            "task_id": task["id"],
            "column_id": in_progress_column["id"],
            "position": 0
        }
        client.post("/api/tasks/move", json=move_to_progress, headers=member_headers)
        
        # Update status to in progress
        client.put(f"/api/tasks/{task['id']}", json={"status": "in_progress"}, headers=member_headers)
        
        # Move to done
        move_to_done = {
            "task_id": task["id"],
            "column_id": done_column["id"],
            "position": 0
        }
        client.post("/api/tasks/move", json=move_to_done, headers=member_headers)
        
        # Mark as done
        completion_response = client.put(f"/api/tasks/{task['id']}", json={"status": "done"}, headers=member_headers)
        assert completion_response.status_code == 200
        
        # 7. Verify owner can see completed task
        final_task_response = client.get(f"/api/tasks/{task['id']}", headers=owner_headers)
        assert final_task_response.status_code == 200
        final_task_data = final_task_response.json()
        assert final_task_data["column_id"] == done_column["id"]
        assert final_task_data["status"] == "done"

class TestComplexWorkflowScenarios:
    """Test complex workflow scenarios"""
    
    def test_multi_column_task_organization_workflow(self, client, db_session):
        """Test organizing tasks across multiple columns"""
        
        # Setup user and project
        user = User(
            username="organizer",
            email="organizer@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Task Organizer"
        )
        db_session.add(user)
        db_session.commit()
        
        token = create_access_token({"sub": user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Create project
        project_data = {
            "name": "Complex Workflow Project",
            "description": "Testing complex task organization"
        }
        project_response = client.post("/api/projects/", json=project_data, headers=headers)
        assert project_response.status_code == 201
        project = project_response.json()
        
        # 2. Add custom column (avoid position conflict with default columns)
        custom_columns = [
            {"name": "Backlog", "position": 3, "project_id": project["id"]},
            {"name": "Ready", "position": 4, "project_id": project["id"]},
            {"name": "Review", "position": 5, "project_id": project["id"]},
            {"name": "Testing", "position": 6, "project_id": project["id"]}
        ]
        
        created_columns = []
        for col_data in custom_columns:
            col_response = client.post("/api/columns/", json=col_data, headers=headers)
            assert col_response.status_code == 201
            created_columns.append(col_response.json())
        
        # 3. Get all columns (including default columns)
        project_detail_response = client.get(f"/api/projects/{project['id']}", headers=headers)
        all_columns = project_detail_response.json()["columns"]
        
        # 4. Create tasks in different columns
        backlog_column = next(col for col in all_columns if col["name"] == "Backlog")
        ready_column = next(col for col in all_columns if col["name"] == "Ready")
        
        tasks_data = [
            {
                "title": "Feature A - Research",
                "description": "Research requirements for Feature A",
                "status": "todo",
                "position": 0,
                "column_id": backlog_column["id"]
            },
            {
                "title": "Feature A - Design",
                "description": "Design UI/UX for Feature A",
                "status": "todo", 
                "position": 1,
                "column_id": backlog_column["id"]
            },
            {
                "title": "Feature B - Implementation",
                "description": "Implement Feature B backend",
                "status": "todo",
                "position": 0,
                "column_id": ready_column["id"]
            }
        ]
        
        created_tasks = []
        for task_data in tasks_data:
            task_response = client.post("/api/tasks/", json=task_data, headers=headers)
            assert task_response.status_code == 201
            created_tasks.append(task_response.json())
        
        # 5. Move tasks between columns to reorganize
        research_task = created_tasks[0]
        move_data = {
            "task_id": research_task["id"],
            "column_id": ready_column["id"],
            "position": 1  # Place after Feature B task
        }
        move_response = client.post("/api/tasks/move", json=move_data, headers=headers)
        assert move_response.status_code == 200
        
        # 6. Verify tasks are correctly organized - check moved tasks
        moved_task_response = client.get(f"/api/tasks/{research_task['id']}", headers=headers)
        assert moved_task_response.status_code == 200
        moved_task_data = moved_task_response.json()
        assert moved_task_data["column_id"] == ready_column["id"]
        assert moved_task_data["title"] == "Feature A - Research"
    
    def test_error_recovery_workflow(self, client, db_session):
        """Test error recovery and access control"""
        
        # Create two users
        user1 = User(
            username="user1",
            email="user1@example.com",
            hashed_password=get_password_hash("password123")
        )
        user2 = User(
            username="user2", 
            email="user2@example.com",
            hashed_password=get_password_hash("password123")
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        
        user1_token = create_access_token({"sub": user1.username})
        user2_token = create_access_token({"sub": user2.username})
        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        # 1. User1 creates project
        project_data = {"name": "Error Recovery Test", "description": "Testing error scenarios"}
        project_response = client.post("/api/projects/", json=project_data, headers=user1_headers)
        assert project_response.status_code == 201
        project = project_response.json()
        
        # 2. User2 tries to access User1's project (should fail)
        access_response = client.get(f"/api/projects/{project['id']}", headers=user2_headers)
        assert access_response.status_code == 403
        
        # 3. User1 adds User2 as member
        add_member_response = client.post(
            f"/api/projects/{project['id']}/members/{user2.id}?role=member",
            headers=user1_headers
        )
        assert add_member_response.status_code == 200
        
        # 4. Now User2 can access project
        access_response = client.get(f"/api/projects/{project['id']}", headers=user2_headers)
        assert access_response.status_code == 200
        
        # 5. User2 tries to delete project (should fail - only owner can delete)
        delete_response = client.delete(f"/api/projects/{project['id']}", headers=user2_headers)
        assert delete_response.status_code == 403
        
        # 6. User1 successfully deletes project
        delete_response = client.delete(f"/api/projects/{project['id']}", headers=user1_headers)
        assert delete_response.status_code == 200
        
        # 7. Verify project is deleted
        verify_response = client.get(f"/api/projects/{project['id']}", headers=user1_headers)
        assert verify_response.status_code == 404 