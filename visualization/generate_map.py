import logging
import json
import folium
from pathlib import Path
from shapely.geometry import shape

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def build_interactive_map(geojson_path: Path, output_html: Path):
    if not geojson_path.exists():
        logger.error(f"Vector file not found at {geojson_path}")
        return

    logger.info(f"Loading vector risk zones from {geojson_path.name}")
    with open(geojson_path, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    features = geojson_data.get("features", [])
    if not features:
        logger.warning("No risk polygons found in GeoJSON file.")
        return

    # Extract geometries to compute spatial bounds without Fiona
    geoms = [shape(feat["geometry"]) for feat in features if "geometry" in feat and feat["geometry"]]
    if not geoms:
        logger.warning("No valid geometries found to render.")
        return

    # Bounding box: [minx, miny, maxx, maxy]
    minx = min(g.bounds[0] for g in geoms)
    miny = min(g.bounds[1] for g in geoms)
    maxx = max(g.bounds[2] for g in geoms)
    maxy = max(g.bounds[3] for g in geoms)

    center_lat = (miny + maxy) / 2.0
    center_lon = (minx + maxx) / 2.0

    # Initialize Folium Map centered over ROI
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles=None
    )

    # Add Esri World Imagery Basemap (Satellite)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite View",
        overlay=False,
        control=True
    ).add_to(m)

    # Add OpenTopoMap Basemap (Terrain Topography)
    folium.TileLayer(
        tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        attr="OpenTopoMap",
        name="Terrain Topography",
        overlay=False,
        control=True
    ).add_to(m)

    # Style function for red high-risk hazard polygons
    def style_function(feature):
        return {
            'fillColor': '#ff0033',
            'color': '#cc0000',
            'weight': 2,
            'fillOpacity': 0.55
        }

    # Overlay Hazard Vectors directly from parsed GeoJSON dict
    risk_layer = folium.GeoJson(
        geojson_data,
        name="High Avalanche Risk Zones (>50%)",
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=['risk_level'], aliases=['Hazard Level:'])
    )
    risk_layer.add_to(m)

    # Layer Control toggle
    folium.LayerControl(collapsed=False).add_to(m)

    output_html.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(output_html))
    logger.info(f"Interactive Web Map saved successfully to {output_html}")

if __name__ == "__main__":
    geojson_file = Path("data/processed/high_risk_zones.geojson")
    html_file = Path("data/processed/avalanche_risk_map.html")
    
    build_interactive_map(geojson_file, html_file)