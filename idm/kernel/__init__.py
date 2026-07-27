"""IDM Symbolic Kernel v2 — the one import surface: ``from idm import kernel as K``.

Phase 1 / Wave 0 (pillar P1.1): the shared status/tier vocabulary, the exact/certified number tower,
the immutable expression tree with structural hashing + request-scoped interning, and the migration
bridge to the legacy :mod:`idm.symbolic` tuple tree. Additive — no existing module changes; the new
tree is a tested target for later phases to migrate the 258 kinds onto.

Later waves add: ``assumptions`` (P1.2), ``engine``/``rewrite`` (P1.3), ``eval`` (numeric bridge),
``solution`` (P1.5), and ``poly`` (P1.4). Those import surfaces will extend this file.
"""

from __future__ import annotations

from .tiers import (
    Tier, OK, CERTIFIED, HOLD,
    HoldError, DomainUnsafeRewrite, ResourceBudgetExceeded,
)
from .numbers import (
    ExactInteger, ExactRational, AlgebraicNumber, ComplexExact,
    RealBall, ComplexBall, Number, Certificate,
    coerce_up, coerce_down, from_python, to_fraction,
)
from .nodes import (
    Expr, Const, Symbol, Undefined, Infinity, ComplexInfinity,
    Add, Mul, Pow, Func, Relation, Piecewise, Derivative, Integral, Limit,
)
from .hashcons import struct_hash, canonical_order_key, InternTable
from .legacy import from_legacy, to_legacy

__all__ = [
    # tiers
    "Tier", "OK", "CERTIFIED", "HOLD",
    "HoldError", "DomainUnsafeRewrite", "ResourceBudgetExceeded",
    # numbers
    "ExactInteger", "ExactRational", "AlgebraicNumber", "ComplexExact",
    "RealBall", "ComplexBall", "Number", "Certificate",
    "coerce_up", "coerce_down", "from_python", "to_fraction",
    # nodes
    "Expr", "Const", "Symbol", "Undefined", "Infinity", "ComplexInfinity",
    "Add", "Mul", "Pow", "Func", "Relation", "Piecewise",
    "Derivative", "Integral", "Limit",
    # hashcons + bridge
    "struct_hash", "canonical_order_key", "InternTable",
    "from_legacy", "to_legacy",
]
