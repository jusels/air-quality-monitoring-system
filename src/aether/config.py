from __future__ import annotations
from .persistence import read_json
from dataclasses import dataclass
import typing as tt
import pathlib
import json
import re

WKT_POINT_PATTERN = re.compile(
        r"POINT\s*\(\s*(?P<lon>-?\d+\.?\d*)\s+(?P<lat>-?\d+\.?\d*)\s*\)",
        re.IGNORECASE,
    )

def parse_wkt(wkt_string: str) -> tuple[float, float]:
    """Parse a WKT POINT string to extract latitude and longitude coordinates."""
    match = WKT_POINT_PATTERN.fullmatch(wkt_string)

    if not match:
        raise ValueError(f"Invalid WKT POINT: {wkt_string!r}")

    longitude = float(match.group("lon"))
    latitude = float(match.group("lat"))

    if not -180 <= longitude <= 180:
        raise ValueError(f"Longitude {longitude} out of valid range [-180, 180]")
    if not -90 <= latitude <= 90:
        raise ValueError(f"Latitude {latitude} out of valid range [-90, 90]")

    return latitude, longitude


def validate_file_path(fpath: tt.Union[str, pathlib.Path]) -> pathlib.Path:
    """Validate that the given path exists and is a file."""
    filepath = pathlib.Path(fpath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}.")
    if not filepath.is_file():
        raise ValueError(f"Path is not a file: {filepath}.")
    return filepath

@dataclass
class MapConfig:
    """Configuration for map visualization settings."""
    default_zoom: int
    map_style: str

@dataclass
class ThresholdsConfig:
    """Air quality threshold values for categorizing pollution levels."""
    pm25_safe: float
    pm25_moderate: float
    pm25_danger: float
    pm10_safe: float
    pm10_moderate: float
    pm10_danger: float

@dataclass
class AppConfig:
    """Main application configuration container."""
    storage_file: pathlib.Path
    historical_data_file: pathlib.Path
    host: str
    port: int
    thresholds: ThresholdsConfig
    map_config: MapConfig

    @staticmethod
    def load(file_path: str | pathlib.Path) -> AppConfig:
        """Load application configuration from a JSON file."""
        try:
            file_path = validate_file_path(file_path)
            raw = read_json(file_path)

            return AppConfig(
                storage_file=pathlib.Path(raw["storage_file"]),
                historical_data_file=validate_file_path(pathlib.Path(raw["historical_data_file"])),
                host=raw["host"],
                port=raw["port"],
                thresholds=ThresholdsConfig(**raw["thresholds"]),
                map_config=MapConfig(**raw["map_config"]),
            )
        except json.JSONDecodeError:
            raise ValueError(f"ERROR: Invalid JSON format in config file {file_path}")
        except KeyError as e:
            raise ValueError(f"Missing required configuration key: {e}")