#!/usr/bin/env python3
"""Exact small Horn-closure search without semi-filter enumeration.

For a target A and literal generator basis, the fusion/Horn normal form says
rho(A) is the minimum number of subset-intersection rules whose least closure
derives bottom for every positive target point.

This diagnostic enumerates rule *families* directly for selected 3-input
functions.  It is intended as a search/calibration engine, not an asymptotic
lower bound.

Exact controls checked here:
  OR_3       : rho = 0
  MAJORITY_3 : rho = 2
  PARITY_3   : rho = 3

Parity is a mandatory negative control because parity has linear-size ordinary
Boolean circuits; no candidate readout measure may turn this finite pattern
into an unrestricted superpolynomial parity claim.
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from fusion_horn_exact import (
    horn_closure,
    literal_generators,
    pointset_all,
    subsets_of,
)


def truth_mask(m: int, fn) -> int:
    out = 0
    for x in range(1 << m):
        if fn(x):
            out |= 1 << x
    return out


def candidate_pairs(U: int) -> list[tuple[int, int]]:
    """All nontrivial unordered intersection pairs over subsets of U.

    Pairs whose intersection equals one parent cannot create a new Horn atom
    when both parents are present, so they are omitted without changing the
    minimum rule count.
    """
    subs = subsets_of(U)
    out = []
    for i, E in enumerate(subs):
        for H in subs[i:]:
            I = E & H
            if I == E or I == H:
                continue
            out.append((E, H))
    return out


def forces_bottom(A: int, m: int, pairs: tuple[tuple[int, int], ...]) -> bool:
    gamma = pointset_all(m)
    U = gamma ^ A
    gens = literal_generators(m)
    for a in range(1 << m):
        if (A >> a) & 1:
            if 0 not in horn_closure(a, U, gens, pairs):
                return False
    return True


def exact_rho(A: int, m: int, max_k: int) -> tuple[int, tuple[tuple[int, int], ...]]:
    gamma = pointset_all(m)
    if A in (0, gamma):
        raise ValueError("target must be nontrivial")
    pairs = candidate_pairs(gamma ^ A)

    for k in range(max_k + 1):
        for chosen in combinations(pairs, k):
            if forces_bottom(A, m, chosen):
                return k, chosen
    raise AssertionError(f"no cover found up to max_k={max_k}")


def main() -> None:
    m = 3
    named = {
        "OR3": truth_mask(m, lambda x: any((x >> i) & 1 for i in range(m))),
        "MAJ3": truth_mask(m, lambda x: x.bit_count() >= 2),
        "PARITY3": truth_mask(m, lambda x: (x.bit_count() & 1) == 1),
    }
    expected = {"OR3": 0, "MAJ3": 2, "PARITY3": 3}

    print("exact Horn-cover family search")
    for name, A in named.items():
        rho, chosen = exact_rho(A, m, max_k=expected[name])
        assert rho == expected[name], (name, rho, chosen)
        U = pointset_all(m) ^ A
        print(
            f"{name}: positives={A.bit_count()} negatives={U.bit_count()} "
            f"candidate_pairs={len(candidate_pairs(U))} rho={rho} chosen={chosen}"
        )

    print("three-bit Horn-cover controls: PASS")
    print("tier=exact_finite_diagnostic; asymptotic circuit lower bound=NOT CLAIMED")


if __name__ == "__main__":
    main()
