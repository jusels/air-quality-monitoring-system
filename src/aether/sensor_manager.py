import pandas as pd
import typing as tt
from .sensor import SensorInfo, SensorReading
from .data_cleaning import DataCleaner
from datetime import datetime
from .persistence import read_json, read_csv, append_reading
from .config import AppConfig, parse_wkt, MapConfig
import logging
import pathlib
from .models import SensorStatus

class UnauthorizedSensorError(Exception):
    """Exception raised when sensor id is not valid"""
    pass

class InvalidReadingError(Exception):
    """Exception raised when sensor readings fail validation check"""
    pass

logger = logging.getLogger(__name__)

class SensorManager:
    """Manages sensor data ingestion, storage, and retrieval for the air quality monitoring system."""

    def __init__(self, sensors_config: pathlib.Path, server_config: AppConfig) -> None:
        """Initialize the SensorManager with configuration files."""
        self._sensors_path = sensors_config
        self._historical_path = server_config.historical_data_file
        self._readings_path = server_config.storage_file

        self._thresholds = server_config.thresholds
        self._historical_df = None
        self._latest_data = {}

        self._startup_time = datetime.now()
        self._sensors_whitelist = {}

        self._active_sensors = 0
        self._total_readings = 0
        self._last_update: tt.Optional[datetime] = None

        self._sensors_df = None

        self._load_sensors_config()
        self._load_historical_readings()


    def _load_historical_readings(self) -> None:
        """Load and clean historical sensor data from CSV file."""
        self._historical_df = read_csv(self._historical_path)
        self._historical_df = DataCleaner.clean_readings_batch(self._historical_df)


    def _load_sensors_config(self) -> None:
        """Load sensor configuration from JSON file and parse WKT location strings."""
        raw_sensors_list = read_json(self._sensors_path)
        invalid_sensors = 0
        for sensor_data in raw_sensors_list:
            try:
                coord = parse_wkt(sensor_data["location"])
            except ValueError as e:
                invalid_sensors += 1
                continue
            sensor = SensorInfo (
                sensor_id=sensor_data["id"],
                location=coord,
                metadata=sensor_data["metadata"]
            )
            self._sensors_whitelist[sensor.sensor_id] = sensor
        if invalid_sensors > 0:
            logger.warning(f"Skipped {invalid_sensors} sensors with invalid WKT")

    def ingest(self, sensor_id: str, readings: dict[str, float]) -> SensorReading:
        """Ingest sensor readings after validation."""
        if sensor_id not in self._sensors_whitelist:
            raise UnauthorizedSensorError("Sensor is not authorized")

        valid, errors = DataCleaner.validate_readings(readings)
        if not valid:
            raise InvalidReadingError("; ".join(errors))

        reading = SensorReading(
            sensor_id=sensor_id,
            readings=readings,
            timestamp=datetime.now()
        )

        append_reading(self._readings_path, reading)

        sensor = self._sensors_whitelist[sensor_id]
        sensor.last_reading = reading
        sensor.last_update = reading.timestamp

        self._latest_data[sensor_id] = reading
        self._active_sensors = len(self._latest_data)
        self._total_readings += 1
        self._last_update = reading.timestamp

        return reading


    def get_status(self) -> dict:
        """Get system health and statistics."""
        status_enum = SensorStatus.HEALTHY if self._active_sensors > 0 else SensorStatus.DEGRADED

        return {
            "status": status_enum,
            "uptime_seconds": (datetime.now() - self._startup_time).total_seconds(),
            "active_sensors": self._active_sensors,
            "total_readings": self._total_readings,
            "last_update": self._last_update
        }

    def get_sensor_data(self, sensor_id: str) -> pd.DataFrame | None:
        """Get historical data for a specific sensor."""
        if sensor_id not in self._sensors_whitelist:
            return None
        df = self._historical_df[self._historical_df["sensor_id"] == sensor_id]
        return df if not df.empty else None

    def get_distribution_data(self) -> pd.DataFrame | None:
        """Get dataframe for distribution analysis."""
        provinces = {
            sensor_id: info.metadata["province"]
            for sensor_id, info in self._sensors_whitelist.items()
        }

        distribution_df = self._historical_df.copy()

        distribution_df.insert(
            0,
            "province",
            distribution_df["sensor_id"].map(provinces)
        )
        return distribution_df

    def get_map_data(self) -> pd.DataFrame:
        """Get current sensor data formatted for map visualization."""
        data = []
        for sensor_id, sensor in self._sensors_whitelist.items():
            pm25_value = None
            if sensor.last_reading:
                pm25_value = sensor.last_reading.readings.get("pm25")


            data.append({
                "sensor_id": sensor_id,
                "lat": sensor.latitude,
                "lon": sensor.longitude,
                "pm25": pm25_value,
                "province": sensor.metadata.get("province", ""),
                "category": DataCleaner.categorize_pm25(pm25_value, self._thresholds)
            })
        return pd.DataFrame(data)