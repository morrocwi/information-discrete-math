#!/usr/bin/env python3
"""RCP-Energy: exact finite planning over retained energy records.

Nothing in this module assumes continuous time, a real-valued state space, an
infinite penalty, or an external optimization oracle.  A site is a finite tape
of supplied records.  At tick ``n`` the reader sees integer energy, thermal,
storage, and source quanta.  An inadmissible transition is absent rather than
assigned an infinite cost.

Histories ending in the same exposed state are reader-equivalent.  The
Retained Burden Algebra keeps the representative with the least declared
finite burden.  This is the energy-planning extension of the Retained
Contraction Protocol: declare -> preflight -> execute -> replay -> witness ->
ACCEPT/HOLD/BLOCK.

Tier: ``finite_diagnostic``.  The executable uses exact ``Fraction`` arithmetic
and exhaustive finite witnesses on small instances.  A general Coq
minimality/preservation theorem remains ``Th_coqc-elig``.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from itertools import product
from typing import Iterable, Sequence

try:
    from tools.idm_discipline import ACCEPT, BLOCK, HOLD, Verdict
    from tools.retained_burden_algebra import BurdenOrder, RetainedBurden
except ModuleNotFoundError:  # direct execution from tools/
    from idm_discipline import ACCEPT, BLOCK, HOLD, Verdict
    from retained_burden_algebra import BurdenOrder, RetainedBurden


BURDEN_ORDER = BurdenOrder(
    (
        "diesel_quanta",
        "grid_quanta",
        "source_cost",
        "battery_wear_quanta",
        "curtailed_quanta",
        "peak_grid_quanta",
    ),
    ("sum", "sum", "sum", "sum", "sum", "max"),
)


@dataclass(frozen=True, order=True)
class EnergyState:
    """Everything from the past that can change a future readout."""

    storage_quanta: int
    thermal_quanta: int


@dataclass(frozen=True, order=True)
class EnergyAction:
    """A finite choice at one tick.

    ``battery_level < 0`` charges; ``battery_level > 0`` discharges.
    """

    cooling_level: int
    battery_level: int


@dataclass(frozen=True)
class EnergyStep:
    tick: int
    before: EnergyState
    action: EnergyAction
    after: EnergyState
    base_load_quanta: int
    cooling_quanta: int
    solar_quanta: int
    charge_input_quanta: int
    discharge_output_quanta: int
    grid_quanta: int
    diesel_quanta: int
    curtailed_quanta: int
    burden: RetainedBurden


@dataclass(frozen=True)
class EnergyProblem:
    """A fully finite energy tape and its local transition declarations."""

    name: str
    resolution_lambda: str
    tick_minutes: int
    energy_quantum_kwh: Fraction
    base_load: tuple[int, ...]
    solar_supply: tuple[int, ...]
    thermal_ingress: tuple[int, ...]
    grid_capacity: tuple[int, ...]
    grid_price: tuple[Fraction, ...]
    initial_storage: int
    storage_min: int
    storage_max: int
    initial_thermal: int
    thermal_min: int
    thermal_max: int
    cooling_levels: tuple[int, ...]
    cooling_energy_per_level: int
    cooling_effect_per_level: int
    battery_levels: tuple[int, ...]
    charge_input_per_level: int
    charge_storage_per_level: int
    discharge_storage_per_level: int
    discharge_output_per_level: int
    diesel_max_per_tick: int
    diesel_price: Fraction
    battery_wear_price: Fraction

    @property
    def ticks(self) -> int:
        return len(self.base_load)

    @property
    def actions(self) -> tuple[EnergyAction, ...]:
        return tuple(
            EnergyAction(cooling, battery)
            for cooling, battery in product(
                self.cooling_levels,
                self.battery_levels,
            )
        )


@dataclass(frozen=True)
class EnergyDeclaration:
    """Resource and terminal boundaries fixed before tick zero."""

    protocol: str
    output_names: tuple[str, ...]
    priority_names: tuple[str, ...]
    max_candidate_records: int
    max_retained_states: int
    max_work_tokens: int
    tier: str = "finite_diagnostic"


@dataclass(frozen=True)
class EnergyWorkPlan:
    state_bound: int
    action_count: int
    candidate_record_bound: int
    retained_state_bound: int
    work_token_bound: int


@dataclass(frozen=True)
class EnergyPreflight:
    protocol: str
    declaration: EnergyDeclaration
    problem_name: str
    ticks: int
    plan: EnergyWorkPlan
    lineage_digest: str


@dataclass(frozen=True)
class EnergyWorkLedger:
    candidate_records: int
    admissible_records: int
    burden_compositions: int
    retention_comparisons: int
    retention_writes: int
    backtrace_steps: int
    peak_retained_states: int

    @property
    def work_tokens(self) -> int:
        return (
            self.candidate_records
            + self.admissible_records
            + self.burden_compositions
            + self.retention_comparisons
            + self.retention_writes
            + self.backtrace_steps
        )


@dataclass(frozen=True)
class EnergyResult:
    protocol: str
    problem_name: str
    lineage_digest: str
    final_state: EnergyState
    burden: RetainedBurden
    steps: tuple[EnergyStep, ...]
    work: EnergyWorkLedger
    tier: str

    @property
    def priority_readout(self) -> tuple[Fraction, ...]:
        return self.burden.values

    @property
    def output_readout(self) -> tuple[Fraction, ...]:
        diesel, grid, source_cost, wear, curtailment, peak = self.burden.values
        return (
            diesel,
            grid,
            peak,
            source_cost,
            wear,
            curtailment,
            Fraction(self.final_state.storage_quanta),
            Fraction(self.final_state.thermal_quanta),
        )


@dataclass(frozen=True)
class EnergyCertificate:
    protocol: str
    problem_name: str
    lineage_digest: str
    output_names: tuple[str, ...]
    readout: tuple[Fraction, ...]
    witness_readout: tuple[Fraction, ...]
    witness_method: str
    replay_preserved: bool
    planned_candidate_bound: int
    measured_candidate_records: int
    planned_work_bound: int
    measured_work_tokens: int
    tier: str


def _fraction_text(value: Fraction) -> str:
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}"


def _problem_payload(problem: EnergyProblem) -> dict[str, object]:
    payload = asdict(problem)
    for key in ("energy_quantum_kwh", "diesel_price", "battery_wear_price"):
        payload[key] = _fraction_text(payload[key])
    payload["grid_price"] = [_fraction_text(value) for value in problem.grid_price]
    return payload


def _lineage_digest(
    declaration: EnergyDeclaration,
    problem: EnergyProblem,
    plan: EnergyWorkPlan,
) -> str:
    payload = {
        "protocol": declaration.protocol,
        "declaration": asdict(declaration),
        "problem": _problem_payload(problem),
        "plan": asdict(plan),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _block(reason: str, value: object = None) -> Verdict:
    return Verdict(BLOCK, value=value, reason=reason)


def _validate_nonnegative_ints(name: str, values: Iterable[int]) -> str | None:
    if any(
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
        for value in values
    ):
        return f"{name} must contain finite non-negative integer quanta"
    return None


def preflight_energy(
    declaration: EnergyDeclaration,
    problem: EnergyProblem,
) -> Verdict:
    """Compile a conservative resource bound before reading tick zero."""

    if declaration.protocol != "RCP-Energy/1.0":
        return _block("unknown retained-energy protocol")
    if problem.ticks <= 0:
        return _block("energy tape must retain at least one tick")
    if (
        not problem.name.strip()
        or not problem.resolution_lambda.strip()
        or problem.tick_minutes <= 0
        or problem.energy_quantum_kwh <= 0
    ):
        return _block("problem name and positive finite resolutions are required")
    lengths = {
        len(problem.base_load),
        len(problem.solar_supply),
        len(problem.thermal_ingress),
        len(problem.grid_capacity),
        len(problem.grid_price),
    }
    if lengths != {problem.ticks}:
        return _block("all supplied tapes must expose the same finite tick count")
    for name, values in (
        ("base_load", problem.base_load),
        ("solar_supply", problem.solar_supply),
        ("thermal_ingress", problem.thermal_ingress),
        ("grid_capacity", problem.grid_capacity),
    ):
        error = _validate_nonnegative_ints(name, values)
        if error:
            return _block(error)
    if any(Fraction(price) < 0 for price in problem.grid_price):
        return _block("grid price tape must be finite and non-negative")
    if problem.diesel_price < 0 or problem.battery_wear_price < 0:
        return _block("source prices must be finite and non-negative")
    if not (
        0 <= problem.storage_min <= problem.initial_storage <= problem.storage_max
    ):
        return _block("initial storage lies outside its retained boundary")
    if not (
        problem.thermal_min
        <= problem.initial_thermal
        <= problem.thermal_max
    ):
        return _block("initial thermal record lies outside its retained boundary")
    if (
        not problem.cooling_levels
        or not problem.battery_levels
        or len(set(problem.cooling_levels)) != len(problem.cooling_levels)
        or len(set(problem.battery_levels)) != len(problem.battery_levels)
    ):
        return _block("action alphabets must be non-empty finite distinctions")
    if any(level < 0 for level in problem.cooling_levels):
        return _block("cooling levels must be non-negative")
    if any(
        value <= 0
        for value in (
            problem.cooling_energy_per_level,
            problem.cooling_effect_per_level,
            problem.charge_input_per_level,
            problem.charge_storage_per_level,
            problem.discharge_storage_per_level,
            problem.discharge_output_per_level,
            problem.diesel_max_per_tick,
        )
    ):
        return _block("transition quanta must be positive finite integers")
    if declaration.output_names != (
        "diesel_quanta",
        "grid_quanta",
        "peak_grid_quanta",
        "source_cost",
        "battery_wear_quanta",
        "curtailed_quanta",
        "final_storage_quanta",
        "final_thermal_quanta",
    ):
        return _block("terminal energy boundary is incomplete or reordered")
    if declaration.priority_names != (
        "diesel_quanta",
        "grid_quanta",
        "source_cost",
        "battery_wear_quanta",
        "curtailed_quanta",
        "peak_grid_quanta",
    ):
        return _block("reader priority must be declared explicitly")
    if any(
        not isinstance(value, int)
        or isinstance(value, bool)
        or value <= 0
        for value in (
            declaration.max_candidate_records,
            declaration.max_retained_states,
            declaration.max_work_tokens,
        )
    ):
        return _block("resource budgets must be positive finite counts")

    storage_count = problem.storage_max - problem.storage_min + 1
    thermal_count = problem.thermal_max - problem.thermal_min + 1
    state_bound = storage_count * thermal_count
    action_count = len(problem.actions)
    candidate_bound = problem.ticks * state_bound * action_count
    # At most five ledger events per candidate plus one backtrace token/tick.
    work_bound = 5 * candidate_bound + problem.ticks
    plan = EnergyWorkPlan(
        state_bound=state_bound,
        action_count=action_count,
        candidate_record_bound=candidate_bound,
        retained_state_bound=state_bound,
        work_token_bound=work_bound,
    )
    preflight = EnergyPreflight(
        protocol=declaration.protocol,
        declaration=declaration,
        problem_name=problem.name,
        ticks=problem.ticks,
        plan=plan,
        lineage_digest=_lineage_digest(declaration, problem, plan),
    )
    if candidate_bound > declaration.max_candidate_records:
        return _block(
            f"candidate bound {candidate_bound} exceeds budget "
            f"{declaration.max_candidate_records}; execution refused",
            preflight,
        )
    if state_bound > declaration.max_retained_states:
        return _block(
            f"state bound {state_bound} exceeds budget "
            f"{declaration.max_retained_states}; execution refused",
            preflight,
        )
    if work_bound > declaration.max_work_tokens:
        return _block(
            f"work bound {work_bound} exceeds budget "
            f"{declaration.max_work_tokens}; execution refused",
            preflight,
        )
    return Verdict(
        ACCEPT,
        value=preflight,
        reason=(
            f"admissible before tick 0: candidates≤{candidate_bound}, "
            f"states≤{state_bound}, work≤{work_bound}"
        ),
    )


def transition(
    problem: EnergyProblem,
    tick: int,
    state: EnergyState,
    action: EnergyAction,
) -> EnergyStep | None:
    """Read one local transition; return absence when it is inadmissible."""

    if not 0 <= tick < problem.ticks:
        raise IndexError("tick outside the supplied finite tape")
    if action.cooling_level not in problem.cooling_levels:
        return None
    if action.battery_level not in problem.battery_levels:
        return None

    cooling_energy = (
        action.cooling_level * problem.cooling_energy_per_level
    )
    thermal_after = (
        state.thermal_quanta
        + problem.thermal_ingress[tick]
        - action.cooling_level * problem.cooling_effect_per_level
    )
    if not problem.thermal_min <= thermal_after <= problem.thermal_max:
        return None

    charge_input = 0
    discharge_output = 0
    storage_after = state.storage_quanta
    if action.battery_level < 0:
        level = -action.battery_level
        charge_input = level * problem.charge_input_per_level
        storage_after += level * problem.charge_storage_per_level
    elif action.battery_level > 0:
        level = action.battery_level
        discharge_output = level * problem.discharge_output_per_level
        storage_after -= level * problem.discharge_storage_per_level
    if not problem.storage_min <= storage_after <= problem.storage_max:
        return None

    required = problem.base_load[tick] + cooling_energy + charge_input
    retained_supply = problem.solar_supply[tick] + discharge_output
    unsupplied = required - retained_supply
    if unsupplied <= 0:
        grid = 0
        diesel = 0
        curtailed = -unsupplied
    else:
        grid = min(unsupplied, problem.grid_capacity[tick])
        diesel = unsupplied - grid
        curtailed = 0
    if diesel > problem.diesel_max_per_tick:
        return None

    wear = (
        (-action.battery_level * problem.charge_storage_per_level)
        if action.battery_level < 0
        else action.battery_level * problem.discharge_storage_per_level
    )
    source_cost = (
        Fraction(grid) * problem.grid_price[tick]
        + Fraction(diesel) * problem.diesel_price
        + Fraction(wear) * problem.battery_wear_price
    )
    burden = RetainedBurden.from_values(
        BURDEN_ORDER,
        (diesel, grid, source_cost, wear, curtailed, grid),
    )
    after = EnergyState(storage_after, thermal_after)
    return EnergyStep(
        tick=tick,
        before=state,
        action=action,
        after=after,
        base_load_quanta=problem.base_load[tick],
        cooling_quanta=cooling_energy,
        solar_quanta=problem.solar_supply[tick],
        charge_input_quanta=charge_input,
        discharge_output_quanta=discharge_output,
        grid_quanta=grid,
        diesel_quanta=diesel,
        curtailed_quanta=curtailed,
        burden=burden,
    )


def _terminal_key(
    state: EnergyState,
    burden: RetainedBurden,
) -> tuple[Fraction, ...]:
    del state
    return burden.values


def compile_energy_plan(
    preflight: Verdict,
    problem: EnergyProblem,
    *,
    reverse_action_order: bool = False,
) -> Verdict:
    """Retain one least-burden representative for every exposed state."""

    if preflight.status != ACCEPT or not isinstance(
        preflight.value,
        EnergyPreflight,
    ):
        return _block(
            f"execution has no accepted preflight: {preflight.reason}",
            preflight.value,
        )
    certificate = preflight.value
    if certificate.lineage_digest != _lineage_digest(
        certificate.declaration,
        problem,
        certificate.plan,
    ):
        return _block("problem/declaration lineage differs from preflight")

    initial = EnergyState(
        problem.initial_storage,
        problem.initial_thermal,
    )
    current: dict[EnergyState, RetainedBurden] = {
        initial: RetainedBurden.zero(BURDEN_ORDER)
    }
    parents: list[dict[EnergyState, tuple[EnergyState, EnergyStep]]] = []
    actions: Sequence[EnergyAction] = problem.actions
    if reverse_action_order:
        actions = tuple(reversed(actions))

    candidate_records = 0
    admissible_records = 0
    compositions = 0
    comparisons = 0
    writes = 0
    peak_states = 1

    for tick in range(problem.ticks):
        following: dict[EnergyState, RetainedBurden] = {}
        back: dict[EnergyState, tuple[EnergyState, EnergyStep]] = {}
        for state in sorted(current):
            prior = current[state]
            for action in actions:
                candidate_records += 1
                step = transition(problem, tick, state, action)
                if step is None:
                    continue
                admissible_records += 1
                candidate = prior.extend(step.burden)
                compositions += 1
                existing = following.get(step.after)
                if existing is not None:
                    comparisons += 1
                if existing is None or candidate.values < existing.values:
                    following[step.after] = candidate
                    back[step.after] = (state, step)
                    writes += 1
        if not following:
            return Verdict(
                HOLD,
                value=certificate,
                reason=f"no admissible retained state survives tick {tick}",
            )
        current = following
        parents.append(back)
        peak_states = max(peak_states, len(current))

    final_state = min(
        current,
        key=lambda state: (_terminal_key(state, current[state]), state),
    )
    burden = current[final_state]
    path: list[EnergyStep] = []
    cursor = final_state
    for tick in range(problem.ticks - 1, -1, -1):
        previous, step = parents[tick][cursor]
        path.append(step)
        cursor = previous
    path.reverse()
    work = EnergyWorkLedger(
        candidate_records=candidate_records,
        admissible_records=admissible_records,
        burden_compositions=compositions,
        retention_comparisons=comparisons,
        retention_writes=writes,
        backtrace_steps=len(path),
        peak_retained_states=peak_states,
    )
    if candidate_records > certificate.plan.candidate_record_bound:
        return _block("measured candidates exceed the preflight bound", work)
    if peak_states > certificate.plan.retained_state_bound:
        return _block("measured retained states exceed the preflight bound", work)
    if work.work_tokens > certificate.plan.work_token_bound:
        return _block("measured work exceeds the preflight bound", work)
    return Verdict(
        ACCEPT,
        value=EnergyResult(
            protocol=certificate.protocol,
            problem_name=problem.name,
            lineage_digest=certificate.lineage_digest,
            final_state=final_state,
            burden=burden,
            steps=tuple(path),
            work=work,
            tier=certificate.declaration.tier,
        ),
        reason=(
            f"retained {peak_states} peak states from "
            f"{candidate_records} finite candidate records"
        ),
    )


def replay_energy(
    problem: EnergyProblem,
    actions: Sequence[EnergyAction],
) -> Verdict:
    """Replay a declared action lineage without planning or state merging."""

    if len(actions) != problem.ticks:
        return _block("action lineage length differs from the finite energy tape")
    state = EnergyState(problem.initial_storage, problem.initial_thermal)
    burden = RetainedBurden.zero(BURDEN_ORDER)
    steps: list[EnergyStep] = []
    for tick, action in enumerate(actions):
        step = transition(problem, tick, state, action)
        if step is None:
            return Verdict(
                HOLD,
                reason=f"action lineage is inadmissible at tick {tick}",
            )
        burden = burden.extend(step.burden)
        state = step.after
        steps.append(step)
    return Verdict(
        ACCEPT,
        value=(state, burden, tuple(steps)),
        reason="finite action lineage replayed exactly",
    )


def enumerate_energy_plan(
    preflight: Verdict,
    problem: EnergyProblem,
) -> Verdict:
    """Independent full-history enumeration for deliberately small tapes."""

    if preflight.status != ACCEPT or not isinstance(
        preflight.value,
        EnergyPreflight,
    ):
        return _block("enumeration has no accepted preflight")
    history_count = len(problem.actions) ** problem.ticks
    if history_count > preflight.value.declaration.max_candidate_records:
        return _block(
            f"full-history count {history_count} exceeds declared candidate budget"
        )
    best: tuple[
        tuple[Fraction, ...],
        tuple[EnergyAction, ...],
        EnergyState,
        RetainedBurden,
    ] | None = None
    admissible = 0
    for actions in product(problem.actions, repeat=problem.ticks):
        replay = replay_energy(problem, actions)
        if replay.status != ACCEPT:
            continue
        admissible += 1
        state, burden, _steps = replay.value
        key = _terminal_key(state, burden)
        record = (key, actions, state, burden)
        if best is None or (record[0], record[1]) < (best[0], best[1]):
            best = record
    if best is None:
        return Verdict(HOLD, reason="no admissible complete history exists")
    key, actions, state, burden = best
    return Verdict(
        ACCEPT,
        value={
            "priority_readout": key,
            "actions": actions,
            "final_state": state,
            "burden": burden,
            "admissible_histories": admissible,
            "total_histories": history_count,
        },
        reason=f"enumerated all {history_count} finite histories",
    )


def greedy_energy_baseline(problem: EnergyProblem) -> Verdict:
    """A causal one-tick reader with no retained view of future ticks."""

    state = EnergyState(problem.initial_storage, problem.initial_thermal)
    burden = RetainedBurden.zero(BURDEN_ORDER)
    steps: list[EnergyStep] = []
    for tick in range(problem.ticks):
        candidates = [
            step
            for action in problem.actions
            if (step := transition(problem, tick, state, action)) is not None
        ]
        if not candidates:
            return Verdict(
                HOLD,
                reason=f"greedy reader has no admissible action at tick {tick}",
            )
        # One-tick burden only: it cannot retain an outage or hot interval that
        # has not appeared yet.
        step = min(
            candidates,
            key=lambda item: (
                item.burden.values,
                item.after.thermal_quanta,
                item.action,
            ),
        )
        burden = burden.extend(step.burden)
        state = step.after
        steps.append(step)
    return Verdict(
        ACCEPT,
        value={
            "final_state": state,
            "burden": burden,
            "priority_readout": _terminal_key(state, burden),
            "steps": tuple(steps),
        },
        reason="one-tick causal baseline completed",
    )


def certify_energy(
    preflight: Verdict,
    execution: Verdict,
    problem: EnergyProblem,
    witness_readout: Sequence[Fraction] | None,
    *,
    witness_method: str,
) -> Verdict:
    """Issue ACCEPT only for a preserved replay and finite exact witness."""

    if preflight.status != ACCEPT or not isinstance(
        preflight.value,
        EnergyPreflight,
    ):
        return _block("certificate has no accepted preflight")
    if execution.status != ACCEPT or not isinstance(
        execution.value,
        EnergyResult,
    ):
        return Verdict(
            HOLD,
            value=execution.value,
            reason=f"execution is not accepted: {execution.reason}",
        )
    result = execution.value
    replay = replay_energy(problem, tuple(step.action for step in result.steps))
    replay_preserved = (
        replay.status == ACCEPT
        and replay.value[0] == result.final_state
        and replay.value[1] == result.burden
        and replay.value[2] == result.steps
    )
    if not replay_preserved:
        return Verdict(HOLD, value=result, reason="lineage replay was not preserved")
    if witness_readout is None:
        return Verdict(
            HOLD,
            value=result,
            reason="no exact finite preservation witness was supplied",
        )
    if not isinstance(witness_method, str) or not witness_method.strip():
        return _block("witness method is undeclared")
    witness = tuple(Fraction(value) for value in witness_readout)
    readout = result.output_readout
    if witness != readout:
        return Verdict(
            HOLD,
            value=result,
            reason=f"witness differs: execution={readout}, witness={witness}",
        )
    planned = preflight.value.plan
    certificate = EnergyCertificate(
        protocol=result.protocol,
        problem_name=result.problem_name,
        lineage_digest=result.lineage_digest,
        output_names=preflight.value.declaration.output_names,
        readout=readout,
        witness_readout=witness,
        witness_method=witness_method,
        replay_preserved=True,
        planned_candidate_bound=planned.candidate_record_bound,
        measured_candidate_records=result.work.candidate_records,
        planned_work_bound=planned.work_token_bound,
        measured_work_tokens=result.work.work_tokens,
        tier=result.tier,
    )
    return Verdict(
        ACCEPT,
        value=certificate,
        reason="exact finite readout, replay, witness, and resource bounds agree",
    )


def default_energy_declaration(problem: EnergyProblem) -> EnergyDeclaration:
    """A budget sized from the declared finite tape, not from a trial run."""

    state_bound = (
        (problem.storage_max - problem.storage_min + 1)
        * (problem.thermal_max - problem.thermal_min + 1)
    )
    candidates = problem.ticks * state_bound * len(problem.actions)
    return EnergyDeclaration(
        protocol="RCP-Energy/1.0",
        output_names=(
            "diesel_quanta",
            "grid_quanta",
            "peak_grid_quanta",
            "source_cost",
            "battery_wear_quanta",
            "curtailed_quanta",
            "final_storage_quanta",
            "final_thermal_quanta",
        ),
        priority_names=(
            "diesel_quanta",
            "grid_quanta",
            "source_cost",
            "battery_wear_quanta",
            "curtailed_quanta",
            "peak_grid_quanta",
        ),
        max_candidate_records=candidates,
        max_retained_states=state_bound,
        max_work_tokens=5 * candidates + problem.ticks,
    )
