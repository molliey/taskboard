import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def project_data():
    return {"title": "Test Project", "description": "A test project."}

def test_create_project(project_data):
    response = client.post("/projects/", json=project_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == project_data["title"]
    assert data["description"] == project_data["description"]
    assert "id" in data
    assert "created_at" in data
    # Save project id for later tests
    project_data["id"] = data["id"]

def test_get_projects():
    response = client.get("/projects/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_single_project(project_data):
    # Create a project first
    create_resp = client.post("/projects/", json=project_data)
    project_id = create_resp.json()["id"]
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["title"] == project_data["title"]

def test_update_project(project_data):
    # Create a project first
    create_resp = client.post("/projects/", json=project_data)
    project_id = create_resp.json()["id"]
    update_data = {"title": "Updated Project", "description": "Updated desc."}
    response = client.put(f"/projects/{project_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]

def test_delete_project(project_data):
    # Create a project first
    create_resp = client.post("/projects/", json=project_data)
    project_id = create_resp.json()["id"]
    response = client.delete(f"/projects/{project_id}")
    assert response.status_code == 204
    # Ensure it's gone
    get_resp = client.get(f"/projects/{project_id}")
    assert get_resp.status_code == 404 