"""Service layer: one shared ocean + drift engine behind the HTTP routes.

Holding a single :class:`~oceanfield.ToyOceanField` (and its engine) avoids
rebuilding the field on every request and keeps the route handlers thin.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np

from oceandrift import DriftConfig, DriftEngine, DriftResult, seed_disk
from oceanfield import FieldGrid, ToyOceanField, sample_grid


class OceanService:
    """Wraps the field and drift engine used by the API."""

    def __init__(self, seed: int = 7):
        self.ocean = ToyOceanField(seed=seed)
        self.engine = DriftEngine(self.ocean)

    def sample_field(
        self, resolution: float = 1.5, lat_limit: float = 80.0, t: float = 0.0
    ) -> FieldGrid:
        return sample_grid(
            self.ocean, resolution=resolution, lat_limit=lat_limit, t=t
        )

    def drift(self, lat, lon, config: DriftConfig) -> DriftResult:
        return self.engine.run(np.asarray(lat), np.asarray(lon), config)

    def seed_patch(self, lat, lon, radius_km, count, seed):
        return seed_disk(lat, lon, radius_km, count, seed=seed)


@lru_cache(maxsize=1)
def get_service() -> OceanService:
    """The process-wide service singleton (FastAPI dependency)."""
    return OceanService()
