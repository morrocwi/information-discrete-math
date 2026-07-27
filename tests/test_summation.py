"""Identity / reconstruction tests for Gosper's algorithm (idm.kernel.poly.summation).

Ground truth throughout is TELESCOPING: for every summable case we check the general defining
identity

    R(n+1) * r(n) - R(n) == 1                                                            (*)

purely as an EXACT POLYNOMIAL identity (cross-multiplied, no division, no float -- see the
`_verify_certificate_identity` helper), which is equivalent to S(n+1)-S(n)=t(n) for every
hypergeometric t with ratio r = num/den and S = R * t (derivation in summation.py's docstring).
Where a genuinely closed-form t(n) is available (t(n)=n, t(n)=n*n!) we ALSO cross-check the
certificate numerically against exact Fraction evaluation of the known closed form, as a second,
independent confirmation.
"""

from fractions import Fraction
import math

import pytest

from idm.kernel.poly.coeffring import QRing
from idm.kernel.poly.univariate import UPoly, add, mul
from idm.kernel.poly.summation import gosper_sum, gp_normal_form, shift

Q = QRing()


def P(*coeffs):
    """UPoly over QRing from low-order-first int/Fraction coefficients."""
    return UPoly([Fraction(c) for c in coeffs], Q)


def _neg(poly: UPoly) -> UPoly:
    return UPoly([Q.neg(c) for c in poly.coeffs], Q)


def _verify_certificate_identity(num: UPoly, den: UPoly, cert_num: UPoly, cert_den: UPoly):
    """Cross-multiplied, division-free check of R(n+1)*r(n) - R(n) == 1, i.e.

        shift(Rn,1)*p*Rd - Rn*shift(Rd,1)*q  ==  shift(Rd,1)*q*Rd

    exactly as UPoly equality (== compares domain and trimmed coefficient lists).
    """
    p, q = num, den
    Rn, Rd = cert_num, cert_den
    Rn1, Rd1 = shift(Rn, 1), shift(Rd, 1)
    lhs = add(mul(Rn1, mul(p, Rd)), _neg(mul(Rn, mul(Rd1, q))))
    rhs = mul(Rd1, mul(q, Rd))
    assert lhs == rhs, f"Gosper certificate identity failed: {lhs.coeffs} != {rhs.coeffs}"


# ------------------------------------------------------------------------------------------------
# REQUIRED: t(n) = n.  ratio r(n) = t(n+1)/t(n) = (n+1)/n.  Known closed form S(n) = n(n-1)/2.
# ------------------------------------------------------------------------------------------------
def test_gosper_sum_n_matches_telescoping_closed_form():
    num, den = P(1, 1), P(0, 1)              # p(n) = n+1, q(n) = n
    result = gosper_sum(num, den)

    # (1) general symbolic identity, no t(n) ever materialized:
    _verify_certificate_identity(num, den, result["num"], result["den"])

    # (2) independent numeric check against the textbook closed form S(n) = n(n-1)/2,
    #     using t(n) = n directly (an actual Python function this time, Fraction-exact):
    def t(n):
        return Fraction(n)

    def R(n):
        # evaluate the returned rational-function certificate at integer n
        Rn, Rd = result["num"], result["den"]

        def ev(poly, x):
            acc = Fraction(0)
            for c in reversed(poly.coeffs):
                acc = acc * x + c
            return acc

        return ev(Rn, Fraction(n)) / ev(Rd, Fraction(n))

    for n in range(1, 8):
        S_n = R(n) * t(n)
        S_n1 = R(n + 1) * t(n + 1)
        assert S_n1 - S_n == t(n)
        assert S_n == Fraction(n * (n - 1), 2)          # the known closed form, exactly


# ------------------------------------------------------------------------------------------------
# REQUIRED (second summable term): t(n) = n * n!.  ratio r(n) = (n+1)^2 / n.
# Closed form (classic telescoping identity k*k! = (k+1)! - k!): S(n) = n!  (choosing the additive
# constant that makes S a pure hypergeometric multiple of t, i.e. S(n)/t(n) = 1/n, a rational fn).
# ------------------------------------------------------------------------------------------------
def test_gosper_sum_n_factorial_matches_telescoping_closed_form():
    num, den = P(1, 2, 1), P(0, 1)           # p(n) = (n+1)^2 = n^2+2n+1, q(n) = n
    result = gosper_sum(num, den)

    _verify_certificate_identity(num, den, result["num"], result["den"])

    # certificate should be exactly R(n) = 1/n
    assert result["num"] == P(1)
    assert result["den"] == P(0, 1)

    def t(n):
        return n * math.factorial(n)

    def R(n):
        return Fraction(1, n)

    for n in range(1, 8):
        S_n = R(n) * t(n)
        S_n1 = R(n + 1) * t(n + 1)
        assert S_n1 - S_n == t(n)
        assert S_n == math.factorial(n)                 # S(n) = n!, exactly


# ------------------------------------------------------------------------------------------------
# REQUIRED: non-summable term -- t(n) = 1/n (harmonic term). ratio r(n) = t(n+1)/t(n) = n/(n+1).
# The indefinite sum of 1/n is H_n, the harmonic numbers, which are NOT hypergeometric: Gosper
# must HOLD (ValueError), never return a wrong/fabricated certificate.
# ------------------------------------------------------------------------------------------------
def test_gosper_sum_harmonic_term_holds():
    num, den = P(0, 1), P(1, 1)              # p(n) = n, q(n) = n+1
    with pytest.raises(ValueError):
        gosper_sum(num, den)


# ------------------------------------------------------------------------------------------------
# Bonus sanity: t(n) = 1 (pure constant term, the trivial "sum of a constant" case). r(n) = 1.
# Closed form S(n) = n.
# ------------------------------------------------------------------------------------------------
def test_gosper_sum_constant_term():
    num, den = P(1), P(1)
    result = gosper_sum(num, den)
    _verify_certificate_identity(num, den, result["num"], result["den"])
    assert result["num"] == P(0, 1)          # R(n) = n
    assert result["den"] == P(1)

    def t(n):
        return Fraction(1)

    for n in range(0, 6):
        R_n = Fraction(n)
        R_n1 = Fraction(n + 1)
        S_n, S_n1 = R_n * t(n), R_n1 * t(n + 1)
        assert S_n1 - S_n == t(n)
        assert S_n == n


# ------------------------------------------------------------------------------------------------
# gp_normal_form reconstruction: r(n) == a(n)/b(n) * c(n+1)/c(n) exactly, cross-multiplied,
# for every case above (independent check of step 2 alone, isolated from step 3).
# ------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("num,den", [
    (P(1, 1), P(0, 1)),          # (n+1)/n
    (P(1, 2, 1), P(0, 1)),       # (n+1)^2/n
    (P(0, 1), P(1, 1)),          # n/(n+1)  (a case where NO shift is needed: a=p,b=q,c=1)
    (P(1), P(1)),                # 1/1
])
def test_gp_normal_form_reconstructs_ratio(num, den):
    a, b, c = gp_normal_form(num, den)
    c1 = shift(c, 1)
    # p(n)*b(n)*c(n) == q(n)*a(n)*c(n+1)   (cross-multiplied r = a/b * c(n+1)/c(n))
    lhs = mul(num, mul(b, c))
    rhs = mul(den, mul(a, c1))
    assert lhs == rhs


# ------------------------------------------------------------------------------------------------
# HOLD discipline on malformed input -- never silently produce a wrong answer.
# ------------------------------------------------------------------------------------------------
def test_gosper_sum_zero_denominator_raises():
    with pytest.raises(ZeroDivisionError):
        gosper_sum(P(1), P(0))


def test_gosper_sum_zero_numerator_raises():
    with pytest.raises(ValueError):
        gosper_sum(P(0), P(1))
