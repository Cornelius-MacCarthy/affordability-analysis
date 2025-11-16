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
