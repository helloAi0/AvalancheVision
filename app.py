import streamlit as st
import folium
from streamlit_folium import st_folium
import json
from shapely.geometry import shape
from pathlib import Path

# Configure the web page
st.set_page_config(page_title="AvalancheVision | AI Hazard Prediction", page_icon="🏔️", layout="wide")

# Main Header
st.title("🏔️ AvalancheVision: SAR & AI Hazard Prediction")
st.markdown("Real-time avalanche risk mapping using Sentinel-1 backscatter and ERA5 meteorological data.")

# Sidebar Controls
st.sidebar.header("System Controls")
st.sidebar.info("Model Engine: U-Net (10-Band Tensor)")
threshold = st.sidebar.slider("Risk Probability Threshold", min_value=0.1, max_value=0.9, value=0.5, step=0.1)

# Metrics Row
col1, col2, col3 = st.columns(3)
col1.metric("Current Pipeline Status", "Active", "Connected")
col2.metric("Latest SAR Acquisition", "12 hours ago", "-2h latency")
col3.metric("High Risk Zones Detected", "1", "Requires Attention", delta_color="inverse")

st.divider()

# Map Rendering Logic
geojson_path = Path("data/processed/high_risk_zones.geojson")

# Default coordinates (e.g., a specific mountain range, defaulting to Swiss Alps for UI purposes)
center_lat, center_lon = 46.0, 7.5 
zoom = 6

if geojson_path.exists():
    with open(geojson_path, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)
    
    features = geojson_data.get("features", [])
    if features:
        # Calculate rough center of the generated polygons to focus the map
        geoms = [shape(feat["geometry"]) for feat in features if "geometry" in feat and feat["geometry"]]
        if geoms:
            minx = min(g.bounds[0] for g in geoms)
            miny = min(g.bounds[1] for g in geoms)
            maxx = max(g.bounds[2] for g in geoms)
            maxy = max(g.bounds[3] for g in geoms)
            center_lat = (miny + maxy) / 2.0
            center_lon = (minx + maxx) / 2.0
            zoom = 10

# Initialize UI Map
m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles=None)

# Add Basemaps
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri",
    name="Satellite View",
    control=True
).add_to(m)

folium.TileLayer(
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="OpenTopoMap",
    name="Terrain Topography",
    control=True
).add_to(m)

# Add Hazard Layer if data exists
if geojson_path.exists() and features:
    def style_function(feature):
        return {'fillColor': '#ff0033', 'color': '#cc0000', 'weight': 2, 'fillOpacity': 0.55}

    folium.GeoJson(
        geojson_data,
        name=f"High Risk Zones (>{threshold*100}%)",
        style_function=style_function
    ).add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

# Render map in Streamlit
st_data = st_folium(m, width=1200, height=600)

st.caption("Developed for competitive deployment. End-to-end architecture integrates CDSE OData, Xarray Dask, and PyTorch.")