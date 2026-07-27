#!/usr/bin/env python3
"""Same-operator executor audit: native vs SciPy vs JAX.

All three solvers receive one identical finite operator that the native solver
already constructed (same window, same interval count, same samples).  Only the
*execution* of the eigenvalue solve differs, so this isolates the solve kernel:

* native  — the retained requested-only Sturm/bisection kernel, O(k·N) work and
  O(N) memory, computing only the requested low modes;
* SciPy    — ``scipy.linalg.eigh_tridiagonal`` with ``select="i"`` (a tuned
  LAPACK tridiagonal solver, also requested-only);
* JAX      — ``jnp.linalg.eigvalsh`` on the densified operator (x64, JIT), the
  standard dense route, which computes the whole spectrum.

This is an executor comparison, not an independent JAX/SciPy pipeline: neither
library performs the well search, window admission, or mesh refinement — those
remain the native method's.  The dense JAX route is the only eigensolver JAX
exposes here; its O(N^2) memory and whole-spectrum cost are real properties of
that route, reported honestly rather than hidden.
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

    from scipy.linalg import eigh_tridiagonal

    native_full = retained_raw_input_readout(problem)
    window = native_full.window
    diagonal, off_diagonal, _spacing = retained_tridiagonal(
        problem, window, intervals
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

    # SciPy tridiagonal executor on the same operator
    scipy_seconds, scipy_values = _hot_median(
        lambda: eigh_tridiagonal(
            diagonal,
            off_diagonal,
            select="i",
            select_range=(0, problem.modes - 1),
            eigvals_only=True,
            check_finite=False,
        ),
        repeats=repeats,
    )
    scipy_values = np.asarray(scipy_values)

    record: dict[str, object] = {
        "intervals": intervals,
        "interior_points": diagonal.size,
        "window": [float(window[0]), float(window[1])],
        "requested_modes": problem.modes,
        "native_hot_median_seconds": native_seconds,
        "native_working_bytes": int(native_readout.working_bytes),
        "scipy_hot_median_seconds": scipy_seconds,
        "scipy_to_native_time_ratio": scipy_seconds / native_seconds,
        "scipy_vs_native_max_abs_difference": float(
            np.max(np.abs(scipy_values - native_values))
        ),
    }

    if jax_bundle is not None:
        _jax, jnp, dense_eigvalsh = jax_bundle
        dense = (
            np.diag(diagonal)
            + np.diag(off_diagonal, 1)
            + np.diag(off_diagonal, -1)
        )
        dense_jnp = jnp.asarray(dense)

        def _run_jax():
            return np.asarray(dense_eigvalsh(dense_jnp))[: problem.modes]

        jax_seconds, jax_values = _hot_median(_run_jax, repeats=repeats)
        jax_values = np.asarray(jax_values)
        record.update(
            {
                "jax_hot_median_seconds": jax_seconds,
                "jax_to_native_time_ratio": jax_seconds / native_seconds,
                "jax_dense_matrix_bytes": int(dense.nbytes),
                "jax_dense_to_native_memory_ratio": (
                    dense.nbytes / native_readout.working_bytes
                ),
                "jax_vs_native_max_abs_difference": float(
                    np.max(np.abs(jax_values - native_values))
                ),
            }
        )

    record["cross_check_ok"] = bool(
        record["scipy_vs_native_max_abs_difference"] <= cross_check_tol
        and record.get("jax_vs_native_max_abs_difference", 0.0)
        <= cross_check_tol
    )
    return record


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
