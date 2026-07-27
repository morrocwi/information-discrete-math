#!/usr/bin/env python3
"""Exact minimal polynomial of a rational matrix.

Run: PYTHONPATH=. python3 -m pytest tests/test_matrix_minpoly.py -q
"""

from __future__ import annotations

from fractions import Fraction as Q

import pytest

from idm.kernel.poly.coeffring import QRing
from idm.kernel.poly.eigen import characteristic_polynomial
from idm.kernel.poly.matrix_minpoly import eval_poly_at_matrix, minimal_polynomial
from idm.kernel.poly.univariate import UPoly, divmod_


def _is_zero_matrix(m):
    return all(Q(x) == 0 for row in m for x in row)


def _assert_annihilates_and_divides_charpoly(A):
    """The two REQUIRED checks for any minimal_polynomial result: m(A) == 0, and m | charpoly(A)."""
    m = minimal_polynomial(A)
    assert _is_zero_matrix(eval_poly_at_matrix(m, A))

    cp = characteristic_polynomial(A)
    q, r = divmod_(cp, m)
    assert r.is_zero()
    return m, cp


def test_repeated_eigenvalue_minpoly_lower_degree_than_charpoly():
    # 2*I_3: charpoly = (x-2)^3 (degree 3), but minpoly = x-2 (degree 1) since A already satisfies it.
    A = [[2, 0, 0], [0, 2, 0], [0, 0, 2]]
    m, cp = _assert_annihilates_and_divides_charpoly(A)

    assert m.coeffs == [Q(-2), Q(1)]                       # x - 2, monic degree 1
    assert cp.coeffs == [Q(-8), Q(12), Q(-6), Q(1)]         # (x-2)^3 = x^3-6x^2+12x-8
    assert m.degree() == 1 < cp.degree() == 3


def test_diagonal_two_distinct_eigenvalues_one_repeated():
    # diag(1,1,2): diagonalizable, minpoly = (x-1)(x-2) = x^2-3x+2 (degree 2, lower than charpoly's 3).
    A = [[1, 0, 0], [0, 1, 0], [0, 0, 2]]
    m, cp = _assert_annihilates_and_divides_charpoly(A)

    assert m.coeffs == [Q(2), Q(-3), Q(1)]                  # x^2 - 3x + 2
    assert cp.coeffs == [Q(-2), Q(5), Q(-4), Q(1)]           # (x-1)^2(x-2) = x^3-4x^2+5x-2
    assert m.degree() < cp.degree()


def test_companion_matrix_minpoly_equals_charpoly():
    # Companion matrix of x^2 - 5x + 6 = (x-2)(x-3): det(xI-C) = x^2-5x+6, cyclic -> minpoly == charpoly.
    A = [[0, -6], [1, 5]]
    m, cp = _assert_annihilates_and_divides_charpoly(A)

    assert cp.coeffs == [Q(6), Q(-5), Q(1)]
    assert m.coeffs == cp.coeffs
    assert m == cp


def test_1x1_matrix():
    A = [[5]]
    m, cp = _assert_annihilates_and_divides_charpoly(A)
    assert m.coeffs == [Q(-5), Q(1)]                        # x - 5
    assert m == cp


def test_non_square_raises_value_error():
    with pytest.raises(ValueError):
        minimal_polynomial([[1, 2, 3], [4, 5, 6]])
    with pytest.raises(ValueError):
        minimal_polynomial([[1, 2], [3, 4], [5, 6]])
    with pytest.raises(ValueError):
        minimal_polynomial([])


def test_eval_poly_at_matrix_requires_qring_poly():
    from idm.kernel.poly.coeffring import GFRing

    p = UPoly([1, 0, 1], GFRing(5))
    with pytest.raises(ValueError):
        eval_poly_at_matrix(p, [[1, 0], [0, 1]])
