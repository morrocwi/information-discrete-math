#!/usr/bin/env python3
"""LAPACK MRRR (dstemr via ctypes) peer — agreement with the native kernel and with SciPy.

MRRR is an OPTIONAL benchmark comparator (it is never a credibility gate), so the whole module skips
cleanly on a host where the BLAS ``dstemr`` symbol cannot be resolved.

Run: PYTHONPATH=. python3 -m pytest tests/test_mrrr.py -q
"""

from __future__ import annotations

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("scipy")

from retained_spectral.competition.mrrr import mrrr_available, mrrr_eigenvalues
from retained_spectral.engine import native_eigvals_from_tridiagonal, warm_native_kernel

pytestmark = pytest.mark.skipif(not mrrr_available(), reason="LAPACK dstemr not resolvable on this host")


def _harmonic(n, L=40.0):
    x = np.linspace(-L, L, n + 2)[1:-1]
    h = x[1] - x[0]
    return 1.0 / (h * h) + 0.5 * x * x, np.full(n - 1, -0.5 / (h * h))


@pytest.mark.parametrize("n,k", [(500, 4), (2000, 8), (4000, 16)])
def test_mrrr_agrees_with_scipy_and_native(n, k):
    from scipy.linalg import eigh_tridiagonal

    warm_native_kernel()
    d, e = _harmonic(n)
    vm = mrrr_eigenvalues(d, e, k)
    assert vm.shape == (k,)
    vs = eigh_tridiagonal(d, e, select="i", select_range=(0, k - 1))[0]
    assert float(np.max(np.abs(vm - vs))) < 1e-9          # same operator, same LAPACK family
    vn = np.asarray(native_eigvals_from_tridiagonal(d, e, k, 1e-10))[:k]
    assert float(np.max(np.abs(vm - vn))) <= 1e-8         # native meets its declared tolerance vs MRRR


def test_mrrr_reports_nonzero_info_as_error():
    # a malformed request (k > n) must raise, never return a wrong-length or garbage array
    d, e = _harmonic(64)
    with pytest.raises(Exception):
        mrrr_eigenvalues(d, e, 999)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
