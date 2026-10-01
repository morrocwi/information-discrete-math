#!/usr/bin/env python3
"""Exact finite audit: tiny defect alphabet does not imply cheap defect search.

For SAT restriction recursion, an internal local-defect certificate is decided
entirely by the triple

    (C(F), C(F|x=0), C(F|x=1)),

so there are only 8 internal signature types.  A terminal boundary certificate
is decided by (C(F), leaf_truth(F)), so there are only 4 boundary types.
Hence an omniscient representative support needs at most 12 states.

The catch is construction cost.  This diagnostic uses the candidate C=0 and a
CNF with a unique satisfying assignment at the last DFS leaf.  C=0 has no
internal recursion defects anywhere; the only refuter is the satisfying leaf.
A left-first exact search therefore scans the full restriction tree before it
finds the defect, even though the final signature support is constant-size.

This is the readout/construction-cost guard:

    small certificate alphabet != efficient certificate constructor.

No SAT/circuit lower bound is claimed.
"""
from __future__ import annotations

from collections.abc import Callable

from sat_one_sided_audit import normalize, restrict, leaf_truth, brute_sat

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Candidate = Callable[[CNF, tuple[int, ...]], bool]
State = tuple[CNF, tuple[int, ...]]


def const_false(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    return False


def no_empty_clause(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    return not any(len(c) == 0 for c in normalize(cnf))


def enumerate_states(cnf: CNF, remaining: tuple[int, ...]) -> list[State]:
    """Preorder DFS over the complete declared restriction tree."""
    f = normalize(cnf)
    rem = tuple(remaining)
    out: list[State] = [(f, rem)]
    if not rem:
        return out
    v = rem[0]
    tail = rem[1:]
    out.extend(enumerate_states(restrict(f, v, False), tail))
    out.extend(enumerate_states(restrict(f, v, True), tail))
    return out


def local_signature(state: State, candidate: Candidate) -> tuple:
    f, rem = state
    c = bool(candidate(f, rem))
    if not rem:
        return ("B", c, leaf_truth(f))
    v = rem[0]
    tail = rem[1:]
    f0 = normalize(restrict(f, v, False))
    f1 = normalize(restrict(f, v, True))
    c0 = bool(candidate(f0, tail))
    c1 = bool(candidate(f1, tail))
    return ("I", c, c0, c1)


def signature_is_defect(sig: tuple) -> bool:
    if sig[0] == "B":
        _, c, target = sig
        return c != target
    _, c, c0, c1 = sig
    return c != (c0 or c1)


def signature_support(states: list[State], candidate: Candidate) -> dict[tuple, State]:
    """One representative per observed local signature (omniscient audit)."""
    reps: dict[tuple, State] = {}
    for st in states:
        reps.setdefault(local_signature(st, candidate), st)
    assert len(reps) <= 12
    return reps


def first_defect_scan(states: list[State], candidate: Candidate) -> tuple[int | None, State | None, tuple | None]:
    for i, st in enumerate(states, start=1):
        sig = local_signature(st, candidate)
        if signature_is_defect(sig):
            return i, st, sig
    return None, None, None


def unique_all_true_formula(n: int) -> tuple[CNF, tuple[int, ...]]:
    """CNF x1 & ... & xn: exactly one satisfying assignment, all True."""
    return normalize(tuple((i,) for i in range(1, n + 1))), tuple(range(1, n + 1))


def audit_unique_witness_search(max_n: int = 10) -> None:
    print("unique-witness constant-false search-cost guard")
    for n in range(1, max_n + 1):
        f, rem = unique_all_true_formula(n)
        states = enumerate_states(f, rem)
        expected = (1 << (n + 1)) - 1
        assert len(states) == expected
        assert brute_sat(f, rem)
        assert not const_false(f, rem)

        scanned, st, sig = first_defect_scan(states, const_false)
        assert scanned == expected, (n, scanned, expected, st, sig)
        assert sig == ("B", False, True)

        reps = signature_support(states, const_false)
        hit_types = [s for s in reps if signature_is_defect(s)]
        assert hit_types == [("B", False, True)]
        # Despite scanning exponentially many states, the final support has
        # only the internal nondefect plus false/true boundary signatures.
        assert len(reps) <= 3
        capture = len(hit_types) / len(reps)
        print(
            f"n={n:2d} full_tree={expected:5d} first_defect_scan={scanned:5d} "
            f"signature_support={len(reps)} uniform_capture={capture:.3f}"
        )


def audit_signature_invariance() -> None:
    # A small pair of candidates: one exact and one cheap syntactic heuristic.
    f = normalize(((1, 2), (-1, 2), (1, -2)))
    rem = (1, 2)
    states = enumerate_states(f, rem)

    exact_reps = signature_support(states, brute_sat)
    assert not any(signature_is_defect(s) for s in exact_reps)

    cheap_reps = signature_support(states, no_empty_clause)
    cheap_hits = [s for s in cheap_reps if signature_is_defect(s)]
    assert cheap_hits
    assert len(exact_reps) <= 12 and len(cheap_reps) <= 12
    print(
        "signature alphabet audit: "
        f"exact_types={len(exact_reps)} cheap_types={len(cheap_reps)} "
        f"cheap_defect_types={len(cheap_hits)}"
    )


def main() -> None:
    audit_signature_invariance()
    audit_unique_witness_search()
    print("defect signature support audit: PASS")
    print("observed signature support <=12, but exact support construction can scan 2^(n+1)-1 states")
    print("tier=finite_diagnostic; efficient lineage hitting-support constructor=OPEN")
    print("P!=NP=NOT CLAIMED")


if __name__ == "__main__":
    main()
