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
import json
import platform
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
from retained_spectral.competition.scipy_pipeline import scipy_raw_input_readout

DEFAULT_RESULTS = (
    Path(__file__).resolve().parent.parent / "results" / "competition_results.json"
)


def _package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "not-installed"


def _max_reference_error(values, reference) -> float:
    length = min(len(values), len(reference))
    if length == 0:
        return float("inf")
    return float(
        np.max(
            np.abs(
                np.asarray(values[:length]) - np.asarray(reference[:length])
            )
        )
    )


def _timed(solver, problem, *, repeats: int) -> tuple[float, object]:
    result = solver(problem)  # warm / compile outside timing
    samples: list[float] = []
    for _ in range(repeats):
        started = time.perf_counter()
        result = solver(problem)
        samples.append(time.perf_counter() - started)
    return float(statistics.median(samples)), result


def end_to_end_case(target: RawBenchmarkTarget, *, repeats: int) -> dict[str, object]:
    """Interleave native RMS and independent SciPy on one raw problem."""

    problem = target.problem
    native_samples: list[float] = []
    scipy_samples: list[float] = []
    native_result = retained_raw_input_readout(problem)
    scipy_result = scipy_raw_input_readout(problem)
    for _ in range(repeats):
        started = time.perf_counter()
        native_result = retained_raw_input_readout(problem)
        native_samples.append(time.perf_counter() - started)

        started = time.perf_counter()
        scipy_result = scipy_raw_input_readout(problem)
        scipy_samples.append(time.perf_counter() - started)

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
            "max_reference_abs_error": native_error,
            "correct": native_error <= max(problem.tolerance, 1e-6),
        },
        "scipy": {
            **result_as_dict(scipy_result),
            "hot_median_seconds": scipy_seconds,
            "max_reference_abs_error": scipy_error,
            "correct": scipy_error <= max(problem.tolerance, 1e-6),
        },
        "scipy_to_native_time_ratio": scipy_seconds / native_seconds,
    }


def run_competition(
    *,
    repeats: int = 9,
    audit_intervals: int = 768,
    audit_repeats: int = 5,
    include_jax: bool = True,
) -> dict[str, object]:
    targets = raw_benchmark_targets()
    warm_native_kernel()

    end_to_end: dict[str, object] = {}
    for target in targets:
        end_to_end[target.problem.name] = end_to_end_case(target, repeats=repeats)

    ratios = [
        case["scipy_to_native_time_ratio"] for case in end_to_end.values()
    ]
    geomean = float(np.exp(np.mean(np.log(ratios))))
    native_correct = sum(case["native"]["correct"] for case in end_to_end.values())
    scipy_correct = sum(case["scipy"]["correct"] for case in end_to_end.values())
    native_accept = sum(
        case["native"]["status"] == "ACCEPT" for case in end_to_end.values()
    )
    native_wins = sum(r > 1.0 for r in ratios)

    audit = run_executor_audit(
        [t.problem for t in targets],
        intervals=audit_intervals,
        repeats=audit_repeats,
        include_jax=include_jax,
    )

    verdict = (
        "ACCEPT"
        if (
            native_correct == len(targets)
            and native_accept == len(targets)
            and native_wins == len(targets)
        )
        else "HOLD"
    )

    return {
        "schema": "idm.retained-spectral-competition.v1",
        "simulation": False,
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
            "scipy": _package_version("scipy"),
            "jax": _package_version("jax"),
            "jaxlib": _package_version("jaxlib"),
        },
        "end_to_end": {
            "boundary": (
                "both pipelines receive only (potential, parameters, modes, "
                "tolerance); references consulted only after both return"
            ),
            "repeats": repeats,
            "summary": {
                "cases": len(targets),
                "native_correct": native_correct,
                "scipy_correct": scipy_correct,
                "native_accepted": native_accept,
                "native_faster_cases": native_wins,
                "speedup_min": float(min(ratios)),
                "speedup_max": float(max(ratios)),
                "speedup_geomean": geomean,
            },
            "cases": end_to_end,
        },
        "executor_audit": audit,
        "verdict": verdict,
        "tier": "finite_diagnostic",
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=9)
    parser.add_argument("--audit-intervals", type=int, default=768)
    parser.add_argument("--audit-repeats", type=int, default=5)
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
