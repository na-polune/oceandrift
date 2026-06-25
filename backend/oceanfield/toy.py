"""The assembled toy ocean.

:class:`ToyOceanField` is the headline object of the package: it adds the gyres,
the zonal current bands and the mesoscale eddies together and zeroes the result
over land.  It is a plain :class:`~oceanfield.base.VelocityField`, so it plugs
straight into the drift engine and the web API.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from .base import CompositeField, VelocityField, _broadcast
from .eddies import CurlNoiseField
from .gyres import Gyre, GyreField, default_gyres
from .landmask import LandMask
from .zonal import ZonalBand, ZonalCurrents, default_bands


class ToyOceanField(VelocityField):
    """A plausible, fully-offline model of Earth's surface currents.

    Args:
        gyres: Override the default list of :class:`~oceanfield.gyres.Gyre`.
        bands: Override the default list of
            :class:`~oceanfield.zonal.ZonalBand`.
        eddies: Include mesoscale curl-noise eddies.
        mask_land: Zero the velocity over land.
        seed: Seed for the eddy field.
    """

    def __init__(
        self,
        gyres: Optional[List[Gyre]] = None,
        bands: Optional[List[ZonalBand]] = None,
        eddies: bool = True,
        mask_land: bool = True,
        seed: int = 0,
    ):
        parts: List[VelocityField] = [
            GyreField(default_gyres() if gyres is None else gyres),
            ZonalCurrents(default_bands() if bands is None else bands),
        ]
        if eddies:
            parts.append(CurlNoiseField(seed=seed))

        self._field = CompositeField(parts)
        self._mask = LandMask() if mask_land else None

    def velocity(self, lat, lon, t: float = 0.0):
        lat, lon = _broadcast(lat, lon)
        u, v = self._field.velocity(lat, lon, t)
        if self._mask is not None:
            ocean = self._mask.is_ocean(lat, lon)
            u = np.where(ocean, u, 0.0)
            v = np.where(ocean, v, 0.0)
        return u, v

    def is_land(self, lat, lon):
        """Boolean array: ``True`` where ``(lat, lon)`` is over land.

        Lets a drift engine beach particles without knowing how the mask works.
        Returns all-``False`` when land masking is disabled.
        """
        lat, lon = _broadcast(lat, lon)
        if self._mask is None:
            return np.zeros(lat.shape, dtype=bool)
        return self._mask.is_land(lat, lon)
