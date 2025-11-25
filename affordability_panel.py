import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.offline as pyo
# Setting file paths
DL = r"C:\Users\conor\Documents\Affordability Analysis"
F_INCOME_1 = os.path.join(DL, "Median_income_2004-2019.csv")
F_INCOME_2 = os.path.join(DL, "Median_income_2020-2024.csv")
F_RENT     = os.path.join(DL, "Rents_per_month_by_location.csv")
F_PPI      = os.path.join(DL, "Property_Price_Index.csv")
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
