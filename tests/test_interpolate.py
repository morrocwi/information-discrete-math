"""Identity / reconstruction tests for idm.kernel.poly.interpolate (exact ℚ interpolation).

Every test either:
  (a) evaluates the returned polynomial EXACTLY back at the source x_i and checks it equals y_i
      (via univariate._eval_at, Horner, exact Fraction arithmetic), or
  (b) checks the degree bound (< number of points), or
  (c) checks lagrange(points) == newton(points) as UPoly objects — two independently-derived
      constructions must land on the identical unique interpolating polynomial, or
  (d) reconstructs a KNOWN polynomial (x^3 - 2x + 1) from samples of it and checks the exact
      coefficient list, or
  (e) checks the honest ValueError on duplicate x_i / empty input.

No floats anywhere — only fractions.Fraction, exactly.
"""

from fractions import Fraction as Q

import pytest

from idm.kernel.poly.coeffring import QRing
from idm.kernel.poly.univariate import UPoly, _eval_at
from idm.kernel.poly.interpolate import lagrange, newton


def _upoly(*coeffs_low_to_high):
    """Build a UPoly over QRing from plain ints/Fractions, low-order coefficient first."""
    return UPoly([Q(c) for c in coeffs_low_to_high], QRing())


def _assert_exact_fraction_coeffs(p):
    for c in p.coeffs:
        assert isinstance(c, Q), f"expected exact Fraction coefficient, got {type(c)}: {c!r}"


# ---------------------------------------------------------------------------------------- exact evaluation back through the source points


@pytest.mark.parametrize("method", [lagrange, newton])
def test_evaluates_exactly_at_every_source_point_generic(method):
    # A generic, non-trivial rational point set (not evenly spaced, includes negative/fractional x, y).
    points = [(Q(-2), Q(7)), (Q(0), Q(1, 2)), (Q(1, 3), Q(-5)), (Q(4), Q(11))]
    p = method(points)
    _assert_exact_fraction_coeffs(p)
    for x, y in points:
        got = _eval_at(p, x)
        assert isinstance(got, Q)
        assert got == y


@pytest.mark.parametrize("method", [lagrange, newton])
def test_evaluates_exactly_at_every_source_point_integer_grid(method):
    # f(x) = x^3 - 2x + 1 sampled at x = 0,1,2,3 (degree 3, exactly 4 points -> exact fit).
    points = [(Q(0), Q(1)), (Q(1), Q(0)), (Q(2), Q(5)), (Q(3), Q(22))]
    p = method(points)
    for x, y in points:
        assert _eval_at(p, x) == y


@pytest.mark.parametrize("method", [lagrange, newton])
def test_evaluates_exactly_single_point_constant(method):
    points = [(Q(5), Q(-3))]
    p = method(points)
    assert p.degree() == 0
    assert _eval_at(p, Q(5)) == Q(-3)
    assert _eval_at(p, Q(999)) == Q(-3)     # a constant polynomial: same value everywhere


# ---------------------------------------------------------------------------------------- degree bound


@pytest.mark.parametrize("method", [lagrange, newton])
@pytest.mark.parametrize(
    "points",
    [
        [(Q(0), Q(1))],
        [(Q(0), Q(1)), (Q(1), Q(2))],
        [(Q(0), Q(1)), (Q(1), Q(2)), (Q(2), Q(9))],
        [(Q(-1), Q(4)), (Q(0), Q(1)), (Q(1), Q(0)), (Q(2), Q(5)), (Q(5), Q(116))],
    ],
)
def test_degree_below_number_of_points(method, points):
    p = method(points)
    assert p.degree() < len(points)


def test_degree_can_drop_below_bound_when_points_are_collinear():
    # 3 points that are exactly on a line: the degree-<3 interpolant is degree 1, not 2.
    points = [(Q(0), Q(1)), (Q(1), Q(3)), (Q(2), Q(5))]      # y = 2x + 1
    for method in (lagrange, newton):
        p = method(points)
        assert p.degree() == 1
        assert p.coeffs == [Q(1), Q(2)]


# ---------------------------------------------------------------------------------------- lagrange == newton (uniqueness)


@pytest.mark.parametrize(
    "points",
    [
        [(Q(5), Q(-3))],
        [(Q(0), Q(1)), (Q(1), Q(2))],
        [(Q(-2), Q(7)), (Q(0), Q(1, 2)), (Q(1, 3), Q(-5)), (Q(4), Q(11))],
        [(Q(0), Q(1)), (Q(1), Q(0)), (Q(2), Q(5)), (Q(3), Q(22))],
        [(Q(-1), Q(4)), (Q(0), Q(1)), (Q(1), Q(0)), (Q(2), Q(5)), (Q(5), Q(116))],
    ],
)
def test_lagrange_equals_newton(points):
    p_lagrange = lagrange(points)
    p_newton = newton(points)
    assert p_lagrange == p_newton
    assert p_lagrange.coeffs == p_newton.coeffs


# ---------------------------------------------------------------------------------------- recovering a KNOWN polynomial


@pytest.mark.parametrize("method", [lagrange, newton])
def test_recovers_known_cubic_from_four_samples(method):
    # f(x) = x^3 - 2x + 1  (coeffs low-to-high: [1, -2, 0, 1])
    def f(x):
        return x**3 - 2 * x + 1

    xs = [Q(0), Q(1), Q(2), Q(3)]
    points = [(x, f(x)) for x in xs]
    p = method(points)
    assert p.coeffs == [Q(1), Q(-2), Q(0), Q(1)]
    assert p == _upoly(1, -2, 0, 1)


@pytest.mark.parametrize("method", [lagrange, newton])
def test_recovers_known_cubic_from_four_non_grid_samples(method):
    # Same cubic, sampled at a DIFFERENT (non-integer, non-consecutive) x set -> same unique cubic back.
    def f(x):
        return x**3 - 2 * x + 1

    xs = [Q(-3), Q(-1, 2), Q(2), Q(7)]
    points = [(x, f(x)) for x in xs]
    p = method(points)
    assert p.coeffs == [Q(1), Q(-2), Q(0), Q(1)]


# ---------------------------------------------------------------------------------------- honest failure: duplicate x_i / empty input


@pytest.mark.parametrize("method", [lagrange, newton])
def test_duplicate_x_raises_value_error(method):
    points = [(Q(0), Q(1)), (Q(1), Q(2)), (Q(0), Q(99))]     # x=0 repeated
    with pytest.raises(ValueError):
        method(points)


@pytest.mark.parametrize("method", [lagrange, newton])
def test_empty_points_raises_value_error(method):
    with pytest.raises(ValueError):
        method([])


@pytest.mark.parametrize("method", [lagrange, newton])
def test_duplicate_x_with_equal_y_still_raises(method):
    # Even a "consistent" duplicate (same y at the repeated x) is rejected: the construction still
    # divides by (x_i - x_j) = 0, so it must HOLD honestly rather than silently drop a point.
    points = [(Q(2), Q(4)), (Q(2), Q(4)), (Q(3), Q(9))]
    with pytest.raises(ValueError):
        method(points)
