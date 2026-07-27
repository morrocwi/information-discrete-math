"""Tests for idm.kernel.poly.subresultant — subresultant polynomial remainder sequence over ℚ.

Run: PYTHONPATH=. python3 -m pytest tests/test_subresultant.py -q
"""

from __future__ import annotations

from fractions import Fraction as Q

import pytest

from idm.kernel.poly.coeffring import GFRing, QRing
from idm.kernel.poly.univariate import UPoly, gcd, mul, resultant
from idm.kernel.poly.subresultant import gcd_prs, resultant_prs, subresultant_prs


# ---------------------------------------------------------------------------------------- helpers
def linear(r, D):
    """(x - r) over domain D."""
    return UPoly([-r, 1], D)


def Qr():
    return QRing()


# =============================================================== resultant_prs == resultant (Sylvester)
def test_resultant_prs_matches_sylvester_shared_root():
    D = Qr()
    # a = (x-1)(x-2), b = (x-1)(x-3): share root 1 -> resultant is 0
    a = mul(linear(1, D), linear(2, D))
    b = mul(linear(1, D), linear(3, D))
    assert resultant_prs(a, b) == Q(0)
    assert resultant_prs(a, b) == resultant(a, b)


def test_resultant_prs_matches_sylvester_coprime():
    D = Qr()
    a = UPoly([1, 0, 1], D)      # x^2 + 1
    b = UPoly([1, 1], D)         # x + 1
    # hand-verified via the root-product formula Res(f,g)=lead(f)^deg(g)*prod(g(root of f)):
    # roots of x^2+1 are +-i; (i+1)(1-i) = 1 - i^2 = 2
    assert resultant_prs(a, b) == Q(2)
    assert resultant_prs(a, b) == resultant(a, b)


@pytest.mark.parametrize(
    "a_coeffs, b_coeffs",
    [
        ([1, 0, 1], [1, 1]),            # x^2+1, x+1                (coprime)
        ([1, 0, 0, 1], [1, 0, 1]),      # x^3+1, x^2+1               (coprime)
        ([-2, 0, 1], [-3, 1]),          # x^2-2, x-3                 (coprime, deg mismatch)
        ([-3, 1], [-2, 0, 1]),          # x-3, x^2-2  (swapped order of the pair above)
        ([2, -3, 1], [3, -4, 1]),       # (x-1)(x-2), (x-1)(x-3)     (shared root -> 0)
        ([2, -3, 1], [6, -5, 1]),       # (x-1)(x-2), (x-2)(x-3)     (shared root -> 0)
        ([-4, 2, 2], [-3, 3]),          # 2(x-1)(x+2), 3(x-1)        (shared root, scaled leads)
        ([0, -1, 0, 1], [-4, 0, 1]),    # x^3-x, x^2-4               (coprime, no shared root)
        ([-1, 0, 0, 0, 1], [-1, 0, 0, 1]),  # x^4-1, x^3-1           (shared root 1 -> 0)
        ([1, 1], [1, 1]),               # x+1, x+1                   (degree-equal, shared -> 0)
    ],
)
def test_resultant_prs_matches_sylvester_many_pairs(a_coeffs, b_coeffs):
    D = Qr()
    a = UPoly(a_coeffs, D)
    b = UPoly(b_coeffs, D)
    assert resultant_prs(a, b) == resultant(a, b)


# ================================================================= gcd_prs == gcd (up to comparison via monic)
def test_gcd_prs_matches_spec_example():
    D = Qr()
    a = mul(linear(1, D), linear(2, D))   # (x-1)(x-2)
    b = mul(linear(1, D), linear(3, D))   # (x-1)(x-3)
    g_prs = gcd_prs(a, b)
    g_ref = gcd(a, b)
    assert g_prs.coeffs == linear(1, D).coeffs        # exactly x - 1
    assert g_prs == g_ref                              # both monic -> exact equality


@pytest.mark.parametrize(
    "roots_a, roots_b",
    [
        ((1, 2), (1, 3)),        # common factor (x-1)
        ((2, 3), (2, 5)),        # common factor (x-2)
        ((1, 2, 3), (1, 2, 4)),  # common factor (x-1)(x-2)
        ((-1, 0, 1), (1, 2)),    # common factor (x-1)
    ],
)
def test_gcd_prs_matches_gcd_for_known_common_factors(roots_a, roots_b):
    D = Qr()
    a = UPoly([1], D)
    for r in roots_a:
        a = mul(a, linear(r, D))
    b = UPoly([1], D)
    for r in roots_b:
        b = mul(b, linear(r, D))

    g_prs = gcd_prs(a, b).monic()
    g_ref = gcd(a, b).monic()
    assert g_prs == g_ref
    assert g_prs.lead() == Q(1)                        # exactness of "monic for comparability"

    # cross-check the monic gcd is exactly the product of the SHARED roots (as a set), monic
    shared = sorted(set(roots_a) & set(roots_b))
    expected = UPoly([1], D)
    for r in shared:
        expected = mul(expected, linear(r, D))
    assert g_prs == expected.monic()


def test_gcd_prs_robust_to_nonmonic_scaling():
    D = Qr()
    # 2*(x-1)(x+1) and 3*(x-1): common factor (x-1), but neither input is monic
    a = UPoly([Q(2)], D)
    for r in (1, -1):
        a = mul(a, linear(r, D))
    b = UPoly([Q(3)], D)
    b = mul(b, linear(1, D))
    g_prs = gcd_prs(a, b)
    assert g_prs == linear(1, D)                        # exactly monic x - 1
    assert g_prs == gcd(a, b)


def test_gcd_prs_coprime_pair_is_constant_one():
    D = Qr()
    a = UPoly([1, 0, 1], D)      # x^2 + 1
    b = UPoly([1, 1], D)         # x + 1
    g_prs = gcd_prs(a, b)
    assert g_prs.coeffs == [Q(1)]
    assert g_prs == gcd(a, b)


# =========================================================================== subresultant_prs shape
def test_subresultant_prs_terminates_with_last_nonzero_remainder():
    D = Qr()
    a = mul(linear(1, D), linear(2, D))
    b = mul(linear(1, D), linear(3, D))
    seq = subresultant_prs(a, b)
    assert seq[0].degree() >= seq[1].degree()
    for i in range(1, len(seq) - 1):     # remainders (index >= 2) strictly decrease in degree
        assert seq[i + 1].degree() < seq[i].degree()
    assert not seq[-1].is_zero()
    # the theoretical last remainder for this pair is a scalar multiple of (x-1)
    assert seq[-1].monic() == linear(1, D)


# =============================================================================== honest error paths
def test_degree_zero_input_raises_valueerror():
    D = Qr()
    a = UPoly([1, 1], D)      # x + 1
    const = UPoly([5], D)     # constant, degree 0
    with pytest.raises(ValueError):
        subresultant_prs(a, const)
    with pytest.raises(ValueError):
        resultant_prs(a, const)
    with pytest.raises(ValueError):
        gcd_prs(a, const)


def test_non_qring_domain_raises_valueerror():
    F2 = GFRing(2)
    a = UPoly([1, 1, 1], F2)   # x^2+x+1 over GF(2)
    b = UPoly([1, 1], F2)      # x+1 over GF(2)
    with pytest.raises(ValueError):
        subresultant_prs(a, b)


def test_domain_mismatch_raises():
    a = UPoly([1, 1], QRing())
    b = UPoly([1, 1], GFRing(2))
    with pytest.raises(Exception):
        subresultant_prs(a, b)
