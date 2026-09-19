#!/usr/bin/env python3
"""Exact guard against raw gate-signature compression claims.

A size-s Boolean circuit may realize all 2^s internal gate-value signatures.
Take independent copy gates g_i = x_i AND x_i.  Their joint value vector is
exactly the input bit vector.  Hence quotienting restriction states only by the
full internal gate-value signature gives at best an exponential 2^s generic
bound, not a polynomial-in-s negative-closure compression theorem.

Finite exact no-go diagnostic; no P != NP claim.
"""
from __future__ import annotations


def copy_gate_signature(x: int, s: int) -> tuple[int, ...]:
    # Semantics of g_i = x_i AND x_i.
    return tuple((((x >> i) & 1) & ((x >> i) & 1)) for i in range(s))


def main() -> None:
    rows = []
    for s in range(1, 13):
        sigs = {copy_gate_signature(x, s) for x in range(1 << s)}
        assert len(sigs) == 1 << s
        rows.append((s, len(sigs)))

    print("lineage gate-signature guard: exact finite diagnostic")
    for s, count in rows:
        print(f"s={s:2d} distinct_internal_signatures={count}")
    print("verified: s independent copy gates realize all 2^s value signatures")
    print("NO-GO: raw full-gate-value signature quotient does not imply poly(s) closure compression")
    print("next target: SAT-restriction transition structure among signatures, not signature cardinality")


if __name__ == "__main__":
    main()
