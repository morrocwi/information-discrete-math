"""The kernel expression tree (pillar P1.1) — immutable, structurally hashed, canonically ordered.

Additive in Phase 1: this is *not yet* the wire format any of the 258 kinds speaks (the ``symbolic_*``
kinds keep using :mod:`idm.symbolic`'s legacy tuple tree throughout Phase 1). It exists so later phases
have a real, tested target to migrate onto. Every node is effectively immutable (no mutators), carries
a cached bottom-up structural hash ``_hash`` and an O(1) ordering key ``_order``, and defines
``__hash__``/``__eq__`` so structurally-equal trees compare equal (and intern to one object).

Explicit non-readout leaves — ``Undefined``, ``Infinity``, ``ComplexInfinity`` — set
``is_nonreadout = True``. They are never produced silently; the continuum is named, never injected.
Calculus nodes (``Derivative``/``Integral``/``Limit``) are *representable*, never auto-evaluating.
"""

from __future__ import annotations

from fractions import Fraction as Q
from typing import Optional, Tuple

from .hashcons import canonical_order_key, struct_hash
from .numbers import Number, from_python, _EXACT_RUNGS


class Expr:
    """Abstract base for every kernel node."""

    __slots__ = ()
    is_nonreadout = False

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if self is other:
            return True
        if type(self) is not type(other):
            return False
        return self._key() == other._key()

    def _key(self) -> tuple:  # structural identity; overridden per node
        return ()

    def children(self) -> Tuple["Expr", ...]:
        return ()


class Const(Expr):
    __slots__ = ("value", "_hash", "_order")

    def __init__(self, value):
        # A Const holds ONLY an exact readout rung (or a plain int/Fraction, coerced to one).
        # A finite-precision ball or a Certificate is NOT an exact readout and is rejected here,
        # so a non-readout value can never be laundered into a leaf labeled exact (readout-first).
        if isinstance(value, (int, Q)):
            self.value: Number = from_python(value)
        elif isinstance(value, _EXACT_RUNGS):
            self.value = value
        else:
            raise TypeError(
                "Const value must be an exact Number rung "
                "(ExactInteger/ExactRational/AlgebraicNumber/ComplexExact) or int/Fraction; "
                f"got {type(value).__name__}"
            )
        self._hash = struct_hash("Const", (), self.value)
        self._order = canonical_order_key(self)

    def _key(self):
        return (self.value,)


class Symbol(Expr):
    __slots__ = ("name", "_hash", "_order")

    def __init__(self, name: str):
        self.name = name
        self._hash = struct_hash("Symbol", (), name)
        self._order = canonical_order_key(self)

    def _key(self):
        return (self.name,)


# ---- explicit non-readout leaves ----
class Undefined(Expr):
    __slots__ = ("reason", "_hash", "_order")
    is_nonreadout = True

    def __init__(self, reason: str = ""):
        self.reason = reason
        self._hash = struct_hash("Undefined", (), reason)
        self._order = canonical_order_key(self)

    def _key(self):
        return (self.reason,)


class Infinity(Expr):
    __slots__ = ("sign", "_hash", "_order")
    is_nonreadout = True

    def __init__(self, sign: int = 1):
        self.sign = sign
        self._hash = struct_hash("Infinity", (), sign)
        self._order = canonical_order_key(self)

    def _key(self):
        return (self.sign,)


class ComplexInfinity(Expr):
    __slots__ = ("_hash", "_order")
    is_nonreadout = True

    def __init__(self):
        self._hash = struct_hash("ComplexInfinity", (), None)
        self._order = canonical_order_key(self)

    def _key(self):
        return ()


# ---- algebraic structure ----
class Add(Expr):
    __slots__ = ("args", "_hash", "_order")

    def __init__(self, args):
        self.args: Tuple[Expr, ...] = tuple(sorted(args, key=lambda e: e._order))
        self._hash = struct_hash("Add", tuple(a._hash for a in self.args), None)
        self._order = canonical_order_key(self)

    def _key(self):
        return self.args

    def children(self):
        return self.args


class Mul(Expr):
    __slots__ = ("args", "_hash", "_order")

    def __init__(self, args):
        self.args: Tuple[Expr, ...] = tuple(sorted(args, key=lambda e: e._order))
        self._hash = struct_hash("Mul", tuple(a._hash for a in self.args), None)
        self._order = canonical_order_key(self)

    def _key(self):
        return self.args

    def children(self):
        return self.args


class Pow(Expr):
    __slots__ = ("base", "exp", "_hash", "_order")

    def __init__(self, base: Expr, exp: Expr):
        self.base = base
        self.exp = exp
        self._hash = struct_hash("Pow", (base._hash, exp._hash), None)
        self._order = canonical_order_key(self)

    def _key(self):
        return (self.base, self.exp)

    def children(self):
        return (self.base, self.exp)


class Func(Expr):
    __slots__ = ("name", "args", "_hash", "_order")

    def __init__(self, name: str, args):
        self.name = name
        self.args: Tuple[Expr, ...] = tuple(args)
        self._hash = struct_hash("Func", tuple(a._hash for a in self.args), name)
        self._order = canonical_order_key(self)

    def _key(self):
        return (self.name, self.args)

    def children(self):
        return self.args


# ---- relations / logic (net-new vs. idm.symbolic) ----
class Relation(Expr):
    __slots__ = ("op", "lhs", "rhs", "_hash", "_order")

    def __init__(self, op: str, lhs: Expr, rhs: Expr):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
        self._hash = struct_hash("Relation", (lhs._hash, rhs._hash), op)
        self._order = canonical_order_key(self)

    def _key(self):
        return (self.op, self.lhs, self.rhs)

    def children(self):
        return (self.lhs, self.rhs)


# ---- domain-safety escape valve (defined, unused by any Phase-1 rewrite path) ----
class Piecewise(Expr):
    __slots__ = ("branches", "otherwise", "_hash", "_order")

    def __init__(self, branches, otherwise: Optional[Expr] = None):
        self.branches: Tuple[Tuple[Expr, Expr], ...] = tuple((v, c) for v, c in branches)
        self.otherwise = otherwise
        flat = tuple(h for v, c in self.branches for h in (v._hash, c._hash))
        if otherwise is not None:
            flat = flat + (otherwise._hash,)
        self._hash = struct_hash("Piecewise", flat, None)
        self._order = canonical_order_key(self)

    def _key(self):
        return (self.branches, self.otherwise)


# ---- calculus as nodes (representable, never auto-evaluating) ----
class Derivative(Expr):
    __slots__ = ("expr", "var", "order", "_hash", "_order")

    def __init__(self, expr: Expr, var: Symbol, order: int = 1):
        self.expr = expr
        self.var = var
        self.order = order
        self._hash = struct_hash("Derivative", (expr._hash, var._hash), order)
        self._order = canonical_order_key(self)

    def _key(self):
        return (self.expr, self.var, self.order)

    def children(self):
        return (self.expr, self.var)


class Integral(Expr):
    __slots__ = ("expr", "var", "lower", "upper", "_hash", "_order")

    def __init__(self, expr: Expr, var: Symbol, lower: Optional[Expr] = None, upper: Optional[Expr] = None):
        self.expr = expr
        self.var = var
        self.lower = lower
        self.upper = upper
        kids = (expr._hash, var._hash,
                lower._hash if lower is not None else 0,
                upper._hash if upper is not None else 0)
        self._hash = struct_hash("Integral", kids, None)
        self._order = canonical_order_key(self)

    def _key(self):
        return (self.expr, self.var, self.lower, self.upper)


class Limit(Expr):
    __slots__ = ("expr", "var", "point", "direction", "_hash", "_order")

    def __init__(self, expr: Expr, var: Symbol, point: Expr, direction: str = "both"):
        self.expr = expr
        self.var = var
        self.point = point
        self.direction = direction
        self._hash = struct_hash("Limit", (expr._hash, var._hash, point._hash), direction)
        self._order = canonical_order_key(self)

    def _key(self):
        return (self.expr, self.var, self.point, self.direction)


__all__ = [
    "Expr", "Const", "Symbol", "Undefined", "Infinity", "ComplexInfinity",
    "Add", "Mul", "Pow", "Func", "Relation", "Piecewise",
    "Derivative", "Integral", "Limit",
]
