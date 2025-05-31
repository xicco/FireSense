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


# --- 2) SIDEBAR / DATE PICKER ---------------------------------------
st.sidebar.header("Select a date to visualize")
min_date = df_risk["date"].min()
max_date = df_risk["date"].max()
default_date = max_date

selected_date = st.sidebar.date_input(
    "Date",
    value=default_date,
    min_value=min_date,
    max_value=max_date
)

# Filter df_risk to only that date:
df_today = df_risk[df_risk["date"] == selected_date]
df_today_clean = df_today.copy()
df_today_clean["risk_score"] = df_today_clean["risk_score"].fillna(0)

# Quick info at top of sidebar (optional):
st.sidebar.markdown(f"**Showing date for:** {selected_date}")
st.sidebar.markdown(f"**Total grid cells today:** {len(df_today_clean)}")


# --- 3) GEOGRAPHIC VIEW: Plotly Map of Risk Scores -----------------
st.subheader(f"Fire-Risk map on {selected_date}")

if df_today.empty:
    st.warning("No data available for this date.")
else:
    fig_map = px.scatter_mapbox(
        df_today_clean,
        lat="lat",
        lon="lon",
        color="risk_score",
        size="risk_score",
        hover_data=["moisture", "threshold", "risk_flag"],
        color_continuous_scale="YlOrRd",
        size_max=12,
        zoom=3,
        mapbox_style="open-street-map",
        title=None
    )
    # Force the map’s layout to look good
    fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0))

    st.plotly_chart(fig_map, use_container_width=True)

# --- 3) GEOGRAPHIC VIEW: Heatmap of Risk Scores instead of circles ---
st.subheader(f"Fire-Risk Heatmap on {selected_date}")

if df_today.empty:
    st.warning("No data available for this date.")
else:
    # 1. Prepare a “plot” DataFrame that has no NaN risk_score
    #    (either drop NaNs or fill them; here I’ll drop to focus on valid data)

    # 2. Use px.density_mapbox to build a continuous heatmap of risk_score
    fig_heat = px.density_mapbox(
        df_today_clean,
        lat="lat",
        lon="lon",
        z="risk_score",                # weight each point by its risk_score
        radius=10,                     # radius of influence (in pixels) per point
        center={"lat": df_today_clean["lat"].mean(), "lon": df_plot["lon"].mean()},
        zoom=3,                        # adjust based on how zoomed-in you want
        mapbox_style="open-street-map",
        color_continuous_scale="YlOrRd",
        title=None
    )

    # 3. Tweak layout margins so it uses the full width
    fig_heat.update_layout(margin=dict(l=0, r=0, t=0, b=0))

    # 4. Show the heatmap
    st.plotly_chart(fig_heat, use_container_width=True)
