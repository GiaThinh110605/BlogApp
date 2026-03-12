import pytest
from fastapi import status

def test_soft_delete_todo(client, auth_headers):
    """Test soft delete todo"""
    # Tạo todo
    todo_data = {"title": "Todo to delete", "description": "Will be soft deleted"}
    create_response = client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    todo_id = create_response.json()["id"]
    
    # Soft delete
    response = client.delete(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert "trash" in response.json()["message"].lower()
    
    # Kiểm tra không còn trong active todos
    get_response = client.get("/api/v1/todos", headers=auth_headers)
    todos = get_response.json()["items"]
    assert todo_id not in [todo["id"] for todo in todos]

def test_get_deleted_todos(client, auth_headers):
    """Test lấy danh sách đã xóa"""
    # Tạo và soft delete todo
    todo_data = {"title": "Deleted todo", "description": "In trash"}
    create_response = client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    todo_id = create_response.json()["id"]
    
    client.delete(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    
    # Lấy trash
    response = client.get("/api/v1/trash/todos", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    deleted_todos = response.json()
    assert todo_id in [todo["id"] for todo in deleted_todos]

def test_restore_todo(client, auth_headers):
    """Test khôi phục todo"""
    # Tạo và soft delete todo
    todo_data = {"title": "Todo to restore", "description": "Will be restored"}
    create_response = client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    todo_id = create_response.json()["id"]
    
    client.delete(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    
    # Restore
    response = client.post(f"/api/v1/trash/todos/{todo_id}/restore", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Kiểm tra todo đã quay lại active
    get_response = client.get("/api/v1/todos", headers=auth_headers)
    todos = get_response.json()["items"]
    assert todo_id in [todo["id"] for todo in todos]

def test_permanent_delete_todo(client, auth_headers):
    """Test xóa vĩnh viễn"""
    # Tạo và soft delete todo
    todo_data = {"title": "Todo to permanent delete", "description": "Will be gone forever"}
    create_response = client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    todo_id = create_response.json()["id"]
    
    client.delete(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    
    # Permanent delete
    response = client.delete(f"/api/v1/trash/todos/{todo_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Kiểm tra không còn ở đâu cả
    trash_response = client.get("/api/v1/trash/todos", headers=auth_headers)
    deleted_todos = trash_response.json()
    assert todo_id not in [todo["id"] for todo in deleted_todos]
