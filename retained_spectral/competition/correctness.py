#!/usr/bin/env python3
"""Three independent correctness layers for the Retained Spectral native readout (B4).

A speed benchmark is only as trustworthy as its correctness floor. For each declared 1-D spectrum we
check the native eigenvalues three independent ways, all on the SAME finite operator the native method
actually solved — no layer reuses another's result:

* **Layer 1 — external analytic reference.** The published/closed-form eigenvalues of the continuum
  problem (supplied by the benchmark target). This is the only layer that leaves the discrete operator.
* **Layer 2 — extended-precision recomputation.** The k smallest eigenvalues of the IDENTICAL
  tridiagonal operator, recomputed by Sturm bisection in mpmath at high precision. This catches any
  float64 arithmetic loss in the native path: the native float64 answer must match the extended-precision
  answer on the very same matrix.
* **Layer 3 — Sturm sign-count certificate.** An eigensolve-free counting argument: the number of
  eigenvalues strictly below a threshold equals the number of negative pivots in the LDLᵀ factorization
  (Sturm's theorem). For sorted eigenvalues v_0<…<v_{k-1}, the count just below v_i must be exactly i and
  just above must be ≥ i+1 — this certifies each eigenvalue's INDEX by a different principle than solving.

``three_layer_case`` runs all three and returns a per-case record + an overall ``ok``.
"""

from __future__ import annotations

import mpmath as mp
import numpy as np

from retained_spectral.engine import (
    RawSpectralProblem,
    _sturm_count_python,
    native_eigvals_from_tridiagonal,
    retained_raw_input_readout,
    retained_tridiagonal,
)


def sturm_index_certificate(diagonal, off_diagonal, values, *, rel_delta: float = 1.0e-7,
                            abs_delta: float = 0.0) -> dict:
    """Layer 3 — certify each eigenvalue's index by Sturm sign-counting on the identical operator.

    The band ``delta`` around each eigenvalue must be WIDER than the solve's own accuracy (so the true
    eigenvalue sits inside [v-delta, v+delta]) yet far NARROWER than the eigenvalue spacing (so it never
    swallows a neighbour). Pass ``abs_delta`` tied to the solver's declared tolerance for that.
    """
    vals = sorted(float(v) for v in values)
    checks = []
    ok = True
    for i, v in enumerate(vals):
        delta = max(rel_delta * max(1.0, abs(v)), abs_delta)
        below = _sturm_count_python(diagonal, off_diagonal, v - delta)
        above = _sturm_count_python(diagonal, off_diagonal, v + delta)
        this_ok = (below == i) and (above >= i + 1)
        ok = ok and this_ok
        checks.append({"index": i, "value": v, "count_below": below,
                       "count_above": above, "ok": bool(this_ok)})
    return {"ok": bool(ok), "checks": checks}


def _sturm_count_mp(diag, off, threshold) -> int:
    """Sturm negative-pivot count in the ambient mpmath precision (call inside mp.workdps)."""
    tiny = mp.mpf(10) ** -300
    pivot = diag[0] - threshold
    count = 1 if pivot < 0 else 0
    if abs(pivot) < tiny:
        pivot = -tiny
    for i in range(1, len(diag)):
        c = off[i - 1]
        pivot = diag[i] - threshold - c * c / pivot
        if pivot < 0:
            count += 1
        if abs(pivot) < tiny:
            pivot = -tiny
    return count


def high_precision_reference(diagonal, off_diagonal, k: int, *, dps: int = 40,
                             bisect_steps: int = 140) -> list[float]:
    """Layer 2 — the k smallest eigenvalues of the IDENTICAL tridiagonal, by Sturm bisection in mpmath
    extended precision. Independent of LAPACK and of the native float64 path (same principle, higher
    precision), so it exposes any precision loss the native solve incurred on this operator."""
    with mp.workdps(dps):
        diag = [mp.mpf(float(x)) for x in np.asarray(diagonal)]
        off = [mp.mpf(float(x)) for x in np.asarray(off_diagonal)]
        radius = max((abs(off[i - 1]) if i > 0 else mp.mpf(0)) +
                     (abs(off[i]) if i < len(off) else mp.mpf(0)) for i in range(len(diag)))
        lo = min(diag) - radius
        hi = max(diag) + radius
        eigs = []
        for idx in range(k):
            a, b = lo, hi
            for _ in range(bisect_steps):
                m = (a + b) / 2
                if _sturm_count_mp(diag, off, m) > idx:
                    b = m
                else:
                    a = m
            eigs.append(float((a + b) / 2))
        return eigs


def three_layer_case(problem: RawSpectralProblem, reference, *, intervals: int = 768,
                     match_tol: float | None = None) -> dict:
    """Verify one declared problem three independent ways.

    Layer 1 checks the native CONTINUUM estimate (the Richardson-extrapolated product output) against
    the external analytic reference. Layers 2 & 3 check the native DISCRETE kernel solve — the k
    eigenvalues of one fixed finite operator, the same object every competitor is timed on — against an
    extended-precision recomputation and a Sturm sign-count, both on that identical operator. The
    discrete solve differs from the continuum by O(h²) discretisation error, so the two are checked
    against the right targets and never conflated.
    """
    continuum = retained_raw_input_readout(problem)
    ref = np.asarray(reference, dtype=np.float64)
    cvals = np.asarray(continuum.values, dtype=np.float64)
    k = len(cvals)
    analytic_err = float(np.max(np.abs(cvals - ref))) if len(ref) == k else float("inf")

    # the SAME fixed operator the executor audit times every solver on
    diagonal, off_diagonal, _ = retained_tridiagonal(problem, continuum.window, intervals)
    discrete = np.asarray(native_eigvals_from_tridiagonal(
        diagonal, off_diagonal, k, problem.tolerance), dtype=np.float64)

    hp = np.asarray(high_precision_reference(diagonal, off_diagonal, k))
    hp_err = float(np.max(np.abs(discrete - hp))) if len(hp) == k else float("inf")

    # the native discrete solve bisects only to its DECLARED tolerance, so it should match the exact
    # (extended-precision) eigenvalues of the same operator to within that tolerance — not to 40 digits.
    tol = match_tol if match_tol is not None else max(problem.tolerance, 1.0e-12)
    # the Sturm band must exceed the solve's accuracy so the true eigenvalue lies inside it
    sturm = sturm_index_certificate(diagonal, off_diagonal, discrete, abs_delta=4.0 * tol)
    layers = {
        "analytic_reference_ok": analytic_err <= problem.tolerance,      # continuum estimate vs analytic
        "extended_precision_ok": hp_err <= tol,                          # discrete solve vs mpmath, same op
        "sturm_certificate_ok": sturm["ok"],                             # Sturm index count, same op
    }
    return {
        "returned_modes": k,
        "analytic_max_abs_error": analytic_err,
        "discrete_extended_precision_max_abs_error": hp_err,
        "extended_precision_dps": 40,
        "sturm_certificate": sturm,
        "layers": layers,
        "ok": bool(all(layers.values())),
    }


__all__ = ["sturm_index_certificate", "high_precision_reference", "three_layer_case"]
