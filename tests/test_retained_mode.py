#!/usr/bin/env python3
"""Retained Mode Readout (RMR) — eigenvector accuracy vs LAPACK.

The eigenvectors are read out of the RETAINED Sturm LDL^T pivots (no inverse iteration); each mode must
agree with SciPy's dense-tridiagonal eigenvector to near machine precision, satisfy its residual gate,
and be orthonormal across the returned set. Bounded sizes so it runs in the core-adjacent CI.

Run: PYTHONPATH=. python3 -m pytest tests/test_retained_mode.py -q
"""

from __future__ import annotations

import pytest

np = pytest.importorskip("numpy")             # bench-only dep (see requirements-bench.txt)
sla = pytest.importorskip("scipy.linalg")

from retained_spectral.engine import native_eigvals_from_tridiagonal, warm_native_kernel
from retained_spectral.retained_mode import modes, mode_readout, expectation, warm


def _harmonic(n, L=40.0):
    x = np.linspace(-L, L, n + 2)[1:-1]
    h = x[1] - x[0]
    return 1.0 / (h * h) + 0.5 * x * x, np.full(n - 1, -0.5 / (h * h)), x


def _double_well(n, L=8.0, a=1.0):
    x = np.linspace(-L, L, n + 2)[1:-1]
    h = x[1] - x[0]
    return 1.0 / (h * h) + (x * x - a) ** 2, np.full(n - 1, -0.5 / (h * h)), x


@pytest.fixture(scope="module", autouse=True)
def _warm():
    warm_native_kernel()
    warm()


@pytest.mark.parametrize("n,k", [(300, 6), (1000, 8)])
def test_rmr_modes_agree_with_lapack(n, k):
    d, e, _ = _harmonic(n)
    lam = np.asarray(native_eigvals_from_tridiagonal(d, e, k, 1e-12))[:k]
    V, res, status, verdict, orth, notes = modes(d, e, lam, rho=1e-10)
    assert verdict == "ACCEPT" and all(s == "ACCEPT" for s in status)

    w_lap, Vlap = sla.eigh_tridiagonal(d, e, select="i", select_range=(0, k - 1))
    Z = np.asarray(V).T                                   # columns are our modes
    # each mode aligns with LAPACK's (up to sign) to near machine precision
    overlap = np.abs(np.sum(Z * Vlap, axis=0))
    assert np.max(np.abs(1.0 - overlap)) < 1e-9
    # residual gate really holds, and the set is orthonormal
    assert np.max(res) <= 1e-8
    assert np.max(np.abs(Z.T @ Z - np.eye(k))) < 1e-7


def test_single_mode_readout_residual():
    d, e, _ = _harmonic(400)
    lam = float(np.asarray(native_eigvals_from_tridiagonal(d, e, 1, 1e-12))[0])
    z, residual, status = mode_readout(d, e, lam, rho=1e-10)
    assert status == "ACCEPT"
    # H z ≈ lam z  (finite tridiagonal apply)
    Hz = d * z
    Hz[:-1] += e * z[1:]
    Hz[1:] += e * z[:-1]
    assert np.max(np.abs(Hz - lam * z)) / np.max(np.abs(z)) <= 1e-8


def test_clustered_double_well_accepts():
    # a symmetric double well produces near-degenerate pairs — RMR must still ACCEPT and stay orthonormal
    d, e, _ = _double_well(800)
    lam = np.asarray(native_eigvals_from_tridiagonal(d, e, 6, 1e-12))[:6]
    V, res, status, verdict, orth, notes = modes(d, e, lam, rho=1e-10)
    assert verdict == "ACCEPT"
    Z = np.asarray(V).T
    assert np.max(np.abs(Z.T @ Z - np.eye(len(lam)))) < 1e-6


def test_expectation_streams_without_retaining_vectors():
    # a scalar readout per mode (here <x^2>) computed without materialising the eigenvectors
    d, e, x = _harmonic(500)
    lam = np.asarray(native_eigvals_from_tridiagonal(d, e, 4, 1e-12))[:4]
    vals = expectation(d, e, lam, weight=x * x, rho=1e-10)
    assert len(vals) == 4
    assert all(np.isfinite(v) for v in vals)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
