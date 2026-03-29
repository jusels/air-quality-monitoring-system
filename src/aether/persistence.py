import json
import pathlib
import pandas as pd
from .sensor import SensorReading

def read_json(file_path: pathlib.Path) -> dict | list:
    """Read and parse a JSON file."""
    try:
        with file_path.open("rt", encoding='utf-8') as fd:
            raw_data = json.load(fd)
        return raw_data
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in {file_path}: {e}")
    except OSError as e:
        raise RuntimeError(f"Error reading config file {file_path}: {e}")

def read_csv(file_path: pathlib.Path) -> pd.DataFrame:
    """Read and parse a CSV file into a pandas DataFrame."""
    try:
        df = pd.read_csv(file_path)
        return df
    except pd.errors.EmptyDataError:
        raise RuntimeError(f"CSV file is empty: {file_path}")
    except pd.errors.ParserError as e:
        raise RuntimeError(f"Malformed CSV in {file_path}: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to read CSV {file_path}: {e}")

def append_reading(path: pathlib.Path, reading: SensorReading) -> None:
    """Append a sensor reading to a JSON file."""
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(reading.to_dict()) + "\n")
    except OSError as e:
        raise RuntimeError(f"ERROR: Error writing into storage file {path}: {e}")




