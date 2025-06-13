import streamlit as st
import pandas as pd
import plotly.express as px
from dataframe import netcdf_to_pandas, load_multiple_files
from algorithm import add_season_column, compute_threshold, classify_risk

path_to_file = "data/C3S-SOILMOISTURE-L3S-SSMV-COMBINED-DAILY-20230101000000-TCDR-v202312.0.0.nc"


@st.cache_data
def load_sample(path):
    return netcdf_to_pandas(path, ["sm", "sm_uncertainty"]).head(100)


df = load_sample(path_to_file)

st.subheader("Sample data")
st.dataframe(df)

fig = px.scatter(
    df,
    x = "lat",
    y = "lon",
    color = "moisture",
    size = "moisture",
   hover_data=["uncertainty"],
    title="Soil Moisture (sample)"
)

st.plotly_chart(fig, use_container_width=True)

