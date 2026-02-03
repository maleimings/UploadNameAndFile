# String Data API

A FastAPI application that accepts two string inputs and saves them in JSON format to a local file.

## Features

- Save two string values with automatic timestamp
- Store data in `data.json` file
- Retrieve all saved data
- Get specific data entry by ID
- Unique ID generation for each entry

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Save String Data
- **POST** `/save-data/`
- Accept JSON body with `string1` and `string2`
- Returns saved data with unique ID and timestamp

### Get All Data
- **GET** `/data/`
- Returns all saved string data entries

### Get Data by ID
- **GET** `/data/{entry_id}`
- Returns specific data entry by unique ID

### Root
- **GET** `/`
- Returns API status message

## Usage Examples

### Save string data:
```bash
curl -X POST "http://localhost:8000/save-data/" \
  -H "Content-Type: application/json" \
  -d '{"string1": "Hello", "string2": "World"}'
```

### Get all data:
```bash
curl "http://localhost:8000/data/"
```

### Get specific entry:
```bash
curl "http://localhost:8000/data/{entry_id}"
```

## Data Storage

Data is stored in `data.json` file with structure:
```json
[
  {
    "id": "unique-uuid",
    "string1": "first string",
    "string2": "second string", 
    "timestamp": "2024-01-01T12:00:00"
  }
]
```

## Testing

Run tests with:
```bash
pytest test_string_data.py -v
```

## Interactive API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
