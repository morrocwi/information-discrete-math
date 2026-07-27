#!/usr/bin/env python3
"""Adversarial and scaling audit for the Retained Spectral benchmark.

This is deliberately stronger than the seven-case product demo.  It checks
translated/narrow/broad wells, more bound states, a factorized double well,
quartic scale covariance, requested-mode scaling, exact declared tolerances,
and cold versus warmed execution.  Performance observations never substitute
for correctness gates.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import random
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.linalg import eigh_tridiagonal

from retained_spectral.engine import (
    RawSpectralProblem,
    _finite_native_readout,
    raw_benchmark_targets,
    retained_raw_input_readout,
    retained_tridiagonal,
    warm_native_kernel,
)
from retained_spectral.competition.scipy_pipeline import scipy_raw_input_readout
from retained_spectral.competition.run import run_competition
from retained_spectral.competition.correctness import three_layer_case


@dataclass(frozen=True)
class AuditTarget:
    problem: RawSpectralProblem
    reference: tuple[float, ...]
    reason: str


def _problem(
    name: str,
    potential: str,
    parameters: dict[str, float],
    modes: int,
    tolerance: float,
) -> RawSpectralProblem:
    return RawSpectralProblem(
        name=name,
        potential=potential,
        parameters=tuple(parameters.items()),
        modes=modes,
        tolerance=tolerance,
    )


def adversarial_targets() -> tuple[AuditTarget, ...]:
    quartic_anchor = 0.420804974478
    morse_lambda = 8.0
    morse_a = 0.75
    morse_depth = (morse_lambda * morse_a) ** 2 / 2.0
    return (
        AuditTarget(
            _problem(
                "audit_harmonic_center80",
                "harmonic",
                {"omega": 1.0, "center": 80.0},
                4,
                5.0e-7,
            ),
            tuple(n + 0.5 for n in range(4)),
            "minimum lies far outside the original competitor's fixed search box",
        ),
        AuditTarget(
            _problem(
                "audit_harmonic_broad",
                "harmonic",
                {"omega": 0.1, "center": -40.0},
                6,
                5.0e-6,
            ),
            tuple(0.1 * (n + 0.5) for n in range(6)),
            "broad translated well stresses boundary expansion",
        ),
        AuditTarget(
            _problem(
                "audit_harmonic_narrow",
                "harmonic",
                {"omega": 64.0, "center": 13.0},
                6,
                1.0e-4,
            ),
            tuple(64.0 * (n + 0.5) for n in range(6)),
            "narrow translated well stresses mesh refinement",
        ),
        AuditTarget(
            _problem(
                "audit_poschl_lambda6",
                "poschl_teller",
                {"lambda": 6.0},
                6,
                2.0e-5,
            ),
            tuple(-0.5 * (6.0 - n) ** 2 for n in range(6)),
            "all six bound modes, including the shallowest state",
        ),
        AuditTarget(
            _problem(
                "audit_morse_lambda8",
                "morse",
                {"a": morse_a, "depth": morse_depth},
                8,
                5.0e-5,
            ),
            tuple(
                -0.5 * morse_a**2 * (morse_lambda - n - 0.5) ** 2
                for n in range(8)
            ),
            "asymmetric well with eight bound modes",
        ),
        AuditTarget(
            _problem(
                "audit_factorized_double_well",
                "factorized_sextic",
                {"a": -1.0},
                1,
                5.0e-6,
            ),
            (0.0,),
            "factorized double-well ground state has exact zero energy",
        ),
        AuditTarget(
            _problem(
                "audit_quartic_broad",
                "pure_quartic",
                {"coupling": 0.00025},
                1,
                1.0e-6,
            ),
            (quartic_anchor * (0.00025 / 0.25) ** (1.0 / 3.0),),
            "quartic scale covariance over three decades downward",
        ),
        AuditTarget(
            _problem(
                "audit_quartic_stiff",
                "pure_quartic",
                {"coupling": 16.0},
                1,
                1.0e-5,
            ),
            (quartic_anchor * (16.0 / 0.25) ** (1.0 / 3.0),),
            "quartic scale covariance over two decades upward",
        ),
    )


def _max_error(values, reference) -> float:
    if len(values) != len(reference):
        return float("inf")
    return float(
        np.max(
            np.abs(
                np.asarray(values, dtype=np.float64)
                - np.asarray(reference, dtype=np.float64)
            )
        )
    )


def run_adversarial() -> dict[str, object]:
    cases: dict[str, object] = {}
    all_ok = True
    for target in adversarial_targets():
        problem = target.problem
        record: dict[str, object] = {
            "reason": target.reason,
            "reference": list(target.reference),
            "tolerance": problem.tolerance,
        }
        for label, solver in (
            ("native", retained_raw_input_readout),
            ("scipy", scipy_raw_input_readout),
        ):
            started = time.perf_counter()
            try:
                result = solver(problem)
                elapsed = time.perf_counter() - started
                error = _max_error(result.values, target.reference)
                ok = result.status == "ACCEPT" and error <= problem.tolerance
                record[label] = {
                    "status": result.status,
                    "values": list(result.values),
                    "window": list(result.window),
                    "finest_intervals": result.finest_intervals,
                    "solve_count": result.solve_count,
                    "elapsed_seconds": elapsed,
                    "max_reference_abs_error": error,
                    "correct_at_declared_tolerance": ok,
                }
            except Exception as exc:  # failure must be visible in the artifact
                ok = False
                record[label] = {
                    "error": f"{type(exc).__name__}: {exc}",
                    "correct_at_declared_tolerance": False,
                }
            all_ok = all_ok and ok
        cases[problem.name] = record
    return {"all_ok": bool(all_ok), "cases": cases}


def _timed_randomized(
    native_fn,
    scipy_fn,
    *,
    repeats: int,
    seed: int,
) -> tuple[list[float], list[float], object, object]:
    native_fn()
    scipy_fn()
    native_samples: list[float] = []
    scipy_samples: list[float] = []
    native_value = None
    scipy_value = None
    rng = random.Random(seed)
    for _ in range(repeats):
        order = ["native", "scipy"]
        rng.shuffle(order)
        for label in order:
            started = time.perf_counter()
            if label == "native":
                native_value = native_fn()
                native_samples.append(time.perf_counter() - started)
            else:
                scipy_value = scipy_fn()
                scipy_samples.append(time.perf_counter() - started)
    return native_samples, scipy_samples, native_value, scipy_value


def run_scaling(*, repeats: int = 7) -> dict[str, object]:
    """Requested-mode/grid scaling against the fair tridiagonal comparator."""

    warm_native_kernel()
    cases: dict[str, object] = {}
    all_cross_checks = True
    for intervals in (256, 512, 1024, 2048):
        for modes in (1, 4, 8, 16, 32):
            if modes >= intervals:
                continue
            problem = _problem(
                f"scaling_n{intervals}_k{modes}",
                "harmonic",
                {"omega": 1.0, "center": 0.0},
                modes,
                1.0e-8,
            )
            window = (-12.0, 12.0)
            diagonal, off_diagonal, _ = retained_tridiagonal(
                problem, window, intervals
            )

            def native_fn():
                return _finite_native_readout(
                    problem,
                    window,
                    intervals,
                    energy_tolerance=1.0e-10,
                )

            def scipy_fn():
                return eigh_tridiagonal(
                    diagonal,
                    off_diagonal,
                    select="i",
                    select_range=(0, modes - 1),
                    eigvals_only=True,
                    check_finite=False,
                )

            native_samples, scipy_samples, native_value, scipy_value = _timed_randomized(
                native_fn,
                scipy_fn,
                repeats=repeats,
                seed=intervals * 1000 + modes,
            )
            native_values = np.asarray(native_value.values)
            scipy_values = np.asarray(scipy_value)
            difference = float(np.max(np.abs(native_values - scipy_values)))
            cross_ok = difference <= 1.0e-6
            all_cross_checks = all_cross_checks and cross_ok
            native_median = float(statistics.median(native_samples))
            scipy_median = float(statistics.median(scipy_samples))
            cases[problem.name] = {
                "intervals": intervals,
                "modes": modes,
                "native_median_seconds": native_median,
                "scipy_eigh_tridiagonal_median_seconds": scipy_median,
                "scipy_to_native_time_ratio": scipy_median / native_median,
                "max_abs_difference": difference,
                "cross_check_ok": cross_ok,
            }
    return {"all_cross_checks": bool(all_cross_checks), "cases": cases}


def _cold_command(kind: str) -> str:
    solver_import = (
        "from retained_spectral.engine import retained_raw_input_readout as solve"
        if kind == "native"
        else "from retained_spectral.competition.scipy_pipeline import "
        "scipy_raw_input_readout as solve"
    )
    return f"""
import json, time
from retained_spectral.engine import RawSpectralProblem
{solver_import}
p = RawSpectralProblem('cold', 'harmonic', (('omega', 1.0), ('center', 0.0)), 4, 2e-8)
t = time.perf_counter(); r = solve(p); elapsed = time.perf_counter() - t
print(json.dumps({{'status': r.status, 'values': r.values, 'elapsed_seconds': elapsed}}))
"""


def run_cold_start() -> dict[str, object]:
    records: dict[str, object] = {}
    for kind in ("native", "scipy"):
        started = time.perf_counter()
        completed = subprocess.run(
            [sys.executable, "-c", _cold_command(kind)],
            check=False,
            text=True,
            capture_output=True,
            env=os.environ.copy(),
        )
        wall = time.perf_counter() - started
        records[kind] = {
            "process_wall_seconds": wall,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
    return records


def run_three_layer_correctness() -> dict[str, object]:
    """Three independent correctness layers per declared spectrum (B4): external analytic reference,
    an extended-precision recomputation of the same discrete operator, and a Sturm sign-count index
    certificate. A speed benchmark is only trustworthy on top of an independently-checked correct answer.
    """
    cases: dict[str, object] = {}
    all_ok = True
    for target in raw_benchmark_targets():
        rec = three_layer_case(target.problem, target.reference)
        cases[target.problem.name] = rec
        all_ok = all_ok and rec["ok"]
    return {"all_ok": bool(all_ok), "cases": cases}


def run_credibility_audit(
    *,
    include_jax: bool = True,
    baseline_repeats: int = 9,
    executor_repeats: int = 5,
    scaling_repeats: int = 7,
) -> dict[str, object]:
    baseline = run_competition(
        repeats=baseline_repeats,
        audit_intervals=512,
        audit_repeats=executor_repeats,
        include_jax=include_jax,
    )
    adversarial = run_adversarial()
    scaling = run_scaling(repeats=scaling_repeats)
    cold_start = run_cold_start()
    three_layer = run_three_layer_correctness()

    # Two separate axes, never conflated (the repo's tier-honesty rule):
    #   (1) credibility gates — is the reproduction itself sound? correctness on the adversarial
    #       suite, scaling cross-checks, a recorded source commit, a frozen thread environment.
    #       These are what THIS audit certifies, and what its exit code / CI gate on.
    #   (2) baseline_benchmark_verdict — the SEPARATE speed/fairness claim from run_competition.
    #       It can honestly be HOLD (e.g. a competitor like ARPACK fails to converge on one well)
    #       WITHOUT making the reproduction less credible. It is reported, not gated: a green
    #       credibility run never silently implies the native method won every peer contest.
    credibility_gates = {
        "three_layer_correctness_all": three_layer["all_ok"],
        "adversarial_correctness_all": adversarial["all_ok"],
        "scaling_cross_checks_all": scaling["all_cross_checks"],
        "source_commit_recorded": baseline["source_commit"] != "not-recorded",
        "frozen_thread_environment": all(
            baseline["environment"]["thread_environment"][name] == "1"
            for name in baseline["environment"]["thread_environment"]
        ),
    }
    verdict = "ACCEPT" if all(credibility_gates.values()) else "HOLD"
    return {
        "schema": "idm.retained-spectral-credibility-audit.v2",
        "simulation": False,
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
            "github_sha": os.environ.get("GITHUB_SHA", "not-recorded"),
            "github_runner_os": os.environ.get("RUNNER_OS", "local"),
        },
        "baseline": baseline,
        "three_layer_correctness": three_layer,
        "adversarial": adversarial,
        "scaling": scaling,
        "cold_start": cold_start,
        "credibility_gates": credibility_gates,
        "baseline_benchmark_verdict": baseline["verdict"],  # reported, NOT a credibility gate
        "verdict": verdict,
        "scope_note": (
            "ACCEPT certifies REPRODUCIBILITY and CORRECTNESS for the declared and adversarial "
            "one-dimensional finite-diagnostic suite (exact declared tolerances, scaling "
            "cross-checks, recorded commit, frozen threads). It is deliberately separate from "
            "baseline_benchmark_verdict, the speed/fairness contest, which may be HOLD when a "
            "competitor does not converge — that never lowers this reproduction's credibility, and "
            "a green audit never implies universal solver dominance."
        ),
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-jax", action="store_true")
    parser.add_argument("--baseline-repeats", type=int, default=9)
    parser.add_argument("--executor-repeats", type=int, default=5)
    parser.add_argument("--scaling-repeats", type=int, default=7)
    parser.add_argument("--json", type=Path, default=Path("credibility-audit.json"))
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    result = run_credibility_audit(
        include_jax=not args.no_jax,
        baseline_repeats=args.baseline_repeats,
        executor_repeats=args.executor_repeats,
        scaling_repeats=args.scaling_repeats,
    )
    args.json.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["credibility_gates"], indent=2, sort_keys=True))
    print("credibility verdict:", result["verdict"])
    print("baseline benchmark verdict (reported, not gated):", result["baseline_benchmark_verdict"])
    print("results:", args.json)
    return 0 if result["verdict"] == "ACCEPT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
