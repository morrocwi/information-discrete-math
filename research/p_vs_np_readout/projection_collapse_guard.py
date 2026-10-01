#!/usr/bin/env python3
"""Exact finite no-go diagnostic for witness-diversity hardness.

For R_m(x,w) = [x == w] over m-bit strings, the witness slices
x -> R_m(x,w) are all distinct (2^m of them), while existential projection
exists_w R_m(x,w) is the constant-1 function.

This demonstrates that pre-projection witness diversity is not, by itself,
a lower-bound invariant for SAT-style existential projection.
"""
from itertools import product


def bits(m):
    return tuple(product((0, 1), repeat=m))


def slice_signature(xs, w):
    return tuple(int(x == w) for x in xs)


def projection_signature(xs, ws):
    return tuple(int(any(x == w for w in ws)) for x in xs)


def check(m):
    xs = bits(m)
    ws = xs
    slices = {slice_signature(xs, w) for w in ws}
    projection = projection_signature(xs, ws)
    assert len(slices) == 2 ** m
    assert projection == (1,) * (2 ** m)
    return {
        "m": m,
        "source_points": 2 ** m,
        "distinct_witness_slices": len(slices),
        "projection_support": sum(projection),
        "projection_constant_true": True,
    }


def main():
    rows = [check(m) for m in range(1, 9)]
    for r in rows:
        print(
            f"m={r['m']}: slices={r['distinct_witness_slices']} "
            f"projection=constant-1 over {r['source_points']} inputs"
        )
    print("projection-collapse guard: PASS")


if __name__ == "__main__":
    main()
