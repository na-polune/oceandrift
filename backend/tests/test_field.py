"""Correctness checks for the toy ocean field.

These lock in the physical sanity of the model -- rotation senses, the Antarctic
Circumpolar Current, land masking and plausible speed ranges -- so future tuning
can't silently break them.  Run with ``pytest`` from the ``backend`` directory.
"""

import numpy as np
import pytest

from oceanfield import ToyOceanField, sample_grid


@pytest.fixture(scope="module")
def ocean():
    # Eddies off: tests target the steady large-scale backbone.
    return ToyOceanField(eddies=False)


def test_scalar_and_array_shapes(ocean):
    u, v = ocean.velocity(30.0, -40.0)
    assert np.shape(u) == () and np.shape(v) == ()

    lat = np.array([[10.0, 20.0], [30.0, 40.0]])
    lon = np.array([[-50.0, -40.0], [-30.0, -20.0]])
    u, v = ocean.velocity(lat, lon)
    assert u.shape == lat.shape == v.shape


def test_land_velocity_is_zero(ocean):
    # Central North America and the Sahara are unambiguously land.
    for lat, lon in [(40.0, -100.0), (23.0, 13.0)]:
        u, v = ocean.velocity(lat, lon)
        assert float(u) == 0.0 and float(v) == 0.0


def test_open_ocean_is_moving(ocean):
    # Open-water points on gyre limbs (not the slack gyre centres).
    for lat, lon in [(40.0, -50.0), (-45.0, -120.0), (-55.0, 0.0)]:
        assert float(ocean.speed(lat, lon)) > 0.05


def test_subtropical_gyres_rotate_correctly(ocean):
    # Northern subtropical gyres turn clockwise: westward on the south limb,
    # eastward on the north limb.
    assert float(ocean.velocity(15.0, -45.0)[0]) < 0  # N. Atlantic south limb
    assert float(ocean.velocity(45.0, -40.0)[0]) > 0  # N. Atlantic north limb
    # Southern subtropical gyres turn anticlockwise: the reverse.
    assert float(ocean.velocity(-15.0, -20.0)[0]) < 0  # S. Atlantic north limb
    assert float(ocean.velocity(-42.0, -20.0)[0]) > 0  # S. Atlantic south limb


def test_antarctic_circumpolar_current_is_strong_eastward(ocean):
    u, v = ocean.velocity(-55.0, 0.0)
    assert float(u) > 0.7


def test_global_speeds_are_plausible():
    grid = sample_grid(ToyOceanField(seed=7), resolution=1.0)
    speed = grid.speed
    ocean_speed = speed[speed > 0]
    assert 0.2 < ocean_speed.mean() < 0.9  # energetic but not absurd
    assert speed.max() < 3.5  # boundary-current peak, not a blow-up
