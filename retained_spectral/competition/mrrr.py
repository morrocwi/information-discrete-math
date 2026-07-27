"""LAPACK MRRR (dstemr) called directly through ctypes — a CREDIBLE tridiagonal peer.

SciPy's f2py wrapper for the MRRR driver declares the eigenvector output as a dense ``(n, n)`` array and
allocates it even with ``jobz='N'`` (eigenvalues only) — ~74.5 GiB at n=100,000 — so a timing taken
through the SciPy wrapper is NOT a valid MRRR timing (it measures a doomed allocation, not the solver).
This module calls ``dstemr_`` from the OpenBLAS shared library SciPy already ships, with ``jobz='N'`` and
``range='I'`` (the k smallest), allocating only the ``O(k)`` eigenvalue output — the honest way to time
MRRR against the native Retained Multilevel Sturm kernel.

It is OPTIONAL and defensive: if the shared library or the ``dstemr_`` symbol cannot be resolved the peer
is simply unavailable (``mrrr_available()`` is False), exactly like the JAX peer — it is never wired into a
credibility GATE, only offered as a benchmark comparator, so a platform without a locatable BLAS never
changes a verdict.
"""

from __future__ import annotations

import ctypes
import glob
import os

import numpy as np

_lib = None
_dstemr = None


def _load() -> None:
    global _lib, _dstemr
    if _dstemr is not None:
        return
    import scipy

    base = os.path.dirname(scipy.__file__)
    candidates = []
    for pat in ("scipy.libs/libscipy_openblas*.so*", "scipy.libs/libopenblas*.so*",
                "numpy.libs/libscipy_openblas*.so*", "numpy.libs/libopenblas*.so*"):
        candidates += glob.glob(os.path.join(base, "..", pat))
    # scipy's bundled OpenBLAS mangles the LAPACK symbol name (e.g. 'scipy_dstemr_') to avoid an ABI
    # clash; a plain OpenBLAS exposes 'dstemr_'. Try both, LP64 first.
    symbol_names = ("dstemr_", "scipy_dstemr_", "dstemr", "scipy_dstemr")
    for path in candidates:
        try:
            lib = ctypes.CDLL(path)
        except OSError:
            continue
        for name in symbol_names:
            sym = getattr(lib, name, None)
            if sym is not None:
                _lib, _dstemr = lib, sym
                return
    raise RuntimeError("MRRR peer unavailable: no BLAS library exposing a dstemr symbol was found")


def mrrr_available() -> bool:
    """True iff LAPACK dstemr can be called through ctypes on this host."""
    try:
        _load()
        return True
    except Exception:
        return False


def mrrr_eigenvalues(diagonal, off_diagonal, k: int) -> np.ndarray:
    """The ``k`` smallest eigenvalues of the symmetric tridiagonal (``diagonal``, ``off_diagonal``) via
    LAPACK MRRR (``dstemr``, ``jobz='N'``, ``range='I'``), timed honestly — only ``O(k)`` output is
    allocated. Returns a length-``k`` float64 array. Raises on an unavailable library or a nonzero info."""
    _load()
    d = np.ascontiguousarray(diagonal, dtype=np.float64).copy()
    n = d.size
    e = np.ascontiguousarray(np.append(np.asarray(off_diagonal, dtype=np.float64), 0.0)).copy()
    dp = ctypes.POINTER(ctypes.c_double)
    ip = ctypes.POINTER(ctypes.c_int)
    i32 = ctypes.c_int

    W = np.zeros(n, dtype=np.float64)
    Z = np.zeros(1, dtype=np.float64)                       # jobz='N' → not referenced, size 1
    isuppz = np.zeros(2 * max(1, k), dtype=np.int32)
    lwork, liwork = 12 * n + 100, 8 * n + 100
    work = np.zeros(lwork, dtype=np.float64)
    iwork = np.zeros(liwork, dtype=np.int32)
    m = i32(0)
    info = i32(0)
    tryrac = i32(1)

    _dstemr(
        ctypes.c_char_p(b"N"), ctypes.c_char_p(b"I"),
        ctypes.byref(i32(n)), d.ctypes.data_as(dp), e.ctypes.data_as(dp),
        ctypes.byref(ctypes.c_double(0.0)), ctypes.byref(ctypes.c_double(0.0)),
        ctypes.byref(i32(1)), ctypes.byref(i32(k)),
        ctypes.byref(m), W.ctypes.data_as(dp), Z.ctypes.data_as(dp),
        ctypes.byref(i32(1)), ctypes.byref(i32(k)), isuppz.ctypes.data_as(ip),
        ctypes.byref(tryrac), work.ctypes.data_as(dp), ctypes.byref(i32(lwork)),
        iwork.ctypes.data_as(ip), ctypes.byref(i32(liwork)), ctypes.byref(info),
        i32(1), i32(1),
    )
    if info.value != 0:
        raise RuntimeError(f"dstemr returned info={info.value}")
    return W[:k]


__all__ = ["mrrr_available", "mrrr_eigenvalues"]
