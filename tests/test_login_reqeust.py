import pytest
from fastapi.testclient import TestClient
from app.main import app 

client = TestClient(app)

def test_login_success():
    response = client.post("/api/token", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_incorrect_username():
    response = client.post("/api/token", json={"username": "wronguser", "password": "testpassword"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

def test_login_incorrect_password():
    response = client.post("/api/token", json={"username": "testuser", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

def test_login_missing_credentials():
    response = client.post("/api/token", json={})
    assert response.status_code == 422  # Unprocessable Entity