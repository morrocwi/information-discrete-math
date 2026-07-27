#!/usr/bin/env python3
"""IDM Symbolic Kernel v2 — Wave 3 (pillar P1.6): numeric bridge (exact + certified ball eval).

Run: PYTHONPATH=. python3 -m pytest tests/test_kernel_p6.py -q
"""

from __future__ import annotations

from fractions import Fraction as Q

import mpmath as mp

from idm import kernel as K
from idm import symbolic as SYM
from idm import interval as IVL


# ------------------------------------------------------------------ ball arithmetic (item 13)
def test_ball_add_and_mul():
    a = K.real_ball((Q(1), Q(2)))
    b = K.real_ball((Q(3), Q(4)))
    s = K.ball_add(a, b)
    assert float(s.lo) == 4.0 and float(s.hi) == 6.0
    p = K.ball_mul(a, b)
    assert float(p.lo) == 3.0 and float(p.hi) == 8.0


def test_ball_add_agrees_with_interval_engine():
    # ball_add reproduces the same rigorous engine idm.interval uses
    a = K.real_ball((Q(1), Q(2)))
    r = K.ball_add(a, a)
    vr = IVL.verified_range("x + x", "x", 1, 2)
    assert float(r.lo) == float(vr["min"]) and float(r.hi) == float(vr["max"])


def test_ball_apply_encloses_e():
    b = K.ball_apply("exp", K.real_ball(Q(1)))
    assert b.status == "ok" and b.tier == K.Tier.FINITE_DIAGNOSTIC
    assert float(b.value.lo) <= float(mp.e) <= float(b.value.hi)


def test_ball_div_by_zero_enclosure_holds():
    a = K.real_ball(Q(1))
    z = K.real_ball((Q(-1), Q(1)))       # encloses 0
    assert K.ball_div(a, z).status == K.HOLD


# ------------------------------------------------------------------ exact evaluation (item 14)
def test_evaluate_exact_is_rational_never_float():
    c = K.evaluate_exact(SYM.parse("2 + 3*4"))
    assert c.status == "ok" and c.tier == K.Tier.EXACT
    assert isinstance(c.value, K.ExactInteger) and c.value.value == 14
    # no bare mpmath float ever
    assert not isinstance(c.value, mp.mpf)


def test_evaluate_exact_rational_result():
    c = K.evaluate_exact(SYM.parse("1/2 + 1/3"))
    assert c.value == K.ExactRational(Q(5, 6))


def test_evaluate_exact_with_variable():
    c = K.evaluate_exact(SYM.parse("x**2 + 1"), {"x": K.ExactRational(Q(3))})
    assert c.value == K.ExactInteger(10)


def test_func_has_no_exact_value_holds():
    c = K.evaluate_exact(SYM.parse("sin(x)"), {"x": K.ExactRational(Q(1))})
    assert c.status == K.HOLD          # sin has no exact rational value -> HOLD, not a float
    d = K.evaluate_exact(SYM.parse("x**(1/2)"), {"x": K.ExactRational(Q(2))})
    assert d.status == K.HOLD          # non-integer power -> HOLD


# ------------------------------------------------------------------ certified evaluation (item 14)
def test_evaluate_certified_routes_func_through_finite_primitive():
    env = {"x": K.real_ball(Q(1))}
    c = K.evaluate_certified(SYM.parse("exp(x)"), env)
    assert c.status == "ok" and c.tier == K.Tier.FINITE_DIAGNOSTIC
    assert isinstance(c.value, K.RealBall)
    assert float(c.value.lo) <= float(mp.e) <= float(c.value.hi)


def test_evaluate_certified_sin_zero():
    c = K.evaluate_certified(SYM.parse("sin(x)"), {"x": K.real_ball(Q(0))})
    assert float(c.value.lo) <= 0.0 <= float(c.value.hi)


def test_evaluate_certified_polynomial_matches_interval():
    # x^2 + 1 at x in [2,2] encloses 5
    c = K.evaluate_certified(SYM.parse("x**2 + 1"), {"x": K.real_ball(Q(2))})
    assert float(c.value.lo) <= 5.0 <= float(c.value.hi)


def test_evaluate_dispatcher_prefers_exact():
    exact = K.evaluate(SYM.parse("2 + 3*4"))
    assert exact.tier == K.Tier.EXACT and isinstance(exact.value, K.ExactInteger)
    certified = K.evaluate(SYM.parse("exp(x)"), {"x": Q(1)})
    assert certified.tier == K.Tier.FINITE_DIAGNOSTIC and isinstance(certified.value, K.RealBall)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
