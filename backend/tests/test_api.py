"""Endpoint tests for the oceandrift API, via FastAPI's TestClient."""

import numpy as np
import pytest
from fastapi.testclient import TestClient

from oceanapi import create_app


@pytest.fixture(scope="module")
def client():
    return TestClient(create_app())


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_field_shape_and_payload(client):
    r = client.get("/field", params={"resolution": 5.0})
    assert r.status_code == 200
    body = r.json()
    assert len(body["u"]) == body["width"] * body["height"]
    assert len(body["v"]) == body["width"] * body["height"]
    assert body["bbox"][0] == -180.0
    # Some water is moving and nothing is absurd.
    assert max(abs(x) for x in body["u_range"]) > 0.0
    assert max(abs(x) for x in body["u_range"]) < 5.0


def test_field_evolves_with_time(client):
    a = client.get("/field", params={"resolution": 5.0, "time_days": 0}).json()
    b = client.get("/field", params={"resolution": 5.0, "time_days": 40}).json()
    # The eddies drift, so the fields differ.
    assert not np.allclose(a["u"], b["u"])


def test_drift_geojson_from_seeds(client):
    r = client.post(
        "/drift",
        json={
            "seeds": [{"lat": 35, "lon": -45}, {"lat": -30, "lon": -120}],
            "duration_days": 30,
        },
    )
    assert r.status_code == 200
    fc = r.json()
    assert fc["type"] == "FeatureCollection"
    assert len(fc["features"]) == 2
    geom = fc["features"][0]["geometry"]
    assert geom["type"] in ("LineString", "MultiLineString", "Point")


def test_drift_patch_count(client):
    r = client.post(
        "/drift",
        json={
            "patch": {"lat": 36, "lon": -55, "radius_km": 60, "count": 25},
            "duration_days": 20,
            "max_points": 100,
        },
    )
    assert r.status_code == 200
    assert len(r.json()["features"]) == 25


def test_drift_czml(client):
    r = client.post(
        "/drift",
        json={
            "seeds": [{"lat": 35, "lon": -45}],
            "duration_days": 20,
            "format": "czml",
        },
    )
    assert r.status_code == 200
    packets = r.json()
    assert isinstance(packets, list)
    assert packets[0]["id"] == "document"
    assert "clock" in packets[0]
    assert packets[1]["id"] == "drifter-0"
    assert "cartographicDegrees" in packets[1]["position"]


def test_drift_requires_seeds(client):
    r = client.post("/drift", json={"duration_days": 10})
    assert r.status_code == 422  # validation error
