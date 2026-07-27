"""Exact eigenvalues of a rational matrix (pillar P1.4, on the Wave-5 tower).

The characteristic polynomial ``det(x·I − A)`` is built EXACTLY over ℚ by the Faddeev–LeVerrier
recurrence (only rational add/mul/trace — no division of the matrix, no float), and its REAL eigenvalues
are then isolated exactly by :func:`idm.kernel.poly.univariate.isolate_real_roots` (Sturm bisection).
Every eigenvalue is a rational half-open interval ``(lo, hi]`` that provably brackets exactly one real
eigenvalue — refinable to any rational width, still exact, never a float and never a continuum readout.

Complex eigenvalues are not enumerated (that needs a splitting field); ``real_eigenvalues`` reports the
real ones with their algebraic multiplicity and honestly says how many eigenvalues remain complex.
"""

from __future__ import annotations

from fractions import Fraction as Q
from typing import List, Tuple

from .coeffring import QRing
from .univariate import UPoly, count_real_roots, isolate_real_roots


def _square_rational(matrix) -> List[List[Q]]:
    rows = [list(r) for r in matrix]
    n = len(rows)
    if n == 0 or any(len(r) != n for r in rows):
        raise ValueError("matrix must be square and non-empty")
    return [[Q(x) for x in r] for r in rows]


def _matmul(a, b):
    n = len(a)
    return [[sum(a[i][t] * b[t][j] for t in range(n)) for j in range(n)] for i in range(n)]


def _trace(a):
    return sum(a[i][i] for i in range(len(a)))


def characteristic_polynomial(matrix) -> UPoly:
    """``det(x·I − A)`` as an exact monic ``UPoly`` over ℚ, via Faddeev–LeVerrier.

    Back-checks (all exact): the ``x^{n-1}`` coefficient is ``−trace(A)`` and the constant term is
    ``(−1)^n · det(A)``.
    """
    a = _square_rational(matrix)
    n = len(a)
    ident = [[Q(1) if i == j else Q(0) for j in range(n)] for i in range(n)]
    m = ident                                   # M_1 = I
    coeffs_high = [Q(1)]                         # c_n = 1 (leading), then c_{n-1}, …, c_0
    for k in range(1, n + 1):
        am = _matmul(a, m)                       # A · M_k
        ck = -_trace(am) / k                     # c_{n-k}
        coeffs_high.append(ck)
        m = [[am[i][j] + (ck if i == j else Q(0)) for j in range(n)] for i in range(n)]  # M_{k+1}
    return UPoly(list(reversed(coeffs_high)), QRing())     # low-order-first coefficients


def real_eigenvalues(matrix, *, width=None) -> dict:
    """The REAL eigenvalues of a rational matrix, exact.

    Returns ``{"char_poly", "real_intervals", "real_count_with_multiplicity", "distinct_real",
    "complex_count", "all_real"}``. ``real_intervals`` is the sorted list of ``(lo, hi]`` rational
    intervals from Sturm isolation — one per DISTINCT real eigenvalue (refined below ``width`` if given).
    ``real_count_with_multiplicity`` counts real eigenvalues with algebraic multiplicity; the remaining
    ``complex_count`` eigenvalues are non-real (reported, not enumerated).
    """
    from .univariate import _root_bound, square_free_factorization

    p = characteristic_polynomial(matrix)
    n = p.degree()
    intervals = isolate_real_roots(p, width=width)
    distinct_real = len(intervals)

    # algebraic multiplicity of the real eigenvalues: a real root of p lives in exactly one square-free
    # factor g_i (multiplicity i), so summing (distinct real roots of g_i)·i counts real eigenvalues with
    # multiplicity — exactly, without needing to divide out an irrational root.
    _, sqfree = square_free_factorization(p)
    real_with_mult = 0
    for g, i in sqfree:
        b = _root_bound(g)
        real_with_mult += count_real_roots(g, -b, b) * i
    return {
        "char_poly": p,
        "real_intervals": intervals,
        "distinct_real": distinct_real,
        "real_count_with_multiplicity": real_with_mult,
        "complex_count": n - real_with_mult,
        "all_real": real_with_mult == n,
    }


__all__ = ["characteristic_polynomial", "real_eigenvalues"]
