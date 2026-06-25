"""Helpers for seeding particles.

Small conveniences for placing the initial cloud of drifters that the
:class:`~oceandrift.engine.DriftEngine` will track.
"""

from __future__ import annotations

import numpy as np

#: Approximate kilometres per degree of latitude.
_KM_PER_DEG = 111.195


def seed_disk(lat0: float, lon0: float, radius_km: float, n: int, seed: int = 0):
    """Random particles uniformly inside a disk around ``(lat0, lon0)``.

    Returns ``(lat, lon)`` arrays of length ``n`` (degrees).  The radius is
    converted to degrees with a local flat-Earth approximation, which is plenty
    accurate for the modest patch sizes used when releasing drifters.
    """
    rng = np.random.default_rng(seed)
    radius = radius_km * np.sqrt(rng.uniform(0.0, 1.0, n))  # uniform area
    angle = rng.uniform(0.0, 2.0 * np.pi, n)
    dnorth_km = radius * np.sin(angle)
    deast_km = radius * np.cos(angle)
    lat = lat0 + dnorth_km / _KM_PER_DEG
    lon = lon0 + deast_km / (_KM_PER_DEG * np.cos(np.radians(lat0)))
    return lat, lon


def seed_grid(lat0: float, lon0: float, half_deg: float, n_side: int):
    """A square ``n_side`` x ``n_side`` grid of particles centred on a point."""
    lats = np.linspace(lat0 - half_deg, lat0 + half_deg, n_side)
    lons = np.linspace(lon0 - half_deg, lon0 + half_deg, n_side)
    grid_lon, grid_lat = np.meshgrid(lons, lats)
    return grid_lat.ravel(), grid_lon.ravel()
