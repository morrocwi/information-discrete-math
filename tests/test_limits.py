#!/usr/bin/env python3
"""Exact ℚ rational-function limits — CAS-grade coverage (pillar P2).

The numeric `limit` kind extrapolates a sequence; this is its exact symbolic counterpart for rational
functions. It must return an EXACT value (a rational, a signed ±∞, or an honest "does not exist"),
handling removable singularities by cancellation and genuine poles by sign analysis.

Run: PYTHONPATH=. python3 -m pytest tests/test_limits.py -q
"""

from __future__ import annotations

from fractions import Fraction as Q

import pytest

import idm
from idm.kernel.poly.limits import rational_limit, rational_limit_oneside


def test_removable_singularity_cancels_to_finite():
    # (x^2 - 1)/(x - 1) -> 2 at x=1 (the 0/0 removes)
    r = rational_limit([-1, 0, 1], [-1, 1], 1)
    assert r.status == "finite" and r.value == Q(2) and r.removable is True


def test_ordinary_finite_point():
    # (x + 2)/(x - 3) at x=0 -> -2/3, no cancellation
    r = rational_limit([2, 1], [-3, 1], 0)
    assert r.status == "finite" and r.value == Q(-2, 3) and r.removable is False


def test_double_removable():
    # (x^2 - 4)/(x^2 - x - 2) = (x-2)(x+2)/((x-2)(x+1)) -> (x+2)/(x+1) -> 4/3 at x=2
    r = rational_limit([-4, 0, 1], [-2, -1, 1], 2)
    assert r.status == "finite" and r.value == Q(4, 3) and r.removable is True


def test_simple_pole_two_sided_dne():
    # 1/x at x=0: +inf from the right, -inf from the left -> DNE
    r = rational_limit([1], [0, 1], 0)
    assert r.status == "dne"


def test_simple_pole_one_sided_signs():
    assert rational_limit_oneside([1], [0, 1], 0, "+").sign == 1
    assert rational_limit_oneside([1], [0, 1], 0, "-").sign == -1


def test_even_pole_two_sided_infinite():
    # 1/x^2 at x=0 -> +inf on both sides
    r = rational_limit([1], [0, 0, 1], 0)
    assert r.status == "infinite" and r.sign == 1


def test_even_pole_negative_numerator():
    # -1/x^2 -> -inf on both sides
    r = rational_limit([-1], [0, 0, 1], 0)
    assert r.status == "infinite" and r.sign == -1


def test_limit_at_infinity_equal_degree():
    # (2x + 1)/(x + 1) -> 2
    r = rational_limit([1, 2], [1, 1], "inf")
    assert r.status == "finite" and r.value == Q(2)


def test_limit_at_infinity_numerator_smaller():
    # (x + 1)/(x^2 + 1) -> 0
    r = rational_limit([1, 1], [1, 0, 1], "inf")
    assert r.status == "finite" and r.value == Q(0)


def test_limit_at_infinity_diverges_sign_and_parity():
    # x^2/(x + 1): +inf at +inf, -inf at -inf (odd degree gap, positive lead)
    assert rational_limit([0, 0, 1], [1, 1], "+inf").sign == 1
    assert rational_limit([0, 0, 1], [1, 1], "-inf").sign == -1
    # x^3/x = x^2 gap 2 (even): +inf at both ends
    assert rational_limit([0, 0, 0, 1], [0, 1], "-inf").sign == 1


def test_zero_denominator_polynomial_raises():
    with pytest.raises(ValueError):
        rational_limit([1, 2], [0], 0)


# ---- the registered kind, end to end ----

def test_kind_removable():
    r = idm.solve({"kind": "rational_limit", "num": [-1, 0, 1], "den": [-1, 1], "point": 1})
    assert r["status"] == "ok" and r["tier"] == "exact"
    assert r["value"]["limit_type"] == "finite" and r["value"]["limit"]["exact"] == "2/1"
    assert r["value"]["removable"] is True


def test_kind_at_infinity():
    r = idm.solve({"kind": "rational_limit", "num": [1, 2], "den": [1, 1], "point": "inf"})
    assert r["value"]["limit_type"] == "finite" and r["value"]["limit"]["exact"] == "2/1"


def test_kind_pole_dne():
    r = idm.solve({"kind": "rational_limit", "num": [1], "den": [0, 1], "point": 0})
    assert r["status"] == "ok" and r["value"]["limit_type"] == "dne"


def test_kind_one_sided():
    r = idm.solve({"kind": "rational_limit", "num": [1], "den": [0, 1], "point": 0, "side": "+"})
    assert r["value"]["limit_type"] == "infinite" and r["value"]["sign"] == 1


def test_kind_missing_field_holds():
    r = idm.solve({"kind": "rational_limit", "num": [1, 2]})  # no den/point
    assert r["status"] == "HOLD"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
