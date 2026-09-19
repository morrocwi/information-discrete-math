#!/usr/bin/env python3
"""Exact finite black-pebbling diagnostics for the readout recomputation lane.

The state graph is finite.  BFS computes the minimum move count under a fixed
maximum number of simultaneously retained pebbles.  This is a finite diagnostic
for the declared DAG-evaluator model, not a SAT lower bound and not P != NP.
"""

from __future__ import annotations

from collections import deque
from typing import Dict, FrozenSet, Iterable, List, Set, Tuple

Preds = Dict[int, FrozenSet[int]]


def pyramid(height: int) -> Tuple[Preds, int]:
    """Triangular pyramid: bottom has h+1 sources, each upper node depends on two below."""
    if height < 1:
        raise ValueError("height must be >= 1")
    levels: List[List[int]] = []
    next_id = 0
    for level in range(height + 1):
        width = height + 1 - level
        nodes = list(range(next_id, next_id + width))
        next_id += width
        levels.append(nodes)

    preds: Preds = {v: frozenset() for level in levels for v in level}
    for level in range(1, len(levels)):
        lower = levels[level - 1]
        upper = levels[level]
        for j, v in enumerate(upper):
            preds[v] = frozenset((lower[j], lower[j + 1]))
    return preds, levels[-1][0]


def shortest_pebbling(preds: Preds, sink: int, space: int) -> int | None:
    """Minimum legal add/remove moves reaching any state containing sink."""
    if space < 0:
        return None
    nodes = tuple(sorted(preds))
    start: FrozenSet[int] = frozenset()
    q = deque([(start, 0)])
    seen = {start}

    while q:
        state, moves = q.popleft()
        if sink in state:
            return moves

        # Forget/remove one retained node.
        for v in state:
            nxt = frozenset(set(state) - {v})
            if nxt not in seen:
                seen.add(nxt)
                q.append((nxt, moves + 1))

        # Retain/place one node if the predecessor boundary is live.
        if len(state) < space:
            for v in nodes:
                if v in state:
                    continue
                if preds[v].issubset(state):
                    nxt = frozenset(set(state) | {v})
                    if nxt not in seen:
                        seen.add(nxt)
                        q.append((nxt, moves + 1))

    return None


def exact_frontier(height: int) -> dict:
    preds, sink = pyramid(height)
    n = len(preds)
    feasible = []
    for space in range(1, n + 1):
        moves = shortest_pebbling(preds, sink, space)
        if moves is not None:
            feasible.append((space, moves))
    assert feasible
    return {
        "height": height,
        "nodes": n,
        "first_feasible_space": feasible[0][0],
        "space_move_frontier": feasible,
        "status": "exact_finite_diagnostic",
    }


def main() -> None:
    print("Readout-pebbling exact finite frontier")
    print("claim boundary: declared DAG evaluator only; not an unrestricted SAT lower bound")
    expected_first = {1: 3, 2: 4, 3: 5, 4: 6}
    for height in range(1, 5):
        result = exact_frontier(height)
        assert result["first_feasible_space"] == expected_first[height], result
        print(result)
    print("PASS")


if __name__ == "__main__":
    main()
