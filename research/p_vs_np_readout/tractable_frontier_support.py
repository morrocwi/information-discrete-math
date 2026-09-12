#!/usr/bin/env python3
"""Certified-frontier hitting support for SAT restriction trees.

This prototype extends local/boundary defect certificates with an independently
solved tractable frontier.  A declared backdoor B is expanded only on its
variables.  At each frontier state, if the restricted CNF is 2-CNF, an exact
polynomial-time 2-SAT solver supplies the target truth.  If a frontier remains
outside the certified class, the constructor returns HOLD rather than guessing.

Finite principle (already mirrored by IDM_SATRestrictionDefect):

    root error <= sum(internal local defects) + sum(frontier errors).

Therefore, if every frontier is certified exactly, a wrong root candidate must
expose either an internal restriction defect or a frontier mismatch.

Support size for a backdoor of size k is at most 2^(k+1)-1 states.  Thus a
logarithmic certified backdoor yields polynomial support.  This is a restricted,
parameterized constructor, not an unrestricted SAT lower bound.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from sat_one_sided_audit import normalize, restrict, brute_sat
from sat_circuit_refuter_certificate import verify_refuter_certificate, local_defect_certificate

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Candidate = Callable[[CNF, tuple[int, ...]], bool]


def const_false(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    return False


def variables_in(cnf: CNF) -> set[int]:
    return {abs(lit) for clause in cnf for lit in clause}


def is_2cnf(cnf: CNF) -> bool:
    return all(len(clause) <= 2 for clause in normalize(cnf))


def two_sat_truth(cnf: CNF) -> bool:
    """Exact 2-SAT by implication SCC; raises on clauses wider than 2."""
    f = normalize(cnf)
    if not is_2cnf(f):
        raise ValueError("not 2-CNF")
    if any(len(c) == 0 for c in f):
        return False

    vars_ = sorted(variables_in(f))
    if not vars_:
        return True
    idx = {v: i for i, v in enumerate(vars_)}
    n = len(vars_)
    g = [[] for _ in range(2 * n)]
    rg = [[] for _ in range(2 * n)]

    def node(lit: int) -> int:
        base = 2 * idx[abs(lit)]
        return base if lit > 0 else base + 1

    def neg_node_id(u: int) -> int:
        return u ^ 1

    def add_edge(a: int, b: int) -> None:
        g[a].append(b)
        rg[b].append(a)

    for clause in f:
        if len(clause) == 1:
            a = node(clause[0])
            add_edge(neg_node_id(a), a)
        elif len(clause) == 2:
            a = node(clause[0]); b = node(clause[1])
            add_edge(neg_node_id(a), b)
            add_edge(neg_node_id(b), a)

    seen = [False] * (2 * n)
    order: list[int] = []

    def dfs(u: int) -> None:
        seen[u] = True
        for v in g[u]:
            if not seen[v]:
                dfs(v)
        order.append(u)

    for u in range(2 * n):
        if not seen[u]:
            dfs(u)

    comp = [-1] * (2 * n)

    def rdfs(u: int, k: int) -> None:
        comp[u] = k
        for v in rg[u]:
            if comp[v] < 0:
                rdfs(v, k)

    k = 0
    for u in reversed(order):
        if comp[u] < 0:
            rdfs(u, k)
            k += 1

    for v in vars_:
        p = 2 * idx[v]
        if comp[p] == comp[p ^ 1]:
            return False
    return True


@dataclass(frozen=True)
class FrontierCert:
    cnf: CNF
    remaining: tuple[int, ...]
    target: bool


def verify_frontier(candidate: Candidate, cert: FrontierCert) -> bool:
    f = normalize(cert.cnf)
    if not is_2cnf(f):
        return False
    truth = two_sat_truth(f)
    if truth != cert.target:
        return False
    return bool(candidate(f, cert.remaining)) != truth


@dataclass
class BackdoorResult:
    status: str
    internal_support: list[dict]
    frontier_support: list[FrontierCert]
    visited: int
    reason: str


def build_backdoor_support(
    cnf: CNF,
    remaining: tuple[int, ...],
    candidate: Candidate,
    backdoor: tuple[int, ...],
) -> BackdoorResult:
    f0 = normalize(cnf)
    rem0 = tuple(remaining)
    internal: list[dict] = []
    frontier: list[FrontierCert] = []
    visited = 0

    def rec(f: CNF, rem: tuple[int, ...], depth: int) -> str | None:
        nonlocal visited
        visited += 1

        if depth < len(backdoor):
            v = backdoor[depth]
            if v not in rem:
                return "declared backdoor variable absent from remainder"

            # Internal local defect at the declared split.
            # The generic certificate verifier assumes the first remaining
            # variable is the split, so reorder only the declared remainder
            # metadata; CNF semantics are unchanged.
            ordered_rem = (v,) + tuple(x for x in rem if x != v)
            cert = local_defect_certificate(f, ordered_rem)
            internal.append(cert)
            if verify_refuter_certificate(candidate, cert):
                return None

            tail = tuple(x for x in rem if x != v)
            err = rec(normalize(restrict(f, v, False)), tail, depth + 1)
            if err is not None:
                return err
            err = rec(normalize(restrict(f, v, True)), tail, depth + 1)
            return err

        if not is_2cnf(f):
            return "frontier outside certified 2-CNF class"
        truth = two_sat_truth(f)
        cert = FrontierCert(f, rem, truth)
        frontier.append(cert)
        return None

    err = rec(f0, rem0, 0)
    if err is not None:
        return BackdoorResult("HOLD", internal, frontier, visited, err)

    # If any supplied support item already verifies a mismatch, expose DEFECT.
    for cert in internal:
        if verify_refuter_certificate(candidate, cert):
            return BackdoorResult("DEFECT", internal, frontier, visited, "internal local defect")
    for cert in frontier:
        if verify_frontier(candidate, cert):
            return BackdoorResult("DEFECT", internal, frontier, visited, "certified 2-SAT frontier mismatch")

    return BackdoorResult("NO_DEFECT", internal, frontier, visited, "all tested local/frontier equations agree")


def main() -> None:
    # 2-CNF root: no branching required.  This was HOLD for unit-only closure.
    f2 = normalize(((1, 2),))
    r2 = build_backdoor_support(f2, (1, 2), const_false, ())
    assert brute_sat(f2, (1, 2))
    assert r2.status == "DEFECT", r2
    assert r2.visited == 1
    print(f"2-CNF root: status={r2.status}, visited={r2.visited}")

    # One-variable backdoor: restricting x1 turns the 3-CNF root into 2-CNF.
    f1 = normalize(((1, 2, 3), (-1, 2, 3)))
    r1 = build_backdoor_support(f1, (1, 2, 3), const_false, (1,))
    assert brute_sat(f1, (1, 2, 3))
    assert r1.status == "DEFECT", r1
    assert r1.visited <= 3
    print(
        f"1-backdoor 3-CNF: status={r1.status}, visited={r1.visited}, "
        f"frontier={len(r1.frontier_support)}"
    )

    # Two disjoint 3-clauses need both declared variables to reach 2-CNF on
    # every branch.  A one-variable declaration must fail closed.
    fdis = normalize(((1, 2, 3), (4, 5, 6)))
    hold = build_backdoor_support(fdis, (1, 2, 3, 4, 5, 6), const_false, (1,))
    assert hold.status == "HOLD", hold
    good = build_backdoor_support(fdis, (1, 2, 3, 4, 5, 6), const_false, (1, 4))
    assert brute_sat(fdis, (1, 2, 3, 4, 5, 6))
    assert good.status == "DEFECT", good
    assert good.visited <= 7
    print(
        f"disjoint-3clauses: one-backdoor={hold.status}, "
        f"two-backdoor={good.status}, visited={good.visited}"
    )

    # Exact candidate should expose no false defect under a certified frontier.
    exact = build_backdoor_support(f1, (1, 2, 3), brute_sat, (1,))
    assert exact.status == "NO_DEFECT", exact
    print(f"exact-candidate control: status={exact.status}, visited={exact.visited}")

    print("tractable frontier support: PASS")
    print("k-backdoor support visits at most 2^(k+1)-1 states; k=O(log n) is polynomial")
    print("frontiers outside the certified tractable class return HOLD")
    print("tier=finite_diagnostic; unrestricted lineage backdoor theorem=OPEN; P!=NP=NOT CLAIMED")


if __name__ == "__main__":
    main()
