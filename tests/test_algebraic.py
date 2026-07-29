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


def test_wp13_exact_eigenvalues_are_algebraic_objects():
    """WP13: exact real eigenvalues as algebraic objects + multiplicity, no Durand–Kerner."""
    import idm
    # symmetric integer matrix with rational eigenvalues 1, 3
    r = idm.solve({"kind": "exact_eigenvalues", "matrix": [[2, 1], [1, 2]]})["value"]
    assert r["completeness"] == "complete" and r["num_complex"] == 0
    assert [e["rational_value"] for e in r["real_eigenvalues"]] == ["1", "3"]
    # companion of x^2-x-1: golden-ratio eigenvalues, irrational, exact min-poly, both real
    g = idm.solve({"kind": "exact_eigenvalues", "matrix": [[0, 1], [1, 1]]})["value"]
    assert g["num_complex"] == 0 and len(g["real_eigenvalues"]) == 2
    assert all(e["min_poly"] == ["-1", "-1", "1"] and not e["is_rational"] for e in g["real_eigenvalues"])
    # rotation matrix: 0 real eigenvalues, 2 complex — none faked
    c = idm.solve({"kind": "exact_eigenvalues", "matrix": [[0, -1], [1, 0]]})["value"]
    assert c["real_eigenvalues"] == [] and c["num_complex"] == 2 and c["completeness"] == "real_complete"
    # multiplicity: diag(2,2,3) → eigenvalue 2 mult 2, 3 mult 1
    d = idm.solve({"kind": "exact_eigenvalues", "matrix": [[2,0,0],[0,2,0],[0,0,3]]})["value"]
    assert {e["rational_value"]: e["multiplicity"] for e in d["real_eigenvalues"]} == {"2": 2, "3": 1}
    # never lose an eigenvalue
    assert d["num_real_with_multiplicity"] + d["num_complex"] == d["size"]
def test_wp6_symbolic_solve_returns_complete_real_roots():
    """WP6: symbolic_solve on a univariate ℚ-polynomial returns the COMPLETE exact real solution set —
    no lost irrational roots — with multiplicity and an honest complex count (was: rational-only)."""
    import idm
    # x^3 - 2: the real root ∛2 must appear exactly (previously dropped as 'use poly_roots')
    r = idm.solve({"kind": "symbolic_solve", "expr": "x**3-2", "var": "x"})["value"]
    assert r["completeness"] == "real_complete" and r["num_complex"] == 2
    assert len(r["real_solutions"]) == 1
    assert r["real_solutions"][0]["min_poly"] == ["-2", "0", "0", "1"]      # x^3 - 2, exact
    assert not r["real_solutions"][0]["is_rational"]
    # (x-1)(x-2)(x-3): three rational roots, complete, none lost
    r2 = idm.solve({"kind": "symbolic_solve", "expr": "x**3-6*x**2+11*x-6", "var": "x"})["value"]
    assert r2["completeness"] == "complete" and r2["num_complex"] == 0
    assert [s["exact_value"] for s in r2["real_solutions"]] == ["1", "2", "3"]
    # no root is ever lost: real (with mult) + complex == degree
    for expr in ("x**3-2", "x**4-5*x**2+4", "x**5+x+1"):
        v = idm.solve({"kind": "symbolic_solve", "expr": expr, "var": "x"})["value"]
        real_mult = sum(s["multiplicity"] for s in v["real_solutions"])
        assert real_mult + v["num_complex"] == v["degree"]


def test_wp13_large_matrix_holds_not_hangs():
    """Reviewer regression: exact_eigenvalues on a big matrix (large char-poly coefficients) must HOLD via
    the factorization budget, NOT hang. The root cause was rational_roots' O(m) divisor helper running
    before the budget; it is now O(√m). This must return within a couple of seconds."""
    import idm
    M = [[((i * 7 + j * 3 - 5) % 19) - 9 for j in range(10)] for i in range(10)]   # generic 10×10 ints
    r = idm.solve({"kind": "exact_eigenvalues", "matrix": M})
    assert r["status"] in ("ok", "HOLD")     # returns (does not hang); HOLD is the honest Increment-1 answer


def test_wp11_ode_resolves_real_algebraic_characteristic_roots():
    """WP11: a constant-coeff linear ODE whose characteristic polynomial has an irreducible degree-≥3
    factor now resolves that factor's REAL roots exactly (was: HOLD on the whole factor)."""
    import idm
    # char r^3 - 3r + 1: three real irrational roots (casus irreducibilis) → fully SOLVED now
    r = idm.solve({"kind": "linear_ode", "coeffs": [1, -3, 0, 1]})["value"]
    assert r["solution_status"] == "solved" and len(r["basis"]) == 3
    assert all(b["type"] == "real_algebraic" and b["root_min_poly"] == ["1", "-3", "0", "1"] for b in r["basis"])
    # char r^3 - 2: real root ∛2 resolved exactly; the 2 complex roots honestly left for a later increment
    r2 = idm.solve({"kind": "linear_ode", "coeffs": [-2, 0, 0, 1]})["value"]
    assert r2["solution_status"] == "partial"
    assert len(r2["basis"]) == 1 and r2["basis"][0]["root_min_poly"] == ["-2", "0", "0", "1"]
    assert "complex" in r2["unresolved"][0]


def test_wp11_ode_repeated_factor_complex_count_and_high_degree_hold():
    """Reviewer regressions: (B) complex count of a repeated irreducible factor is multiplicity-weighted;
    (C) a hard high-degree characteristic polynomial HOLDs (budget), not hang."""
    import idm, time
    from idm.kernel.poly.univariate import UPoly, mul
    from idm.kernel.poly.coeffring import QRing
    D = QRing()
    def PP(cs): return UPoly([Q(c) for c in cs], D)
    # (r^3-2)^2: multiplicity 2, one real root ∛2 → real basis 2, complex count 4 (2 pairs × mult 2)
    sq = mul(PP([-2,0,0,1]), PP([-2,0,0,1]))
    r = idm.solve({"kind": "linear_ode", "coeffs": [int(c) for c in sq.coeffs]})["value"]
    assert r["solution_status"] == "partial" and len(r["basis"]) == 2
    assert "4 complex" in r["unresolved"][0] and "multiplicity 2" in r["unresolved"][0]
    # r^10-2 (irreducible degree 10): must return partial within a few seconds, not hang
    t = time.time()
    r2 = idm.solve({"kind": "linear_ode", "coeffs": [-2,0,0,0,0,0,0,0,0,0,1]})["value"]
    assert r2["solution_status"] == "partial" and time.time() - t < 20


def test_all_roots_real_and_complex_complete():
    """Complex-root increment: all_roots returns every root (real + complex) as exact rational-rectangle
    enclosures, count == degree, conjugate-paired, each verified. Completes degree-n → all n roots."""
    import idm
    def rr(coeffs): return idm.solve({"kind": "all_roots", "coeffs": coeffs})["value"]
    r = rr([1, 0, 1])                                  # x^2+1 -> ±i
    assert r["num_real"] == 0 and r["num_complex"] == 2 and len(r["roots"]) == 2
    r2 = rr([-2, 0, 0, 1])                             # x^3-2 -> ∛2 + complex pair
    assert r2["num_real"] == 1 and r2["num_complex"] == 2
    r3 = rr([-1, 0, 0, 0, 1])                          # x^4-1 -> ±1, ±i
    assert r3["num_real"] == 2 and r3["num_complex"] == 2
    # generic distinct-root polynomials at higher degree (NOT just lucky roots-of-unity structure)
    generic = [[1,0,1],[-2,0,0,1],[5,-2,1],[1,0,0,0,1],[-6,11,-6,1],
               [10,-14,10,-4,1],   # (x^2-2x+2)(x^2-2x+5): 1±i, 1±2i
               [-1,0,0,0,0,1],     # x^5-1: 1 real + 4 complex
               [-1,0,0,0,0,0,1],   # x^6-1: 2 real + 4 complex
               [1,1,0,1]]          # x^3+x+1: 1 real + 2 complex
    for coeffs in generic:
        v = rr(coeffs)
        assert v["num_real"] + v["num_complex"] == v["degree"]    # complete: no root lost
        assert all(x["verified"] for x in v["roots"])             # each Re/Im part substitutes back exactly
    # a repeated-root polynomial fails closed (HOLD) — multiplicity is a declared later increment
    assert idm.solve({"kind": "all_roots", "coeffs": [-1, 3, -3, 1]})["status"] == "HOLD"   # (x-1)^3
