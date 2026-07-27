#!/usr/bin/env python3
"""Exact eigenvalues of rational matrices (P2): characteristic polynomial (Faddeev-LeVerrier) +
Sturm real-root isolation.

Run: PYTHONPATH=. python3 -m pytest tests/test_kernel_eigen.py -q
"""

from __future__ import annotations

from fractions import Fraction as Q

import pytest

from idm.kernel import poly as P


def test_characteristic_polynomial_matches_known_and_backchecks():
    A = [[1, 0, 0], [0, 2, 0], [0, 0, 3]]                  # diag(1,2,3)
    p = P.characteristic_polynomial(A)
    assert p.coeffs == [Q(-6), Q(11), Q(-6), Q(1)]         # (x-1)(x-2)(x-3) = x^3-6x^2+11x-6
    # back-checks: x^{n-1} coefficient is -trace(A); constant term is (-1)^n det(A)
    B = [[2, 1], [1, 2]]                                    # trace 4, det 3
    q = P.characteristic_polynomial(B)
    assert q.coeffs[-2] == -(2 + 2)                         # -trace
    assert q.coeffs[0] == ((-1) ** 2) * (2 * 2 - 1 * 1)     # (-1)^n det


def test_real_eigenvalues_isolates_each_and_reports_complex():
    A = [[1, 0, 0], [0, 2, 0], [0, 0, 3]]
    r = P.real_eigenvalues(A)
    assert r["all_real"] and r["distinct_real"] == 3 and r["real_count_with_multiplicity"] == 3
    for lo, hi in r["real_intervals"]:                     # each interval holds exactly one eigenvalue
        assert P.count_real_roots(r["char_poly"], lo, hi) == 1
    for lam in (1, 2, 3):
        assert sum(lo < lam <= hi for lo, hi in r["real_intervals"]) == 1

    rot = P.real_eigenvalues([[0, -1], [1, 0]])            # rotation: eigenvalues ±i, no real ones
    assert rot["distinct_real"] == 0 and rot["complex_count"] == 2 and not rot["all_real"]


def test_repeated_eigenvalue_multiplicity():
    r = P.real_eigenvalues([[2, 0], [0, 2]])               # (x-2)^2
    assert r["distinct_real"] == 1                          # one DISTINCT real eigenvalue
    assert r["real_count_with_multiplicity"] == 2          # algebraic multiplicity 2
    assert r["all_real"]


def test_irrational_eigenvalues_isolated_exactly_to_width():
    # [[0,2],[1,0]] has characteristic polynomial x^2 - 2 -> eigenvalues ±sqrt(2), irrational
    r = P.real_eigenvalues([[0, 2], [1, 0]], width=Q(1, 10 ** 6))
    assert r["char_poly"].coeffs == [Q(-2), Q(0), Q(1)]
    assert r["distinct_real"] == 2 and r["all_real"]
    for lo, hi in r["real_intervals"]:
        assert isinstance(lo, Q) and isinstance(hi, Q)     # exact rational brackets, no float
        assert hi - lo <= Q(1, 10 ** 6)
    pos = next((lo, hi) for lo, hi in r["real_intervals"] if lo > 0)
    assert pos[0] * pos[0] < 2 < pos[1] * pos[1]           # brackets +sqrt(2)


def test_non_square_matrix_rejected():
    with pytest.raises(ValueError):
        P.characteristic_polynomial([[1, 2, 3], [4, 5, 6]])


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
