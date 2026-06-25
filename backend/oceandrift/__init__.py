"""oceandrift -- Lagrangian drift of particles on an ocean velocity field.

Pairs with :mod:`oceanfield`: build a velocity field there, then trace where
seeded objects drift with :class:`DriftEngine`.

Example:
    >>> from oceanfield import ToyOceanField
    >>> from oceandrift import DriftEngine, DriftConfig
    >>> ocean = ToyOceanField()
    >>> engine = DriftEngine(ocean)
    >>> result = engine.run([35.0], [-60.0], DriftConfig(duration=60 * 86400))
"""

from __future__ import annotations

from .engine import DAY, DriftConfig, DriftEngine, DriftResult
from .seeding import seed_disk, seed_grid

__version__ = "0.1.0"

__all__ = [
    "DriftEngine",
    "DriftConfig",
    "DriftResult",
    "DAY",
    "seed_disk",
    "seed_grid",
    "__version__",
]
