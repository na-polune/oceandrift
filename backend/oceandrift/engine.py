"""Lagrangian drift engine.

Given any :class:`~oceanfield.base.VelocityField`, :class:`DriftEngine` advances
a set of particles through it and records their trajectories.  Particles are
integrated with a 4th-order Runge-Kutta scheme on the sphere; they optionally
spread by a random-walk (eddy diffusion) and beach when they hit land.

The engine depends only on the ``velocity()`` interface, so it works unchanged
whether the field is the offline toy ocean or a future data-backed one.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from typing import Callable, Optional

import numpy as np

from oceanfield.base import DEG2M, VelocityField, wrap180

#: Latitude is clamped just short of the poles to avoid the 1/cos(lat)
#: singularity in the longitude update.
_MAX_LAT = 89.9

#: Floor on cos(lat) so high-latitude longitude rates stay finite.
_MIN_COS = 1e-3

# A drift "day" in seconds; handy default unit for durations.
DAY = 86_400.0


def _cos_lat(lat):
    return np.maximum(np.cos(np.radians(lat)), _MIN_COS)


@dataclass
class DriftConfig:
    """Parameters for a drift run.

    Attributes:
        dt: Integration time step in seconds.
        duration: Total simulated time in seconds.
        diffusivity: Horizontal eddy diffusivity in m^2/s for the random walk
            (``0`` disables diffusion, giving deterministic trajectories).
        t0: Start time in seconds, passed through to the (time-dependent) field.
        seed: Random seed for the diffusion noise.
    """

    dt: float = 3 * 3600.0
    duration: float = 120 * DAY
    diffusivity: float = 0.0
    t0: float = 0.0
    seed: int = 0

    @property
    def n_steps(self) -> int:
        return int(round(self.duration / self.dt))


@dataclass
class DriftResult:
    """The output of a drift run.

    ``lat`` and ``lon`` have shape ``(n_steps + 1, n_particles)``: row 0 is the
    seeding position and each subsequent row is one time step later.
    """

    times: np.ndarray  # (T+1,) seconds
    lat: np.ndarray  # (T+1, N) degrees
    lon: np.ndarray  # (T+1, N) degrees
    beached: np.ndarray  # (N,) bool

    @property
    def days(self) -> np.ndarray:
        return self.times / DAY

    @property
    def n_particles(self) -> int:
        return self.lat.shape[1]

    @property
    def n_steps(self) -> int:
        return self.lat.shape[0] - 1

    def final_position(self):
        """``(lat, lon)`` of every particle at the end of the run."""
        return self.lat[-1], self.lon[-1]


class DriftEngine:
    """Integrates particles through a velocity field.

    Args:
        field: The velocity field to drift through.
        is_land: Optional ``is_land(lat, lon) -> bool array`` callable; when
            given, particles that step onto land are beached.  Defaults to the
            field's own ``is_land`` method if it has one.
    """

    def __init__(
        self,
        field: VelocityField,
        is_land: Optional[Callable] = None,
    ):
        self.field = field
        if is_land is None:
            is_land = getattr(field, "is_land", None)
        self.is_land = is_land

    # -- derivatives & integration ------------------------------------------

    def _deriv(self, lat, lon, t):
        """Rates of change of latitude/longitude in degrees per second."""
        u, v = self.field.velocity(lat, lon, t)
        dlat = v / DEG2M
        dlon = u / (DEG2M * _cos_lat(lat))
        return dlat, dlon

    def _rk4_step(self, lat, lon, t, dt):
        k1_lat, k1_lon = self._deriv(lat, lon, t)
        k2_lat, k2_lon = self._deriv(
            lat + 0.5 * dt * k1_lat, lon + 0.5 * dt * k1_lon, t + 0.5 * dt
        )
        k3_lat, k3_lon = self._deriv(
            lat + 0.5 * dt * k2_lat, lon + 0.5 * dt * k2_lon, t + 0.5 * dt
        )
        k4_lat, k4_lon = self._deriv(
            lat + dt * k3_lat, lon + dt * k3_lon, t + dt
        )
        new_lat = lat + dt / 6.0 * (k1_lat + 2 * k2_lat + 2 * k3_lat + k4_lat)
        new_lon = lon + dt / 6.0 * (k1_lon + 2 * k2_lon + 2 * k3_lon + k4_lon)
        return new_lat, new_lon

    # -- public API ----------------------------------------------------------

    def run(self, lat0, lon0, config: Optional[DriftConfig] = None) -> DriftResult:
        """Drift particles seeded at ``lat0``/``lon0`` (degrees)."""
        config = config or DriftConfig()
        lat = np.asarray(lat0, dtype=float).ravel().copy()
        lon = wrap180(np.asarray(lon0, dtype=float).ravel())
        n = lat.size
        steps = config.n_steps

        rng = np.random.default_rng(config.seed)
        sigma = (
            np.sqrt(2.0 * config.diffusivity * config.dt)
            if config.diffusivity > 0.0
            else 0.0
        )

        beached = np.zeros(n, dtype=bool)
        if self.is_land is not None:
            beached = np.asarray(self.is_land(lat, lon), dtype=bool).copy()

        lat_hist = np.empty((steps + 1, n))
        lon_hist = np.empty((steps + 1, n))
        times = np.empty(steps + 1)
        lat_hist[0], lon_hist[0], times[0] = lat, lon, config.t0

        t = config.t0
        for i in range(1, steps + 1):
            active = ~beached

            new_lat, new_lon = self._rk4_step(lat, lon, t, config.dt)

            if sigma > 0.0:
                new_lat = new_lat + rng.normal(0.0, sigma, n) / DEG2M
                new_lon = new_lon + rng.normal(0.0, sigma, n) / (DEG2M * _cos_lat(lat))

            new_lat = np.clip(new_lat, -_MAX_LAT, _MAX_LAT)
            new_lon = wrap180(new_lon)

            if self.is_land is not None:
                hit = np.asarray(self.is_land(new_lat, new_lon), dtype=bool)
            else:
                hit = np.zeros(n, dtype=bool)

            moving = active & ~hit
            lat = np.where(moving, new_lat, lat)
            lon = np.where(moving, new_lon, lon)
            beached = beached | (active & hit)

            t += config.dt
            lat_hist[i], lon_hist[i], times[i] = lat, lon, t

        return DriftResult(times=times, lat=lat_hist, lon=lon_hist, beached=beached)
