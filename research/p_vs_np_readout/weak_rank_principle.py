#!/usr/bin/env python3
"""Exact finite checks for the weak rank principle over F_2.

For X in F_2^{m x n} and Y in F_2^{n x m}, rank(XY) <= n.  Hence when
m>n, XY cannot equal I_m.  We exhaust small instances as finite diagnostics.

The general rank inequality is standard linear algebra; enumeration is not
presented as its proof and this script makes no P-vs-NP claim.
"""

from __future__ import annotations

import itertools
from typing import Iterable, List

Matrix = List[List[int]]


def matrices(rows: int, cols: int) -> Iterable[Matrix]:
    for bits in itertools.product((0, 1), repeat=rows * cols):
        yield [list(bits[i * cols : (i + 1) * cols]) for i in range(rows)]


def matmul_f2(a: Matrix, b: Matrix) -> Matrix:
    bt = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col)) & 1 for col in bt] for row in a]


def rank_f2(a: Matrix) -> int:
    a = [row[:] for row in a]
    if not a:
        return 0
    rows, cols = len(a), len(a[0])
    r = 0
    for c in range(cols):
        pivot = next((i for i in range(r, rows) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        for i in range(rows):
            if i != r and a[i][c]:
                a[i] = [x ^ y for x, y in zip(a[i], a[r])]
        r += 1
        if r == rows:
            break
    return r


def identity(n: int) -> Matrix:
    return [[int(i == j) for j in range(n)] for i in range(n)]


def verify(m: int, n: int) -> dict:
    assert m > n >= 1
    target = identity(m)
    assert rank_f2(target) == m

    pairs = 0
    target_hits = 0
    max_product_rank = 0
    for x in matrices(m, n):
        for y in matrices(n, m):
            product = matmul_f2(x, y)
            pairs += 1
            rank = rank_f2(product)
            max_product_rank = max(max_product_rank, rank)
            assert rank <= n, (m, n, x, y, product, rank)
            if product == target:
                target_hits += 1

    assert target_hits == 0
    assert max_product_rank <= n < m
    return {
        "m": m,
        "n": n,
        "enumerated_pairs": pairs,
        "max_rank_XY": max_product_rank,
        "rank_target_I_m": m,
        "solutions_XY_eq_I_m": target_hits,
        "status": "exact_finite_diagnostic",
    }


def main() -> None:
    print("Weak rank principle exact F_2 finite checks")
    print("claim boundary: finite diagnostics; general rank inequality is standard; not P != NP")
    for dims in ((2, 1), (3, 1), (3, 2)):
        print(verify(*dims))
    print("PASS")


if __name__ == "__main__":
    main()
