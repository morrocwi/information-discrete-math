#!/usr/bin/env python3
"""Head-to-head benchmark: Retained Spectral versus SLEPc.

This benchmark is deliberately narrow and falsifiable.  It asks for the lowest
requested modes of the SAME prebuilt real symmetric tridiagonal Hamiltonian.
Operator construction and imports are outside the timed region.  The native
Numba kernel and SLEPc both run single-threaded in one process.

Two output contracts are measured separately:
  1. requested eigenvalues only;
  2. requested eigenpairs (native RMS + RMR versus SLEPc EPS).

SLEPc is tested with tuned Krylov-Schur + shift-invert, and a plain
Krylov-Schur control on the smallest case.  Every speed verdict is gated by
value agreement and residual checks.  A bootstrap 95% interval whose lower
endpoint exceeds 1 is required before the record says native_faster.
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

# Must be set before NumPy/PETSc load.
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

import slepc4py
slepc4py.init(sys.argv)
from petsc4py import PETSc
from slepc4py import SLEPc

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
    diagonal = 1.0 / h**2 + 0.5 * x**2
    off = np.full(case.n - 1, -0.5 / h**2, dtype=np.float64)
    return diagonal, off


def petsc_from_tridiagonal(d: np.ndarray, e: np.ndarray) -> PETSc.Mat:
    """Create a serial AIJ matrix from the exact same d/e arrays."""
    n = int(d.size)
    nnz = 3 * n - 2
    ia = np.empty(n + 1, dtype=PETSc.IntType)
    ja = np.empty(nnz, dtype=PETSc.IntType)
    av = np.empty(nnz, dtype=PETSc.ScalarType)
    p = 0
    ia[0] = 0
    for i in range(n):
        if i:
            ja[p] = i - 1
            av[p] = e[i - 1]
            p += 1
        ja[p] = i
        av[p] = d[i]
        p += 1
        if i + 1 < n:
            ja[p] = i + 1
            av[p] = e[i]
            p += 1
        ia[i + 1] = p
    assert p == nnz
    A = PETSc.Mat().createAIJ(size=(n, n), csr=(ia, ja, av), comm=PETSc.COMM_SELF)
    A.assemble()
    return A


def bootstrap_ratio(peer: list[float], native: list[float]) -> dict[str, float | str]:
    """Bootstrap the median speedup peer/native."""
    rng = np.random.default_rng(SEED)
    a = np.asarray(peer, dtype=float)
    b = np.asarray(native, dtype=float)
    ratios = np.empty(BOOTSTRAPS, dtype=float)
    for i in range(BOOTSTRAPS):
        aa = a[rng.integers(0, a.size, a.size)]
        bb = b[rng.integers(0, b.size, b.size)]
        ratios[i] = np.median(aa) / np.median(bb)
    lo, hi = np.quantile(ratios, (0.025, 0.975))
    med = statistics.median(peer) / statistics.median(native)
    verdict = "native_faster" if lo > 1.0 else ("peer_faster" if hi < 1.0 else "tie_or_unresolved")
    return {
        "median_speedup_peer_over_native": float(med),
        "ci95_low": float(lo),
        "ci95_high": float(hi),
        "verdict": verdict,
    }


def time_native_values(d: np.ndarray, e: np.ndarray, k: int, tol: float) -> tuple[list[float], np.ndarray]:
    samples: list[float] = []
    value = None
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        value = native_eigvals_from_tridiagonal(d, e, k, tol)
        samples.append(time.perf_counter() - t0)
    assert value is not None
    return samples, np.asarray(value)


def time_native_pairs(d: np.ndarray, e: np.ndarray, k: int, tol: float) -> tuple[list[float], np.ndarray, float, float]:
    samples: list[float] = []
    final_lams = None
    final_residual = float("inf")
    final_orth = float("inf")
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        lams = native_eigvals_from_tridiagonal(d, e, k, tol)
        vecs, residuals, statuses, verdict, orth, _notes = retained_modes(
            d, e, lams, rho=1.0e-9, orth_tol=1.0e-7
        )
        elapsed = time.perf_counter() - t0
        if verdict != "ACCEPT" or not all(s == "ACCEPT" for s in statuses):
            raise RuntimeError(f"native eigenpair readout HOLD: {statuses}, orth={orth}")
        samples.append(elapsed)
        final_lams = np.asarray(lams)
        final_residual = float(np.max(residuals))
        final_orth = float(orth)
        # Ensure vectors really materialised and have the declared dimensions.
        Z = np.asarray(vecs).T
        if Z.shape != (d.size, k):
            raise RuntimeError(f"bad native eigenvector shape: {Z.shape}")
    assert final_lams is not None
    return samples, final_lams, final_residual, final_orth


def slepc_once(A: PETSc.Mat, k: int, tol: float, *, shift_invert: bool) -> tuple[float, np.ndarray, float, int]:
    eps = SLEPc.EPS().create(comm=PETSc.COMM_SELF)
    eps.setOperators(A)
    eps.setProblemType(SLEPc.EPS.ProblemType.HEP)
    eps.setType(SLEPc.EPS.Type.KRYLOVSCHUR)
    ncv = min(A.getSize()[0], max(2 * k + 20, 40))
    eps.setDimensions(k, ncv)
    eps.setTolerances(tol, 20_000)
    if shift_invert:
        eps.setTarget(0.0)
        eps.setWhichEigenpairs(SLEPc.EPS.Which.TARGET_MAGNITUDE)
        st = eps.getST()
        st.setType(SLEPc.ST.Type.SINVERT)
        st.setShift(0.0)
        ksp = st.getKSP()
        ksp.setType(PETSc.KSP.Type.PREONLY)
        ksp.getPC().setType(PETSc.PC.Type.LU)
    else:
        eps.setWhichEigenpairs(SLEPc.EPS.Which.SMALLEST_REAL)

    t0 = time.perf_counter()
    eps.solve()
    elapsed = time.perf_counter() - t0
    nconv = int(eps.getConverged())
    if nconv < k:
        its = int(eps.getIterationNumber())
        eps.destroy()
        raise RuntimeError(f"SLEPc converged {nconv}/{k} eigenpairs after {its} iterations")

    vals = np.asarray(sorted(float(np.real(eps.getEigenvalue(i))) for i in range(k)))
    errors = [float(eps.computeError(i, SLEPc.EPS.ErrorType.RELATIVE)) for i in range(k)]
    max_error = max(errors) if errors else 0.0
    its = int(eps.getIterationNumber())
    eps.destroy()
    return elapsed, vals, max_error, its


def time_slepc(A: PETSc.Mat, k: int, tol: float, *, shift_invert: bool) -> tuple[list[float], np.ndarray, float, list[int]]:
    samples: list[float] = []
    final = None
    max_residual = 0.0
    iterations: list[int] = []
    for _ in range(REPEATS):
        elapsed, vals, residual, its = slepc_once(A, k, tol, shift_invert=shift_invert)
        samples.append(elapsed)
        final = vals
        max_residual = max(max_residual, residual)
        iterations.append(its)
    assert final is not None
    return samples, final, max_residual, iterations


def accuracy_record(values: np.ndarray, reference: np.ndarray, residual: float, tol: float) -> dict[str, float | bool]:
    max_abs = float(np.max(np.abs(values - reference)))
    # The eigenvalue comparison is deliberately slightly looser than the requested
    # iterative tolerance because different solvers use different stopping norms.
    ok = bool(max_abs <= max(50.0 * tol, 1.0e-8) and residual <= 1.0e-7)
    return {
        "max_abs_eigenvalue_difference": max_abs,
        "max_reported_relative_residual": float(residual),
        "ok": ok,
    }


def main() -> int:
    require_compiled_kernel("Retained Spectral vs SLEPc benchmark")
    warm_native_kernel()
    warm_retained_modes()

    record: dict[str, object] = {
        "scope": "serial single-thread real symmetric tridiagonal lowest requested modes",
        "claim_boundary": (
            "This can establish superiority only in the declared cases. It is not a claim over all "
            "SLEPc problem classes, MPI scales, GPUs, non-Hermitian systems, or arbitrary sparsity."
        ),
        "repeats": REPEATS,
        "bootstrap_resamples": BOOTSTRAPS,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "petsc_version": PETSc.Sys.getVersion(),
            "slepc_version": SLEPc.Sys.getVersion(),
            "numpy_version": np.__version__,
        },
        "cases": [],
    }

    all_tuned_native_faster = True
    all_correct = True

    for case in CASES:
        print(f"\n=== n={case.n:,} k={case.k} ===", flush=True)
        d, e = harmonic_tridiagonal(case)
        A = petsc_from_tridiagonal(d, e)
        reference = eigh_tridiagonal(
            d, e, eigvals_only=True, select="i", select_range=(0, case.k - 1), tol=case.tolerance / 10
        )

        native_value_times, native_values = time_native_values(d, e, case.k, case.tolerance)
        native_pair_times, native_pair_values, native_pair_residual, native_orth = time_native_pairs(
            d, e, case.k, case.tolerance
        )
        slepc_times, slepc_values, slepc_residual, slepc_iterations = time_slepc(
            A, case.k, case.tolerance, shift_invert=True
        )

        native_value_acc = accuracy_record(native_values, reference, 0.0, case.tolerance)
        native_pair_acc = accuracy_record(native_pair_values, reference, native_pair_residual, case.tolerance)
        slepc_acc = accuracy_record(slepc_values, reference, slepc_residual, case.tolerance)
        all_correct = all_correct and bool(native_value_acc["ok"] and native_pair_acc["ok"] and slepc_acc["ok"])

        values_ratio = bootstrap_ratio(slepc_times, native_value_times)
        pairs_ratio = bootstrap_ratio(slepc_times, native_pair_times)
        all_tuned_native_faster = all_tuned_native_faster and values_ratio["verdict"] == "native_faster"

        item: dict[str, object] = {
            "case": asdict(case),
            "reference_first": float(reference[0]),
            "reference_last": float(reference[-1]),
            "native_eigenvalues": {
                "samples_seconds": native_value_times,
                "median_seconds": statistics.median(native_value_times),
                "accuracy": native_value_acc,
            },
            "native_eigenpairs": {
                "samples_seconds": native_pair_times,
                "median_seconds": statistics.median(native_pair_times),
                "accuracy": native_pair_acc,
                "orthogonality_error": native_orth,
            },
            "slepc_krylovschur_shiftinvert_eigenpairs": {
                "samples_seconds": slepc_times,
                "median_seconds": statistics.median(slepc_times),
                "accuracy": slepc_acc,
                "iterations": slepc_iterations,
            },
            "slepc_speedup_over_native_eigenvalues": values_ratio,
            "slepc_speedup_over_native_eigenpairs": pairs_ratio,
        }

        # Plain Krylov-Schur is included only on the bounded case; it is a
        # control, while shift-invert is the tuned peer used for the verdict.
        if case.n == CASES[0].n:
            try:
                plain_times, plain_values, plain_residual, plain_iterations = time_slepc(
                    A, case.k, case.tolerance, shift_invert=False
                )
                plain_acc = accuracy_record(plain_values, reference, plain_residual, case.tolerance)
                item["slepc_krylovschur_plain_eigenpairs"] = {
                    "samples_seconds": plain_times,
                    "median_seconds": statistics.median(plain_times),
                    "accuracy": plain_acc,
                    "iterations": plain_iterations,
                    "speedup_over_native_eigenvalues": bootstrap_ratio(plain_times, native_value_times),
                }
                all_correct = all_correct and bool(plain_acc["ok"])
            except RuntimeError as exc:
                item["slepc_krylovschur_plain_eigenpairs"] = {"status": "HOLD", "reason": str(exc)}

        print(
            f"native values {statistics.median(native_value_times):.6f}s | "
            f"native pairs {statistics.median(native_pair_times):.6f}s | "
            f"SLEPc sinvert {statistics.median(slepc_times):.6f}s | "
            f"speedup={values_ratio['median_speedup_peer_over_native']:.2f}x "
            f"CI=[{values_ratio['ci95_low']:.2f},{values_ratio['ci95_high']:.2f}] "
            f"{values_ratio['verdict']}",
            flush=True,
        )
        record["cases"].append(item)
        A.destroy()

    record["gates"] = {
        "all_correct": all_correct,
        "native_faster_than_tuned_slepc_for_eigenvalues_all_declared_cases": all_tuned_native_faster,
    }
    record["verdict"] = (
        "ACCEPT_NATIVE_FASTER_IN_DECLARED_FIELD"
        if all_correct and all_tuned_native_faster
        else "HOLD_NO_UNIVERSAL_SPEED_PROOF"
    )

    out = Path(os.environ.get("IDM_SLEPC_RESULT", "slepc_vs_retained.json"))
    out.write_text(json.dumps(record, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(f"\nVERDICT: {record['verdict']}")
    print(f"record: {out}")
    # Benchmark execution itself succeeds as long as all numerical gates pass;
    # the speed result remains data-driven and may honestly be HOLD.
    return 0 if all_correct else 2


if __name__ == "__main__":
    raise SystemExit(main())
