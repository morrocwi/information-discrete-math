#!/usr/bin/env python3
"""LLVM execution substrate for the native Retained Readout Pullback.

The planner and sensitivity grammar remain RRP-native.  Numba is used only to
compile the already-declared finite closure program; no automatic
differentiation, junction-tree construction, or tensor-network backend is
called.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from functools import lru_cache
from hashlib import sha256
from typing import Iterable

import numpy as np

try:
    from numba import njit
    from numba.typed import List
except ImportError as exc:  # pragma: no cover - optional benchmark backend
    raise RuntimeError("install numba to run compiled native RRP") from exc

try:
    from benchmarks.coupled_nd_retained_compiler import PairwiseProblem
    from benchmarks.direct_nd_work_tokens import quadrature_rule
    from benchmarks.retained_fold_tree import (
        _plan_retained_closure_program,
        compile_retained_readout_pullback,
    )
except ModuleNotFoundError:  # direct script execution
    from coupled_nd_retained_compiler import PairwiseProblem
    from direct_nd_work_tokens import quadrature_rule
    from retained_fold_tree import (
        _plan_retained_closure_program,
        compile_retained_readout_pullback,
    )


@dataclass(frozen=True)
class CompiledRetainedPullbackResult:
    value: float
    partition_gradients: list[float]
    log_partition_gradients: list[float]
    compile_plus_first_execution_seconds: float
    strategy: str
    plan_signature: str = ""
    topology_cache_hit: bool = False
    structural_witness: dict[str, int | str | bool] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class RetainedTopology:
    """Value-independent identity of one finite retained program family."""

    dimension: int
    edge_scopes: tuple[tuple[int, int], ...]
    order: int

    @property
    def signature(self) -> str:
        payload = (
            f"rrp-plan-v1|d={self.dimension}|q={self.order}|"
            + ",".join(
                f"{left}:{right}" for left, right in self.edge_scopes
            )
        )
        return sha256(payload.encode("ascii")).hexdigest()[:16]


def retained_topology(
    problem: PairwiseProblem,
    order: int,
) -> RetainedTopology:
    """Erase coefficient values while retaining declared dependency scopes."""
    return RetainedTopology(
        dimension=problem.dimension,
        edge_scopes=tuple(
            (left, right) for left, right, _strength in problem.couplings
        ),
        order=order,
    )


@lru_cache(maxsize=256)
def _parameter_array(problem: PairwiseProblem) -> np.ndarray:
    """Materialize values separately from the cached structural program."""
    parameters = np.asarray(
        [
            *problem.linear,
            *(
                strength
                for _left, _right, strength in problem.couplings
            ),
        ],
        dtype=np.float64,
    )
    parameters.setflags(write=False)
    return parameters


@njit
def _fill_original_factors(
    parameters,
    nodes,
    weights,
    order,
    dimension,
    coupling_count,
    factor_values,
):
    for axis in range(dimension):
        target = factor_values[axis]
        coefficient = parameters[axis]
        for state in range(order):
            target[state] = (
                weights[state] * math.exp(-coefficient * nodes[state])
            )
    for edge_index in range(coupling_count):
        target = factor_values[dimension + edge_index]
        strength = parameters[dimension + edge_index]
        for left_state in range(order):
            for right_state in range(order):
                target[left_state * order + right_state] = math.exp(
                    -strength
                    * nodes[left_state]
                    * nodes[right_state]
                )


@njit
def _execute_dense_retained_pullback_serial(
    parameters,
    nodes,
    weights,
    order,
    dimension,
    coupling_left,
    coupling_right,
    input_ids,
    input_count,
    input_maps,
    axis_states,
    factor_values,
    masses,
):
    coupling_count = len(coupling_left)
    _fill_original_factors(
        parameters,
        nodes,
        weights,
        order,
        dimension,
        coupling_count,
        factor_values,
    )
    joint_length = len(masses)
    partition = 0.0
    for joint_index in range(joint_length):
        mass = 1.0
        for input_position in range(input_count):
            factor_id = input_ids[input_position]
            mass *= factor_values[factor_id][
                input_maps[input_position, joint_index]
            ]
        masses[joint_index] = mass
        partition += mass

    parameter_count = dimension + coupling_count
    partition_gradients = np.empty(parameter_count, dtype=np.float64)
    log_partition_gradients = np.empty(parameter_count, dtype=np.float64)
    for parameter_index in range(parameter_count):
        numerator = 0.0
        if parameter_index < dimension:
            for joint_index in range(joint_length):
                numerator += (
                    nodes[axis_states[parameter_index, joint_index]]
                    * masses[joint_index]
                )
        else:
            edge_index = parameter_index - dimension
            left = coupling_left[edge_index]
            right = coupling_right[edge_index]
            for joint_index in range(joint_length):
                numerator += (
                    nodes[axis_states[left, joint_index]]
                    * nodes[axis_states[right, joint_index]]
                    * masses[joint_index]
                )
        partition_gradients[parameter_index] = -numerator
        log_partition_gradients[parameter_index] = -numerator / partition
    return partition, partition_gradients, log_partition_gradients


@njit
def _execute_compiled_retained_pullback(
    parameters,
    nodes,
    weights,
    order,
    dimension,
    coupling_left,
    coupling_right,
    closure_input_ids,
    closure_input_counts,
    closure_input_maps,
    closure_input_pair_indices,
    closure_pair_left_positions,
    closure_pair_right_positions,
    closure_output_ids,
    closure_output_maps,
    closure_joint_lengths,
    closure_axis_ids,
    closure_axis_positions,
    closure_axis_counts,
    terminal_factor_ids,
    factor_values,
    closure_joints,
    factor_contexts,
):
    coupling_count = len(coupling_left)
    original_factor_count = dimension + coupling_count

    _fill_original_factors(
        parameters,
        nodes,
        weights,
        order,
        dimension,
        coupling_count,
        factor_values,
    )

    closure_count = len(closure_output_ids)
    for closure_index in range(closure_count):
        output = factor_values[closure_output_ids[closure_index]]
        output[:] = 0.0
        joint = closure_joints[closure_index]
        joint_length = closure_joint_lengths[closure_index]
        input_count = closure_input_counts[closure_index]
        for joint_index in range(joint_length):
            product = 1.0
            for input_position in range(input_count):
                factor_id = closure_input_ids[
                    closure_index, input_position
                ]
                factor_index = closure_input_maps[
                    closure_index, input_position, joint_index
                ]
                product *= factor_values[factor_id][factor_index]
            joint[joint_index] = product
            output_index = closure_output_maps[
                closure_index, joint_index
            ]
            output[output_index] += product

    partition = 1.0
    for terminal_position in range(len(terminal_factor_ids)):
        partition *= factor_values[
            terminal_factor_ids[terminal_position]
        ][0]

    for factor_id in range(original_factor_count, len(factor_contexts)):
        factor_contexts[factor_id][:] = 0.0
    for terminal_position in range(len(terminal_factor_ids)):
        context = 1.0
        for other_position in range(len(terminal_factor_ids)):
            if other_position != terminal_position:
                context *= factor_values[
                    terminal_factor_ids[other_position]
                ][0]
        factor_contexts[terminal_factor_ids[terminal_position]][0] = context

    axis_numerators = np.zeros(dimension, dtype=np.float64)
    coupling_numerators = np.zeros(coupling_count, dtype=np.float64)

    for reverse_index in range(closure_count):
        closure_index = closure_count - reverse_index - 1
        output_context = factor_contexts[
            closure_output_ids[closure_index]
        ]
        joint = closure_joints[closure_index]
        joint_length = closure_joint_lengths[closure_index]
        input_count = closure_input_counts[closure_index]
        axis_count = closure_axis_counts[closure_index]

        for joint_index in range(joint_length):
            output_index = closure_output_maps[
                closure_index, joint_index
            ]
            belief = joint[joint_index] * output_context[output_index]

            for axis_position in range(axis_count):
                axis = closure_axis_ids[closure_index, axis_position]
                state_position = closure_axis_positions[
                    closure_index, axis_position, joint_index
                ]
                axis_numerators[axis] += nodes[state_position] * belief

            for input_position in range(input_count):
                pair_index = closure_input_pair_indices[
                    closure_index, input_position
                ]
                if pair_index >= 0:
                    left_state = closure_pair_left_positions[
                        closure_index, input_position, joint_index
                    ]
                    right_state = closure_pair_right_positions[
                        closure_index, input_position, joint_index
                    ]
                    coupling_numerators[pair_index] += (
                        nodes[left_state] * nodes[right_state] * belief
                    )

                child_factor_id = closure_input_ids[
                    closure_index, input_position
                ]
                if child_factor_id >= original_factor_count:
                    child_index = closure_input_maps[
                        closure_index, input_position, joint_index
                    ]
                    factor_contexts[child_factor_id][child_index] += (
                        belief
                        / factor_values[child_factor_id][child_index]
                    )

    parameter_count = dimension + coupling_count
    partition_gradients = np.empty(parameter_count, dtype=np.float64)
    log_partition_gradients = np.empty(parameter_count, dtype=np.float64)
    for axis in range(dimension):
        moment = axis_numerators[axis] / partition
        log_partition_gradients[axis] = -moment
        partition_gradients[axis] = -axis_numerators[axis]
    for edge_index in range(coupling_count):
        moment = coupling_numerators[edge_index] / partition
        parameter_index = dimension + edge_index
        log_partition_gradients[parameter_index] = -moment
        partition_gradients[parameter_index] = -coupling_numerators[
            edge_index
        ]

    return partition, partition_gradients, log_partition_gradients


def _flat_states(flat_index: int, width: int, order: int) -> list[int]:
    states = [0] * width
    remainder = flat_index
    for position in range(width - 1, -1, -1):
        states[position] = remainder % order
        remainder //= order
    return states


class CompiledRetainedReadoutProgram:
    """Preplanned native RRP whose finite loop program is LLVM-compiled."""

    def __init__(self, topology: RetainedTopology) -> None:
        started = time.perf_counter()
        problem = PairwiseProblem(
            dimension=topology.dimension,
            linear=(0.0,) * topology.dimension,
            couplings=tuple(
                (left, right, 0.0)
                for left, right in topology.edge_scopes
            ),
        )
        order = topology.order
        self.topology = topology
        self.order = topology.order
        program = _plan_retained_closure_program(problem, order, 16_384)
        closures = program.closures
        dimension = problem.dimension
        coupling_count = len(problem.couplings)
        original_factor_count = dimension + coupling_count
        factor_scopes: list[tuple[int, ...]] = [
            (axis,) for axis in range(dimension)
        ] + [
            (left, right)
            for left, right, _strength in problem.couplings
        ]
        for closure in closures:
            if closure.output_factor_id != len(factor_scopes):
                raise AssertionError("non-contiguous compiled factor ids")
            factor_scopes.append(closure.output_scope)

        closure_count = len(closures)
        max_inputs = max(
            (len(closure.input_factor_ids) for closure in closures),
            default=1,
        )
        max_axes = max(
            (len(closure.axes) for closure in closures),
            default=1,
        )
        max_joint = max(
            (
                order ** len(closure.joined_scope)
                for closure in closures
            ),
            default=1,
        )
        closure_input_ids = np.zeros(
            (closure_count, max_inputs), dtype=np.int32
        )
        closure_input_counts = np.zeros(closure_count, dtype=np.int32)
        closure_input_maps = np.zeros(
            (closure_count, max_inputs, max_joint), dtype=np.int32
        )
        closure_input_pair_indices = np.full(
            (closure_count, max_inputs), -1, dtype=np.int32
        )
        closure_pair_left_positions = np.zeros(
            (closure_count, max_inputs, max_joint), dtype=np.int16
        )
        closure_pair_right_positions = np.zeros(
            (closure_count, max_inputs, max_joint), dtype=np.int16
        )
        closure_output_ids = np.zeros(closure_count, dtype=np.int32)
        closure_output_maps = np.zeros(
            (closure_count, max_joint), dtype=np.int32
        )
        closure_joint_lengths = np.zeros(closure_count, dtype=np.int32)
        closure_axis_ids = np.zeros(
            (closure_count, max_axes), dtype=np.int32
        )
        closure_axis_positions = np.zeros(
            (closure_count, max_axes, max_joint), dtype=np.int16
        )
        closure_axis_counts = np.zeros(closure_count, dtype=np.int32)

        for closure_index, closure in enumerate(closures):
            joined_position = {
                axis: position
                for position, axis in enumerate(closure.joined_scope)
            }
            joint_length = order ** len(closure.joined_scope)
            closure_joint_lengths[closure_index] = joint_length
            closure_input_counts[closure_index] = len(
                closure.input_factor_ids
            )
            closure_output_ids[closure_index] = closure.output_factor_id
            closure_axis_counts[closure_index] = len(closure.axes)
            for axis_position, axis in enumerate(closure.axes):
                closure_axis_ids[closure_index, axis_position] = axis

            for input_position, factor_id in enumerate(
                closure.input_factor_ids
            ):
                closure_input_ids[
                    closure_index, input_position
                ] = factor_id
                if (
                    dimension
                    <= factor_id
                    < original_factor_count
                ):
                    edge_index = factor_id - dimension
                    closure_input_pair_indices[
                        closure_index, input_position
                    ] = edge_index

            for joint_index in range(joint_length):
                states = _flat_states(
                    joint_index,
                    len(closure.joined_scope),
                    order,
                )
                for axis_position, axis in enumerate(closure.axes):
                    closure_axis_positions[
                        closure_index, axis_position, joint_index
                    ] = states[joined_position[axis]]

                output_index = 0
                for axis in closure.output_scope:
                    output_index = (
                        output_index * order
                        + states[joined_position[axis]]
                    )
                closure_output_maps[
                    closure_index, joint_index
                ] = output_index

                for input_position, factor_id in enumerate(
                    closure.input_factor_ids
                ):
                    factor_index = 0
                    for axis in factor_scopes[factor_id]:
                        factor_index = (
                            factor_index * order
                            + states[joined_position[axis]]
                        )
                    closure_input_maps[
                        closure_index, input_position, joint_index
                    ] = factor_index
                    pair_index = closure_input_pair_indices[
                        closure_index, input_position
                    ]
                    if pair_index >= 0:
                        left, right, _strength = problem.couplings[pair_index]
                        closure_pair_left_positions[
                            closure_index, input_position, joint_index
                        ] = states[joined_position[left]]
                        closure_pair_right_positions[
                            closure_index, input_position, joint_index
                        ] = states[joined_position[right]]

        nodes, weights = quadrature_rule(order)
        self.nodes = np.asarray(nodes, dtype=np.float64)
        self.weights = np.asarray(weights, dtype=np.float64)
        self.dimension = dimension
        self.coupling_left = np.asarray(
            [left for left, _right, _strength in problem.couplings],
            dtype=np.int32,
        )
        self.coupling_right = np.asarray(
            [right for _left, right, _strength in problem.couplings],
            dtype=np.int32,
        )
        self.closure_input_ids = closure_input_ids
        self.closure_input_counts = closure_input_counts
        self.closure_input_maps = closure_input_maps
        self.closure_input_pair_indices = closure_input_pair_indices
        self.closure_pair_left_positions = closure_pair_left_positions
        self.closure_pair_right_positions = closure_pair_right_positions
        self.closure_output_ids = closure_output_ids
        self.closure_output_maps = closure_output_maps
        self.closure_joint_lengths = closure_joint_lengths
        self.closure_axis_ids = closure_axis_ids
        self.closure_axis_positions = closure_axis_positions
        self.closure_axis_counts = closure_axis_counts
        self.terminal_factor_ids = np.asarray(
            program.terminal_factor_ids,
            dtype=np.int32,
        )
        self.dense_axis_states = np.zeros((0, 0), dtype=np.int16)
        self.dense_mode = (
            closure_count == 1
            and len(closures[0].axes) == dimension
            and int(closure_joint_lengths[0]) < 16_384
        )
        if self.dense_mode:
            joint_length = int(closure_joint_lengths[0])
            self.dense_axis_states = np.zeros(
                (dimension, joint_length),
                dtype=np.int16,
            )
            for axis_position in range(
                int(closure_axis_counts[0])
            ):
                axis = int(closure_axis_ids[0, axis_position])
                self.dense_axis_states[axis] = closure_axis_positions[
                    0, axis_position, :joint_length
                ]

        self.factor_values = List()
        self.factor_contexts = List()
        for scope in factor_scopes:
            length = order ** len(scope)
            self.factor_values.append(np.zeros(length, dtype=np.float64))
            self.factor_contexts.append(np.zeros(length, dtype=np.float64))
        self.closure_joints = List()
        for joint_length in closure_joint_lengths:
            self.closure_joints.append(
                np.zeros(int(joint_length), dtype=np.float64)
            )

        self.closure_count = closure_count
        self.largest_joint_length = int(
            np.max(closure_joint_lengths, initial=0)
        )
        self._execute(
            np.zeros(
                topology.dimension + len(topology.edge_scopes),
                dtype=np.float64,
            )
        )
        self.compile_plus_first_execution_seconds = (
            time.perf_counter() - started
        )

    def _execute(self, parameters: np.ndarray):
        if self.dense_mode:
            arguments = (
                parameters,
                self.nodes,
                self.weights,
                self.order,
                self.dimension,
                self.coupling_left,
                self.coupling_right,
                self.closure_input_ids[0],
                int(self.closure_input_counts[0]),
                self.closure_input_maps[0],
                self.dense_axis_states,
                self.factor_values,
                self.closure_joints[0],
            )
            return _execute_dense_retained_pullback_serial(*arguments)
        return _execute_compiled_retained_pullback(
            parameters,
            self.nodes,
            self.weights,
            self.order,
            self.dimension,
            self.coupling_left,
            self.coupling_right,
            self.closure_input_ids,
            self.closure_input_counts,
            self.closure_input_maps,
            self.closure_input_pair_indices,
            self.closure_pair_left_positions,
            self.closure_pair_right_positions,
            self.closure_output_ids,
            self.closure_output_maps,
            self.closure_joint_lengths,
            self.closure_axis_ids,
            self.closure_axis_positions,
            self.closure_axis_counts,
            self.terminal_factor_ids,
            self.factor_values,
            self.closure_joints,
            self.factor_contexts,
        )

    def run(
        self,
        parameters: np.ndarray,
        *,
        topology_cache_hit: bool,
    ) -> CompiledRetainedPullbackResult:
        expected = self.topology.dimension + len(self.topology.edge_scopes)
        if parameters.shape != (expected,):
            raise ValueError(
                f"expected {expected} parameters, got {parameters.shape}"
            )
        value, gradient, log_gradient = self._execute(parameters)
        return CompiledRetainedPullbackResult(
            value=float(value),
            partition_gradients=[
                float(item) for item in np.asarray(gradient)
            ],
            log_partition_gradients=[
                float(item) for item in np.asarray(log_gradient)
            ],
            compile_plus_first_execution_seconds=(
                self.compile_plus_first_execution_seconds
            ),
            strategy="Numba/LLVM compiled sparse closure",
            plan_signature=self.topology.signature,
            topology_cache_hit=topology_cache_hit,
            structural_witness={
                "plan_version": "rrp-plan-v1",
                "dimension": self.topology.dimension,
                "coupling_count": len(self.topology.edge_scopes),
                "quadrature_order": self.topology.order,
                "closure_count": self.closure_count,
                "largest_joint_length": self.largest_joint_length,
                "parameter_values_in_plan_key": False,
                "autodiff": False,
                "jax_dependency": False,
            },
        )


def _finite_state_block(
    width: int,
    order: int,
    nodes: np.ndarray,
    weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Declare every finite state and quadrature weight in one block."""
    if width == 0:
        return (
            np.zeros((1, 0), dtype=np.float64),
            np.ones(1, dtype=np.float64),
        )
    indices = np.indices(
        (order,) * width,
        dtype=np.int16,
    ).reshape(width, -1).T
    return (
        np.ascontiguousarray(nodes[indices]),
        np.prod(weights[indices], axis=1),
    )


class BalancedRetainedCutProgram:
    """Exact dense readout through one balanced retained boundary.

    The left and right state blocks are finite declared records. Their only
    shared retained distinction is the cross-block interaction matrix. One
    mass matrix then supplies the partition, within-block moments, and
    cross-block moments without an autodiff tape or factor-by-factor tensor
    construction.
    """

    def __init__(self, topology: RetainedTopology) -> None:
        started = time.perf_counter()
        self.topology = topology
        self.dimension = topology.dimension
        self.split = topology.dimension // 2
        right_width = topology.dimension - self.split
        nodes, weights = quadrature_rule(topology.order)
        node_array = np.asarray(nodes, dtype=np.float64)
        weight_array = np.asarray(weights, dtype=np.float64)
        self.left_states, self.left_weights = _finite_state_block(
            self.split,
            topology.order,
            node_array,
            weight_array,
        )
        self.right_states, self.right_weights = _finite_state_block(
            right_width,
            topology.order,
            node_array,
            weight_array,
        )
        self.left_log_weights = np.log(self.left_weights)
        self.right_log_weights = np.log(self.right_weights)

        left_edges: list[tuple[int, int, int]] = []
        right_edges: list[tuple[int, int, int]] = []
        cross_edges: list[tuple[int, int, int]] = []
        for edge_index, (first, second) in enumerate(topology.edge_scopes):
            if first < self.split and second < self.split:
                left_edges.append((edge_index, first, second))
            elif first >= self.split and second >= self.split:
                right_edges.append(
                    (
                        edge_index,
                        first - self.split,
                        second - self.split,
                    )
                )
            elif first < self.split:
                cross_edges.append(
                    (edge_index, first, second - self.split)
                )
            else:
                cross_edges.append(
                    (edge_index, second, first - self.split)
                )

        self.left_edge_ids = np.asarray(
            [edge for edge, _first, _second in left_edges],
            dtype=np.int32,
        )
        self.right_edge_ids = np.asarray(
            [edge for edge, _first, _second in right_edges],
            dtype=np.int32,
        )
        self.cross_edge_ids = np.asarray(
            [edge for edge, _first, _second in cross_edges],
            dtype=np.int32,
        )
        self.cross_left = np.asarray(
            [first for _edge, first, _second in cross_edges],
            dtype=np.int32,
        )
        self.cross_right = np.asarray(
            [second for _edge, _first, second in cross_edges],
            dtype=np.int32,
        )
        self.cross_scopes_unique = (
            len(set(zip(self.cross_left, self.cross_right)))
            == len(cross_edges)
        )

        self.left_pair_features = np.ascontiguousarray(
            np.column_stack(
                [
                    self.left_states[:, first]
                    * self.left_states[:, second]
                    for _edge, first, second in left_edges
                ]
            )
            if left_edges
            else np.zeros(
                (len(self.left_states), 0),
                dtype=np.float64,
            )
        )
        self.right_pair_features = np.ascontiguousarray(
            np.column_stack(
                [
                    self.right_states[:, first]
                    * self.right_states[:, second]
                    for _edge, first, second in right_edges
                ]
            )
            if right_edges
            else np.zeros(
                (len(self.right_states), 0),
                dtype=np.float64,
            )
        )
        self.left_statistics = np.ascontiguousarray(
            np.concatenate(
                (self.left_states, self.left_pair_features),
                axis=1,
            )
        )
        self.right_statistics = np.ascontiguousarray(
            np.concatenate(
                (self.right_states, self.right_pair_features),
                axis=1,
            )
        )
        self.left_parameter_indices = np.concatenate(
            (
                np.arange(self.split, dtype=np.int32),
                self.dimension + self.left_edge_ids,
            )
        )
        self.right_parameter_indices = np.concatenate(
            (
                np.arange(
                    self.split,
                    self.dimension,
                    dtype=np.int32,
                ),
                self.dimension + self.right_edge_ids,
            )
        )

        self.cross_coefficients = np.zeros(
            (self.split, right_width),
            dtype=np.float64,
        )
        self.cross_energy_left = np.empty(
            (len(self.left_states), right_width),
            dtype=np.float64,
        )
        self.mass = np.empty(
            (len(self.left_states), len(self.right_states)),
            dtype=np.float64,
        )
        self.mass_times_right = np.empty(
            (len(self.left_states), right_width),
            dtype=np.float64,
        )
        self.retained_elements = (
            self.left_states.size
            + self.right_states.size
            + self.left_statistics.size
            + self.right_statistics.size
            + self.mass.size
            + self.cross_energy_left.size
            + self.mass_times_right.size
        )
        self._execute(
            np.zeros(
                self.dimension + len(topology.edge_scopes),
                dtype=np.float64,
            )
        )
        self.compile_plus_first_execution_seconds = (
            time.perf_counter() - started
        )

    def _execute(
        self,
        parameters: np.ndarray,
    ) -> tuple[float, np.ndarray, np.ndarray]:
        left_score = self.left_log_weights - (
            self.left_statistics
            @ parameters[self.left_parameter_indices]
        )
        right_score = self.right_log_weights - (
            self.right_statistics
            @ parameters[self.right_parameter_indices]
        )

        self.cross_coefficients.fill(0.0)
        cross_values = -parameters[
            self.dimension + self.cross_edge_ids
        ]
        if self.cross_scopes_unique:
            self.cross_coefficients[
                self.cross_left,
                self.cross_right,
            ] = cross_values
        else:
            np.add.at(
                self.cross_coefficients,
                (self.cross_left, self.cross_right),
                cross_values,
            )

        np.matmul(
            self.left_states,
            self.cross_coefficients,
            out=self.cross_energy_left,
        )
        np.matmul(
            self.cross_energy_left,
            self.right_states.T,
            out=self.mass,
        )
        self.mass += left_score[:, None]
        self.mass += right_score[None, :]
        np.exp(self.mass, out=self.mass)

        left_mass = self.mass.sum(axis=1)
        right_mass = self.mass.sum(axis=0)
        partition = float(left_mass.sum())
        parameter_count = self.dimension + len(
            self.topology.edge_scopes
        )
        gradients = np.empty(parameter_count, dtype=np.float64)
        gradients[: self.split] = -(
            self.left_states.T @ left_mass
        )
        gradients[self.split : self.dimension] = -(
            self.right_states.T @ right_mass
        )
        gradients[self.dimension + self.left_edge_ids] = -(
            self.left_pair_features.T @ left_mass
        )
        gradients[self.dimension + self.right_edge_ids] = -(
            self.right_pair_features.T @ right_mass
        )

        np.matmul(
            self.mass,
            self.right_states,
            out=self.mass_times_right,
        )
        cross_moments = -(
            self.left_states.T @ self.mass_times_right
        )
        gradients[self.dimension + self.cross_edge_ids] = cross_moments[
            self.cross_left,
            self.cross_right,
        ]
        return partition, gradients, gradients / partition

    def run(
        self,
        parameters: np.ndarray,
        *,
        topology_cache_hit: bool,
    ) -> CompiledRetainedPullbackResult:
        expected = self.dimension + len(self.topology.edge_scopes)
        if parameters.shape != (expected,):
            raise ValueError(
                f"expected {expected} parameters, got {parameters.shape}"
            )
        value, gradient, log_gradient = self._execute(parameters)
        return CompiledRetainedPullbackResult(
            value=value,
            partition_gradients=[
                float(item) for item in np.asarray(gradient)
            ],
            log_partition_gradients=[
                float(item) for item in np.asarray(log_gradient)
            ],
            compile_plus_first_execution_seconds=(
                self.compile_plus_first_execution_seconds
            ),
            strategy="NumPy balanced retained-cut fusion",
            plan_signature=self.topology.signature,
            topology_cache_hit=topology_cache_hit,
            structural_witness={
                "plan_version": "rrp-balanced-cut-v1",
                "dimension": self.dimension,
                "coupling_count": len(self.topology.edge_scopes),
                "quadrature_order": self.topology.order,
                "left_width": self.split,
                "right_width": self.dimension - self.split,
                "mass_elements": self.mass.size,
                "retained_working_elements": self.retained_elements,
                "parameter_values_in_plan_key": False,
                "autodiff": False,
                "jax_dependency": False,
            },
        )


@lru_cache(maxsize=128)
def _compiled_program(
    topology: RetainedTopology,
) -> CompiledRetainedReadoutProgram:
    return CompiledRetainedReadoutProgram(topology)


@lru_cache(maxsize=128)
def _balanced_cut_program(
    topology: RetainedTopology,
) -> BalancedRetainedCutProgram:
    return BalancedRetainedCutProgram(topology)


def compiled_retained_parameter_pullback(
    problem: PairwiseProblem,
    order: int,
) -> CompiledRetainedPullbackResult:
    """Execute a value-independent, topology-cached native program."""
    topology = retained_topology(problem, order)
    cache_before = _compiled_program.cache_info()
    program = _compiled_program(topology)
    cache_after = _compiled_program.cache_info()
    return program.run(
        _parameter_array(problem),
        topology_cache_hit=cache_after.hits > cache_before.hits,
    )


def balanced_cut_retained_parameter_pullback(
    problem: PairwiseProblem,
    order: int,
) -> CompiledRetainedPullbackResult:
    """Execute one exact balanced-cut dense readout program."""
    topology = retained_topology(problem, order)
    cache_before = _balanced_cut_program.cache_info()
    program = _balanced_cut_program(topology)
    cache_after = _balanced_cut_program.cache_info()
    return program.run(
        _parameter_array(problem),
        topology_cache_hit=cache_after.hits > cache_before.hits,
    )


def compiled_retained_parameter_pullback_batch(
    problems: Iterable[PairwiseProblem],
    order: int,
) -> list[CompiledRetainedPullbackResult]:
    """Reuse one finite structural program for many coefficient records."""
    problem_list = list(problems)
    if not problem_list:
        return []
    topology = retained_topology(problem_list[0], order)
    if any(
        retained_topology(problem, order) != topology
        for problem in problem_list[1:]
    ):
        raise ValueError("all batch members must share one retained topology")
    cache_before = _compiled_program.cache_info()
    program = _compiled_program(topology)
    cache_after = _compiled_program.cache_info()
    initial_hit = cache_after.hits > cache_before.hits
    return [
        program.run(
            _parameter_array(problem),
            topology_cache_hit=initial_hit or index > 0,
        )
        for index, problem in enumerate(problem_list)
    ]


def balanced_cut_retained_parameter_pullback_batch(
    problems: Iterable[PairwiseProblem],
    order: int,
) -> list[CompiledRetainedPullbackResult]:
    """Reuse one balanced retained boundary for many coefficient records."""
    problem_list = list(problems)
    if not problem_list:
        return []
    topology = retained_topology(problem_list[0], order)
    if any(
        retained_topology(problem, order) != topology
        for problem in problem_list[1:]
    ):
        raise ValueError("all batch members must share one retained topology")
    cache_before = _balanced_cut_program.cache_info()
    program = _balanced_cut_program(topology)
    cache_after = _balanced_cut_program.cache_info()
    initial_hit = cache_after.hits > cache_before.hits
    return [
        program.run(
            _parameter_array(problem),
            topology_cache_hit=initial_hit or index > 0,
        )
        for index, problem in enumerate(problem_list)
    ]


def adaptive_retained_parameter_pullback(
    problem: PairwiseProblem,
    order: int,
) -> CompiledRetainedPullbackResult:
    """Select a native execution substrate from declared graph density."""
    if len(problem.couplings) < 2 * problem.dimension:
        return compiled_retained_parameter_pullback(problem, order)
    if order**problem.dimension <= 524_288:
        return balanced_cut_retained_parameter_pullback(problem, order)
    result = compile_retained_readout_pullback(problem, order)
    pullback = result.retained_readout_pullback
    if pullback is None:
        raise AssertionError("native dense pullback was not produced")
    return CompiledRetainedPullbackResult(
        value=result.value,
        partition_gradients=[
            *pullback.partition_linear_gradients,
            *pullback.partition_coupling_gradients,
        ],
        log_partition_gradients=[
            *pullback.log_partition_linear_gradients,
            *pullback.log_partition_coupling_gradients,
        ],
        compile_plus_first_execution_seconds=0.0,
        strategy="NumPy retained-basis dense readout",
        plan_signature=retained_topology(problem, order).signature,
        topology_cache_hit=False,
        structural_witness={
            "plan_version": "rrp-dense-readout-v1",
            "dimension": problem.dimension,
            "coupling_count": len(problem.couplings),
            "quadrature_order": order,
            "parameter_values_in_plan_key": False,
            "autodiff": False,
            "jax_dependency": False,
        },
    )
