"""Tests for the conditional a-priori Richardson stability model.

The exact ratio and geometric envelope are valid algebra. Applying them to a concrete finite sequence
without proving entry into the asymptotic regime yields `STABLE`, not an unconditional target certificate.
"""

from fractions import Fraction as Q

import idm  # noqa: F401
from idm.certified import (
    richardson_apriori_ratio,
    richardson_apriori_bound,
    richardson_apriori_certified,
)


def test_apriori_ratio_is_exact_power_of_two():
    assert richardson_apriori_ratio(1) == Q(1, 2)
    assert richardson_apriori_ratio(2) == Q(1, 4)
    assert richardson_apriori_ratio(3) == Q(1, 8)
    assert richardson_apriori_ratio(4) == Q(1, 16)


def test_order_below_one_is_rejected():
    import pytest

    with pytest.raises(ValueError):
        richardson_apriori_ratio(0)


def test_apriori_bound_is_refine_stable_constant():
    gap = Q(3, 1000)
    for order in (1, 2, 3):
        rho = richardson_apriori_ratio(order)
        assert richardson_apriori_bound(gap, order) == gap / (1 - rho)


def test_stable_when_conditional_bound_within_eps_else_hold():
    tiny = richardson_apriori_certified(Q(1, 10**9), 2, Q(1, 10**6))
    assert tiny.status == "STABLE"
    assert tiny.bound <= Q(1, 10**6)
    big = richardson_apriori_certified(Q(1, 2), 2, Q(1, 10**6))
    assert big.status == "HOLD"
    assert big.bound > Q(1, 10**6)


def _trapezoid(f, a, b, n):
    h = (b - a) / n
    return h * (f(a) / 2 + f(b) / 2 + sum(f(a + i * h) for i in range(1, n)))


def test_apriori_ratio_envelopes_order2_trapezoid_example():
    f = lambda x: x**3 - 2.0 * x**2 + 1.0
    a, b = 0.0, 1.0
    values = [_trapezoid(f, a, b, 8 * 2**j) for j in range(9)]
    gaps = [abs(values[i + 1] - values[i]) for i in range(len(values) - 1)]
    tail = gaps[len(gaps) // 2:]
    ratios = [tail[i + 1] / tail[i] for i in range(len(tail) - 1) if tail[i] > 0]
    rho = float(richardson_apriori_ratio(2))
    assert max(ratios) <= rho * 1.05, (max(ratios), rho)
    index = len(gaps) // 2
    observed_remaining = sum(gaps[index:])
    conditional = richardson_apriori_bound(gaps[index], 2)
    assert observed_remaining <= float(conditional) + 1e-15
