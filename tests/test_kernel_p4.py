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


def test_gfring_rejects_composite_modulus():
    # a composite modulus is NOT a field: Fermat's inverse is bogus and gcd would hang.
    # Reject at construction (HOLD direction), never accept with a silently-wrong answer.
    for composite in (4, 6, 9, 1):
        with pytest.raises(ValueError):
            P.GFRing(composite)
    # primes are fine
    for prime in (2, 3, 5, 7, 11):
        assert P.GFRing(prime).p == prime


def test_domain_mismatch_raises():
    a = P.UPoly([1, 1], P.QRing())
    b = P.UPoly([1, 1], P.GFRing(2))
    with pytest.raises(P.DomainMismatch):
        P.add(a, b)


# ------------------------------------------------------------------ factor (Phase 2, depth)
from idm.kernel.poly.univariate import _product   # back-verification helper


def _back_verify(p):
    f = P.factor(p)
    recon = _product(f["factors"], f["unit"], f["remaining"])
    assert recon == p, f"factor did not multiply back to the input: {recon} != {p}"
    return f


def test_factor_splits_over_Q():
    Qr = P.QRing()
    p = P.UPoly([-6, 11, -6, 1], Qr)          # x^3 - 6x^2 + 11x - 6 = (x-1)(x-2)(x-3)
    f = _back_verify(p)
    assert f["complete"] is True and f["unit"] == Q(1)
    roots = sorted(-fac.coeffs[0] for fac, m in f["factors"])   # (x - r) has constant -r
    assert roots == [Q(1), Q(2), Q(3)]
    assert all(m == 1 for _, m in f["factors"])


def test_factor_handles_multiplicity_and_leading_unit():
    Qr = P.QRing()
    # 2*(x-1)^2*(x-2) = 2x^3 - 8x^2 + 10x - 4
    p = P.UPoly([-4, 10, -8, 2], Qr)
    f = _back_verify(p)
    assert f["unit"] == Q(2) and f["complete"] is True
    mults = sorted(m for _, m in f["factors"])
    assert mults == [1, 2]


def test_factor_irreducible_over_Q_is_incomplete():
    p = P.UPoly([1, 0, 1], P.QRing())          # x^2 + 1: no rational roots
    f = _back_verify(p)
    assert f["complete"] is False
    assert f["remaining"].coeffs == [Q(1), Q(0), Q(1)]   # the whole thing survives


def test_factor_differs_over_GF2():
    # x^2 + 1 is irreducible over ℚ but = (x+1)^2 over GF(2): SAME poly, different factorization
    f = _back_verify(P.UPoly([1, 0, 1], P.GFRing(2)))
    assert f["complete"] is True
    assert f["factors"] == [(P.UPoly([1, 1], P.GFRing(2)), 2)]   # (x+1)^2


def test_factor_needs_a_field():
    with pytest.raises(ValueError):
        P.factor(P.UPoly([-1, 0, 1], P.ZRing()))


# ------------------------------------------------------------------ cancel / resultant / discriminant
def test_cancel_reduces_to_lowest_terms():
    Qr = P.QRing()
    # (x^2-1)/(x-1) = (x+1)/1
    num = P.UPoly([-1, 0, 1], Qr)
    den = P.UPoly([-1, 1], Qr)
    r = P.cancel(num, den)
    assert r["num"].coeffs == [Q(1), Q(1)]        # x + 1
    assert r["den"].coeffs == [Q(1)]              # 1
    # cross-multiplication identity: reduced_num * den == reduced_den * num
    assert P.mul(r["num"], den) == P.mul(r["den"], num)


def test_cancel_shared_quadratic_factor():
    Qr = P.QRing()
    # ((x-1)(x-2)) / ((x-1)(x-3)) -> (x-2)/(x-3)
    num = P.mul(P.UPoly([-1, 1], Qr), P.UPoly([-2, 1], Qr))
    den = P.mul(P.UPoly([-1, 1], Qr), P.UPoly([-3, 1], Qr))
    r = P.cancel(num, den)
    assert P.mul(r["num"], den) == P.mul(r["den"], num)   # exact cross-multiply
    assert r["common"].coeffs == [Q(-1), Q(1)]            # gcd = x - 1


def test_resultant_zero_iff_common_root():
    Qr = P.QRing()
    a = P.mul(P.UPoly([-1, 1], Qr), P.UPoly([-2, 1], Qr))   # (x-1)(x-2)
    shared = P.UPoly([-2, 1], Qr)                            # x-2 (shares root 2)
    coprime = P.UPoly([-3, 1], Qr)                           # x-3 (no shared root)
    assert P.resultant(a, shared) == Q(0)
    assert P.resultant(a, coprime) != Q(0)
    # res(x-1, x-2) = -1 (known value)
    assert P.resultant(P.UPoly([-1, 1], Qr), P.UPoly([-2, 1], Qr)) == Q(-1)


def test_discriminant_matches_b2_minus_4ac():
    Qr = P.QRing()
    # x^2 - 5x + 6 : disc = 25 - 24 = 1
    assert P.discriminant(P.UPoly([6, -5, 1], Qr)) == Q(1)
    # x^2 - 2 : disc = 8
    assert P.discriminant(P.UPoly([-2, 0, 1], Qr)) == Q(8)
    # x^2 + 1 : disc = -4  (negative -> no real roots, matches P1.5)
    assert P.discriminant(P.UPoly([1, 0, 1], Qr)) == Q(-4)
    # general 2x^2+3x+5: b^2-4ac = 9-40 = -31
    assert P.discriminant(P.UPoly([5, 3, 2], Qr)) == Q(-31)


def test_resultant_needs_field_and_positive_degree():
    Qr = P.QRing()
    with pytest.raises(ValueError):
        P.resultant(P.UPoly([1, 1], P.ZRing()), P.UPoly([1, 1], P.ZRing()))
    with pytest.raises(ValueError):
        P.resultant(P.UPoly([5], Qr), P.UPoly([1, 1], Qr))     # degree 0


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
