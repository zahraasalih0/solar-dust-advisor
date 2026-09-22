from dash import Input, Output
import plotly.graph_objects as go

from src.utils.calculations import (
    build_cumulative_loss,
    build_forecast,
    build_scenarios,
    build_weekly_losses,
    calculate_metrics,
)


CHART_TRANSITION = {"duration": 500, "easing": "cubic-in-out"}
DONUT_TRANSITION = {"duration": 800, "easing": "cubic-in-out"}


def _donut_figure(metrics):
    return go.Figure(go.Pie(labels=["Dust loss", "Remaining potential"], values=[metrics["dust_loss_pct"], max(0, 100 - metrics["dust_loss_pct"])], hole=0.68, marker={"colors": ["#e36a4d", "#dce8ee"]}, textinfo="none", hovertemplate="%{label}: %{value:.1f}%<extra></extra>")).update_layout(showlegend=True, legend={"orientation": "h", "y": -0.05}, margin={"t": 10, "b": 30, "l": 10, "r": 10}, height=260, transition=DONUT_TRANSITION)


def _forecast_figure(metrics):
    days = [f"Day {index}" for index in range(1, 15)]
    return go.Figure(go.Scatter(x=days, y=build_forecast(metrics), mode="lines+markers", line={"color": "#2f78a8", "width": 3}, marker={"size": 6, "color": "#2f78a8"}, hovertemplate="%{x}: %{y:.1f}% efficiency<extra></extra>")).update_layout(yaxis={"title": "Efficiency %", "range": [50, 102], "gridcolor": "#e5edf2"}, xaxis={"showgrid": False}, margin={"t": 10, "b": 35, "l": 45, "r": 10}, height=300, plot_bgcolor="white", paper_bgcolor="white", transition=CHART_TRANSITION)


def _soiling_gauge(metrics):
    return go.Figure(go.Indicator(
        mode="gauge+number",
        value=metrics["dust_loss_pct"],
        number={"suffix": "%", "font": {"size": 34, "color": "#173042"}},
        title={"text": "Soiling index", "font": {"size": 15, "color": "#6a7f8e"}},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%"},
            "bar": {"color": "#173042", "thickness": 0.2},
            "steps": [{"range": [0, 15], "color": "#e6f5ef"}, {"range": [15, 30], "color": "#fff4df"}, {"range": [30, 100], "color": "#fff0ec"}],
            "threshold": {"line": {"color": "#c95e45", "width": 4}, "thickness": 0.75, "value": metrics["dust_loss_pct"]},
        },
    )).update_layout(margin={"t": 25, "b": 5, "l": 20, "r": 20}, height=235, paper_bgcolor="white", transition=CHART_TRANSITION)


def _cumulative_loss_figure(metrics):
    days = [f"Day {index}" for index in range(1, 15)]
    return go.Figure(go.Scatter(x=days, y=build_cumulative_loss(metrics), mode="lines", fill="tozeroy", line={"color": "#c95e45", "width": 3}, fillgradient={"type": "horizontal", "colorscale": [[0, "rgba(255, 232, 176, 0.20)"], [1, "rgba(201, 94, 69, 0.42)"]]}, hovertemplate="%{x}: %{y:,.0f} IQD<extra></extra>")).update_layout(yaxis={"title": "Cumulative loss (IQD)", "gridcolor": "#e5edf2"}, xaxis={"showgrid": False}, margin={"t": 10, "b": 35, "l": 55, "r": 10}, height=260, plot_bgcolor="white", paper_bgcolor="white", transition=CHART_TRANSITION)


def _weekly_loss_figure(metrics):
    weeks = [f"Week {index}" for index in range(1, 5)]
    return go.Figure(go.Bar(x=weeks, y=build_weekly_losses(metrics), marker={"color": ["#f3d36a", "#f3b25b", "#e8894e", "#c95e45"]}, hovertemplate="%{x}: %{y:,.0f} IQD<extra></extra>")).update_layout(yaxis={"title": "Loss (IQD)", "gridcolor": "#e5edf2"}, xaxis={"showgrid": False}, margin={"t": 10, "b": 45, "l": 50, "r": 15}, height=260, plot_bgcolor="white", paper_bgcolor="white", transition=CHART_TRANSITION)


def _savings_comparison_figure(scenarios):
    return go.Figure(go.Bar(x=[scenarios["clean_revenue"], scenarios["ignore_revenue"]], y=["Clean Today", "Ignore 30 Days"], orientation="h", marker={"color": ["#248c69", "#c95e45"]}, text=[f"{scenarios['clean_revenue']:,.0f} IQD", f"{scenarios['ignore_revenue']:,.0f} IQD"], textposition="auto", hovertemplate="%{y}: %{x:,.0f} IQD<extra></extra>")).update_layout(xaxis={"title": "Expected net revenue (IQD)", "gridcolor": "#e5edf2"}, yaxis={"showgrid": False}, margin={"t": 10, "b": 45, "l": 115, "r": 20}, height=190, plot_bgcolor="white", paper_bgcolor="white", transition=CHART_TRANSITION)


def register_callbacks(app, analysis):
    @app.callback(
        Output("recommendation-value", "children"),
        Output("recommendation-value", "className"),
        Output("root-cause-chart", "figure"),
        Output("soiling-gauge-chart", "figure"),
        Output("forecast-chart", "figure"),
        Output("cumulative-loss-chart", "figure"),
        Output("savings-comparison-chart", "figure"),
        Output("weekly-loss-chart", "figure"),
        Output("scenario-clean-efficiency", "children"),
        Output("scenario-ignore-efficiency", "children"),
        Output("financial-metrics-store", "data"),
        Input("recalculate-button", "n_clicks"),
        Input("capacity-input", "value"),
        Input("tariff-slider", "value"),
        Input("cleaning-cost-input", "value"),
        prevent_initial_call=False,
    )
    def recalculate(_, capacity_kw, tariff, cleaning_cost):
        capacity_kw = float(capacity_kw or 0)
        tariff = float(tariff or 0)
        cleaning_cost = float(cleaning_cost or 0)
        metrics = calculate_metrics(capacity_kw, tariff, cleaning_cost, analysis)
        scenarios = build_scenarios(capacity_kw, tariff, cleaning_cost, analysis, metrics)
        recommendation_class = {
            "Clean Today": "card-value recommendation-positive",
            "Consider Cleaning": "card-value recommendation-caution",
            "Do Not Clean": "card-value recommendation-negative",
        }[metrics["recommendation"]]
        return (
            metrics["recommendation"], recommendation_class,
            _donut_figure(metrics), _soiling_gauge(metrics), _forecast_figure(metrics), _cumulative_loss_figure(metrics), _savings_comparison_figure(scenarios), _weekly_loss_figure(metrics),
            scenarios["clean_efficiency"], scenarios["ignore_efficiency"],
            {
                "recommendation": metrics["recommendation"],
                "payback": f"{metrics['payback_days']:.1f} days",
                "loss": f"{metrics['daily_financial_loss_iqd']:,.0f} IQD / {metrics['weekly_loss_iqd']:,.0f} IQD",
                "clean_revenue": f"{scenarios['clean_revenue']:,.0f} IQD",
                "ignore_revenue": f"{scenarios['ignore_revenue']:,.0f} IQD",
            },
        )
