#!/usr/bin/env python3
"""Exact tiny diagnostic: Fusion/Horn survivor -> concrete target mismatch.

For a target A and a DeMorgan candidate circuit C on two bits, build the actual
AND-gate lineage pairs relative to U=A^c.  If the least Horn closure above a
target-positive point a avoids bottom, then the fusion survivor has two cases:

  * C(a)=0: a itself is a false negative;
  * C(a)=1: the candidate output slice C^{-1}(1) cap U is retained and nonempty,
    so any u in that slice is a false positive.

The second case is the executable finite counterpart of
formal/IDM_FusionSurvivorRefuter.v.

This extracts a counterexample only when a preserving survivor is already
available.  It does not construct survivors asymptotically and proves no
unrestricted circuit lower bound.
"""
from __future__ import annotations

from circuit_lineage_fusion_diagnostic import (
    N,
    GAMMA,
    lineage_pairs,
    make_and,
    make_or,
    make_xor,
)
from fusion_horn_exact import horn_closure, literal_generators, tt


def bit(mask: int, x: int) -> bool:
    return bool((mask >> x) & 1)


def first_point(mask: int) -> int:
    assert mask
    return (mask & -mask).bit_length() - 1


def survivor_refute(C, out: int, target_A: int):
    vals = C.semantics()
    output = vals[out]
    U = GAMMA ^ target_A
    generators = literal_generators(N)
    pairs = lineage_pairs(C, out, target_A)

    for a in range(1 << N):
        if not bit(target_A, a):
            continue
        closure = horn_closure(a, U, generators, pairs)
        if 0 in closure:
            continue

        if not bit(output, a):
            return {
                "kind": "false_negative",
                "positive_seed": a,
                "counterexample": a,
                "pairs": len(pairs),
                "closure_size": len(closure),
            }

        out_slice = output & U
        # Circuit induction through literal seeds, upward closure, OR and the
        # preserved AND lineage predicts this slice is retained.
        assert out_slice in closure, (a, output, U, out_slice, closure, pairs)
        assert out_slice != 0, "survivor excludes bottom, so output false-region slice must be nonempty"
        u = first_point(out_slice)
        assert not bit(target_A, u)
        assert bit(output, u)
        return {
            "kind": "false_positive",
            "positive_seed": a,
            "counterexample": u,
            "pairs": len(pairs),
            "closure_size": len(closure),
        }

    return None


def main() -> None:
    xor_A = tt(lambda x: ((x & 1) ^ ((x >> 1) & 1)))

    # OR as XOR: positive XOR points are accepted, but survivor propagation
    # retains the candidate's false-region output slice and extracts 11 as a
    # false positive.
    C_or, out_or = make_or()
    r_or = survivor_refute(C_or, out_or, xor_A)
    assert r_or is not None and r_or["kind"] == "false_positive", r_or
    u = r_or["counterexample"]
    assert bit(C_or.semantics()[out_or], u) and not bit(xor_A, u)

    # AND as XOR: a survivor exists above a positive XOR point that the
    # candidate rejects, yielding a direct false negative.
    C_and, out_and = make_and()
    r_and = survivor_refute(C_and, out_and, xor_A)
    assert r_and is not None and r_and["kind"] == "false_negative", r_and
    a = r_and["counterexample"]
    assert not bit(C_and.semantics()[out_and], a) and bit(xor_A, a)

    # Exact XOR construction: its lineage covers the target semi-filters, so
    # there is no preserving survivor from which to extract a mismatch.
    C_xor, out_xor = make_xor()
    assert C_xor.semantics()[out_xor] == xor_A
    r_xor = survivor_refute(C_xor, out_xor, xor_A)
    assert r_xor is None, r_xor

    print(f"OR-as-XOR survivor refuter: {r_or}")
    print(f"AND-as-XOR survivor refuter: {r_and}")
    print("exact-XOR control: no survivor / no false refutation")
    print("fusion survivor -> concrete mismatch diagnostic: PASS")
    print("survivor construction for unrestricted SAT remains OPEN")
    print("tier=finite_diagnostic; P!=NP=NOT CLAIMED")


if __name__ == "__main__":
    main()
