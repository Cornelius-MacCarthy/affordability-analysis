# dashboard.py
# Main 2x2 Dash layout – runs the full dashboard

import dash
from dash import html, dcc

from Scripts.OisinPaulDaly import run_panel
from Scripts.CorneliusMacCarthy import build_affordability_panel
from Scripts.MaximusJohnsonKane import build_dereliction_panel
from Scripts.ConalIrvine import build_completions_panel

app = dash.Dash(__name__)

# Build figures once at start
panel_3d = run_panel()
panel_afford = build_affordability_panel()
panel_derelict = build_dereliction_panel()
panel_completions = build_completions_panel()


def wrap(fig, animate=False):
    return dcc.Graph(
        figure=fig,
        animate=animate,
        config={"displayModeBar": True, "responsive": True},
        style={"height": "100%", "width": "100%", "margin": 0},
    )


app.layout = html.Div(
    style={
        "display": "grid",
        "gridTemplateColumns": "1fr 1fr",
        "gridTemplateRows": "1fr 1fr",
        "gap": "10px",
        "padding": "10px",
        "height": "100vh",
        "boxSizing": "border-box",
        "overflow": "hidden",
    },
    children=[
        # Top-left: 3D panel with slider
        html.Div(
            wrap(panel_3d, animate=True),
            style={
                "border": "1px solid #ddd",
                "padding": 0,
                "overflow": "hidden",
                "height": "100%",
                "minHeight": 0,
            },
        ),
        # Top-right: Affordability
        html.Div(
            wrap(panel_afford),
            style={
                "border": "1px solid #ddd",
                "padding": 0,
                "overflow": "hidden",
                "height": "100%",
                "minHeight": 0,
            },
        ),
        # Bottom-left: Dereliction
        html.Div(
            wrap(panel_derelict),
            style={
                "border": "1px solid #ddd",
                "padding": 0,
                "overflow": "hidden",
                "height": "100%",
                "minHeight": 0,
            },
        ),
        # Bottom-right: Completions
        html.Div(
            wrap(panel_completions),
            style={
                "border": "1px solid #ddd",
                "padding": 0,
                "overflow": "hidden",
                "height": "100%",
                "minHeight": 0,
            },
        ),
    ],
)

if __name__ == "__main__":
    app.run(debug=True)
