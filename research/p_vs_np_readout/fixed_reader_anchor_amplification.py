#!/usr/bin/env python3
"""Exact finite audit: local readers alone do not amplify, world-bound anchors do.

This diagnostic uses the genuine <=2-gate DeMorgan circuit class from
``tiny_circuit_direct_sample_hitting.py`` (5,684 distinct functions on the
9-bit CNF-presence encoding for two semantic variables).

We compare two verifier families.

Internal readers
----------------
* terminal TRUE/FALSE boundaries;
* SAT restriction recursion C(F)=C(F|x=0) OR C(F|x=1);
* variable-swap / polarity symmetries;
* unit-propagation equivalences;
* subsumption-removal equivalences.

All of these are target-preserving identities.  Adding more such fixed readers
need not amplify a sparse wrong candidate: constant FALSE and constant TRUE
satisfy all internal identities and miss only one terminal boundary.

World-bound anchors
-------------------
* every satisfiable finite fixture is paired with an explicit satisfying
  assignment (the tiny benchmark enumerates it exactly);
* every fixture containing the empty clause has a direct syntactic UNSAT
  certificate.

These anchors are independently checkable and do not import a SAT answer as a
parameter.  In this finite universe they raise the minimum number of verified
defects from 1/3986 to 96/4337.

This is a finite calibration only.  It does NOT show inverse-polynomial margin
for arbitrary polynomial-size circuits: a large circuit can concentrate its
error on hard instances outside a fixed easy-anchor family.
"""
from __future__ import annotations

from itertools import product

from tiny_circuit_direct_sample_hitting import (
    BANK,
    BANK_INDEX,
    N_FORMULAS,
    ALL_FORMULA_BITS,
    target_table,
    restrict_mask,
    enumerate_demorgan_at_most_two_gates,
)


def bit(table: int, i: int) -> int:
    return (table >> i) & 1


def transform_clause(clause: tuple[int, ...], mapping: dict[int, int]) -> tuple[int, ...]:
    if not clause:
        return ()
    return tuple(sorted((mapping[x] for x in clause), key=lambda x: (abs(x), x < 0)))


def transform_mask(mask: int, mapping: dict[int, int]) -> int:
    out = 0
    for j, clause in enumerate(BANK):
        if (mask >> j) & 1:
            out |= 1 << BANK_INDEX[transform_clause(clause, mapping)]
    return out


def satisfying_assignment(mask: int) -> tuple[bool, bool] | None:
    for a1, a2 in product((False, True), repeat=2):
        assignment = {1: a1, 2: a2}
        ok = True
        for j, clause in enumerate(BANK):
            if not ((mask >> j) & 1):
                continue
            if not clause:
                ok = False
                break
            if not any(
                (lit > 0 and assignment[abs(lit)])
                or (lit < 0 and not assignment[abs(lit)])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return (a1, a2)
    return None


def build_internal_readers(target: int):
    boundary = [(0, bit(target, 0)), (1, bit(target, 1))]
    restriction = [
        (mask, var, restrict_mask(mask, var, False), restrict_mask(mask, var, True))
        for mask in range(N_FORMULAS)
        for var in (1, 2)
    ]

    symmetries: set[tuple[int, int]] = set()
    maps = (
        {1: 2, -1: -2, 2: 1, -2: -1},
        {1: -1, -1: 1, 2: 2, -2: -2},
        {1: 1, -1: -1, 2: -2, -2: 2},
    )
    for mapping in maps:
        for mask in range(N_FORMULAS):
            other = transform_mask(mask, mapping)
            if other != mask:
                symmetries.add(tuple(sorted((mask, other))))

    unit_pairs: set[tuple[int, int]] = set()
    for mask in range(N_FORMULAS):
        for unit_idx, var, value in ((1, 1, True), (2, 1, False), (3, 2, True), (4, 2, False)):
            if (mask >> unit_idx) & 1:
                other = restrict_mask(mask, var, value)
                if other != mask:
                    unit_pairs.add(tuple(sorted((mask, other))))

    clause_sets = [set(c) for c in BANK]
    subsumption_pairs: set[tuple[int, int]] = set()
    for mask in range(N_FORMULAS):
        present = [j for j in range(len(BANK)) if (mask >> j) & 1]
        for i in present:
            for j in present:
                if i != j and clause_sets[i].issubset(clause_sets[j]):
                    other = mask & ~(1 << j)
                    subsumption_pairs.add(tuple(sorted((mask, other))))

    # Sanity: every added identity is genuinely target-preserving.
    assert all(bit(target, a) == bit(target, b) for a, b in symmetries)
    assert all(bit(target, a) == bit(target, b) for a, b in unit_pairs)
    assert all(bit(target, a) == bit(target, b) for a, b in subsumption_pairs)

    return boundary, restriction, symmetries, unit_pairs, subsumption_pairs


def internal_defects(table: int, readers) -> int:
    boundary, restriction, symmetries, unit_pairs, subsumption_pairs = readers
    defects = 0
    for mask, truth in boundary:
        defects += bit(table, mask) != truth
    for mask, _var, r0, r1 in restriction:
        defects += bit(table, mask) != (bit(table, r0) | bit(table, r1))
    for a, b in symmetries:
        defects += bit(table, a) != bit(table, b)
    for a, b in unit_pairs:
        defects += bit(table, a) != bit(table, b)
    for a, b in subsumption_pairs:
        defects += bit(table, a) != bit(table, b)
    return defects


def anchor_defects(table: int, sat_anchors: list[int], empty_clause_anchors: list[int]) -> int:
    return sum(bit(table, m) == 0 for m in sat_anchors) + sum(
        bit(table, m) == 1 for m in empty_clause_anchors
    )


def main() -> None:
    target = target_table()
    _one, two = enumerate_demorgan_at_most_two_gates()
    candidates = sorted(two)
    assert len(candidates) == 5684
    assert target not in two

    readers = build_internal_readers(target)
    internal_total = sum((len(x) for x in readers))
    internal_counts = [internal_defects(c, readers) for c in candidates]
    assert min(internal_counts) == 1
    assert internal_total == 3986, internal_total

    # Positive world-bound anchors carry an explicit witness.  We store the
    # formula masks here; witness existence is independently rechecked below.
    sat_anchors = [m for m in range(N_FORMULAS) if satisfying_assignment(m) is not None]
    assert len(sat_anchors) == target.bit_count() == 95
    for m in sat_anchors:
        assert bit(target, m) == 1

    # Empty clause is a direct syntactic contradiction.
    empty_clause_anchors = [m for m in range(N_FORMULAS) if m & 1]
    assert len(empty_clause_anchors) == 256
    assert all(bit(target, m) == 0 for m in empty_clause_anchors)

    total = internal_total + len(sat_anchors) + len(empty_clause_anchors)
    counts = [
        internal_defects(c, readers) + anchor_defects(c, sat_anchors, empty_clause_anchors)
        for c in candidates
    ]
    minimum = min(counts)
    worst = [c for c, d in zip(candidates, counts) if d == minimum]
    assert minimum == 96, minimum
    assert len(worst) == 1 and worst[0] == 0  # constant FALSE
    assert total == 4337

    print(f"genuine_candidates={len(candidates)}")
    print(f"internal_reader_tests={internal_total} minimum_defects={min(internal_counts)}")
    print(f"internal_min_fraction={min(internal_counts) / internal_total:.12f}")
    print(f"sat_witness_anchors={len(sat_anchors)} empty_clause_anchors={len(empty_clause_anchors)}")
    print(f"anchored_tests={total} minimum_defects={minimum}")
    print(f"anchored_min_fraction={minimum / total:.12f}")
    print("worst_anchored_candidate=constant_FALSE")
    print("fixed reader + world-bound anchor amplification: PASS")
    print("tier=exact_finite_diagnostic; unrestricted inverse-poly margin=OPEN")
    print("SAT notin P/poly=NOT CLAIMED; P!=NP=NOT CLAIMED")


if __name__ == "__main__":
    main()
