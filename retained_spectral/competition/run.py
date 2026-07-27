#!/usr/bin/env python3
"""Run the reproducible Retained Spectral competition and write a JSON record.

Two measurements, one file:

1. **End-to-end independent pipelines** — the native RMS solver and an
   independent SciPy pipeline each receive only ``(potential, parameters,
   modes, tolerance)``.  Both discover their own well, window, and mesh.  The
   analytic/reference values are consulted *after* both return, never during
   planning.  Timings are interleaved so neither solver is favoured by cache
   or thermal drift.

2. **Same-operator executor audit** — native, SciPy, and JAX solve one
   identical native-constructed operator (see :mod:`.executor_audit`).

Everything is measured on the host machine at run time; nothing is copied from
a prior report.  Run::

    PYTHONPATH=. python3 -m retained_spectral.competition.run --repeats 9
"""

from __future__ import annotations

import argparse
import os

# Pin every BLAS/LAPACK/threading backend to a single thread BEFORE numpy/scipy/jax import, so a timing
# comparison measures the algorithm, not the host's thread scheduler (B3). setdefault: the caller can
# still override from the shell.
for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_var, "1")
os.environ.setdefault("JAX_PLATFORMS", "cpu")
os.environ.setdefault("JAX_ENABLE_X64", "1")

import json
import platform
import random
import statistics
import sys
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np

from retained_spectral.engine import (
    NATIVE_KERNEL_COMPILED,
    RawBenchmarkTarget,
    raw_benchmark_targets,
    result_as_dict,
    retained_raw_input_readout,
    warm_native_kernel,
)
from retained_spectral.competition.executor_audit import run_executor_audit
from retained_spectral.competition.scipy_pipeline import scipy_raw_input_readout
from retained_spectral.competition.stats import summarize, speedup_ci

DEFAULT_RESULTS = (
    Path(__file__).resolve().parent.parent / "results" / "competition_results.json"
)


def _package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "not-installed"


def _max_reference_error(values, reference) -> float:
    # A solver that returned the WRONG NUMBER of eigenvalues fails outright — never compare on the
    # shorter prefix (that would let a partial result pass correctness).
    if len(values) != len(reference) or len(reference) == 0:
        return float("inf")
    return float(np.max(np.abs(np.asarray(values) - np.asarray(reference))))


def _timed(solver, problem, *, repeats: int) -> tuple[float, object]:
    result = solver(problem)  # warm / compile outside timing
    samples: list[float] = []
    for _ in range(repeats):
        started = time.perf_counter()
        result = solver(problem)
        samples.append(time.perf_counter() - started)
    return float(statistics.median(samples)), result


def end_to_end_case(target: RawBenchmarkTarget, *, repeats: int, seed: int = 20260727) -> dict[str, object]:
    """Interleave native RMS and independent SciPy on one raw problem."""

    problem = target.problem
    native_samples: list[float] = []
    scipy_samples: list[float] = []
    native_result = retained_raw_input_readout(problem)   # warm-up (outside timing)
    scipy_result = scipy_raw_input_readout(problem)

    def _time_native():
        started = time.perf_counter()
        r = retained_raw_input_readout(problem)
        return time.perf_counter() - started, r

    def _time_scipy():
        started = time.perf_counter()
        r = scipy_raw_input_readout(problem)
        return time.perf_counter() - started, r

    # seeded-randomized ordering: shuffle which pipeline runs first on every repeat so neither is
    # systematically favoured by cache/thermal state. The seed is recorded, so the interleaving is
    # reproducible (stronger than a fixed alternation, which a solver could in principle phase-lock to).
    rng = random.Random(f"{seed}:{problem.name}")
    for _ in range(repeats):
        order = [_time_native, _time_scipy]
        rng.shuffle(order)
        for fn in order:
            dt, r = fn()
            if fn is _time_native:
                native_samples.append(dt)
                native_result = r
            else:
                scipy_samples.append(dt)
                scipy_result = r

    native_seconds = float(statistics.median(native_samples))
    scipy_seconds = float(statistics.median(scipy_samples))
    native_error = _max_reference_error(native_result.values, target.reference)
    scipy_error = _max_reference_error(scipy_result.values, target.reference)

    return {
        "reference": list(target.reference),
        "reference_kind": target.reference_kind,
        "tolerance": problem.tolerance,
        "native": {
            **result_as_dict(native_result),
            "hot_median_seconds": native_seconds,
            "expected_modes": len(target.reference),
            "returned_modes": len(native_result.values),
            "max_reference_abs_error": native_error,
            "correct": native_error <= problem.tolerance,   # the DECLARED tolerance, no hidden floor
        },
        "scipy": {
            **result_as_dict(scipy_result),
            "hot_median_seconds": scipy_seconds,
            "expected_modes": len(target.reference),
            "returned_modes": len(scipy_result.values),
            "max_reference_abs_error": scipy_error,
            "correct": scipy_error <= problem.tolerance,
        },
        "scipy_to_native_time_ratio": scipy_seconds / native_seconds,
        "native_stats": summarize(native_samples),
        "scipy_stats": summarize(scipy_samples),
        "scipy_speedup_over_native": speedup_ci(native_samples, scipy_samples),
    }


def run_competition(
    *,
    repeats: int = 9,
    audit_intervals: int = 768,
    audit_repeats: int = 5,
    include_jax: bool = True,
    seed: int = 20260727,
) -> dict[str, object]:
    targets = raw_benchmark_targets()
    warm_native_kernel()

    end_to_end: dict[str, object] = {}
    for target in targets:
        end_to_end[target.problem.name] = end_to_end_case(target, repeats=repeats, seed=seed)

    ratios = [
        case["scipy_to_native_time_ratio"] for case in end_to_end.values()
    ]
    geomean = float(np.exp(np.mean(np.log(ratios))))
    native_correct = sum(case["native"]["correct"] for case in end_to_end.values())
    scipy_correct = sum(case["scipy"]["correct"] for case in end_to_end.values())
    native_accept = sum(
        case["native"]["status"] == "ACCEPT" for case in end_to_end.values()
    )
    scipy_accept = sum(
        case["scipy"]["status"] == "ACCEPT" for case in end_to_end.values()
    )
    native_wins = sum(r > 1.0 for r in ratios)

    audit = run_executor_audit(
        [t.problem for t in targets],
        intervals=audit_intervals,
        repeats=audit_repeats,
        include_jax=include_jax,
    )

    n = len(targets)
    audit_cases = audit.get("cases", {})
    executor_cross_check_all = bool(audit_cases) and all(
        c.get("cross_check_ok") for c in audit_cases.values()
    )
    executor_complete_all = all(
        c.get("comparison_complete", True) for c in audit_cases.values()
    )

    # THREE independent verdicts — speed never compensates for incorrectness, correctness never
    # compensates for an unequal/incomplete comparison.
    correctness_verdict = "ACCEPT" if (native_correct == n and scipy_correct == n) else "HOLD"
    fairness_verdict = "ACCEPT" if (executor_cross_check_all and executor_complete_all) else "HOLD"
    # median-based (confidence intervals are B3): ACCEPT only if native is faster in EVERY case;
    # if any case has a competitor faster it is HOLD (never silently an overall ACCEPT).
    # CI-based speed verdict on the PRIMARY same-work peer (SciPy eigh_tridiagonal, kernel-only):
    # native win requires the 95% bootstrap CI of the speedup to sit entirely above 1 in EVERY case.
    peer = "SciPy eigh_tridiagonal"
    peer_verdicts = [
        c["solvers"].get(peer, {}).get("speedup_over_native", {}).get("verdict", "insufficient-samples")
        for c in audit_cases.values()
    ]
    if peer_verdicts and all(v == "native_faster" for v in peer_verdicts):
        speed_verdict = "ACCEPT"
    elif any(v == "competitor_faster" for v in peer_verdicts):
        speed_verdict = "HOLD"
    else:
        speed_verdict = "TIE"
    # Named gates (every one must pass for an overall ACCEPT). "both pipelines ACCEPT" is a stronger
    # fairness bar than native-only: an unconverged competitor cannot flatter the native win.
    verdict_gates = {
        "native_correct_all": native_correct == n,
        "scipy_correct_all": scipy_correct == n,
        "native_accept_all": native_accept == n,
        "scipy_accept_all": scipy_accept == n,
        "executor_cross_check_all": executor_cross_check_all,
        "executor_comparison_complete_all": executor_complete_all,
        "speed_ci_native_faster_all": speed_verdict == "ACCEPT",
    }
    strict_accept = all(verdict_gates.values())
    verdict = "ACCEPT" if strict_accept else "HOLD"

    return {
        "schema": "idm.retained-spectral-competition.v1",
        "simulation": False,
        "source_commit": os.environ.get("GITHUB_SHA", "not-recorded"),
        "claim_scope": (
            "finite_diagnostic agreement and wall-clock cost on seven declared "
            "1-D Schrodinger spectra; the native method is faster than an "
            "independent SciPy pipeline end-to-end and than SciPy/JAX on an "
            "identical operator; no universal quantum-advantage or "
            "empirical-physics claim is made"
        ),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "processor": platform.processor() or "unknown",
            "numpy": np.__version__,
            "numba": _package_version("numba"),
            # the native Sturm kernel is Numba/LLVM-JIT-compiled only when numba is importable; without
            # it the SAME exact recurrence runs in pure Python, numerically identical but far slower, so
            # a False here means the wall-clock speed numbers are NOT the compiled field and must not be
            # read as the headline result.
            "native_kernel_compiled": bool(NATIVE_KERNEL_COMPILED),
            "scipy": _package_version("scipy"),
            "jax": _package_version("jax"),
            "jaxlib": _package_version("jaxlib"),
            "thread_environment": {
                name: os.environ.get(name, "unset")
                for name in (
                    "OMP_NUM_THREADS",
                    "OPENBLAS_NUM_THREADS",
                    "MKL_NUM_THREADS",
                    "VECLIB_MAXIMUM_THREADS",
                    "NUMEXPR_NUM_THREADS",
                )
            },
        },
        "end_to_end": {
            "boundary": (
                "both pipelines receive only (potential, parameters, modes, "
                "tolerance); references consulted only after both return"
            ),
            "repeats": repeats,
            "seed": seed,
            "timing_order": "seeded-randomized per repeat after one untimed warm run",
            "summary": {
                "cases": len(targets),
                "native_correct": native_correct,
                "scipy_correct": scipy_correct,
                "native_accepted": native_accept,
                "scipy_accepted": scipy_accept,
                "native_faster_cases": native_wins,
                "speedup_min": float(min(ratios)),
                "speedup_max": float(max(ratios)),
                "speedup_geomean": geomean,
            },
            "cases": end_to_end,
        },
        "executor_audit": audit,
        "verdict": verdict,
        "verdict_gates": verdict_gates,
        "verdicts": {
            "correctness": correctness_verdict,   # native AND scipy hit references within DECLARED tol
            "fairness": fairness_verdict,          # executor audit cross-checked AND complete (no solver errors)
            "speed": speed_verdict,                # from the 95% bootstrap CI of the same-work peer speedup
            "note": "speed ACCEPT requires the 95% bootstrap CI of native-vs-SciPy-eigh_tridiagonal "
                    "(kernel-only) to sit above 1 in EVERY case; TIE if a CI straddles 1, HOLD if a "
                    "competitor's CI is below 1. Overall ACCEPT requires ALL verdict_gates: both "
                    "pipelines correct AND both ACCEPT at the declared tolerance, executor cross-checks "
                    "complete, and the CI-based speed win in every case. Multi-process runs are the "
                    "remaining B3 item.",
        },
        "tier": "finite_diagnostic",
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=9)
    parser.add_argument("--audit-intervals", type=int, default=768)
    parser.add_argument("--audit-repeats", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260727)
    parser.add_argument("--no-jax", action="store_true")
    parser.add_argument("--json", type=Path, default=DEFAULT_RESULTS)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    result = run_competition(
        repeats=args.repeats,
        audit_intervals=args.audit_intervals,
        audit_repeats=args.audit_repeats,
        include_jax=not args.no_jax,
        seed=args.seed,
    )
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary = result["end_to_end"]["summary"]
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("verdict:", result["verdict"])
    print("results:", args.json)
    return 0 if result["verdict"] == "ACCEPT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
