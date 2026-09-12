#!/usr/bin/env python3
"""Oracle-free outer refuter CEGIS baseline for SAT candidates.

The search tests only locally checkable SAT fixed-point equations and terminal
boundary truth.  It never asks whether an arbitrary nonterminal formula is SAT.

Search order:
  1. canonical TRUE/FALSE terminal states;
  2. normalized CNFs over a small declared variable set, ordered by number of
     clauses and literal count;
  3. root local recursion defect at the first declared variable.

If a defect is found, it is returned with the same local verifier used by the
main refuter lane.  If the finite budget is exhausted, return HOLD.

This is an executable outer-search baseline, not a polynomial worst-case
constructor for arbitrary circuits and not a P != NP proof.
"""
from __future__ import annotations

from itertools import combinations
from typing import Callable, Iterable

from sat_one_sided_audit import normalize, brute_sat
from sat_circuit_refuter_certificate import (
    local_defect_certificate,
    verify_refuter_certificate,
)

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Candidate = Callable[[CNF, tuple[int, ...]], bool]


def const_false(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    return False


def const_true(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    return True


def no_empty_clause(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    return not any(len(c) == 0 for c in normalize(cnf))


def clause_bank(n: int) -> list[Clause]:
    vars_ = list(range(1, n + 1))
    bank: list[Clause] = []
    for v in vars_:
        bank.extend([(v,), (-v,)])
    for i, a in enumerate(vars_):
        for b in vars_[i + 1:]:
            bank.extend([(a, b), (a, -b), (-a, b), (-a, -b)])
    return bank


def formula_complexity(f: CNF) -> tuple[int, int, CNF]:
    return (len(f), sum(len(c) for c in f), f)


def enumerate_root_formulas(n: int, max_clauses: int) -> Iterable[CNF]:
    bank = clause_bank(n)
    seen: set[CNF] = set()
    formulas: list[CNF] = []
    for r in range(0, min(max_clauses, len(bank)) + 1):
        for cs in combinations(bank, r):
            f = normalize(tuple(cs))
            if f not in seen:
                seen.add(f)
                formulas.append(f)
    formulas.sort(key=formula_complexity)
    return formulas


def outer_refute(
    candidate: Candidate,
    *,
    max_vars: int = 2,
    max_clauses: int = 3,
    max_tests: int = 10_000,
) -> dict:
    tests = 0

    # Canonical terminal target values are direct syntax, not SAT-oracle calls.
    for f in (normalize(()), normalize(((),))):
        cert = local_defect_certificate(f, ())
        tests += 1
        if verify_refuter_certificate(candidate, cert):
            return {"status": "REFUTED", "tests": tests, "certificate": cert, "phase": "boundary"}

    for n in range(1, max_vars + 1):
        rem = tuple(range(1, n + 1))
        for f in enumerate_root_formulas(n, max_clauses):
            if tests >= max_tests:
                return {"status": "HOLD", "tests": tests, "reason": "test budget exhausted"}
            cert = local_defect_certificate(f, rem)
            tests += 1
            if verify_refuter_certificate(candidate, cert):
                return {"status": "REFUTED", "tests": tests, "certificate": cert, "phase": "local"}

    return {
        "status": "HOLD",
        "tests": tests,
        "reason": "no local/boundary defect in declared finite search region",
    }


def main() -> None:
    cases = [
        ("constant-false", const_false, True),
        ("constant-true", const_true, True),
        ("no-empty-clause", no_empty_clause, True),
    ]
    for name, cand, expect_refuted in cases:
        out = outer_refute(cand)
        assert (out["status"] == "REFUTED") == expect_refuted, (name, out)
        if out["status"] == "REFUTED":
            assert verify_refuter_certificate(cand, out["certificate"])
        print(f"{name}: {out}")

    # Exact SAT candidate on this finite search must not produce a false defect.
    exact = outer_refute(brute_sat, max_vars=2, max_clauses=3)
    assert exact["status"] == "HOLD", exact
    print(f"exact-SAT finite control: {exact}")

    # Ensure the baseline itself never uses root SAT truth: brute_sat appears
    # only as the exact-candidate negative control above.
    print("outer refuter CEGIS baseline: PASS")
    print("verification=local/boundary only; arbitrary-circuit polynomial search bound=OPEN")
    print("tier=finite_diagnostic; P!=NP=NOT CLAIMED")


if __name__ == "__main__":
    main()
