#!/usr/bin/env python3
"""Same-operator executor audit: native vs every standard eigensolver.

All solvers receive one identical finite operator that the native solver already
constructed (same window, same interval count, same samples).  Only the
*execution* of the eigenvalue solve differs, so this isolates the solve kernel:

* native                    — retained requested-only Sturm/bisection, O(k·N)
  work and O(N) memory, computing only the requested low modes;
* SciPy ``eigh_tridiagonal`` — LAPACK tridiagonal, requested-only (``select="i"``);
* SciPy ``eigh`` (dense)     — LAPACK dense, whole spectrum;
* NumPy ``eigvalsh`` (dense) — LAPACK dense, whole spectrum;
* SciPy ``eigsh`` (ARPACK)   — iterative, k smallest-algebraic;
* JAX ``eigvalsh`` (dense)   — XLA dense, whole spectrum (optional).

This is an executor comparison, not an independent pipeline: none of the
libraries perform the well search, window admission, or mesh refinement — those
remain the native method's.  The dense/iterative routes' whole-spectrum cost and
O(N^2) memory are real properties reported honestly, not hidden.  Dense-route
wall-clock also depends on the linked BLAS/LAPACK backend.
"""

from __future__ import annotations

import statistics
import time
from typing import Callable

import numpy as np

from retained_spectral.engine import (
    RawSpectralProblem,
    _finite_native_readout,
    retained_raw_input_readout,
    retained_tridiagonal,
    warm_native_kernel,
)


def _hot_median(fn: Callable[[], object], *, repeats: int) -> tuple[float, object]:
    fn()  # warm dispatch outside timing
    samples: list[float] = []
    value = None
    for _ in range(repeats):
        started = time.perf_counter()
        value = fn()
        samples.append(time.perf_counter() - started)
    return float(statistics.median(samples)), value


def _jax_solver():
    """Return an x64 JIT dense eigvalsh executor, or ``None`` if JAX missing."""

    try:
        import os

        os.environ.setdefault("JAX_PLATFORMS", "cpu")
        import jax

        jax.config.update("jax_enable_x64", True)
        import jax.numpy as jnp

        @jax.jit
        def _dense_eigvalsh(dense):
            return jnp.linalg.eigvalsh(dense)

        return jax, jnp, _dense_eigvalsh
    except Exception:  # pragma: no cover - JAX is an optional competitor
        return None


def executor_audit_case(
    problem: RawSpectralProblem,
    *,
    intervals: int = 768,
    repeats: int = 5,
    jax_bundle: object | None = None,
    cross_check_tol: float = 1e-6,
) -> dict[str, object]:
    """Compare native, SciPy, and JAX on one identical operator.

    The window comes from a full native solve so the operator is a real,
    admitted finite window rather than an arbitrary box.  ``intervals`` is held
    fixed and modest so the dense JAX route stays memory-safe.
    """

    import scipy.linalg as sla
    import scipy.sparse as sp
    import scipy.sparse.linalg as spla

    k = problem.modes
    native_full = retained_raw_input_readout(problem)
    window = native_full.window
    diagonal, off_diagonal, _spacing = retained_tridiagonal(
        problem, window, intervals
    )
    dense = (
        np.diag(diagonal) + np.diag(off_diagonal, 1) + np.diag(off_diagonal, -1)
    )

    # native requested-only solve on this exact grid
    native_seconds, native_readout = _hot_median(
        lambda: _finite_native_readout(
            problem,
            window,
            intervals,
            energy_tolerance=problem.tolerance,
        ),
        repeats=repeats,
    )
    native_values = np.asarray(native_readout.values)

    # Every competitor below receives the IDENTICAL operator (dense/tridiagonal
    # forms of the same matrix); only the eigensolver differs.
    competitors: list[tuple[str, str, object]] = [
        (
            "SciPy eigh_tridiagonal",
            "LAPACK tridiagonal, requested-only",
            lambda: sla.eigh_tridiagonal(
                diagonal, off_diagonal, select="i",
                select_range=(0, k - 1), eigvals_only=True, check_finite=False,
            ),
        ),
        (
            "SciPy eigh (dense)",
            "LAPACK dense, whole spectrum",
            lambda: sla.eigh(dense, eigvals_only=True, check_finite=False)[:k],
        ),
        (
            "NumPy eigvalsh (dense)",
            "LAPACK dense, whole spectrum",
            lambda: np.linalg.eigvalsh(dense)[:k],
        ),
        (
            "SciPy eigsh (ARPACK)",
            "ARPACK iterative, k smallest-algebraic",
            lambda: np.sort(
                spla.eigsh(
                    sp.diags(
                        [off_diagonal, diagonal, off_diagonal], [-1, 0, 1]
                    ).tocsc(),
                    k=k, which="SA", return_eigenvectors=False,
                )
            ),
        ),
    ]
    if jax_bundle is not None:
        _jax, jnp, dense_eigvalsh = jax_bundle
        dense_jnp = jnp.asarray(dense)
        competitors.append((
            "JAX eigvalsh (dense)",
            "XLA dense, whole spectrum",
            lambda: np.asarray(dense_eigvalsh(dense_jnp))[:k],
        ))

    solvers: dict[str, object] = {}
    all_ok = True
    all_complete = True
    for name, kind, fn in competitors:
        try:
            seconds, values = _hot_median(fn, repeats=repeats)
            values = np.asarray(values)
            diff = float(np.max(np.abs(values - native_values)))
        except Exception as error:  # a competitor that cannot run makes the comparison INCOMPLETE
            solvers[name] = {"kind": kind, "error": f"{type(error).__name__}: {error}"}
            all_ok = False          # a missing solver means the cross-check is not established
            all_complete = False
            continue
        # a wrong length (partial eigenvalues) is a cross-check failure, not silently truncated
        length_ok = len(values) == len(native_values)
        ok = length_ok and diff <= cross_check_tol
        all_ok = all_ok and ok
        solvers[name] = {
            "kind": kind,
            "hot_median_seconds": seconds,
            "to_native_time_ratio": seconds / native_seconds,
            "max_abs_difference": diff,
            "returned_modes": int(values.size),
            "cross_check_ok": ok,
        }

    return {
        "intervals": intervals,
        "interior_points": diagonal.size,
        "window": [float(window[0]), float(window[1])],
        "requested_modes": k,
        "dense_matrix_bytes": int(dense.nbytes),
        "native_hot_median_seconds": native_seconds,
        "native_working_bytes": int(native_readout.working_bytes),
        "solvers": solvers,
        "cross_check_ok": bool(all_ok),
        "comparison_complete": bool(all_complete),   # False if any solver errored on this case
    }


def run_executor_audit(
    problems,
    *,
    intervals: int = 768,
    repeats: int = 5,
    include_jax: bool = True,
) -> dict[str, object]:
    """Run the executor audit across all problems on one fixed grid."""

    warm_native_kernel()
    jax_bundle = _jax_solver() if include_jax else None
    per_case: dict[str, object] = {}
    for problem in problems:
        per_case[problem.name] = executor_audit_case(
            problem,
            intervals=intervals,
            repeats=repeats,
            jax_bundle=jax_bundle,
        )
    return {
        "jax_available": jax_bundle is not None,
        "intervals": intervals,
        "repeats": repeats,
        "boundary": (
            "identical native-constructed operator handed to every solver; "
            "this audits the solve kernel only, not an independent pipeline"
        ),
        "cases": per_case,
    }


__all__ = ["executor_audit_case", "run_executor_audit"]
