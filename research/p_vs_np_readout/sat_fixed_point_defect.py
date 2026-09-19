#!/usr/bin/env python3
"""Exact finite localization of SAT fixed-point defects.

SAT is the unique labeling of a complete restriction tree satisfying both

    value(F) = value(F|x=0) OR value(F|x=1)

at internal nodes and direct truth at terminal leaves.  Given a candidate, this
script exhaustively searches one finite tree for either a local recursion defect
or a boundary defect.  If the candidate root is wrong, such a defect must exist.

The search may be exponential; this is a localization theorem/diagnostic, not
an efficient refuter and not a P != NP proof.
"""
from __future__ import annotations

from sat_one_sided_audit import (
    normalize,
    restrict,
    leaf_truth,
    brute_sat,
    no_empty_clause,
    const_true,
)


def const_false(cnf, remaining):
    return False


def find_first_defect(cnf, remaining, candidate):
    cnf = normalize(cnf)
    cache = {}
    visited = 0

    def claim(f, rem):
        key = (f, rem)
        if key not in cache:
            cache[key] = bool(candidate(f, rem))
        return cache[key]

    def walk(f, rem, path):
        nonlocal visited
        visited += 1
        parent = claim(f, rem)
        if not rem:
            target = leaf_truth(f)
            if parent != target:
                return {
                    "kind": "boundary_defect",
                    "path": tuple(path),
                    "formula": f,
                    "candidate": parent,
                    "target": target,
                }
            return None

        v = rem[0]
        tail = rem[1:]
        f0 = normalize(restrict(f, v, False))
        f1 = normalize(restrict(f, v, True))
        c0 = claim(f0, tail)
        c1 = claim(f1, tail)
        if parent != (c0 or c1):
            return {
                "kind": "local_recursion_defect",
                "path": tuple(path),
                "variable": v,
                "parent": parent,
                "children": (c0, c1),
            }

        left = walk(f0, tail, path + [(v, False)])
        if left is not None:
            return left
        return walk(f1, tail, path + [(v, True)])

    defect = walk(cnf, tuple(remaining), [])
    return {
        "defect": defect,
        "visited_tree_nodes": visited,
        "unique_candidate_queries": len(cache),
    }


def main():
    sat_formula = normalize(((1, 2), (-1, 2)))
    unsat_formula = normalize(((1,), (-1,)))

    exact_sat = find_first_defect(sat_formula, (1, 2), brute_sat)
    exact_unsat = find_first_defect(unsat_formula, (1, 2), brute_sat)
    assert exact_sat["defect"] is None
    assert exact_unsat["defect"] is None

    # Constant false satisfies every internal OR equation identically.  Its
    # error on a satisfiable instance is visible only at a true terminal leaf.
    zero_on_sat = find_first_defect(sat_formula, (1, 2), const_false)
    assert zero_on_sat["defect"]["kind"] == "boundary_defect"
    assert zero_on_sat["defect"]["candidate"] is False
    assert zero_on_sat["defect"]["target"] is True

    # Constant true also satisfies every internal OR equation identically; on
    # an UNSAT instance it is caught only by a false terminal boundary.
    one_on_unsat = find_first_defect(unsat_formula, (1, 2), const_true)
    assert one_on_unsat["defect"]["kind"] == "boundary_defect"
    assert one_on_unsat["defect"]["candidate"] is True
    assert one_on_unsat["defect"]["target"] is False

    cheap = find_first_defect(unsat_formula, (1, 2), no_empty_clause)
    assert cheap["defect"] is not None

    print("SAT fixed-point defect localization: exact finite diagnostic")
    print(f"exact SAT candidate on SAT fixture -> {exact_sat}")
    print(f"exact SAT candidate on UNSAT fixture -> {exact_unsat}")
    print(f"constant-false on SAT fixture -> {zero_on_sat}")
    print(f"constant-true on UNSAT fixture -> {one_on_unsat}")
    print(f"cheap candidate -> {cheap}")
    print("verified: recursion equations alone are insufficient; terminal boundary is load-bearing")
    print("tier=finite_diagnostic; efficient global defect search=OPEN; P!=NP=NOT CLAIMED")


if __name__ == "__main__":
    main()
