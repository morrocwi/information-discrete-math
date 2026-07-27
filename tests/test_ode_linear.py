#!/usr/bin/env python3
"""Exact linear constant-coefficient ODE solver — CAS-grade coverage (pillar P2).

The general solution is read off the characteristic polynomial, factored exactly over ℚ. These tests
check the solution-space dimension (= ODE order), that every claimed REAL root actually satisfies the
characteristic polynomial, the exact form for each root type (real, repeated, complex, irrational),
and the honest HOLD on an irreducible degree-≥3 factor.

Run: PYTHONPATH=. python3 -m pytest tests/test_ode_linear.py -q
"""

from __future__ import annotations

from fractions import Fraction as Q

import pytest

import idm
from idm.kernel.poly.ode_linear import solve_linear_ode


def _char_eval(coeffs, r):
    # evaluate the characteristic polynomial Σ coeffs[i]·r^i exactly
    return sum(Q(c) * Q(r) ** i for i, c in enumerate(coeffs))


def test_distinct_real_roots():
    # y'' - 3y' + 2y = 0  ->  (r-1)(r-2)
    sol = solve_linear_ode([2, -3, 1])
    assert sol.status == "solved" and sol.order == 2
    assert len(sol.basis) == 2
    roots = [b["root"] for b in sol.basis if b["type"] == "real"]
    assert set(roots) == {"1", "2"}
    for r in (1, 2):
        assert _char_eval([2, -3, 1], r) == 0     # every basis exponent is a genuine char root


def test_repeated_real_root_gives_x_multiplier():
    # y'' - 2y' + y = 0  ->  (r-1)^2  ->  e^x, x e^x
    sol = solve_linear_ode([1, -2, 1])
    assert sol.status == "solved" and len(sol.basis) == 2
    powers = sorted(b["poly_power"] for b in sol.basis)
    assert powers == [0, 1]
    assert sol.general == "C1*e^x + C2*x*e^x"


def test_complex_conjugate_pair():
    # y'' + y = 0  ->  r^2 + 1  ->  cos x, sin x
    sol = solve_linear_ode([1, 0, 1])
    assert sol.status == "solved" and len(sol.basis) == 2
    kinds = {b["type"] for b in sol.basis}
    assert kinds == {"complex"}
    assert all(b["alpha"] == "0" and b["beta_squared"] == "1" for b in sol.basis)
    assert sol.general == "C1*cos(x) + C2*sin(x)"


def test_damped_oscillator():
    # y'' + 4y' + 5y = 0  ->  r = -2 ± i  ->  e^{-2x} cos x, e^{-2x} sin x
    sol = solve_linear_ode([5, 4, 1])
    assert sol.status == "solved"
    assert all(b["alpha"] == "-2" and b["beta_squared"] == "1" for b in sol.basis)
    assert "e^(-2*x)*cos(x)" in sol.general and "e^(-2*x)*sin(x)" in sol.general


def test_irrational_real_roots():
    # y'' - 2y = 0  ->  r^2 - 2  ->  irrational real roots ±sqrt(2)
    sol = solve_linear_ode([-2, 0, 1])
    assert sol.status == "solved" and len(sol.basis) == 2
    assert all(b["type"] == "real_irrational" for b in sol.basis)


def test_mixed_real_and_complex():
    # (r-1)(r^2+1) = r^3 - r^2 + r - 1
    sol = solve_linear_ode([-1, 1, -1, 1])
    assert sol.status == "solved" and sol.order == 3 and len(sol.basis) == 3
    types = sorted(b["type"] for b in sol.basis)
    assert types == ["complex", "complex", "real"]


def test_repeated_complex_pair():
    # (r^2+1)^2 = r^4 + 2r^2 + 1  ->  cos x, sin x, x cos x, x sin x
    sol = solve_linear_ode([1, 0, 2, 0, 1])
    assert sol.status == "solved" and sol.order == 4 and len(sol.basis) == 4
    assert sorted(b["poly_power"] for b in sol.basis) == [0, 0, 1, 1]


def test_first_order():
    sol = solve_linear_ode([-3, 1])   # y' - 3y = 0 -> e^{3x}
    assert sol.status == "solved" and sol.general == "C1*e^(3*x)"


def test_irreducible_cubic_holds_partial():
    # r^3 - 2 is irreducible over ℚ (no rational root, cubic) -> partial, honest fence
    sol = solve_linear_ode([-2, 0, 0, 1])
    assert sol.status == "partial"
    assert sol.unresolved and "degree-3" in sol.unresolved[0]


def test_degenerate_operator_raises():
    with pytest.raises(ValueError):
        solve_linear_ode([5])        # order 0, not a differential operator


def test_basis_dimension_always_equals_order():
    # for a fully-resolved operator, #basis functions == order (solution-space dimension)
    for coeffs in ([2, -3, 1], [1, -2, 1], [1, 0, 1], [5, 4, 1], [-1, 1, -1, 1], [1, 0, 2, 0, 1]):
        sol = solve_linear_ode(coeffs)
        assert sol.status == "solved" and len(sol.basis) == sol.order


# ---- the registered kind, end to end ----

def test_kind_solved():
    r = idm.solve({"kind": "linear_ode", "coeffs": [2, -3, 1]})
    assert r["status"] == "ok" and r["tier"] == "exact"
    assert r["value"]["solution_status"] == "solved"
    assert r["value"]["general"] == "C1*e^x + C2*e^(2*x)"


def test_kind_partial_holds():
    r = idm.solve({"kind": "linear_ode", "coeffs": [-2, 0, 0, 1]})
    assert r["status"] == "HOLD" and r["value"]["solution_status"] == "partial"


def test_kind_missing_field_holds():
    r = idm.solve({"kind": "linear_ode"})
    assert r["status"] == "HOLD"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
