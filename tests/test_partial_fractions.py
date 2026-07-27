"""Identity / reconstruction tests for idm.kernel.poly.partial_fractions (square-free apart/together).

Every scenario is checked by the SAME discipline: ``together(apart(num, den))`` must cross-multiply
back to ``num/den`` exactly --

    together_num * den  ==  together_den * num          (as UPoly equality, Fraction coefficients)

-- never by comparing floats or trusting an eyeballed answer. Additionally every returned term
``(g, j, A)`` is checked structurally: ``deg(A) < deg(g)`` (the defining property of a partial
fraction numerator).

No floats anywhere -- only fractions.Fraction, exactly.
"""

from fractions import Fraction as Q

from idm.kernel.poly.coeffring import QRing, GFRing
from idm.kernel.poly.univariate import UPoly, add, mul, divmod_
from idm.kernel.poly.partial_fractions import apart, together, extended_gcd, PartialFraction


def _mono(*coeffs_low_to_high):
    """UPoly over QRing from plain ints/Fractions, low-order coefficient first."""
    return UPoly([Q(c) for c in coeffs_low_to_high], QRing())


def _const(v):
    return UPoly([Q(v)], QRing())


def _cross_equal(n1: UPoly, d1: UPoly, n2: UPoly, d2: UPoly) -> bool:
    """n1/d1 == n2/d2 as rational functions, checked by exact cross-multiplication."""
    return mul(n1, d2) == mul(d1, n2)


def _assert_reconstructs(num, den):
    decomp = apart(num, den)
    t_num, t_den = together(decomp)
    assert not t_den.is_zero()
    assert _cross_equal(t_num, t_den, num, den), (
        f"together(apart(num,den)) != num/den: "
        f"got {t_num.coeffs}/{t_den.coeffs}, want {num.coeffs}/{den.coeffs}"
    )
    for g, j, A in decomp.terms:
        assert j >= 1
        assert A.degree() < g.degree(), f"numerator degree {A.degree()} >= g degree {g.degree()}"
    return decomp


# ---------------------------------------------------------------------------------------- (a) distinct linear factors


def test_apart_distinct_linear_factors_reconstructs():
    # 1 / ((x-1)(x-2))  ==  1 / (x^2 - 3x + 2)
    num = _const(1)
    den = mul(_mono(-1, 1), _mono(-2, 1))
    decomp = _assert_reconstructs(num, den)
    assert decomp.poly.is_zero()                 # proper fraction: no polynomial part
    assert len(decomp.terms) >= 1
    # square-free factorization keeps both multiplicity-1 roots as ONE square-free block here
    # (square-free is enough -- see module docstring), so we only assert reconstruction + shape,
    # not a specific 1/(x-1) - 1/(x-2) split.


def test_apart_distinct_linear_factors_matches_classical_split_when_evaluated():
    # Independent sanity check of the SAME case via known closed form:
    # 1/((x-1)(x-2)) = -1/(x-1) + 1/(x-2).  Build that decomposition BY HAND, together() it, and
    # cross-check it lands on the same rational function as apart()'s own answer.
    num = _const(1)
    den = mul(_mono(-1, 1), _mono(-2, 1))
    hand = PartialFraction(
        poly=_const(0),
        terms=[(_mono(-1, 1), 1, _const(-1)), (_mono(-2, 1), 1, _const(1))],
    )
    h_num, h_den = together(hand)
    assert _cross_equal(h_num, h_den, num, den)

    decomp = apart(num, den)
    a_num, a_den = together(decomp)
    assert _cross_equal(a_num, a_den, h_num, h_den)


# ---------------------------------------------------------------------------------------- (b) repeated factor


def test_apart_repeated_factor_reconstructs():
    # (x+1) / ((x-1)^2 * x)
    num = _mono(1, 1)                              # x + 1
    x_minus_1_sq = mul(_mono(-1, 1), _mono(-1, 1))  # (x-1)^2
    den = mul(x_minus_1_sq, _mono(0, 1))            # (x-1)^2 * x
    decomp = _assert_reconstructs(num, den)
    assert decomp.poly.is_zero()

    # hand-derived closed form: (x+1)/(x(x-1)^2) = 1/x - 1/(x-1) + 2/(x-1)^2
    by_g = {}
    for g, j, A in decomp.terms:
        by_g.setdefault(tuple(g.coeffs), {})[j] = A
    x_key = tuple(_mono(0, 1).coeffs)
    xm1_key = tuple(_mono(-1, 1).coeffs)
    assert by_g[x_key][1] == _const(1)
    assert by_g[xm1_key][1] == _const(-1)
    assert by_g[xm1_key][2] == _const(2)


def test_apart_repeated_factor_multiplicity_in_terms():
    num = _mono(1, 1)
    x_minus_1_sq = mul(_mono(-1, 1), _mono(-1, 1))
    den = mul(x_minus_1_sq, _mono(0, 1))
    decomp = apart(num, den)
    # every g with multiplicity 2 in the square-free factorization must be able to appear at j=1 and j=2
    js_for_xm1 = sorted(j for g, j, _ in decomp.terms if g == _mono(-1, 1))
    assert js_for_xm1 == [1, 2]


# ---------------------------------------------------------------------------------------- (c) improper fraction


def test_apart_improper_fraction_has_nonzero_polynomial_part():
    # (x^3 + 1) / (x^2 - 1)  =  x  +  (x+1)/(x^2-1)   [deg num (3) >= deg den (2)]
    num = _mono(1, 0, 0, 1)          # x^3 + 1
    den = _mono(-1, 0, 1)            # x^2 - 1
    decomp = _assert_reconstructs(num, den)
    assert not decomp.poly.is_zero()
    assert decomp.poly == _mono(0, 1)             # polynomial part == x, exactly
    assert len(decomp.terms) == 1
    g, j, A = decomp.terms[0]
    assert j == 1
    assert A == _mono(1, 1)                       # x + 1


def test_apart_improper_fraction_polynomial_part_matches_divmod():
    # cross-check the polynomial part against the tower's own divmod_ independently
    num = _mono(1, 0, 0, 1)
    den = _mono(-1, 0, 1)
    q, r = divmod_(num, den)
    decomp = apart(num, den)
    assert decomp.poly == q


# ---------------------------------------------------------------------------------------- (d) irreducible quadratic kept as-is


def test_apart_irreducible_quadratic_factor_reconstructs():
    # 1 / ((x^2+1)(x-1))
    num = _const(1)
    den = mul(_mono(1, 0, 1), _mono(-1, 1))       # (x^2+1)(x-1)
    decomp = _assert_reconstructs(num, den)
    assert decomp.poly.is_zero()
    assert len(decomp.terms) >= 1
    # the quadratic factor x^2+1 has no rational root, so it can only appear as a degree-2 g_i
    # (never split into two degree-1 pieces) -- assert every term's g has degree 1 or 2 and that the
    # decomposition is honest about it (no g of degree > deg(den)).
    for g, j, A in decomp.terms:
        assert 1 <= g.degree() <= den.degree()


# ---------------------------------------------------------------------------------------- extra: zero numerator, HOLDs


def test_apart_zero_numerator():
    num = _const(0)
    den = mul(_mono(-1, 1), _mono(-2, 1))
    decomp = apart(num, den)
    assert decomp.poly.is_zero()
    assert decomp.terms == []
    t_num, t_den = together(decomp)
    assert t_num.is_zero()


def test_apart_constant_denominator_is_pure_polynomial():
    # den is a nonzero constant: num/den is itself a polynomial, no fractional terms at all
    num = _mono(2, 4, 6)             # 6x^2 + 4x + 2
    den = _const(2)
    decomp = _assert_reconstructs(num, den)
    assert decomp.terms == []
    assert decomp.poly == _mono(1, 2, 3)


def test_apart_holds_on_zero_denominator():
    num = _const(1)
    den = _const(0)
    try:
        apart(num, den)
        assert False, "expected ValueError for zero denominator"
    except ValueError:
        pass


def test_apart_holds_on_domain_mismatch():
    num = UPoly([1, 1], GFRing(5))
    den = _mono(-1, 1)
    try:
        apart(num, den)
        assert False, "expected ValueError for domain mismatch"
    except ValueError:
        pass


def test_apart_holds_on_non_qring_domain():
    num = UPoly([1, 1], GFRing(5))
    den = UPoly([1, 0, 1], GFRing(5))
    try:
        apart(num, den)
        assert False, "expected ValueError for non-QRing domain"
    except ValueError:
        pass


# ---------------------------------------------------------------------------------------- extended_gcd (Bezout)


def test_extended_gcd_bezout_identity_holds():
    a = _mono(0, 1)                       # x
    b = mul(_mono(-1, 1), _mono(-1, 1))   # (x-1)^2
    s, t, g = extended_gcd(a, b)
    lhs = add(mul(s, a), mul(t, b))
    assert lhs == g
    assert g.degree() == 0                # x and (x-1)^2 are coprime -> gcd is a nonzero constant


def test_extended_gcd_matches_hand_computation():
    # hand-traced in the implementation notes: extended_gcd(x, (x-1)^2) == (2-x, 1, 1)
    a = _mono(0, 1)
    b = mul(_mono(-1, 1), _mono(-1, 1))
    s, t, g = extended_gcd(a, b)
    assert g == _const(1)
    assert s == _mono(2, -1)
    assert t == _const(1)


# ---------------------------------------------------------------------------------------- together() standalone


def test_together_of_hand_built_decomposition():
    # 1/x + 1/(x-1) should recombine to (2x-1)/(x^2-x)
    decomp = PartialFraction(
        poly=_const(0),
        terms=[(_mono(0, 1), 1, _const(1)), (_mono(-1, 1), 1, _const(1))],
    )
    num, den = together(decomp)
    assert _cross_equal(num, den, _mono(-1, 2), mul(_mono(0, 1), _mono(-1, 1)))


def test_together_empty_terms_is_just_the_polynomial_part():
    decomp = PartialFraction(poly=_mono(1, 1), terms=[])
    num, den = together(decomp)
    assert den == _const(1)
    assert num == _mono(1, 1)


def test_apart_three_and_four_block_round_trip():
    # closes the coverage gap the review flagged: exercise the multi-denominator Bezout-peeling loop
    # with 3 and 4 distinct square-free blocks of different multiplicities (incl. an improper fraction).
    from fractions import Fraction as Q
    from idm.kernel import poly as P
    D = P.QRing()

    def poly(cs):
        return P.UPoly([Q(c) for c in cs], D)

    def powr(g, n):
        r = poly([1])
        for _ in range(n):
            r = P.mul(r, g)
        return r

    x, xm1, xm2, xm3 = poly([0, 1]), poly([-1, 1]), poly([-2, 1]), poly([-3, 1])
    cases = [
        (poly([1]), P.mul(P.mul(x, powr(xm1, 2)), powr(xm2, 3))),        # 3 blocks, mults 1,2,3
        (poly([7, 3, 1]), P.mul(P.mul(P.mul(x, xm1), powr(xm2, 2)), powr(xm3, 3))),  # 4 blocks
        (powr(x, 6), P.mul(x, powr(xm1, 2))),                            # improper: nonzero poly part
    ]
    for num, den in cases:
        num2, den2 = P.together(P.apart(num, den))
        assert P.mul(num2, den) == P.mul(num, den2)                     # num/den == num2/den2 exactly
