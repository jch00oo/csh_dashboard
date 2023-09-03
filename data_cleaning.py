import streamlit as st
import pandas as pd
import plotly
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

### This is the Python script for data cleaning and basic calculations to be used for the dashboard. If importing new data/columns and/or changes need to be made to calculations, edit this file.

# data loading
url = 'https://raw.githubusercontent.com/jch00oo/csh_dashboard/main/Data%20Dump%20_%20Customer%20Metrics%20(make%20a%20copy)%20-%20Raw%20CM%20Data.csv'
data = pd.read_csv(url)

# change columns to date type
date_columns = ["Last Product Usage Date", "Activation Date"]

for column in date_columns:
    data[column] = data[column].astype("datetime64[ns]").dt.date
    data[column] = data[column].astype("datetime64[ns]")

# changing product type categorical to numerical rank

# 0: nan
# 1: POS Integration
# 2: Order Manager
# 3: Premium
# 4: Premium + POS

hp_types = list(data["Highest Product"].unique())
hp_types_rank = [2,3,4,1,0]

data["HP Score"] = (data["Highest Product"].replace(hp_types, hp_types_rank) / 4) * 30

# changing payment status to priority rank

# 0: nan
# 1: Canceled
# 2: Paused
# 3: Past_Due
# 4: Pending
# 5: Active

pm_types = list(data["Payment Status"].unique())
pm_types_rank = [5,0,3,1,2,4]

data["PS Score"] = (data["Payment Status"].replace(pm_types, pm_types_rank) / 5) * 25

### Weekly profit

# only consider fulfilled orders; subtract cancellations and missed orders
data["Fulfilled Orders Week 1"] = data["Orders Week 1"] - data["Cancellations Week 1"] - data["Missed Orders Week 1"]
data["Fulfilled Orders Week 2"] = data["Orders Week 2"] - data["Cancellations Week 2"] - data["Missed Orders Week 2"]

data["Profit Week 1"] = data["Average Order Value week 1"] * data["Fulfilled Orders Week 1"]
data["Profit Week 2"] = data["Average Order Week 2"] * data["Fulfilled Orders Week 2"]

### What should be considered recent for last product usage date?

# best: after 35%
# okay: bw 25% and 35%
# less okay: bw 15% and 25%
# bad: less than 15%

data["LPU Score"] = 0

# best: after 35%
data.loc[data["Last Product Usage Date"] >= np.nanpercentile(data["Last Product Usage Date"], 35), "LPU Score"] = 4
# okay: bw 25% and 35%
data.loc[(data["Last Product Usage Date"] < np.nanpercentile(data["Last Product Usage Date"], 35)) & (data["Last Product Usage Date"] >= np.percentile(data["Last Product Usage Date"], 25)), "LPU Score"] = 3
# less okay: bw 15% and 25%
data.loc[(data["Last Product Usage Date"] < np.nanpercentile(data["Last Product Usage Date"], 25)) & (data["Last Product Usage Date"] >= np.percentile(data["Last Product Usage Date"], 15)), "LPU Score"] = 2
# bad: less than 15%
data.loc[data["Last Product Usage Date"] < np.nanpercentile(data["Last Product Usage Date"], 15), "LPU Score"] = 1

data["LPU Score"] = (data["LPU Score"] / 4) * 25

# normalizing profit growth rate

data["Profit Growth Rate"] = (data["Average Order Week 2"] - data["Average Order Value week 1"]) / data["Average Order Value week 1"]
data["Profit Growth Rate"].replace(np.inf, np.nan, inplace=True)
data["Normalized & Scaled PGR"] = ((data["Profit Growth Rate"] - np.nanmin(data["Profit Growth Rate"])) / (np.nanmax(data["Profit Growth Rate"]) - np.nanmin(data["Profit Growth Rate"]))) * 20

# calculate customer health score

data["Customer Health Score"] = data["LPU Score"] + data["PS Score"] + data["HP Score"] + data["Normalized & Scaled PGR"]

data["Customer Health"] = "Missing Data"
data.loc[data["Customer Health Score"] >= 75, "Customer Health"] = "Healthy"
data.loc[(data["Customer Health Score"] >= 40) & (data["Customer Health Score"] < 75), "Customer Health"] = "Neutral"
data.loc[data["Customer Health Score"] < 40, "Customer Health"] = "Unhealthy"

data_missing = data[data["Customer Health"] == "Missing Data"]
data = data[data["Customer Health"] != "Missing Data"]
