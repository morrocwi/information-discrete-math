#!/usr/bin/env python3
"""Correctness-gated Retained Spectral versus SLEPc benchmark.

Both solvers receive the same already-built real symmetric tridiagonal
Hamiltonian, request the same lowest k modes, use the same tolerance, and run
serially with one numerical thread. Operator construction is outside timing.

Two contracts are reported separately:
  * eigenvalues requested;
  * eigenpairs requested.

The headline verdict uses the SAME-OUTPUT eigenpair comparison. It says native
is faster only when every case passes the accuracy gates and the lower endpoint
of a deterministic 95% bootstrap interval is above 1. The claim is deliberately
limited to these serial tridiagonal cases; it says nothing universal about MPI,
GPU, non-Hermitian, generalized, polynomial, nonlinear, or arbitrary sparse
SLEPc workloads.
"""
from __future__ import annotations

import json
import os
import platform
import statistics
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

for _name in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ.setdefault(_name, "1")

import numpy as np
from scipy.linalg import eigh_tridiagonal

try:
    import slepc4py
    slepc4py.init(sys.argv)
    from petsc4py import PETSc
    from slepc4py import SLEPc
except ImportError as exc:  # the independent peer is required to run this head-to-head
    sys.stderr.write(
        f"SKIPPED: this benchmark requires the SLEPc/PETSc peer, which is not installed ({exc}).\n"
        "Install it (e.g. `apt install python3-slepc4py-real python3-petsc4py-real`, or via conda/pip)\n"
        "and re-run, or trigger the `slepc-head-to-head` workflow from the Actions tab.\n")
    raise SystemExit(2)

from retained_spectral.engine import (
    native_eigvals_from_tridiagonal,
    require_compiled_kernel,
    warm_native_kernel,
)
from retained_spectral.retained_mode import modes as retained_modes
from retained_spectral.retained_mode import warm as warm_retained_modes


@dataclass(frozen=True)
class Case:
    n: int
    k: int
    half_width: float = 40.0
    tolerance: float = 1.0e-9


CASES = (
    Case(20_000, 4),
    Case(50_000, 8),
    Case(100_000, 16),
)
REPEATS = int(os.environ.get("IDM_SLEPC_REPEATS", "5"))
BOOTSTRAPS = int(os.environ.get("IDM_SLEPC_BOOTSTRAPS", "5000"))
SEED = 20260728


def harmonic_tridiagonal(case: Case) -> tuple[np.ndarray, np.ndarray]:
    x = np.linspace(-case.half_width, case.half_width, case.n + 2, dtype=np.float64)[1:-1]
    h = float(x[1] - x[0])
    return (
        1.0 / h**2 + 0.5 * x**2,
        np.full(case.n - 1, -0.5 / h**2, dtype=np.float64),
    )


def petsc_from_tridiagonal(d: np.ndarray, e: np.ndarray) -> PETSc.Mat:
    n = int(d.size)
    ia = np.empty(n + 1, dtype=PETSc.IntType)
    ja = np.empty(3 * n - 2, dtype=PETSc.IntType)
    av = np.empty(3 * n - 2, dtype=PETSc.ScalarType)
    p = 0
    ia[0] = 0
    for i in range(n):
        if i:
            ja[p], av[p] = i - 1, e[i - 1]
            p += 1
        ja[p], av[p] = i, d[i]
        p += 1
        if i + 1 < n:
            ja[p], av[p] = i + 1, e[i]
            p += 1
        ia[i + 1] = p
    A = PETSc.Mat().createAIJ(size=(n, n), csr=(ia, ja, av), comm=PETSc.COMM_SELF)
    A.assemble()
    return A


def bootstrap_ratio(peer: list[float], native: list[float]) -> dict[str, float | str]:
    rng = np.random.default_rng(SEED)
    a = np.asarray(peer, dtype=float)
    b = np.asarray(native, dtype=float)
    ratios = np.empty(BOOTSTRAPS, dtype=float)
    for i in range(BOOTSTRAPS):
        aa = a[rng.integers(0, a.size, a.size)]
        bb = b[rng.integers(0, b.size, b.size)]
        ratios[i] = np.median(aa) / np.median(bb)
    lo, hi = np.quantile(ratios, (0.025, 0.975))
    median = statistics.median(peer) / statistics.median(native)
    verdict = "native_faster" if lo > 1.0 else (
        "peer_faster" if hi < 1.0 else "tie_or_unresolved"
    )
    return {
        "median_speedup_peer_over_native": float(median),
        "ci95_low": float(lo),
        "ci95_high": float(hi),
        "verdict": verdict,
    }


def warm_all_native_paths() -> None:
    """Compile values, twisted generation, retained solve, and cluster gates."""
    warm_native_kernel()
    warm_retained_modes()
    case = Case(256, 4, half_width=8.0, tolerance=1.0e-9)
    d, e = harmonic_tridiagonal(case)
    lams = native_eigvals_from_tridiagonal(d, e, case.k, case.tolerance)
    result = retained_modes(d, e, lams, rho=1.0e-9, orth_tol=1.0e-7)
    if result[3] != "ACCEPT":
        raise RuntimeError(f"native warm-up HOLD: {result[2:]}" )


def time_native_values(
    d: np.ndarray, e: np.ndarray, k: int, tol: float
) -> tuple[list[float], np.ndarray]:
    samples: list[float] = []
    values = np.empty(0)
    for _ in range(REPEATS):
        started = time.perf_counter()
        values = native_eigvals_from_tridiagonal(d, e, k, tol)
        samples.append(time.perf_counter() - started)
    return samples, np.asarray(values)


def time_native_pairs(
    d: np.ndarray, e: np.ndarray, k: int, tol: float
) -> tuple[list[float], np.ndarray, float, float]:
    samples: list[float] = []
    final_lams = np.empty(0)
    max_residual = 0.0
    final_orth = float("inf")
    for _ in range(REPEATS):
        started = time.perf_counter()
        lams = native_eigvals_from_tridiagonal(d, e, k, tol)
        vecs, residuals, statuses, verdict, orth, _notes = retained_modes(
            d, e, lams, rho=1.0e-9, orth_tol=1.0e-7
        )
        samples.append(time.perf_counter() - started)
        if verdict != "ACCEPT" or not all(s == "ACCEPT" for s in statuses):
            raise RuntimeError(f"native eigenpair HOLD: {statuses}, orth={orth}")
        Z = np.asarray(vecs).T
        if Z.shape != (d.size, k):
            raise RuntimeError(f"bad native eigenvector shape: {Z.shape}")
        final_lams = np.asarray(lams)
        max_residual = max(max_residual, float(np.max(residuals)))
        final_orth = float(orth)
    return samples, final_lams, max_residual, final_orth


def slepc_once(
    A: PETSc.Mat, k: int, tol: float
) -> tuple[float, np.ndarray, float, int]:
    eps = SLEPc.EPS().create(comm=PETSc.COMM_SELF)
    eps.setOperators(A)
    eps.setProblemType(SLEPc.EPS.ProblemType.HEP)
    eps.setType(SLEPc.EPS.Type.KRYLOVSCHUR)
    eps.setDimensions(k, min(A.getSize()[0], max(2 * k + 20, 40)))
    eps.setTolerances(tol, 20_000)

    # With spectral transforms SLEPc may otherwise converge using a cheap
    # transformed-problem estimate. Require the explicit residual of the
    # original eigenproblem for both stopping and the reported accuracy gate.
    eps.setTrueResidual(True)
    eps.setTarget(0.0)
    eps.setWhichEigenpairs(SLEPc.EPS.Which.TARGET_MAGNITUDE)
    st = eps.getST()
    st.setType(SLEPc.ST.Type.SINVERT)
    st.setShift(0.0)
    ksp = st.getKSP()
    ksp.setType(PETSc.KSP.Type.PREONLY)
    ksp.getPC().setType(PETSc.PC.Type.LU)

    started = time.perf_counter()
    eps.solve()
    elapsed = time.perf_counter() - started
    nconv = int(eps.getConverged())
    iterations = int(eps.getIterationNumber())
    if nconv < k:
        eps.destroy()
        raise RuntimeError(f"SLEPc converged {nconv}/{k} after {iterations} iterations")

    vals = np.asarray(sorted(float(np.real(eps.getEigenvalue(i))) for i in range(k)))
    errors = [
        float(eps.computeError(i, SLEPc.EPS.ErrorType.RELATIVE))
        for i in range(k)
    ]
    eps.destroy()
    return elapsed, vals, max(errors, default=0.0), iterations


def time_slepc(
    A: PETSc.Mat, k: int, tol: float
) -> tuple[list[float], np.ndarray, float, list[int]]:
    samples: list[float] = []
    final = np.empty(0)
    max_residual = 0.0
    iterations: list[int] = []
    for _ in range(REPEATS):
        elapsed, values, residual, its = slepc_once(A, k, tol)
        samples.append(elapsed)
        final = values
        max_residual = max(max_residual, residual)
        iterations.append(its)
    return samples, final, max_residual, iterations


def accuracy(
    values: np.ndarray, reference: np.ndarray, residual: float, tol: float
) -> dict[str, float | bool]:
    max_abs = float(np.max(np.abs(values - reference)))
    ok = bool(max_abs <= max(50.0 * tol, 1.0e-8) and residual <= 1.0e-7)
    return {
        "max_abs_eigenvalue_difference": max_abs,
        "max_reported_relative_residual": float(residual),
        "ok": ok,
    }


def main() -> int:
    require_compiled_kernel("Retained Spectral vs SLEPc benchmark")
    warm_all_native_paths()

    record: dict[str, object] = {
        "scope": "serial single-thread real symmetric tridiagonal lowest requested modes",
        "claim_boundary": (
            "Only the declared cases are tested; no universal claim over all "
            "SLEPc problem classes, MPI/GPU scales, or arbitrary sparsity."
        ),
        "repeats": REPEATS,
        "bootstrap_resamples": BOOTSTRAPS,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "numpy_version": np.__version__,
            "petsc_version": PETSc.Sys.getVersion(),
            "slepc_version": SLEPc.Sys.getVersion(),
            "slepc_true_residual": True,
        },
        "cases": [],
    }

    all_correct = True
    all_value_wins = True
    all_pair_wins = True

    for case in CASES:
        print(f"\n=== n={case.n:,} k={case.k} ===", flush=True)
        d, e = harmonic_tridiagonal(case)
        A = petsc_from_tridiagonal(d, e)
        reference = eigh_tridiagonal(
            d,
            e,
            eigvals_only=True,
            select="i",
            select_range=(0, case.k - 1),
            tol=case.tolerance / 10.0,
        )

        nv_times, nv = time_native_values(d, e, case.k, case.tolerance)
        np_times, np_values, np_residual, np_orth = time_native_pairs(
            d, e, case.k, case.tolerance
        )
        sp_times, sp_values, sp_residual, sp_iterations = time_slepc(
            A, case.k, case.tolerance
        )

        nv_accuracy = accuracy(nv, reference, 0.0, case.tolerance)
        np_accuracy = accuracy(np_values, reference, np_residual, case.tolerance)
        sp_accuracy = accuracy(sp_values, reference, sp_residual, case.tolerance)
        correct = bool(nv_accuracy["ok"] and np_accuracy["ok"] and sp_accuracy["ok"])
        value_ratio = bootstrap_ratio(sp_times, nv_times)
        pair_ratio = bootstrap_ratio(sp_times, np_times)

        all_correct = all_correct and correct
        all_value_wins = all_value_wins and value_ratio["verdict"] == "native_faster"
        all_pair_wins = all_pair_wins and pair_ratio["verdict"] == "native_faster"

        item = {
            "case": asdict(case),
            "reference_first": float(reference[0]),
            "reference_last": float(reference[-1]),
            "native_eigenvalues": {
                "samples_seconds": nv_times,
                "median_seconds": statistics.median(nv_times),
                "accuracy": nv_accuracy,
            },
            "native_eigenpairs": {
                "samples_seconds": np_times,
                "median_seconds": statistics.median(np_times),
                "accuracy": np_accuracy,
                "orthogonality_error": np_orth,
            },
            "slepc_krylovschur_shiftinvert_eigenpairs": {
                "samples_seconds": sp_times,
                "median_seconds": statistics.median(sp_times),
                "accuracy": sp_accuracy,
                "iterations": sp_iterations,
                "true_residual": True,
            },
            "slepc_speedup_over_native_eigenvalues": value_ratio,
            "slepc_speedup_over_native_eigenpairs": pair_ratio,
        }
        record["cases"].append(item)
        A.destroy()

        print(
            f"native values={statistics.median(nv_times):.6f}s | "
            f"native pairs={statistics.median(np_times):.6f}s | "
            f"SLEPc pairs={statistics.median(sp_times):.6f}s | "
            f"pair speedup={pair_ratio['median_speedup_peer_over_native']:.2f}x "
            f"CI=[{pair_ratio['ci95_low']:.2f},{pair_ratio['ci95_high']:.2f}] | "
            f"accuracy={correct}",
            flush=True,
        )

    record["gates"] = {
        "all_correct": all_correct,
        "native_faster_for_eigenvalues_all_declared_cases": all_value_wins,
        "native_faster_for_same_output_eigenpairs_all_declared_cases": all_pair_wins,
    }
    accepted = all_correct and all_value_wins and all_pair_wins
    record["verdict"] = (
        "ACCEPT_NATIVE_FASTER_IN_DECLARED_FIELD"
        if accepted
        else "HOLD_NO_SPEED_PROOF"
    )

    out = Path(os.environ.get("IDM_SLEPC_RESULT", "slepc_vs_retained.json"))
    out.write_text(json.dumps(record, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(f"\nVERDICT: {record['verdict']}")
    print(f"record: {out}")
    return 0 if all_correct else 2


if __name__ == "__main__":
    raise SystemExit(main())
