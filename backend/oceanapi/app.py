"""The oceandrift HTTP API.

Two endpoints back the front end:

* ``GET /field`` -- a regular grid of surface-current u/v, for the animated
  current layer.
* ``POST /drift`` -- seed particles and get their trajectories as GeoJSON or
  CZML.

CORS is wide open because this is a local, offline toy service meant to be
called from a separate dev-server origin (the CesiumJS app in M4).
"""

from __future__ import annotations

import numpy as np
from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from oceandrift import DAY, DriftConfig

from .schemas import DriftRequest, FieldResponse
from .serialize import stride_for, to_czml, to_geojson
from .service import OceanService, get_service


def create_app() -> FastAPI:
    app = FastAPI(
        title="oceandrift API",
        version="0.1.0",
        description="Offline toy ocean currents and Lagrangian drift.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/field", response_model=FieldResponse)
    def field(
        resolution: float = Query(1.5, gt=0.25, le=10.0, description="degrees"),
        time_days: float = Query(0.0, ge=0.0, description="evolves the eddies"),
        lat_limit: float = Query(80.0, gt=1.0, le=89.0),
        service: OceanService = Depends(get_service),
    ) -> FieldResponse:
        grid = service.sample_field(resolution, lat_limit, t=time_days * DAY)
        u = np.round(grid.u, 4)
        v = np.round(grid.v, 4)
        return FieldResponse(
            width=int(grid.lons.size),
            height=int(grid.lats.size),
            bbox=[
                float(grid.lons[0]),
                float(grid.lats[0]),
                float(grid.lons[-1]),
                float(grid.lats[-1]),
            ],
            lon0=float(grid.lons[0]),
            lat0=float(grid.lats[0]),
            dlon=resolution,
            dlat=resolution,
            u_range=[float(u.min()), float(u.max())],
            v_range=[float(v.min()), float(v.max())],
            time_seconds=time_days * DAY,
            u=u.ravel().tolist(),
            v=v.ravel().tolist(),
        )

    @app.post("/drift")
    def drift(
        request: DriftRequest,
        service: OceanService = Depends(get_service),
    ) -> JSONResponse:
        lats: list[float] = []
        lons: list[float] = []
        if request.seeds:
            lats += [s.lat for s in request.seeds]
            lons += [s.lon for s in request.seeds]
        if request.patch is not None:
            plat, plon = service.seed_patch(
                request.patch.lat,
                request.patch.lon,
                request.patch.radius_km,
                request.patch.count,
                request.random_seed,
            )
            lats += plat.tolist()
            lons += plon.tolist()

        config = DriftConfig(
            dt=request.dt_hours * 3600.0,
            duration=request.duration_days * DAY,
            diffusivity=request.diffusivity,
            seed=request.random_seed,
        )
        result = service.drift(lats, lons, config)
        stride = stride_for(result.lat.shape[0], request.max_points)

        if request.format == "czml":
            return JSONResponse(to_czml(result, request.start_time, config.dt, stride))
        return JSONResponse(to_geojson(result, stride))

    return app


app = create_app()
