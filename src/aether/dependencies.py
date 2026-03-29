from typing import Optional
from .sensor_manager import SensorManager
from .map_visualization import MapVisualizer
from .temporal_visualization import TemporalVisualizer
from . import config
import pathlib
import logging

logger = logging.getLogger(__name__)

_sensor_manager: Optional[SensorManager] = None
_map_visualizer: Optional[MapVisualizer] = None
_temporal_visualizer: Optional[TemporalVisualizer] = None

def init_dependencies() -> None:
    """Initialize all services synchronously. Called once at application startup."""
    global _sensor_manager, _map_visualizer, _temporal_visualizer
    try:
        project_root = pathlib.Path(__file__).parent.parent.parent
        sensors_path = project_root / "config" / "sensors.json"
        server_config_path = project_root /"config"/"server_config.json"

        config.validate_file_path(sensors_path)
        config.validate_file_path(server_config_path)

        server_config = config.AppConfig.load(server_config_path)

        _sensor_manager = SensorManager(sensors_path, server_config)
        _map_visualizer = MapVisualizer(server_config.map_config)
        _temporal_visualizer = TemporalVisualizer(server_config.thresholds)

        logger.info("Dependencies initialized")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

def get_sensor_manager() -> SensorManager:
    """Dependency provider for SensorManager."""
    if _sensor_manager is None:
        raise RuntimeError("Not initialized")
    return _sensor_manager

def get_visualizer() -> MapVisualizer:
    """Dependency provider for MapVisualizer."""
    if _map_visualizer is None:
        raise RuntimeError("MapVisualizer not initialized")
    return _map_visualizer

def get_temporal_visualizer() -> TemporalVisualizer:
    """Dependency provider for TemporalVisualizer."""
    if _temporal_visualizer is None:
        raise RuntimeError("TemporalVisualizer not initialized")
    return _temporal_visualizer

