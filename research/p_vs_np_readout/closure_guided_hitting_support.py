#!/usr/bin/env python3
"""Syntax-guided defect support using sound unit-propagation closure.

This is a constructive restricted prototype for the Lineage Hitting-Support
frontier.  It deliberately uses only CNF syntax plus the candidate's local
restriction evaluations; it never calls a SAT solver.

If a unit clause forces x=b, we follow that forced branch, add the current
state to the defect support, and continue.  A contradiction closes the formula.
If all variables are assigned, direct leaf truth is available.  If propagation
stalls with unresolved variables, the constructor returns HOLD.

The key calibration is the unique-witness family

    x1 & x2 & ... & xn.

A black-box left-first search for the constant-false candidate visits the full
2^(n+1)-1 restriction tree before reaching its only defect.  Unit closure,
however, reads the forced literals and reaches the satisfying boundary in O(n)
states.  This demonstrates genuine syntax/closure compression while preserving
a fail-closed boundary: formulas not decided by the rule remain HOLD.

Tier: exact finite diagnostic for a restricted closure system.  No P != NP
claim and no completeness claim for unit propagation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from sat_one_sided_audit import normalize, restrict, leaf_truth, brute_sat
from sat_circuit_refuter_certificate import (
    local_defect_certificate,
    verify_refuter_certificate,
)

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Candidate = Callable[[CNF, tuple[int, ...]], bool]


def const_false(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    return False


def unit_literal(cnf: CNF, remaining: tuple[int, ...]) -> int | None:
    rem = set(remaining)
    for clause in normalize(cnf):
        if len(clause) == 1 and abs(clause[0]) in rem:
            return clause[0]
    return None


def contradiction(cnf: CNF) -> bool:
    return any(len(c) == 0 for c in normalize(cnf))


@dataclass
class SupportResult:
    status: str
    support: list[dict]
    assignments: dict[int, bool]
    reason: str


def build_unit_closure_support(
    cnf: CNF,
    remaining: tuple[int, ...],
    candidate: Candidate,
) -> SupportResult:
    f = normalize(cnf)
    rem = tuple(remaining)
    support: list[dict] = []
    assignment: dict[int, bool] = {}

    while True:
        cert = local_defect_certificate(f, rem)
        support.append(cert)
        if verify_refuter_certificate(candidate, cert):
            return SupportResult("DEFECT", support, assignment, "local/boundary defect verified")

        if contradiction(f):
            # A direct syntactic contradiction is a sound negative closure.
            return SupportResult("CLOSED_FALSE", support, assignment, "empty clause")

        if not rem:
            # No defect and direct boundary truth agrees with the candidate.
            return SupportResult("BOUNDARY_OK", support, assignment, "terminal state agrees")

        lit = unit_literal(f, rem)
        if lit is None:
            return SupportResult(
                "HOLD",
                support,
                assignment,
                "unit closure stalled with unresolved variables",
            )

        v = abs(lit)
        value = lit > 0
        if v not in rem:
            return SupportResult("HOLD", support, assignment, "unit literal outside declared remainder")
        assignment[v] = value
        f = normalize(restrict(f, v, value))
        rem = tuple(x for x in rem if x != v)


def unique_all_true_formula(n: int) -> tuple[CNF, tuple[int, ...]]:
    return normalize(tuple((i,) for i in range(1, n + 1))), tuple(range(1, n + 1))


def audit_compression(max_n: int = 20) -> None:
    print("unit-closure compression on unique-witness family")
    for n in range(1, max_n + 1):
        f, rem = unique_all_true_formula(n)
        result = build_unit_closure_support(f, rem, const_false)
        assert brute_sat(f, rem)
        assert result.status == "DEFECT", (n, result)
        assert len(result.support) == n + 1, (n, len(result.support))
        assert result.assignments == {i: True for i in range(1, n + 1)}
        black_box_nodes = (1 << (n + 1)) - 1
        print(
            f"n={n:2d} black_box={black_box_nodes:8d} "
            f"unit_support={len(result.support):3d} status={result.status}"
        )


def audit_fail_closed() -> None:
    # Satisfiable but no unit clause at the root.  Constant-false is wrong,
    # yet this restricted constructor must not pretend to have found a defect.
    f = normalize(((1, 2),))
    rem = (1, 2)
    assert brute_sat(f, rem)
    result = build_unit_closure_support(f, rem, const_false)
    assert result.status == "HOLD", result
    assert len(result.support) == 1
    print(f"non-unit satisfiable control: status={result.status}, support={len(result.support)}")

    # Exact candidate never produces a false defect; unit closure may terminate
    # or HOLD depending on syntax.
    g = normalize(((1,), (-1, 2)))
    exact = build_unit_closure_support(g, (1, 2), brute_sat)
    assert exact.status != "DEFECT", exact
    print(f"exact-candidate control: status={exact.status}, support={len(exact.support)}")


def main() -> None:
    audit_compression()
    audit_fail_closed()
    print("closure-guided hitting support: PASS")
    print("syntax-aware unit closure compresses an exponential black-box search to O(n) on the calibrated family")
    print("stalled unresolved formulas return HOLD; unrestricted completeness remains OPEN")
    print("tier=finite_diagnostic; P!=NP=NOT CLAIMED")


if __name__ == "__main__":
    main()
