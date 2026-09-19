#!/usr/bin/env python3
"""Executable one-sided audit for SAT-style existential restriction.

Given a candidate predictor C and a CNF F with C(F)=1, repeatedly query both
restricted children.  At each level either:

  * parent=1 but both children=0 -> local restriction defect;
  * some child=1 -> follow such a child.

At a terminal leaf, candidate=1 must coincide with direct syntactic truth.
Hence the audit returns either a genuine satisfying assignment or a concrete
local/leaf defect.  No SAT oracle is used by the audit itself.

If C(F)=0 the one-sided audit returns HOLD: validating a negative existential
claim requires universal closure or a separately supplied UNSAT certificate.

Tier: exact finite diagnostic / witness-or-defect procedure. No P != NP claim.
"""
from __future__ import annotations

from typing import Callable

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Candidate = Callable[[CNF, tuple[int, ...]], bool]


def normalize(cnf: CNF) -> CNF:
    out = []
    for clause in cnf:
        lits = set(clause)
        if any(-l in lits for l in lits):
            continue
        out.append(tuple(sorted(lits, key=lambda z: (abs(z), z))))
    return tuple(sorted(out))


def restrict(cnf: CNF, var: int, value: bool) -> CNF:
    sat_lit = var if value else -var
    false_lit = -sat_lit
    out = []
    for clause in cnf:
        if sat_lit in clause:
            continue
        out.append(tuple(l for l in clause if l != false_lit))
    return normalize(tuple(out))


def leaf_truth(cnf: CNF) -> bool:
    if any(len(c) == 0 for c in cnf):
        return False
    return len(cnf) == 0


def no_empty_clause(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    return not any(len(c) == 0 for c in cnf)


def const_true(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    return True


def brute_sat(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    if not remaining:
        return leaf_truth(cnf)
    v = remaining[0]
    tail = remaining[1:]
    return brute_sat(restrict(cnf, v, False), tail) or brute_sat(
        restrict(cnf, v, True), tail
    )


def audit_positive_claim(cnf: CNF, remaining: tuple[int, ...], candidate: Candidate) -> dict:
    cnf = normalize(cnf)
    root = bool(candidate(cnf, remaining))
    if not root:
        return {
            "status": "HOLD",
            "reason": "candidate makes a negative existential claim; one-sided witness audit is not applicable",
            "queries": 1,
        }

    assignment: dict[int, bool] = {}
    cur = cnf
    rem = remaining
    queries = 1

    while rem:
        v = rem[0]
        tail = rem[1:]
        f0 = restrict(cur, v, False)
        f1 = restrict(cur, v, True)
        c0 = bool(candidate(f0, tail))
        c1 = bool(candidate(f1, tail))
        queries += 2

        if not (c0 or c1):
            return {
                "status": "REFUTED",
                "kind": "local_defect",
                "variable": v,
                "parent_claim": True,
                "child_claims": (False, False),
                "queries": queries,
                "partial_assignment": dict(assignment),
            }

        choose = True if c1 else False
        assignment[v] = choose
        cur = f1 if choose else f0
        rem = tail

    # The followed path has candidate value 1 at every selected node.
    if not leaf_truth(cur):
        return {
            "status": "REFUTED",
            "kind": "leaf_error",
            "queries": queries,
            "assignment": assignment,
            "leaf_formula": cur,
        }

    return {
        "status": "WITNESS",
        "queries": queries,
        "assignment": assignment,
        "leaf_formula": cur,
    }


def main() -> None:
    sat_formula = normalize(((1, 2), (-1, 2)))
    unsat_formula = normalize(((1,), (-1,)))

    r_exact = audit_positive_claim(sat_formula, (1, 2), brute_sat)
    assert r_exact["status"] == "WITNESS", r_exact

    r_cheap = audit_positive_claim(unsat_formula, (1,), no_empty_clause)
    assert r_cheap["status"] == "REFUTED"
    assert r_cheap["kind"] == "local_defect"

    r_true = audit_positive_claim(unsat_formula, (1,), const_true)
    assert r_true["status"] == "REFUTED"
    assert r_true["kind"] == "leaf_error"

    r_hold = audit_positive_claim(unsat_formula, (1,), brute_sat)
    assert r_hold["status"] == "HOLD"

    print(f"exact positive claim -> {r_exact}")
    print(f"cheap false positive -> {r_cheap}")
    print(f"constant-true false positive -> {r_true}")
    print(f"exact negative claim -> {r_hold}")
    print("one-sided SAT audit: PASS")
    print("positive claims: witness-or-defect; negative claims: HOLD without universal closure")


if __name__ == "__main__":
    main()
