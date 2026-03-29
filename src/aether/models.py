from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Optional
from enum import Enum

class SensorStatus(str, Enum):
    """Enumeration of possible system health statuses."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"

class IngestRequest(BaseModel):
    """Request model for sensor data ingestion endpoint."""
    sensor_id: str = Field(..., min_length=1)
    readings: Dict[str, float]

class IngestResponse(BaseModel):
    """Response model for successful sensor data ingestion."""
    status: str
    message: str
    sensor_id: str = Field(..., min_length=1)
    timestamp: datetime

class StatusResponse(BaseModel):
    """Response model for system health status endpoint."""
    status: SensorStatus
    uptime_seconds: float
    active_sensors: int
    total_readings: int
    last_update: Optional[datetime]

class ErrorResponse(BaseModel):
    """Generic error response model for API error conditions."""
    status: str
    message: str
