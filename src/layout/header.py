from dash import html
import dash_bootstrap_components as dbc


def create_header():
    return dbc.Navbar(
        [
            html.Canvas(id="dust-particles-canvas", className="dust-particles-canvas"),
            dbc.Container(
                [
                    html.Div(
                        [
                            html.Div("☀", className="brand-mark"),
                            html.Div(
                                [
                                    html.Div("SolarOptima", className="brand-name"),
                                    html.Div("Smart Decision Support System", className="brand-subtitle"),
                                ]
                            ),
                        ],
                        className="brand-lockup",
                    ),
                    html.Div(
                        [
                            dbc.Button("◉", className="icon-button", color="link", title="Notifications"),
                            dbc.Button("♙", className="icon-button", color="link", title="User profile"),
                        ],
                        className="header-actions",
                    ),
                ],
                fluid=True,
            ),
        ],
        className="topbar",
    )
