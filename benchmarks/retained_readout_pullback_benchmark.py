#!/usr/bin/env python3
"""benchmarks/retained_readout_pullback_benchmark.py — reproduction harness for native RRP.

Runs the native Retained Fold Tree / Retained Readout Pullback executor
(`benchmarks/retained_fold_tree.py`) on sparse and complete pairwise families and cross-checks every
readout against an INDEPENDENT reference: the partition and moments recomputed by tilted-factor
contraction (never the RFT downward pass), and the log-partition gradients against central finite
differences. Autograd is used ONLY as an optional external comparator; the benchmark is fully
self-checking without it. Emits machine-readable JSON with a `finite_diagnostic` verdict.

Usage:
    python3 benchmarks/retained_readout_pullback_benchmark.py --repeats 31 \
        --output benchmarks/retained_readout_pullback_results.json
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coupled_nd_retained_compiler import PairwiseProblem, default_problem  # noqa: E402
from retained_fold_tree import compile_retained_readout_pullback, reference_readouts  # noqa: E402


def complete_problem(dimension: int) -> PairwiseProblem:
    linear = tuple(0.15 + 0.03 * axis for axis in range(dimension))
    couplings = tuple(
        (i, j, 0.04 + 0.01 * ((i * dimension + j) % 5))
        for i in range(dimension)
        for j in range(i + 1, dimension)
    )
    return PairwiseProblem(dimension, linear, couplings)


def _median_hot_seconds(problem, order, repeats):
    compile_retained_readout_pullback(problem, order)   # warm any import/JIT cost out of the timing
    samples = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        compile_retained_readout_pullback(problem, order)
        samples.append(time.perf_counter() - t0)
    return statistics.median(samples), min(samples), max(samples)


def _fd_loggrad(problem, order, h=1e-6):
    base = list(problem.linear) + [s for _l, _r, s in problem.couplings]
    d = problem.dimension

    def logZ(theta):
        lin = tuple(theta[:d])
        cpl = tuple((l, r, theta[d + e]) for e, (l, r, _s) in enumerate(problem.couplings))
        return math.log(reference_readouts(PairwiseProblem(d, lin, cpl), order)[0])

    grad = []
    for k in range(len(base)):
        tp = base[:]; tm = base[:]; tp[k] += h; tm[k] -= h
        grad.append((logZ(tp) - logZ(tm)) / (2 * h))
    return grad


def run_case(family, problem, order, repeats, check_fd):
    result = compile_retained_readout_pullback(problem, order)
    p = result.retained_readout_pullback
    Z_ref, mu_ref, chi_ref = reference_readouts(problem, order)

    d_Z = abs(result.value - Z_ref)
    d_mu = max((abs(a - b) for a, b in zip(result.axis_first_moments, mu_ref)), default=0.0)
    d_chi = max((abs(a - b) for a, b in zip(p.coupling_cross_moments, chi_ref)), default=0.0)

    d_grad = None
    if check_fd:
        grad_rft = p.log_partition_linear_gradients + p.log_partition_coupling_gradients
        grad_fd = _fd_loggrad(problem, order)
        d_grad = max(abs(a - b) for a, b in zip(grad_rft, grad_fd))

    median_s, min_s, max_s = _median_hot_seconds(problem, order, repeats)
    return {
        "family": family,
        "dimension": problem.dimension,
        "coupling_count": len(problem.couplings),
        "order": order,
        "parameter_count": problem.dimension + len(problem.couplings),
        "closure_count": result.closure_count,
        "native_rft": {
            "median_seconds": median_s, "minimum_seconds": min_s, "maximum_seconds": max_s,
            "pullback_work_elements": p.pullback_work_elements,
            "retained_basis_elements": p.retained_basis_elements,
            "autodiff": False, "junction_tree": False,
        },
        "agreement_vs_reference": {
            "partition_abs_difference": d_Z,
            "axis_moment_max_abs_difference": d_mu,
            "coupling_moment_max_abs_difference": d_chi,
            "log_partition_gradient_vs_central_fd": d_grad,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="native RRP reproduction + self-check")
    ap.add_argument("--repeats", type=int, default=31)
    ap.add_argument("--order", type=int, default=4)
    ap.add_argument("--output", type=str, default="")
    ap.add_argument("--tolerance", type=float, default=1e-9)
    args = ap.parse_args()

    cases = []
    for d in (5, 7, 9, 11):
        cases.append(run_case("sparse", default_problem(d), args.order, args.repeats, check_fd=(d <= 7)))
    for d in (5, 7, 8):
        cases.append(run_case("complete", complete_problem(d), args.order, args.repeats, check_fd=(d <= 5)))

    worst = 0.0
    for c in cases:
        a = c["agreement_vs_reference"]
        worst = max(worst, a["partition_abs_difference"], a["axis_moment_max_abs_difference"],
                    a["coupling_moment_max_abs_difference"])
        if a["log_partition_gradient_vs_central_fd"] is not None:
            worst = max(worst, a["log_partition_gradient_vs_central_fd"])
    verdict = "ACCEPT" if worst <= args.tolerance else "HOLD"

    report = {
        "benchmark": "native_retained_readout_pullback_self_check",
        "method": "one upward FTCC fold + one downward relevance unfold (RRP); no autodiff, no junction tree",
        "reference": "independent tilted-factor contraction + central finite differences",
        "tier": "finite_diagnostic",
        "order": args.order, "repeats": args.repeats, "tolerance": args.tolerance,
        "worst_abs_difference": worst, "verdict": verdict,
        "cases": cases,
    }
    text = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)

    print(f"\nVERDICT: {verdict}  (worst |Δ| = {worst:.2e} ≤ tol {args.tolerance:.0e})", file=sys.stderr)
    for c in cases:
        n = c["native_rft"]
        print(f"  {c['family']:8} d={c['dimension']:2} params={c['parameter_count']:2} "
              f"closures={c['closure_count']:2}  median={n['median_seconds']*1e3:7.3f} ms  "
              f"pullback_work={n['pullback_work_elements']}", file=sys.stderr)
    return 0 if verdict == "ACCEPT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
