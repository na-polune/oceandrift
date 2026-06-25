"""M2 sanity check: drift particles across the toy ocean and plot the tracks.

Produces two figures in ``backend/scripts/figures/``:

* ``drift_tracks.png`` -- deterministic trajectories released from several
  current systems, showing objects carried along the gyres and boundary jets.
* ``drift_cloud.png`` -- a single patch released with eddy diffusion, showing
  how a cloud of drifters stretches and spreads over time.

Run it directly::

    python backend/scripts/plot_drift.py
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np

# Trajectories are split with NaNs at the +/-180 seam; shapely warns on those.
warnings.filterwarnings("ignore", message="invalid value encountered in linestrings")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from oceandrift import DAY, DriftConfig, DriftEngine, seed_disk
from oceanfield import ToyOceanField

FIGURES = Path(__file__).resolve().parent / "figures"

# Release sites chosen to trace long journeys across distinct current systems.
SITES = [
    ("N. Atlantic crossing", 34.0, -64.0, "#e6194B"),
    ("Kuroshio Extension", 32.0, 158.0, "#f58231"),
    ("Brazil Current", -28.0, -42.0, "#3cb44b"),
    ("Agulhas / S. Indian", -33.0, 58.0, "#42d4f4"),
    ("S. Pacific gyre", -42.0, -150.0, "#4363d8"),
    ("Antarctic Circumpolar", -55.0, 20.0, "#911eb4"),
]


def split_dateline(lon, lat):
    """Insert NaNs where a track crosses the +/-180 seam so lines don't streak."""
    lon = np.asarray(lon, dtype=float)
    lat = np.asarray(lat, dtype=float)
    breaks = np.where(np.abs(np.diff(lon)) > 180.0)[0]
    if breaks.size == 0:
        return lon, lat
    lon = np.insert(lon, breaks + 1, np.nan)
    lat = np.insert(lat, breaks + 1, np.nan)
    return lon, lat


def _make_axes(extent=None):
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    proj = ccrs.PlateCarree()
    fig = plt.figure(figsize=(18, 9) if extent is None else (12, 9))
    ax = plt.axes(projection=proj)
    if extent is None:
        ax.set_global()
    else:
        ax.set_extent(extent, crs=proj)
    ax.add_feature(cfeature.LAND, facecolor="#e8e6dd", zorder=1)
    ax.coastlines(linewidth=0.5, zorder=2)
    return fig, ax, proj


def plot_tracks(ocean):
    engine = DriftEngine(ocean)
    config = DriftConfig(dt=3 * 3600.0, duration=150 * DAY)

    fig, ax, proj = _make_axes()
    for name, lat0, lon0, color in SITES:
        lat, lon = seed_disk(lat0, lon0, radius_km=90.0, n=12, seed=1)
        result = engine.run(lat, lon, config)
        for p in range(result.n_particles):
            plon, plat = split_dateline(result.lon[:, p], result.lat[:, p])
            ax.plot(plon, plat, color=color, lw=0.7, alpha=0.8,
                    transform=proj, zorder=3)
        # Seed points (circles) and final positions (crosses).
        ax.scatter(lon, lat, c=color, s=14, edgecolor="k", linewidth=0.3,
                   transform=proj, zorder=4, label=name)
        end_lat, end_lon = result.final_position()
        ax.scatter(end_lon, end_lat, c=color, s=36, marker="*",
                   edgecolor="k", linewidth=0.3, transform=proj, zorder=5)

    ax.legend(loc="lower left", fontsize=8, ncol=2, framealpha=0.9)
    ax.set_title("oceandrift - 150-day drift tracks (o = release, * = end)")
    path = FIGURES / "drift_tracks.png"
    fig.savefig(path, dpi=130, bbox_inches="tight")
    print(f"Wrote {path}")


def plot_cloud(ocean):
    engine = DriftEngine(ocean)
    config = DriftConfig(
        dt=3 * 3600.0, duration=90 * DAY, diffusivity=600.0, seed=3
    )
    lat0, lon0 = 36.0, -55.0  # Gulf Stream extension
    lat, lon = seed_disk(lat0, lon0, radius_km=60.0, n=800, seed=2)
    result = engine.run(lat, lon, config)

    fig, ax, proj = _make_axes(extent=[-80, 10, 25, 65])
    snapshots = [0, 30, 60, 90]
    colors = ["#2166ac", "#67a9cf", "#ef8a62", "#b2182b"]
    for day, color in zip(snapshots, colors):
        i = int(np.argmin(np.abs(result.days - day)))
        ax.scatter(result.lon[i], result.lat[i], s=3, c=color, alpha=0.5,
                   transform=proj, zorder=3, label=f"day {day}")
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9, markerscale=3)
    ax.set_title("oceandrift - a drifting, spreading patch (eddy diffusion on)")
    path = FIGURES / "drift_cloud.png"
    fig.savefig(path, dpi=130, bbox_inches="tight")
    print(f"Wrote {path}")


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    ocean = ToyOceanField(seed=7)
    plot_tracks(ocean)
    plot_cloud(ocean)


if __name__ == "__main__":
    main()
