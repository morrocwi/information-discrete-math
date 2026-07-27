"""The exact/certified number tower (pillar P1.6, canonical rung set).

A strict ladder — **no type auto-widens**. Every rung transition is an explicit ``coerce_up`` /
``coerce_down`` call; there is never a bare ``+`` or ``float()`` that silently drops exactness. Coercing
an exact value onto a ball rung honestly downgrades the tier to ``finite_diagnostic`` — never ``exact``.

Wave-0 scope (P1.1): ``ExactInteger``/``ExactRational`` carry real bodies and lossless/​partial
coercion; ``AlgebraicNumber``/``RealBall``/``ComplexBall`` are typed rungs whose heavy arithmetic
bodies land in a later wave (kernel/eval.py). The coercion *contract* — and its honesty guarantees —
is fully live now.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from typing import Optional, Union

from .tiers import CERTIFIED, HOLD, OK, Tier


@dataclass(frozen=True, slots=True)
class ExactInteger:
    value: int


@dataclass(frozen=True, slots=True)
class ExactRational:
    value: Q


@dataclass(frozen=True, slots=True)
class AlgebraicNumber:
    """A real/complex algebraic number: a minimal polynomial + an isolating enclosure + a root index.

    Ball-based so it subsumes complex roots and carries an explicit re-isolation contract; heavy
    arithmetic (precision escalation, field ops) is a later-wave body. ``escalate_precision`` must
    HOLD, never guess, if re-isolation finds overlapping balls.
    """

    min_poly: tuple           # Fraction coeffs, low -> high
    interval: object          # RealBall | ComplexBall isolating enclosure (one root)
    index: int


@dataclass(frozen=True, slots=True)
class ComplexExact:
    """Exact complex number over exact-rational/algebraic components (kept distinct from ComplexBall,
    which is a finite-precision enclosure, not exact)."""

    re: Union[ExactRational, AlgebraicNumber]
    im: Union[ExactRational, AlgebraicNumber]


@dataclass(frozen=True, slots=True)
class RealBall:
    lo: object                # mpmath.mpf, directed-rounding DOWN
    hi: object                # mpmath.mpf, directed-rounding UP
    prec_dps: int
    name: str = "R~"          # self-disclosing non-exactness — never "the reals"


@dataclass(frozen=True, slots=True)
class ComplexBall:
    re: RealBall
    im: RealBall
    prec_dps: int


Number = Union[ExactInteger, ExactRational, AlgebraicNumber, ComplexExact]
_EXACT_RUNGS = (ExactInteger, ExactRational, AlgebraicNumber, ComplexExact)
_BALL_RUNGS = (RealBall, ComplexBall)


@dataclass(frozen=True)
class Certificate:
    """The numeric-layer view of the shared result vocabulary (value + status + tier + bound/reason)."""

    value: Optional[object]
    status: str               # OK | CERTIFIED | HOLD — from .tiers, never a new word
    tier: Tier
    bound: Optional[object] = None
    reason: Optional[str] = None

    def to_dict(self) -> dict:
        d: dict = {"status": self.status, "tier": self.tier.value}
        if self.value is not None:
            d["value"] = self.value
        if self.bound is not None:
            d["bound"] = self.bound
        if self.reason is not None:
            d["reason"] = self.reason
        return d


def coerce_up(x, target_rung: type, *, prec_dps: int = 30) -> Certificate:
    """Widen along ℤ → ℚ → Algebraic → RealBall/ComplexBall. Never silent, never automatic.

    Coercing an exact value to a ball rung comes back tier ``finite_diagnostic`` — never ``exact``.
    Returns a HOLD-status ``Certificate`` on a nonsensical/unsupported target (never raises).
    """

    # exact -> exact widenings
    if target_rung is ExactRational:
        if isinstance(x, ExactInteger):
            return Certificate(ExactRational(Q(x.value)), OK, Tier.EXACT)
        if isinstance(x, ExactRational):
            return Certificate(x, OK, Tier.EXACT)
    if target_rung is ExactInteger and isinstance(x, ExactInteger):
        return Certificate(x, OK, Tier.EXACT)

    # exact -> ball: honest tier downgrade
    if target_rung is RealBall and isinstance(x, (ExactInteger, ExactRational)):
        try:
            import mpmath as mp
            mp.mp.dps = prec_dps
            v = mp.mpf(x.value.numerator) / mp.mpf(x.value.denominator) if isinstance(x, ExactRational) \
                else mp.mpf(x.value)
            return Certificate(RealBall(v, v, prec_dps), OK, Tier.FINITE_DIAGNOSTIC)
        except Exception as exc:  # pragma: no cover
            return Certificate(None, HOLD, Tier.FINITE_DIAGNOSTIC, reason=f"ball coercion failed: {exc}")

    return Certificate(None, HOLD, Tier.EXACT,
                       reason=f"unsupported coercion {type(x).__name__} -> {target_rung.__name__}")


def coerce_down(x, target_rung: type) -> Certificate:
    """Narrow along RealBall → Algebraic → ExactRational → ExactInteger, PARTIAL.

    Returns a HOLD-status ``Certificate`` when the narrowing is not exact (e.g. a ball whose width
    has not collapsed to a single rational, or a rational whose denominator ≠ 1 for ℤ).
    """

    if target_rung is ExactInteger:
        if isinstance(x, ExactInteger):
            return Certificate(x, OK, Tier.EXACT)
        if isinstance(x, ExactRational) and x.value.denominator == 1:
            return Certificate(ExactInteger(int(x.value)), OK, Tier.EXACT)
        return Certificate(None, HOLD, Tier.EXACT,
                           reason="not exactly representable as an integer")
    if target_rung is ExactRational:
        if isinstance(x, ExactRational):
            return Certificate(x, OK, Tier.EXACT)
        if isinstance(x, ExactInteger):
            return Certificate(ExactRational(Q(x.value)), OK, Tier.EXACT)
    return Certificate(None, HOLD, Tier.EXACT,
                       reason=f"cannot narrow {type(x).__name__} -> {target_rung.__name__} exactly")


def from_python(value) -> Number:
    """Build the tightest exact rung for a Python int/Fraction (float rejected — no silent widening)."""

    if isinstance(value, bool):
        return ExactInteger(int(value))
    if isinstance(value, int):
        return ExactInteger(value)
    if isinstance(value, Q):
        return ExactInteger(int(value)) if value.denominator == 1 else ExactRational(value)
    raise TypeError(f"no exact rung for {type(value).__name__} (float is rejected by design)")


def to_fraction(n: Number) -> Q:
    """Exact ℚ view of an ExactInteger/ExactRational (used by the legacy bridge)."""

    if isinstance(n, ExactInteger):
        return Q(n.value)
    if isinstance(n, ExactRational):
        return n.value
    raise TypeError(f"{type(n).__name__} has no exact rational view")


__all__ = [
    "ExactInteger", "ExactRational", "AlgebraicNumber", "ComplexExact",
    "RealBall", "ComplexBall", "Number", "Certificate",
    "coerce_up", "coerce_down", "from_python", "to_fraction",
]
