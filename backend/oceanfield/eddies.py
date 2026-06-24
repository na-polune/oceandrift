"""Mesoscale eddies via curl noise.

Real ocean currents are full of swirling eddies on top of the steady large-scale
flow.  We fake them with "curl noise": a smooth pseudo-random streamfunction
built from a sum of sinusoids.  Because the velocity is the curl of that
streamfunction (see :class:`~oceanfield.base.StreamFunctionField`), the eddies
are automatically divergence-free and slowly evolve in time.

The field is fully analytic and seeded, so it is deterministic, periodic in
longitude, and needs no external data.
"""

from __future__ import annotations

import numpy as np

from .base import StreamFunctionField


class CurlNoiseField(StreamFunctionField):
    """A smooth, time-evolving random streamfunction (curl noise).

    Args:
        amplitude: Overall streamfunction strength in m^2/s; sets the typical
            eddy speed.
        n_modes: Number of sinusoidal modes summed together.
        evolution_days: Rough timescale over which the eddy pattern drifts.
        seed: Random seed for reproducibility.
    """

    def __init__(
        self,
        amplitude: float = 1.4e4,
        n_modes: int = 48,
        evolution_days: float = 30.0,
        seed: int = 0,
    ):
        rng = np.random.default_rng(seed)
        self.amplitude = amplitude

        # Integer zonal wavenumbers keep the field periodic in longitude.
        # Modest wavenumbers keep the eddies large and gentle rather than noisy.
        self.kx = rng.integers(2, 14, size=n_modes).astype(float)
        self.ky = rng.uniform(2.0, 11.0, size=n_modes)
        self.phase = rng.uniform(0.0, 2.0 * np.pi, size=n_modes)
        # Steep red spectrum (~1/k^2 in the streamfunction) so the velocity is
        # dominated by the large scales and stays smooth.
        self.weight = 1.0 / (self.kx**2 + self.ky**2)
        self.weight /= np.sqrt(np.mean(self.weight**2))
        # Slow temporal evolution, a few radians over `evolution_days`.
        omega_scale = 2.0 * np.pi / (evolution_days * 86_400.0)
        self.omega = rng.normal(0.0, omega_scale, size=n_modes)

    def psi(self, lat, lon, t: float = 0.0):
        lat = np.asarray(lat, dtype=float)
        lon = np.asarray(lon, dtype=float)
        # Map lon -> [0, 1) over 360 deg and lat -> [-0.5, 0.5] over 180 deg.
        u = lon[..., np.newaxis] / 360.0
        w = lat[..., np.newaxis] / 180.0
        phase = (
            2.0 * np.pi * (self.kx * u + self.ky * w)
            + self.phase
            + self.omega * t
        )
        return self.amplitude * np.sum(self.weight * np.sin(phase), axis=-1)
