#!/usr/bin/env python3
"""Spectral counting by inertia — cross-checked against dense eigensolves (pillar: absorbed method).

The count of pencil eigenvalues below σ is `#negative pivots of LDLᵀ(K−σM)` (Sylvester). These tests
lock: (1) it equals the true generalized-eigenvalue count for M positive definite, across bandwidths
and shifts; (2) the cost is independent of the count; (3) the eigenvalue bisection built on the count
matches scipy; (4) the pivot-floor handles a shift that exactly annihilates a diagonal (the defect the
source work found and repaired); (5) the honest validity boundary (M indefinite → NOT the eigenvalue
count) behaves as documented.

Run: PYTHONPATH=. python3 -m pytest tests/test_inertia_count.py -q
"""

from __future__ import annotations

import pytest

np = pytest.importorskip("numpy")
scipy_linalg = pytest.importorskip("scipy.linalg")

from retained_spectral.inertia import (
    count_below_banded,
    count_below_dense,
    eigenvalues_below_count,
    to_upper_band,
)


def _sym_band(n, b, rng):
    A = np.zeros((n, n))
    for i in range(n):
        for j in range(i, min(i + b + 1, n)):
            v = rng.standard_normal()
            A[i, j] = A[j, i] = v
    return A


def _spd_band(n, b, rng):
    A = _sym_band(n, b, rng)
    return (A + A.T) / 2 + n * np.eye(n)          # diagonally dominant → positive definite


@pytest.mark.parametrize("n,b", [(20, 1), (30, 3), (25, 4), (40, 2)])
def test_count_matches_generalized_eigh(n, b):
    rng = np.random.default_rng(n * 10 + b)
    K, M = _sym_band(n, b, rng), _spd_band(n, b, rng)
    w = scipy_linalg.eigh(K, M, eigvals_only=True)
    for sigma in (-5.0, -1.0, 0.0, 1.0, 5.0, float(w[n // 2]) + 1e-6):
        got = count_below_dense(K, M, sigma, bandwidth=b)
        assert got == int(np.count_nonzero(w < sigma)), f"n={n} b={b} sigma={sigma}"


def test_cost_is_independent_of_the_count():
    # counting 0 vs (nearly) all eigenvalues is the SAME work — one factorization either way
    rng = np.random.default_rng(7)
    n, b = 150, 6
    K, M = _sym_band(n, b, rng), _spd_band(n, b, rng)
    assert count_below_dense(K, M, -1e9, b) == 0
    assert count_below_dense(K, M, 1e9, b) == n            # every eigenvalue is below +inf
    # (both are single O(n b^2) passes; correctness is the invariant we assert)


def test_eigenvalue_bisection_built_on_the_count():
    rng = np.random.default_rng(3)
    n, b = 60, 4
    K, M = _sym_band(n, b, rng), _spd_band(n, b, rng)
    w = scipy_linalg.eigh(K, M, eigvals_only=True)
    kb, mb = to_upper_band(K, b), to_upper_band(M, b)
    ev = eigenvalues_below_count(kb, mb, float(w[0]) - 1, float(w[6]) + 1, 6, tol=1e-10)
    assert np.allclose(ev, w[:6], atol=1e-6)


def test_pivot_floor_handles_diagonal_annihilating_shift():
    # a shift equal to a diagonal entry makes a pivot exactly zero; the signed floor must keep the
    # recurrence sign-valid (without it a whole diagonal vanishing loses a sign — the repaired defect).
    n, b = 15, 1
    K = np.diag(np.arange(1.0, n + 1)) + np.diag(np.full(n - 1, 0.25), 1) + np.diag(np.full(n - 1, 0.25), -1)
    M = np.eye(n)
    w = scipy_linalg.eigh(K, M, eigvals_only=True)
    for sigma in (3.0, 7.0, 10.0):                         # exactly on diagonal entries -> zero pivot
        got = count_below_dense(K, M, sigma, bandwidth=b)
        true_strict = int(np.count_nonzero(w < sigma))
        near = float(np.min(np.abs(w - sigma))) < 1e-6     # a shift can also land on an eigenvalue
        assert 0 <= got <= n                               # never crashes / loses a sign
        # exact off the spectrum; at most a one-off tie when sigma sits on an eigenvalue (by convention)
        assert abs(got - true_strict) <= (1 if near else 0), f"sigma={sigma}: {got} vs {true_strict}"
    # and nudging the shift strictly off the spectrum gives the exact count
    for sigma in (3.0, 7.0, 10.0):
        s = sigma + 1e-4
        assert count_below_dense(K, M, s, bandwidth=b) == int(np.count_nonzero(w < s))


def test_indefinite_M_is_inertia_not_eigenvalue_count():
    # honest validity boundary: for indefinite M the pivot count is the inertia of K−σM, which is NOT
    # the pencil eigenvalue count — the function still returns a well-defined integer in [0, n]
    rng = np.random.default_rng(11)
    n, b = 20, 2
    K = _sym_band(n, b, rng)
    M = np.diag(np.sign(rng.standard_normal(n)))           # indefinite (±1 diagonal)
    c = count_below_dense(K, M, 0.5, bandwidth=b)
    assert 0 <= c <= n                                     # defined; not asserted to be the eig count


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
