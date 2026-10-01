#!/usr/bin/env python3
"""Exact bounded diagnostic: DeMorgan circuit lineage -> fusion pair cover.

This script checks the static fusion bridge on tiny two-input circuits without
pretending to prove an asymptotic lower bound.  A gate is represented by its
finite truth-table semantics only because n=2 in this diagnostic.

For a circuit C that exactly computes target A, the relative semantic sets of
its AND gates induce a fusion-pair family Gamma_C.  The fusion theorem predicts
that Gamma_C covers every target semi-filter.  We verify this directly.

For an intentionally underpowered candidate (OR trying to compute XOR), the
empty AND-pair family cannot cover the XOR semi-filters, giving a survivor.
"""

from dataclasses import dataclass

from fusion_horn_exact import (
    pointset_all,
    literal_generators,
    enumerate_semifilters,
    above_some_positive,
    pair_cover_mask,
    tt,
)

N = 2
GAMMA = pointset_all(N)


@dataclass(frozen=True)
class Gate:
    op: str
    left: int | None = None
    right: int | None = None
    literal_mask: int | None = None


class Circuit:
    def __init__(self):
        self.gates = []

    def lit(self, mask):
        i = len(self.gates)
        self.gates.append(Gate("LIT", literal_mask=mask))
        return i

    def AND(self, a, b):
        i = len(self.gates)
        self.gates.append(Gate("AND", a, b))
        return i

    def OR(self, a, b):
        i = len(self.gates)
        self.gates.append(Gate("OR", a, b))
        return i

    def semantics(self):
        vals = []
        for g in self.gates:
            if g.op == "LIT":
                vals.append(g.literal_mask)
            elif g.op == "AND":
                vals.append(vals[g.left] & vals[g.right])
            elif g.op == "OR":
                vals.append(vals[g.left] | vals[g.right])
            else:
                raise ValueError(g.op)
        return vals

    def reachable(self, output):
        seen = set()
        stack = [output]
        while stack:
            g = stack.pop()
            if g in seen:
                continue
            seen.add(g)
            node = self.gates[g]
            if node.op != "LIT":
                stack.extend([node.left, node.right])
        return seen


def variable_masks():
    gens = literal_generators(N)
    # literal_generators emits x0, ~x0, x1, ~x1
    return gens[0], gens[1], gens[2], gens[3]


def target_filters(A):
    U = GAMMA ^ A
    gens = literal_generators(N)
    return U, [
        F for F in enumerate_semifilters(U)
        if above_some_positive(F, A, U, gens, N)
    ]


def lineage_pairs(C, output, target_A):
    vals = C.semantics()
    U = GAMMA ^ target_A
    live = C.reachable(output)
    pairs = []
    for i in sorted(live):
        g = C.gates[i]
        if g.op == "AND":
            pairs.append((vals[g.left] & U, vals[g.right] & U))
    return pairs


def uncovered_filters(A, pairs):
    U, filters = target_filters(A)
    if not filters:
        return []
    covered = 0
    for p in pairs:
        covered |= pair_cover_mask(p, filters)
    return [filters[j] for j in range(len(filters)) if not (covered >> j) & 1]


def make_and():
    x, nx, y, ny = variable_masks()
    C = Circuit(); gx = C.lit(x); gy = C.lit(y)
    return C, C.AND(gx, gy)


def make_or():
    x, nx, y, ny = variable_masks()
    C = Circuit(); gx = C.lit(x); gy = C.lit(y)
    return C, C.OR(gx, gy)


def make_xor():
    x, nx, y, ny = variable_masks()
    C = Circuit()
    gx = C.lit(x); gnx = C.lit(nx); gy = C.lit(y); gny = C.lit(ny)
    # (x OR y) AND (~x OR ~y): exactly one intersection gate.
    a = C.OR(gx, gy)
    b = C.OR(gnx, gny)
    return C, C.AND(a, b)


def make_eq():
    x, nx, y, ny = variable_masks()
    C = Circuit()
    gx = C.lit(x); gnx = C.lit(nx); gy = C.lit(y); gny = C.lit(ny)
    # (x OR ~y) AND (~x OR y)
    a = C.OR(gx, gny)
    b = C.OR(gnx, gy)
    return C, C.AND(a, b)


def run_exact(name, maker):
    C, out = maker()
    A = C.semantics()[out]
    pairs = lineage_pairs(C, out, A)
    survivors = uncovered_filters(A, pairs)
    assert not survivors, (name, pairs, survivors)
    return len(C.reachable(out)), len(pairs), A


def main():
    print("circuit-lineage -> fusion exact diagnostic")
    for name, maker in [("AND", make_and), ("OR", make_or), ("XOR", make_xor), ("EQ", make_eq)]:
        gates, ands, A = run_exact(name, maker)
        print(f"{name:4s}: reachable_gates={gates}, AND_pairs={ands}, truth=0x{A:x}, cover=ACCEPT")

    # Negative control: OR's zero-intersection construction cannot generate XOR.
    C_or, out_or = make_or()
    xor_A = tt(lambda x: ((x & 1) ^ ((x >> 1) & 1)))
    assert C_or.semantics()[out_or] != xor_A
    pairs = lineage_pairs(C_or, out_or, xor_A)
    survivors = uncovered_filters(xor_A, pairs)
    assert len(pairs) == 0
    assert survivors, "expected an uncovered XOR semi-filter under zero AND pairs"
    print(f"OR-as-XOR negative control: AND_pairs=0, surviving_semifilters={len(survivors)} -> REJECT candidate")
    print("finite_diagnostic: ACCEPT")


if __name__ == "__main__":
    main()
