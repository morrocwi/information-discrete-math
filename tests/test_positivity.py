#!/usr/bin/env python3
"""Polynomial Positivity Certificate Solver — exact circuit/AM-GM certificates.

Run: PYTHONPATH=. python3 -m pytest tests/test_positivity.py -q
"""

from __future__ import annotations

from fractions import Fraction as Q

import pytest

import idm
from idm import positivity as POS


def _solve(poly, variables, domain="R"):
    return idm.solve({
        "kind": "polynomial_positivity",
        "polynomial": poly,
        "variables": variables,
        "domain": domain,
    })


# ------------------------------------------------------------------ CERTIFIED
def test_motzkin_certified():
    """M(x,y)=x⁴y²+x²y⁴+1−3x²y² ≥ 0 — the classic non-SOS nonnegative polynomial."""
    r = _solve("x**4*y**2 + x**2*y**4 + 1 - 3*x**2*y**2", ["x", "y"])
    assert r["status"] == "CERTIFIED"
    assert r["tier"] == "exact"
    assert r["value"] is True
    c = r["certificate"]
    assert c["weights"] == ["1/3", "1/3", "1/3"]
    assert c["circuit_number"] == "3"
    assert c["inner_coefficient"] == "-3"
    # boundary equality d = Θ, with real zeros at |x|=|y|=1
    assert c["comparison"]["abs_inner_coeff_pow_n"] == c["comparison"]["circuit_number_pow_n"]
    zpts = {tuple(z["point"]) for z in r["zeros"]}
    assert ("1", "1") in zpts and ("-1", "-1") in zpts


def test_quartic_family_boundary_certified():
    """x⁶+y⁶+z⁶+3−6xyz ≥ 0 (c = 6, the exact threshold |c| ≤ 6)."""
    r = _solve("x**6 + y**6 + z**6 + 3 - 6*x*y*z", ["x", "y", "z"])
    assert r["status"] == "CERTIFIED"
    assert r["certificate"]["circuit_number"] == "6"
    assert r["certificate"]["weights"] == ["1/6", "1/6", "1/6", "1/2"]


def test_sum_of_even_monomials_certified():
    r = _solve("x**2 + y**2", ["x", "y"])
    assert r["status"] == "CERTIFIED"
    assert "sum of positive even monomials" in r["method"]


def test_zero_polynomial_certified():
    r = _solve("x**2 - x**2", ["x"])
    assert r["status"] == "CERTIFIED"


# ------------------------------------------------------------------ REFUTED
def test_quartic_family_refuted_with_exact_witness():
    """c = 61/10 > 6 — REFUTED by the exact rational witness (1,1,1) → −1/10."""
    r = _solve("x**6 + y**6 + z**6 + 3 - (61/10)*x*y*z", ["x", "y", "z"])
    assert r["status"] == "REFUTED"
    assert r["value"] is False
    assert r["witness"] == ["1", "1", "1"]
    assert r["witness_value"] == "-1/10"
    # sanity: the witness really is negative under exact evaluation
    mons = POS.monomials("x**6 + y**6 + z**6 + 3 - (61/10)*x*y*z", ["x", "y", "z"])
    assert POS.evaluate(mons, (Q(1), Q(1), Q(1))) == Q(-1, 10)


def test_over_threshold_motzkin_refuted():
    r = _solve("x**4*y**2 + x**2*y**4 + 1 - 4*x**2*y**2", ["x", "y"])
    assert r["status"] == "REFUTED"
    assert r["witness_value"].startswith("-")


# ------------------------------------------------------------------ HOLD
def test_decimal_literal_is_exact_not_binary_artifact():
    """A decimal coefficient parses by its written value (0.1 → 1/10), never the float artifact."""
    mons = POS.monomials("x**2 - 0.1*x + 1", ["x"])
    assert mons[(1,)] == Q(-1, 10)
    # and it agrees with the rational-division spelling
    assert POS.monomials("x**2 - (1/10)*x + 1", ["x"]) == mons


def test_two_negative_terms_hold():
    r = _solve("x**4 + y**4 - x**2 - y**2", ["x", "y"])
    assert r["status"] == "HOLD"
    assert "SONC" in r["reason"] or "circuit" in r["reason"]


def test_non_real_domain_hold():
    r = _solve("x**2", ["x"], domain="C")
    assert r["status"] == "HOLD"


# ------------------------------------------------------------------ registry
def test_registered_kind():
    assert "polynomial_positivity" in idm.kinds()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
