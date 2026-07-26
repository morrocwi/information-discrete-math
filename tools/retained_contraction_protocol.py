#!/usr/bin/env python3
"""Retained Contraction Protocol (RCP).

RCP wraps a finite factor contraction with:

* a declared resolution, output boundary, tolerance, and resource budget;
* an admissibility check for the elimination path;
* a replayable path/work/peak-retained plan before execution; and
* a fail-closed preservation certificate after execution.

The module does not claim a new contraction-path optimizer.  It specifies the
information contract around an optimizer or executor such as min-fill,
variable elimination, ``einsum``, or ``opt_einsum``.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Iterable, Sequence

try:
    from tools.idm_discipline import ACCEPT, BLOCK, HOLD, Verdict
except ModuleNotFoundError:  # direct execution: tools/ is sys.path[0]
    from idm_discipline import ACCEPT, BLOCK, HOLD, Verdict


@dataclass(frozen=True)
class RCPDeclaration:
    """Everything that must be fixed before contraction begins."""

    resolution_lambda: str
    tolerance: float
    axis_sizes: tuple[tuple[int, int], ...]
    boundary_axes: tuple[int, ...]
    output_names: tuple[str, ...]
    max_work_tokens: int
    max_peak_elements: int
    query_strategy: str = "declared_terminal_readouts"
    arithmetic: str = "binary64"
    tier: str = "finite_diagnostic"


@dataclass(frozen=True)
class RetainedFactor:
    """A finite local record and the distinctions to which it is coupled."""

    name: str
    scope: tuple[int, ...]


@dataclass(frozen=True)
class EliminationStep:
    axis: int
    input_factors: tuple[str, ...]
    joined_scope: tuple[int, ...]
    output_scope: tuple[int, ...]
    output_elements: int
    multiply_tokens: int
    add_tokens: int


@dataclass(frozen=True)
class ContractionPlan:
    elimination_order: tuple[int, ...]
    steps: tuple[EliminationStep, ...]
    multiply_tokens_per_execution: int
    add_tokens_per_execution: int
    work_tokens_per_execution: int
    peak_retained_elements: int
    peak_retained_rank: int


@dataclass(frozen=True)
class PreflightCertificate:
    protocol: str
    declaration: RCPDeclaration
    factors: tuple[RetainedFactor, ...]
    plan: ContractionPlan
    executions: int
    fixed_work_tokens: int
    planned_work_tokens: int
    lineage_digest: str


@dataclass(frozen=True)
class PreservationCertificate:
    protocol: str
    declaration: RCPDeclaration
    lineage_digest: str
    elimination_order: tuple[int, ...]
    output_names: tuple[str, ...]
    readout: tuple[float, ...]
    witness_readout: tuple[float, ...]
    witness_method: str
    absolute_differences: tuple[float, ...]
    maximum_absolute_difference: float
    tolerance: float
    planned_work_tokens: int
    measured_work_tokens: int
    measured_work_by_op: tuple[tuple[str, int], ...]
    peak_retained_elements: int
    tier: str


def _product(values: Iterable[int]) -> int:
    result = 1
    for value in values:
        result *= value
    return result


def _lineage_digest(
    declaration: RCPDeclaration,
    factors: Sequence[RetainedFactor],
    plan: ContractionPlan,
    executions: int,
    fixed_work_tokens: int,
    planned_work_tokens: int,
) -> str:
    payload = {
        "protocol": "RCP/1.0",
        "declaration": asdict(declaration),
        "factors": [asdict(factor) for factor in factors],
        "plan": asdict(plan),
        "executions": executions,
        "fixed_work_tokens": fixed_work_tokens,
        "planned_work_tokens": planned_work_tokens,
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _block(reason: str) -> Verdict:
    return Verdict(BLOCK, reason=reason)


def plan_contraction(
    declaration: RCPDeclaration,
    factors: Sequence[RetainedFactor],
    elimination_order: Sequence[int],
) -> Verdict:
    """Validate and compile an elimination path without executing arithmetic."""

    if (
        not isinstance(declaration.resolution_lambda, str)
        or not declaration.resolution_lambda.strip()
    ):
        return _block("resolution λ is undeclared")
    if not (
        isinstance(declaration.tolerance, (int, float))
        and not isinstance(declaration.tolerance, bool)
        and math.isfinite(declaration.tolerance)
        and declaration.tolerance > 0
    ):
        return _block("tolerance must be a declared positive finite number")
    if any(
        not isinstance(value, int)
        or isinstance(value, bool)
        or value <= 0
        for value in (
            declaration.max_work_tokens,
            declaration.max_peak_elements,
        )
    ):
        return _block("resource budgets must be positive")
    if not declaration.output_names:
        return _block("at least one terminal readout must be declared")
    if any(
        not isinstance(name, str) or not name.strip()
        for name in declaration.output_names
    ):
        return _block("terminal readout names must be non-empty strings")
    if (
        not isinstance(declaration.query_strategy, str)
        or not declaration.query_strategy.strip()
    ):
        return _block("terminal query strategy is undeclared")
    if len(set(declaration.output_names)) != len(declaration.output_names):
        return _block("terminal readout names must be unique")
    if not factors:
        return _block("at least one retained factor is required")
    if any(
        not isinstance(factor.name, str) or not factor.name.strip()
        for factor in factors
    ):
        return _block("retained factor names must be non-empty strings")
    if len({factor.name for factor in factors}) != len(factors):
        return _block("retained factor names must be unique")

    try:
        axis_sizes = dict(declaration.axis_sizes)
    except (TypeError, ValueError):
        return _block("axis declarations are malformed")
    if len(axis_sizes) != len(declaration.axis_sizes):
        return _block("axis declarations must be unique")
    if any(
        not isinstance(axis, int)
        or isinstance(axis, bool)
        or not isinstance(size, int)
        or isinstance(size, bool)
        or size <= 0
        for axis, size in declaration.axis_sizes
    ):
        return _block("each axis must have an integer name and positive finite size")

    known_axes = set(axis_sizes)
    factor_axes: set[int] = set()
    for factor in factors:
        if len(set(factor.scope)) != len(factor.scope):
            return _block(f"factor {factor.name!r} repeats an axis")
        unknown = set(factor.scope) - known_axes
        if unknown:
            return _block(
                f"factor {factor.name!r} uses undeclared axes {sorted(unknown)}"
            )
        factor_axes.update(factor.scope)

    boundary_axes = set(declaration.boundary_axes)
    if len(boundary_axes) != len(declaration.boundary_axes):
        return _block("boundary axes must be unique")
    if not boundary_axes <= factor_axes:
        return _block(
            f"boundary contains absent axes {sorted(boundary_axes - factor_axes)}"
        )

    internal_axes = factor_axes - boundary_axes
    order = tuple(elimination_order)
    if any(
        not isinstance(axis, int) or isinstance(axis, bool)
        for axis in order
    ):
        return _block("elimination path axes must be integers")
    if len(set(order)) != len(order):
        return _block("elimination path repeats an axis")
    if set(order) != internal_axes:
        missing = sorted(internal_axes - set(order))
        forbidden = sorted(set(order) - internal_axes)
        return _block(
            "elimination path does not match the internal distinctions: "
            f"missing={missing}, forbidden={forbidden}"
        )

    active: list[tuple[str, tuple[int, ...]]] = [
        (factor.name, factor.scope) for factor in factors
    ]
    peak_elements = max(
        _product(axis_sizes[axis] for axis in factor.scope)
        for factor in factors
    )
    peak_rank = max(len(factor.scope) for factor in factors)
    multiply_tokens = 0
    add_tokens = 0
    steps: list[EliminationStep] = []

    for step_index, axis in enumerate(order):
        bucket = [item for item in active if axis in item[1]]
        if not bucket:
            return _block(f"axis {axis} has no active retained coupling")
        active = [item for item in active if axis not in item[1]]
        joined_scope = tuple(
            sorted({item for _name, scope in bucket for item in scope})
        )
        output_scope = tuple(item for item in joined_scope if item != axis)
        joined_elements = _product(axis_sizes[item] for item in joined_scope)
        output_elements = _product(axis_sizes[item] for item in output_scope)
        step_multiply = joined_elements * len(bucket)
        step_add = joined_elements
        multiply_tokens += step_multiply
        add_tokens += step_add
        peak_elements = max(peak_elements, output_elements)
        peak_rank = max(peak_rank, len(output_scope))
        generated_name = f"rcp_step_{step_index}_after_axis_{axis}"
        active.append((generated_name, output_scope))
        steps.append(
            EliminationStep(
                axis=axis,
                input_factors=tuple(name for name, _scope in bucket),
                joined_scope=joined_scope,
                output_scope=output_scope,
                output_elements=output_elements,
                multiply_tokens=step_multiply,
                add_tokens=step_add,
            )
        )

    remaining_axes = {axis for _name, scope in active for axis in scope}
    if remaining_axes != boundary_axes:
        return _block(
            "compiled boundary differs from the declared boundary: "
            f"compiled={sorted(remaining_axes)}, declared={sorted(boundary_axes)}"
        )

    # The low-level executor multiplies all remaining scalar/boundary factors.
    multiply_tokens += len(active)
    plan = ContractionPlan(
        elimination_order=order,
        steps=tuple(steps),
        multiply_tokens_per_execution=multiply_tokens,
        add_tokens_per_execution=add_tokens,
        work_tokens_per_execution=multiply_tokens + add_tokens,
        peak_retained_elements=peak_elements,
        peak_retained_rank=peak_rank,
    )
    return Verdict(ACCEPT, value=plan, reason="contraction path is admissible")


def preflight_contraction(
    declaration: RCPDeclaration,
    factors: Sequence[RetainedFactor],
    elimination_order: Sequence[int],
    *,
    executions: int = 1,
    fixed_work_tokens: int = 0,
) -> Verdict:
    """Fail closed before tick 0 if path or dominant resources are inadmissible."""

    if (
        not isinstance(executions, int)
        or isinstance(executions, bool)
        or executions <= 0
        or not isinstance(fixed_work_tokens, int)
        or isinstance(fixed_work_tokens, bool)
        or fixed_work_tokens < 0
    ):
        return _block("executions and fixed work must be finite non-negative integers")

    planned = plan_contraction(declaration, factors, elimination_order)
    if planned.status != ACCEPT:
        return planned
    plan = planned.value
    assert isinstance(plan, ContractionPlan)

    planned_work = fixed_work_tokens + executions * plan.work_tokens_per_execution
    preflight = PreflightCertificate(
        protocol="RCP/1.0",
        declaration=declaration,
        factors=tuple(factors),
        plan=plan,
        executions=executions,
        fixed_work_tokens=fixed_work_tokens,
        planned_work_tokens=planned_work,
        lineage_digest=_lineage_digest(
            declaration,
            factors,
            plan,
            executions,
            fixed_work_tokens,
            planned_work,
        ),
    )
    if plan.peak_retained_elements > declaration.max_peak_elements:
        return Verdict(
            BLOCK,
            value=preflight,
            reason=(
                f"planned peak {plan.peak_retained_elements} elements exceeds "
                f"budget {declaration.max_peak_elements}; execution refused"
            ),
        )
    if planned_work > declaration.max_work_tokens:
        return Verdict(
            BLOCK,
            value=preflight,
            reason=(
                f"planned work {planned_work} tokens exceeds budget "
                f"{declaration.max_work_tokens}; execution refused"
            ),
        )
    return Verdict(
        ACCEPT,
        value=preflight,
        reason=(
            f"admissible before tick 0: work {planned_work}/"
            f"{declaration.max_work_tokens}, peak "
            f"{plan.peak_retained_elements}/{declaration.max_peak_elements}"
        ),
    )


def certify_contraction(
    preflight: Verdict,
    readout: Sequence[float],
    witness_readout: Sequence[float] | None,
    *,
    measured_work_tokens: int,
    witness_method: str,
    measured_work_by_op: dict[str, int] | None = None,
) -> Verdict:
    """Issue ACCEPT only when the declared terminal readout is preserved."""

    if preflight.status != ACCEPT:
        return Verdict(
            BLOCK,
            value=preflight.value,
            reason=f"execution has no accepted preflight: {preflight.reason}",
        )
    certificate = preflight.value
    if not isinstance(certificate, PreflightCertificate):
        return _block("preflight payload is not an RCP certificate")
    declaration = certificate.declaration

    if (
        not isinstance(measured_work_tokens, int)
        or isinstance(measured_work_tokens, bool)
        or measured_work_tokens < 0
    ):
        return _block("measured work ledger is unreadable")
    if measured_work_tokens > declaration.max_work_tokens:
        return Verdict(
            BLOCK,
            value=certificate,
            reason=(
                f"measured work {measured_work_tokens} exceeds declared budget "
                f"{declaration.max_work_tokens}"
            ),
        )
    if measured_work_tokens != certificate.planned_work_tokens:
        return Verdict(
            HOLD,
            value=certificate,
            reason=(
                "work ledger differs from the preflight plan: "
                f"planned={certificate.planned_work_tokens}, "
                f"measured={measured_work_tokens}"
            ),
        )
    if measured_work_by_op is not None and not isinstance(
        measured_work_by_op,
        dict,
    ):
        return _block("measured operation ledger must be a mapping")
    work_by_op = tuple(sorted((measured_work_by_op or {}).items()))
    if any(
        not isinstance(name, str)
        or not name
        or not isinstance(count, int)
        or isinstance(count, bool)
        or count < 0
        for name, count in work_by_op
    ):
        return _block("measured operation ledger is unreadable")
    if work_by_op and sum(count for _name, count in work_by_op) != measured_work_tokens:
        return Verdict(
            HOLD,
            value=certificate,
            reason=(
                "operation ledger does not sum to measured work: "
                f"by_op={sum(count for _name, count in work_by_op)}, "
                f"measured={measured_work_tokens}"
            ),
        )

    try:
        output = tuple(float(value) for value in readout)
    except (TypeError, ValueError, OverflowError):
        return _block("terminal readout cannot be translated to finite numbers")
    if len(output) != len(declaration.output_names):
        return _block(
            f"terminal boundary declared {len(declaration.output_names)} readouts "
            f"but execution returned {len(output)}"
        )
    if not all(math.isfinite(value) for value in output):
        return Verdict(HOLD, value=certificate, reason="terminal readout is non-finite")
    if witness_readout is None:
        return Verdict(
            HOLD,
            value=certificate,
            reason="no independent preservation witness was supplied",
        )

    try:
        witness = tuple(float(value) for value in witness_readout)
    except (TypeError, ValueError, OverflowError):
        return _block("witness readout cannot be translated to finite numbers")
    if len(witness) != len(output):
        return _block(
            f"witness has {len(witness)} readouts but terminal boundary has {len(output)}"
        )
    if not all(math.isfinite(value) for value in witness):
        return Verdict(HOLD, value=certificate, reason="witness readout is non-finite")
    if not isinstance(witness_method, str) or not witness_method.strip():
        return _block("preservation witness method is undeclared")

    differences = tuple(
        abs(left - right) for left, right in zip(output, witness)
    )
    maximum_difference = max(differences, default=0.0)
    preservation = PreservationCertificate(
        protocol=certificate.protocol,
        declaration=declaration,
        lineage_digest=certificate.lineage_digest,
        elimination_order=certificate.plan.elimination_order,
        output_names=declaration.output_names,
        readout=output,
        witness_readout=witness,
        witness_method=witness_method,
        absolute_differences=differences,
        maximum_absolute_difference=maximum_difference,
        tolerance=declaration.tolerance,
        planned_work_tokens=certificate.planned_work_tokens,
        measured_work_tokens=measured_work_tokens,
        measured_work_by_op=work_by_op,
        peak_retained_elements=certificate.plan.peak_retained_elements,
        tier=declaration.tier,
    )
    if maximum_difference > declaration.tolerance:
        return Verdict(
            HOLD,
            value=preservation,
            reason=(
                f"preservation difference {maximum_difference:.6g} exceeds "
                f"tolerance {declaration.tolerance:.6g}"
            ),
        )
    return Verdict(
        ACCEPT,
        value=preservation,
        reason=(
            f"terminal readout preserved: maximum difference "
            f"{maximum_difference:.6g} <= {declaration.tolerance:.6g}"
        ),
    )


def verdict_report(verdict: Verdict) -> dict[str, object]:
    """Serialize a verdict together with its replayable evidence."""

    value = (
        asdict(verdict.value)
        if hasattr(verdict.value, "__dataclass_fields__")
        else verdict.value
    )
    return {
        "status": verdict.status,
        "reason": verdict.reason,
        "certificate": value,
    }


if __name__ == "__main__":
    declaration = RCPDeclaration(
        resolution_lambda="2 states per retained axis",
        tolerance=1e-12,
        axis_sizes=((0, 2), (1, 2)),
        boundary_axes=(),
        output_names=("partition",),
        max_work_tokens=100,
        max_peak_elements=16,
    )
    factors = (
        RetainedFactor("left", (0,)),
        RetainedFactor("coupling", (0, 1)),
        RetainedFactor("right", (1,)),
    )
    preflight = preflight_contraction(
        declaration,
        factors,
        (0, 1),
    )
    assert preflight.status == ACCEPT
    planned = preflight.value
    assert isinstance(planned, PreflightCertificate)
    certified = certify_contraction(
        preflight,
        (0.75,),
        (0.75,),
        measured_work_tokens=planned.planned_work_tokens,
        witness_method="independent finite enumeration",
    )
    assert certified.status == ACCEPT
    print("RCP self-check OK — preflight · lineage · budget · preservation · fail-closed verdict")
