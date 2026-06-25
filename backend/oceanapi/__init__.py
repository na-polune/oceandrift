"""oceanapi -- a small FastAPI service exposing the toy ocean and drift engine.

Run it with::

    uvicorn oceanapi.app:app --reload      # from the backend/ directory
    python -m oceanapi                      # equivalent convenience runner
"""

from __future__ import annotations

from .app import app, create_app
from .service import OceanService, get_service

__version__ = "0.1.0"

__all__ = ["app", "create_app", "OceanService", "get_service", "__version__"]
