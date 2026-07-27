#!/usr/bin/env python3
"""IDM Symbolic Kernel v2 — P2: kernel-native simplify surface (assumption-aware + rational cancel).

Run: PYTHONPATH=. python3 -m pytest tests/test_kernel_simplify.py -q
"""

from __future__ import annotations

from fractions import Fraction as Q

from idm.kernel import simplify as KS
from idm import symbolic as SYM


def test_simplify_default_is_byte_identical_to_legacy():
    for src in ("(x**2)**3", "x + x", "sin(0)", "x**2 + 2*x + 1", "2*x + 3*x - x"):
        assert KS.simplify(src) == SYM.simplify(SYM.parse(src))


def test_simplify_is_assumption_aware():
    from idm import kernel as K
    e = ("pow", ("pow", ("var", "x"), Q(2)), Q(1, 2))
    empty = K.AssumptionSet.empty()
    assert KS.simplify(e, empty) == e                       # gated off: no collapse
    asm = K.parse_assumptions({"x": ["positive"]})
    assert KS.simplify(e, asm) == ("var", "x")              # x>0: (x^2)^(1/2) = x


def test_cancel_rational_reduces_and_cross_verifies():
    r = KS.cancel_rational("x**2 - 1", "x - 1", "x")
    assert r["status"] == "ok"
    assert KS._coeffs_low_to_high(r["num"], "x") == [Q(1), Q(1)]   # x + 1
    assert KS._coeffs_low_to_high(r["den"], "x") == [Q(1)]         # 1
    # cross-multiply identity as polynomials: reduced_num * den == reduced_den * num
    from idm.kernel import poly as P
    Qr = P.QRing()
    lhs = P.mul(P.UPoly(KS._coeffs_low_to_high(r["num"], "x"), Qr),
                P.UPoly(KS._coeffs_low_to_high("x - 1", "x"), Qr))
    rhs = P.mul(P.UPoly(KS._coeffs_low_to_high(r["den"], "x"), Qr),
                P.UPoly(KS._coeffs_low_to_high("x**2 - 1", "x"), Qr))
    assert lhs == rhs


def test_cancel_rational_shared_quadratic():
    r = KS.cancel_rational("x**3 - 6*x**2 + 11*x - 6", "x**2 - 4*x + 3", "x")
    # (x-1)(x-2)(x-3) / (x-1)(x-3) = (x-2)/1
    assert r["status"] == "ok"
    assert r["common_str"] != "1"                           # a nontrivial gcd was cancelled


def test_cancel_rational_non_polynomial_holds():
    r = KS.cancel_rational("sin(x)", "x", "x")
    assert r["status"] == "HOLD"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
