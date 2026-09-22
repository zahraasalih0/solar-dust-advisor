from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go


CHART_TRANSITION = {"duration": 500, "easing": "cubic-in-out"}
DONUT_TRANSITION = {"duration": 800, "easing": "cubic-in-out"}


def _donut_figure(analysis):
    dust_loss = analysis["maximum_soiling_loss_percent"]
    return go.Figure(
        go.Pie(labels=["Dust loss", "Remaining potential"], values=[dust_loss, max(0, 100 - dust_loss)], hole=0.68, marker={"colors": ["#e36a4d", "#dce8ee"]}, textinfo="none", hovertemplate="%{label}: %{value:.1f}%<extra></extra>")
    ).update_layout(showlegend=True, legend={"orientation": "h", "y": -0.05}, margin={"t": 10, "b": 30, "l": 10, "r": 10}, height=260, transition=DONUT_TRANSITION)


def _soiling_gauge(analysis):
    return go.Figure(go.Indicator(
        mode="gauge+number",
        value=analysis["maximum_soiling_loss_percent"],
        number={"suffix": "%", "font": {"size": 34, "color": "#173042"}},
        title={"text": "Soiling index", "font": {"size": 15, "color": "#6a7f8e"}},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%"},
            "bar": {"color": "#173042", "thickness": 0.2},
            "steps": [
                {"range": [0, 15], "color": "#e6f5ef"},
                {"range": [15, 30], "color": "#fff4df"},
                {"range": [30, 100], "color": "#fff0ec"},
            ],
            "threshold": {"line": {"color": "#c95e45", "width": 4}, "thickness": 0.75, "value": analysis["maximum_soiling_loss_percent"]},
        },
    )).update_layout(margin={"t": 25, "b": 5, "l": 20, "r": 20}, height=235, paper_bgcolor="white", transition=CHART_TRANSITION)


def _forecast_figure(analysis):
    days = [f"Day {index}" for index in range(1, 15)]
    start = analysis["maximum_soiling_loss_percent"]
    values = [100 - start * (1 + index / 14) for index in range(14)]
    return go.Figure(go.Scatter(x=days, y=values, mode="lines+markers", line={"color": "#2f78a8", "width": 3}, marker={"size": 6, "color": "#2f78a8"}, hovertemplate="%{x}: %{y:.1f}% efficiency<extra></extra>")).update_layout(yaxis={"title": "Efficiency %", "range": [50, 102], "gridcolor": "#e5edf2"}, xaxis={"showgrid": False}, margin={"t": 10, "b": 35, "l": 45, "r": 10}, height=300, plot_bgcolor="white", paper_bgcolor="white", transition=CHART_TRANSITION)


def create_performance_analysis(analysis):
    return dcc.Loading(
        html.Section(
            [
                html.Div("Performance & forensics", className="section-kicker"),
                html.H2("See what is costing you", className="section-title"),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.H3("Root cause", className="panel-title"),
                                    html.P("Dust contribution to current loss", className="chart-subtitle"),
                                    dcc.Graph(id="root-cause-chart", figure=_donut_figure(analysis), config={"displayModeBar": False}),
                                ]),
                                className="analysis-panel chart-card",
                            ),
                            lg=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.H3("Soiling index", className="panel-title"),
                                    html.P("Maximum measured soiling loss", className="chart-subtitle"),
                                    dcc.Graph(id="soiling-gauge-chart", figure=_soiling_gauge(analysis), config={"displayModeBar": False}),
                                ]),
                                className="analysis-panel chart-card",
                            ),
                            lg=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.H3("14-day forecast", className="panel-title"),
                                    html.P("Projected efficiency trend", className="chart-subtitle"),
                                    dcc.Graph(id="forecast-chart", figure=_forecast_figure(analysis), config={"displayModeBar": False}),
                                ]),
                                className="analysis-panel chart-card",
                            ),
                            lg=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.H3("Cumulative loss", className="panel-title"),
                                    html.P("Projected over 14 days", className="chart-subtitle"),
                                    dcc.Graph(id="cumulative-loss-chart", config={"displayModeBar": False}),
                                ]),
                                className="analysis-panel chart-card",
                            ),
                            lg=6,
                            className="mb-3",
                        ),
                    ],
                    className="g-3",
                ),
            ], className="performance-section"
        ),
        type="dot",
        color="#2f78a8",
    )
