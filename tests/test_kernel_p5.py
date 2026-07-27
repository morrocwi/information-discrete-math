#!/usr/bin/env python3
"""IDM Symbolic Kernel v2 — Wave 4 (pillar P1.5): conditional solution objects.

Run: PYTHONPATH=. python3 -m pytest tests/test_kernel_p5.py -q
"""

from __future__ import annotations

from fractions import Fraction as Q

from idm.kernel import solution as SOL


# ------------------------------------------------------------------ symbolic leading coeff (item 15)
def test_symbolic_linear_returns_exceptional_cases():
    """solve(a*x + b, x): a is unassumed -> the answer's shape depends on whether a = 0."""
    s = SOL.solve("a*x + b", "x")
    assert s.kind is SOL.SolutionKind.PARAMETRIC
    assert s.status == "ok"
    conds = [e.condition for e in s.exceptional]
    # the a != 0 branch gives x = -b/a
    nonzero = next(e for e in s.exceptional if "!= 0" in e.condition and "==" not in e.condition)
    root_str = nonzero.solutions[0].tostr()["x"]
    assert nonzero.solutions and "b" in root_str and "a" in root_str
    # and it is genuinely -b/a: substituting it back satisfies the equation exactly
    assert SOL.verify(nonzero.solutions[0], "a*x + b", "x") is True
    # there is an a == 0 (with b != 0) -> no-solution branch
    assert any("== 0" in e.condition and "!= 0" in e.condition for e in s.exceptional)


def test_numeric_linear_is_direct():
    s = SOL.solve("2*x - 6", "x")
    assert s.kind is SOL.SolutionKind.POINTS
    assert s.completeness == "complete"
    assert s.solutions[0].values["x"] == Q(3)


def test_constant_equations():
    assert SOL.solve("0", "x").kind is SOL.SolutionKind.ALL
    assert SOL.solve("5", "x").kind is SOL.SolutionKind.EMPTY


def test_non_polynomial_holds():
    s = SOL.solve("sin(x) - 1", "x")
    assert s.status == SOL.HOLD


# ------------------------------------------------------------------ verify (item 16)
def test_verify_point_solution_by_exact_substitution():
    s = SOL.solve("2*x - 6", "x")
    assert SOL.verify(s.solutions[0], "2*x - 6", "x") is True
    # a wrong candidate fails verification
    assert SOL.verify(SOL.Solution({"x": Q(4)}), "2*x - 6", "x") is False


def test_verify_symbolic_root_is_identity_not_enumeration():
    # x = -b/a verifies as an exact identity a*(-b/a)+b = 0, without enumerating a,b
    s = SOL.solve("a*x + b", "x")
    root = next(e for e in s.exceptional if "!= 0" in e.condition and "==" not in e.condition).solutions[0]
    assert SOL.verify(root, "a*x + b", "x") is True


# ------------------------------------------------------------------ completeness (item 17)
def test_cubic_with_missing_complex_roots_is_partial():
    # (x-1)(x^2+1) = x^3 - x^2 + x - 1: only x=1 is rational; two complex roots remain -> partial
    s = SOL.solve("x**3 - x**2 + x - 1", "x")
    assert Q(1) in [sol.values["x"] for sol in s.solutions]
    assert s.completeness == "partial"
    assert "degree-2" in (s.reason or "")


def test_fully_rational_cubic_is_complete():
    # (x-1)(x-2)(x-3) = x^3 - 6x^2 + 11x - 6 : all three roots rational -> complete
    s = SOL.solve("x**3 - 6*x**2 + 11*x - 6", "x")
    roots = sorted(sol.values["x"] for sol in s.solutions)
    assert roots == [Q(1), Q(2), Q(3)]
    assert s.completeness == "complete"


def test_repeated_rational_root_is_complete_not_falsely_partial():
    # (x-1)^2 (x-2) = x^3 - 4x^2 + 5x - 2 : double root at 1 -> still complete
    s = SOL.solve("x**3 - 4*x**2 + 5*x - 2", "x")
    assert s.completeness == "complete"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
