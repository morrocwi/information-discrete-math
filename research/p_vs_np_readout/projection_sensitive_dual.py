#!/usr/bin/env python3
"""Projection-sensitive residual-cover dual diagnostic.

The input object is a finite relation R(x,w).  We first perform the declared
existential readout

    f(x) = exists_w R(x,w),

and only then build the residual fusion-cover instance for f.  Hence relation
representations with the same existential projection receive exactly the same
cover debt / dual certificate.

This is the Readout-Genesis guard needed to avoid charging witness distinctions
that disappear at the declared downstream readout.

Tier: exact finite diagnostic.  No asymptotic SAT lower bound or P != NP claim.
"""
from __future__ import annotations

from fractions import Fraction as Q
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from idm.combopt import linear_program
from residual_cover_debt import build_instance, residual_debt, pointset_all


def projected_truth_mask(m: int, witnesses: tuple[int, ...], rel) -> int:
    mask = 0
    for x in range(1 << m):
        if any(rel(x, w) for w in witnesses):
            mask |= 1 << x
    return mask


def exact_projected_certificate(m: int, target_mask: int) -> dict:
    gamma = pointset_all(m)
    if target_mask == gamma:
        return {
            "target_mask": target_mask,
            "integral_debt": 0,
            "dual_mass": Q(0),
            "filters": 0,
            "status": "CERTIFIED",
        }

    U = gamma ^ target_mask
    # This finite checker intentionally stays in the tiny regime used by the
    # residual-cover fixture, where semi-filter enumeration is exact.
    if U.bit_count() > 3:
        return {
            "target_mask": target_mask,
            "integral_debt": None,
            "dual_mass": None,
            "filters": None,
            "status": "HOLD",
            "reason": "negative-set size exceeds exact tiny-fixture budget",
        }

    _, filters, pairs, cover_masks, survivors = build_instance(m, target_mask)
    debt, _ = residual_debt(cover_masks, survivors)
    nf = len(filters)
    if nf == 0:
        dual = Q(0)
    else:
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
        dual = Q(sol["objective"])
        assert all(v >= 0 for v in y)
        for mask in cover_masks:
            load = sum((y[j] for j in range(nf) if mask & (1 << j)), Q(0))
            assert load <= 1
        assert sum(y, Q(0)) == dual
        assert dual <= debt

    return {
        "target_mask": target_mask,
        "integral_debt": debt,
        "dual_mass": dual,
        "filters": nf,
        "status": "CERTIFIED",
    }


def equality_collapse(m: int) -> dict:
    ws = tuple(range(1 << m))
    A = projected_truth_mask(m, ws, lambda x, w: x == w)
    cert = exact_projected_certificate(m, A)
    assert A == pointset_all(m)
    assert cert["integral_debt"] == 0
    assert cert["dual_mass"] == 0
    return cert


def representation_invariance_fixture() -> tuple[dict, dict]:
    # Reuse the exact 3-input target whose negative points are 011,101,110.
    m = 3
    gamma = pointset_all(m)
    U = sum(1 << p for p in (3, 5, 6))
    target = gamma ^ U

    # Two extensionally different witness relations with the same projection.
    A1 = projected_truth_mask(
        m,
        (0, 1),
        lambda x, w: bool((target >> x) & 1) and w == 0,
    )
    A2 = projected_truth_mask(
        m,
        (0, 1),
        lambda x, w: bool((target >> x) & 1),
    )
    assert A1 == target == A2

    c1 = exact_projected_certificate(m, A1)
    c2 = exact_projected_certificate(m, A2)
    assert c1 == c2
    assert c1["integral_debt"] == 2
    return c1, c2


def main() -> None:
    print("projection-sensitive residual dual diagnostic")
    for m in (1, 2, 3):
        c = equality_collapse(m)
        print(f"equality m={m}: projection=constant-1 debt={c['integral_debt']} dual={c['dual_mass']}")

    c1, c2 = representation_invariance_fixture()
    print(f"same-projection relation A: {c1}")
    print(f"same-projection relation B: {c2}")
    print("verified: witness-representation differences vanish before debt/dual accounting")
    print("verified: equality witness diversity projects to zero residual-cover debt")
    print("tier=exact_finite_diagnostic; unrestricted SAT lower bound=NOT CLAIMED")


if __name__ == "__main__":
    main()
