#!/usr/bin/env python3
"""Exact tiny-instance checker for the Fusion/Horn normal form.

For every non-trivial Boolean function on two input bits:
  * build the DeMorgan literal generator family;
  * enumerate every semi-filter over U=A^c;
  * keep the semi-filters above at least one positive input;
  * build the fusion cover graph;
  * solve its minimum set cover exactly;
  * verify the chosen pair family again by forward Horn closure.

The ground set has four points. Since A is non-trivial, |U|<=3, so exhaustive
semi-filter enumeration is tiny. Tier: exact finite diagnostic, not an
asymptotic circuit lower bound.
"""

from itertools import combinations_with_replacement


def pointset_all(m):
    return (1 << (1 << m)) - 1


def literal_generators(m):
    gamma = pointset_all(m)
    out = []
    for i in range(m):
        pos = 0
        for x in range(1 << m):
            if (x >> i) & 1:
                pos |= 1 << x
        out.append(pos)
        out.append(gamma ^ pos)
    return out


def subsets_of(mask):
    elems = [i for i in range(mask.bit_length()) if (mask >> i) & 1]
    out = []
    for code in range(1 << len(elems)):
        s = 0
        for j, e in enumerate(elems):
            if (code >> j) & 1:
                s |= 1 << e
        out.append(s)
    return out


def is_subset(a, b):
    return (a & ~b) == 0


def enumerate_semifilters(U):
    subs = subsets_of(U)
    fams = []
    # At |U|<=3 there are at most 8 subset-atoms and hence 256 families.
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


def seeds_above(a, U, generators):
    return frozenset(B & U for B in generators if (B >> a) & 1)


def above_some_positive(F, A, U, generators, m):
    for a in range(1 << m):
        if (A >> a) & 1:
            if all(s in F for s in seeds_above(a, U, generators)):
                return True
    return False


def pair_cover_mask(pair, filters):
    E, H = pair
    I = E & H
    mask = 0
    for j, F in enumerate(filters):
        if E in F and H in F and I not in F:
            mask |= 1 << j
    return mask


def exact_min_cover(cover_masks, universe_mask):
    if universe_mask == 0:
        return []

    # Remove zero and duplicate cover sets; keep one representative index.
    rep = {}
    for i, c in enumerate(cover_masks):
        if c:
            rep.setdefault(c, i)
    unique = [(c, i) for c, i in rep.items()]

    by_bit = {}
    for b in range(universe_mask.bit_length()):
        bit = 1 << b
        if universe_mask & bit:
            by_bit[b] = [(c, i) for c, i in unique if c & bit]

    best = [None]

    def dfs(covered, chosen):
        if covered == universe_mask:
            if best[0] is None or len(chosen) < len(best[0]):
                best[0] = chosen[:]
            return
        if best[0] is not None and len(chosen) >= len(best[0]):
            return

        uncovered = universe_mask & ~covered
        bits = [b for b in by_bit if uncovered & (1 << b)]
        # Hardest uncovered filter first.
        b = min(bits, key=lambda z: len(by_bit[z]))
        for c, original_i in by_bit[b]:
            dfs(covered | c, chosen + [original_i])

    dfs(0, [])
    if best[0] is None:
        raise AssertionError("cover graph has uncovered filter with no violating pair")
    return best[0]


def upward_close(F, U):
    subs = subsets_of(U)
    out = set(F)
    changed = True
    while changed:
        changed = False
        for s in list(out):
            for t in subs:
                if is_subset(s, t) and t not in out:
                    out.add(t)
                    changed = True
    return out


def horn_closure(a, U, generators, pairs):
    F = upward_close(seeds_above(a, U, generators), U)
    changed = True
    while changed:
        changed = False
        for E, H in pairs:
            if E in F and H in F:
                I = E & H
                if I not in F:
                    F.add(I)
                    F = upward_close(F, U)
                    changed = True
    return frozenset(F)


def cover_complexity_two_bit(A):
    m = 2
    gamma = pointset_all(m)
    if A in (0, gamma):
        raise ValueError("target must be non-trivial")
    U = gamma ^ A
    generators = literal_generators(m)
    semifilters = enumerate_semifilters(U)
    filters = [
        F for F in semifilters
        if above_some_positive(F, A, U, generators, m)
    ]

    subs = subsets_of(U)
    pairs = list(combinations_with_replacement(subs, 2))
    cover_masks = [pair_cover_mask(p, filters) for p in pairs]
    universe_mask = (1 << len(filters)) - 1
    chosen_idx = exact_min_cover(cover_masks, universe_mask)
    chosen = [pairs[i] for i in chosen_idx]

    # Horn-normal-form verification: the selected pair family must derive
    # bottom for every positive point.
    for a in range(1 << m):
        if (A >> a) & 1:
            cl = horn_closure(a, U, generators, chosen)
            assert 0 in cl, (A, a, chosen, cl)

    return len(chosen), len(filters), chosen


def tt(fn, m=2):
    out = 0
    for x in range(1 << m):
        if fn(x):
            out |= 1 << x
    return out


def main():
    gamma = pointset_all(2)
    rows = []
    for A in range(1, gamma):
        rho, nf, chosen = cover_complexity_two_bit(A)
        rows.append((A, rho, nf))

    named = {
        "AND": tt(lambda x: ((x & 1) and ((x >> 1) & 1))),
        "OR": tt(lambda x: ((x & 1) or ((x >> 1) & 1))),
        "XOR": tt(lambda x: ((x & 1) ^ ((x >> 1) & 1))),
        "EQ": tt(lambda x: ((x & 1) == ((x >> 1) & 1))),
    }

    print("exact finite diagnostic: ACCEPT")
    print("all 14 non-trivial two-bit Boolean functions checked")
    print("A_truth_table_hex  rho  #semi-filters-above")
    for A, rho, nf in rows:
        print(f"0x{A:x} {rho:3d} {nf:3d}")
    print("named controls:")
    for name, A in named.items():
        rho, nf, _ = cover_complexity_two_bit(A)
        print(f"  {name:4s}: rho={rho}, filters={nf}")

    # Sanity controls: OR can be made with unions only, so intersection/cover
    # complexity is zero; AND requires one intersection.
    assert cover_complexity_two_bit(named["OR"])[0] == 0
    assert cover_complexity_two_bit(named["AND"])[0] == 1
    print("sanity controls OR->0 and AND->1 passed")


if __name__ == "__main__":
    main()
