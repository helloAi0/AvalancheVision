import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check_endpoint():
    """Verify system diagnostics and health readiness probe."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"].lower() in ["healthy", "degraded"]
    if data["status"].lower() == "degraded":
        assert data["database_status"] == "UNAVAILABLE"

def test_detections_geojson_schema():
    """Verify GeoJSON streaming endpoint returns valid FeatureCollection format."""
    response = client.get("/api/v1/detections/geojson")
    assert response.status_code == 200
    geojson = response.json()
    
    assert geojson["type"] == "FeatureCollection"
    assert "features" in geojson
    if len(geojson["features"]) > 0:
        first_feature = geojson["features"][0]
        assert first_feature["type"] == "Feature"
        assert "geometry" in first_feature
        assert "properties" in first_feature

def test_response_includes_request_id():
    response = client.get("/api/v1/health", headers={"X-Request-ID": "test-request-001"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-001"

def test_cors_rejects_unknown_origin():
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert "access-control-allow-origin" not in response.headers

def test_raster_metadata_uses_registered_artifact():
    response = client.get("/api/v1/rasters/risk-probability")

    assert response.status_code == 200
    metadata = response.json()
    assert metadata["raster_id"] == "risk-probability"
    assert metadata["band_count"] >= 1
    assert "path" not in metadata

def test_unknown_raster_is_rejected():
    response = client.get("/api/v1/rasters/not-registered")

    assert response.status_code == 404

def test_raster_window_returns_png_for_real_artifact():
    metadata = client.get("/api/v1/rasters/risk-probability").json()
    left, bottom, right, top = metadata["bounds"]
    response = client.get(
        "/api/v1/rasters/window/risk-probability",
        params={"bbox": f"{left},{bottom},{right},{top}", "width": 64, "height": 64},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(b"\x89PNG")

def test_profile_samples_registered_raster():
    metadata = client.get("/api/v1/rasters/risk-probability").json()
    left, bottom, right, top = metadata["bounds_wgs84"]
    response = client.post("/api/v1/analysis/profile", json={
        "raster_id": "risk-probability",
        "start": [left, bottom],
        "end": [right, top],
        "samples": 8,
    })

    assert response.status_code == 200
    profile = response.json()
    assert profile["sample_count"] == 8
    assert len(profile["points"]) == 8
    assert profile["points"][0]["distance_m"] == 0