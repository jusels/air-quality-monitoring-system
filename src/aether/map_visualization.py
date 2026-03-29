import pandas as pd
from .config import MapConfig
import plotly.express as px
import plotly.graph_objects as go

class MapVisualizer:
    def __init__(self, map_config: MapConfig) -> None:
        self._map_config = map_config
        self._color_map = {
            "Safe": "green",
            "Moderate": "yellow",
            "Unhealthy": "orange",
            "Dangerous": "red",
            "No data": "gray"
        }

    def create_map(self, df: pd.DataFrame) -> go.Figure:
        fig = px.scatter_mapbox(
            df,
            lat="lat",
            lon="lon",
            color="category",
            color_discrete_map=self._color_map,
            hover_name="sensor_id",
            hover_data={"pm25": True, "province": True, "lat": False, "lon": False, "category": False},
            zoom=self._map_config.default_zoom,
            height=600
        )

        fig.update_layout(mapbox_style=self._map_config.map_style)
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

        return fig