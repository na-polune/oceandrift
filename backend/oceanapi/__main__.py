"""Convenience runner: ``python -m oceanapi`` starts the dev server."""

from __future__ import annotations

import os

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "oceanapi.app:app",
        host=os.environ.get("OCEANDRIFT_HOST", "127.0.0.1"),
        port=int(os.environ.get("OCEANDRIFT_PORT", "8000")),
        reload=bool(os.environ.get("OCEANDRIFT_RELOAD")),
    )
