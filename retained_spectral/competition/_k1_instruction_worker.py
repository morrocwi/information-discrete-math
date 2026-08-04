#!/usr/bin/env python3
"""Worker process for the k=1 discrete instruction-count readout.

Not a library module -- invoked as a subprocess (once per (solver, N) pair)
under ``perf stat -e instructions:u`` by :mod:`.k1_discrete_readout`. Runs one
solver N times on one prebuilt operator; the *retired CPU instruction count*
of the whole process (reported by perf, on stderr, outside this script) is the
readout, not anything this script prints. Kept as its own tiny process (not a
function called in-process) so perf can attribute instructions to exactly this
solve loop, isolated from the measurement harness's own instructions.

Usage::

    python3 _k1_instruction_worker.py <problem_name> <solver> <intervals> <N>

``solver`` is ``native`` or ``scipy``.
"""

from __future__ import annotations

import sys

import warnings

warnings.filterwarnings("ignore")


def main() -> None:
    problem_name, solver, intervals_s, n_s = sys.argv[1:5]
    intervals = int(intervals_s)
    n_repeats = int(n_s)

    from retained_spectral.engine import (
        raw_benchmark_targets,
        retained_raw_input_readout,
        retained_tridiagonal,
        warm_native_kernel,
        native_eigvals_from_tridiagonal,
    )

    warm_native_kernel()
    targets = {t.problem.name: t.problem for t in raw_benchmark_targets()}
    problem = targets[problem_name]
    native_full = retained_raw_input_readout(problem)
    window = native_full.window
    diagonal, off_diagonal, _spacing = retained_tridiagonal(problem, window, intervals)

    if solver == "native":
        for _ in range(n_repeats):
            native_eigvals_from_tridiagonal(diagonal, off_diagonal, problem.modes, problem.tolerance)
    elif solver == "scipy":
        import scipy.linalg as sla

        k = problem.modes
        for _ in range(n_repeats):
            sla.eigh_tridiagonal(
                diagonal, off_diagonal, select="i",
                select_range=(0, k - 1), eigvals_only=True, check_finite=False,
            )
    else:
        raise ValueError(f"unknown solver {solver!r}, expected 'native' or 'scipy'")


if __name__ == "__main__":
    main()
