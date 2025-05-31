import os
import streamlit as st
import pandas as pd
import plotly.express as px

# Bring in your data-loading and risk-calculation routines:
from dataframe import load_multiple_files
from algorithm import add_season_column, compute_threshold, classify_risk

# Set Streamlit page config if you want a wide layout:
st.set_page_config(page_title="FireSense Dashboard", layout="wide")


# --- 1) CACHE & LOAD ALL DATA ---------------------------------------
@st.cache_data
def load_all_data(data_folder: str) -> pd.DataFrame:
     """
    Load every .nc file in `data_folder`, compute seasonal thresholds, classify risk,
    and return a single DataFrame with these columns at minimum:
      [time, lat, lon, moisture, threshold, risk_flag, risk_score, date, season, ...]
    """
     # 1A. Find all .nc files in that folder:
    all_files = []
    for file in os.listdir(data_folder):
        if file.endswith(".nc"):
            full_path = os.path.join(data_folder, file)
            all_files.append(full_path)


    # 1B. Load them into one big DataFrame:
    #     We ask for both "sm" and "sm_uncertainty" so we get your renamed columns.
    df_all = load_multiple_files(all_files, ["sm", "sm_uncertainty"])

    # 1C. Add season column (needed for thresholds)
    df_all = add_season_column(df_all)

    # 1D. Compute seasonal thresholds once for the entire dataset
    thresholds = compute_threshold(df_all, pct=10.0)

    # 1E. Classify every row (so we get risk_flag + risk_score for all rows)
    df_risk = classify_risk(df_all, thresholds)

    # 1F. Create a "date" column (strip the time-of-day portion)
    #     Now we can easily filter by a single day.
    df_risk["date"] = df_risk["time"].dt.date

    return df_risk

# Call it once (cached on disk/memory):
DATA_FOLDER = "data/daily/"
df_risk = load_all_data(DATA_FOLDER)

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

