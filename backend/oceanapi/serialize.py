"""Convert drift results into web-friendly formats.

* GeoJSON -- a ``FeatureCollection`` of trajectories, handy for any map and for
  inspection.  Tracks are split at the +/-180 seam so they don't streak across
  the map.
* CZML -- Cesium's time-dynamic format, so drifters animate on the globe's clock
  in the front end (M5).
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

import numpy as np


def stride_for(n_rows: int, max_points: int) -> int:
    """Step size that keeps at most ``max_points`` samples along a track."""
    return max(1, math.ceil(n_rows / max_points))


def _parse_iso(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _split_segments(lons, lats):
    """Split a track into segments at antimeridian crossings."""
    segments = []
    current = [[round(float(lons[0]), 4), round(float(lats[0]), 4)]]
    for i in range(1, len(lons)):
        if abs(float(lons[i]) - float(lons[i - 1])) > 180.0:
            segments.append(current)
            current = []
        current.append([round(float(lons[i]), 4), round(float(lats[i]), 4)])
    segments.append(current)
    return [s for s in segments if len(s) >= 2]


def to_geojson(result, stride: int) -> dict:
    """A ``FeatureCollection`` with one feature per particle."""
    features = []
    for p in range(result.n_particles):
        lons = result.lon[::stride, p]
        lats = result.lat[::stride, p]
        segments = _split_segments(lons, lats)

        if not segments:
            geometry = {
                "type": "Point",
                "coordinates": [round(float(lons[0]), 4), round(float(lats[0]), 4)],
            }
        elif len(segments) == 1:
            geometry = {"type": "LineString", "coordinates": segments[0]}
        else:
            geometry = {"type": "MultiLineString", "coordinates": segments}

        features.append(
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": {"id": p, "beached": bool(result.beached[p])},
            }
        )
    return {"type": "FeatureCollection", "features": features}


def to_czml(result, start_time: str, dt_seconds: float, stride: int) -> list:
    """A CZML document: a clock packet plus one moving point per particle."""
    epoch = _parse_iso(start_time)
    stop = epoch + timedelta(seconds=float(result.times[-1]))
    interval = f"{_iso(epoch)}/{_iso(stop)}"

    document = {
        "id": "document",
        "name": "oceandrift",
        "version": "1.0",
        "clock": {
            "interval": interval,
            "currentTime": _iso(epoch),
            "multiplier": int(max(dt_seconds * 6.0, 3600.0)),
            "range": "LOOP_STOP",
        },
    }
    packets = [document]

    rows = range(0, result.lat.shape[0], stride)
    for p in range(result.n_particles):
        cartographic = []
        for k in rows:
            cartographic += [
                float(result.times[k]),
                round(float(result.lon[k, p]), 4),
                round(float(result.lat[k, p]), 4),
                0.0,
            ]
        packets.append(
            {
                "id": f"drifter-{p}",
                "availability": interval,
                "position": {
                    "epoch": _iso(epoch),
                    "cartographicDegrees": cartographic,
                },
                "point": {"pixelSize": 7, "color": {"rgba": [255, 140, 0, 220]}},
                "path": {
                    "leadTime": 0,
                    "trailTime": 3 * 86400,
                    "width": 2,
                    "resolution": 3600,
                    "material": {
                        "solidColor": {"color": {"rgba": [255, 160, 0, 150]}}
                    },
                },
            }
        )
    return packets
