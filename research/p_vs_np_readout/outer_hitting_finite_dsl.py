#!/usr/bin/env python3
"""Exact finite outer-hitting synthesis for a small CNF-feature candidate DSL.

This diagnostic validates the complete refuter interface on a finite hypothesis
class.  Candidates are all 256 Boolean functions of three cheap syntactic CNF
features:

  e = formula contains an empty clause
  z = formula has zero clauses
  u = formula contains a unit clause

Each candidate therefore has an 8-bit truth table.  We enumerate valid small
restriction states over variables {x1,x2}, compute the local SAT fixed-point or
boundary defect predicate without a SAT oracle, and synthesize a minimum set of
states whose defect tests hit every candidate in the DSL.

Result for this declared finite universe: a 4-state support is sufficient and
minimal.  This is an end-to-end finite demonstration of

  candidate class -> outer hitting support -> local verifier -> refutation.

It is NOT an unrestricted circuit result and gives no asymptotic P != NP claim.
"""
from __future__ import annotations

from itertools import combinations

from sat_one_sided_audit import normalize, restrict, leaf_truth

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
State = tuple[CNF, tuple[int, ...]]


def clause_bank(vars_: tuple[int, ...]) -> list[Clause]:
    bank: list[Clause] = [()]
    for v in vars_:
        bank.extend([(v,), (-v,)])
    if len(vars_) >= 2:
        a, b = vars_[:2]
        bank.extend([(a, b), (a, -b), (-a, b), (-a, -b)])
    return bank


def all_valid_states() -> list[State]:
    states: list[State] = []
    for rem in ((1, 2), (1,), (2,), ()):
        bank = clause_bank(rem)
        seen: set[CNF] = set()
        for mask in range(1 << len(bank)):
            f = normalize(tuple(bank[i] for i in range(len(bank)) if (mask >> i) & 1))
            if f in seen:
                continue
            seen.add(f)
            states.append((f, rem))
    return states


def candidate(mask: int):
    def eval_candidate(cnf: CNF, remaining: tuple[int, ...]) -> bool:
        f = normalize(cnf)
        has_empty = any(len(c) == 0 for c in f)
        no_clauses = len(f) == 0
        has_unit = any(len(c) == 1 for c in f)
        idx = (4 if has_empty else 0) + (2 if no_clauses else 0) + (1 if has_unit else 0)
        return bool((mask >> idx) & 1)
    return eval_candidate


def is_local_defect(state: State, cand) -> bool:
    f, rem = state
    c = bool(cand(f, rem))
    if not rem:
        return c != leaf_truth(f)
    v = rem[0]
    tail = rem[1:]
    c0 = bool(cand(restrict(f, v, False), tail))
    c1 = bool(cand(restrict(f, v, True), tail))
    return c != (c0 or c1)


def coverage_mask(state: State, candidates) -> int:
    out = 0
    for i, cand in enumerate(candidates):
        if is_local_defect(state, cand):
            out |= 1 << i
    return out


def synthesize_minimum_support(states: list[State], candidates) -> list[State]:
    # States with identical candidate-coverage masks are interchangeable for
    # this finite set-cover problem; retain one representative per mask.
    representative: dict[int, State] = {}
    for st in states:
        cover = coverage_mask(st, candidates)
        if cover:
            representative.setdefault(cover, st)

    items = list(representative.items())
    full = (1 << len(candidates)) - 1
    for r in range(1, len(items) + 1):
        for inds in combinations(range(len(items)), r):
            covered = 0
            for j in inds:
                covered |= items[j][0]
            if covered == full:
                return [items[j][1] for j in inds]
    raise AssertionError("finite candidate class was not fully hit")


def main() -> None:
    states = all_valid_states()
    candidates = [candidate(mask) for mask in range(256)]
    support = synthesize_minimum_support(states, candidates)

    assert len(support) == 4, support
    full = (1 << len(candidates)) - 1
    covered = 0
    for st in support:
        covered |= coverage_mask(st, candidates)
    assert covered == full

    # Independent minimality check: no subset of at most three distinct
    # coverage types covers the full 256-candidate class.
    unique_masks = sorted({coverage_mask(st, candidates) for st in states if coverage_mask(st, candidates)})
    for r in range(1, 4):
        for combo in combinations(unique_masks, r):
            cov = 0
            for m in combo:
                cov |= m
            assert cov != full, (r, combo)

    print(f"candidate_DSL=256 states={len(states)} unique_coverage_types={len(unique_masks)}")
    print("minimum outer hitting support = 4 states")
    for i, (f, rem) in enumerate(support, start=1):
        hit = coverage_mask((f, rem), candidates).bit_count()
        print(f"  test{i}: cnf={f} remaining={rem} hits={hit}/256")
    print("outer finite DSL hitting synthesis: PASS")
    print("minimality=EXACT for declared finite universe")
    print("tier=finite_diagnostic; unrestricted outer lineage theorem=OPEN; P!=NP=NOT CLAIMED")


if __name__ == "__main__":
    main()
