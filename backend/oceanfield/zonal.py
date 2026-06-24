"""Zonal (east-west) current bands.

Some of the ocean's biggest features are not closed gyres but latitude bands:
the westward equatorial currents either side of a thin eastward counter-current,
and the mighty Antarctic Circumpolar Current that runs unbroken around the
Southern Ocean.  These are modelled directly as a sum of Gaussian-in-latitude
zonal jets.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np

from .base import VelocityField, _broadcast


@dataclass(frozen=True)
class ZonalBand:
    """A purely east-west current centred on a latitude.

    Attributes:
        name: Human-readable label.
        lat0: Centre latitude in degrees.
        half_width: Gaussian half-width in degrees.
        speed: Peak eastward speed in m/s (negative is westward).
    """

    name: str
    lat0: float
    half_width: float
    speed: float


class ZonalCurrents(VelocityField):
    """A set of east-west current bands; contributes only to ``u``."""

    def __init__(self, bands: List[ZonalBand]):
        self.bands = list(bands)

    def velocity(self, lat, lon, t: float = 0.0):
        lat, lon = _broadcast(lat, lon)
        u = np.zeros(lat.shape)
        for b in self.bands:
            u = u + b.speed * np.exp(-0.5 * ((lat - b.lat0) / b.half_width) ** 2)
        v = np.zeros(lat.shape)
        return u, v


def default_bands() -> List[ZonalBand]:
    """Equatorial current system plus the Antarctic Circumpolar Current."""
    return [
        ZonalBand("North Equatorial Current", 17, 5, -0.25),
        ZonalBand("Equatorial Counter Current", 6, 2.5, +0.55),
        ZonalBand("South Equatorial Current", -3, 6, -0.35),
        ZonalBand("Antarctic Circumpolar Current", -55, 9, +0.90),
    ]
