"""Core velocity-field abstractions for the toy ocean.

Every current model in :mod:`oceanfield` is a :class:`VelocityField`: given a
latitude, longitude and time it returns the eastward (``u``) and northward
(``v``) velocity in metres per second.  Two ready-made base classes cover the
common cases:

* :class:`StreamFunctionField` -- define a scalar streamfunction ``psi`` and the
  velocity is taken as its horizontal curl, which is divergence-free by
  construction (no spurious sources or sinks of water).
* :class:`CompositeField` -- add several fields together.

Keeping a single, narrow interface is what makes the project reusable: the drift
engine and the web API only ever depend on ``velocity()``, so the analytic toy
model used here can later be swapped for one backed by real gridded data without
touching anything downstream.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Sequence

import numpy as np

#: Mean Earth radius (metres).
R_EARTH = 6_371_000.0

#: Metres per degree of latitude (also per degree of longitude at the equator).
DEG2M = R_EARTH * np.pi / 180.0


def _broadcast(lat, lon):
    """Return ``lat``/``lon`` as float arrays broadcast to a common shape."""
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    return np.broadcast_arrays(lat, lon)


def wrap180(delta_lon):
    """Wrap a longitude difference into ``[-180, 180)`` degrees."""
    return (np.asarray(delta_lon, dtype=float) + 180.0) % 360.0 - 180.0


class VelocityField(ABC):
    """A time-dependent horizontal ocean velocity field on the globe."""

    @abstractmethod
    def velocity(self, lat, lon, t: float = 0.0):
        """Eastward/northward velocity ``(u, v)`` in m/s.

        ``lat`` and ``lon`` are in degrees and may be scalars or any
        broadcast-compatible numpy arrays; ``t`` is seconds.  The returned
        ``u`` and ``v`` have the broadcast shape of the inputs.
        """

    def speed(self, lat, lon, t: float = 0.0):
        """Convenience helper: the current speed ``|(u, v)|`` in m/s."""
        u, v = self.velocity(lat, lon, t)
        return np.hypot(u, v)


class StreamFunctionField(VelocityField):
    """Velocity derived as the curl of a scalar streamfunction ``psi``.

    On the sphere the horizontal, non-divergent velocity is

    ``u = -(1 / R) * d(psi)/d(lat)``  and
    ``v =  (1 / (R cos(lat))) * d(psi)/d(lon)``

    with ``psi`` in m^2/s.  Subclasses only implement :meth:`psi`; the
    derivatives are evaluated by a centred finite difference so any analytic
    streamfunction -- however asymmetric -- yields a clean, divergence-free
    flow without hand-derived gradients.
    """

    #: Finite-difference half-step for the curl, in degrees.
    step_deg = 0.02

    @abstractmethod
    def psi(self, lat, lon, t: float = 0.0):
        """The streamfunction in m^2/s at ``lat``/``lon`` (degrees) and ``t``."""

    def velocity(self, lat, lon, t: float = 0.0):
        lat, lon = _broadcast(lat, lon)
        h = self.step_deg

        dpsi_dnorth = (self.psi(lat + h, lon, t) - self.psi(lat - h, lon, t)) / (
            2.0 * h * DEG2M
        )
        cos_lat = np.maximum(np.cos(np.radians(lat)), 1e-3)
        dpsi_deast = (self.psi(lat, lon + h, t) - self.psi(lat, lon - h, t)) / (
            2.0 * h * DEG2M * cos_lat
        )

        u = -dpsi_dnorth
        v = dpsi_deast
        return u, v


class CompositeField(VelocityField):
    """The sum of several velocity fields."""

    def __init__(self, fields: Iterable[VelocityField]):
        self.fields: Sequence[VelocityField] = list(fields)

    def velocity(self, lat, lon, t: float = 0.0):
        lat, lon = _broadcast(lat, lon)
        u = np.zeros(lat.shape)
        v = np.zeros(lat.shape)
        for field in self.fields:
            fu, fv = field.velocity(lat, lon, t)
            u = u + fu
            v = v + fv
        return u, v
