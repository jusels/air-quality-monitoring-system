import pandas as pd
import logging
from typing import Dict, List, Tuple
from .config import ThresholdsConfig

logger = logging.getLogger(__name__)

class DataCleaner:
    @staticmethod
    def clean_readings_batch(df: pd.DataFrame) -> pd.DataFrame:
        """Basic cleaning of raw historical data"""
        if df.empty:
            return df

        rows_loaded = len(df)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', errors='coerce')
        df = df.dropna(subset=['sensor_id', 'timestamp'])

        pollutant_cols = ['pm25', 'pm10', 'no2', 'o3']
        existing_pollutants = [col for col in pollutant_cols if col in df.columns]
        if existing_pollutants:
            df = df[(df[existing_pollutants] >= 0).all(axis=1)]
        df = df[df['pm25'] < 500]

        rows_kept = len(df)
        rows_dropped = rows_loaded - rows_kept
        percent_cleaned = (rows_dropped / rows_loaded) * 100 if rows_loaded else 0
        logger.info(
            "Batch cleaning: %d → %d rows (%d dropped, %.1f%%)",
            rows_loaded, rows_kept, rows_dropped, percent_cleaned
        )
        return df.reset_index(drop=True)

    @staticmethod
    def validate_readings(readings: Dict[str, float]) -> Tuple[bool, List[str]]:
        """Validate incoming readings before ingestion"""
        errors = []
        if not readings:
            errors.append("Reading dictionary is empty")

        for key, value in readings.items():
            if not isinstance(value, (int, float)):
                errors.append(f"{key} must be a number")
            elif value < 0:
                errors.append(f"{key} must be non-negative")

        return len(errors) == 0, errors

    @staticmethod
    def filter_by_threshold(df: pd.DataFrame, thresholds: ThresholdsConfig) -> pd.DataFrame:
        """Filter rows exceeding danger thresholds for chart/analysis purposes"""
        return df[
            (df["pm25"] <= thresholds.pm25_danger) &
            (df["pm10"] <= thresholds.pm10_danger)
            ]

    @staticmethod
    def categorize_pm10(value: float, thresholds: ThresholdsConfig) -> str:
        """Categorize PM10 according to thresholds"""
        if value is None:
            return "No data"
        elif value <= thresholds.pm10_safe:
            return "Safe"
        elif value <= thresholds.pm10_moderate:
            return "Moderate"
        elif value <= thresholds.pm10_danger:
            return "Unhealthy"
        return "Dangerous"

    @staticmethod
    def categorize_pm25(value: float, thresholds: ThresholdsConfig) -> str:
        """Categorize PM2.5 according to thresholds"""
        if value is None:
            return "No data"
        elif value <= thresholds.pm25_safe:
            return "Safe"
        elif value <= thresholds.pm25_moderate:
            return "Moderate"
        elif value <= thresholds.pm25_danger:
            return "Unhealthy"
        return "Dangerous"

    @staticmethod
    def aggregate_by_sensor(df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate readings by sensor, computing mean per pollutant"""
        return df.groupby("sensor_id")[["pm25", "pm10", "no2", "o3"]].mean().reset_index()

    @staticmethod
    def calculate_statistics(df: pd.DataFrame) -> pd.DataFrame:
        """Compute statistics (mean, median, min, max, std) per pollutant"""
        stats = df[["pm25", "pm10", "no2", "o3"]].agg(['mean', 'median', 'min', 'max', 'std'])
        return stats.transpose()
