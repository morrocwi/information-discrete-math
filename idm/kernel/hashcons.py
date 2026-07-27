"""Structural hashing + request-scoped interning for the kernel expression tree (P1.1 §c).

``struct_hash`` is a pure bottom-up combiner: given a node's type tag, the already-computed structural
hashes of its children, and any leaf payload, it returns an int in O(1). ``canonical_order_key`` gives
an O(1) comparator key for sorting the operands of ``Add``/``Mul`` — replacing the O(size)
``tostr()``-based comparator in the legacy ``idm.symbolic``. ``InternTable`` is **request-scoped**:
constructed per top-level kernel call and discarded after, so a long-running server never accumulates
unbounded memory, and it is never shared across two unrelated calls.
"""

from __future__ import annotations

from typing import Dict, List

# Stable per-process ranking of node kinds, so canonical ordering is deterministic within a run.
_TYPE_RANK = {
    "Const": 0, "Symbol": 1, "Undefined": 2, "Infinity": 3, "ComplexInfinity": 4,
    "Pow": 5, "Mul": 6, "Add": 7, "Func": 8, "Relation": 9, "Piecewise": 10,
    "Derivative": 11, "Integral": 12, "Limit": 13,
}


def type_rank(type_tag: str) -> int:
    return _TYPE_RANK.get(type_tag, 99)


def struct_hash(type_tag: str, children_hashes: tuple, leaf_payload=None) -> int:
    """Pure structural hash. Deterministic within a process; O(1) given children's hashes."""

    return hash((type_tag, children_hashes, leaf_payload))


def canonical_order_key(node) -> tuple:
    """O(1) comparator key ``(type_rank, structural_hash)`` for operand sorting."""

    return (type_rank(type(node).__name__), node._hash)


class InternTable:
    """Request-scoped interning: structurally-equal subtrees collapse to one object.

    After interning, equality reduces to ``is``. Not a module-level singleton — build one per
    top-level kernel call and let it be garbage-collected afterwards.
    """

    __slots__ = ("_by_hash",)

    def __init__(self) -> None:
        self._by_hash: Dict[int, List[object]] = {}

    def intern(self, node):
        """Return ``node``, or an already-seen structurally-equal node (so callers can use ``is``)."""

        bucket = self._by_hash.setdefault(node._hash, [])
        for existing in bucket:
            if existing == node:
                return existing
        bucket.append(node)
        return node


__all__ = ["struct_hash", "canonical_order_key", "type_rank", "InternTable"]
