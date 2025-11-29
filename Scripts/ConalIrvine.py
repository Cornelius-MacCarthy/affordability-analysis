# Scripts/ConallIrvine.py
# Panel 4 – New dwelling completions

def build_completions_panel():
    import pandas as pd
    import plotly.graph_objects as go
    from pathlib import Path

    # --- 1. Load dataset from ../Data ---
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "Data"
    df = pd.read_csv(DATA_DIR / "NDA02.20251105T221144.csv")

    # --- 2. Filter to main dwelling types ---
    dwelling_types = ["Single house", "Scheme house", "Apartment"]
    df = df[df["Type of House"].isin(dwelling_types)]

    # --- 3. Aggregate and compute shares ---
    df_year = df.groupby(["Year", "Type of House"], as_index=False)["VALUE"].sum()
    df_year["Total"] = df_year.groupby("Year")["VALUE"].transform("sum")
    df_year["Share"] = df_year["VALUE"] / df_year["Total"]

    order = ["Single house", "Scheme house", "Apartment"]

    # (a) Shares for composition view
    df_pivot = (
        df_year.pivot(index="Year", columns="Type of House", values="Share")
        .reindex(columns=order)
        .fillna(0)
    )

    # (b) Absolute totals per year
    df_totals = df_year.groupby("Year", as_index=False)["Total"].first()

    # (c) Absolute completions by type
    df_abs = df_year.groupby(["Year", "Type of House"], as_index=False)["VALUE"].sum()
    df_abs_pivot = (
        df_abs.pivot(index="Year", columns="Type of House", values="VALUE")
        .reindex(columns=order)
        .fillna(0)
    )

    # --- 4. Build interactive figure ---
    fig = go.Figure()

    colors = {
        "Single house": "#f2ccbf",
        "Scheme house": "#8da0b6",
        "Apartment": "#d06a75",
        "Total": "#6b7b8c",
    }

    # Stacked area (% composition)
    for name in order:
        fig.add_trace(
            go.Scatter(
                x=df_pivot.index,
                y=df_pivot[name],
                stackgroup="one",
                name=name,
                mode="none",
                fillcolor=colors[name],
                hovertemplate=f"{name}: %{{y:.1%}}<extra></extra>",
                visible=True,
            )
        )

    # White separators
    cumulative = df_pivot.cumsum(axis=1)
    for name in order[1:]:
        fig.add_trace(
            go.Scatter(
                x=cumulative.index,
                y=cumulative[name],
                mode="lines",
                line=dict(color="white", width=1),
                hoverinfo="skip",
                showlegend=False,
                visible=True,
            )
        )

    # Total completions line
    fig.add_trace(
        go.Scatter(
            x=df_totals["Year"],
            y=df_totals["Total"],
            name="Total completions",
            mode="lines",
            line=dict(color=colors["Total"], width=3),
            fill="tozeroy",
            fillcolor="rgba(139,154,172,0.25)",
            hovertemplate="Total: %{y:,}<extra></extra>",
            visible=False,
        )
    )

    # Stacked bars (absolute)
    for name in order:
        fig.add_trace(
            go.Bar(
                x=df_abs_pivot.index,
                y=df_abs_pivot[name],
                name=name,
                marker=dict(color=colors[name]),
                hovertemplate=f"Year %{{x}}<br>{name}: %{{y:,}}<extra></extra>",
                visible=False,
            )
        )

    # --- 5. Visibility logic ---
    num_area_layers = len(order)
    num_separators = len(order) - 1
    num_area_block = num_area_layers + num_separators
    num_total_line = 1
    num_bar_traces = len(order)

    visible_comp = [True] * num_area_block + [False] * (
        num_total_line + num_bar_traces
    )
    visible_total = [False] * num_area_block + [True] + [False] * num_bar_traces
    visible_bars = [False] * (num_area_block + num_total_line) + [True] * num_bar_traces

    # --- 6. Buttons + FT-style layout ---
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                x=0.5,
                xanchor="center",
                y=1.2,
                yanchor="top",
                buttons=[
                    dict(
                        label="Composition (%)",
                        method="update",
                        args=[
                            {"visible": visible_comp},
                            {
                                "yaxis": {
                                    "title": "Share of total completions (%)",
                                    "tickformat": ".0%",
                                    "range": [0, 1],
                                },
                                "title": {
                                    "text": "Composition of New Dwelling Completions in Ireland"
                                },
                                "barmode": "stack",
                            },
                        ],
                    ),
                    dict(
                        label="Total completions (line)",
                        method="update",
                        args=[
                            {"visible": visible_total},
                            {
                                "yaxis": {
                                    "title": "Total completions",
                                    "tickformat": ",",
                                    "range": [0, df_totals["Total"].max() * 1.1],
                                },
                                "title": {
                                    "text": "Total New Dwelling Completions per Year"
                                },
                                "barmode": "stack",
                            },
                        ],
                    ),
                    dict(
                        label="Total & breakdown (bars)",
                        method="update",
                        args=[
                            {"visible": visible_bars},
                            {
                                "yaxis": {
                                    "title": "New dwelling completions",
                                    "tickformat": ",",
                                    "range": [0, df_totals["Total"].max() * 1.1],
                                },
                                "title": {
                                    "text": "New Dwelling Completions by Type and Year"
                                },
                                "barmode": "stack",
                            },
                        ],
                    ),
                ],
                direction="right",
                showactive=True,
                bgcolor="white",
                bordercolor="#ccc",
                borderwidth=1,
            )
        ],
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=70, r=50, t=130, b=80),
        title_font=dict(
            family="Georgia, 'Times New Roman', serif",
            size=18,
            color="#3C3C3C",
        ),
        font=dict(
            family="Georgia, 'Times New Roman', serif",
            size=14,
            color="#3C3C3C",
        ),
        plot_bgcolor="#FFF1E5",
        paper_bgcolor="#FFF1E5",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="center",
            x=0.5,
        ),
        xaxis=dict(
            title=None,  # no "Year" axis title as requested
            showgrid=True,
            gridcolor="#dcd6d0",
            linecolor="#dcd6d0",
            zeroline=False,
            range=[df_pivot.index.min() - 0.2, df_pivot.index.max()],
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#dcd6d0",
            linecolor="#dcd6d0",
            zeroline=False,
        ),
        transition=dict(duration=600, easing="cubic-in-out"),
        autosize=True,
        height=None,
    )

    fig.add_annotation(
        text="Source: CSO",
        xref="paper",
        yref="paper",
        x=0,
        y=-0.32,
        showarrow=False,
        font=dict(
            family="Georgia, 'Times New Roman', serif",
            size=12,
            color="#3C3C3C",
        ),
    )

    return fig
