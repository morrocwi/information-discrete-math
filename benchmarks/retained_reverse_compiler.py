#!/usr/bin/env python3
"""One forward retained contraction plus one reverse pass for all axis moments.

The earlier prototype repeated the full contraction once per requested moment.
This compiler treats the terminal readout as the boundary of a finite causal
program.  It contracts the partition once, reverses the recorded elimination
lineage once, and reads every one-axis first moment from the adjoints of the
unary retained factors.

This is reverse accumulation on a finite factor-contraction DAG.  Reverse-mode
automatic differentiation and marginal extraction are established techniques;
the research object here is their explicit RCP declaration, lineage, resource
gate, terminal-boundary certificate, and information-language architecture.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np

try:
    from benchmarks.coupled_nd_retained_compiler import (
        PairwiseProblem,
        WorkCounter,
        build_factors,
        min_fill_order,
    )
except ModuleNotFoundError:  # direct script execution
    from coupled_nd_retained_compiler import (
        PairwiseProblem,
        WorkCounter,
        build_factors,
        min_fill_order,
    )


@dataclass(frozen=True)
class DenseFactor:
    factor_id: int
    name: str
    scope: tuple[int, ...]
    values: np.ndarray


@dataclass(frozen=True)
class ReverseStep:
    axis: int
    joined_scope: tuple[int, ...]
    inputs: tuple[DenseFactor, ...]
    output: DenseFactor


@dataclass(frozen=True)
class ReverseCompilerResult:
    value: float
    axis_first_moments: list[float]
    elimination_order: list[int]
    induced_width: int
    factor_sample_tokens: int
    forward_multiply_tokens: int
    forward_add_tokens: int
    reverse_multiply_tokens: int
    reverse_add_tokens: int
    readout_tokens: int
    total_work_tokens: int
    peak_retained_elements: int
    elapsed_seconds: float


@dataclass(frozen=True)
class ReverseWorkPlan:
    factor_sample_tokens: int
    forward_multiply_tokens: int
    forward_add_tokens: int
    reverse_multiply_tokens: int
    reverse_add_tokens: int
    readout_tokens: int
    total_work_tokens: int
    peak_retained_elements: int


def _elements(scope: tuple[int, ...], node_count: int) -> int:
    return node_count ** len(scope)


def _align(
    values: np.ndarray,
    scope: tuple[int, ...],
    joined_scope: tuple[int, ...],
    node_count: int,
) -> np.ndarray:
    shape = tuple(node_count if axis in scope else 1 for axis in joined_scope)
    return values.reshape(shape)


def _dense_factors(
    problem: PairwiseProblem,
    order: int,
) -> tuple[list[DenseFactor], tuple[float, ...], WorkCounter, dict[int, int]]:
    factors, nodes, counter = build_factors(problem, order)
    dense: list[DenseFactor] = []
    unary_ids: dict[int, int] = {}
    for factor_id, factor in enumerate(factors):
        shape = (order,) * len(factor.scope)
        values = np.empty(shape, dtype=float)
        for key, value in factor.values.items():
            values[key] = value
        name = (
            f"axis_{factor.scope[0]}"
            if len(factor.scope) == 1
            else (
                f"coupling_{factor_id - problem.dimension}_"
                + "_".join(str(axis) for axis in factor.scope)
            )
        )
        dense_factor = DenseFactor(factor_id, name, factor.scope, values)
        dense.append(dense_factor)
        if len(factor.scope) == 1:
            unary_ids[factor.scope[0]] = factor_id
    return dense, nodes, counter, unary_ids


def _sum_to_scope(
    contribution: np.ndarray,
    joined_scope: tuple[int, ...],
    target_scope: tuple[int, ...],
) -> np.ndarray:
    reduce_axes = tuple(
        position
        for position, axis in enumerate(joined_scope)
        if axis not in target_scope
    )
    if reduce_axes:
        contribution = contribution.sum(axis=reduce_axes)
    return np.asarray(contribution)


def plan_reverse_work(
    problem: PairwiseProblem,
    order: int,
) -> ReverseWorkPlan:
    """Symbolically price the complete forward/reverse program before tick 0."""
    active: list[tuple[str, tuple[int, ...]]] = [
        (f"axis_{axis}", (axis,))
        for axis in range(problem.dimension)
    ] + [
        (f"coupling_{edge_index}_{left}_{right}", (left, right))
        for edge_index, (left, right, _strength) in enumerate(problem.couplings)
    ]
    elimination_order, _induced_width = min_fill_order(problem)
    forward_multiply = 0
    forward_add = 0
    reverse_multiply = 0
    reverse_add = 0
    peak_elements = max(order ** len(scope) for _name, scope in active)

    for step_index, axis in enumerate(elimination_order):
        bucket = [factor for factor in active if axis in factor[1]]
        active = [factor for factor in active if axis not in factor[1]]
        joined_scope = tuple(
            sorted({item for _name, scope in bucket for item in scope})
        )
        joined_elements = order ** len(joined_scope)
        output_scope = tuple(item for item in joined_scope if item != axis)
        peak_elements = max(peak_elements, order ** len(output_scope))
        forward_multiply += joined_elements * len(bucket)
        forward_add += joined_elements

        # For each bucket input, reverse accumulation multiplies the incoming
        # adjoint by every other factor.  The executor's ledger also charges
        # copying the incoming adjoint as one multiplication-equivalent token.
        reverse_multiply += joined_elements * len(bucket) ** 2
        for _name, target_scope in bucket:
            if set(joined_scope) - set(target_scope):
                reverse_add += joined_elements

        active.append(
            (f"rcp_step_{step_index}_after_axis_{axis}", output_scope)
        )

    forward_multiply += len(active)
    reverse_multiply += len(active) * max(len(active) - 1, 0)
    factor_samples = (
        problem.dimension * order
        + len(problem.couplings) * order**2
    )
    readout_tokens = problem.dimension * (3 * order + 1)
    total = (
        factor_samples
        + forward_multiply
        + forward_add
        + reverse_multiply
        + reverse_add
        + readout_tokens
    )
    return ReverseWorkPlan(
        factor_sample_tokens=factor_samples,
        forward_multiply_tokens=forward_multiply,
        forward_add_tokens=forward_add,
        reverse_multiply_tokens=reverse_multiply,
        reverse_add_tokens=reverse_add,
        readout_tokens=readout_tokens,
        total_work_tokens=total,
        peak_retained_elements=peak_elements,
    )


def compile_retained_reverse(
    problem: PairwiseProblem,
    order: int,
) -> ReverseCompilerResult:
    """Return partition and every axis moment from one contraction DAG."""
    started = time.perf_counter()
    active, nodes, sample_counter, unary_ids = _dense_factors(problem, order)
    elimination_order, induced_width = min_fill_order(problem)
    next_factor_id = len(active)
    steps: list[ReverseStep] = []
    forward_multiply = 0
    forward_add = 0
    peak_elements = max(factor.values.size for factor in active)

    for step_index, axis in enumerate(elimination_order):
        bucket = tuple(factor for factor in active if axis in factor.scope)
        active = [factor for factor in active if axis not in factor.scope]
        if not bucket:
            continue
        joined_scope = tuple(
            sorted({item for factor in bucket for item in factor.scope})
        )
        joint_shape = (order,) * len(joined_scope)
        joint = np.ones(joint_shape, dtype=float)
        for factor in bucket:
            joint *= _align(factor.values, factor.scope, joined_scope, order)
        joined_elements = joint.size
        forward_multiply += joined_elements * len(bucket)
        forward_add += joined_elements

        axis_position = joined_scope.index(axis)
        output_values = joint.sum(axis=axis_position)
        output_scope = tuple(item for item in joined_scope if item != axis)
        output = DenseFactor(
            next_factor_id,
            f"rcp_step_{step_index}_after_axis_{axis}",
            output_scope,
            np.asarray(output_values),
        )
        next_factor_id += 1
        peak_elements = max(peak_elements, output.values.size)
        active.append(output)
        steps.append(ReverseStep(axis, joined_scope, bucket, output))

    if any(factor.scope for factor in active):
        raise AssertionError(
            f"uneliminated scopes: {[factor.scope for factor in active]}"
        )
    terminal_values = [float(factor.values) for factor in active]
    partition = float(np.prod(terminal_values))
    forward_multiply += len(active)

    adjoints: dict[int, np.ndarray] = {}
    reverse_multiply = 0
    reverse_add = 0
    for factor_index, factor in enumerate(active):
        other_values = (
            terminal_values[:factor_index] + terminal_values[factor_index + 1 :]
        )
        adjoints[factor.factor_id] = np.asarray(
            float(np.prod(other_values)) if other_values else 1.0
        )
        reverse_multiply += len(other_values)

    for step in reversed(steps):
        output_adjoint = adjoints.pop(step.output.factor_id)
        joined_shape = (order,) * len(step.joined_scope)
        expanded_output_scope = tuple(
            axis for axis in step.joined_scope if axis != step.axis
        )
        adjoint_joint = _align(
            output_adjoint,
            expanded_output_scope,
            step.joined_scope,
            order,
        )
        adjoint_joint = np.broadcast_to(adjoint_joint, joined_shape)
        joined_elements = _elements(step.joined_scope, order)

        for target in step.inputs:
            contribution = np.array(adjoint_joint, copy=True)
            reverse_multiply += joined_elements
            for other in step.inputs:
                if other.factor_id == target.factor_id:
                    continue
                contribution *= _align(
                    other.values,
                    other.scope,
                    step.joined_scope,
                    order,
                )
                reverse_multiply += joined_elements
            reduce_count = len(set(step.joined_scope) - set(target.scope))
            if reduce_count:
                reverse_add += joined_elements
            target_adjoint = _sum_to_scope(
                contribution,
                step.joined_scope,
                target.scope,
            )
            if target.factor_id in adjoints:
                adjoints[target.factor_id] += target_adjoint
                reverse_add += target_adjoint.size
            else:
                adjoints[target.factor_id] = target_adjoint

    node_array = np.asarray(nodes)
    moments: list[float] = []
    readout_tokens = 0
    original_by_id = {
        factor.factor_id: factor
        for step in steps
        for factor in step.inputs
        if factor.factor_id < len(unary_ids) + len(problem.couplings)
    }
    # All original factors occur in exactly one bucket; the comprehension above
    # recovers them without retaining a second tensor copy.
    for axis in range(problem.dimension):
        factor_id = unary_ids[axis]
        unary = original_by_id[factor_id]
        numerator_terms = adjoints[factor_id] * unary.values * node_array
        numerator = float(np.sum(numerator_terms))
        moments.append(numerator / partition)
        readout_tokens += 2 * order + order + 1

    total_work = (
        sample_counter.factor_sample_tokens
        + forward_multiply
        + forward_add
        + reverse_multiply
        + reverse_add
        + readout_tokens
    )
    return ReverseCompilerResult(
        value=partition,
        axis_first_moments=moments,
        elimination_order=elimination_order,
        induced_width=induced_width,
        factor_sample_tokens=sample_counter.factor_sample_tokens,
        forward_multiply_tokens=forward_multiply,
        forward_add_tokens=forward_add,
        reverse_multiply_tokens=reverse_multiply,
        reverse_add_tokens=reverse_add,
        readout_tokens=readout_tokens,
        total_work_tokens=total_work,
        peak_retained_elements=peak_elements,
        elapsed_seconds=time.perf_counter() - started,
    )
