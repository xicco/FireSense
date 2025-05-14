# FireSense 🔥🌱  
*A soil moisture dashboard for wildfire risk detection*

## 📌 Overview

**FireSense** is a lightweight monitoring system that tracks soil moisture using satellite-based remote sensing data. The goal is to support wildfire prevention efforts by identifying high-risk dry zones in forests and natural areas.

This project pulls and processes data from the [Copernicus Climate Data Store (CDS)](https://cds.climate.copernicus.eu/) using the `cdsapi`, and visualizes trends through an interactive dashboard and map interface.

---

## 🌍 Features

- 📊 Daily, 10-day, and monthly averages of soil moisture
- 🛰️ Data from passive + active satellite sensors (1978–present)
- 🗺️ Interactive map view of monitored zones
- 📈 Real-time dashboard for moisture trends
- 🕒 Seasonal awareness for fire risk insights

---

## 🧰 Tech Stack

- Python 3.x  
- `cdsapi` – Copernicus data retrieval  
- `xarray`, `pandas` – data processing  
- `Dash` – interactive dashboard  
- `Plotly` – visualization  
- `GeoPandas`, `folium` – map overlays (optional)

---

## 📦 Folder Structure

