import pytest
from fastapi import status
from datetime import datetime, timedelta

def test_create_todo_success(client, auth_headers):
    """Test tạo todo thành công"""
    todo_data = {
        "title": "Test Todo",
        "description": "Test Description",
        "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
        "tag_ids": []
    }
    response = client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == todo_data["title"]
    assert data["description"] == todo_data["description"]
    assert "id" in data
    assert "owner_id" in data

def test_create_todo_validation_fail(client, auth_headers):
    """Test tạo todo với validation fail"""
    # Title quá ngắn
    todo_data = {
        "title": "ab",  # < 3 ký tự
        "description": "Test Description"
    }
    response = client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

def test_get_todos_success(client, auth_headers):
    """Test lấy danh sách todos thành công"""
    # Tạo todo trước
    todo_data = {
        "title": "Test Todo",
        "description": "Test Description"
    }
    client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    
    # Lấy danh sách
    response = client.get("/api/v1/todos", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0

def test_get_todo_success(client, auth_headers):
    """Test lấy todo cụ thể thành công"""
    # Tạo todo trước
    todo_data = {
        "title": "Test Todo",
        "description": "Test Description"
    }
    create_response = client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    todo_id = create_response.json()["id"]
    
    # Lấy todo cụ thể
    response = client.get(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == todo_data["title"]

def test_get_todo_not_found(client, auth_headers):
    """Test lấy todo không tồn tại"""
    response = client.get("/api/v1/todos/99999", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "không tồn tại" in response.json()["detail"].lower()

def test_get_todo_unauthorized(client):
    """Test lấy todo mà không có token"""
    response = client.get("/api/v1/todos/1")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_todo_success(client, auth_headers):
    """Test cập nhật todo thành công"""
    # Tạo todo trước
    todo_data = {
        "title": "Original Title",
        "description": "Original Description"
    }
    create_response = client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    todo_id = create_response.json()["id"]
    
    # Cập nhật
    update_data = {
        "title": "Updated Title",
        "is_done": True
    }
    response = client.patch(f"/api/v1/todos/{todo_id}", json=update_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["is_done"] == True

def test_delete_todo_success(client, auth_headers):
    """Test xóa todo thành công"""
    # Tạo todo trước
    todo_data = {
        "title": "Todo to Delete",
        "description": "Will be deleted"
    }
    create_response = client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    todo_id = create_response.json()["id"]
    
    # Xóa
    response = client.delete(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Kiểm tra không còn tồn tại
    get_response = client.get(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_get_overdue_todos(client, auth_headers):
    """Test lấy todos quá hạn"""
    # Tạo overdue todo
    overdue_todo = {
        "title": "Overdue Todo",
        "description": "Should be overdue",
        "due_date": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
    }
    client.post("/api/v1/todos", json=overdue_todo, headers=auth_headers)
    
    # Lấy overdue todos
    response = client.get("/api/v1/todos/overdue", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    # Kiểm tra có overdue todo
    assert len(data) > 0
    assert data[0]["is_done"] == False

def test_get_today_todos(client, auth_headers):
    """Test lấy todos hôm nay"""
    # Tạo today todo
    today_todo = {
        "title": "Today Todo",
        "description": "Should be today",
        "due_date": datetime.utcnow().isoformat() + "Z"
    }
    client.post("/api/v1/todos", json=today_todo, headers=auth_headers)
    
    # Lấy today todos
    response = client.get("/api/v1/todos/today", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
