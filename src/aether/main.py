from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi import status as http_status
from starlette.responses import HTMLResponse
from .map_visualization import MapVisualizer
from .temporal_visualization import TemporalVisualizer
from .dependencies import get_sensor_manager, get_visualizer, get_temporal_visualizer, init_dependencies
from .sensor_manager import SensorManager, UnauthorizedSensorError, InvalidReadingError
from .models import StatusResponse, IngestResponse, IngestRequest
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pathlib import Path
import logging

app = FastAPI()

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors and return consistent JSON format."""
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "details": exc.errors()}
    )

@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle HTTP exceptions and return consistent JSON error format."""
    return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail}
        )

init_dependencies()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@app.get('/', response_class=HTMLResponse)
def welcome() -> HTMLResponse:
    """Return the welcome page with API documentation and navigation links."""
    html_file = Path(__file__).parent / "templates" / "welcome.html"
    html_content = html_file.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)

@app.post('/ingest', response_model=IngestResponse)
def ingest(request: IngestRequest, manager: Annotated[SensorManager, Depends(get_sensor_manager)]) -> IngestResponse:
    """Ingest sensor readings from IoT devices. Validates sensor authorization and reading format before storing. Returns success response with timestamp if ingestion succeeds."""
    try:
        reading = manager.ingest(request.sensor_id, request.readings)
        return IngestResponse(
            status="success",
            message="Reading ingested successfully",
            sensor_id=reading.sensor_id,
            timestamp=reading.timestamp
        )
    except UnauthorizedSensorError:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized sensor"
        )
    except InvalidReadingError as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/map", response_class=HTMLResponse, response_model=None)
def map_view(manager: Annotated[SensorManager, Depends(get_sensor_manager)], visualizer: Annotated[MapVisualizer, Depends(get_visualizer)]) -> HTMLResponse:
    """Display interactive map with real-time sensor data."""
    try:
        df = manager.get_map_data()
        fig = visualizer.create_map(df)
        return HTMLResponse(content=fig.to_html(include_plotlyjs='cdn', full_html=True))
    except Exception as e:
        logger.error(f"Error generating map: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate map visualization")

@app.get('/status', response_model=StatusResponse)
def status(manager: Annotated[SensorManager, Depends(get_sensor_manager)]) -> StatusResponse:
    """Return system health and statistics including sensor status and reading counts."""
    return manager.get_status()

@app.get('/history/{sensor_id}', response_class=HTMLResponse)
def history(sensor_id: str, manager: Annotated[SensorManager, Depends(get_sensor_manager)], temp_visualizer: Annotated[TemporalVisualizer, Depends(get_temporal_visualizer)]) -> HTMLResponse:
    """Display time series chart for a specific sensor."""
    df = manager.get_sensor_data(sensor_id)

    if df is None:
        raise HTTPException(status_code=404, detail="Sensor not found or no historical data")

    fig = temp_visualizer.create_time_series(sensor_id, df)
    return HTMLResponse(content=fig.to_html(full_html=True))

@app.get('/distribution/{year}/{month}', response_class=HTMLResponse)
def distribution(year: int, month: int, manager: Annotated[SensorManager, Depends(get_sensor_manager)], temp_visualizer: Annotated[TemporalVisualizer, Depends(get_temporal_visualizer)]) -> HTMLResponse:
    """Display PM2.5 distribution by province for a specific month."""
    if not 1 <= month <= 12:
        raise HTTPException(status_code=400, detail="Invalid month (1–12 required)")

    df = manager.get_distribution_data()
    if df is None:
        raise HTTPException(status_code=404, detail="No historical data")

    try:
        fig = temp_visualizer.create_distribution_chart(df, year, month)
        if fig is None:
            raise HTTPException(status_code=404, detail="No data for selected period")

        return HTMLResponse(content=fig.to_html(full_html=True))
    except Exception as e:
        logger.error(f"Error generating distribution chart for {year}/{month}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate distribution visualization")
