"""Tests for n-dimensional finite-refinement stability readouts."""

import pytest

import idm  # noqa: F401
mp = pytest.importorskip("mpmath")
from idm.certified import integral_nd, richardson_apriori_ratio


def test_2d_contracting_is_stable_and_matches_value():
    r = integral_nd(lambda p: p[0] ** 2 * p[1] ** 2, [(0, 1), (0, 1)], mp.mpf(10) ** -4)
    assert r.stable
    assert not r.certified
    assert abs(r.q - mp.mpf(1) / 9) <= max(r.bound, mp.mpf(10) ** -3)


def test_3d_contracting_is_stable_and_matches_value():
    r = integral_nd(lambda p: p[0] ** 2 + p[1] ** 2 + p[2] ** 2, [(0, 1)] * 3,
                    mp.mpf(10) ** -3, n0=4, refines=5)
    assert r.stable
    assert not r.certified
    assert abs(r.q - 1) <= max(r.bound, mp.mpf(10) ** -2)


def test_bilinear_zero_gap_is_stable():
    r = integral_nd(lambda p: p[0] * p[1], [(0, 1), (0, 2)], mp.mpf(10) ** -6)
    assert r.stable
    assert not r.certified
    assert r.bound == 0
    assert abs(r.q - 1) <= mp.mpf(10) ** -6


def test_invalid_sample_holds():
    r = integral_nd(lambda p: 1 / (p[0] - mp.mpf("0.5")), [(0, 1), (0, 1)], mp.mpf(10) ** -4)
    assert r.status == "HOLD"


def test_zero_tolerance_holds():
    r = integral_nd(lambda p: p[0] + p[1], [(0, 1), (0, 1)], 0)
    assert r.status == "HOLD"


def test_observed_ratio_matches_apriori_quarter():
    from certified_readout import _tensor_trapezoid

    f = lambda p: mp.e ** (p[0] + p[1])
    box = [(0, 1), (0, 1)]
    values = [_tensor_trapezoid(f, box, 4 * 2 ** j) for j in range(6)]
    gaps = [abs(values[i + 1] - values[i]) for i in range(len(values) - 1)]
    tail = gaps[len(gaps) // 2:]
    ratios = [float(tail[i + 1] / tail[i]) for i in range(len(tail) - 1) if tail[i] > 0]
    rho = float(richardson_apriori_ratio(2))
    assert max(ratios) <= rho * 1.05, (max(ratios), rho)
