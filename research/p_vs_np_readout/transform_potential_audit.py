#!/usr/bin/env python3
"""Finite exhaustive audit of simple gate-local semantic potentials.

Tier: finite_diagnostic.  This does not prove asymptotic circuit lower bounds.
It exhausts every Boolean function on n=3 inputs (256 truth tables) and every
pair of such functions for AND/OR/XOR, checking elementary composition bounds
used in CIRCUIT_BRIDGE_AND_TRANSFORM_POTENTIAL.md.
"""

from itertools import product

N = 3
SIZE = 1 << N
MASK = (1 << SIZE) - 1


def bits(f):
    return [(f >> i) & 1 for i in range(SIZE)]


def anf_coeffs(f):
    a = bits(f)
    # Möbius transform over F_2, indexed by subset bitmask.
    for j in range(N):
        for m in range(SIZE):
            if m & (1 << j):
                a[m] ^= a[m ^ (1 << j)]
    return a


def degree(f):
    a = anf_coeffs(f)
    return max((m.bit_count() for m, c in enumerate(a) if c), default=0)


def support(f):
    return sum(anf_coeffs(f))


def comm_rows(f, k=1):
    # first k variables = row side, remaining variables = column side
    rows = []
    for x in range(1 << k):
        row = []
        for y in range(1 << (N - k)):
            idx = x | (y << k)
            row.append((f >> idx) & 1)
        rows.append(tuple(row))
    return rows


def residual_count(f, k=1):
    return len(set(comm_rows(f, k)))


def real_rank(rows):
    # Exact rational-free Gaussian elimination is enough for 0/1 matrices here.
    from fractions import Fraction
    A = [[Fraction(v) for v in r] for r in rows]
    if not A:
        return 0
    m, n = len(A), len(A[0])
    r = 0
    c = 0
    while r < m and c < n:
        piv = next((i for i in range(r, m) if A[i][c] != 0), None)
        if piv is None:
            c += 1
            continue
        A[r], A[piv] = A[piv], A[r]
        p = A[r][c]
        A[r] = [z / p for z in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                q = A[i][c]
                A[i] = [u - q * v for u, v in zip(A[i], A[r])]
        r += 1
        c += 1
    return r


def rr(f):
    return real_rank(comm_rows(f))


def check():
    funcs = list(range(1 << SIZE))
    max_deg = max(map(degree, funcs))
    max_supp = max(map(support, funcs))
    max_res = max(map(residual_count, funcs))
    max_rank = max(map(rr, funcs))

    assert max_deg <= N
    assert max_supp <= (1 << N)
    assert max_res <= (1 << 1)
    assert max_rank <= (1 << 1)

    checked = 0
    for f in funcs:
        nf = (~f) & MASK
        assert residual_count(nf) <= residual_count(f) + 1
        assert rr(nf) <= rr(f) + 1
        assert degree(nf) <= max(1, degree(f))
        for g in funcs:
            checked += 1
            h_and = f & g
            h_or = f | g
            h_xor = f ^ g

            # Future-readout rows of a binary composition are determined by
            # the pair of predecessor rows.
            assert residual_count(h_and) <= residual_count(f) * residual_count(g)
            assert residual_count(h_or) <= residual_count(f) * residual_count(g)
            assert residual_count(h_xor) <= residual_count(f) * residual_count(g)

            # For AND, the communication matrix is the Hadamard product;
            # rank(A o B) <= rank(A) rank(B).  Zero-rank edge cases included.
            assert rr(h_and) <= rr(f) * rr(g)

            # ANF composition ceilings.
            assert degree(h_xor) <= max(degree(f), degree(g))
            assert degree(h_and) <= min(N, degree(f) + degree(g))
            assert support(h_xor) <= support(f) + support(g)
            assert support(h_and) <= support(f) * support(g)

    print("finite_diagnostic: ACCEPT")
    print(f"n={N}, functions={len(funcs)}, binary_gate_pairs={checked}")
    print(f"max algebraic degree={max_deg} <= n={N}")
    print(f"max ANF support={max_supp} <= 2^n={1<<N}")
    print(f"max residual count at 1|2 cut={max_res} <= 2")
    print(f"max real communication rank at 1|2 cut={max_rank} <= 2")
    print("All declared AND/OR/XOR/NOT local inequalities passed exhaustively.")
    print("Interpretation: these simple logarithmic/additive potentials have only O(n) semantic headroom for unrestricted n-input functions.")


if __name__ == "__main__":
    check()
