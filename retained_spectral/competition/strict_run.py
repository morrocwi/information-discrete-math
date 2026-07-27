#!/usr/bin/env python3
"""Strict reproducibility competition for Retained Spectral.

Differences from the first competition runner:

* the independent SciPy pipeline has an expanding, reference-blind well search;
* correctness is checked against the declared tolerance exactly (no 1e-6 floor);
* native/SciPy timing order is randomized on every repeat;
* both pipelines must be correct and ACCEPT;
* the same-operator audit and the fair requested-only SciPy tridiagonal comparator
  must cross-check before the overall verdict can be ACCEPT.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import random
import statistics
import sys
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np

from retained_spectral.engine import (
    RawBenchmarkTarget,
    raw_benchmark_targets,
    result_as_dict,
    retained_raw_input_readout,
    warm_native_kernel,
)
from retained_spectral.competition.executor_audit import run_executor_audit
from retained_spectral.competition.scipy_pipeline_strict import (
    scipy_raw_input_readout_strict,
)

DEFAULT_RESULTS = (
    Path(__file__).resolve().parent.parent / "results" / "strict_competition_results.json"
)


def _package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "not-installed"


def _max_reference_error(values, reference) -> float:
    length = min(len(values), len(reference))
    if length == 0 or len(values) != len(reference):
        return float("inf")
    return float(
        np.max(
            np.abs(
                np.asarray(values[:length], dtype=np.float64)
                - np.asarray(reference[:length], dtype=np.float64)
            )
        )
    )


def _distribution(samples: list[float]) -> dict[str, object]:
    ordered = sorted(float(value) for value in samples)
    return {
        "samples_seconds": ordered,
        "median_seconds": float(statistics.median(ordered)),
        "min_seconds": float(ordered[0]),
        "max_seconds": float(ordered[-1]),
    }


def end_to_end_case(
    target: RawBenchmarkTarget,
    *,
    repeats: int,
    seed: int,
) -> dict[str, object]:
    """Randomly interleave both independent pipelines on one raw problem."""

    problem = target.problem
    native_result = retained_raw_input_readout(problem)
    scipy_result = scipy_raw_input_readout_strict(problem)
    native_samples: list[float] = []
    scipy_samples: list[float] = []
    rng = random.Random(f"{seed}:{problem.name}")

    for _ in range(repeats):
        order = ["native", "scipy"]
        rng.shuffle(order)
        for name in order:
            started = time.perf_counter()
            if name == "native":
                native_result = retained_raw_input_readout(problem)
                native_samples.append(time.perf_counter() - started)
            else:
                scipy_result = scipy_raw_input_readout_strict(problem)
                scipy_samples.append(time.perf_counter() - started)

    native_timing = _distribution(native_samples)
    scipy_timing = _distribution(scipy_samples)
    native_seconds = float(native_timing["median_seconds"])
    scipy_seconds = float(scipy_timing["median_seconds"])
    native_error = _max_reference_error(native_result.values, target.reference)
    scipy_error = _max_reference_error(scipy_result.values, target.reference)

    return {
        "reference": list(target.reference),
        "reference_kind": target.reference_kind,
        "tolerance": problem.tolerance,
        "timing_order": "randomized per repeat after one untimed warm run",
        "native": {
            **result_as_dict(native_result),
            "timing": native_timing,
            "hot_median_seconds": native_seconds,
            "max_reference_abs_error": native_error,
            "correct": native_error <= problem.tolerance,
        },
        "scipy": {
            **result_as_dict(scipy_result),
            "timing": scipy_timing,
            "hot_median_seconds": scipy_seconds,
            "max_reference_abs_error": scipy_error,
            "correct": scipy_error <= problem.tolerance,
        },
        "scipy_to_native_time_ratio": scipy_seconds / native_seconds,
    }


def _audit_gates(audit: dict[str, object]) -> dict[str, object]:
    cases = audit["cases"]
    per_case: dict[str, object] = {}
    all_converged_cross_checks = True
    fair_comparator_all_ok = True
    for name, case in cases.items():
        solvers = case["solvers"]
        fair = solvers.get("SciPy eigh_tridiagonal")
        fair_ok = bool(
            fair
            and "error" not in fair
            and fair.get("cross_check_ok") is True
        )
        converged_ok = bool(case.get("cross_check_ok"))
        all_converged_cross_checks = all_converged_cross_checks and converged_ok
        fair_comparator_all_ok = fair_comparator_all_ok and fair_ok
        per_case[name] = {
            "all_converged_cross_checks": converged_ok,
            "fair_requested_only_comparator_ok": fair_ok,
            "competitor_errors": {
                solver: details["error"]
                for solver, details in solvers.items()
                if "error" in details
            },
        }
    return {
        "all_converged_cross_checks": bool(all_converged_cross_checks),
        "fair_requested_only_comparator_all_ok": bool(fair_comparator_all_ok),
        "cases": per_case,
    }


def run_strict_competition(
    *,
    repeats: int = 11,
    audit_intervals: int = 768,
    audit_repeats: int = 7,
    include_jax: bool = True,
    seed: int = 20260727,
) -> dict[str, object]:
    targets = raw_benchmark_targets()
    warm_native_kernel()

    end_to_end: dict[str, object] = {}
    for target in targets:
        end_to_end[target.problem.name] = end_to_end_case(
            target, repeats=repeats, seed=seed
        )

    ratios = [
        float(case["scipy_to_native_time_ratio"]) for case in end_to_end.values()
    ]
    geomean = float(np.exp(np.mean(np.log(ratios))))
    native_correct = sum(bool(case["native"]["correct"]) for case in end_to_end.values())
    scipy_correct = sum(bool(case["scipy"]["correct"]) for case in end_to_end.values())
    native_accept = sum(
        case["native"]["status"] == "ACCEPT" for case in end_to_end.values()
    )
    scipy_accept = sum(
        case["scipy"]["status"] == "ACCEPT" for case in end_to_end.values()
    )
    native_wins = sum(ratio > 1.0 for ratio in ratios)

    audit = run_executor_audit(
        [target.problem for target in targets],
        intervals=audit_intervals,
        repeats=audit_repeats,
        include_jax=include_jax,
    )
    audit_gates = _audit_gates(audit)

    gate_values = {
        "native_correct_all": native_correct == len(targets),
        "scipy_correct_all": scipy_correct == len(targets),
        "native_accept_all": native_accept == len(targets),
        "scipy_accept_all": scipy_accept == len(targets),
        "native_faster_all_declared_cases": native_wins == len(targets),
        "all_converged_executor_cross_checks": audit_gates[
            "all_converged_cross_checks"
        ],
        "fair_requested_only_comparator_all_ok": audit_gates[
            "fair_requested_only_comparator_all_ok"
        ],
    }
    verdict = "ACCEPT" if all(gate_values.values()) else "HOLD"

    return {
        "schema": "idm.retained-spectral-strict-competition.v2",
        "simulation": False,
        "source_commit": os.environ.get("GITHUB_SHA", "not-recorded"),
        "claim_scope": (
            "finite_diagnostic correctness and wall-clock cost on seven declared "
            "1-D Schrodinger spectra under a frozen CPU environment; the strict "
            "verdict requires both independent pipelines to hit the declared "
            "tolerance, both to ACCEPT, randomized-order native wins on every "
            "declared case, and same-operator cross-checks including SciPy's "
            "requested-only tridiagonal solver; no universal advantage claim"
        ),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "processor": platform.processor() or "unknown",
            "numpy": np.__version__,
            "numba": _package_version("numba"),
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
                "both pipelines receive only potential, finite parameters, modes, "
                "and tolerance; references are consulted only after return"
            ),
            "repeats": repeats,
            "seed": seed,
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
        "audit_gates": audit_gates,
        "verdict_gates": gate_values,
        "verdict": verdict,
        "tier": "finite_diagnostic",
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=11)
    parser.add_argument("--audit-intervals", type=int, default=768)
    parser.add_argument("--audit-repeats", type=int, default=7)
    parser.add_argument("--seed", type=int, default=20260727)
    parser.add_argument("--no-jax", action="store_true")
    parser.add_argument("--json", type=Path, default=DEFAULT_RESULTS)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    result = run_strict_competition(
        repeats=args.repeats,
        audit_intervals=args.audit_intervals,
        audit_repeats=args.audit_repeats,
        include_jax=not args.no_jax,
        seed=args.seed,
    )
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["end_to_end"]["summary"], indent=2, sort_keys=True))
    print(json.dumps(result["verdict_gates"], indent=2, sort_keys=True))
    print("verdict:", result["verdict"])
    print("results:", args.json)
    return 0 if result["verdict"] == "ACCEPT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
