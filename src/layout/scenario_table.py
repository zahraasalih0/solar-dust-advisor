from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go


CHART_TRANSITION = {"duration": 500, "easing": "cubic-in-out"}


def _savings_comparison_figure():
    return go.Figure(go.Bar(
        x=[0, 0],
        y=["Clean Today", "Ignore 30 Days"],
        orientation="h",
        marker={"color": ["#248c69", "#c95e45"]},
        text=["-- IQD", "-- IQD"],
        textposition="auto",
    )).update_layout(xaxis={"title": "Expected net revenue (IQD)", "gridcolor": "#e5edf2"}, yaxis={"showgrid": False}, margin={"t": 10, "b": 45, "l": 115, "r": 20}, height=190, plot_bgcolor="white", paper_bgcolor="white", transition=CHART_TRANSITION)


def _weekly_loss_figure():
    return go.Figure(go.Bar(
        x=["Week 1", "Week 2", "Week 3", "Week 4"],
        y=[0, 0, 0, 0],
        marker={"color": ["#f3d36a", "#f3b25b", "#e8894e", "#c95e45"]},
        hovertemplate="%{x}: %{y:,.0f} IQD<extra></extra>",
    )).update_layout(yaxis={"title": "Loss (IQD)", "gridcolor": "#e5edf2"}, xaxis={"showgrid": False}, margin={"t": 10, "b": 45, "l": 50, "r": 15}, height=260, plot_bgcolor="white", paper_bgcolor="white", transition=CHART_TRANSITION)


def create_scenario_table():
    return html.Section(
        [
            html.Div("What-if scenarios", className="section-kicker"),
            html.H2("Compare the cost of waiting", className="section-title"),
            dbc.Card(dbc.CardBody([html.H3("Savings comparison", className="panel-title"), dcc.Graph(id="savings-comparison-chart", figure=_savings_comparison_figure(), config={"displayModeBar": False})]), className="analysis-panel mb-3"),
            dbc.Table(
                [
                    html.Thead(html.Tr([html.Th("Metric"), html.Th("Scenario A · Clean today"), html.Th("Scenario B · Ignore 30 days") ])),
                    html.Tbody([
                        html.Tr([html.Th("Expected net revenue", scope="row"), html.Td(id="scenario-clean-revenue", children="-- IQD"), html.Td(id="scenario-ignore-revenue", children="-- IQD")]),
                        html.Tr([html.Th("Efficiency level", scope="row"), html.Td(id="scenario-clean-efficiency", children="--"), html.Td(id="scenario-ignore-efficiency", children="--")]),
                    ]),
                ], bordered=False, hover=True, responsive=True, className="scenario-table"
            ),
            html.Div(className="chart-spacer"),
            dbc.Card(dbc.CardBody([html.H3("Weekly loss if cleaning is ignored", className="panel-title"), dcc.Graph(id="weekly-loss-chart", figure=_weekly_loss_figure(), config={"displayModeBar": False})]), className="analysis-panel mt-3"),
        ], className="scenario-section"
    )
