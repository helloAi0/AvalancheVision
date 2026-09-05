"""Export service for serializing avalanche deposit detection results into GeoJSON, CSV, and Shapefile metadata packages."""

import csv
import io
import json
import logging
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional
import geopandas as gpd
from shapely.geometry import shape
from xml.sax.saxutils import escape
from backend.repositories.spatial_repository import spatial_repo

logger = logging.getLogger("AvalancheVision.ExportService")


class ExportService:
    def __init__(self):
        self.repo = spatial_repo

    def export_geojson_bytes(self) -> bytes:
        """Returns formatted GeoJSON bytes with WGS84 coordinates."""
        raw_data = self.repo._load_geojson()
        return json.dumps(raw_data, indent=2).encode("utf-8")

    def export_csv_bytes(self) -> bytes:
        """Flattens detection polygons and zonal statistics into CSV format."""
        raw_data = self.repo._load_geojson()
        features = raw_data.get("features", [])

        output = io.StringIO()
        fieldnames = [
            "detection_id",
            "risk_level",
            "confidence_score",
            "area_ha",
            "area_m2",
            "perimeter_m",
            "elevation_mean_m",
            "elevation_min_m",
            "elevation_max_m",
            "slope_mean_deg",
            "aspect_cardinal",
            "aspect_mean_deg",
            "delta_vv_db",
            "delta_vh_db",
            "era5_temperature_c",
            "era5_precip_mm",
            "era5_snow_depth_m",
            "acquisition_t1",
            "acquisition_t2",
            "model_version",
            "sensor",
            "region",
            "centroid_lon",
            "centroid_lat",
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for feat in features:
            props = dict(feat.get("properties", {}))
            geom = feat.get("geometry", {})
            coords = geom.get("coordinates", [[]])[0]
            
            if coords:
                c_lon = sum(pt[0] for pt in coords) / len(coords)
                c_lat = sum(pt[1] for pt in coords) / len(coords)
            else:
                c_lon, c_lat = 9.83, 46.80

            row = {
                "detection_id": props.get("detection_id", ""),
                "risk_level": props.get("risk_level", "High"),
                "confidence_score": props.get("confidence_score", 0.0),
                "area_ha": props.get("area_ha", 0.0),
                "area_m2": props.get("area_m2", 0.0),
                "perimeter_m": props.get("perimeter_m", 0.0),
                "elevation_mean_m": props.get("elevation_mean_m", 0.0),
                "elevation_min_m": props.get("elevation_min_m", 0.0),
                "elevation_max_m": props.get("elevation_max_m", 0.0),
                "slope_mean_deg": props.get("slope_mean_deg", 0.0),
                "aspect_cardinal": props.get("aspect_cardinal", ""),
                "aspect_mean_deg": props.get("aspect_mean_deg", 0.0),
                "delta_vv_db": props.get("delta_vv_db", 0.0),
                "delta_vh_db": props.get("delta_vh_db", 0.0),
                "era5_temperature_c": props.get("era5_temperature_c", 0.0),
                "era5_precip_mm": props.get("era5_precip_mm", 0.0),
                "era5_snow_depth_m": props.get("era5_snow_depth_m", 0.0),
                "acquisition_t1": props.get("acquisition_t1", ""),
                "acquisition_t2": props.get("acquisition_t2", ""),
                "model_version": props.get("model_version", ""),
                "sensor": props.get("sensor", ""),
                "region": props.get("region", ""),
                "centroid_lon": round(c_lon, 6),
                "centroid_lat": round(c_lat, 6),
            }
            writer.writerow(row)

        return output.getvalue().encode("utf-8")

    def export_kml_bytes(self) -> bytes:
        """Returns a standards-compatible KML document for GIS interchange."""
        raw_data = self.repo._load_geojson()
        placemarks = []
        for feature in raw_data.get("features", []):
            properties = feature.get("properties", {})
            name = properties.get("detection_id", "detection")
            geometry = shape(feature.get("geometry", {}))
            description = escape(" | ".join(f"{key}: {value}" for key, value in properties.items() if value is not None))
            polygons = list(geometry.geoms) if geometry.geom_type == "MultiPolygon" else [geometry]
            polygon_markup = []
            for polygon in polygons:
                rings = [polygon.exterior, *polygon.interiors]
                ring_markup = []
                for index, ring in enumerate(rings):
                    coordinates = " ".join(f"{lon},{lat},0" for lon, lat, *rest in ring.coords)
                    tag = "outerBoundaryIs" if index == 0 else "innerBoundaryIs"
                    ring_markup.append(f"<{tag}><LinearRing><coordinates>{coordinates}</coordinates></LinearRing></{tag}>")
                polygon_markup.append(f"<Polygon>{''.join(ring_markup)}</Polygon>")
            placemarks.append(f"<Placemark><name>{escape(str(name))}</name><description>{description}</description><MultiGeometry>{''.join(polygon_markup)}</MultiGeometry></Placemark>")
        document = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
            + "".join(placemarks)
            + "</Document></kml>"
        )
        return document.encode("utf-8")

    def export_shapefile_zip(self) -> bytes:
        """Writes a WGS84 ESRI Shapefile package and returns it as a ZIP archive."""
        raw_data = self.repo._load_geojson()
        field_mapping = {
            "detection_id": "det_id",
            "risk_level": "risk_level",
            "confidence_score": "conf_score",
            "area_ha": "area_ha",
            "area_m2": "area_m2",
            "perimeter_m": "perim_m",
            "elevation_mean_m": "elev_mean",
            "slope_mean_deg": "slope_deg",
            "aspect_cardinal": "aspect",
            "delta_vv_db": "delta_vv",
            "delta_vh_db": "delta_vh",
            "model_version": "model_ver",
            "sensor": "sensor",
            "region": "region",
        }
        rows = []
        for feature in raw_data.get("features", []):
            properties = {
                field_mapping[key]: value
                for key, value in feature.get("properties", {}).items()
                if key in field_mapping
            }
            properties["geometry"] = shape(feature["geometry"])
            rows.append(properties)
        frame = gpd.GeoDataFrame(rows, geometry="geometry", crs="EPSG:4326")
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "avalanche_detections"
            output_dir.mkdir()
            frame.to_file(output_dir / "detections.shp", driver="ESRI Shapefile")
            archive = io.BytesIO()
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for path in output_dir.iterdir():
                    zip_file.write(path, path.name)
                zip_file.writestr(
                    "FIELD_MAPPING.txt",
                    "Shapefile DBF field mapping (source -> field)\n"
                    + "\n".join(f"{source} -> {target}" for source, target in field_mapping.items()),
                )
            return archive.getvalue()

    def report_pdf_bytes(self) -> bytes:
        """Generates a compact ROI hazard report for operational review."""
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        stats = self.repo.get_summary_statistics()
        output = io.BytesIO()
        document = canvas.Canvas(output, pagesize=letter)
        width, height = letter
        document.setTitle("AvalancheVision ROI Hazard Report")
        document.setFont("Helvetica-Bold", 18)
        document.drawString(48, height - 64, "AvalancheVision ROI Hazard Report")
        document.setFont("Helvetica", 10)
        document.drawString(48, height - 84, f"Region: {stats.region}")
        document.drawString(48, height - 100, f"Model: {stats.model_version}")
        document.drawString(48, height - 116, f"Acquisition window: {stats.acquisition_window}")
        document.setFont("Helvetica-Bold", 12)
        document.drawString(48, height - 154, "Hazard summary")
        document.setFont("Helvetica", 10)
        values = [
            ("Total detections", stats.total_detections),
            ("Total area (ha)", stats.total_area_ha),
            ("Mean confidence", stats.mean_confidence),
            ("Mean slope (deg)", stats.mean_slope_deg),
            ("High risk detections", stats.high_risk_count),
            ("Very high risk detections", stats.very_high_risk_count),
        ]
        for index, (label, value) in enumerate(values):
            document.drawString(64, height - 178 - (index * 18), f"{label}: {value}")
        document.setFont("Helvetica-Oblique", 8)
        document.drawString(48, 40, "For scientific GIS review. Not a real-time avalanche warning product.")
        document.save()
        return output.getvalue()


export_service = ExportService()
