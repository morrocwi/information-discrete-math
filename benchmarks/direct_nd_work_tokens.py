#!/usr/bin/env python3
"""Direct N-D work-token benchmark with no radial reduction.

Problem
-------
    I_d = integral_[0,1]^d exp(-(x_1 + ... + x_d)) dx_1 ... dx_d

Two computations use the same Gauss-Legendre rule on every axis:

1. ``direct_tensor`` visits every one of the n**d N-D grid points.  Every
   integrand call receives all d coordinates.
2. ``axis_preserving`` computes a readout for each of the d named axes and
   combines those d readouts using the exact separable structure
   exp(-sum(x_j)) = product(exp(-x_j)).

The second path does not use a radial coordinate and does not merge the axes
into one anonymous dimension: it returns all d axis readouts.  It does exploit
separability, so this benchmark is a structural-compression benchmark, not a
claim that every arbitrary N-D integrand admits the same reduction.

A work token is one weighted kernel sample.  Combination multiplications are
reported separately and also included in ``total_work_tokens``.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import platform
import sys
import time
from dataclasses import asdict, dataclass
from typing import Callable, Iterable


_RAW_RULES = {
    4: (
        (
            -0.8611363115940525752,
            -0.3399810435848562648,
            0.3399810435848562648,
            0.8611363115940525752,
        ),
        (
            0.3478548451374538574,
            0.6521451548625461426,
            0.6521451548625461426,
            0.3478548451374538574,
        ),
    ),
    5: (
        (
            -0.9061798459386639928,
            -0.5384693101056830910,
            0.0,
            0.5384693101056830910,
            0.9061798459386639928,
        ),
        (
            0.2369268850561890875,
            0.4786286704993664680,
            0.5688888888888888889,
            0.4786286704993664680,
            0.2369268850561890875,
        ),
    ),
}


def quadrature_rule(order: int) -> tuple[tuple[float, ...], tuple[float, ...]]:
    try:
        raw_nodes, raw_weights = _RAW_RULES[order]
    except KeyError as exc:
        raise ValueError(f"unsupported Gauss-Legendre order: {order}") from exc
    nodes = tuple((x + 1.0) / 2.0 for x in raw_nodes)
    weights = tuple(w / 2.0 for w in raw_weights)
    return nodes, weights


@dataclass(frozen=True)
class Run:
    method: str
    dimension: int
    value: float
    axis_readouts: list[float]
    sample_tokens: int
    combine_tokens: int
    total_work_tokens: int
    elapsed_seconds: float
    absolute_error_vs_analytic: float


def _kahan_add(total: float, compensation: float, value: float) -> tuple[float, float]:
    corrected = value - compensation
    updated = total + corrected
    return updated, (updated - total) - corrected


def direct_tensor(dimension: int, order: int = 5) -> Run:
    """Visit the complete order**dimension tensor grid."""
    if dimension < 1:
        raise ValueError("dimension must be positive")
    nodes, weights = quadrature_rule(order)

    started = time.perf_counter()
    total = 0.0
    compensation = 0.0
    sample_tokens = 0

    for indices in itertools.product(range(len(nodes)), repeat=dimension):
        coordinate_sum = 0.0
        weight_product = 1.0
        for index in indices:
            coordinate_sum += nodes[index]
            weight_product *= weights[index]
        weighted_sample = weight_product * math.exp(-coordinate_sum)
        total, compensation = _kahan_add(total, compensation, weighted_sample)
        sample_tokens += 1

    elapsed = time.perf_counter() - started
    analytic = (1.0 - math.exp(-1.0)) ** dimension
    return Run(
        method="direct_tensor",
        dimension=dimension,
        value=total,
        axis_readouts=[],
        sample_tokens=sample_tokens,
        combine_tokens=0,
        total_work_tokens=sample_tokens,
        elapsed_seconds=elapsed,
        absolute_error_vs_analytic=abs(total - analytic),
    )


def axis_preserving(dimension: int, order: int = 5) -> Run:
    """Compute and retain one finite readout for every named axis."""
    if dimension < 1:
        raise ValueError("dimension must be positive")
    nodes, weights = quadrature_rule(order)

    started = time.perf_counter()
    axis_readouts: list[float] = []
    sample_tokens = 0

    # Recompute every axis independently even though this symmetric test gives
    # identical values.  This deliberately preserves all d dimension readouts.
    for _axis in range(dimension):
        axis_value = 0.0
        for node, weight in zip(nodes, weights):
            axis_value += weight * math.exp(-node)
            sample_tokens += 1
        axis_readouts.append(axis_value)

    total = 1.0
    for axis_value in axis_readouts:
        total *= axis_value
    combine_tokens = max(0, dimension - 1)

    elapsed = time.perf_counter() - started
    analytic = (1.0 - math.exp(-1.0)) ** dimension
    return Run(
        method="axis_preserving",
        dimension=dimension,
        value=total,
        axis_readouts=axis_readouts,
        sample_tokens=sample_tokens,
        combine_tokens=combine_tokens,
        total_work_tokens=sample_tokens + combine_tokens,
        elapsed_seconds=elapsed,
        absolute_error_vs_analytic=abs(total - analytic),
    )


def scipy_nquad(dimension: int, eps: float) -> Run:
    """External adaptive baseline; requires SciPy.

    SciPy documents ``neval`` as the number of integrand evaluations returned
    by ``nquad(..., full_output=True)``.  We use that value as sample tokens.
    """
    try:
        from scipy.integrate import nquad
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("SciPy is required for --scipy-dimension") from exc

    calls = 0

    def integrand(*coordinates: float) -> float:
        nonlocal calls
        calls += 1
        return math.exp(-sum(coordinates))

    started = time.perf_counter()
    value, _reported_error, info = nquad(
        integrand,
        [(0.0, 1.0)] * dimension,
        opts={"epsabs": eps, "epsrel": eps},
        full_output=True,
    )
    elapsed = time.perf_counter() - started
    neval = int(info["neval"])
    if calls != neval:
        raise AssertionError(f"local call count {calls} != SciPy neval {neval}")

    analytic = (1.0 - math.exp(-1.0)) ** dimension
    return Run(
        method="scipy_nquad",
        dimension=dimension,
        value=value,
        axis_readouts=[],
        sample_tokens=neval,
        combine_tokens=0,
        total_work_tokens=neval,
        elapsed_seconds=elapsed,
        absolute_error_vs_analytic=abs(value - analytic),
    )


def _record(run: Run) -> dict[str, object]:
    return asdict(run)


def _ratios(baseline: Run, ours: Run) -> dict[str, float]:
    return {
        "sample_token_ratio": baseline.sample_tokens / ours.sample_tokens,
        "total_work_token_ratio": baseline.total_work_tokens / ours.total_work_tokens,
        "elapsed_ratio": baseline.elapsed_seconds / max(ours.elapsed_seconds, sys.float_info.min),
        "absolute_difference": abs(baseline.value - ours.value),
    }


def run_benchmark(
    dimension: int,
    order: int,
    scipy_dimension: int | None,
    eps: float,
) -> dict[str, object]:
    ours = axis_preserving(dimension, order)
    direct = direct_tensor(dimension, order)
    report: dict[str, object] = {
        "problem": "integral_[0,1]^d exp(-(x1+...+xd)) dx1...dxd",
        "quadrature": f"{order}-point Gauss-Legendre on every axis",
        "work_token_definition": "one weighted kernel sample; combination multiplies reported separately",
        "requested_absolute_tolerance": eps,
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "direct_nd": _record(direct),
        "idm_axis_preserving_nd": _record(ours),
        "direct_vs_idm": _ratios(direct, ours),
    }

    if scipy_dimension is not None:
        scipy_run = scipy_nquad(scipy_dimension, eps)
        scipy_ours = axis_preserving(scipy_dimension, order)
        report["scipy_external"] = _record(scipy_run)
        report["idm_axis_preserving_for_scipy_dimension"] = _record(scipy_ours)
        report["scipy_vs_idm"] = _ratios(scipy_run, scipy_ours)
        report["scipy_documentation"] = (
            "https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.nquad.html"
        )

    return report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dimension", type=int, default=11)
    parser.add_argument("--nodes-per-axis", type=int, choices=sorted(_RAW_RULES), default=5)
    parser.add_argument("--scipy-dimension", type=int)
    parser.add_argument("--eps", type=float, default=1e-10)
    args = parser.parse_args(argv)

    report = run_benchmark(args.dimension, args.nodes_per_axis, args.scipy_dimension, args.eps)
    print(json.dumps(report, indent=2, sort_keys=True))

    direct = report["direct_nd"]
    ours = report["idm_axis_preserving_nd"]
    assert isinstance(direct, dict) and isinstance(ours, dict)
    difference = abs(float(direct["value"]) - float(ours["value"]))
    return 0 if difference <= 1e-12 else 1


if __name__ == "__main__":
    raise SystemExit(main())
