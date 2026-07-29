"""Tests for idm.kernel.poly.algebraic — exact real algebraic-number arithmetic (WP2, Increment 1).

Ground truth is the minimal polynomial (checked against known closed forms and, where available, against
SymPy's ``minimal_polynomial`` as an independent comparator) plus the WP2 closure criterion: every result
substitutes back to satisfy its own minimal polynomial exactly.
"""
import os
import sys
from fractions import Fraction as Q

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from idm.kernel.poly.algebraic import AlgReal, AlgebraicHOLD


def _mp(a):
    return [Q(c) for c in a.min_poly_coeffs()]


SQRT2 = lambda: AlgReal.rootof([-2, 0, 1], 1)
SQRT3 = lambda: AlgReal.rootof([-3, 0, 1], 1)
CBRT2 = lambda: AlgReal.rootof([-2, 0, 0, 1], 0)
GOLDEN = lambda: AlgReal.rootof([-1, -1, 1], 1)


def test_construct_and_verify():
    for a in (SQRT2(), SQRT3(), CBRT2(), GOLDEN(), AlgReal.from_rational(Q(3, 7))):
        assert a.verify(), f"{a!r} failed its substitute-back certificate"


def test_known_minimal_polynomials():
    assert _mp(SQRT2() + SQRT3()) == [Q(1), 0, Q(-10), 0, Q(1)]      # x^4 - 10x^2 + 1
    assert _mp(SQRT2() * SQRT3()) == [Q(-6), 0, Q(1)]                 # sqrt6: x^2 - 6
    assert _mp(SQRT2() + 1) == [Q(-1), Q(-2), Q(1)]                   # x^2 - 2x - 1
    assert _mp(SQRT2() - 1) == [Q(-1), Q(2), Q(1)]                    # x^2 + 2x - 1
    assert _mp(SQRT2().inv()) == [Q(-1, 2), 0, Q(1)]                  # x^2 - 1/2
    assert _mp(CBRT2() * CBRT2()) == [Q(-4), 0, 0, Q(1)]             # x^3 - 4
    assert _mp(GOLDEN()) == [Q(-1), Q(-1), Q(1)]                      # x^2 - x - 1


def test_substitute_back_holds_for_results():
    """The WP2 closure criterion: every arithmetic result satisfies its own minimal polynomial exactly."""
    a, b = SQRT2(), SQRT3()
    for r in (a + b, a - b, a * b, a / b, a.inv(), -a, a ** 3, CBRT2() * CBRT2()):
        assert r.verify()


def test_power_substitutes_to_the_defining_relation():
    assert (CBRT2() ** 3) == AlgReal.from_rational(2)                 # (2^{1/3})^3 = 2, exactly
    assert (SQRT2() ** 2) == AlgReal.from_rational(2)
    s = SQRT2()
    assert (s * s * s) == (s ** 3)


def test_exact_ordering_and_equality_no_floats():
    assert SQRT2() < SQRT3()
    assert SQRT2() == AlgReal.rootof([-2, 0, 1], 1)                   # same number, same min poly
    assert not (SQRT2() == SQRT3())
    assert not (AlgReal.from_rational(Q(3, 2)) < SQRT2())            # 1.5 < 1.414… is false
    assert SQRT2() < AlgReal.from_rational(Q(3, 2))                   # 1.414… < 1.5 is true
    assert AlgReal.from_rational(Q(7, 5)) < SQRT2()                   # 1.4 < 1.414…
    # the two real roots of x^2-2 are -sqrt2 < sqrt2
    lo, hi = AlgReal.real_roots([-2, 0, 1])
    assert lo < hi and lo == -SQRT2() and hi == SQRT2()


def test_sign():
    assert SQRT2().sign() == 1
    assert (-SQRT2()).sign() == -1
    assert (SQRT2() - SQRT2()).sign() == 0
    assert AlgReal.from_rational(0).sign() == 0


def test_rational_fast_path_stays_rational():
    half = AlgReal.from_rational(Q(1, 2))
    assert half.is_rational and half.as_rational() == Q(1, 2)
    assert (half + AlgReal.from_rational(Q(1, 3))).as_rational() == Q(5, 6)
    assert (half * AlgReal.from_rational(4)).as_rational() == Q(2)


def test_division_by_zero_holds():
    with pytest.raises(AlgebraicHOLD):
        AlgReal.from_rational(0).inv()
    with pytest.raises(AlgebraicHOLD):
        SQRT2() / AlgReal.from_rational(0)
    with pytest.raises(AlgebraicHOLD):
        (SQRT2() - SQRT2()).inv()                                    # equals 0 → HOLD, not a fake number


def test_real_roots_count_and_isolation():
    # x^2+1 has no real roots
    assert AlgReal.real_roots([1, 0, 1]) == []
    # (x-1)(x-2)(x-3) has 3 rational real roots
    roots = AlgReal.real_roots([-6, 11, -6, 1])
    assert [r.as_rational() for r in roots] == [Q(1), Q(2), Q(3)]
    with pytest.raises(AlgebraicHOLD):
        AlgReal.rootof([-2, 0, 1], 5)                                # out-of-range index


def test_to_float_is_correct_for_rational_results():
    """Reviewer regression (bug 1): to_float / the public `approx` must equal the exact value for a
    RATIONAL result, not the artificial (r-1, r] lower endpoint."""
    assert float(AlgReal.from_rational(2).to_float(20)) == 2.0
    assert float(AlgReal.from_rational(0).to_float(20)) == 0.0
    assert float(AlgReal.real_roots([-3, -2, 1])[0].to_float(10)) == -1.0   # roots of x²-2x-3 are -1, 3
    assert float((SQRT2() - SQRT2()).to_float(20)) == 0.0                    # α−α = 0 exactly
    assert float((SQRT2() * SQRT2()).to_float(20)) == 2.0                    # α·α = 2 exactly
    assert abs(float(SQRT2().to_float(20)) - 2 ** 0.5) < 1e-12               # irrational still accurate


def test_hard_high_degree_holds_not_hangs():
    """Reviewer regression (bug 2): a high-degree combination whose minimal-polynomial isolation would
    run Kronecker's search unboundedly must HOLD (deterministic budget), never hang."""
    a = AlgReal.rootof([-6, -5, 5, 4, 1], 0)      # a real root of a degree-4 polynomial
    b = AlgReal.rootof([-6, -3, 1], 1)            # a real root of a degree-2 polynomial
    with pytest.raises(AlgebraicHOLD):
        a * b                                     # degree-8 result → exceeds the Increment-1 budget → HOLD


def test_differential_against_sympy_minimal_polynomial():
    """Cross-check the minimal polynomial of algebraic combinations against SymPy (comparator only)."""
    sympy = pytest.importorskip("sympy")
    x = sympy.symbols("x")

    def sympy_minpoly(expr):
        p = sympy.minimal_polynomial(expr, x, polys=True)
        # monic, low->high Fraction coeffs
        cs = p.all_coeffs()[::-1]
        lead = cs[-1]
        return [Q(int(c.p), int(c.q)) if hasattr(c, "p") else Q(int(c)) for c in
                [sympy.nsimplify(ci / lead) for ci in cs]]

    cases = [
        (SQRT2() + SQRT3(), sympy.sqrt(2) + sympy.sqrt(3)),
        (SQRT2() * SQRT3(), sympy.sqrt(6)),
        (SQRT2() + AlgReal.from_rational(1), sympy.sqrt(2) + 1),
        (CBRT2() * CBRT2(), sympy.cbrt(2) ** 2),
        (SQRT2().inv(), 1 / sympy.sqrt(2)),
        (SQRT2() - SQRT3(), sympy.sqrt(2) - sympy.sqrt(3)),
    ]
    for ours, sy in cases:
        assert _mp(ours) == sympy_minpoly(sy), f"minpoly mismatch for {ours!r}"


def test_real_roots_with_multiplicity_no_durand_kerner():
    """WP3 real-part closure: every real root exact + multiplicity, sorted, no float; complex counted."""
    # (x-1)^2 (x^2-2) (x^2+1) : real roots -sqrt2(m1), 1(m2), sqrt2(m1); 2 complex (±i)
    from idm.kernel.poly.univariate import UPoly, mul
    from idm.kernel.poly.coeffring import QRing
    D = QRing()
    def PP(cs): return UPoly([Q(c) for c in cs], D)
    poly = mul(mul(mul(PP([-1,1]),PP([-1,1])), PP([-2,0,1])), PP([1,0,1]))
    rm = AlgReal.real_roots_with_multiplicity([int(c) for c in poly.coeffs])
    assert [(str(r.as_rational()) if r.is_rational else _mp(r), m) for r, m in rm] == [
        ([Q(-2),0,Q(1)], 1), ("1", 2), ([Q(-2),0,Q(1)], 1)]
    assert all(r.verify() for r, _ in rm)
    real_mult = sum(m for _, m in rm)
    assert real_mult == 4 and poly.degree() - real_mult == 2   # 2 complex roots, none faked


def test_all_real_roots_high_degree_holds_not_hangs():
    """Reviewer regression: the multiplicity/real-root path must fail closed (budget → HOLD), not hang,
    on a hard high-degree generic polynomial — same guard as the arithmetic path."""
    with pytest.raises(AlgebraicHOLD):
        AlgReal.real_roots_with_multiplicity([3,-5,7,-11,13,-17,19,-23,29,-31,37])   # degree 10, generic
    with pytest.raises(AlgebraicHOLD):
        AlgReal.real_roots([3,-5,7,-11,13,-17,19,-23,29,-31,37])
