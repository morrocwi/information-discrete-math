#!/usr/bin/env python3
"""Exact tiny online adversary for semantic-generation capacity.

This diagnostic reuses the two-bit fusion/semi-filter universe and feeds it the
*ordered AND-gate lineage* of an actual tiny circuit.  The adversary state is the
set of target semi-filters not yet killed by the prefix.

The purpose is to test, and if necessary falsify, the most naive discrete
analogue of an NS-style contraction coefficient:

    survivor burden after one gate >= eta * burden before one gate

for a universal eta>0.

A correct circuit may have a single AND gate that kills every currently
surviving semi-filter.  Hence raw survivor cardinality cannot satisfy a useful
universal positive-survival factor.  This is a finite diagnostic/no-go control,
not a circuit lower bound.
"""

from circuit_lineage_fusion_diagnostic import (
    make_and,
    make_eq,
    make_or,
    make_xor,
    lineage_pairs,
    target_filters,
    tt,
)


def pair_kills_filter(pair, filt):
    E, H = pair
    return E in filt and H in filt and (E & H) not in filt


def online_survivors(target_A, pairs):
    _, filters = target_filters(target_A)
    survivors = list(filters)
    trace = []
    for step, pair in enumerate(pairs, 1):
        before = len(survivors)
        kept = [F for F in survivors if not pair_kills_filter(pair, F)]
        killed = before - len(kept)
        frac = 0.0 if before == 0 else killed / before
        trace.append(
            {
                "step": step,
                "pair": pair,
                "before": before,
                "killed": killed,
                "after": len(kept),
                "kill_fraction": frac,
            }
        )
        survivors = kept
    return survivors, trace


def run_correct(name, maker):
    C, out = maker()
    target = C.semantics()[out]
    pairs = lineage_pairs(C, out, target)
    survivors, trace = online_survivors(target, pairs)
    assert not survivors, (name, trace, len(survivors))
    return {"name": name, "and_pairs": len(pairs), "trace": trace}


def main():
    rows = [
        run_correct("AND", make_and),
        run_correct("OR", make_or),
        run_correct("XOR", make_xor),
        run_correct("EQ", make_eq),
    ]

    # A correct OR circuit has no AND/fusion pairs, and OR has zero fusion
    # complexity, so its target semi-filter universe is already empty.
    or_row = next(r for r in rows if r["name"] == "OR")
    assert or_row["and_pairs"] == 0

    # Crucial no-go control: at least one correct target has a gate which kills
    # every survivor present at that step.  Therefore there is no universal
    # eta>0 with |A_{t+1}| >= eta |A_t| for raw survivor count.
    all_fractions = [
        step["kill_fraction"]
        for row in rows
        for step in row["trace"]
        if step["before"] > 0
    ]
    assert all_fractions
    assert max(all_fractions) == 1.0

    # Negative control: OR syntax cannot compute XOR. With zero AND pairs the
    # XOR semi-filter adversary has a genuine survivor.
    C_or, out_or = make_or()
    xor_target = tt(lambda x: ((x & 1) ^ ((x >> 1) & 1)))
    assert C_or.semantics()[out_or] != xor_target
    bad_pairs = lineage_pairs(C_or, out_or, xor_target)
    bad_survivors, bad_trace = online_survivors(xor_target, bad_pairs)
    assert not bad_pairs
    assert bad_survivors

    print("adaptive semantic-generation adversary: finite exact diagnostic")
    for row in rows:
        print(f"{row['name']:4s}: AND_pairs={row['and_pairs']} trace={row['trace']}")
    print(f"max one-gate survivor kill fraction = {max(all_fractions):.1f}")
    print(
        "NO-GO: raw surviving-semi-filter cardinality has no universal "
        "positive per-gate survival factor"
    )
    print(
        f"OR-as-XOR negative control: surviving_semifilters={len(bad_survivors)} "
        "-> candidate circuit rejected"
    )
    print("tier=finite_diagnostic; unrestricted circuit lower bound=NOT CLAIMED")


if __name__ == "__main__":
    main()
