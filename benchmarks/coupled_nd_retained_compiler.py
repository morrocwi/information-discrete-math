#!/usr/bin/env python3
"""Automatic retained-graph contraction for a genuinely coupled N-D integral.

The benchmark discretizes

    integral_[0,1]^d exp(-sum_i a_i*x_i - sum_(i,j) b_ij*x_i*x_j) dx

with a Gauss-Legendre rule on every named axis. Pair terms make the integrand
non-separable. The direct path visits all n**d coordinate tuples. The retained
path reads the coupling graph, chooses a min-fill elimination order, contracts
the discrete factors, and returns the partition readout plus a first-moment
readout for every axis.

This is a finite factor-graph compiler prototype. Its certificate reports the
elimination order, induced width, table-sample tokens, arithmetic tokens, and
agreement with direct full-tensor enumeration.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import platform
from pathlib import Path
import sys
import time
from dataclasses import asdict, dataclass, replace
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from benchmarks.direct_nd_work_tokens import quadrature_rule
except ModuleNotFoundError:  # direct script execution: benchmarks/ is sys.path[0]
    from direct_nd_work_tokens import quadrature_rule

from tools.idm_discipline import ACCEPT
from tools.retained_contraction_protocol import (
    RCPDeclaration,
    RetainedFactor,
    certify_contraction,
    preflight_contraction,
    verdict_report,
)


@dataclass(frozen=True)
class PairwiseProblem:
    dimension: int
    linear: tuple[float, ...]
    couplings: tuple[tuple[int, int, float], ...]


@dataclass(frozen=True)
class Factor:
    scope: tuple[int, ...]
    values: dict[tuple[int, ...], float]


@dataclass
class WorkCounter:
    factor_sample_tokens: int = 0
    multiply_tokens: int = 0
    add_tokens: int = 0

    @property
    def total_work_tokens(self) -> int:
        return self.factor_sample_tokens + self.multiply_tokens + self.add_tokens

    def absorb(self, other: "WorkCounter") -> None:
        self.factor_sample_tokens += other.factor_sample_tokens
        self.multiply_tokens += other.multiply_tokens
        self.add_tokens += other.add_tokens


@dataclass(frozen=True)
class DirectResult:
    value: float
    axis_first_moments: list[float]
    configuration_sample_tokens: int
    multiply_tokens: int
    add_tokens: int
    total_work_tokens: int
    elapsed_seconds: float


@dataclass(frozen=True)
class CompilerResult:
    value: float
    axis_first_moments: list[float]
    elimination_order: list[int]
    induced_width: int
    factor_sample_tokens: int
    multiply_tokens: int
    add_tokens: int
    total_work_tokens: int
    elapsed_seconds: float


@dataclass(frozen=True)
class ExternalTensorResult:
    method: str
    value: float
    axis_first_moments: list[float]
    path_search_seconds: float
    execution_seconds: float
    optimized_flops_per_contraction: float
    estimated_total_flops_all_outputs: float
    largest_intermediate_elements: float


def default_problem(dimension: int = 11) -> PairwiseProblem:
    """A deterministic sparse graph with real pair coupling and width > 1."""
    if dimension < 3:
        raise ValueError("dimension must be at least 3")
    linear = tuple(0.15 + 0.03 * axis for axis in range(dimension))
    chain = [(axis, axis + 1) for axis in range(dimension - 1)]
    chords = [(axis, axis + 2) for axis in range(0, dimension - 2, 2)]
    edges = chain + chords
    couplings = tuple(
        (left, right, 0.04 + 0.01 * (edge_index % 5))
        for edge_index, (left, right) in enumerate(edges)
    )
    return PairwiseProblem(dimension, linear, couplings)


def _adjacency(problem: PairwiseProblem) -> dict[int, set[int]]:
    graph = {axis: set() for axis in range(problem.dimension)}
    for left, right, _strength in problem.couplings:
        if left == right:
            raise ValueError("self-couplings are not supported")
        graph[left].add(right)
        graph[right].add(left)
    return graph


def min_fill_order(problem: PairwiseProblem) -> tuple[list[int], int]:
    """Choose a deterministic min-fill order and report induced width."""
    graph = _adjacency(problem)
    remaining = set(graph)
    order: list[int] = []
    induced_width = 0

    while remaining:
        def score(axis: int) -> tuple[int, int, int]:
            neighbors = sorted(graph[axis] & remaining)
            missing = sum(
                1
                for index, left in enumerate(neighbors)
                for right in neighbors[index + 1 :]
                if right not in graph[left]
            )
            return missing, len(neighbors), axis

        axis = min(remaining, key=score)
        neighbors = sorted(graph[axis] & remaining)
        induced_width = max(induced_width, len(neighbors))
        for index, left in enumerate(neighbors):
            for right in neighbors[index + 1 :]:
                graph[left].add(right)
                graph[right].add(left)
        remaining.remove(axis)
        order.append(axis)

    return order, induced_width


def build_factors(
    problem: PairwiseProblem,
    order: int,
) -> tuple[list[Factor], tuple[float, ...], WorkCounter]:
    nodes, weights = quadrature_rule(order)
    factors: list[Factor] = []
    counter = WorkCounter()

    for axis, coefficient in enumerate(problem.linear):
        values = {
            (node_index,): weights[node_index] * math.exp(-coefficient * node)
            for node_index, node in enumerate(nodes)
        }
        factors.append(Factor((axis,), values))
        counter.factor_sample_tokens += len(nodes)

    for left, right, strength in problem.couplings:
        values = {
            (left_index, right_index): math.exp(
                -strength * nodes[left_index] * nodes[right_index]
            )
            for left_index in range(len(nodes))
            for right_index in range(len(nodes))
        }
        factors.append(Factor((left, right), values))
        counter.factor_sample_tokens += len(nodes) ** 2

    return factors, nodes, counter


def _factor_value(factor: Factor, assignment: dict[int, int]) -> float:
    return factor.values[tuple(assignment[axis] for axis in factor.scope)]


def contract(
    factors: list[Factor],
    elimination_order: list[int],
    node_count: int,
) -> tuple[float, WorkCounter]:
    active = list(factors)
    counter = WorkCounter()

    for axis in elimination_order:
        bucket = [factor for factor in active if axis in factor.scope]
        active = [factor for factor in active if axis not in factor.scope]
        if not bucket:
            continue

        joined_scope = sorted({item for factor in bucket for item in factor.scope})
        output_scope = tuple(item for item in joined_scope if item != axis)
        output_values: dict[tuple[int, ...], float] = {}

        for output_indices in itertools.product(range(node_count), repeat=len(output_scope)):
            assignment = dict(zip(output_scope, output_indices))
            total = 0.0
            compensation = 0.0
            for eliminated_index in range(node_count):
                assignment[axis] = eliminated_index
                product = 1.0
                for factor in bucket:
                    product *= _factor_value(factor, assignment)
                    counter.multiply_tokens += 1

                corrected = product - compensation
                updated = total + corrected
                compensation = (updated - total) - corrected
                total = updated
                counter.add_tokens += 1

            output_values[output_indices] = total

        active.append(Factor(output_scope, output_values))

    result = 1.0
    for factor in active:
        if factor.scope:
            raise AssertionError(f"uneliminated scope: {factor.scope}")
        result *= factor.values[()]
        counter.multiply_tokens += 1
    return result, counter


def _moment_factors(
    factors: list[Factor],
    axis: int,
    nodes: tuple[float, ...],
    counter: WorkCounter,
) -> list[Factor]:
    changed: list[Factor] = []
    replaced = False
    for factor in factors:
        if factor.scope == (axis,) and not replaced:
            values = {
                key: value * nodes[key[0]]
                for key, value in factor.values.items()
            }
            counter.multiply_tokens += len(values)
            changed.append(Factor(factor.scope, values))
            replaced = True
        else:
            changed.append(factor)
    if not replaced:
        raise AssertionError(f"missing unary factor for axis {axis}")
    return changed


def compile_retained(problem: PairwiseProblem, order: int) -> CompilerResult:
    started = time.perf_counter()
    factors, nodes, total_counter = build_factors(problem, order)
    elimination_order, induced_width = min_fill_order(problem)

    partition, partition_counter = contract(
        factors,
        elimination_order,
        len(nodes),
    )
    total_counter.absorb(partition_counter)

    moments: list[float] = []
    for axis in range(problem.dimension):
        moment_counter = WorkCounter()
        numerator_factors = _moment_factors(factors, axis, nodes, moment_counter)
        numerator, contraction_counter = contract(
            numerator_factors,
            elimination_order,
            len(nodes),
        )
        moment_counter.absorb(contraction_counter)
        total_counter.absorb(moment_counter)
        moments.append(numerator / partition)
        total_counter.multiply_tokens += 1  # division/combine token

    elapsed = time.perf_counter() - started
    return CompilerResult(
        value=partition,
        axis_first_moments=moments,
        elimination_order=elimination_order,
        induced_width=induced_width,
        factor_sample_tokens=total_counter.factor_sample_tokens,
        multiply_tokens=total_counter.multiply_tokens,
        add_tokens=total_counter.add_tokens,
        total_work_tokens=total_counter.total_work_tokens,
        elapsed_seconds=elapsed,
    )


def external_opt_einsum(problem: PairwiseProblem, order: int) -> ExternalTensorResult:
    """External tensor-network baseline with automatic contraction ordering."""
    try:
        import numpy as np
        import opt_einsum as oe
    except ImportError as exc:  # pragma: no cover - optional benchmark
        raise RuntimeError("NumPy and opt_einsum are required") from exc

    factors, nodes, _counter = build_factors(problem, order)
    arrays = []
    labels = []
    unary_positions: dict[int, int] = {}
    for factor in factors:
        shape = (len(nodes),) * len(factor.scope)
        array = np.empty(shape, dtype=float)
        for key, value in factor.values.items():
            array[key] = value
        if len(factor.scope) == 1:
            unary_positions[factor.scope[0]] = len(arrays)
        arrays.append(array)
        labels.append(list(factor.scope))

    def operands(current_arrays):
        interleaved = []
        for array, label in zip(current_arrays, labels):
            interleaved.extend((array, label))
        interleaved.append([])
        return interleaved

    path_started = time.perf_counter()
    path, info = oe.contract_path(*operands(arrays), optimize="greedy")
    path_seconds = time.perf_counter() - path_started

    execution_started = time.perf_counter()
    partition = float(oe.contract(*operands(arrays), optimize=path))
    moments: list[float] = []
    node_array = np.asarray(nodes)
    for axis in range(problem.dimension):
        changed = list(arrays)
        unary_position = unary_positions[axis]
        changed[unary_position] = changed[unary_position] * node_array
        numerator = float(oe.contract(*operands(changed), optimize=path))
        moments.append(numerator / partition)
    execution_seconds = time.perf_counter() - execution_started

    outputs = problem.dimension + 1
    return ExternalTensorResult(
        method="opt_einsum_greedy_reused_path",
        value=partition,
        axis_first_moments=moments,
        path_search_seconds=path_seconds,
        execution_seconds=execution_seconds,
        optimized_flops_per_contraction=float(info.opt_cost),
        estimated_total_flops_all_outputs=float(info.opt_cost) * outputs,
        largest_intermediate_elements=float(info.largest_intermediate),
    )


def _kahan_update(total: float, compensation: float, value: float) -> tuple[float, float]:
    corrected = value - compensation
    updated = total + corrected
    return updated, (updated - total) - corrected


def direct_full_tensor(problem: PairwiseProblem, order: int) -> DirectResult:
    """Enumerate every N-D tuple and retain all axis first moments."""
    factors, nodes, _build_counter = build_factors(problem, order)
    node_count = len(nodes)
    configurations = node_count ** problem.dimension
    started = time.perf_counter()
    partition = 0.0
    partition_compensation = 0.0
    moment_totals = [0.0] * problem.dimension
    moment_compensations = [0.0] * problem.dimension

    for indices in itertools.product(range(node_count), repeat=problem.dimension):
        assignment = dict(enumerate(indices))
        term = 1.0
        for factor in factors:
            term *= _factor_value(factor, assignment)
        partition, partition_compensation = _kahan_update(
            partition,
            partition_compensation,
            term,
        )

        for axis, node_index in enumerate(indices):
            weighted_coordinate = term * nodes[node_index]
            moment_totals[axis], moment_compensations[axis] = _kahan_update(
                moment_totals[axis],
                moment_compensations[axis],
                weighted_coordinate,
            )

    moments = [total / partition for total in moment_totals]
    elapsed = time.perf_counter() - started
    factor_count = len(factors)
    multiply_tokens = configurations * factor_count
    multiply_tokens += configurations * problem.dimension
    multiply_tokens += problem.dimension  # final moment divisions
    add_tokens = configurations
    add_tokens += configurations * problem.dimension
    total_work = configurations + multiply_tokens + add_tokens
    return DirectResult(
        value=partition,
        axis_first_moments=moments,
        configuration_sample_tokens=configurations,
        multiply_tokens=multiply_tokens,
        add_tokens=add_tokens,
        total_work_tokens=total_work,
        elapsed_seconds=elapsed,
    )


def retained_factor_lineage(problem: PairwiseProblem) -> tuple[RetainedFactor, ...]:
    """Translate the problem to named finite retained couplings."""
    unary = tuple(
        RetainedFactor(name=f"axis_{axis}", scope=(axis,))
        for axis in range(problem.dimension)
    )
    pairwise = tuple(
        RetainedFactor(
            name=f"coupling_{edge_index}_{left}_{right}",
            scope=(left, right),
        )
        for edge_index, (left, right, _strength) in enumerate(problem.couplings)
    )
    return unary + pairwise


def rcp_preflight(
    problem: PairwiseProblem,
    order: int,
    *,
    tolerance: float,
    max_work_tokens: int,
    max_peak_elements: int,
):
    """Declare and preflight all scalar readouts before executing contraction."""
    elimination_order, _induced_width = min_fill_order(problem)
    output_names = ("partition",) + tuple(
        f"axis_{axis}_first_moment" for axis in range(problem.dimension)
    )
    declaration = RCPDeclaration(
        resolution_lambda=f"Gauss-Legendre nodes_per_axis={order}",
        tolerance=tolerance,
        axis_sizes=tuple(
            (axis, order) for axis in range(problem.dimension)
        ),
        boundary_axes=(),
        output_names=output_names,
        max_work_tokens=max_work_tokens,
        max_peak_elements=max_peak_elements,
    )
    factor_sample_tokens = (
        problem.dimension * order
        + len(problem.couplings) * order**2
    )
    # Each moment multiplies one unary table by its coordinate nodes and
    # performs one final numerator/partition division.
    output_setup_tokens = problem.dimension * (order + 1)
    return preflight_contraction(
        declaration,
        retained_factor_lineage(problem),
        elimination_order,
        executions=problem.dimension + 1,
        fixed_work_tokens=factor_sample_tokens + output_setup_tokens,
    )


def run_benchmark(
    dimension: int,
    order: int,
    with_opt_einsum: bool = False,
    *,
    rcp_tolerance: float = 1e-12,
    rcp_max_work_tokens: int = 1_000_000,
    rcp_max_peak_elements: int = 1_000_000,
) -> dict[str, object]:
    problem = default_problem(dimension)
    preflight = rcp_preflight(
        problem,
        order,
        tolerance=rcp_tolerance,
        max_work_tokens=rcp_max_work_tokens,
        max_peak_elements=rcp_max_peak_elements,
    )
    if preflight.status != ACCEPT:
        return {
            "problem": {
                "dimension": dimension,
                "nodes_per_axis": order,
                "linear_coefficients": list(problem.linear),
                "couplings": [list(edge) for edge in problem.couplings],
                "separable": False,
            },
            "rcp_preflight": verdict_report(preflight),
            "execution_skipped": True,
        }

    compiled = compile_retained(problem, order)
    direct = direct_full_tensor(problem, order)
    rcp_certificate = certify_contraction(
        preflight,
        (compiled.value, *compiled.axis_first_moments),
        (direct.value, *direct.axis_first_moments),
        measured_work_tokens=compiled.total_work_tokens,
        witness_method="independent direct finite full-tensor enumeration",
    )
    axis_differences = [
        abs(left - right)
        for left, right in zip(direct.axis_first_moments, compiled.axis_first_moments)
    ]
    report: dict[str, object] = {
        "problem": {
            "dimension": dimension,
            "nodes_per_axis": order,
            "linear_coefficients": list(problem.linear),
            "couplings": [list(edge) for edge in problem.couplings],
            "separable": False,
        },
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "direct_full_tensor": asdict(direct),
        "retained_graph_compiler": asdict(compiled),
        "retained_contraction_protocol": verdict_report(rcp_certificate),
        "agreement": {
            "partition_absolute_difference": abs(direct.value - compiled.value),
            "maximum_axis_moment_difference": max(axis_differences),
            "all_11_axis_moment_differences": axis_differences,
        },
        "ratios": {
            "configuration_vs_factor_sample_tokens": (
                direct.configuration_sample_tokens / compiled.factor_sample_tokens
            ),
            "direct_vs_compiler_total_work_tokens": (
                direct.total_work_tokens / compiled.total_work_tokens
            ),
            "direct_vs_compiler_elapsed": (
                direct.elapsed_seconds
                / max(compiled.elapsed_seconds, sys.float_info.min)
            ),
        },
        "certificate": {
            "identity_checked_against_full_tensor": True,
            "all_axis_readouts_returned": len(compiled.axis_first_moments) == dimension,
            "compression_available_because": (
                "sparse retained pair-coupling graph with bounded induced width"
            ),
        },
    }
    if with_opt_einsum:
        external = external_opt_einsum(problem, order)
        report["external_opt_einsum"] = asdict(external)
        report["external_agreement"] = {
            "partition_difference_vs_compiler": abs(external.value - compiled.value),
            "maximum_axis_difference_vs_compiler": max(
                abs(left - right)
                for left, right in zip(
                    external.axis_first_moments,
                    compiled.axis_first_moments,
                )
            ),
        }
        report["external_source"] = "https://dgasmith.github.io/opt_einsum/"
    return report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dimension", type=int, default=11)
    parser.add_argument("--nodes-per-axis", type=int, choices=(4, 5), default=4)
    parser.add_argument("--opt-einsum", action="store_true")
    parser.add_argument("--rcp-tolerance", type=float, default=1e-12)
    parser.add_argument("--rcp-max-work-tokens", type=int, default=1_000_000)
    parser.add_argument("--rcp-max-peak-elements", type=int, default=1_000_000)
    args = parser.parse_args(argv)

    report = run_benchmark(
        args.dimension,
        args.nodes_per_axis,
        with_opt_einsum=args.opt_einsum,
        rcp_tolerance=args.rcp_tolerance,
        rcp_max_work_tokens=args.rcp_max_work_tokens,
        rcp_max_peak_elements=args.rcp_max_peak_elements,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if report.get("execution_skipped"):
        return 2
    agreement = report["agreement"]
    assert isinstance(agreement, dict)
    protocol = report["retained_contraction_protocol"]
    assert isinstance(protocol, dict)
    return 0 if (
        float(agreement["partition_absolute_difference"]) <= 1e-12
        and float(agreement["maximum_axis_moment_difference"]) <= 1e-12
        and protocol["status"] == ACCEPT
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
