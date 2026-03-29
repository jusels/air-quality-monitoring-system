import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
import pandas as pd
import numpy as np
from datetime import datetime
from src.aether.main import app
from src.aether.dependencies import get_sensor_manager, get_visualizer, get_temporal_visualizer

mock_manager = Mock()
mock_map_viz = Mock()
mock_temp_viz = Mock()

def get_test_manager():
    return mock_manager

def get_test_map_viz():
    return mock_map_viz

def get_test_temp_viz():
    return mock_temp_viz

app.dependency_overrides[get_sensor_manager] = get_test_manager
app.dependency_overrides[get_visualizer] = get_test_map_viz
app.dependency_overrides[get_temporal_visualizer] = get_test_temp_viz

@pytest.fixture
def client():
    """Reset mocks for each test."""
    mock_manager.reset_mock()
    mock_map_viz.reset_mock()
    mock_temp_viz.reset_mock()

    with TestClient(app) as test_client:
        yield test_client


def create_test_df():
    """Create a real DataFrame for testing."""
    return pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=10, freq='H'),
        'pm25': np.random.uniform(20, 60, 10),
        'pm10': np.random.uniform(30, 80, 10),
        'no2': np.random.uniform(10, 40, 10),
        'o3': np.random.uniform(30, 70, 10)
    })


class MockPlotlyFigure:
    def to_html(self, full_html=True, include_plotlyjs='cdn'):
        return f"<html><body>Mock Plotly Figure</body></html>"

def test_welcome_page(client):
    """Test GET / returns HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_status_endpoint(client):
    """Test GET /status."""
    mock_manager.get_status.return_value = {
        "status": "healthy",
        "uptime_seconds": 100.0,
        "active_sensors": 5,
        "total_readings": 50,
        "last_update": datetime.now()
    }

    response = client.get("/status")
    assert response.status_code == 200


def test_ingest_valid(client):
    """Test POST /ingest."""
    from sensor import SensorReading

    test_reading = SensorReading(
        sensor_id="sensor_amsterdam_001",
        readings={"pm25": 25.5},
        timestamp=datetime.now()
    )
    mock_manager.ingest.return_value = test_reading

    response = client.post("/ingest", json={
        "sensor_id": "sensor_amsterdam_001",
        "readings": {"pm25": 25.5}
    })

    assert response.status_code == 200


def test_map_endpoint(client):
    """Test GET /map."""
    map_df = pd.DataFrame({
        "sensor_id": ["sensor_amsterdam_001", "sensor_rotterdam_001"],
        "lat": [52.3676, 51.9244],
        "lon": [4.9041, 4.4777],
        "pm25": [25.5, 45.7],
        "province": ["North Holland", "South Holland"],
        "category": ["Safe", "Moderate"]
    })

    mock_manager.get_map_data.return_value = map_df
    mock_map_viz.create_map.return_value = MockPlotlyFigure()

    response = client.get("/map")
    assert response.status_code == 200


def test_history_endpoint_valid(client):
    """Test GET /history/{sensor_id}."""
    history_df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=5, freq="h"),
        "pm25": [25.5, 26.1, 24.8, 27.3, 25.9],
        "pm10": [40.1, 41.2, 39.8, 42.5, 40.7],
        "no2": [12.3, 13.1, 11.8, 14.2, 12.9],
        "o3": [45.6, 44.8, 46.2, 43.7, 45.1]
    })

    mock_manager._sensors_whitelist = {"sensor_amsterdam_001": Mock()}
    mock_manager.get_sensor_data.return_value = history_df
    mock_temp_viz.create_time_series.return_value = MockPlotlyFigure()

    response = client.get("/history/sensor_amsterdam_001")
    assert response.status_code == 200


def test_distribution_endpoint_valid(client):
    """Test GET /distribution/{year}/{month}."""
    distribution_df = pd.DataFrame({
        "sensor_id": ["sensor_amsterdam_001", "sensor_rotterdam_001", "sensor_amsterdam_001"],
        "timestamp": pd.to_datetime(["2024-01-01 12:00:00", "2024-01-01 12:00:00", "2024-01-02 12:00:00"]),
        "pm25": [25.5, 45.7, 28.3],
        "pm10": [40.1, 60.8, 42.5],
        "no2": [12.3, 25.4, 13.8],
        "o3": [45.6, 38.9, 44.2],
        "province": ["North Holland", "South Holland", "North Holland"]  # Added province
    })

    mock_manager.get_distribution_data.return_value = distribution_df
    mock_temp_viz.create_distribution_chart.return_value = MockPlotlyFigure()

    response = client.get("/distribution/2024/1")
    assert response.status_code == 200


def test_docs_endpoint(client):
    """Test GET /docs."""
    response = client.get("/docs")
    assert response.status_code in [200, 307]