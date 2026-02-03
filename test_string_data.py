import pytest
from fastapi.testclient import TestClient
from main import app
import json
import os

client = TestClient(app)

@pytest.fixture
def cleanup_data_file():
    """Clean up data file before and after tests"""
    if os.path.exists("data.json"):
        os.remove("data.json")
    yield
    if os.path.exists("data.json"):
        os.remove("data.json")

def test_save_string_data_success(cleanup_data_file):
    """Test successful saving of string data"""
    test_data = {
        "string1": "Hello World",
        "string2": "FastAPI Test"
    }
    
    response = client.post("/save-data/", json=test_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["string1"] == "Hello World"
    assert data["string2"] == "FastAPI Test"
    assert "timestamp" in data
    assert data["message"] == "Data saved successfully"

def test_save_string_data_empty_strings(cleanup_data_file):
    """Test saving empty strings"""
    test_data = {
        "string1": "",
        "string2": ""
    }
    
    response = client.post("/save-data/", json=test_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["string1"] == ""
    assert data["string2"] == ""

def test_save_string_data_special_characters(cleanup_data_file):
    """Test saving strings with special characters"""
    test_data = {
        "string1": "Hello! @#$%^&*()",
        "string2": "Unicode: ñáéíóú 🚀"
    }
    
    response = client.post("/save-data/", json=test_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["string1"] == "Hello! @#$%^&*()"
    assert data["string2"] == "Unicode: ñáéíóú 🚀"

def test_save_string_data_long_strings(cleanup_data_file):
    """Test saving long strings"""
    test_data = {
        "string1": "A" * 1000,
        "string2": "B" * 1000
    }
    
    response = client.post("/save-data/", json=test_data)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["string1"]) == 1000
    assert len(data["string2"]) == 1000

def test_save_string_data_missing_fields():
    """Test saving data with missing fields"""
    test_data = {
        "string1": "Only one string"
    }
    
    response = client.post("/save-data/", json=test_data)
    
    assert response.status_code == 422  # Validation error

def test_save_string_data_invalid_json():
    """Test saving invalid JSON data"""
    response = client.post("/save-data/", data="invalid json")
    
    assert response.status_code == 422  # Validation error

def test_get_all_data_empty(cleanup_data_file):
    """Test getting all data when file is empty"""
    response = client.get("/data/")
    
    assert response.status_code == 200
    data = response.json()
    assert data == []

def test_get_all_data_with_entries(cleanup_data_file):
    """Test getting all data after saving entries"""
    # Save first entry
    test_data1 = {"string1": "First", "string2": "Entry"}
    client.post("/save-data/", json=test_data1)
    
    # Save second entry
    test_data2 = {"string1": "Second", "string2": "Entry"}
    client.post("/save-data/", json=test_data2)
    
    # Get all data
    response = client.get("/data/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["string1"] == "First"
    assert data[1]["string1"] == "Second"

def test_get_data_by_id_success(cleanup_data_file):
    """Test getting specific data entry by ID"""
    # Save data
    test_data = {"string1": "Test", "string2": "ID"}
    save_response = client.post("/save-data/", json=test_data)
    entry_id = save_response.json()["id"]
    
    # Get by ID
    response = client.get(f"/data/{entry_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == entry_id
    assert data["string1"] == "Test"
    assert data["string2"] == "ID"

def test_get_data_by_id_not_found(cleanup_data_file):
    """Test getting non-existent data entry"""
    fake_id = "non-existent-id"
    response = client.get(f"/data/{fake_id}")
    
    assert response.status_code == 404
    assert "Data entry not found" in response.json()["detail"]

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "String Data API is running"

def test_data_persistence(cleanup_data_file):
    """Test that data persists between requests"""
    # Save data
    test_data = {"string1": "Persistent", "string2": "Data"}
    save_response = client.post("/save-data/", json=test_data)
    entry_id = save_response.json()["id"]
    
    # Get all data
    all_response = client.get("/data/")
    assert len(all_response.json()) == 1
    
    # Get by ID
    id_response = client.get(f"/data/{entry_id}")
    assert id_response.json()["string1"] == "Persistent"

def test_multiple_entries_unique_ids(cleanup_data_file):
    """Test that multiple entries have unique IDs"""
    entries = []
    
    # Save multiple entries
    for i in range(5):
        test_data = {"string1": f"Entry {i}", "string2": f"Value {i}"}
        response = client.post("/save-data/", json=test_data)
        entries.append(response.json()["id"])
    
    # Verify all IDs are unique
    assert len(set(entries)) == 5
    
    # Verify all entries are retrievable
    for entry_id in entries:
        response = client.get(f"/data/{entry_id}")
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
