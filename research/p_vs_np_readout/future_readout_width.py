#!/usr/bin/env python3
"""Exact truth-table residual-width counter for future-readout equivalence.

Baseline function: EQ_m(x,y) = [x == y].

For the block order x_1..x_m,y_1..y_m the middle residual signatures are all
2^m distinct.  For the interleaved order x_1,y_1,...,x_m,y_m the maximum
number of distinct residual signatures is 3 for m>=2.

This is an exact finite restricted-model diagnostic, not a P-vs-NP claim.
"""

from __future__ import annotations

import argparse
import itertools
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

Bits = Tuple[int, ...]


def eq_function(bits: Bits) -> bool:
    assert len(bits) % 2 == 0
    m = len(bits) // 2
    return bits[:m] == bits[m:]


def residual_signature(
    f: Callable[[Bits], bool], n: int, order: Sequence[int], prefix: Bits
) -> Tuple[bool, ...]:
    """Truth table of the residual function after a prefix in the given order."""
    k = len(prefix)
    assigned: Dict[int, int] = dict(zip(order[:k], prefix))
    suffix_vars = order[k:]
    table = []
    for suffix in itertools.product((0, 1), repeat=len(suffix_vars)):
        a = dict(assigned)
        a.update(dict(zip(suffix_vars, suffix)))
        table.append(f(tuple(a[i] for i in range(n))))
    return tuple(table)


def residual_widths(f: Callable[[Bits], bool], n: int, order: Sequence[int]) -> List[int]:
    assert sorted(order) == list(range(n))
    widths = []
    for k in range(n + 1):
        signatures = {
            residual_signature(f, n, order, prefix)
            for prefix in itertools.product((0, 1), repeat=k)
        }
        widths.append(len(signatures))
    return widths


def verify_equality(m: int) -> dict:
    n = 2 * m
    block = list(range(n))
    interleaved = [j for i in range(m) for j in (i, m + i)]

    wb = residual_widths(eq_function, n, block)
    wi = residual_widths(eq_function, n, interleaved)

    assert wb[m] == 2**m, (m, wb)
    assert max(wb) == 2**m, (m, wb)
    if m >= 2:
        assert max(wi) == 3, (m, wi)
    else:
        assert max(wi) == 2, (m, wi)

    return {
        "m": m,
        "block_widths": wb,
        "block_max": max(wb),
        "interleaved_widths": wi,
        "interleaved_max": max(wi),
        "status": "exact_finite_diagnostic",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--max-m", type=int, default=6)
    args = p.parse_args()
    if args.max_m < 1:
        raise SystemExit("--max-m must be >= 1")

    print("Future-readout residual width: EQ_m")
    print("claim boundary: ordered read-once / OBDD-style width only; not P != NP")
    for m in range(1, args.max_m + 1):
        print(verify_equality(m))
    print("PASS")


if __name__ == "__main__":
    main()
