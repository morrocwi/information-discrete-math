#!/usr/bin/env python3
"""Dependency-free executable checks for RCP-Energy/1.0."""

from __future__ import annotations

import sys
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmarks.rcp_energy_challenge import (  # noqa: E402
    default_energy_problem,
    exact_small_problem,
)
from tools.idm_discipline import ACCEPT, BLOCK, HOLD  # noqa: E402
from tools.retained_burden_algebra import (  # noqa: E402
    BurdenOrder,
    RetainedBurden,
    retain_lesser,
)
from tools.retained_energy_protocol import (  # noqa: E402
    certify_energy,
    compile_energy_plan,
    default_energy_declaration,
    enumerate_energy_plan,
    preflight_energy,
)


def main() -> int:
    checks: list[tuple[str, bool]] = []

    order = BurdenOrder(("fuel", "grid", "peak"), ("sum", "sum", "max"))
    a = RetainedBurden.from_values(order, (1, 2, 7))
    b = RetainedBurden.from_values(order, (3, 4, 5))
    z = RetainedBurden.zero(order)
    checks.append(("RBA finite identity", a.extend(z) == a))
    checks.append(
        (
            "RBA sum/sum/max composition",
            a.extend(b).values == (4, 6, 7),
        )
    )
    checks.append(("RBA explicit absence", retain_lesser(None, a) == a))

    small = exact_small_problem()
    small_decl = default_energy_declaration(small)
    small_decl = replace(
        small_decl,
        max_candidate_records=max(
            small_decl.max_candidate_records,
            len(small.actions) ** small.ticks,
        ),
    )
    small_preflight = preflight_energy(small_decl, small)
    small_run = compile_energy_plan(small_preflight, small)
    small_exact = enumerate_energy_plan(small_preflight, small)
    checks.append(("small preflight ACCEPT", small_preflight.status == ACCEPT))
    checks.append(("small execution ACCEPT", small_run.status == ACCEPT))
    checks.append(("small exhaustive witness ACCEPT", small_exact.status == ACCEPT))
    checks.append(
        (
            "small exact priority preserved",
            small_run.status == ACCEPT
            and small_exact.status == ACCEPT
            and small_run.value.priority_readout
            == small_exact.value["priority_readout"],
        )
    )

    full = default_energy_problem()
    full_decl = default_energy_declaration(full)
    full_preflight = preflight_energy(full_decl, full)
    forward = compile_energy_plan(full_preflight, full)
    reverse = compile_energy_plan(
        full_preflight,
        full,
        reverse_action_order=True,
    )
    checks.append(("96-tick preflight ACCEPT", full_preflight.status == ACCEPT))
    checks.append(("96-tick forward ACCEPT", forward.status == ACCEPT))
    checks.append(("96-tick reversed-order ACCEPT", reverse.status == ACCEPT))
    checks.append(
        (
            "96-tick action-order invariant",
            forward.status == reverse.status == ACCEPT
            and forward.value.output_readout == reverse.value.output_readout,
        )
    )
    full_cert = certify_energy(
        full_preflight,
        forward,
        full,
        reverse.value.output_readout if reverse.status == ACCEPT else None,
        witness_method="reversed action-order retention plus exact replay",
    )
    checks.append(("96-tick certificate ACCEPT", full_cert.status == ACCEPT))

    low_budget = preflight_energy(
        replace(full_decl, max_candidate_records=1),
        full,
    )
    checks.append(("low budget BLOCK", low_budget.status == BLOCK))
    wrong_boundary = preflight_energy(
        replace(full_decl, output_names=("diesel_quanta",)),
        full,
    )
    checks.append(("incomplete boundary BLOCK", wrong_boundary.status == BLOCK))
    no_witness = certify_energy(
        full_preflight,
        forward,
        full,
        None,
        witness_method="",
    )
    checks.append(("missing witness HOLD", no_witness.status == HOLD))
    wrong_witness = certify_energy(
        full_preflight,
        forward,
        full,
        (Fraction(0),) * 8,
        witness_method="deliberately wrong",
    )
    checks.append(("different witness HOLD", wrong_witness.status == HOLD))

    for name, passed in checks:
        print(f"{'PASS' if passed else 'FAIL'}  {name}")
    passed = sum(ok for _name, ok in checks)
    print(f"RCP-Energy self-check: {passed}/{len(checks)} PASS")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())

