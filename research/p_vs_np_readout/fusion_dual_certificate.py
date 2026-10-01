#!/usr/bin/env python3
"""Exact fractional dual certificates for finite Fusion/Horn cover instances.

The cover universe is the family of semi-filters above some positive point.
Each fusion pair (E,H) covers exactly the semi-filters it violates.  The
fractional set-cover dual is

    maximize  sum_F y_F
    subject to sum_{F covered by pair p} y_F <= 1   for every p
               y_F >= 0.

Any exact feasible dual vector certifies rho >= sum_F y_F.  The LP is solved
with IDM's exact-rational simplex and then rechecked independently with
Fraction arithmetic.

Tier: exact finite certificate.  No asymptotic P-vs-NP claim.
"""

from fractions import Fraction as Q
from itertools import combinations_with_replacement
from pathlib import Path
import sys

# When executed as `python3 research/p_vs_np_readout/fusion_dual_certificate.py`,
# Python places this script directory, not necessarily the repository root, at
# sys.path[0].  Insert the root explicitly so the test always exercises the
# checked-out `idm` package rather than relying on an installed copy.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from idm.combopt import linear_program
from fusion_horn_exact import (
    pointset_all,
    literal_generators,
    subsets_of,
    enumerate_semifilters,
    above_some_positive,
    pair_cover_mask,
    exact_min_cover,
    tt,
)


def instance(A, m=2):
    gamma = pointset_all(m)
    if A in (0, gamma):
        raise ValueError("target must be non-trivial")
    U = gamma ^ A
    generators = literal_generators(m)
    filters = [
        F for F in enumerate_semifilters(U)
        if above_some_positive(F, A, U, generators, m)
    ]
    subs = subsets_of(U)
    pairs = list(combinations_with_replacement(subs, 2))
    cover_masks = [pair_cover_mask(p, filters) for p in pairs]
    return U, filters, pairs, cover_masks


def exact_integral_rho(cover_masks, nfilters):
    chosen = exact_min_cover(cover_masks, (1 << nfilters) - 1)
    return len(chosen)


def exact_dual(A, m=2):
    U, filters, pairs, cover_masks = instance(A, m)
    nf = len(filters)
    if nf == 0:
        return {
            "objective": Q(0), "weights": [], "rho": 0,
            "filters": filters, "pairs": pairs, "cover_masks": cover_masks,
        }

    c = [Q(1)] * nf
    A_lp = []
    b_lp = []
    for mask in cover_masks:
        if mask == 0:
            continue
        A_lp.append([Q(1) if mask & (1 << j) else Q(0) for j in range(nf)])
        b_lp.append(Q(1))

    sol = linear_program(c, A_lp, b_lp, sense="max")
    assert sol["status"] == "optimal", sol
    y = [Q(v) for v in sol["x"]]
    obj = Q(sol["objective"])

    # Independent exact certificate check.
    assert all(v >= 0 for v in y)
    for mask in cover_masks:
        load = sum((y[j] for j in range(nf) if mask & (1 << j)), Q(0))
        assert load <= 1, (mask, load)
    assert sum(y, Q(0)) == obj

    rho = exact_integral_rho(cover_masks, nf)
    assert obj <= rho

    return {
        "objective": obj,
        "weights": y,
        "rho": rho,
        "filters": filters,
        "pairs": pairs,
        "cover_masks": cover_masks,
    }


def main():
    gamma = pointset_all(2)
    gaps = []
    print("exact fusion-cover LP-dual certificates")
    print("truth  rho  dual     gap")
    for A in range(1, gamma):
        r = exact_dual(A)
        gap = Q(r["rho"]) - r["objective"]
        gaps.append(gap)
        print(f"0x{A:x}   {r['rho']:2d}   {str(r['objective']):>7s}   {gap}")

    named = {
        "AND": tt(lambda x: ((x & 1) and ((x >> 1) & 1))),
        "OR": tt(lambda x: ((x & 1) or ((x >> 1) & 1))),
        "XOR": tt(lambda x: ((x & 1) ^ ((x >> 1) & 1))),
        "EQ": tt(lambda x: ((x & 1) == ((x >> 1) & 1))),
    }
    print("named controls:")
    for name, A in named.items():
        r = exact_dual(A)
        print(f"  {name:4s}: rho={r['rho']}, exact dual={r['objective']}")

    print("certificate check: ACCEPT")
    print(f"integrality gaps observed: {sorted(set(map(str, gaps)))}")
    print("Every reported dual objective is independently rechecked against every fusion-pair constraint.")


if __name__ == "__main__":
    main()
