from datetime import datetime
from typing import Any, Optional

class SensorReading:
    def __init__(self, sensor_id: str, readings: dict[str, float], timestamp: datetime) -> None:
        self.sensor_id = sensor_id
        self.readings = readings
        self.timestamp = timestamp

    def to_dict(self) -> dict[str, Any]:
        return {
            "sensor_id": self.sensor_id,
            "readings": self.readings,
            "timestamp": self.timestamp.isoformat(),
        }

class SensorInfo:
    def __init__(self, sensor_id: str, location: tuple[float, float], metadata: dict[str, Any], last_reading: Optional[SensorReading] = None, last_update: Optional[datetime] = None) -> None:
        self.sensor_id = sensor_id
        self.location = location
        self.latitude = location[0]
        self.longitude = location[1]
        self.metadata = metadata
        self.last_reading = last_reading
        self.last_update = last_update
