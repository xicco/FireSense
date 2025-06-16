import os
import streamlit as st
import pandas as pd
import plotly.express as px

# Bring in your data-loading and risk-calculation routines:
from dataframe import load_multiple_files, load_fire_data
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

FIRE_DATA_PATH = "data/fire/fire_archive_MODIS_GLOBAL_2023.csv"
df_fire = load_fire_data(FIRE_DATA_PATH)


# SIDEBAR / DATE PICKER
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
moisture_today = df_risk[df_risk["date"] == selected_date]
fire_today = df_fire[df_fire["date"] == pd.to_datetime(selected_date)]

# Clean up any NaNs in risk_score (so plots won’t break)
moisture_today_clean = moisture_today.copy()
moisture_today_clean["risk_score"] = moisture_today_clean["risk_score"].fillna(0)

# Quick info at top of sidebar (optional):
st.sidebar.markdown(f"**Showing date for:** {selected_date}")
st.sidebar.markdown(f"**Total grid cells today:** {len(moisture_today_clean)}")








# SUMMARY METRICS
st.subheader("🔥 Today’s Fire-Risk Overview")

# compute KPIs
total_cells = len(moisture_today_clean)
at_risk_cells = int(moisture_today_clean["risk_flag"].sum())
if total_cells:
    pct_at_risk = (at_risk_cells / total_cells)
else:
    pct_at_risk = 0

# create 3 columns for summary metrics
col1, col2, col3 = st.columns(3)

# fill them with metrics
col1.metric("Total Grid Cells",      f"{total_cells}")
col2.metric("Cells At Risk",         f"{at_risk_cells}")
col3.metric("Percent At Risk",       f"{pct_at_risk:.1%}")







# GEOGRAPHIC VIEW
st.subheader(f"Fire-Risk Heatmap on {selected_date}")

if moisture_today.empty:
    st.warning("No data available for this date.")
else:
    # 1. Prepare a “plot” DataFrame that has no NaN risk_score
    #    (either drop NaNs or fill them; here I’ll drop to focus on valid data)

    # 2. Use px.density_mapbox to build a continuous heatmap of risk_score
    fig_heat = px.density_map(
        moisture_today_clean,
        lat="lat",
        lon="lon", 
        z="risk_score",                # weight each point by its risk_score
        radius=10,                     # radius of influence (in pixels) per point
        center={"lat": moisture_today_clean["lat"].mean(), "lon": moisture_today_clean["lon"].mean()},
        zoom=3,                        # adjust based on how zoomed-in you want
        map_style="open-street-map",
        color_continuous_scale="YlOrRd",
        title=None
    )

    # 3. Tweak layout margins so it uses the full width
    #fig_heat.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    

    # 4. Add fire points if available
    if not fire_today.empty:
        fig_heat.add_scattermap(
            lat=fire_today["lat"],
            lon=fire_today["lon"],
            mode="markers",
            marker=dict(
                size=5,
                color="red",
                opacity=0.4
            ),
            name="Detected Fires"
        )

    fig_heat.update_layout(
    mapbox=dict(
        style="open-street-map",
        center={"lat": moisture_today_clean["lat"].mean(), "lon": moisture_today_clean["lon"].mean()},
        zoom=3
    ),
    margin=dict(l=0, r=0, t=0, b=0),
    showlegend=True
    )

    # 5. Show the final combined map
    st.plotly_chart(fig_heat, use_container_width=True, config={"scrollZoom": True})



st.markdown("<br><br>", unsafe_allow_html=True)





# LINE GRAPH
 # 4a. Count “how many total rows” per date
total_per_day = (
    df_risk
    .groupby("date")   # “group” the DataFrame by each distinct date
    .size()            # count how many rows are in each group
    .rename("total_count")  # give that resulting Series a name
)

# 4b. Count “how many at‐risk rows” per date
at_risk_per_day = (
    df_risk[df_risk["risk_flag"]]  # filter to only at-risk rows
    .groupby("date")               # then group by date
    .size()                        # count rows per date
    .rename("at_risk_count")       # name that Series
)

# 4c. Merge into a single daily DataFrame
df_daily_counts = pd.concat(
    [total_per_day, at_risk_per_day], 
    axis=1            # concatenate as columns (not rows)
).fillna(0)           # if a date had zero at-risk, fill that missing value with 0

# 4d. Compute the proportion at risk
df_daily_counts["proportion_at_risk"] = (
    df_daily_counts["at_risk_count"] 
    / df_daily_counts["total_count"]
)

# 4e. Turn the date index back into a column
df_daily_counts = df_daily_counts.reset_index()

# 4f. Plot the time series with Plotly
fig_timeseries = px.line(
    df_daily_counts,
    x="date",
    y="proportion_at_risk",
    markers=True,               # draw a dot at each date point
    title="Daily Proportion of Grid Cells At Risk"
)

# 4g. Show everything
st.subheader("📈 Area-wide % at Risk Over Time")
st.plotly_chart(fig_timeseries, use_container_width=True)


st.markdown("<br><br>", unsafe_allow_html=True)
# HISTOGRAM
 # 5a. Select only rows where risk_score > 0
moisture_atrisk = moisture_today[moisture_today["risk_score"] > 0]

# 5b. Make histogram
fig_hist = px.histogram(
    moisture_atrisk,
    x="risk_score",
    nbins=30,
    title=f"Distribution of Risk Scores on {selected_date}"
)

fig_hist.update_layout(
    xaxis_title="Risk Score",
    yaxis_title="Count of Grid Cells"
)

st.plotly_chart(fig_hist, use_container_width=True)