"""Helpers for sampling a velocity field onto a regular lat/lon grid.

This is what visualisation and the (future) web API need: a dense grid of
``u``/``v`` values they can draw or stream to the browser.
"""

from __future__ import annotations

from typing import NamedTuple

import numpy as np

from .base import VelocityField


class FieldGrid(NamedTuple):
    """A velocity field sampled on a regular grid."""

    lons: np.ndarray  # 1-D, degrees
    lats: np.ndarray  # 1-D, degrees
    u: np.ndarray  # 2-D (lat, lon), m/s
    v: np.ndarray  # 2-D (lat, lon), m/s

    @property
    def speed(self) -> np.ndarray:
        """2-D current speed in m/s."""
        return np.hypot(self.u, self.v)


def sample_grid(
    field: VelocityField,
    resolution: float = 1.5,
    lat_limit: float = 80.0,
    t: float = 0.0,
) -> FieldGrid:
    """Sample ``field`` on a global regular grid.

    Args:
        field: Any velocity field.
        resolution: Grid spacing in degrees.
        lat_limit: Latitude is sampled over ``[-lat_limit, +lat_limit]`` to
            avoid the polar singularity.
        t: Time in seconds.
    """
    lons = np.arange(-180.0, 180.0 + resolution, resolution)
    lats = np.arange(-lat_limit, lat_limit + resolution, resolution)
    grid_lon, grid_lat = np.meshgrid(lons, lats)
    u, v = field.velocity(grid_lat, grid_lon, t)
    return FieldGrid(lons=lons, lats=lats, u=u, v=v)
