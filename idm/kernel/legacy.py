"""Migration-only bridge: :mod:`idm.symbolic`'s tuple/Fraction tree <-> :mod:`idm.kernel.nodes` Expr.

Used ONLY where a ``kernel/`` function needs the new tree. The 6 ``symbolic_*`` kinds do NOT round-trip
through this in Phase 1 — they keep speaking the legacy tree end to end.

Note on canonical order: ``Add``/``Mul`` canonically sort their operands, so the *kernel-level*
round-trip ``from_legacy(to_legacy(e)) == e`` is an identity, while the *legacy-level*
``to_legacy(from_legacy(t))`` returns ``t`` up to that canonical reordering of sum/product operands.

Legacy node shapes (from ``idm.symbolic``):
    Fraction / int             — a rational constant
    ('var', name)              — a symbol
    ('add', [t, ...])          — n-ary sum
    ('mul', [f, ...])          — n-ary product
    ('pow', base, exp)         — power
    ('func', name, arg)        — unary function
"""

from __future__ import annotations

from fractions import Fraction as Q

from . import nodes as N
from .numbers import to_fraction


def from_legacy(tree) -> N.Expr:
    """Legacy tuple/Fraction tree -> kernel Expr (Const/Symbol/Add/Mul/Pow/Func only)."""

    if isinstance(tree, (int, Q)):
        return N.Const(tree)
    if not isinstance(tree, tuple) or not tree:
        raise ValueError(f"not a legacy node: {tree!r}")
    tag = tree[0]
    if tag == "var":
        return N.Symbol(tree[1])
    if tag == "add":
        return N.Add([from_legacy(x) for x in tree[1]])
    if tag == "mul":
        return N.Mul([from_legacy(x) for x in tree[1]])
    if tag == "pow":
        return N.Pow(from_legacy(tree[1]), from_legacy(tree[2]))
    if tag == "func":
        return N.Func(tree[1], (from_legacy(tree[2]),))
    raise ValueError(f"unknown legacy tag {tag!r}")


def to_legacy(e: N.Expr):
    """Kernel Expr -> legacy tuple/Fraction tree. Raises ValueError on a node with no legacy form."""

    if isinstance(e, N.Const):
        return to_fraction(e.value)
    if isinstance(e, N.Symbol):
        return ("var", e.name)
    if isinstance(e, N.Add):
        return ("add", [to_legacy(a) for a in e.args])
    if isinstance(e, N.Mul):
        return ("mul", [to_legacy(a) for a in e.args])
    if isinstance(e, N.Pow):
        return ("pow", to_legacy(e.base), to_legacy(e.exp))
    if isinstance(e, N.Func):
        if len(e.args) != 1:
            raise ValueError("legacy func node is unary")
        return ("func", e.name, to_legacy(e.args[0]))
    raise ValueError(f"no legacy equivalent for {type(e).__name__}")


__all__ = ["from_legacy", "to_legacy"]
