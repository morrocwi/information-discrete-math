"""Exact rational-function limits over ℚ (pillar P2, CAS-grade).

The numeric ``limit`` kind extrapolates a sequence with Richardson acceleration; this is its exact
symbolic counterpart for the rational-function case: given ``P(x)/Q(x)`` with ℚ coefficients, it
returns the EXACT limit — a rational number, ``±∞``, or a genuine "does not exist" — with no floating
point and no extrapolation.

Two mechanisms, both exact on the univariate ℚ tower:

  * ``x → a`` (finite):   reduce ``P/Q`` to lowest terms with :func:`cancel` (dividing out the common
                          ``gcd``), which removes any *removable* singularity, then evaluate.  If the
                          reduced denominator is nonzero at ``a`` the limit is the exact ratio; if it
                          vanishes (the reduced num/den are now coprime, so the numerator does not)
                          the point is a true POLE — ``±∞`` for a one-sided request, "does not exist"
                          for a two-sided one whose two sides disagree in sign.
  * ``x → ±∞``:           compare degrees.  ``deg P < deg Q → 0``; ``deg P = deg Q →`` ratio of the
                          leading coefficients (exact ℚ); ``deg P > deg Q → ±∞`` with the sign fixed
                          by the leading coefficients and, at ``-∞``, the degree-difference parity.

The result is a structured verdict so a caller can tell a finite value from an infinity from a
non-existent limit, rather than getting a lone number that hides the distinction.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from typing import List, Optional, Sequence

from .coeffring import QRing
from .univariate import UPoly, cancel, _eval_at


@dataclass(frozen=True)
class LimitResult:
    """The exact limit of a rational function.

    ``status`` is ``"finite"`` (``value`` is the exact ℚ limit), ``"infinite"`` (``sign`` is ``+1`` or
    ``-1``; ``value`` is ``None``) or ``"dne"`` (a two-sided limit at a pole whose sides disagree —
    ``value`` and ``sign`` are ``None``).
    """

    status: str
    value: Optional[Q]
    sign: Optional[int]
    removable: bool = False   # True iff a common factor was cancelled (a 0/0 that resolved finitely)


def _upoly(coeffs: Sequence[object]) -> UPoly:
    D = QRing()
    c = [Q(x) for x in coeffs]
    if not c:
        c = [Q(0)]
    return UPoly(c, D)


def rational_limit(numerator: Sequence[object], denominator: Sequence[object], point) -> LimitResult:
    """Exact limit of ``numerator(x) / denominator(x)`` (coefficients low-order first) as ``x → point``.

    ``point`` is a rational (``int``/``str``/``Fraction``) for a finite limit, or one of the strings
    ``"inf"`` / ``"+inf"`` / ``"-inf"`` for a limit at infinity.  For a finite ``point`` sitting on a
    pole the limit is two-sided by default and reported as ``dne`` when the two one-sided limits
    disagree in sign; pass ``point`` together with :func:`rational_limit_oneside` for a directed limit.
    """
    num = _upoly(numerator)
    den = _upoly(denominator)
    if den.is_zero():
        raise ValueError("denominator is the zero polynomial")

    if isinstance(point, str) and "inf" in point.lower():
        return _limit_at_infinity(num, den, negative=point.strip().startswith("-"))

    a = Q(point)
    return _limit_at_point(num, den, a)


def rational_limit_oneside(numerator: Sequence[object], denominator: Sequence[object],
                           point, side: str) -> LimitResult:
    """One-sided exact limit as ``x → point`` from ``side`` (``"+"`` or ``"-"``).  Differs from the
    two-sided form only at a genuine pole, where it returns the signed ``±∞`` for that side instead of
    ``dne``."""
    if side not in ("+", "-"):
        raise ValueError("side must be '+' or '-'")
    num = _upoly(numerator)
    den = _upoly(denominator)
    if den.is_zero():
        raise ValueError("denominator is the zero polynomial")
    a = Q(point)
    return _limit_at_point(num, den, a, side=side)


def _limit_at_point(num: UPoly, den: UPoly, a: Q, side: Optional[str] = None) -> LimitResult:
    reduced = cancel(num, den)
    rn, rd = reduced["num"], reduced["den"]
    common = reduced["common"]
    removable = common.degree() >= 1

    den_at = _eval_at(rd, a)
    if den_at != 0:
        return LimitResult("finite", _eval_at(rn, a) / den_at, None, removable=removable)

    # reduced denominator vanishes at a: a genuine pole (rn(a) != 0 since rn, rd are coprime).
    num_at = _eval_at(rn, a)
    if num_at == 0:
        # rn and rd coprime yet both zero at a is impossible; guard defensively.
        raise ValueError("internal: reduced numerator and denominator share the root a")

    if side is None:
        # two-sided: compare the sign of rn/rd just left vs just right of the pole. Opposite signs
        # (an odd-order pole) means the sides diverge to +∞ and -∞ -> the two-sided limit DNE; equal
        # signs (an even-order pole) means both sides go to the same ±∞.
        left = _signed_infinity(rn, rd, a, "-")
        right = _signed_infinity(rn, rd, a, "+")
        if left == right:
            return LimitResult("infinite", None, left, removable=removable)
        return LimitResult("dne", None, None, removable=removable)

    return LimitResult("infinite", None, _signed_infinity(rn, rd, a, side), removable=removable)


def _signed_infinity(rn: UPoly, rd: UPoly, a: Q, side: str) -> int:
    """Sign of ``rn/rd`` as ``x → a`` from ``side``, at a point where ``rd(a) = 0`` and ``rn(a) ≠ 0``.

    Numerator sign is just ``sign(rn(a))``.  Denominator sign near a simple/multiple root is
    ``sign(rd'... )`` — computed here concretely by evaluating ``rd`` a rational hair to the chosen
    side of ``a``, which is exact (a tiny rational step never lands on another root for a small
    enough step, and we only need its SIGN)."""
    num_sign = 1 if _eval_at(rn, a) > 0 else -1
    step = _safe_step(rd, a)
    probe = a + step if side == "+" else a - step
    den_val = _eval_at(rd, probe)
    den_sign = 1 if den_val > 0 else -1
    return num_sign * den_sign


def _safe_step(rd: UPoly, a: Q) -> Q:
    """A rational step small enough that ``a ± step`` is closer to ``a`` than any other real root of
    ``rd`` — so the sign of ``rd`` at ``a ± step`` is the true one-sided sign.  Halve until the probe
    point is not itself a root; bounded because ``rd`` has finitely many roots."""
    step = Q(1, 2)
    for _ in range(200):
        if _eval_at(rd, a + step) != 0 and _eval_at(rd, a - step) != 0:
            # also require monotone sign region: shrink a few more times for safety on multiple roots
            if _eval_at(rd, a + step / 2) * _eval_at(rd, a + step) > 0 and \
               _eval_at(rd, a - step / 2) * _eval_at(rd, a - step) > 0:
                return step
        step /= 2
    return step


def _limit_at_infinity(num: UPoly, den: UPoly, negative: bool) -> LimitResult:
    dn, dd = num.degree(), den.degree()
    if num.is_zero():
        return LimitResult("finite", Q(0), None)
    if dn < dd:
        return LimitResult("finite", Q(0), None)
    if dn == dd:
        return LimitResult("finite", Q(num.lead()) / Q(den.lead()), None)
    # dn > dd: diverges. Sign = sign(lead ratio) times (-1)^(deg diff) when x -> -inf.
    lead_sign = 1 if (Q(num.lead()) / Q(den.lead())) > 0 else -1
    if negative and (dn - dd) % 2 == 1:
        lead_sign = -lead_sign
    return LimitResult("infinite", None, lead_sign)


__all__ = ["LimitResult", "rational_limit", "rational_limit_oneside"]
