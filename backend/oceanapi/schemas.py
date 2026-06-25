"""Pydantic request/response models for the API."""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


class SeedPoint(BaseModel):
    """A single release position."""

    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class SeedPatch(BaseModel):
    """A disk of randomly-placed release positions."""

    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(50.0, gt=0, le=2000)
    count: int = Field(100, ge=1, le=2000)


class DriftRequest(BaseModel):
    """Body for ``POST /drift``."""

    seeds: Optional[List[SeedPoint]] = None
    patch: Optional[SeedPatch] = None
    duration_days: float = Field(120.0, gt=0, le=3650)
    dt_hours: float = Field(3.0, gt=0, le=72)
    diffusivity: float = Field(0.0, ge=0, le=10_000, description="m^2/s")
    random_seed: int = 0
    start_time: str = "2024-01-01T00:00:00Z"
    format: Literal["geojson", "czml"] = "geojson"
    max_points: int = Field(400, ge=2, le=5000, description="max vertices per track")

    @model_validator(mode="after")
    def _require_seeds(self):
        if not self.seeds and self.patch is None:
            raise ValueError("Provide at least one of 'seeds' or 'patch'.")
        return self


class FieldResponse(BaseModel):
    """Response for ``GET /field``: a regular lon/lat grid of u/v velocity.

    ``u`` and ``v`` are flattened row-major: row 0 is the southernmost latitude
    (``lat0``) increasing northward, column 0 the westernmost longitude
    (``lon0``) increasing eastward.
    """

    width: int
    height: int
    bbox: List[float] = Field(..., description="[lon_min, lat_min, lon_max, lat_max]")
    lon0: float
    lat0: float
    dlon: float
    dlat: float
    u_range: List[float]
    v_range: List[float]
    time_seconds: float
    u: List[float]
    v: List[float]
