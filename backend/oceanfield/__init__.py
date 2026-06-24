"""oceanfield -- an analytic, offline toy model of Earth's surface ocean currents.

The package builds a plausible global current field from a few interpretable
pieces -- gyres, zonal current bands and mesoscale eddies -- masked to the
ocean.  Everything is exposed through the single :class:`VelocityField`
interface so it can drive a drift engine, a web API or a plot unchanged.

Example:
    >>> from oceanfield import ToyOceanField
    >>> ocean = ToyOceanField()
    >>> u, v = ocean.velocity(40.0, -50.0)  # Gulf Stream region
"""

from __future__ import annotations

from .base import (
    CompositeField,
    DEG2M,
    R_EARTH,
    StreamFunctionField,
    VelocityField,
    wrap180,
)
from .eddies import CurlNoiseField
from .grid import FieldGrid, sample_grid
from .gyres import Gyre, GyreField, default_gyres
from .landmask import LandMask
from .toy import ToyOceanField
from .zonal import ZonalBand, ZonalCurrents, default_bands

__version__ = "0.1.0"

__all__ = [
    "VelocityField",
    "StreamFunctionField",
    "CompositeField",
    "ToyOceanField",
    "GyreField",
    "Gyre",
    "default_gyres",
    "ZonalCurrents",
    "ZonalBand",
    "default_bands",
    "CurlNoiseField",
    "LandMask",
    "FieldGrid",
    "sample_grid",
    "R_EARTH",
    "DEG2M",
    "wrap180",
    "__version__",
]
