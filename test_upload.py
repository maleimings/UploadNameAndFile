import pytest
from fastapi.testclient import TestClient
from main import app
import os
import tempfile
import io

client = TestClient(app)

@pytest.fixture
def sample_file():
    """Create a temporary sample file for testing"""
    content = b"This is a test file content for upload testing."
    return io.BytesIO(content)

@pytest.fixture
def large_file():
    """Create a file larger than 5MB for testing size limit"""
    content = b"x" * (6 * 1024 * 1024)  # 6MB file
    return io.BytesIO(content)

def test_upload_file_success(sample_file):
    """Test successful file upload"""
    response = client.post(
        "/upload/",
        files={"file": ("test.txt", sample_file, "text/plain")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["original_filename"] == "test.txt"
    assert data["content_type"] == "text/plain"
    assert data["file_size"] > 0
    assert data["message"] == "File uploaded successfully"
    assert "upload_time" in data

def test_upload_file_size_limit_exceeded(large_file):
    """Test file upload with size exceeding 5MB limit"""
    response = client.post(
        "/upload/",
        files={"file": ("large_file.txt", large_file, "text/plain")}
    )
    
    assert response.status_code == 413
    assert "File size exceeds 5MB limit" in response.json()["detail"]

def test_upload_file_without_file():
    """Test upload endpoint without providing file"""
    response = client.post("/upload/")
    
    assert response.status_code == 422  # Validation error

def test_upload_empty_file():
    """Test upload with empty file"""
    empty_file = io.BytesIO(b"")
    response = client.post(
        "/upload/",
        files={"file": ("empty.txt", empty_file, "text/plain")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["file_size"] == 0

def test_upload_different_file_types():
    """Test upload with different file types"""
    test_cases = [
        ("image.jpg", b"\xff\xd8\xff\xe0", "image/jpeg"),
        ("document.pdf", b"%PDF-1.4", "application/pdf"),
        ("data.json", b'{"key": "value"}', "application/json"),
    ]
    
    for filename, content, content_type in test_cases:
        file_obj = io.BytesIO(content)
        response = client.post(
            "/upload/",
            files={"file": (filename, file_obj, content_type)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["original_filename"] == filename
        assert data["content_type"] == content_type

def test_list_files_empty():
    """Test listing files when database is empty"""
    # Note: This test might fail if other tests have already uploaded files
    response = client.get("/files/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_list_files_after_upload(sample_file):
    """Test listing files after uploading"""
    # Upload a file first
    upload_response = client.post(
        "/upload/",
        files={"file": ("list_test.txt", sample_file, "text/plain")}
    )
    assert upload_response.status_code == 200
    
    # List files
    response = client.get("/files/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Check if our uploaded file is in the list
    uploaded_files = [f for f in data if f["original_filename"] == "list_test.txt"]
    assert len(uploaded_files) > 0

def test_get_file_info_after_upload(sample_file):
    """Test getting specific file info after upload"""
    # Upload a file first
    upload_response = client.post(
        "/upload/",
        files={"file": ("info_test.txt", sample_file, "text/plain")}
    )
    assert upload_response.status_code == 200
    
    file_id = upload_response.json()["id"]
    
    # Get file info
    response = client.get(f"/files/{file_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == file_id
    assert data["original_filename"] == "info_test.txt"
    assert data["content_type"] == "text/plain"

def test_get_nonexistent_file_info():
    """Test getting info for non-existent file"""
    response = client.get("/files/99999")
    assert response.status_code == 404
    assert "File not found" in response.json()["detail"]

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "File Upload API is running"

def test_upload_with_unicode_filename():
    """Test upload with unicode characters in filename"""
    unicode_file = io.BytesIO(b"Unicode content")
    response = client.post(
        "/upload/",
        files={"file": ("测试文件.txt", unicode_file, "text/plain")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["original_filename"] == "测试文件.txt"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
