#!/usr/bin/env python3
"""IDM Symbolic Kernel v2 — Wave 5 (pillar P1.4): domain-parametrized polynomial tower.

Run: PYTHONPATH=. python3 -m pytest tests/test_kernel_p4.py -q
"""

from __future__ import annotations

from fractions import Fraction as Q

import pytest

from idm import kernel as K
from idm.kernel import poly as P
import idm.exact as X


# ------------------------------------------------------------------ additive regression (item 18)
def test_exact_poly_ops_unchanged():
    # the refactor is additive: exact.py's domain-blind ops still behave exactly as before
    assert X.poly_add([1, 2], [3, 4]) == [Q(4), Q(6)]
    assert X.poly_mul([1, 1], [1, 1]) == [Q(1), Q(2), Q(1)]


# ------------------------------------------------------------------ univariate over ℚ (item 19)
def test_upoly_add_mul_over_Q():
    Qr = P.QRing()
    a = P.UPoly([1, 1], Qr)          # x + 1
    b = P.UPoly([-1, 1], Qr)         # x - 1
    assert P.mul(a, b).coeffs == [Q(-1), Q(0), Q(1)]     # x^2 - 1
    assert P.add(a, b).coeffs == [Q(0), Q(2)]            # 2x


def test_upoly_divmod_and_gcd_over_Q():
    Qr = P.QRing()
    x2m1 = P.UPoly([-1, 0, 1], Qr)   # x^2 - 1
    xm1 = P.UPoly([-1, 1], Qr)       # x - 1
    q, r = P.divmod_(x2m1, xm1)
    assert q.coeffs == [Q(1), Q(1)] and r.is_zero()      # (x^2-1)/(x-1) = x+1, rem 0
    g = P.gcd(x2m1, xm1)
    assert g.coeffs == [Q(-1), Q(1)]                     # gcd = x - 1 (monic)


# ------------------------------------------------------------------ SAME op, DIFFERENT domain (item 20)
def test_gcd_depends_on_the_coefficient_ring():
    x2p1_Q = P.UPoly([1, 0, 1], P.QRing())      # x^2 + 1 over ℚ
    xp1_Q = P.UPoly([1, 1], P.QRing())          # x + 1  over ℚ
    # coprime over ℚ -> gcd is the constant 1
    assert P.gcd(x2p1_Q, xp1_Q).coeffs == [Q(1)]

    F2 = P.GFRing(2)
    x2p1_2 = P.UPoly([1, 0, 1], F2)             # x^2 + 1 = (x+1)^2 over GF(2)
    xp1_2 = P.UPoly([1, 1], F2)
    # over GF(2), x+1 divides x^2+1 -> gcd is x + 1
    assert P.gcd(x2p1_2, xp1_2).coeffs == [1, 1]
    # and the division is exact over GF(2)
    _, rem = P.divmod_(x2p1_2, xp1_2)
    assert rem.is_zero()


def test_gf_arithmetic_reduces_mod_p():
    F5 = P.GFRing(5)
    a = P.UPoly([3, 4], F5)          # 4x + 3
    b = P.UPoly([2, 3], F5)          # 3x + 2
    # (4x+3)+(3x+2) = 7x+5 = 2x+0 mod 5
    assert P.add(a, b).coeffs == [0, 2]
    # inverse via Fermat: 3^-1 = 2 mod 5
    assert F5.div(1, 3) == 2


# ------------------------------------------------------------------ non-field + mismatch guards
def test_zring_is_not_a_field():
    Zr = P.ZRing()
    a = P.UPoly([1, 1], Zr)
    b = P.UPoly([-1, 1], Zr)
    assert P.mul(a, b).coeffs == [-1, 0, 1]     # multiplication is fine over ℤ
    with pytest.raises(ValueError):
        P.gcd(a, b)                              # gcd needs a field
    with pytest.raises(ValueError):
        P.divmod_(a, b)


def test_domain_mismatch_raises():
    a = P.UPoly([1, 1], P.QRing())
    b = P.UPoly([1, 1], P.GFRing(2))
    with pytest.raises(P.DomainMismatch):
        P.add(a, b)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
