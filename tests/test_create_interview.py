import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import create_access_token
from unittest.mock import patch, MagicMock

client = TestClient(app)

@pytest.fixture
def mock_interview_service():
    with patch("app.api.endpoint.InterviewService") as mock:
        yield mock

@pytest.fixture
def auth_headers():
    access_token = create_access_token(data={"sub": "testuser"})
    return {"Authorization": f"Bearer {access_token}"}

def test_create_interview_session(mock_interview_service, auth_headers):
    mock_instance = mock_interview_service.return_value
    mock_instance.create_session.return_value = "test_session_id"

    request_data = {
        "resume": "./docs/local/resume.pdf",
        "job_description": "./docs/local/job_description.txt",
        "model": "claude-3-sonnet-20240229"
    }

    response = client.post("/api/v1/interviews", json=request_data, headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {
        "session_id": "test_session_id",
        "message": "Interview session created successfully"
    }

    mock_instance.create_session.assert_called_once_with(
        "./docs/local/resume.pdf",
        "./docs/local/job_description.txt",
        "claude-3-sonnet-20240229"
    )

def test_create_interview_session_unauthorized():
    # 不提供认证令牌
    response = client.post("/api/v1/interviews", json={})
    assert response.status_code == 401

def test_create_interview_session_error(mock_interview_service, auth_headers):
    # 模拟服务抛出异常
    mock_instance = mock_interview_service.return_value
    mock_instance.create_session.side_effect = Exception("Test error")

    # 准备请求数据
    request_data = {
        "resume": "base64_encoded_resume",
        "job_description": "Software Engineer job description",
        "model": "claude-3-sonnet-20240229"
    }

    # 发送POST请求
    response = client.post("/api/v1/interviews", json=request_data, headers=auth_headers)

    # 验证响应
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to create interview session: Test error"}