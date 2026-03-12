import pytest
from fastapi import status

def test_create_tag_success(client, auth_headers):
    """Test tạo tag thành công"""
    tag_data = {
        "name": "work",
        "color": "#FF0000"
    }
    response = client.post("/api/v1/tags", json=tag_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == tag_data["name"]
    assert data["color"] == tag_data["color"]
    assert "id" in data

def test_create_duplicate_tag(client, auth_headers):
    """Test tạo tag trùng tên"""
    tag_data = {
        "name": "duplicate",
        "color": "#00FF00"
    }
    
    # Tạo lần đầu
    client.post("/api/v1/tags", json=tag_data, headers=auth_headers)
    
    # Tạo lần 2 - nên fail
    response = client.post("/api/v1/tags", json=tag_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()

def test_get_tags_success(client, auth_headers):
    """Test lấy danh sách tags"""
    # Tạo vài tags
    tags = [
        {"name": "work", "color": "#FF0000"},
        {"name": "personal", "color": "#00FF00"}
    ]
    for tag in tags:
        client.post("/api/v1/tags", json=tag, headers=auth_headers)
    
    # Lấy danh sách
    response = client.get("/api/v1/tags", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
