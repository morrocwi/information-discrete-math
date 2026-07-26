#!/usr/bin/env python3
"""RCP Energy Challenge 1: finite cold-store microgrid planning.

The profiles below are a mathematical stress tape, not measurements and not a
claim about a physical facility.  They are generated only by finite integer
rules.  External datasets/solvers are deliberately absent from ``ours``.
"""

from __future__ import annotations

import json
import time
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

try:
    from tools.idm_discipline import ACCEPT
    from tools.retained_energy_protocol import (
        EnergyProblem,
        certify_energy,
        compile_energy_plan,
        default_energy_declaration,
        enumerate_energy_plan,
        greedy_energy_baseline,
        preflight_energy,
    )
except ModuleNotFoundError:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from tools.idm_discipline import ACCEPT
    from tools.retained_energy_protocol import (
        EnergyProblem,
        certify_energy,
        compile_energy_plan,
        default_energy_declaration,
        enumerate_energy_plan,
        greedy_energy_baseline,
        preflight_energy,
    )


def _triangle(
    tick: int,
    start: int,
    summit: int,
    stop: int,
    height: int,
) -> int:
    """Finite triangular tape; no trigonometric/continuum primitive."""

    if tick < start or tick >= stop:
        return 0
    if tick <= summit:
        return height * (tick - start) // max(summit - start, 1)
    return height * (stop - tick) // max(stop - summit, 1)


def default_energy_problem(ticks: int = 96) -> EnergyProblem:
    if ticks != 96:
        raise ValueError("the registered full challenge has exactly 96 ticks")
    base = tuple(
        (4 if tick < 20 or tick >= 88 else 6) + (1 if tick % 8 < 3 else 0)
        for tick in range(ticks)
    )
    solar = tuple(_triangle(tick, 20, 48, 73, 12) for tick in range(ticks))
    thermal = tuple(2 if 28 <= tick < 72 else 1 for tick in range(ticks))
    grid_capacity = tuple(
        0 if 74 <= tick < 83 else (4 if 88 <= tick < 92 else 18)
        for tick in range(ticks)
    )
    price = tuple(
        Fraction(3, 1) if 64 <= tick < 88 else Fraction(1, 1)
        for tick in range(ticks)
    )
    return EnergyProblem(
        name="finite-cold-store-96-tick-stress-tape",
        resolution_lambda=(
            "15-minute tick; 1 energy quantum=1/4 kWh; "
            "integer thermal/storage records"
        ),
        tick_minutes=15,
        energy_quantum_kwh=Fraction(1, 4),
        base_load=base,
        solar_supply=solar,
        thermal_ingress=thermal,
        grid_capacity=grid_capacity,
        grid_price=price,
        initial_storage=8,
        storage_min=0,
        storage_max=32,
        initial_thermal=8,
        thermal_min=2,
        thermal_max=14,
        cooling_levels=(0, 1, 2, 3),
        cooling_energy_per_level=2,
        cooling_effect_per_level=2,
        battery_levels=(-2, -1, 0, 1, 2),
        charge_input_per_level=5,
        charge_storage_per_level=4,
        discharge_storage_per_level=5,
        discharge_output_per_level=4,
        diesel_max_per_tick=14,
        diesel_price=Fraction(5, 1),
        battery_wear_price=Fraction(1, 20),
    )


def exact_small_problem() -> EnergyProblem:
    """A six-tick tape small enough to enumerate every action history."""

    return EnergyProblem(
        name="finite-energy-exact-six-tick",
        resolution_lambda="one finite tick; one integer energy quantum",
        tick_minutes=15,
        energy_quantum_kwh=Fraction(1, 4),
        base_load=(3, 3, 3, 3, 3, 3),
        solar_supply=(0, 3, 4, 0, 0, 0),
        thermal_ingress=(1, 1, 2, 2, 1, 1),
        grid_capacity=(8, 8, 8, 0, 0, 8),
        grid_price=(Fraction(1),) * 6,
        initial_storage=0,
        storage_min=0,
        storage_max=8,
        initial_thermal=4,
        thermal_min=2,
        thermal_max=7,
        cooling_levels=(0, 1),
        cooling_energy_per_level=1,
        cooling_effect_per_level=2,
        battery_levels=(-1, 0, 1),
        charge_input_per_level=2,
        charge_storage_per_level=2,
        discharge_storage_per_level=2,
        discharge_output_per_level=2,
        diesel_max_per_tick=6,
        diesel_price=Fraction(5),
        battery_wear_price=Fraction(1, 20),
    )


def _fraction_json(value: Fraction) -> str:
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}"


def _readout_json(values) -> list[str]:
    return [_fraction_json(value) for value in values]


def _run_problem(problem: EnergyProblem, *, exact: bool) -> dict[str, object]:
    declaration = default_energy_declaration(problem)
    # The small witness enumerates complete histories rather than merged
    # states, so its independent witness budget must admit |A|^ticks.
    if exact:
        declaration = replace(
            declaration,
            max_candidate_records=max(
                declaration.max_candidate_records,
                len(problem.actions) ** problem.ticks,
            ),
        )
    preflight = preflight_energy(declaration, problem)
    if preflight.status != ACCEPT:
        raise RuntimeError(preflight.reason)

    started = time.perf_counter()
    execution = compile_energy_plan(preflight, problem)
    elapsed = time.perf_counter() - started
    if execution.status != ACCEPT:
        raise RuntimeError(execution.reason)
    result = execution.value

    if exact:
        witness = enumerate_energy_plan(preflight, problem)
        if witness.status != ACCEPT:
            raise RuntimeError(witness.reason)
        diesel, grid, cost, wear, curtailment, peak = (
            witness.value["priority_readout"]
        )
        witness_output = (
            diesel,
            grid,
            peak,
            cost,
            wear,
            curtailment,
            Fraction(witness.value["final_state"].storage_quanta),
            Fraction(witness.value["final_state"].thermal_quanta),
        )
        witness_method = "complete finite history enumeration"
        witness_detail = {
            "total_histories": witness.value["total_histories"],
            "admissible_histories": witness.value["admissible_histories"],
        }
    else:
        alternate = compile_energy_plan(
            preflight,
            problem,
            reverse_action_order=True,
        )
        if alternate.status != ACCEPT:
            raise RuntimeError(alternate.reason)
        witness_output = alternate.value.output_readout
        witness_method = "reversed action-order retention plus exact lineage replay"
        witness_detail = {
            "alternate_candidates": alternate.value.work.candidate_records,
        }

    certified = certify_energy(
        preflight,
        execution,
        problem,
        witness_output,
        witness_method=witness_method,
    )
    if certified.status != ACCEPT:
        raise RuntimeError(certified.reason)
    baseline = greedy_energy_baseline(problem)
    if baseline.status != ACCEPT:
        raise RuntimeError(baseline.reason)

    baseline_priority = baseline.value["priority_readout"]
    diesel_saved = baseline_priority[0] - result.priority_readout[0]
    grid_saved = baseline_priority[1] - result.priority_readout[1]
    source_change = (
        result.priority_readout[0]
        + result.priority_readout[1]
        - baseline_priority[0]
        - baseline_priority[1]
    )
    diesel_reduction = (
        diesel_saved / baseline_priority[0]
        if baseline_priority[0] > 0
        else Fraction(0)
    )
    return {
        "problem": problem.name,
        "ticks": problem.ticks,
        "action_count_per_tick": len(problem.actions),
        "energy_quantum_kwh": _fraction_json(problem.energy_quantum_kwh),
        "preflight": {
            "status": preflight.status,
            "lineage_digest": preflight.value.lineage_digest,
            "candidate_bound": preflight.value.plan.candidate_record_bound,
            "state_bound": preflight.value.plan.state_bound,
            "work_bound": preflight.value.plan.work_token_bound,
        },
        "rcp_energy": {
            "status": certified.status,
            "priority_readout": _readout_json(result.priority_readout),
            "output_readout": _readout_json(result.output_readout),
            "diesel_kwh": _fraction_json(
                result.priority_readout[0] * problem.energy_quantum_kwh
            ),
            "grid_kwh": _fraction_json(
                result.priority_readout[1] * problem.energy_quantum_kwh
            ),
            "peak_grid_kw_readout": _fraction_json(
                result.output_readout[2]
            ),
            "candidate_records": result.work.candidate_records,
            "admissible_records": result.work.admissible_records,
            "peak_retained_states": result.work.peak_retained_states,
            "work_tokens": result.work.work_tokens,
            "elapsed_seconds": elapsed,
            "witness_method": witness_method,
            "replay_preserved": certified.value.replay_preserved,
        },
        "causal_one_tick_baseline": {
            "priority_readout": _readout_json(baseline_priority),
            "diesel_kwh": _fraction_json(
                baseline_priority[0] * problem.energy_quantum_kwh
            ),
            "grid_kwh": _fraction_json(
                baseline_priority[1] * problem.energy_quantum_kwh
            ),
        },
        "difference_vs_baseline": {
            "diesel_quanta_saved": _fraction_json(diesel_saved),
            "diesel_kwh_saved": _fraction_json(
                diesel_saved * problem.energy_quantum_kwh
            ),
            "diesel_reduction_fraction": _fraction_json(diesel_reduction),
            "grid_quanta_saved": _fraction_json(grid_saved),
            "grid_kwh_saved": _fraction_json(
                grid_saved * problem.energy_quantum_kwh
            ),
            "total_source_quanta_change": _fraction_json(source_change),
            "total_source_kwh_change": _fraction_json(
                source_change * problem.energy_quantum_kwh
            ),
        },
        "witness_detail": witness_detail,
        "honesty_fence": (
            "finite mathematical stress tape; not an empirical facility claim; "
            "no external solver or continuum library produced ours"
        ),
        "tier": "finite_diagnostic",
    }


def run_suite() -> dict[str, object]:
    return {
        "protocol": "RCP-Energy/1.0",
        "algebra": "Retained Burden Algebra over exact rational readouts",
        "exact_small": _run_problem(exact_small_problem(), exact=True),
        "full_96_tick": _run_problem(default_energy_problem(), exact=False),
    }


def main() -> int:
    report = run_suite()
    output = Path(__file__).with_name("rcp_energy_results.json")
    output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
