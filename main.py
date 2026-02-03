from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
import os
from datetime import datetime
import uuid

app = FastAPI(title="String Data API", description="API to save string data in JSON format")

# Pydantic model for input data
class StringData(BaseModel):
    string1: str
    string2: str

# Data storage file
DATA_FILE = "data.json"

# Initialize data file if it doesn't exist
def initialize_data_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)

# Read existing data
def read_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Write data to file
def write_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)

# Initialize on startup
initialize_data_file()

@app.get("/")
async def root():
    return {"message": "String Data API is running"}

@app.post("/save-data/")
async def save_string_data(data: StringData):
    """Save two string values to JSON file"""
    try:
        # Read existing data
        existing_data = read_data()
        
        # Create new entry
        new_entry = {
            "id": str(uuid.uuid4()),
            "string1": data.string1,
            "string2": data.string2,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add new entry to existing data
        existing_data.append(new_entry)
        
        # Write back to file
        write_data(existing_data)
        
        return {
            "id": new_entry["id"],
            "string1": data.string1,
            "string2": data.string2,
            "timestamp": new_entry["timestamp"],
            "message": "Data saved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save data: {str(e)}")

@app.get("/data/")
async def get_all_data():
    """Get all saved string data"""
    try:
        data = read_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read data: {str(e)}")

@app.get("/data/{entry_id}")
async def get_data_by_id(entry_id: str):
    """Get specific data entry by ID"""
    try:
        data = read_data()
        entry = next((item for item in data if item["id"] == entry_id), None)
        
        if not entry:
            raise HTTPException(status_code=404, detail="Data entry not found")
        
        return entry
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
