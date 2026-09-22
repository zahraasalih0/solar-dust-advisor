from dash import dcc, html
import dash_bootstrap_components as dbc


def _metric_card(card_id, eyebrow, title, value, detail, accent):
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(eyebrow, className="card-eyebrow"),
                html.Div(title, className="card-title"),
                html.Div(value, id=card_id, className="card-value"),
                html.Div(detail, className="card-detail"),
            ]
        ),
        className=f"metric-card {accent}",
    )


def create_financial_cards(defaults):
    return dcc.Loading(
        html.Section(
            [
                html.Div("Financial executive view", className="section-kicker"),
                html.H2("Clean with confidence", className="section-title"),
                dbc.Row(
                    [
                        dbc.Col(_metric_card("recommendation-value", "●  DECISION", "Action recommendation", "Ready", "Based on 15/30-day payback thresholds", "recommendation-card"), lg=4, className="mb-3"),
                        dbc.Col(_metric_card("payback-value", "◷  RETURN", "Payback period", "-- days", "Cleaning investment recovery", "info-card"), lg=4, className="mb-3"),
                        dbc.Col(_metric_card("loss-value", "!  EXPOSURE", "Current & 7-day loss", "0 IQD / 0 IQD", "Estimated revenue at risk", "loss-card"), lg=4, className="mb-3"),
                    ],
                    className="g-3",
                ),
            ],
            className="financial-section",
        ),
        type="circle",
        color="#2f78a8",
    )
