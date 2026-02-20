
import pytest
import numpy as np
from shannon.ground_station import GroundStation

def test_compute_look_angles_optimization_correctness():
    """
    Verifies that compute_look_angles with mask_invisible=True returns
    identical results to mask_invisible=False for visible points,
    and returns NaN for invisible points.
    """
    gs = GroundStation(59.3498, 18.0707, 10)

    # Generate random points (some visible, some not)
    np.random.seed(42)
    N = 1000
    r = np.random.randn(N, 3) * 7000.0 # Random ECI
    jd = np.full(N, 2459000.5)
    fr = np.linspace(0, 0.1, N)

    # Standard path
    az1, el1, range1 = gs.compute_look_angles(r, None, jd=jd, fr=fr, mask_invisible=False)

    # Optimized path
    az2, el2, range2 = gs.compute_look_angles(r, None, jd=jd, fr=fr, mask_invisible=True)

    visible_indices = el1 > 0
    invisible_indices = el1 <= 0

    assert np.sum(visible_indices) > 0, "Should have some visible points for test validity"
    assert np.sum(invisible_indices) > 0, "Should have some invisible points for test validity"

    # Check visible points match
    np.testing.assert_allclose(az1[visible_indices], az2[visible_indices], err_msg="Azimuth mismatch on visible points")
    np.testing.assert_allclose(el1[visible_indices], el2[visible_indices], err_msg="Elevation mismatch on visible points")
    np.testing.assert_allclose(range1[visible_indices], range2[visible_indices], err_msg="Range mismatch on visible points")

    # Check invisible points are NaN
    assert np.all(np.isnan(az2[invisible_indices])), "Expected NaN for Azimuth on invisible points"
    assert np.all(np.isnan(el2[invisible_indices])), "Expected NaN for Elevation on invisible points"
    assert np.all(np.isnan(range2[invisible_indices])), "Expected NaN for Range on invisible points"

def test_compute_look_angles_scalar_optimization():
    """
    Verifies that optimization logic handles scalar inputs gracefully (by falling back or working correctly).
    """
    gs = GroundStation(59.3498, 18.0707, 10)
    r = np.array([7000.0, 0.0, 0.0])
    jd = 2459000.5
    fr = 0.0

    # Standard
    az1, el1, rng1 = gs.compute_look_angles(r, None, jd=jd, fr=fr, mask_invisible=False)

    # Optimized
    az2, el2, rng2 = gs.compute_look_angles(r, None, jd=jd, fr=fr, mask_invisible=True)

    assert az1 == az2
    assert el1 == el2
    assert rng1 == rng2

def test_pass_predictor_consistency():
    """
    Verifies PassPredictor logic with the optimization enabled implicitly.
    We just check that it finds passes correctly (smoke test).
    """
    from shannon.orbits import PassPredictor
    import datetime

    station = GroundStation(lat=59.3498, lon=18.0707, alt=10)
    line1 = "1 25544U 98067A   20164.51268519  .00001614  00000-0  37389-4 0  9998"
    line2 = "2 25544  51.6442 209.3090 0002626  63.5076 250.2989 15.49479383231362"
    predictor = PassPredictor(line1, line2)
    start_time = datetime.datetime(2020, 6, 12, 12, 0, 0)

    pass_data = predictor.get_next_pass(station, start_time=start_time)

    assert pass_data is not None
    assert len(pass_data.points) > 0

    # Check that all returned points have valid data (no NaN)
    for p in pass_data.points:
        assert not np.isnan(p['az'])
        assert not np.isnan(p['el'])
        assert not np.isnan(p['range_km'])
        assert p['el'] > 0
