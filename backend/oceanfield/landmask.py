"""Land/sea mask.

Currents only exist over water, and a drifting object should beach when it hits
a coast.  We use :mod:`global_land_mask`, which bundles a ~1 km global land/sea
grid -- so the mask works fully offline with no downloads.
"""

from __future__ import annotations

import numpy as np
from global_land_mask import globe

from .base import wrap180


class LandMask:
    """A vectorised land/sea test backed by :mod:`global_land_mask`."""

    def is_land(self, lat, lon):
        """Boolean array: ``True`` where ``(lat, lon)`` is over land."""
        lat = np.clip(np.asarray(lat, dtype=float), -90.0, 90.0)
        lon = wrap180(lon)  # global_land_mask expects lon in [-180, 180)
        return globe.is_land(lat, lon)

    def is_ocean(self, lat, lon):
        """Boolean array: ``True`` where ``(lat, lon)`` is over water."""
        return ~self.is_land(lat, lon)
