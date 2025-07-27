import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def task_data():
    return {
        "title": "Test Task",
        "description": "A test task.",
        "status": "TO DO",
        "project": "Test Project"
    }

def test_create_task(task_data):
    response = client.post("/api/tasks/", json=task_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["status"] == task_data["status"]
    assert data["project"] == task_data["project"]
    assert "id" in data
    task_data["id"] = data["id"]

def test_get_tasks():
    response = client.get("/api/tasks/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_single_task(task_data):
    create_resp = client.post("/api/tasks/", json=task_data)
    task_id = create_resp.json()["id"]
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == task_data["title"]

def test_update_task(task_data):
    create_resp = client.post("/api/tasks/", json=task_data)
    task_id = create_resp.json()["id"]
    update_data = {
        "title": "Updated Task",
        "description": "Updated desc.",
        "status": "IN PROGRESS",
        "project": "Updated Project"
    }
    response = client.put(f"/api/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]
    assert data["status"] == update_data["status"]
    assert data["project"] == update_data["project"]

def test_delete_task(task_data):
    create_resp = client.post("/api/tasks/", json=task_data)
    task_id = create_resp.json()["id"]
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 204
    get_resp = client.get(f"/api/tasks/{task_id}")
    assert get_resp.status_code == 404 