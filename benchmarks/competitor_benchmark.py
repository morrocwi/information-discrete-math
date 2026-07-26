#!/usr/bin/env python3
"""Real 11-D comparison: RCP vs opt_einsum, TT-SVD, and two TT-cross APIs.

The default problem is the same sparse, coupled, non-separable finite tensor
used by ``coupled_nd_retained_compiler.py``.  Every method returns the
partition and all named axis first moments.

Two input regimes are reported separately:

* structured: RCP and opt_einsum receive the explicit local factor graph;
* tensor/black-box: TT-SVD receives a dense tensor, TensorLy TT-cross receives
  the dense API required by that implementation, and TTML DMRG-cross samples a
  callable without dense materialization.

No result from one input regime is silently presented as universal dominance.
"""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import time
from dataclasses import asdict, dataclass
from importlib.metadata import PackageNotFoundError, version
from typing import Callable, Iterable, Sequence

import numpy as np

from benchmarks.coupled_nd_retained_compiler import (
    default_problem,
    external_opt_einsum,
    min_fill_order,
    quadrature_rule,
    retained_factor_lineage,
)
from benchmarks.retained_reverse_compiler import (
    ReverseCompilerResult,
    compile_retained_reverse,
    plan_reverse_work,
)
from tools.idm_discipline import ACCEPT
from tools.retained_contraction_protocol import (
    RCPDeclaration,
    certify_contraction,
    preflight_contraction,
    verdict_report,
)


@dataclass(frozen=True)
class TensorBaselineResult:
    method: str
    package: str
    package_version: str
    value: float
    axis_first_moments: list[float]
    input_regime: str
    materialized_input_elements: int
    function_evaluations: int
    unique_function_evaluations: int
    representation_elements: int
    build_seconds: float
    decompose_seconds: float
    readout_seconds: float
    total_seconds: float
    maximum_difference_vs_rcp: float


def _package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "unknown"


def _median_run(function: Callable[[], object], repeats: int):
    times: list[float] = []
    result = None
    for _ in range(repeats):
        started = time.perf_counter()
        result = function()
        times.append(time.perf_counter() - started)
    return result, statistics.median(times), times


def _dense_weighted_tensor(problem, order: int):
    nodes, weights = quadrature_rule(order)
    node_array = np.asarray(nodes)
    weight_array = np.asarray(weights)
    shape = (order,) * problem.dimension
    tensor = np.ones(shape, dtype=float)

    for axis, coefficient in enumerate(problem.linear):
        unary = weight_array * np.exp(-coefficient * node_array)
        view = [1] * problem.dimension
        view[axis] = order
        tensor *= unary.reshape(view)
    for left, right, strength in problem.couplings:
        pair = np.exp(
            -strength
            * node_array[:, np.newaxis]
            * node_array[np.newaxis, :]
        )
        view = [1] * problem.dimension
        view[left] = order
        view[right] = order
        tensor *= pair.reshape(view)
    return tensor, node_array


def _tt_readouts(
    cores: Sequence[np.ndarray],
    nodes: np.ndarray,
) -> tuple[float, list[float]]:
    core_arrays = [np.asarray(core) for core in cores]
    transfers = [core.sum(axis=1) for core in core_arrays]
    terminal = np.asarray([[1.0]])
    for transfer in transfers:
        terminal = terminal @ transfer
    partition = float(terminal[0, 0])

    moments: list[float] = []
    for target_axis in range(len(core_arrays)):
        terminal = np.asarray([[1.0]])
        for axis, core in enumerate(core_arrays):
            transfer = (
                np.einsum("aib,i->ab", core, nodes)
                if axis == target_axis
                else transfers[axis]
            )
            terminal = terminal @ transfer
        moments.append(float(terminal[0, 0]) / partition)
    return partition, moments


def _maximum_output_difference(
    value: float,
    moments: Sequence[float],
    rcp: ReverseCompilerResult,
) -> float:
    return max(
        [abs(value - rcp.value)]
        + [
            abs(left - right)
            for left, right in zip(moments, rcp.axis_first_moments)
        ]
    )


def _adaptive_tt_ranks(
    dimension: int,
    order: int,
    maximum_rank: int,
) -> list[int]:
    return [1] + [
        min(maximum_rank, order ** min(cut, dimension - cut))
        for cut in range(1, dimension)
    ] + [1]


def tensorly_tt_svd(problem, order: int, rank: int, rcp):
    from tensorly.decomposition import tensor_train

    build_started = time.perf_counter()
    tensor, nodes = _dense_weighted_tensor(problem, order)
    build_seconds = time.perf_counter() - build_started
    ranks = _adaptive_tt_ranks(problem.dimension, order, rank)

    decomposition_started = time.perf_counter()
    cores = tensor_train(tensor, ranks)
    decomposition_seconds = time.perf_counter() - decomposition_started
    readout_started = time.perf_counter()
    value, moments = _tt_readouts(cores, nodes)
    readout_seconds = time.perf_counter() - readout_started
    return TensorBaselineResult(
        method="Oseledets_TT-SVD",
        package="tensorly",
        package_version=_package_version("tensorly"),
        value=value,
        axis_first_moments=moments,
        input_regime="dense_tensor",
        materialized_input_elements=int(tensor.size),
        function_evaluations=0,
        unique_function_evaluations=0,
        representation_elements=int(
            sum(np.asarray(core).size for core in cores)
        ),
        build_seconds=build_seconds,
        decompose_seconds=decomposition_seconds,
        readout_seconds=readout_seconds,
        total_seconds=build_seconds + decomposition_seconds + readout_seconds,
        maximum_difference_vs_rcp=_maximum_output_difference(
            value,
            moments,
            rcp,
        ),
    )


def tensorly_tt_cross(problem, order: int, rank: int, rcp):
    from tensorly.contrib.decomposition import tensor_train_cross

    build_started = time.perf_counter()
    tensor, nodes = _dense_weighted_tensor(problem, order)
    build_seconds = time.perf_counter() - build_started
    ranks = _adaptive_tt_ranks(problem.dimension, order, rank)

    decomposition_started = time.perf_counter()
    cores = tensor_train_cross(
        tensor,
        ranks,
        tol=1e-10,
        n_iter_max=20,
        random_state=0,
    )
    decomposition_seconds = time.perf_counter() - decomposition_started
    readout_started = time.perf_counter()
    value, moments = _tt_readouts(cores, nodes)
    readout_seconds = time.perf_counter() - readout_started
    return TensorBaselineResult(
        method="TensorLy_TT-cross",
        package="tensorly",
        package_version=_package_version("tensorly"),
        value=value,
        axis_first_moments=moments,
        input_regime="dense_tensor_api",
        materialized_input_elements=int(tensor.size),
        function_evaluations=0,
        unique_function_evaluations=0,
        representation_elements=int(
            sum(np.asarray(core).size for core in cores)
        ),
        build_seconds=build_seconds,
        decompose_seconds=decomposition_seconds,
        readout_seconds=readout_seconds,
        total_seconds=build_seconds + decomposition_seconds + readout_seconds,
        maximum_difference_vs_rcp=_maximum_output_difference(
            value,
            moments,
            rcp,
        ),
    )


class _CountedTensorFunction:
    def __init__(self, problem, nodes: np.ndarray, weights: np.ndarray):
        self.problem = problem
        self.nodes = nodes
        self.weights = weights
        self.evaluations = 0
        self.unique_indices: set[tuple[int, ...]] = set()

    def __call__(self, indices):
        indices = np.asarray(indices, dtype=int)
        output_shape = indices.shape[:-1]
        rows = indices.reshape(-1, self.problem.dimension)
        self.evaluations += len(rows)
        self.unique_indices.update(map(tuple, rows.tolist()))
        coordinates = self.nodes[rows]
        values = np.prod(self.weights[rows], axis=1)
        values *= np.exp(
            -np.sum(
                coordinates * np.asarray(self.problem.linear),
                axis=1,
            )
        )
        for left, right, strength in self.problem.couplings:
            values *= np.exp(
                -strength
                * coordinates[:, left]
                * coordinates[:, right]
            )
        return values.reshape(output_shape)


def ttml_callable_tt_cross(problem, order: int, rank: int, rcp):
    from ttml.tensor_train import TensorTrain
    from ttml.tt_cross import tt_cross_dmrg

    nodes, weights = quadrature_rule(order)
    node_array = np.asarray(nodes)
    function = _CountedTensorFunction(
        problem,
        node_array,
        np.asarray(weights),
    )
    np.random.seed(0)
    build_started = time.perf_counter()
    tt = TensorTrain.random(
        (order,) * problem.dimension,
        rank,
        mode="r",
        backend="numpy",
        auto_rank=True,
    )
    build_seconds = time.perf_counter() - build_started
    decomposition_started = time.perf_counter()
    tt_cross_dmrg(
        tt,
        function,
        tol=1e-10,
        max_its=8,
        verbose=False,
        inplace=True,
    )
    decomposition_seconds = time.perf_counter() - decomposition_started
    readout_started = time.perf_counter()
    value, moments = _tt_readouts(tt.cores, node_array)
    readout_seconds = time.perf_counter() - readout_started
    return TensorBaselineResult(
        method="TTML_DMRG_TT-cross",
        package="ttml",
        package_version=_package_version("ttml"),
        value=value,
        axis_first_moments=moments,
        input_regime="black_box_callable",
        materialized_input_elements=0,
        function_evaluations=function.evaluations,
        unique_function_evaluations=len(function.unique_indices),
        representation_elements=int(tt.num_params()),
        build_seconds=build_seconds,
        decompose_seconds=decomposition_seconds,
        readout_seconds=readout_seconds,
        total_seconds=build_seconds + decomposition_seconds + readout_seconds,
        maximum_difference_vs_rcp=_maximum_output_difference(
            value,
            moments,
            rcp,
        ),
    )


def run_competitor_benchmark(
    dimension: int = 11,
    order: int = 4,
    rank: int = 8,
    repeats: int = 3,
    tolerance: float = 1e-12,
) -> dict[str, object]:
    problem = default_problem(dimension)
    reverse_plan = plan_reverse_work(problem, order)
    elimination_order, _width = min_fill_order(problem)
    declaration = RCPDeclaration(
        resolution_lambda=f"Gauss-Legendre nodes_per_axis={order}",
        tolerance=tolerance,
        axis_sizes=tuple((axis, order) for axis in range(dimension)),
        boundary_axes=(),
        output_names=("partition",)
        + tuple(f"axis_{axis}_first_moment" for axis in range(dimension)),
        max_work_tokens=1_000_000,
        max_peak_elements=1_000_000,
        query_strategy="one_forward_plus_reverse_lineage_all_moments",
    )

    # RCP's generic path planner prices the forward contraction.  The reverse
    # compiler independently prices sampling, the adjoint pass, and terminal
    # moment readouts; all parts are fixed before execution.
    forward_only = preflight_contraction(
        declaration,
        retained_factor_lineage(problem),
        elimination_order,
        executions=1,
        fixed_work_tokens=0,
    )
    if forward_only.status != ACCEPT:
        raise RuntimeError(forward_only.reason)
    additional_work = (
        reverse_plan.total_work_tokens
        - forward_only.value.plan.work_tokens_per_execution
    )
    preflight = preflight_contraction(
        declaration,
        retained_factor_lineage(problem),
        elimination_order,
        executions=1,
        fixed_work_tokens=additional_work,
    )
    if preflight.status != ACCEPT:
        raise RuntimeError(preflight.reason)

    rcp, rcp_wall_median, rcp_wall_samples = _median_run(
        lambda: compile_retained_reverse(problem, order),
        repeats,
    )
    assert isinstance(rcp, ReverseCompilerResult)
    external, opt_wall_median, opt_wall_samples = _median_run(
        lambda: external_opt_einsum(problem, order),
        repeats,
    )
    rcp_certificate = certify_contraction(
        preflight,
        (rcp.value, *rcp.axis_first_moments),
        (external.value, *external.axis_first_moments),
        measured_work_tokens=rcp.total_work_tokens,
        witness_method="external opt_einsum 3.4.0 contraction",
        measured_work_by_op={
            "factor_sample": rcp.factor_sample_tokens,
            "forward_multiply": rcp.forward_multiply_tokens,
            "forward_add": rcp.forward_add_tokens,
            "reverse_multiply": rcp.reverse_multiply_tokens,
            "reverse_add": rcp.reverse_add_tokens,
            "terminal_readout": rcp.readout_tokens,
        },
    )

    tt_svd, tt_svd_median, tt_svd_samples = _median_run(
        lambda: tensorly_tt_svd(problem, order, rank, rcp),
        repeats,
    )
    dense_cross, dense_cross_median, dense_cross_samples = _median_run(
        lambda: tensorly_tt_cross(problem, order, rank, rcp),
        repeats,
    )
    callable_cross, callable_cross_median, callable_cross_samples = _median_run(
        lambda: ttml_callable_tt_cross(problem, order, rank, rcp),
        repeats,
    )
    assert isinstance(tt_svd, TensorBaselineResult)
    assert isinstance(dense_cross, TensorBaselineResult)
    assert isinstance(callable_cross, TensorBaselineResult)

    opt_difference = _maximum_output_difference(
        external.value,
        external.axis_first_moments,
        rcp,
    )
    rcp_report = asdict(rcp)
    rcp_report["wall_seconds_median"] = rcp_wall_median
    rcp_report["wall_seconds_samples"] = rcp_wall_samples
    rcp_report["input_regime"] = "explicit_sparse_factor_graph"
    rcp_report["retained_factor_samples"] = rcp.factor_sample_tokens

    opt_report = asdict(external)
    opt_report["package_version"] = _package_version("opt_einsum")
    opt_report["wall_seconds_median"] = opt_wall_median
    opt_report["wall_seconds_samples"] = opt_wall_samples
    opt_report["input_regime"] = "explicit_sparse_factor_graph"
    opt_report["maximum_difference_vs_rcp"] = opt_difference

    tt_svd_report = asdict(tt_svd)
    tt_svd_report["wall_seconds_median"] = tt_svd_median
    tt_svd_report["wall_seconds_samples"] = tt_svd_samples
    dense_cross_report = asdict(dense_cross)
    dense_cross_report["wall_seconds_median"] = dense_cross_median
    dense_cross_report["wall_seconds_samples"] = dense_cross_samples
    callable_cross_report = asdict(callable_cross)
    callable_cross_report["wall_seconds_median"] = callable_cross_median
    callable_cross_report["wall_seconds_samples"] = callable_cross_samples

    competitors = {
        "opt_einsum": opt_report,
        "tensor_train_svd": tt_svd_report,
        "tensorly_tt_cross": dense_cross_report,
        "ttml_callable_tt_cross": callable_cross_report,
    }
    accepted = {
        name: float(result["maximum_difference_vs_rcp"]) <= tolerance
        for name, result in competitors.items()
    }
    speed_ratios = {
        "opt_einsum_over_rcp": opt_wall_median / rcp_wall_median,
        "tt_svd_over_rcp": tt_svd_median / rcp_wall_median,
        "tensorly_tt_cross_over_rcp": (
            dense_cross_median / rcp_wall_median
        ),
        "callable_tt_cross_over_rcp": (
            callable_cross_median / rcp_wall_median
        ),
    }
    return {
        "benchmark": {
            "dimension": dimension,
            "nodes_per_axis": order,
            "coupled": True,
            "separable": False,
            "tt_rank_cap": rank,
            "repeats": repeats,
            "declared_tolerance": tolerance,
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "rcp_reverse_compiler": rcp_report,
        "rcp_certificate": verdict_report(rcp_certificate),
        "competitors": competitors,
        "within_declared_tolerance": accepted,
        "measured_speed_ratios": speed_ratios,
        "input_information": {
            "rcp_factor_samples": rcp.factor_sample_tokens,
            "dense_tensor_elements": order**dimension,
            "ttml_cross_function_evaluations": (
                callable_cross.function_evaluations
            ),
            "ttml_cross_unique_function_evaluations": (
                callable_cross.unique_function_evaluations
            ),
        },
        "storage": {
            "rcp_peak_retained_elements": rcp.peak_retained_elements,
            "opt_einsum_largest_intermediate_elements": (
                external.largest_intermediate_elements
            ),
            "tt_svd_representation_elements": (
                tt_svd.representation_elements
            ),
            "tensorly_cross_representation_elements": (
                dense_cross.representation_elements
            ),
            "ttml_cross_representation_elements": (
                callable_cross.representation_elements
            ),
        },
        "arithmetic_reporting_caveat": (
            "RCP work tokens and opt_einsum optimized FLOPs come from different "
            "counting conventions; they are reported, not asserted identical."
        ),
        "scope": (
            "This establishes a measured win only for the declared sparse, "
            "bounded-width, many-readout workload and these implementations."
        ),
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dimension", type=int, default=11)
    parser.add_argument("--nodes-per-axis", type=int, default=4)
    parser.add_argument("--tt-rank", type=int, default=8)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--tolerance", type=float, default=1e-12)
    args = parser.parse_args(argv)
    report = run_competitor_benchmark(
        dimension=args.dimension,
        order=args.nodes_per_axis,
        rank=args.tt_rank,
        repeats=args.repeats,
        tolerance=args.tolerance,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    certificate = report["rcp_certificate"]
    return 0 if certificate["status"] == ACCEPT else 1


if __name__ == "__main__":
    raise SystemExit(main())
