#!/usr/bin/env python3
"""Spectral counting by inertia — how many modes below a shift, at a cost independent of the answer.

A demonstration of the readout rule (do not construct what the readout does not require): to learn how
many eigenvalues of a symmetric pencil `(K, M)` lie below a threshold σ, you do NOT compute the modes —
you read the inertia of `K − σM` off one banded LDLᵀ factorization (Sylvester's law). The work is the
same whether the answer is 0 or n. Classic use: a buckling-safety check ("are there any modes below the
load factor?") answered without solving a single eigenvector.

Tier: finite_diagnostic — a finite sign-count on a finite operator, cross-checked here against a dense
eigensolve. Absorbed method; competitive only for narrow bands (see retained_spectral/inertia.py).

Run:  PYTHONPATH=. python3 -m demos.spectral_count
"""

from __future__ import annotations

import numpy as np

from retained_spectral.inertia import count_below_dense


def _fe_beam(n: int, load: float = 1.0):
    """A tiny 1-D FE-like symmetric pencil: stiffness K (tridiagonal Laplacian) and mass M (lumped),
    with a compressive `load` that lowers the spectrum (a toy buckling operator)."""
    K = (2.0 * np.eye(n) - np.eye(n, k=1) - np.eye(n, k=-1)) - load * (
        0.5 * np.eye(n, k=1) + 0.5 * np.eye(n, k=-1))
    M = np.eye(n)
    return K, M


def main() -> int:
    from scipy.linalg import eigh

    print("Spectral counting by inertia (one factorization per threshold, cost independent of count)")
    print(f"{'load':>6} {'σ':>8} {'#modes < σ (inertia)':>22} {'dense check':>12}")
    n = 400
    for load in (0.0, 0.5, 1.0, 1.5):
        K, M = _fe_beam(n, load)
        reference = eigh(K, M, eigvals_only=True)
        for sigma in (0.0, 1.0, 3.0):
            count = count_below_dense(K, M, sigma, bandwidth=1)
            check = int(np.count_nonzero(reference < sigma))
            flag = "ok" if count == check else "DIFF"
            print(f"{load:>6.1f} {sigma:>8.2f} {count:>22} {check:>10} {flag}")
    print("\nBuckling-safety idiom: a single inertia count answers 'any modes below the load?' with no")
    print("eigenvector computed — the retained object is the count, never the modes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
