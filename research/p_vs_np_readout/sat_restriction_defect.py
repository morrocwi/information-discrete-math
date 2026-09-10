#!/usr/bin/env python3
"""Finite SAT self-reduction / restriction-defect diagnostic.

For CNF F and a remaining variable x_i,

    SAT(F) = SAT(F|x_i=0) OR SAT(F|x_i=1).

A candidate predictor C is locally consistent at a restriction-tree node when

    C(F) = C(F0) OR C(F1).

Leaves have exact syntactic truth after all variables are assigned.  The total
defect is the number of violated local OR identities plus wrong leaf labels.
The exact finite inequality checked here is

    1[C(F) != SAT(F)] <= total_defect(F,C).

This is an executable finite analogue of a quantitative measurement/defect
certificate.  It is not a polynomial-time SAT verifier: the complete tree has
2^n leaves.  No P != NP claim is made.
"""
from __future__ import annotations

from itertools import product

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]


def normalize(cnf: CNF) -> CNF:
    out = []
    for clause in cnf:
        s = sorted(set(clause), key=lambda z: (abs(z), z))
        # Drop tautological clauses.
        lits = set(s)
        if any(-l in lits for l in lits):
            continue
        out.append(tuple(s))
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
    # With no remaining variables, every surviving nonempty literal would be a
    # malformed leaf in this diagnostic.  Normal restriction leaves either no
    # clauses (true) or an empty clause (false).
    if any(len(c) == 0 for c in cnf):
        return False
    return len(cnf) == 0


def brute_sat(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    if not remaining:
        return leaf_truth(cnf)
    for values in product((False, True), repeat=len(remaining)):
        cur = cnf
        for v, b in zip(remaining, values):
            cur = restrict(cur, v, b)
        if leaf_truth(cur):
            return True
    return False


def no_empty_clause(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    return not any(len(c) == 0 for c in cnf)


def const_true(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    return True


def const_false(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    return False


def analyze(cnf: CNF, remaining: tuple[int, ...], candidate) -> dict:
    c_here = bool(candidate(cnf, remaining))
    if not remaining:
        target = leaf_truth(cnf)
        defect = int(c_here != target)
        return {
            "candidate": c_here,
            "target": target,
            "local_defect": defect,
            "total_defect": defect,
            "nodes": 1,
            "leaves": 1,
        }

    v = remaining[0]
    tail = remaining[1:]
    left = analyze(restrict(cnf, v, False), tail, candidate)
    right = analyze(restrict(cnf, v, True), tail, candidate)
    target = left["target"] or right["target"]
    local = int(c_here != (left["candidate"] or right["candidate"]))
    total = local + left["total_defect"] + right["total_defect"]
    root_error = int(c_here != target)
    assert root_error <= total
    return {
        "candidate": c_here,
        "target": target,
        "local_defect": local,
        "total_defect": total,
        "nodes": 1 + left["nodes"] + right["nodes"],
        "leaves": left["leaves"] + right["leaves"],
    }


def fixture(name: str, cnf: CNF, remaining: tuple[int, ...], candidate) -> dict:
    cnf = normalize(cnf)
    r = analyze(cnf, remaining, candidate)
    exact = brute_sat(cnf, remaining)
    assert r["target"] == exact
    assert int(r["candidate"] != exact) <= r["total_defect"]
    return {"name": name, **r}


def main() -> None:
    tests = [
        # Unsatisfiable contradiction: the cheap "no explicit empty clause"
        # heuristic says true at the root but both restrictions are false.
        ("contradiction-cheap", ((1,), (-1,)), (1,), no_empty_clause),
        # Exact SAT must have zero defect everywhere.
        ("contradiction-exact", ((1,), (-1,)), (1,), brute_sat),
        # Satisfiable formula: constant false is locally OR-consistent but must
        # eventually violate a true leaf boundary.
        ("unit-const-false", ((1,),), (1,), const_false),
        # Unsatisfiable formula: constant true eventually violates false leaves.
        ("contradiction-const-true", ((1,), (-1,)), (1,), const_true),
        # Two-variable satisfiable control.
        ("two-var-exact", ((1, 2), (-1, 2)), (1, 2), brute_sat),
    ]

    rows = [fixture(*t) for t in tests]
    for r in rows:
        print(
            f"{r['name']}: candidate={int(r['candidate'])} target={int(r['target'])} "
            f"defect={r['total_defect']} nodes={r['nodes']} leaves={r['leaves']}"
        )

    exact_rows = [r for r in rows if r["name"].endswith("exact")]
    assert all(r["total_defect"] == 0 for r in exact_rows)
    assert next(r for r in rows if r["name"] == "contradiction-cheap")["local_defect"] == 1
    assert next(r for r in rows if r["name"] == "unit-const-false")["total_defect"] >= 1

    print("SAT restriction-defect finite certificate: PASS")
    print("verified: root disagreement <= local defects + leaf errors")
    print("tier=exact_finite_diagnostic; full restriction tree may be exponential")


if __name__ == "__main__":
    main()
