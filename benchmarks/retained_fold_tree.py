#!/usr/bin/env python3
"""benchmarks/retained_fold_tree.py — the native Retained Fold Tree (RFT) executor.

Written for this repository from its own retained-readout primitives — NOT a wrapper around a
junction-tree or an autodiff package. It reuses the declared objects of
`coupled_nd_retained_compiler` (the `PairwiseProblem`, the min-fill closure order, the finite
`build_factors` bucket) and adds two native passes:

  * an UPWARD FTCC fold — bucket elimination that closes each internal distinction into a retained
    boundary record `m_v(x_{B_v}) = Σ_{x_v} ∏_{f∈F_v} f`;
  * a DOWNWARD terminal-relevance UNFOLD — the retained environment of each closed distinction is
    reformed from the relevance arriving from its consumer, and every declared sufficient statistic
    (axis first moment `μ_i`, coupling cross moment `χ_e`) is read exactly where its record is
    consumed, in ONE backward pass — Retained Readout Pullback (RRP).

From `Z`, `{μ_i}`, `{χ_e}` the exponential-family identities give every parameter gradient exactly:
    ∂Z/∂α_i = −Z μ_i,   ∂logZ/∂α_i = −μ_i,   ∂Z/∂β_e = −Z χ_e,   ∂logZ/∂β_e = −χ_e.

Tier: the executor and its benchmark are `finite_diagnostic` (they reproduce the reference contraction
and central finite differences to a declared tolerance); the FTCC fold pattern they instantiate is the
`Th_coqc` core. No continuum, no autodiff tape, no clique calibration.
"""
from __future__ import annotations

import itertools
import time
from dataclasses import dataclass, field

try:
    from benchmarks.coupled_nd_retained_compiler import (
        PairwiseProblem, Factor, build_factors, min_fill_order,
    )
    from benchmarks.direct_nd_work_tokens import quadrature_rule
except ModuleNotFoundError:  # direct script execution from inside benchmarks/
    from coupled_nd_retained_compiler import (
        PairwiseProblem, Factor, build_factors, min_fill_order,
    )
    from direct_nd_work_tokens import quadrature_rule


# ---------------------------------------------------------------- the closure plan (value-free) ----
@dataclass(frozen=True)
class ClosureRecord:
    """One closed distinction: eliminate `axis`, consuming `input_factor_ids`, producing the boundary
    record `output_factor_id` over `output_scope`. `joined_scope` = output_scope ∪ {axis}."""
    axis: int
    input_factor_ids: tuple[int, ...]
    joined_scope: tuple[int, ...]
    output_scope: tuple[int, ...]
    output_factor_id: int

    @property
    def axes(self) -> tuple[int, ...]:
        return (self.axis,)


@dataclass(frozen=True)
class ClosureProgram:
    closures: tuple[ClosureRecord, ...]
    terminal_factor_ids: tuple[int, ...]
    factor_scopes: tuple[tuple[int, ...], ...]
    dimension: int
    coupling_count: int
    order: int


def _plan_retained_closure_program(problem: PairwiseProblem, order: int,
                                   cache_size: int = 16_384) -> ClosureProgram:
    """Compile the value-INDEPENDENT closure lineage from the coupling graph and the min-fill order.

    Factor ids are contiguous: unary `0..d-1`, couplings `d..d+|E|-1`, then one produced record per
    closure. `cache_size` is accepted for signature compatibility with the compiled executor (it bounds
    the compiled fusion record); the pure plan does not fuse. No coefficient value enters this plan."""
    dimension = problem.dimension
    coupling_count = len(problem.couplings)
    # scope table, in the same order build_factors emits: unary first, then couplings
    scopes: list[tuple[int, ...]] = [(axis,) for axis in range(dimension)]
    scopes += [(left, right) for left, right, _s in problem.couplings]
    original_count = len(scopes)

    elimination_order, _width = min_fill_order(problem)
    # active factor ids per bucket simulation
    active: list[int] = list(range(original_count))
    closures: list[ClosureRecord] = []
    next_id = original_count

    for axis in elimination_order:
        bucket = [fid for fid in active if axis in scopes[fid]]
        if not bucket:
            continue
        active = [fid for fid in active if axis not in scopes[fid]]
        joined = tuple(sorted({a for fid in bucket for a in scopes[fid]}))
        output_scope = tuple(a for a in joined if a != axis)
        output_id = next_id
        next_id += 1
        scopes.append(output_scope)
        closures.append(ClosureRecord(axis, tuple(bucket), joined, output_scope, output_id))
        active.append(output_id)

    terminals = tuple(fid for fid in active if len(scopes[fid]) == 0)
    return ClosureProgram(tuple(closures), terminals, tuple(scopes),
                          dimension, coupling_count, order)


# ---------------------------------------------------------------- the RRP result ----
@dataclass(frozen=True)
class RetainedReadoutPullback:
    coupling_cross_moments: list[float]
    partition_linear_gradients: list[float]
    partition_coupling_gradients: list[float]
    log_partition_linear_gradients: list[float]
    log_partition_coupling_gradients: list[float]
    pullback_work_elements: int
    retained_basis_elements: int


@dataclass(frozen=True)
class RetainedFoldTreeResult:
    value: float
    axis_first_moments: list[float]
    retained_readout_pullback: RetainedReadoutPullback
    closure_count: int = 0
    elapsed_seconds: float = 0.0


def compile_retained_readout_pullback(problem: PairwiseProblem, order: int) -> RetainedFoldTreeResult:
    """One upward FTCC fold + one downward relevance unfold → Z, all axis moments, all coupling cross
    moments, and every parameter gradient, with no autodiff tape and no full q^d tensor."""
    started = time.perf_counter()
    factors, nodes, _counter = build_factors(problem, order)
    q = len(nodes)
    dimension = problem.dimension
    couplings = problem.couplings
    plan = _plan_retained_closure_program(problem, order)
    original_count = dimension + len(couplings)

    # value store: factor id -> Factor(scope, values)
    store: dict[int, Factor] = {i: factors[i] for i in range(original_count)}
    pullback_work = 0
    retained_basis = 0

    # ---- UPWARD FOLD: close each distinction into its boundary record ----
    for c in plan.closures:
        bucket = [store[fid] for fid in c.input_factor_ids]
        out_scope = c.output_scope
        out_values: dict[tuple[int, ...], float] = {}
        for out_idx in itertools.product(range(q), repeat=len(out_scope)):
            assign = dict(zip(out_scope, out_idx))
            total = 0.0
            for e in range(q):
                assign[c.axis] = e
                product = 1.0
                for f in bucket:
                    product *= f.values[tuple(assign[a] for a in f.scope)]
                total += product
            out_values[out_idx] = total
        store[c.output_factor_id] = Factor(out_scope, out_values)
        retained_basis += len(out_values)

    partition = 1.0
    for tid in plan.terminal_factor_ids:
        partition *= store[tid].values[()]

    # ---- DOWNWARD UNFOLD: relevance → local environment → declared statistics ----
    context: dict[int, dict[tuple[int, ...], float]] = {fid: {} for fid in store}
    # terminal relevance = product of the OTHER terminal scalars (so value·relevance = Z)
    for tid in plan.terminal_factor_ids:
        other = 1.0
        for o in plan.terminal_factor_ids:
            if o != tid:
                other *= store[o].values[()]
        context[tid][()] = other

    axis_num = [0.0] * dimension
    coupling_num = [0.0] * len(couplings)
    pair_edge = {dimension + e: e for e in range(len(couplings))}

    for c in reversed(plan.closures):
        out_ctx = context[c.output_factor_id]
        bucket = [(fid, store[fid]) for fid in c.input_factor_ids]
        for j_idx in itertools.product(range(q), repeat=len(c.joined_scope)):
            assign = dict(zip(c.joined_scope, j_idx))
            a_out = out_ctx.get(tuple(assign[a] for a in c.output_scope), 0.0)
            if a_out == 0.0:
                continue
            product = 1.0
            for _fid, f in bucket:
                product *= f.values[tuple(assign[a] for a in f.scope)]
            belief = product * a_out
            pullback_work += 1
            v = c.axis
            axis_num[v] += nodes[assign[v]] * belief
            for fid, f in bucket:
                if fid in pair_edge:                       # read the coupling cross moment here
                    i, j = f.scope
                    coupling_num[pair_edge[fid]] += nodes[assign[i]] * nodes[assign[j]] * belief
                if fid >= original_count:                  # propagate relevance to a produced child
                    g_key = tuple(assign[a] for a in f.scope)
                    gval = f.values[g_key]
                    context[fid][g_key] = context[fid].get(g_key, 0.0) + belief / gval

    axis_moments = [axis_num[i] / partition for i in range(dimension)]
    coupling_moments = [coupling_num[e] / partition for e in range(len(couplings))]

    pullback = RetainedReadoutPullback(
        coupling_cross_moments=coupling_moments,
        partition_linear_gradients=[-partition * m for m in axis_moments],
        partition_coupling_gradients=[-partition * m for m in coupling_moments],
        log_partition_linear_gradients=[-m for m in axis_moments],
        log_partition_coupling_gradients=[-m for m in coupling_moments],
        pullback_work_elements=pullback_work,
        retained_basis_elements=retained_basis,
    )
    return RetainedFoldTreeResult(
        value=partition,
        axis_first_moments=axis_moments,
        retained_readout_pullback=pullback,
        closure_count=len(plan.closures),
        elapsed_seconds=time.perf_counter() - started,
    )


# ---------------------------------------------------------------- reference (for the benchmark) ----
def reference_readouts(problem: PairwiseProblem, order: int):
    """An INDEPENDENT reference for the RFT outputs: Z and every moment by the tilted-factor
    contraction (the repeated-retained-contraction stage), reusing the elimination order but NEVER the
    RFT downward pass — so agreement is a genuine cross-check, not a tautology."""
    from math import isclose  # noqa: F401 (documentation of intent)
    factors, nodes, _c = build_factors(problem, order)
    q = len(nodes)
    elim, _w = min_fill_order(problem)

    def contract(fs):
        active = list(fs)
        for axis in elim:
            bucket = [f for f in active if axis in f.scope]
            active = [f for f in active if axis not in f.scope]
            if not bucket:
                continue
            joined = sorted({a for f in bucket for a in f.scope})
            out_scope = tuple(a for a in joined if a != axis)
            out_vals = {}
            for out_idx in itertools.product(range(q), repeat=len(out_scope)):
                assign = dict(zip(out_scope, out_idx))
                s = 0.0
                for e in range(q):
                    assign[axis] = e
                    p = 1.0
                    for f in bucket:
                        p *= f.values[tuple(assign[a] for a in f.scope)]
                    s += p
                out_vals[out_idx] = s
            active.append(Factor(out_scope, out_vals))
        z = 1.0
        for f in active:
            z *= f.values[()]
        return z

    Z = contract(factors)
    # axis moment: tilt the unary factor by the node value
    axis_moments = []
    for axis in range(problem.dimension):
        tilted = []
        done = False
        for f in factors:
            if f.scope == (axis,) and not done:
                tilted.append(Factor(f.scope, {k: v * nodes[k[0]] for k, v in f.values.items()}))
                done = True
            else:
                tilted.append(f)
        axis_moments.append(contract(tilted) / Z)
    # coupling moment: tilt the pair factor by x_i x_j
    coupling_moments = []
    for (i, j, _s) in couplings_iter(problem):
        tilted = []
        done = False
        for f in factors:
            if f.scope == (i, j) and not done:
                tilted.append(Factor(f.scope, {k: v * nodes[k[0]] * nodes[k[1]] for k, v in f.values.items()}))
                done = True
            else:
                tilted.append(f)
        coupling_moments.append(contract(tilted) / Z)
    return Z, axis_moments, coupling_moments


def couplings_iter(problem: PairwiseProblem):
    for left, right, strength in problem.couplings:
        yield left, right, strength


def log_partition(problem: PairwiseProblem, order: int) -> float:
    """log Z, used by the finite-difference gradient check in the benchmark."""
    import math
    z, _m, _c = reference_readouts(problem, order)
    return math.log(z)


if __name__ == "__main__":
    from coupled_nd_retained_compiler import default_problem
    prob = default_problem(7)
    res = compile_retained_readout_pullback(prob, 4)
    Zr, am, cm = reference_readouts(prob, 4)
    print(f"Z            RFT={res.value:.12f}  ref={Zr:.12f}  Δ={abs(res.value-Zr):.2e}")
    print(f"axis moments max Δ = {max(abs(a-b) for a,b in zip(res.axis_first_moments, am)):.2e}")
    print(f"coupling     max Δ = {max(abs(a-b) for a,b in zip(res.retained_readout_pullback.coupling_cross_moments, cm)):.2e}")
    print(f"closures={res.closure_count}  pullback_work={res.retained_readout_pullback.pullback_work_elements}")
