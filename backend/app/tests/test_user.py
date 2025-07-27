import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "email": "testuser@example.com"
    }

def test_create_user(user_data):
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    user_data["id"] = data["id"]

def test_get_users():
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# No single user GET endpoint in your current API, so skipping that

def test_update_user(user_data):
    # Not implemented in your API, so this is a placeholder
    pass

def test_delete_user(user_data):
    # Not implemented in your API, so this is a placeholder
    pass 