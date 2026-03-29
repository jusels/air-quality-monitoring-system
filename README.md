# Project Aether - Air Quality Monitoring System

## Overview
Real-time and historical air quality monitoring with data ingestion, visualization, and analytics.

## Installation
```bash
# Clone the repository
git clone <repository-url>
cd Endterm_Project

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn src.aether.main:app --reload

# Or use the startup script (Windows PowerShell):
.\run.ps1
```

## Usage
Start the FastAPI server:
```bash
uvicorn src.aether.main:app --reload --host 0.0.0.0 --port 8000
```

Access the application at:
```
http://127.0.0.1:8000
```

### Quick Links
- **Welcome Page**: http://127.0.0.1:8000/
- **Interactive API Docs**: http://127.0.0.1:8000/docs
- **Real-time Map**: http://127.0.0.1:8000/map
- **System Status**: http://127.0.0.1:8000/status

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome page with API documentation |
| `/ingest` | POST | Submit sensor readings (JSON payload) |
| `/map` | GET | Interactive sensor map visualization |
| `/status` | GET | System health and statistics |
| `/history/{sensor_id}` | GET | Time series chart for specific sensor |
| `/distribution/{year}/{month}` | GET | Province distribution for given period |
| `/docs` | GET | Auto-generated Swagger UI documentation |

### Example Requests

**Submit Sensor Reading:**
```bash
curl -X POST "http://127.0.0.1:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "sensor_amsterdam_001",
    "readings": {
      "pm25": 25.5,
      "pm10": 40.1,
      "no2": 12.3,
      "o3": 45.6
    }
  }'
```

**Get Sensor History:**
```bash
curl "http://127.0.0.1:8000/history/sensor_amsterdam_001"
```

**Get Monthly Distribution:**
```bash
curl "http://127.0.0.1:8000/distribution/2024/1"
```

## Architecture

### File Structure
```
Endterm_Project/
├── config/                       # Configuration files
│   ├── sensors.json              # Authorized sensor list with WKT locations
│   └── server_config.json        # Application settings & thresholds
├── data/                         # Data storage
│   ├── historical_readings.csv   # Historical sensor data (1 year hourly)
│   └── readings.json             # Real-time ingested readings
├── src/                          # Source code
│   └── aether/                   # Main application package
│       ├── templates/            # HTML templates
│       │   └── welcome.html      # Welcome page HTML
│       ├── config.py             # Configuration parsing & WKT regex
│       ├── data_cleaning.py      # Pandas data processing & validation
│       ├── dependencies.py       # Dependency injection setup
│       ├── main.py               # FastAPI app & all 7 endpoints
│       ├── map_visualization.py  # Interactive Plotly map
│       ├── models.py             # Pydantic DTOs for API validation
│       ├── persistence.py        # File I/O (JSON/CSV read/write)
│       ├── sensor.py             # Domain models (SensorReading, SensorInfo)
│       ├── sensor_manager.py     # Business logic & sensor management
│       └── temporal_visualization.py # Time series & distribution charts
├── tests/                        # Test files
│   └── test_main.py              # FastAPI TestClient tests
├── requirements.txt              # Python dependencies
├── run.ps1                       # PowerShell startup script
└── README.md                     # Project documentation
```

### Layer Architecture
1. **API Layer** (`main.py`): FastAPI routes, HTTP handling, dependency injection
2. **Service Layer** (`sensor_manager.py`): Business logic, sensor authorization, data orchestration
3. **Data Layer** (`persistence.py`, `data_cleaning.py`): File storage, data cleaning with pandas
4. **Domain Layer** (`sensor.py`): Pure business entities (no validation)
5. **DTO Layer** (`models.py`): Pydantic validation for API boundaries
6. **Visualization Layer** (`map_visualization.py`, `temporal_visualization.py`): Plotly charts & maps
7. **Configuration Layer** (`config.py`): WKT parsing, config loading
8. **Dependency Layer** (`dependencies.py`): Service initialization & injection


## Testing

```bash
# Run the test file
pytest tests/
```

### Test Coverage
- All 7 API endpoints
- Basic HTTP status codes (200, 404)
- Integration with FastAPI TestClient

## Author
**Iuliia Lapan**  
Python Course - End-Term Assignment
December 2025