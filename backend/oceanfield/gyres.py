"""The great subtropical and subpolar gyres.

Each gyre is a smooth streamfunction "blob".  Summing a handful of them, with
the rotation sense set by the sign of the amplitude, reproduces the large-scale
pattern of the real surface ocean: clockwise subtropical gyres in the northern
hemisphere, anticlockwise ones in the south, and the cyclonic subpolar gyres.

A western-intensification term narrows the streamfunction on the western side of
each basin, which is what produces the fast, narrow boundary currents the ocean
is famous for -- the Gulf Stream, Kuroshio, Agulhas and friends.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np

from .base import StreamFunctionField, wrap180


@dataclass(frozen=True)
class Gyre:
    """A single rotating gyre.

    Attributes:
        name: Human-readable label (e.g. ``"North Atlantic"``).
        lat0, lon0: Centre of the gyre in degrees.
        half_width_lon, half_width_lat: Gaussian half-widths in degrees.
        amplitude: Streamfunction strength in m^2/s.  Positive spins the gyre
            clockwise, negative anticlockwise.
        western_intensification: ``0``-``1`` factor; how strongly the flow is
            compressed against the western boundary of the basin.
    """

    name: str
    lat0: float
    lon0: float
    half_width_lon: float
    half_width_lat: float
    amplitude: float
    western_intensification: float = 0.0


class GyreField(StreamFunctionField):
    """Streamfunction made of the sum of a list of :class:`Gyre` blobs."""

    def __init__(self, gyres: List[Gyre]):
        self.gyres = list(gyres)

    def psi(self, lat, lon, t: float = 0.0):
        lat = np.asarray(lat, dtype=float)
        lon = np.asarray(lon, dtype=float)
        total = np.zeros(np.broadcast(lat, lon).shape)

        for g in self.gyres:
            dlon = wrap180(lon - g.lon0)
            dlat = lat - g.lat0

            half_lon = g.half_width_lon
            if g.western_intensification > 0.0:
                # Smoothly squeeze the zonal scale on the western side
                # (dlon < 0), steepening the gradient there into a boundary jet.
                west = 0.5 * (1.0 - np.tanh(dlon / (0.4 * g.half_width_lon)))
                half_lon = g.half_width_lon * (
                    1.0 - 0.65 * g.western_intensification * west
                )

            x = dlon / half_lon
            y = dlat / g.half_width_lat
            total = total + g.amplitude * np.exp(-0.5 * (x * x + y * y))

        return total


def default_gyres(amplitude: float = 1.8e6) -> List[Gyre]:
    """The canonical set of world-ocean gyres.

    ``amplitude`` scales every gyre together so the overall current speed can be
    tuned from one place.  Subpolar gyres are given the opposite sign (cyclonic)
    and a fraction of the subtropical strength.
    """
    a = amplitude
    return [
        # --- Northern subtropical (clockwise, +) with western boundary jets ---
        Gyre("North Atlantic", 30, -45, 34, 17, +a, western_intensification=0.85),
        Gyre("North Pacific", 28, 180, 55, 18, +a, western_intensification=0.85),
        # --- Southern subtropical (anticlockwise, -) ---
        Gyre("South Atlantic", -28, -20, 28, 15, -a, western_intensification=0.7),
        Gyre("South Pacific", -30, -130, 55, 18, -a, western_intensification=0.6),
        Gyre("South Indian", -30, 75, 34, 16, -a, western_intensification=0.75),
        # --- Subpolar (cyclonic, opposite sign, weaker) ---
        Gyre("North Atlantic subpolar", 57, -35, 22, 11, -0.55 * a),
        Gyre("North Pacific subpolar", 54, -160, 28, 11, -0.55 * a),
    ]
