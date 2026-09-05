"""FastAPI endpoints for agency GIS and operational report exports."""

from typing import Literal
from fastapi import APIRouter, Query, Response
from backend.services.export_service import export_service

router = APIRouter(prefix="/export", tags=["Data Export"])


@router.get("/detections")
def export_detections(
    format: Literal["geojson", "kml", "shapefile"] = Query(default="geojson")
):
    """Exports detection geometries in a common agency GIS interchange format."""
    exporters = {
        "geojson": (export_service.export_geojson_bytes, "application/geo+json", "detections.geojson"),
        "kml": (export_service.export_kml_bytes, "application/vnd.google-earth.kml+xml", "detections.kml"),
        "shapefile": (export_service.export_shapefile_zip, "application/zip", "detections_shapefile.zip"),
    }
    exporter, media_type, filename = exporters[format]
    return Response(
        content=exporter(),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/report.pdf")
def export_report_pdf():
    """Downloads a PDF summary of the active ROI hazard statistics and metadata."""
    return Response(
        content=export_service.report_pdf_bytes(),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="avalanchevision_roi_report.pdf"'},
    )


@router.get("/geojson")
def export_geojson():
    """Downloads full WGS84 GeoJSON FeatureCollection with all per-polygon scientific metrics."""
    data = export_service.export_geojson_bytes()
    return Response(
        content=data,
        media_type="application/geo+json",
        headers={"Content-Disposition": 'attachment; filename="avalanche_deposit_detections_wgs84.geojson"'}
    )


@router.get("/csv")
def export_csv():
    """Downloads tabular CSV summary of all detections with spatial centroids and physical attributes."""
    data = export_service.export_csv_bytes()
    return Response(
        content=data,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="avalanche_deposit_telemetry.csv"'}
    )
