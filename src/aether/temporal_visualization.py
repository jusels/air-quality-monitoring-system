import pandas as pd
import plotly.graph_objects as go
from .data_cleaning import DataCleaner
from .config import ThresholdsConfig

class TemporalVisualizer:
    def __init__(self, thresholds: ThresholdsConfig) -> None:
        self._thresholds = thresholds

    def create_time_series(self, sensor_id: str, df: pd.DataFrame) -> go.Figure:
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["pm25"],
            mode="lines",
            name="PM2.5",
            line=dict(color="red"),
        ))

        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["pm10"],
            mode="lines",
            name="PM1.0",
            line=dict(color="yellow"),
        ))

        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["no2"],
            mode="lines",
            name="NO2",
            line=dict(color="green"),
        ))

        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["o3"],
            mode="lines",
            name="O3",
            line=dict(color="blue"),
        ))

        fig.update_layout(
            plot_bgcolor="white",
            title=f"Time Series Chart for {sensor_id}",
            xaxis_title="Time",
            yaxis_title="Concentration",
            hovermode="x unified",
            xaxis=dict(
                showgrid=True,
                gridwidth=0.5,
                gridcolor="lightgray",
                rangeslider=dict(visible=True)
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=0.5,
                gridcolor="lightgray"
            ),
            legend=dict(orientation="h", y=-0.25),
        )
        return fig

    def create_distribution_chart(self, df: pd.DataFrame, year: int,month: int) -> go.Figure | None:
        filtered_df = df[
            (df["timestamp"].dt.year == year) &
            (df["timestamp"].dt.month == month)
        ]

        fig = go.Figure()

        if filtered_df.empty:
            return None

        filtered_df = filtered_df.copy()
        filtered_df["category"] = filtered_df["pm25"].apply(
            lambda v: DataCleaner.categorize_pm25(v, self._thresholds)
        )
        grouped = (
            filtered_df
            .groupby(["province", "category"])
            .size()
            .unstack(fill_value=0)
        )

        categories = ["Safe", "Moderate", "Unhealthy", "Dangerous"]
        colors = {
            "Safe": "green",
            "Moderate": "yellow",
            "Unhealthy": "orange",
            "Dangerous": "red",
        }

        percentages = grouped.div(grouped.sum(axis=1), axis=0) * 100

        for cat in categories:
            if cat not in percentages:
                continue

            fig.add_bar(
                name=cat,
                x=percentages.index,
                y=percentages[cat],
                marker_color=colors[cat],
                text=percentages[cat].round(1).astype(str) + "%",
                textposition="inside",
            )

        fig.update_layout(
            title=f"PM2.5 Distribution by Province ({month:02d}/{year})",
            xaxis_title="Province",
            yaxis_title="Percentage (%)",
            yaxis=dict(range=[0, 100], ticksuffix="%"),
            barmode="stack",
            barnorm="percent",
            hovermode="x unified",
            plot_bgcolor="white",
            legend_title="PM2.5 Category",
        )

        return fig
