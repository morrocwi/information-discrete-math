#!/usr/bin/env python3
"""Exact finite negative control for Genesis-native closure-debt metrics.

Equality has 2^m distinct future residual functions after the x-block is fixed,
yet a shared DeMorgan DAG computes equality with O(m) gates. Therefore a raw
count of future contexts/obligations cannot be charged one-for-one to gates.
The correct RRR ledger must account for compact retained/recompute seeds and
multi-obligation resolution by shared gates.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Gate:
    op: str
    a: int | None = None
    b: int | None = None
    inp: int | None = None


class Circuit:
    def __init__(self):
        self.gates = []

    def inp(self, i):
        k = len(self.gates)
        self.gates.append(Gate("IN", inp=i))
        return k

    def NOT(self, a):
        k = len(self.gates)
        self.gates.append(Gate("NOT", a))
        return k

    def AND(self, a, b):
        k = len(self.gates)
        self.gates.append(Gate("AND", a, b))
        return k

    def OR(self, a, b):
        k = len(self.gates)
        self.gates.append(Gate("OR", a, b))
        return k

    def eval(self, bits):
        vals = []
        for g in self.gates:
            if g.op == "IN":
                vals.append(bool(bits[g.inp]))
            elif g.op == "NOT":
                vals.append(not vals[g.a])
            elif g.op == "AND":
                vals.append(vals[g.a] and vals[g.b])
            elif g.op == "OR":
                vals.append(vals[g.a] or vals[g.b])
            else:
                raise ValueError(g.op)
        return vals


def eq_circuit(m):
    C = Circuit()
    xs = [C.inp(i) for i in range(m)]
    ys = [C.inp(m + i) for i in range(m)]
    eqbits = []
    for x, y in zip(xs, ys):
        xy = C.AND(x, y)
        nx = C.NOT(x)
        ny = C.NOT(y)
        nxy = C.AND(nx, ny)
        eqbits.append(C.OR(xy, nxy))
    out = eqbits[0]
    for e in eqbits[1:]:
        out = C.AND(out, e)
    return C, out


def word(v, m):
    return tuple((v >> i) & 1 for i in range(m))


def residual_signature(x, m):
    return tuple(x == word(y, m) for y in range(1 << m))


def verify(m):
    C, out = eq_circuit(m)
    # Inputs are source leaves; count non-input gates as circuit work.
    work = sum(g.op != "IN" for g in C.gates)
    expected = 6 * m - 1  # explicit NOT basis: 5 per bit + m-1 final ANDs
    assert work == expected, (m, work, expected)

    for z in range(1 << (2 * m)):
        bits = word(z, 2 * m)
        got = C.eval(bits)[out]
        want = bits[:m] == bits[m:]
        assert got == want, (m, bits, got, want)

    sigs = {residual_signature(word(x, m), m) for x in range(1 << m)}
    assert len(sigs) == 1 << m

    # RRR negative control: keep/re-read only the m-bit x seed; every future y
    # readout is decoded exactly despite 2^m distinct residual functions.
    for x in range(1 << m):
        seed = word(x, m)
        for y in range(1 << m):
            assert (seed == word(y, m)) == residual_signature(seed, m)[y]
    return work, len(sigs), m


def main():
    print("Genesis RRR / unrestricted-circuit negative control")
    for m in range(1, 9):
        work, residuals, seed_bits = verify(m)
        print(
            f"m={m:2d}: noninput_gates={work:2d}, "
            f"residuals={residuals:4d}, recompute_seed_bits={seed_bits}"
        )
    print(
        "RESULT: raw future-context count is NOT a gate lower bound; "
        "compact sharing/seed defeats it."
    )
    print("finite_diagnostic: ACCEPT")


if __name__ == "__main__":
    main()
