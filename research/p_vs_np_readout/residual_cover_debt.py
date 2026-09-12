#!/usr/bin/env python3
"""Exact residual-cover-debt diagnostic for the P-vs-NP readout lane.

The adversary state is no longer raw survivor cardinality.  It is the exact
minimum number of additional fusion pairs required to cover the semi-filters
that survive the current prefix.

Set-cover structure gives a genuine one-step capacity law: adding one candidate
cover set can reduce the residual minimum cover number by at most one.  This
script verifies the law exhaustively on small fusion instances and supplies a
3-input fixture whose debt follows 2 -> 1 -> 0 along an optimal prefix.

This is a finite exact diagnostic and a concrete capacity instance for the
fusion/intersection model.  It is NOT a superpolynomial SAT lower bound or a
P != NP proof.
"""
from __future__ import annotations

from itertools import combinations, combinations_with_replacement


def pointset_all(m: int) -> int:
    return (1 << (1 << m)) - 1


def literal_generators(m: int) -> list[int]:
    gamma = pointset_all(m)
    out: list[int] = []
    for i in range(m):
        pos = 0
        for x in range(1 << m):
            if (x >> i) & 1:
                pos |= 1 << x
        out.extend((pos, gamma ^ pos))
    return out


def subsets_of(mask: int) -> list[int]:
    elems = [i for i in range(mask.bit_length()) if (mask >> i) & 1]
    out: list[int] = []
    for code in range(1 << len(elems)):
        s = 0
        for j, e in enumerate(elems):
            if (code >> j) & 1:
                s |= 1 << e
        out.append(s)
    return out


def is_subset(a: int, b: int) -> bool:
    return (a & ~b) == 0


def enumerate_semifilters(U: int) -> list[frozenset[int]]:
    subs = subsets_of(U)
    fams: list[frozenset[int]] = []
    for code in range(1 << len(subs)):
        if code == 0:
            continue
        F = frozenset(subs[i] for i in range(len(subs)) if (code >> i) & 1)
        if 0 in F:
            continue
        ok = True
        for s in F:
            for t in subs:
                if is_subset(s, t) and t not in F:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            fams.append(F)
    return fams


def seeds_above(a: int, U: int, generators: list[int]) -> frozenset[int]:
    return frozenset(B & U for B in generators if (B >> a) & 1)


def above_some_positive(
    F: frozenset[int], A: int, U: int, generators: list[int], m: int
) -> bool:
    for a in range(1 << m):
        if (A >> a) & 1:
            if all(s in F for s in seeds_above(a, U, generators)):
                return True
    return False


def pair_cover_mask(pair: tuple[int, int], filters: list[frozenset[int]]) -> int:
    E, H = pair
    I = E & H
    mask = 0
    for j, F in enumerate(filters):
        if E in F and H in F and I not in F:
            mask |= 1 << j
    return mask


def exact_min_cover_masks(cover_masks: list[int], universe_mask: int) -> list[int]:
    if universe_mask == 0:
        return []

    rep: dict[int, int] = {}
    for i, c in enumerate(cover_masks):
        c &= universe_mask
        if c:
            rep.setdefault(c, i)
    unique = [(c, i) for c, i in rep.items()]

    by_bit: dict[int, list[tuple[int, int]]] = {}
    for b in range(universe_mask.bit_length()):
        bit = 1 << b
        if universe_mask & bit:
            choices = [(c, i) for c, i in unique if c & bit]
            if not choices:
                raise AssertionError("uncoverable residual filter")
            by_bit[b] = choices

    best: list[list[int] | None] = [None]

    def dfs(covered: int, chosen: list[int]) -> None:
        if covered == universe_mask:
            if best[0] is None or len(chosen) < len(best[0]):
                best[0] = chosen[:]
            return
        if best[0] is not None and len(chosen) >= len(best[0]):
            return
        uncovered = universe_mask & ~covered
        bits = [b for b in by_bit if uncovered & (1 << b)]
        b = min(bits, key=lambda z: len(by_bit[z]))
        for c, original_i in by_bit[b]:
            dfs(covered | c, chosen + [original_i])

    dfs(0, [])
    assert best[0] is not None
    return best[0]


def build_instance(m: int, A: int):
    gamma = pointset_all(m)
    U = gamma ^ A
    generators = literal_generators(m)
    filters = [
        F
        for F in enumerate_semifilters(U)
        if above_some_positive(F, A, U, generators, m)
    ]
    subs = subsets_of(U)
    pairs = list(combinations_with_replacement(subs, 2))
    masks = [pair_cover_mask(p, filters) for p in pairs]
    all_filters = (1 << len(filters)) - 1
    return U, filters, pairs, masks, all_filters


def residual_debt(cover_masks: list[int], survivor_mask: int) -> tuple[int, list[int]]:
    chosen = exact_min_cover_masks(cover_masks, survivor_mask)
    return len(chosen), chosen


def apply_pair(survivor_mask: int, cover_mask: int) -> int:
    return survivor_mask & ~cover_mask


def exhaust_one_step_capacity(cover_masks: list[int], survivor_mask: int) -> None:
    d, _ = residual_debt(cover_masks, survivor_mask)
    for c in cover_masks:
        after = apply_pair(survivor_mask, c)
        d2, _ = residual_debt(cover_masks, after)
        assert d2 <= d
        assert d <= d2 + 1, (d, d2, survivor_mask, c)


def three_bit_fixture() -> dict:
    m = 3
    gamma = pointset_all(m)
    # Negative points are 011,101,110: exactly the weight-2 assignments.
    U_points = (3, 5, 6)
    U = sum(1 << p for p in U_points)
    A = gamma ^ U
    _, filters, pairs, masks, survivors = build_instance(m, A)

    d0, opt0 = residual_debt(masks, survivors)
    assert d0 == 2
    exhaust_one_step_capacity(masks, survivors)

    first = opt0[0]
    survivors1 = apply_pair(survivors, masks[first])
    d1, opt1 = residual_debt(masks, survivors1)
    assert d1 == 1
    exhaust_one_step_capacity(masks, survivors1)

    second = opt1[0]
    survivors2 = apply_pair(survivors1, masks[second])
    d2, _ = residual_debt(masks, survivors2)
    assert d2 == 0

    return {
        "m": m,
        "negative_points": U_points,
        "target_truth_mask": hex(A),
        "semifilters": len(filters),
        "candidate_pairs": len(pairs),
        "debt_trace": (d0, d1, d2),
        "chosen_pairs": (pairs[first], pairs[second]),
    }


def exhaustive_small_family() -> dict:
    # Keep |U|<=3 so semi-filter enumeration remains tiny.  This covers all
    # two-input nontrivial targets and every three-input target with at most
    # three negative points.
    checked_states = 0
    max_initial_debt = 0
    examples = []
    for m in (2, 3):
        gamma = pointset_all(m)
        max_u = min(3, (1 << m) - 1)
        for k in range(1, max_u + 1):
            for U_points in combinations(range(1 << m), k):
                U = sum(1 << p for p in U_points)
                A = gamma ^ U
                _, filters, pairs, masks, survivors = build_instance(m, A)
                d, _ = residual_debt(masks, survivors)
                max_initial_debt = max(max_initial_debt, d)
                exhaust_one_step_capacity(masks, survivors)
                checked_states += 1
                if d >= 2:
                    examples.append((m, U_points, d, len(filters)))
    return {
        "instances_checked": checked_states,
        "max_initial_debt": max_initial_debt,
        "debt_ge_2_examples": examples[:8],
    }


def main() -> None:
    fam = exhaustive_small_family()
    fix = three_bit_fixture()
    print("residual fusion-cover debt: exact finite diagnostic")
    print(f"family={fam}")
    print(f"three_bit_fixture={fix}")
    print("verified: for every checked residual state and candidate pair, d_before <= d_after + 1")
    print("verified fixture: debt 2 -> 1 -> 0 along an optimal two-pair prefix")
    print("tier=finite_diagnostic; unrestricted SAT lower bound=NOT CLAIMED")


if __name__ == "__main__":
    main()
