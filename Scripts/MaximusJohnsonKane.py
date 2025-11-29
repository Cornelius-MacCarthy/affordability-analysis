# Scripts/MaximusJohnsonKane.py
# Panel 3 – Vacancy & Dereliction Maps (Dashboard FT-styled version)

def build_dereliction_panel():

    import pandas as pd
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # Load data
    data = {
        'County': ['Dublin', 'Kildare', 'Waterford', 'Carlow', 'Meath', 'Laois', 'Wicklow', 'Wexford',
                  'Kilkenny', 'Louth', 'Offaly', 'Cork', 'Limerick', 'Westmeath', 'Monaghan',
                  'Tipperary', 'Clare', 'Galway', 'Cavan', 'Kerry', 'Longford', 'Sligo', 'Donegal',
                  'Roscommon', 'Mayo', 'Leitrim'] * 2,
        'Type': ['Vacancy rate'] * 26 + ['Derelicts'] * 26,
        '%': [1.1, 1.6, 2.1, 2.5, 2.6, 2.6, 2.8, 2.8, 3.0, 3.4, 3.5, 3.7, 3.7, 4.5, 4.5,
              4.7, 5.1, 5.4, 6.7, 7.0, 7.1, 8.4, 9.0, 10.1, 10.6, 11.9,
              1.1, 1.2, 1.4, 1.0, 1.6, 1.1, 1.0, 1.7, 1.1, 1.2, 1.6, 6.4, 5.3, 1.6, 1.7,
              5.6, 5.0, 8.9, 2.8, 5.6, 2.3, 5.6, 11.5, 6.1, 14.1, 3.4]
    }

    df = pd.DataFrame(data)

    county_coords = {
        'Dublin': {'lat': 53.3498, 'lon': -6.2603},
        'Kildare': {'lat': 53.1601, 'lon': -6.9144},
        'Waterford': {'lat': 52.2593, 'lon': -7.1101},
        'Carlow': {'lat': 52.8404, 'lon': -6.9261},
        'Meath': {'lat': 53.6496, 'lon': -6.6563},
        'Laois': {'lat': 53.0324, 'lon': -7.3000},
        'Wicklow': {'lat': 53.0000, 'lon': -6.4167},
        'Wexford': {'lat': 52.5000, 'lon': -6.6667},
        'Kilkenny': {'lat': 52.6541, 'lon': -7.2522},
        'Louth': {'lat': 53.9358, 'lon': -6.5400},
        'Offaly': {'lat': 53.2739, 'lon': -7.4888},
        'Cork': {'lat': 51.8969, 'lon': -8.4863},
        'Limerick': {'lat': 52.6638, 'lon': -8.6267},
        'Westmeath': {'lat': 53.5345, 'lon': -7.3463},
        'Monaghan': {'lat': 54.2490, 'lon': -6.9683},
        'Tipperary': {'lat': 52.4738, 'lon': -8.1619},
        'Clare': {'lat': 52.9045, 'lon': -8.9811},
        'Galway': {'lat': 53.2707, 'lon': -9.0568},
        'Cavan': {'lat': 53.9908, 'lon': -7.3616},
        'Kerry': {'lat': 52.0600, 'lon': -9.5000},
        'Longford': {'lat': 53.7270, 'lon': -7.7992},
        'Sligo': {'lat': 54.2700, 'lon': -8.4700},
        'Donegal': {'lat': 54.6541, 'lon': -8.1106},
        'Roscommon': {'lat': 53.6333, 'lon': -8.1833},
        'Mayo': {'lat': 53.9000, 'lon': -9.3500},
        'Leitrim': {'lat': 54.1167, 'lon': -8.0000},
    }

    df['lat'] = df['County'].map(lambda x: county_coords[x]['lat'])
    df['lon'] = df['County'].map(lambda x: county_coords[x]['lon'])

    vacancy_df = df[df['Type'] == 'Vacancy rate']
    derelict_df = df[df['Type'] == 'Derelicts']

    # FT colour palette
    FT_BG = "#FFF1E5"
    FT_TEXT = "#3C3C3C"

    vacancy_scale = [
        [0.0, "#A7C4CF"],
        [0.4, "#6D8D99"],
        [1.0, "#3E5E66"],
    ]

    derelict_scale = [
        [0.0, "#F2B6A0"],
        [0.4, "#E97E63"],
        [1.0, "#D95847"],
    ]

    fig = make_subplots(
        rows=1,
        cols=2,
        horizontal_spacing=0.05,
        subplot_titles=[
            "Vacancy rates by county (%)",
            "Derelict rates by county (%)",
        ],
        specs=[[{"type": "scattermapbox"}, {"type": "scattermapbox"}]],
    )

    fig.add_trace(
        go.Scattermapbox(
            lat=vacancy_df['lat'],
            lon=vacancy_df['lon'],
            text=vacancy_df['County'] + ": " + vacancy_df['%'].astype(str) + "%",
            marker=dict(
                size=vacancy_df['%'] * 2.2 + 8,
                color=vacancy_df['%'],
                colorscale=vacancy_scale,
                opacity=0.85,
            ),
            hovertemplate="<b>%{text}</b><extra></extra>",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scattermapbox(
            lat=derelict_df['lat'],
            lon=derelict_df['lon'],
            text=derelict_df['County'] + ": " + derelict_df['%'].astype(str) + "%",
            marker=dict(
                size=derelict_df['%'] * 2.2 + 8,
                color=derelict_df['%'],
                colorscale=derelict_scale,
                opacity=0.85,
            ),
            hovertemplate="<b>%{text}</b><extra></extra>",
        ),
        row=1,
        col=2,
    )

    fig.update_layout(
        autosize=True,
        paper_bgcolor=FT_BG,
        plot_bgcolor=FT_BG,
        margin=dict(t=80, b=40, l=10, r=10),
        title=dict(
            text="<b>Ireland: Vacancy & Derelict Rates by County</b>",
            x=0.02,
            xanchor="left",
            yanchor="top",
            font=dict(
                family="Georgia, 'Times New Roman', serif",
                size=18,
                color=FT_TEXT,
            ),
        ),
        font=dict(
            family="Georgia, 'Times New Roman', serif",
            size=13,
            color=FT_TEXT,
        ),
        mapbox1=dict(style="open-street-map", center=dict(lat=53.5, lon=-8), zoom=5.25),
        mapbox2=dict(style="open-street-map", center=dict(lat=53.5, lon=-8), zoom=5.25),
    )

    fig.add_annotation(
        text="Source: County data analysis · FT-style colour scheme",
        x=0.02,
        y=-0.18,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(
            family="Georgia, 'Times New Roman', serif",
            size=11,
            color=FT_TEXT,
        ),
    )

    return fig
