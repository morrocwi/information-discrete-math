"""Reconstruction / irreducibility tests for idm.kernel.poly.factorize.factor_over_Q (independent
attempt C — exact ℚ full factorization via square-free decomposition + Kronecker's bounded-degree
divisor method, no modular arithmetic, no Hensel lifting, no float anywhere).

The ground truth for every test is one (or both) of:
  (a) RECONSTRUCTION — ``lead * prod(g_i ** m_i) == p`` exactly, as ``UPoly`` equality (which compares
      exact ``fractions.Fraction`` coefficient lists), for the returned factorization; or
  (b) IRREDUCIBILITY — a returned ``g_i`` is irreducible over ℚ iff it has NO rational root (checked
      independently via ``idm.kernel.poly.univariate.factor``) AND ``factor_over_Q(g_i)`` returns
      exactly itself with multiplicity 1 (a fixed point of the factorizer).

No float anywhere — only ``fractions.Fraction``, exactly.
"""

from fractions import Fraction as Q

import pytest

from idm.kernel.poly.coeffring import QRing, GFRing
from idm.kernel.poly.univariate import UPoly, mul, factor
from idm.kernel.poly.factorize import factor_over_Q


# --------------------------------------------------------------------------------------------- helpers
def _upoly(*coeffs_low_to_high):
    """Build a UPoly over QRing from plain ints/Fractions, low-order coefficient first."""
    return UPoly([Q(c) for c in coeffs_low_to_high], QRing())


def _assert_exact_fraction_coeffs(p):
    for c in p.coeffs:
        assert isinstance(c, Q), f"expected exact Fraction coefficient, got {type(c)}: {c!r}"


def _reconstruct(lead, factors, domain):
    """lead * prod(g_i ** m_i), rebuilt with the exact ring `mul` — the reconstruction ground truth."""
    acc = UPoly([lead], domain)
    for g, m in factors:
        for _ in range(m):
            acc = mul(acc, g)
    return acc


def _assert_reconstructs(p):
    lead, factors = factor_over_Q(p)
    _assert_exact_fraction_coeffs(UPoly([lead], p.domain))
    for g, m in factors:
        assert isinstance(m, int) and m >= 1
        assert g.lead() == Q(1), f"factor {g!r} is not monic"
        _assert_exact_fraction_coeffs(g)
    rebuilt = _reconstruct(lead, factors, p.domain)
    assert rebuilt == p, f"reconstruction mismatch: {rebuilt!r} != {p!r}"
    return lead, factors


def _assert_distinct(factors):
    keys = [tuple(g.coeffs) for g, _ in factors]
    assert len(keys) == len(set(keys)), f"duplicate irreducible factor in {factors!r}"


def _has_rational_root(g):
    return bool(factor(g)["factors"])


def _assert_irreducible(g):
    """g (monic, over QRing) is irreducible over ℚ: no rational root, AND factor_over_Q(g) is a
    fixed point — returns exactly [(g, 1)] with lead 1."""
    assert not _has_rational_root(g), f"{g!r} has a rational root, so is not irreducible"
    lead, factors = factor_over_Q(g)
    assert lead == Q(1)
    assert len(factors) == 1, f"expected a single irreducible factor, got {factors!r}"
    only_g, only_m = factors[0]
    assert only_m == 1
    assert only_g == g, f"factor_over_Q({g!r}) is not a fixed point: got {only_g!r}"


# ------------------------------------------------------------------------------------- required examples
def test_repeated_linear_factors_x_minus_1_sq_x_minus_2_cubed():
    # (x-1)^2 (x-2)^3
    x_minus_1 = _upoly(-1, 1)
    x_minus_2 = _upoly(-2, 1)
    p = mul(mul(x_minus_1, x_minus_1), mul(mul(x_minus_2, x_minus_2), x_minus_2))
    lead, factors = _assert_reconstructs(p)
    _assert_distinct(factors)
    got = {tuple(g.coeffs): m for g, m in factors}
    assert lead == Q(1)
    assert got == {(Q(-1), Q(1)): 2, (Q(-2), Q(1)): 3}


def test_x_squared_minus_2_is_irreducible():
    p = _upoly(-2, 0, 1)                          # x^2 - 2
    lead, factors = _assert_reconstructs(p)
    assert lead == Q(1)
    assert len(factors) == 1
    g, m = factors[0]
    assert m == 1
    assert g == p
    _assert_irreducible(g)


def test_x_fourth_minus_1_splits_into_two_linear_and_one_irreducible_quadratic():
    p = _upoly(-1, 0, 0, 0, 1)                     # x^4 - 1
    lead, factors = _assert_reconstructs(p)
    _assert_distinct(factors)
    assert lead == Q(1)
    assert len(factors) == 3
    got = {tuple(g.coeffs): m for g, m in factors}
    assert got[(Q(-1), Q(1))] == 1                 # (x - 1)
    assert got[(Q(1), Q(1))] == 1                  # (x + 1)
    assert got[(Q(1), Q(0), Q(1))] == 1             # (x^2 + 1)
    quad = [g for g, m in factors if g.degree() == 2][0]
    _assert_irreducible(quad)


def test_product_of_two_irreducible_quadratics_x2_minus_2_times_x2_minus_3():
    x2_minus_2 = _upoly(-2, 0, 1)
    x2_minus_3 = _upoly(-3, 0, 1)
    p = mul(x2_minus_2, x2_minus_3)
    lead, factors = _assert_reconstructs(p)
    _assert_distinct(factors)
    assert lead == Q(1)
    assert len(factors) == 2
    for g, m in factors:
        assert m == 1
        assert g.degree() == 2
        _assert_irreducible(g)
    got = {tuple(g.coeffs) for g, _ in factors}
    assert got == {(Q(-2), Q(0), Q(1)), (Q(-3), Q(0), Q(1))}


def test_x_fourth_plus_1_is_irreducible_over_Q():
    p = _upoly(1, 0, 0, 0, 1)                      # x^4 + 1
    lead, factors = _assert_reconstructs(p)
    assert lead == Q(1)
    assert len(factors) == 1
    g, m = factors[0]
    assert m == 1
    assert g == p
    _assert_irreducible(g)


def test_reducible_quartic_x4_minus_5x2_plus_6_equals_x2_minus_2_times_x2_minus_3():
    p = _upoly(6, 0, -5, 0, 1)                     # x^4 - 5x^2 + 6
    lead, factors = _assert_reconstructs(p)
    _assert_distinct(factors)
    assert lead == Q(1)
    got = {tuple(g.coeffs): m for g, m in factors}
    assert got == {(Q(-2), Q(0), Q(1)): 1, (Q(-3), Q(0), Q(1)): 1}
    for g, _ in factors:
        _assert_irreducible(g)


# ------------------------------------------------------------------------------ leading coefficient / mixed multiplicities
def test_nonmonic_lead_scalar_is_pulled_out_exactly():
    x_minus_1 = _upoly(-1, 1)
    x2_plus_1 = _upoly(1, 0, 1)
    p = mul(UPoly([Q(2)], QRing()), mul(x_minus_1, x2_plus_1))   # 2(x-1)(x^2+1)
    lead, factors = _assert_reconstructs(p)
    assert lead == Q(2)
    got = {tuple(g.coeffs): m for g, m in factors}
    assert got == {(Q(-1), Q(1)): 1, (Q(1), Q(0), Q(1)): 1}


def test_negative_lead_scalar():
    x_minus_5 = _upoly(-5, 1)
    p = mul(UPoly([Q(-3)], QRing()), x_minus_5)     # -3(x-5)
    lead, factors = _assert_reconstructs(p)
    assert lead == Q(-3)
    assert factors == [(x_minus_5, 1)]


def test_repeated_irreducible_quadratic_x2_plus_1_squared():
    x2_plus_1 = _upoly(1, 0, 1)
    p = mul(x2_plus_1, x2_plus_1)                   # (x^2+1)^2
    lead, factors = _assert_reconstructs(p)
    assert lead == Q(1)
    assert len(factors) == 1
    g, m = factors[0]
    assert m == 2
    assert g == x2_plus_1
    _assert_irreducible(g)


def test_mixed_multiplicities_linear_squared_times_irreducible_quadratic_cubed_times_linear():
    x_minus_1 = _upoly(-1, 1)
    x2_plus_1 = _upoly(1, 0, 1)
    x_plus_5 = _upoly(5, 1)
    p = x_minus_1
    p = mul(p, x_minus_1)
    for _ in range(3):
        p = mul(p, x2_plus_1)
    p = mul(p, x_plus_5)
    lead, factors = _assert_reconstructs(p)
    _assert_distinct(factors)
    got = {tuple(g.coeffs): m for g, m in factors}
    assert got == {(Q(-1), Q(1)): 2, (Q(1), Q(0), Q(1)): 3, (Q(5), Q(1)): 1}


# -------------------------------------------------------------------------------- non-integer rational coefficients
def test_irreducible_factor_with_non_integer_rational_coefficients():
    # (x^2 - 1/2)(x^2 + 1) = x^4 + 1/2 x^2 - 1/2  — a genuinely non-integer-coefficient monic
    # irreducible quadratic factor, exercising the Kronecker search beyond integer-coefficient
    # candidates (the integer-cleared node search must still find it via the rational divmod_ check).
    x2_minus_half = _upoly(Q(-1, 2), 0, 1)
    x2_plus_1 = _upoly(1, 0, 1)
    p = mul(x2_minus_half, x2_plus_1)
    lead, factors = _assert_reconstructs(p)
    _assert_distinct(factors)
    assert lead == Q(1)
    assert len(factors) == 2
    got = {tuple(g.coeffs): m for g, m in factors}
    assert got[(Q(-1, 2), Q(0), Q(1))] == 1
    assert got[(Q(1), Q(0), Q(1))] == 1
    for g, _ in factors:
        _assert_irreducible(g)


# ---------------------------------------------------------------------------------------- many random-ish products
@pytest.mark.parametrize("pieces", [
    [(-7, 1)],                                       # x - 7
    [(-1, 1), (2, 1)],                                # (x-1)(x+2)
    [(1, 0, 1), (-1, 1)],                             # (x^2+1)(x-1)
    [(-2, 0, 1), (1, 1)],                             # (x^2-2)(x+1)
    [(-1, 1), (-1, 1), (-1, 1)],                      # (x-1)^3
    [(3, 1), (-4, 1), (1, 0, 1), (1, 0, 1)],          # (x+3)(x-4)(x^2+1)^2
])
def test_reconstruction_across_many_products(pieces):
    D = QRing()
    p = UPoly([Q(1)], D)
    for coeffs in pieces:
        p = mul(p, _upoly(*coeffs))
    lead, factors = _assert_reconstructs(p)
    _assert_distinct(factors)
    for g, m in factors:
        assert m >= 1
        assert g.degree() >= 1


# ---------------------------------------------------------------------------------------------- guards
def test_constant_polynomial_has_no_irreducible_factors():
    p = _upoly(5)
    lead, factors = factor_over_Q(p)
    assert lead == Q(5)
    assert factors == []


def test_negative_constant_polynomial():
    p = _upoly(-7)
    lead, factors = factor_over_Q(p)
    assert lead == Q(-7)
    assert factors == []


def test_zero_polynomial_raises_value_error():
    p = _upoly(0)
    with pytest.raises(ValueError):
        factor_over_Q(p)


def test_non_qring_domain_raises_value_error():
    p = UPoly([1, 0, 1], GFRing(5))                  # x^2 + 1 over GF(5), NOT QRing
    with pytest.raises(ValueError):
        factor_over_Q(p)


def test_returned_factors_are_all_monic():
    p = _upoly(6, 0, -5, 0, 1)                        # x^4 - 5x^2 + 6
    _, factors = factor_over_Q(p)
    for g, _ in factors:
        assert g.lead() == Q(1)


def test_non_integer_rational_coeff_factor_extra_check():
    x2_minus_half = _upoly(Q(-1, 2), 0, 1)
    x2_plus_1 = _upoly(1, 0, 1)
    p = mul(x2_minus_half, x2_plus_1)
    lead, factors = _assert_reconstructs(p)
    assert lead == Q(1)
    print("FACTORS:", [(g.coeffs, m) for g, m in factors])
    assert len(factors) == 2
