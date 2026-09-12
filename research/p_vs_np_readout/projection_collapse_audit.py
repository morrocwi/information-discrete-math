#!/usr/bin/env python3
"""Exact existential-projection collapse control.

For m-bit x,w define R_m(x,w) = [x = w].  Fixing w yields 2^m distinct
functions of x (one singleton indicator per witness), yet existentially
projecting w gives the constant-1 function:

    exists w R_m(x,w) == 1.

Thus exponential witness-slice diversity is not a lower bound on the circuit
complexity of the existential projection.  The test is exact finite arithmetic
and intentionally functions as a NO-GO guard for Readout/NP measures that count
witness distinctions without quotienting by downstream projection role.
"""
from __future__ import annotations


def equality_slice(m: int, witness: int) -> int:
    # Truth table over x: exactly one accepting x, namely x=witness.
    return 1 << witness


def existential_projection_mask(m: int) -> int:
    out = 0
    for w in range(1 << m):
        out |= equality_slice(m, w)
    return out


def run(max_m: int = 10) -> list[dict]:
    rows = []
    for m in range(1, max_m + 1):
        slices = {equality_slice(m, w) for w in range(1 << m)}
        projection = existential_projection_mask(m)
        constant_one = (1 << (1 << m)) - 1
        assert len(slices) == 1 << m
        assert projection == constant_one
        rows.append(
            {
                "m": m,
                "distinct_witness_slices": len(slices),
                "projection_is_constant_one": True,
            }
        )
    return rows


def main() -> None:
    rows = run()
    print("existential projection collapse: exact finite diagnostic")
    for row in rows:
        print(row)
    print(
        "NO-GO: witness-slice diversity alone cannot lower-bound "
        "existential-projection circuit size"
    )
    print("tier=finite_diagnostic; P!=NP=NOT CLAIMED")


if __name__ == "__main__":
    main()
