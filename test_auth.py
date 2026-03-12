import pytest
from fastapi import status

def test_register_user(client):
    """Test tạo user thành công"""
    user_data = {
        "email": "newuser@example.com",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "hashed_password" not in data

def test_register_duplicate_email(client, test_user):
    """Test register email đã tồn tại"""
    # Register lần đầu
    client.post("/api/v1/auth/register", json=test_user)
    
    # Register lần 2 - nên fail
    response = client.post("/api/v1/auth/register", json=test_user)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "tồn tại" in response.json()["detail"].lower()

def test_login_success(client, test_user):
    """Test đăng nhập thành công"""
    # Register user trước
    client.post("/api/v1/auth/register", json=test_user)
    
    # Login
    response = client.post("/api/v1/auth/login", json=test_user)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test đăng nhập sai thông tin"""
    wrong_user = {
        "email": "wrong@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", json=wrong_user)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "không đúng" in response.json()["detail"].lower()

def test_get_current_user(client, auth_headers):
    """Test lấy thông tin user hiện tại"""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "email" in data
    assert "id" in data

def test_get_current_user_unauthorized(client):
    """Test lấy thông tin user mà không có token"""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
