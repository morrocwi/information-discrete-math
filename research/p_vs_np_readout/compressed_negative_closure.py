#!/usr/bin/env python3
"""Memoized negative-closure audit for SAT-style restriction trees.

Given a candidate C with C(F)=0, recursively inspect both restrictions.  The
procedure either finds a concrete local/leaf defect or builds a finite DAG whose
leaves are syntactic contradictions.  The DAG is independently checkable and
may share identical restricted states.

This is a finite exact diagnostic / proof object for a branching closure model.
It does NOT show that arbitrary UNSAT instances have polynomial-size closure
DAGs and does NOT prove P != NP.
"""
from __future__ import annotations

from typing import Callable

from sat_one_sided_audit import normalize, restrict, leaf_truth, brute_sat

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
State = tuple[CNF, tuple[int, ...]]
Candidate = Callable[[CNF, tuple[int, ...]], bool]


def syntactic_reject(cnf: CNF) -> bool:
    return any(len(c) == 0 for c in cnf)


def state_key(cnf: CNF, remaining: tuple[int, ...]) -> State:
    return normalize(cnf), tuple(remaining)


def audit_negative_claim(cnf: CNF, remaining: tuple[int, ...], candidate: Candidate) -> dict:
    root = state_key(cnf, remaining)
    claim_cache: dict[State, bool] = {}
    nodes: list[dict] = []
    memo_cert: dict[State, int] = {}

    def claim(state: State) -> bool:
        if state not in claim_cache:
            f, rem = state
            claim_cache[state] = bool(candidate(f, rem))
        return claim_cache[state]

    if claim(root):
        return {
            "status": "HOLD",
            "reason": "candidate does not make a negative claim at the root",
            "queries": len(claim_cache),
        }

    def certify(state: State):
        if state in memo_cert:
            return ("CERT", memo_cert[state])

        f, rem = state
        assert claim(state) is False

        if syntactic_reject(f):
            node_id = len(nodes)
            nodes.append({"kind": "leaf", "cnf": f, "remaining": rem})
            memo_cert[state] = node_id
            return ("CERT", node_id)

        if not rem:
            # With every declared variable assigned, the normalized formula is
            # either empty (true) or contains an empty clause (false).  Reaching
            # the true case while C says 0 is a concrete leaf defect.
            if leaf_truth(f):
                return (
                    "REFUTED",
                    {
                        "status": "REFUTED",
                        "kind": "leaf_error",
                        "cnf": f,
                        "remaining": rem,
                        "candidate_claim": False,
                        "queries": len(claim_cache),
                    },
                )
            raise AssertionError("terminal normalized CNF is neither true nor syntactically rejected")

        v = rem[0]
        tail = rem[1:]
        left_state = state_key(restrict(f, v, False), tail)
        right_state = state_key(restrict(f, v, True), tail)
        c0 = claim(left_state)
        c1 = claim(right_state)

        if c0 or c1:
            return (
                "REFUTED",
                {
                    "status": "REFUTED",
                    "kind": "local_defect",
                    "cnf": f,
                    "remaining": rem,
                    "variable": v,
                    "parent_claim": False,
                    "child_claims": (c0, c1),
                    "queries": len(claim_cache),
                },
            )

        ltag, lpayload = certify(left_state)
        if ltag == "REFUTED":
            return ltag, lpayload
        rtag, rpayload = certify(right_state)
        if rtag == "REFUTED":
            return rtag, rpayload

        node_id = len(nodes)
        nodes.append(
            {
                "kind": "split",
                "cnf": f,
                "remaining": rem,
                "variable": v,
                "left": lpayload,
                "right": rpayload,
            }
        )
        memo_cert[state] = node_id
        return ("CERT", node_id)

    tag, payload = certify(root)
    if tag == "REFUTED":
        return payload

    cert = {"root": payload, "nodes": nodes}
    assert verify_negative_closure(cnf, remaining, cert)
    return {
        "status": "CERTIFIED_NEGATIVE",
        "certificate": cert,
        "unique_nodes": len(nodes),
        "unfolded_nodes": unfolded_size(cert, payload),
        "queries": len(claim_cache),
    }


def verify_negative_closure(cnf: CNF, remaining: tuple[int, ...], cert: dict) -> bool:
    nodes = cert.get("nodes")
    root_id = cert.get("root")
    if not isinstance(nodes, list) or not isinstance(root_id, int):
        return False
    if not (0 <= root_id < len(nodes)):
        return False

    expected_root = state_key(cnf, remaining)
    proven_false: list[bool] = [False] * len(nodes)
    states: list[State] = []

    for i, node in enumerate(nodes):
        try:
            f = normalize(tuple(tuple(c) for c in node["cnf"]))
            rem = tuple(node["remaining"])
        except Exception:
            return False
        st = (f, rem)
        states.append(st)

        if node.get("kind") == "leaf":
            if not syntactic_reject(f):
                return False
            proven_false[i] = True
            continue

        if node.get("kind") != "split" or not rem:
            return False
        v = node.get("variable")
        if v != rem[0]:
            return False
        li = node.get("left")
        ri = node.get("right")
        if not isinstance(li, int) or not isinstance(ri, int):
            return False
        if not (0 <= li < i and 0 <= ri < i):
            return False
        tail = rem[1:]
        expected_l = state_key(restrict(f, v, False), tail)
        expected_r = state_key(restrict(f, v, True), tail)
        if states[li] != expected_l or states[ri] != expected_r:
            return False
        if not (proven_false[li] and proven_false[ri]):
            return False
        proven_false[i] = True

    return states[root_id] == expected_root and proven_false[root_id]


def unfolded_size(cert: dict, node_id: int) -> int:
    node = cert["nodes"][node_id]
    if node["kind"] == "leaf":
        return 1
    return 1 + unfolded_size(cert, node["left"]) + unfolded_size(cert, node["right"])


def const_false(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    return False


def root_false_children_true(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    # Deliberately inconsistent candidate used only as a local-defect control.
    return len(remaining) < 2


def main() -> None:
    # All four 2-variable clauses.  Restricting x1 either way yields the same
    # child ((x2),(-x2)); restricting x2 either way yields the same empty-clause
    # contradiction.  A memoized DAG therefore has 3 nodes versus 7 unfolded.
    shared_unsat = normalize(((1, 2), (-1, 2), (1, -2), (-1, -2)))
    exact = audit_negative_claim(shared_unsat, (1, 2), brute_sat)
    assert exact["status"] == "CERTIFIED_NEGATIVE", exact
    assert exact["unique_nodes"] == 3, exact
    assert exact["unfolded_nodes"] == 7, exact
    assert verify_negative_closure(shared_unsat, (1, 2), exact["certificate"])

    # Corrupt one leaf: a verifier must reject the manufactured certificate.
    bad = {
        "root": exact["certificate"]["root"],
        "nodes": [dict(n) for n in exact["certificate"]["nodes"]],
    }
    leaf_i = next(i for i, n in enumerate(bad["nodes"]) if n["kind"] == "leaf")
    bad["nodes"][leaf_i]["cnf"] = ()
    assert not verify_negative_closure(shared_unsat, (1, 2), bad)

    # False negative on a satisfiable formula must eventually expose a true leaf.
    sat_formula = normalize(((1, 2),))
    false_negative = audit_negative_claim(sat_formula, (1, 2), const_false)
    assert false_negative["status"] == "REFUTED", false_negative
    assert false_negative["kind"] == "leaf_error", false_negative

    # A parent-0 / child-1 inconsistency is caught locally.
    local = audit_negative_claim(shared_unsat, (1, 2), root_false_children_true)
    assert local["status"] == "REFUTED", local
    assert local["kind"] == "local_defect", local

    print("compressed negative closure: exact finite diagnostic")
    print(
        "shared UNSAT fixture: "
        f"unique_nodes={exact['unique_nodes']} unfolded_nodes={exact['unfolded_nodes']} "
        f"candidate_queries={exact['queries']}"
    )
    print(f"false-negative control -> {false_negative['kind']}")
    print(f"local-consistency control -> {local['kind']}")
    print("corrupted-certificate control -> REJECT")
    print("tier=finite_diagnostic; universal polynomial closure size=OPEN; P!=NP=NOT CLAIMED")


if __name__ == "__main__":
    main()
