"""M1 sanity check: draw the toy ocean and confirm it looks like Earth.

Samples :class:`oceanfield.ToyOceanField` on a global grid and renders the
surface currents as streamlines coloured by speed, over coastlines.  Run it
directly::

    python backend/scripts/plot_field.py

The figure is written to ``backend/scripts/figures/ocean_field.png``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# Allow running straight from a checkout without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from oceanfield import ToyOceanField, sample_grid

FIGURE_PATH = Path(__file__).resolve().parent / "figures" / "ocean_field.png"


def main() -> None:
    ocean = ToyOceanField(seed=7)

    grid = sample_grid(ocean, resolution=1.0)
    speed = grid.speed

    print("Toy ocean current speed (m/s):")
    print(f"  min  = {speed.min():.3f}")
    print(f"  mean = {speed[speed > 0].mean():.3f}  (ocean only)")
    print(f"  max  = {speed.max():.3f}")

    try:
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature

        projection = ccrs.PlateCarree()
        fig = plt.figure(figsize=(18, 9))
        ax = plt.axes(projection=projection)
        ax.set_global()
        strm = ax.streamplot(
            grid.lons,
            grid.lats,
            grid.u,
            grid.v,
            transform=projection,
            density=3.5,
            linewidth=0.6,
            arrowsize=0.5,
            color=speed,
            cmap="turbo",
            norm=plt.Normalize(0.0, 1.5),
        )
        ax.add_feature(cfeature.LAND, facecolor="#e8e6dd", zorder=3)
        ax.coastlines(linewidth=0.5, zorder=4)
        ax.set_title("oceandrift - toy surface currents (M1)")
        fig.colorbar(
            strm.lines, ax=ax, label="speed (m/s)", shrink=0.6, extend="max"
        )
    except Exception as exc:  # pragma: no cover - cartopy is optional
        print(f"[cartopy unavailable: {exc}] falling back to a plain plot")
        fig, ax = plt.subplots(figsize=(18, 9))
        strm = ax.streamplot(
            grid.lons,
            grid.lats,
            grid.u,
            grid.v,
            density=5,
            linewidth=0.5,
            arrowsize=0.5,
            color=speed,
            cmap="viridis",
        )
        land = np.where(speed == 0, 1.0, np.nan)
        ax.pcolormesh(grid.lons, grid.lats, land, cmap="Greys", vmin=0, vmax=2)
        ax.set_xlabel("longitude")
        ax.set_ylabel("latitude")
        ax.set_title("oceandrift - toy surface currents (M1)")
        fig.colorbar(strm.lines, ax=ax, label="speed (m/s)", shrink=0.7)

    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_PATH, dpi=130, bbox_inches="tight")
    print(f"\nWrote {FIGURE_PATH}")

    # A regional zoom keeps detail legible when the global view is downscaled.
    try:
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature

        proj = ccrs.PlateCarree()
        fig2 = plt.figure(figsize=(11, 9))
        ax2 = plt.axes(projection=proj)
        ax2.set_extent([-90, -5, 5, 65], crs=proj)
        ax2.streamplot(
            grid.lons, grid.lats, grid.u, grid.v, transform=proj,
            density=4.5, linewidth=0.7, arrowsize=0.7,
            color=speed, cmap="turbo", norm=plt.Normalize(0.0, 1.5),
        )
        ax2.add_feature(cfeature.LAND, facecolor="#e8e6dd", zorder=3)
        ax2.coastlines(linewidth=0.6, zorder=4)
        ax2.set_title("North Atlantic gyre + Gulf Stream (zoom)")
        zoom_path = FIGURE_PATH.parent / "north_atlantic.png"
        fig2.savefig(zoom_path, dpi=130, bbox_inches="tight")
        print(f"Wrote {zoom_path}")
    except Exception as exc:  # pragma: no cover
        print(f"[skipped zoom: {exc}]")


if __name__ == "__main__":
    main()
