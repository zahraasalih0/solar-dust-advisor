from dash import dcc, html
import dash_bootstrap_components as dbc


def create_control_panel(defaults):
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.Div("Decision controls", className="section-kicker"),
                        html.H2("Tune your operating assumptions", className="section-title"),
                    ],
                    className="control-heading",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Capacity (kW)", html_for="capacity-input"),
                                dbc.Input(id="capacity-input", type="number", value=defaults["capacity_kw"], min=1, step=1),
                            ], md=3, className="control-field"
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Tariff (IQD / kWh)", html_for="tariff-slider"),
                                dcc.Slider(id="tariff-slider", min=1, max=1000, step=1, value=defaults["tariff_iqd_per_kwh"], marks=None, tooltip={"placement": "bottom", "always_visible": True}),
                            ], md=3, className="control-field slider-field"
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Label("Cleaning cost (IQD)", html_for="cleaning-cost-input"),
                                        html.Span("Auto-calculated: Water (500) + Labor (600) + Consumables (100) per panel", className="field-tooltip", title="Auto-calculated: Water (500) + Labor (600) + Consumables (100) per panel"),
                                    ],
                                    className="label-with-tooltip",
                                ),
                                dbc.Input(id="cleaning-cost-input", type="number", value=defaults["cleaning_cost_iqd"], min=0, step=100),
                            ], md=3, className="control-field"
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Last cleaning date", html_for="last-cleaning-date"),
                                dcc.DatePickerSingle(id="last-cleaning-date", date=defaults["last_cleaning_date"], display_format="DD MMM YYYY", clearable=False),
                            ], md=3, className="control-field"
                        ),
                    ],
                    className="g-3 align-items-end",
                ),
                dbc.Button("↻  Recalculate", id="recalculate-button", color="primary", className="recalculate-button", n_clicks=0),
            ]
        ),
        className="control-panel",
    )
