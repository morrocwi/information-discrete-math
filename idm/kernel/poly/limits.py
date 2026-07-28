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
from .univariate import UPoly, cancel, divmod_, _eval_at


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

    order, cofactor_sign = _pole_order_and_cofactor_sign(rd, a)

    if side is None:
        # two-sided: the two one-sided signs agree iff the pole order is EVEN (both sides → the same
        # ±∞); an ODD-order pole flips sign across a, so the sides diverge to +∞ and -∞ → DNE.
        right = _pole_sign(rn, a, cofactor_sign, order, "+")
        left = _pole_sign(rn, a, cofactor_sign, order, "-")
        if left == right:
            return LimitResult("infinite", None, right, removable=removable)
        return LimitResult("dne", None, None, removable=removable)

    return LimitResult("infinite", None, _pole_sign(rn, a, cofactor_sign, order, side),
                       removable=removable)


def _pole_order_and_cofactor_sign(rd: UPoly, a: Q):
    """Factor ``rd = (x - a)^m · g(x)`` with ``g(a) ≠ 0`` (exact) and return ``(m, sign(g(a)))``.

    This is the exact way to read the one-sided sign of ``rd`` near ``a``: for small ``ε > 0``,
    ``rd(a + ε) = ε^m · g(a + ε)`` has the sign of ``g(a)``, and ``rd(a - ε) = (-ε)^m · g(a - ε)`` has
    the sign of ``(-1)^m · g(a)`` — no numeric probe step (and therefore no risk of a nearby second
    root corrupting the sign, the bug a fixed-halving heuristic had)."""
    D = rd.domain
    divisor = UPoly([D.neg(a), D.one()], D)                 # (x - a)
    g = rd
    m = 0
    while g.degree() >= 1:
        q, r = divmod_(g, divisor)
        if not r.is_zero():
            break
        g = q
        m += 1
    g_at = _eval_at(g, a)                                    # ≠ 0 by construction
    return m, (1 if g_at > 0 else -1)


def _pole_sign(rn: UPoly, a: Q, cofactor_sign: int, order: int, side: str) -> int:
    """Sign of ``rn/rd`` as ``x → a`` from ``side`` at a pole of multiplicity ``order`` whose
    denominator cofactor has sign ``cofactor_sign``.  ``rn(a) ≠ 0`` (rn, rd are coprime), so the
    numerator contributes ``sign(rn(a))``; the denominator contributes ``cofactor_sign`` from the
    right and ``(-1)^order · cofactor_sign`` from the left."""
    num_sign = 1 if _eval_at(rn, a) > 0 else -1
    den_sign = cofactor_sign if side == "+" else cofactor_sign * (1 if order % 2 == 0 else -1)
    return num_sign * den_sign


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
