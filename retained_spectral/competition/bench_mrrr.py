#!/usr/bin/env python3
"""Native Retained Multilevel Sturm vs LAPACK MRRR (dstemr), eigenvalues only, on one tridiagonal.

The honest MRRR timing: ``dstemr`` is called through ctypes with ``jobz='N'`` / ``range='I'`` (see
:mod:`retained_spectral.competition.mrrr`), so only the ``O(k)`` eigenvalue output is allocated —
unlike SciPy's f2py MRRR wrapper, which declares a dense ``(n,n)`` eigenvector array and allocates
~74.5 GiB at n=100,000 even with ``jobz='N'``, making SciPy-wrapped MRRR timings invalid.

Run:  PYTHONPATH=. python3 -m retained_spectral.competition.bench_mrrr
"""

from __future__ import annotations

import argparse
import statistics
import time

import numpy as np

from retained_spectral.competition.mrrr import mrrr_available, mrrr_eigenvalues
from retained_spectral.engine import (
    native_eigvals_from_tridiagonal,
    require_compiled_kernel,
    warm_native_kernel,
)

TOL = 1e-8


def _harmonic(n: int, L: float = 40.0):
    x = np.linspace(-L, L, n + 2)[1:-1]
    h = x[1] - x[0]
    return 1.0 / (h * h) + 0.5 * x * x, np.full(n - 1, -0.5 / (h * h))


def _median(fn, repeats: int = 3):
    samples = []
    value = None
    for _ in range(repeats):
        started = time.perf_counter()
        value = fn()
        samples.append(time.perf_counter() - started)
    return statistics.median(samples), value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--sizes", type=str, default="20000:4,20000:64,100000:4,100000:64")
    args = parser.parse_args()

    require_compiled_kernel("retained_spectral.competition.bench_mrrr")   # fail closed: it's a speed measurement
    if not mrrr_available():
        print("MRRR peer unavailable on this host (no resolvable LAPACK dstemr) — nothing to compare.")
        return 0
    warm_native_kernel()

    print(f"{'n':>8} {'k':>5} {'native ms':>10} {'MRRR ms':>10} {'speedup':>8} {'max|Δλ|':>10}")
    for spec in args.sizes.split(","):
        n, k = (int(v) for v in spec.split(":"))
        d, e = _harmonic(n)
        tn, vn = _median(lambda: native_eigvals_from_tridiagonal(d, e, k, TOL), args.repeats)
        try:
            tm, vm = _median(lambda: mrrr_eigenvalues(d, e, k), args.repeats)
        except Exception as exc:  # a host where dstemr rejects the request — disclose, never fake a number
            print(f"{n:>8} {k:>5} {tn * 1e3:>10.1f}   MRRR FAILED  {type(exc).__name__}: {str(exc)[:40]}")
            continue
        diff = float(np.max(np.abs(np.asarray(vn[:k]) - np.asarray(vm[:k]))))
        print(f"{n:>8} {k:>5} {tn * 1e3:>10.1f} {tm * 1e3:>10.1f} {tm / tn:>8.2f} {diff:>10.1e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
