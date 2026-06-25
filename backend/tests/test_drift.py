"""Correctness checks for the Lagrangian drift engine.

The RK4 integrator is validated against closed-form answers in uniform fields,
and the beaching and diffusion behaviours are checked on controlled setups.
"""

import numpy as np

from oceanfield import ToyOceanField
from oceanfield.base import DEG2M, VelocityField
from oceandrift import DAY, DriftConfig, DriftEngine, seed_disk


class ConstantField(VelocityField):
    """A spatially uniform, steady velocity field (m/s)."""

    def __init__(self, u, v):
        self.u = u
        self.v = v

    def velocity(self, lat, lon, t=0.0):
        lat, lon = np.broadcast_arrays(
            np.asarray(lat, float), np.asarray(lon, float)
        )
        return np.full(lat.shape, self.u), np.full(lat.shape, self.v)


def test_zonal_advection_matches_analytic():
    # At the equator a steady eastward current advects a particle a known
    # number of degrees of longitude; RK4 is exact for a constant field.
    field = ConstantField(u=0.5, v=0.0)
    engine = DriftEngine(field)
    config = DriftConfig(dt=3600.0, duration=10 * DAY)
    result = engine.run([0.0], [0.0], config)

    expected_dlon = 0.5 * config.duration / DEG2M
    assert np.isclose(result.lon[-1, 0], expected_dlon, atol=1e-4)
    assert np.isclose(result.lat[-1, 0], 0.0, atol=1e-9)


def test_meridional_advection_matches_analytic():
    field = ConstantField(u=0.0, v=0.5)
    engine = DriftEngine(field)
    config = DriftConfig(dt=3600.0, duration=10 * DAY)
    result = engine.run([0.0], [0.0], config)

    expected_dlat = 0.5 * config.duration / DEG2M
    assert np.isclose(result.lat[-1, 0], expected_dlat, atol=1e-4)


def test_result_shapes():
    engine = DriftEngine(ConstantField(0.1, 0.1))
    config = DriftConfig(dt=3600.0, duration=5 * DAY)
    result = engine.run(np.zeros(7), np.zeros(7), config)
    assert result.lat.shape == (config.n_steps + 1, 7)
    assert result.lon.shape == (config.n_steps + 1, 7)


def test_particle_seeded_on_land_is_beached():
    ocean = ToyOceanField()
    engine = DriftEngine(ocean)  # picks up ocean.is_land automatically
    result = engine.run([40.0], [-100.0], DriftConfig(duration=5 * DAY))  # USA
    assert bool(result.beached[0]) is True
    # It never moves.
    assert np.allclose(result.lat[:, 0], 40.0)
    assert np.allclose(result.lon[:, 0], -100.0)


def test_particle_beaches_on_reaching_land():
    # Eastward flow toward a synthetic coastline at the prime meridian.
    field = ConstantField(u=1.0, v=0.0)
    is_land = lambda lat, lon: np.asarray(lon, float) > 0.0
    engine = DriftEngine(field, is_land=is_land)
    result = engine.run([0.0], [-2.0], DriftConfig(dt=3600.0, duration=20 * DAY))
    assert bool(result.beached[0]) is True
    # Beached at its last in-water position, never crossing onto land.
    assert result.lon[-1, 0] <= 0.0


def test_diffusion_increases_spread():
    # Identical particles in a uniform field: no spread without diffusion,
    # clear spread with it.
    field = ConstantField(u=0.2, v=0.0)
    lat0 = np.zeros(300)
    lon0 = np.zeros(300)

    no_diff = DriftEngine(field).run(
        lat0, lon0, DriftConfig(dt=3600.0, duration=30 * DAY, diffusivity=0.0)
    )
    diff = DriftEngine(field).run(
        lat0, lon0, DriftConfig(dt=3600.0, duration=30 * DAY, diffusivity=500.0)
    )

    spread_none = np.std(no_diff.lat[-1]) + np.std(no_diff.lon[-1])
    spread_diff = np.std(diff.lat[-1]) + np.std(diff.lon[-1])
    assert spread_none < 1e-9
    assert spread_diff > 0.1


def test_drift_stays_in_ocean():
    # Particles released in open water should remain unbeached over a short run.
    ocean = ToyOceanField(seed=7)
    engine = DriftEngine(ocean)
    lat, lon = seed_disk(35.0, -45.0, radius_km=50.0, n=40, seed=0)
    result = engine.run(lat, lon, DriftConfig(duration=20 * DAY))
    assert result.beached.mean() < 0.25  # most still afloat
