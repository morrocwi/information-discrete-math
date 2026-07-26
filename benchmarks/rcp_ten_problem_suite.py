#!/usr/bin/env python3
"""Ten preregistered retained-contraction problems plus four fail-closed controls.

The suite is designed to test protocol capability rather than one favorable
graph.  It spans chains, cycles, trees, ladders, a grid, a chordal graph, a
sparse skip graph, disconnected components, and a clique.  Every case:

* declares finite resolution, all terminal readouts, tolerance, and budgets;
* preflights the retained elimination path before arithmetic;
* returns the partition and every named axis first moment;
* is witnessed independently by opt_einsum;
* is additionally checked by full finite enumeration when d <= 8; and
* must produce an RCP ACCEPT certificate with matching planned/measured work.

Four negative controls confirm that malformed paths and budgets BLOCK while
missing or corrupted witnesses HOLD.  The suite is finite_diagnostic, not a
formal preservation theorem and not a statement about a physical continuum.
"""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import time
from dataclasses import asdict, dataclass
from typing import Callable, Iterable, Sequence

from benchmarks.coupled_nd_retained_compiler import (
    PairwiseProblem,
    direct_full_tensor,
    external_opt_einsum,
    min_fill_order,
    retained_factor_lineage,
)
from benchmarks.retained_reverse_compiler import (
    ReverseCompilerResult,
    compile_retained_reverse,
    plan_reverse_work,
)
from tools.idm_discipline import ACCEPT, BLOCK, HOLD
from tools.retained_contraction_protocol import (
    RCPDeclaration,
    certify_contraction,
    preflight_contraction,
)


SUITE_TOLERANCE = 1e-12
SUITE_MAX_WORK_TOKENS = 50_000_000
SUITE_MAX_PEAK_ELEMENTS = 1_000_000


@dataclass(frozen=True)
class ProblemSpec:
    name: str
    topology: str
    problem: PairwiseProblem


@dataclass(frozen=True)
class ProblemResult:
    name: str
    topology: str
    dimension: int
    edges: int
    nodes_per_axis: int
    terminal_readouts: int
    induced_width: int
    retained_factor_entries: int
    implicit_dense_elements: int
    dense_vs_retained_input_ratio: float
    planned_work_tokens: int
    measured_work_tokens: int
    peak_retained_elements: int
    opt_einsum_reported_flops: float
    opt_einsum_peak_elements: float
    rcp_wall_seconds_median: float
    opt_einsum_wall_seconds_median: float
    opt_einsum_over_rcp_time: float
    maximum_difference_vs_opt_einsum: float
    maximum_difference_vs_direct: float | None
    direct_witness_used: bool
    certificate_status: str


def _normalized_edges(
    edges: Iterable[tuple[int, int]],
) -> tuple[tuple[int, int], ...]:
    normalized = {
        (min(left, right), max(left, right))
        for left, right in edges
        if left != right
    }
    return tuple(sorted(normalized))


def _problem(
    dimension: int,
    edges: Iterable[tuple[int, int]],
) -> PairwiseProblem:
    normalized = _normalized_edges(edges)
    if any(left < 0 or right >= dimension for left, right in normalized):
        raise ValueError("edge outside declared dimensions")
    linear = tuple(
        0.11 + 0.013 * axis + 0.007 * ((3 * axis) % 5)
        for axis in range(dimension)
    )
    couplings = tuple(
        (
            left,
            right,
            0.025 + 0.006 * ((5 * edge_index + left + right) % 7),
        )
        for edge_index, (left, right) in enumerate(normalized)
    )
    return PairwiseProblem(dimension, linear, couplings)


def preregistered_problems() -> tuple[ProblemSpec, ...]:
    """Return the fixed suite; no topology is selected after seeing timings."""

    chain_4 = [(axis, axis + 1) for axis in range(3)]
    cycle_5 = [(axis, (axis + 1) % 5) for axis in range(5)]
    star_6 = [(0, leaf) for leaf in range(1, 6)]
    binary_tree_7 = [
        (0, 1),
        (0, 2),
        (1, 3),
        (1, 4),
        (2, 5),
        (2, 6),
    ]
    ladder_8 = (
        [(axis, axis + 1) for axis in range(3)]
        + [(axis, axis + 1) for axis in range(4, 7)]
        + [(axis, axis + 4) for axis in range(4)]
    )
    grid_3x3 = []
    for row in range(3):
        for column in range(3):
            node = 3 * row + column
            if column < 2:
                grid_3x3.append((node, node + 1))
            if row < 2:
                grid_3x3.append((node, node + 3))
    chordal_11 = (
        [(axis, axis + 1) for axis in range(10)]
        + [(axis, axis + 2) for axis in range(0, 9, 2)]
    )
    sparse_skip_12 = (
        [(axis, axis + 1) for axis in range(11)]
        + [(0, 3), (3, 6), (6, 9), (2, 8), (5, 11)]
    )
    disconnected_cycles_10 = (
        [(axis, axis + 1) for axis in range(4)]
        + [(4, 0)]
        + [(axis, axis + 1) for axis in range(5, 9)]
        + [(9, 5)]
    )
    clique_6 = [
        (left, right)
        for left in range(6)
        for right in range(left + 1, 6)
    ]

    return (
        ProblemSpec("P01_chain_4", "chain", _problem(4, chain_4)),
        ProblemSpec("P02_cycle_5", "cycle", _problem(5, cycle_5)),
        ProblemSpec("P03_star_6", "star", _problem(6, star_6)),
        ProblemSpec(
            "P04_binary_tree_7",
            "balanced_binary_tree",
            _problem(7, binary_tree_7),
        ),
        ProblemSpec("P05_ladder_8", "two_by_four_ladder", _problem(8, ladder_8)),
        ProblemSpec("P06_grid_9", "three_by_three_grid", _problem(9, grid_3x3)),
        ProblemSpec(
            "P07_chordal_11",
            "chain_with_length_two_chords",
            _problem(11, chordal_11),
        ),
        ProblemSpec(
            "P08_sparse_skip_12",
            "chain_with_long_skip_edges",
            _problem(12, sparse_skip_12),
        ),
        ProblemSpec(
            "P09_disconnected_10",
            "two_disconnected_five_cycles",
            _problem(10, disconnected_cycles_10),
        ),
        ProblemSpec("P10_clique_6", "complete_graph_adverse_case", _problem(6, clique_6)),
    )


def _median_call(function: Callable[[], object], repeats: int):
    samples: list[float] = []
    result = None
    for _ in range(repeats):
        started = time.perf_counter()
        result = function()
        samples.append(time.perf_counter() - started)
    return result, statistics.median(samples)


def _readout(result) -> tuple[float, ...]:
    return (result.value, *result.axis_first_moments)


def _maximum_difference(
    left: Sequence[float],
    right: Sequence[float],
) -> float:
    if len(left) != len(right):
        raise ValueError("readout boundaries differ")
    return max(
        (abs(left_value - right_value)
         for left_value, right_value in zip(left, right)),
        default=0.0,
    )


def _preflight(spec: ProblemSpec, order: int):
    problem = spec.problem
    reverse_plan = plan_reverse_work(problem, order)
    elimination_order, _width = min_fill_order(problem)
    declaration = RCPDeclaration(
        resolution_lambda=f"Gauss-Legendre nodes_per_axis={order}",
        tolerance=SUITE_TOLERANCE,
        axis_sizes=tuple(
            (axis, order) for axis in range(problem.dimension)
        ),
        boundary_axes=(),
        output_names=("partition",)
        + tuple(
            f"axis_{axis}_first_moment"
            for axis in range(problem.dimension)
        ),
        max_work_tokens=SUITE_MAX_WORK_TOKENS,
        max_peak_elements=SUITE_MAX_PEAK_ELEMENTS,
        query_strategy="one_forward_plus_reverse_lineage_all_moments",
    )
    forward = preflight_contraction(
        declaration,
        retained_factor_lineage(problem),
        elimination_order,
    )
    if forward.status != ACCEPT:
        return forward
    additional_work = (
        reverse_plan.total_work_tokens
        - forward.value.plan.work_tokens_per_execution
    )
    return preflight_contraction(
        declaration,
        retained_factor_lineage(problem),
        elimination_order,
        fixed_work_tokens=additional_work,
    )


def run_problem(
    spec: ProblemSpec,
    *,
    order: int,
    repeats: int,
    direct_dimension_limit: int,
) -> ProblemResult:
    problem = spec.problem
    preflight = _preflight(spec, order)
    if preflight.status != ACCEPT:
        raise RuntimeError(
            f"{spec.name} failed preregistered preflight: {preflight.reason}"
        )

    rcp, rcp_median = _median_call(
        lambda: compile_retained_reverse(problem, order),
        repeats,
    )
    external, external_median = _median_call(
        lambda: external_opt_einsum(problem, order),
        repeats,
    )
    assert isinstance(rcp, ReverseCompilerResult)
    rcp_readout = _readout(rcp)
    external_readout = _readout(external)
    certificate = certify_contraction(
        preflight,
        rcp_readout,
        external_readout,
        measured_work_tokens=rcp.total_work_tokens,
        measured_work_by_op={
            "factor_sample": rcp.factor_sample_tokens,
            "forward_multiply": rcp.forward_multiply_tokens,
            "forward_add": rcp.forward_add_tokens,
            "reverse_multiply": rcp.reverse_multiply_tokens,
            "reverse_add": rcp.reverse_add_tokens,
            "terminal_readout": rcp.readout_tokens,
        },
        witness_method="external opt_einsum contraction",
    )

    direct_difference = None
    use_direct = problem.dimension <= direct_dimension_limit
    if use_direct:
        direct = direct_full_tensor(problem, order)
        direct_difference = _maximum_difference(
            rcp_readout,
            _readout(direct),
        )
        if direct_difference > SUITE_TOLERANCE:
            raise AssertionError(
                f"{spec.name} direct witness differs by {direct_difference}"
            )

    if certificate.status != ACCEPT:
        raise AssertionError(
            f"{spec.name} certificate {certificate.status}: "
            f"{certificate.reason}"
        )
    _path, induced_width = min_fill_order(problem)
    dense_elements = order ** problem.dimension
    return ProblemResult(
        name=spec.name,
        topology=spec.topology,
        dimension=problem.dimension,
        edges=len(problem.couplings),
        nodes_per_axis=order,
        terminal_readouts=problem.dimension + 1,
        induced_width=induced_width,
        retained_factor_entries=rcp.factor_sample_tokens,
        implicit_dense_elements=dense_elements,
        dense_vs_retained_input_ratio=(
            dense_elements / rcp.factor_sample_tokens
        ),
        planned_work_tokens=preflight.value.planned_work_tokens,
        measured_work_tokens=rcp.total_work_tokens,
        peak_retained_elements=rcp.peak_retained_elements,
        opt_einsum_reported_flops=external.estimated_total_flops_all_outputs,
        opt_einsum_peak_elements=external.largest_intermediate_elements,
        rcp_wall_seconds_median=rcp_median,
        opt_einsum_wall_seconds_median=external_median,
        opt_einsum_over_rcp_time=external_median / rcp_median,
        maximum_difference_vs_opt_einsum=_maximum_difference(
            rcp_readout,
            external_readout,
        ),
        maximum_difference_vs_direct=direct_difference,
        direct_witness_used=use_direct,
        certificate_status=certificate.status,
    )


def run_fail_closed_controls(order: int = 4) -> dict[str, object]:
    spec = preregistered_problems()[0]
    problem = spec.problem
    accepted = _preflight(spec, order)
    if accepted.status != ACCEPT:
        raise AssertionError(accepted.reason)
    path = tuple(accepted.value.plan.elimination_order)
    declaration = accepted.value.declaration
    factors = retained_factor_lineage(problem)

    wrong_path = preflight_contraction(
        declaration,
        factors,
        path[:-1],
    )
    low_budget_declaration = RCPDeclaration(
        resolution_lambda=declaration.resolution_lambda,
        tolerance=declaration.tolerance,
        axis_sizes=declaration.axis_sizes,
        boundary_axes=declaration.boundary_axes,
        output_names=declaration.output_names,
        max_work_tokens=1,
        max_peak_elements=declaration.max_peak_elements,
        query_strategy=declaration.query_strategy,
    )
    low_budget = preflight_contraction(
        low_budget_declaration,
        factors,
        path,
    )

    result = compile_retained_reverse(problem, order)
    missing_witness = certify_contraction(
        accepted,
        _readout(result),
        None,
        measured_work_tokens=result.total_work_tokens,
        witness_method="",
    )
    corrupted = list(_readout(result))
    corrupted[0] += 1e-3
    corrupted_witness = certify_contraction(
        accepted,
        _readout(result),
        corrupted,
        measured_work_tokens=result.total_work_tokens,
        witness_method="deliberately corrupted control",
    )

    observed = {
        "wrong_path": wrong_path.status,
        "low_budget": low_budget.status,
        "missing_witness": missing_witness.status,
        "corrupted_witness": corrupted_witness.status,
    }
    expected = {
        "wrong_path": BLOCK,
        "low_budget": BLOCK,
        "missing_witness": HOLD,
        "corrupted_witness": HOLD,
    }
    return {
        "expected": expected,
        "observed": observed,
        "passed": observed == expected,
    }


def run_suite(
    *,
    order: int = 4,
    repeats: int = 3,
    direct_dimension_limit: int = 8,
) -> dict[str, object]:
    specs = preregistered_problems()
    results = [
        run_problem(
            spec,
            order=order,
            repeats=repeats,
            direct_dimension_limit=direct_dimension_limit,
        )
        for spec in specs
    ]
    controls = run_fail_closed_controls(order)
    accepted = sum(result.certificate_status == ACCEPT for result in results)
    faster = sum(result.opt_einsum_over_rcp_time > 1.0 for result in results)
    direct_witnesses = sum(result.direct_witness_used for result in results)
    maximum_external_difference = max(
        result.maximum_difference_vs_opt_einsum
        for result in results
    )
    direct_differences = [
        result.maximum_difference_vs_direct
        for result in results
        if result.maximum_difference_vs_direct is not None
    ]
    return {
        "suite": {
            "name": "RCP ten-problem topology suite",
            "problems_preregistered": len(specs),
            "nodes_per_axis": order,
            "repeats": repeats,
            "direct_dimension_limit": direct_dimension_limit,
            "declared_tolerance": SUITE_TOLERANCE,
            "max_work_tokens": SUITE_MAX_WORK_TOKENS,
            "max_peak_elements": SUITE_MAX_PEAK_ELEMENTS,
            "tier": "finite_diagnostic",
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "summary": {
            "accepted": accepted,
            "total": len(results),
            "rcp_faster_than_opt_einsum": faster,
            "direct_enumeration_witnesses": direct_witnesses,
            "maximum_difference_vs_opt_einsum": (
                maximum_external_difference
            ),
            "maximum_difference_vs_direct": max(
                direct_differences,
                default=0.0,
            ),
            "planned_equals_measured_all": all(
                result.planned_work_tokens == result.measured_work_tokens
                for result in results
            ),
            "controls_passed": bool(controls["passed"]),
        },
        "problems": [asdict(result) for result in results],
        "fail_closed_controls": controls,
        "claim_boundary": (
            "Ten finite pair-factor workloads demonstrate protocol breadth "
            "across fixed topologies. They do not prove universal superiority "
            "or a theorem about completed real numbers."
        ),
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nodes-per-axis", type=int, default=4)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--direct-dimension-limit", type=int, default=8)
    args = parser.parse_args(argv)
    report = run_suite(
        order=args.nodes_per_axis,
        repeats=args.repeats,
        direct_dimension_limit=args.direct_dimension_limit,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    summary = report["summary"]
    return 0 if (
        summary["accepted"] == summary["total"] == 10
        and summary["planned_equals_measured_all"]
        and summary["controls_passed"]
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
