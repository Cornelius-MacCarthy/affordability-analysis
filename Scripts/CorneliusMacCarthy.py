def build_affordability_panel():

    import os
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.offline as pyo
    # Setting file paths
    from pathlib import Path
    DL = Path(__file__).resolve().parent.parent / "Data"
    F_INCOME_1 = DL / "Median_income_2004-2019.csv"
    F_INCOME_2 = DL / "Median_income_2020-2024.csv"
    F_RENT     = DL / "Rents_per_month_by_location.csv"
    F_PPI      = DL / "Property_Price_Index.csv"


    # Loading in CSV files basaed on file paths
    income1 = pd.read_csv(F_INCOME_1)
    income2 = pd.read_csv(F_INCOME_2)
    rents   = pd.read_csv(F_RENT)
    ppi     = pd.read_csv(F_PPI)


    # edit column names
    for df in (income1, income2, rents, ppi):
        df.columns = df.columns.str.strip().str.replace(" ", "_")
    # Keep only year + value from both income files
    income1_small = income1[["Year", "VALUE"]]
    income2_small = income2[["Year", "VALUE"]]

    # Combine and average within each year
    income_all = pd.concat([income1_small, income2_small], ignore_index=True)
    income_all = income_all.groupby("Year", as_index=False)["VALUE"].mean()
    income_all = income_all.rename(columns={"VALUE": "Annual_Income"})
    income_all = income_all.sort_values("Year")

    # Convert to monthly income and give each year a date (middle of year)
    income_all["Monthly_Income"] = income_all["Annual_Income"] / 12
    income_all["Date"] = pd.to_datetime(income_all["Year"].astype(str) + "-07-01")
    # Create a full monthly date range and interpolate income
    date_monthly = pd.date_range("2004-01-01", "2025-12-01", freq="MS")
    income_monthly = (income_all.set_index("Date")[["Monthly_Income"]].reindex(date_monthly).interpolate(method="time").rename_axis("Date").reset_index())

    # Create income index (2008-01-01 = 100) for buyers overlay
    base_income_2008 = income_monthly.loc[income_monthly["Date"] == pd.Timestamp("2008-01-01"),"Monthly_Income"].iloc[0]
    income_monthly["Income_Index_2008"] = (income_monthly["Monthly_Income"] / base_income_2008 * 100)

    # Yearly income (for renters chart)
    income_year = income_all[["Year", "Monthly_Income"]]

    # Monthly income index from 2008 onwards (for buyers chart)
    income_m_idx = income_monthly.loc[income_monthly["Date"] >= "2008-01-01",["Date", "Income_Index_2008"]]

    # Keep only year + value from both income files
    income1_small = income1[["Year", "VALUE"]]
    income2_small = income2[["Year", "VALUE"]]

    # Combine and average inside each year
    income_all = pd.concat([income1_small, income2_small], ignore_index=True)
    income_all = income_all.groupby("Year", as_index=False)["VALUE"].mean()
    income_all = income_all.rename(columns={"VALUE": "Annual_Income"})
    income_all = income_all.sort_values("Year")

    # Convert to monthly income and give each year a date (middle of year)
    income_all["Monthly_Income"] = income_all["Annual_Income"] / 12
    income_all["Date"] = pd.to_datetime(income_all["Year"].astype(str) + "-07-01")
    # Create a full monthly date range and interpolate income figs
    date_monthly = pd.date_range("2004-01-01", "2025-12-01", freq="MS")
    income_monthly = (income_all.set_index("Date")[["Monthly_Income"]].reindex(date_monthly).interpolate(method="time").rename_axis("Date").reset_index())

    # Create income index (2008-01-01 = 100) 
    base_income_2008 = income_monthly.loc[income_monthly["Date"] == pd.Timestamp("2008-01-01"),"Monthly_Income"].iloc[0]
    income_monthly["Income_Index_2008"] = (income_monthly["Monthly_Income"] / base_income_2008 * 100)

    # Yearly income (for renters chart)
    income_year = income_all[["Year", "Monthly_Income"]]

    # Monthly income index from 2008 onwards (for buyers chart)
    income_m_idx = income_monthly.loc[income_monthly["Date"] >= "2008-01-01",["Date", "Income_Index_2008"]]
    # RENTS: ANNUAL AVERAGE RENTS BY REGION

    # Use all bedrooms, all property types
    r = rents[(rents["Number_of_Bedrooms"] == "All bedrooms") &(rents["Property_Type"] == "All property types")].copy()
    r["VALUE"] = pd.to_numeric(r["VALUE"], errors="coerce")

    # Label Dublin vs Non-Dublin
    r["Region"] = np.where(r["Location"].str.contains("Dublin", na=False), "Dublin","Non-Dublin")

    # Average rent per year and region
    rent_year = (r.groupby(["Year", "Region"])["VALUE"].mean().reset_index().pivot(index="Year", columns="Region", values="VALUE").reset_index())

    # Add All-Ireland average (simple mean of Dublin + Non-Dublin)
    rent_year["All-Ireland"] = rent_year[["Dublin", "Non-Dublin"]].mean(axis=1)

    # Attach yearly income (for renters view)
    renters = rent_year.merge(income_year, on="Year", how="inner")
    renters = renters[renters["Year"].between(2008, 2024)]

    # PROPERTY PRICE INDEX: REBASE TO 2008=100

    ppi = ppi.rename(columns={"Type_of_Residential_Property": "Type","VALUE": "Value"})
    ppi["Date"] = pd.to_datetime(ppi["Month"], format="%Y %B", errors="coerce")
    ppi["Year"] = ppi["Date"].dt.year
    ppi["Value"] = pd.to_numeric(ppi["Value"], errors="coerce")

    # Keeping just necessary series
    wanted_types = ["Dublin - houses","Dublin - apartments","National - houses","National - apartments"]
    ppi = ppi[ppi["Type"].isin(wanted_types) &ppi["Value"].notna() &ppi["Date"].notna()].copy()

    # Region column: Dublin vs All-Ireland
    ppi["Region"] = np.where(ppi["Type"].str.startswith("Dublin -"),"Dublin","All-Ireland")

    # Property type: Houses vs Apartments
    ppi["PropertyType"] = np.where(ppi["Type"].str.contains("apartments", case=False),"Apartments","Houses")

    # Rebase each (Region, PropertyType) to 2008=100
    rebased_parts = []
    group_cols = ["Region", "PropertyType"]

    for (reg, prop), grp in ppi.groupby(group_cols):
        g = grp.sort_values("Date").copy()
        # first value in 2008 as base
        base_row = g.loc[g["Year"] >= 2008].head(1)
        base_val_ppi = float(base_row["Value"].iloc[0])

        g["PPI_Index_2008"] = g["Value"] / base_val_ppi * 100
        g = g[g["Date"] >= "2008-01-01"]  # start at 2008 in january 
        rebased_parts.append(g)

    ppi_idx = pd.concat(rebased_parts, ignore_index=True)

    FT_COLORS = {"dublin": "#e75446","non": "#1a3b5d","all": "#a39e9e","income": "#000000"}
    layout_ft = dict(plot_bgcolor="#FFF1E5",paper_bgcolor="#FFF1E5",font=dict(family="Georgia, 'Times New Roman', serif",size=14,color="#3C3C3C"),hovermode="x unified",xaxis=dict(showgrid=True,gridcolor="#dddddd",zeroline=False),yaxis=dict(showgrid=True,gridcolor="#dddddd",zeroline=False),legend=dict(orientation="h",y=-0.25,x=0.5,xanchor="center",bgcolor="rgba(255,255,255,0.85)"),margin=dict(l=60,r=50,t=80,b=70))

    fig = go.Figure()

    # Renters traces 
    for region, color in zip(["Dublin", "Non-Dublin", "All-Ireland"],[FT_COLORS["dublin"], FT_COLORS["non"], FT_COLORS["all"]]):
        fig.add_trace(go.Scatter(x=renters["Year"],y=renters[region],name=f"{region} Rent (€)",mode="lines+markers",line=dict(color=color, width=3),visible=(region == "Dublin")  ) )

    # Median monthly income (renters view)
    fig.add_trace(go.Scatter(x=renters["Year"],y=renters["Monthly_Income"],name="Median Monthly Income (€)",mode="lines+markers",line=dict(color=FT_COLORS["income"], width=3),visible=True))

    # Buyers traces  
    buyers_series = [("Dublin","Houses",FT_COLORS["dublin"]),("Dublin","Apartments",FT_COLORS["all"]),("All-Ireland","Houses",FT_COLORS["dublin"]),("All-Ireland","Apartments",FT_COLORS["all"]),]

    for reg, prop, col in buyers_series:
        d = ppi_idx[(ppi_idx["Region"] == reg) &(ppi_idx["PropertyType"] == prop)]
        fig.add_trace(go.Scatter(x=d["Date"],y=d["PPI_Index_2008"],name=f"{reg} {prop} Index (2008=100)",mode="lines+markers",line=dict(color=col, width=3),visible=False))

    # Income index for buyers (2008=100)
    fig.add_trace(go.Scatter(x=income_m_idx["Date"],y=income_m_idx["Income_Index_2008"],name="Median Monthly Income (2008=100)",mode="lines",line=dict(color=FT_COLORS["income"], width=3),visible=False))

    def vis(*indices_on):
        visible_list = [False] * len(fig.data)
        for idx in indices_on:
            visible_list[idx] = True
        return visible_list

    RENT_DUB, RENT_NON, RENT_ALL, RENT_INC = 0, 1, 2, 3
    BUY_DUB_H, BUY_DUB_A, BUY_ALL_H, BUY_ALL_A, BUY_INC = 4, 5, 6, 7, 8

    buttons = [
    dict(label="Renters • Dublin", method="update", args=[{"visible": vis(RENT_DUB, RENT_INC)}, {"yaxis":{"title":"Euro (€)"}, "xaxis":{"title":"Year","type":"-"}, "title":{"text":"Affordability — Renters • Dublin"}}]),
    dict(label="Renters • Non-Dublin", method="update", args=[{"visible": vis(RENT_NON, RENT_INC)}, {"yaxis":{"title":"Euro (€)"}, "xaxis":{"title":"Year","type":"-"}, "title":{"text":"Affordability — Renters • Non-Dublin"}}]),
    dict(label="Renters • All-Ireland", method="update", args=[{"visible": vis(RENT_ALL, RENT_INC)}, {"yaxis":{"title":"Euro (€)"}, "xaxis":{"title":"Year","type":"-"}, "title":{"text":"Affordability — Renters • All-Ireland"}}]),
    dict(label="Buyers • Dublin Houses", method="update", args=[{"visible": vis(BUY_DUB_H, BUY_INC)}, {"yaxis":{"title":"Index (2008=100)"}, "xaxis":{"title":"Month","type":"date"}, "title":{"text":"Affordability — Buyers • Dublin • Houses"}}]),
    dict(label="Buyers • Dublin Apartments", method="update", args=[{"visible": vis(BUY_DUB_A, BUY_INC)}, {"yaxis":{"title":"Index (2008=100)"}, "xaxis":{"title":"Month","type":"date"}, "title":{"text":"Affordability — Buyers • Dublin • Apartments"}}]),
    dict(label="Buyers • All-Ireland Houses", method="update", args=[{"visible": vis(BUY_ALL_H, BUY_INC)}, {"yaxis":{"title":"Index (2008=100)"}, "xaxis":{"title":"Month","type":"date"}, "title":{"text":"Affordability — Buyers • All-Ireland • Houses"}}]),
    dict(label="Buyers • All-Ireland Apartments", method="update", args=[{"visible": vis(BUY_ALL_A, BUY_INC)}, {"yaxis":{"title":"Index (2008=100)"}, "xaxis":{"title":"Month","type":"date"}, "title":{"text":"Affordability — Buyers • All-Ireland • Apartments"}}])]

    fig.update_layout(layout_ft, title="Affordability — Renters • Dublin",title_font=dict(family="Georgia, 'Times New Roman', serif", size=18, color="#3C3C3C"),updatemenus=[dict(type="dropdown", direction="down", x=1.04, y=1.0, xanchor="left", yanchor="top",bgcolor="rgba(255,255,255,0.9)", bordercolor="#ddd", buttons=buttons)])
    fig.add_annotation(text=("Source: CSO & RTB — Median Income (annual to monthly interpolation), ""RTB Average Rents (All bedrooms, All property types), "
                                "and CSO Residential PPI (rebased to 2008=100)."),showarrow=False, xref="paper", yref="paper", x=0, y=-0.22,font=dict(family="Georgia, 'Times New Roman', serif", size=12, color="#3C3C3C"))
    return fig

