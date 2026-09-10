#!/usr/bin/env python3
"""Exact finite falsification audit for static semantic-capacity candidates.

This diagnostic enumerates *all* Boolean functions on three inputs and every
ordered pair of such functions under four pointwise binary operations.  It is
not a circuit lower bound.  Its job is to reject naive static measures before
we mistake them for a universal per-gate capacity theorem.

The audit reports the largest one-gate jump over max(parent measures) for:

  residual-function count under every partial restriction,
  log2 residual count,
  GF(2) algebraic degree,
  GF(2) ANF support,
  truth-table support,
  sensitivity-edge count.

It also exhaustively verifies at n=3 the analytic rule

    R(b(f,g)) <= R(f) R(g)

for each declared pointwise binary operation b.  The general proof is direct:
a restriction of b(f,g) is determined by the corresponding pair of restricted
functions.  The finite run is a regression fixture, not the proof.
"""
from __future__ import annotations

from itertools import product
from math import log2

OPS = ("and", "or", "xor", "nand")


def bit(tt: int, idx: int) -> int:
    return (tt >> idx) & 1


def apply_binary(a: int, b: int, n: int, op: str) -> int:
    out = 0
    for idx in range(1 << n):
        x, y = bit(a, idx), bit(b, idx)
        if op == "and":
            z = x & y
        elif op == "or":
            z = x | y
        elif op == "xor":
            z = x ^ y
        elif op == "nand":
            z = 1 - (x & y)
        else:
            raise ValueError(op)
        if z:
            out |= 1 << idx
    return out


def restrict_tt(tt: int, n: int, partial: tuple[int | None, ...]) -> tuple[int, int]:
    """Canonical residual table on the remaining variables, preserving order."""
    free = [i for i, v in enumerate(partial) if v is None]
    out = 0
    for j, free_bits in enumerate(product((0, 1), repeat=len(free))):
        assignment = list(partial)
        for i, value in zip(free, free_bits):
            assignment[i] = value
        idx = sum(int(assignment[i]) << i for i in range(n))
        if bit(tt, idx):
            out |= 1 << j
    return len(free), out


def residual_set(tt: int, n: int) -> set[tuple[int, int]]:
    return {
        restrict_tt(tt, n, tuple(None if v == 2 else v for v in p))
        for p in product((0, 1, 2), repeat=n)
    }


def anf_coefficients(tt: int, n: int) -> list[int]:
    coeff = [bit(tt, i) for i in range(1 << n)]
    for i in range(n):
        for mask in range(1 << n):
            if mask & (1 << i):
                coeff[mask] ^= coeff[mask ^ (1 << i)]
    return coeff


def semantic_measures(tt: int, n: int) -> dict[str, float | int]:
    residual_count = len(residual_set(tt, n))
    anf = anf_coefficients(tt, n)
    degree = max((mask.bit_count() for mask, c in enumerate(anf) if c), default=0)
    sensitivity_edges = 0
    for x in range(1 << n):
        for i in range(n):
            y = x ^ (1 << i)
            if x < y and bit(tt, x) != bit(tt, y):
                sensitivity_edges += 1
    return {
        "residual_count": residual_count,
        "log2_residual": log2(residual_count),
        "degree": degree,
        "anf_support": sum(anf),
        "support": tt.bit_count(),
        "sensitivity_edges": sensitivity_edges,
    }


def run_exact_audit(n: int = 3) -> dict:
    if n != 3:
        raise ValueError("the exhaustive CI fixture is intentionally frozen at n=3")

    functions = list(range(1 << (1 << n)))
    measures = {f: semantic_measures(f, n) for f in functions}
    names = tuple(next(iter(measures.values())).keys())
    max_jump: dict[str, tuple[float, tuple[str, int, int, int] | None]] = {
        name: (-1.0, None) for name in names
    }
    residual_product_rule = True

    for f in functions:
        for g in functions:
            for op in OPS:
                h = apply_binary(f, g, n, op)
                mf, mg, mh = measures[f], measures[g], measures[h]

                if mh["residual_count"] > mf["residual_count"] * mg["residual_count"]:
                    residual_product_rule = False

                for name in names:
                    jump = float(mh[name]) - max(float(mf[name]), float(mg[name]))
                    if jump > max_jump[name][0]:
                        max_jump[name] = (jump, (op, f, g, h))

    assert residual_product_rule

    max_residual = max(int(m["residual_count"]) for m in measures.values())
    # Generic source-count ceilings specialized to n=3.
    assert max_residual <= 3**n
    assert log2(max_residual) <= n * log2(3)

    return {
        "n": n,
        "functions_enumerated": len(functions),
        "ordered_function_pairs": len(functions) ** 2,
        "binary_operations": OPS,
        "gate_evaluations": len(functions) ** 2 * len(OPS),
        "max_residual_count": max_residual,
        "residual_product_rule_exhaustive": residual_product_rule,
        "static_measure_max_one_gate_jumps": {
            name: {"jump": jump, "witness": witness}
            for name, (jump, witness) in max_jump.items()
        },
        "tier": "finite_diagnostic",
        "scope": (
            "all 3-input Boolean functions; falsification audit only; "
            "no unrestricted circuit lower bound"
        ),
    }


if __name__ == "__main__":
    print(run_exact_audit())
