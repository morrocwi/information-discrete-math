"""Kernel-native simplification surface (pillar P2 depth).

One entry the future migration will adopt, unifying two things that live apart today:

* :func:`simplify` — assumption-aware normalization. With no assumptions it is byte-identical to
  :func:`idm.symbolic.simplify` (so migrating the ``simplify`` kind onto it changes nothing); with an
  assumption set it routes the nested-power collapse through the P1.3 domain-gated rewrite engine.
* :func:`cancel_rational` — reduce a ratio of univariate polynomials to lowest terms via the P1.4/P2
  polynomial tower (``poly.cancel``). This is real depth the legacy simplifier has none of: it turns
  ``(x²−1)/(x−1)`` into ``x+1`` as an exact rational-function identity.

Everything is exact ℚ. ``cancel_rational`` is verifiable by cross-multiplication.
"""

from __future__ import annotations

from fractions import Fraction as Q
from typing import Optional

from . import cas as SYM
from . import poly as P


def simplify(expr, assumptions: Optional[object] = None):
    """Assumption-aware simplify. Byte-identical to symbolic.simplify when ``assumptions`` is None."""
    tree = SYM.parse(expr) if isinstance(expr, str) else expr
    return SYM.simplify(tree, assumptions)


def _coeffs_low_to_high(expr, var: str):
    """Exact ℚ coefficient list (low-order first) of a univariate polynomial, or None if not one."""
    tree = SYM.parse(expr) if isinstance(expr, str) else expr
    cmap = SYM.poly_coeffs(tree, var)
    if cmap is None:
        return None
    deg = max(cmap) if cmap else 0
    return [Q(cmap.get(k, Q(0))) for k in range(deg + 1)]


def _coeffs_to_tree(coeffs, var: str):
    """Rebuild a legacy expression tree from a low-order-first coefficient list."""
    terms = []
    for i, c in enumerate(coeffs):
        if c == 0:
            continue
        if i == 0:
            terms.append(c)
        elif i == 1:
            terms.append(("mul", [c, ("var", var)]) if c != 1 else ("var", var))
        else:
            power = ("pow", ("var", var), Q(i))
            terms.append(("mul", [c, power]) if c != 1 else power)
    if not terms:
        return Q(0)
    return terms[0] if len(terms) == 1 else ("add", terms)


def cancel_rational(num, den, var: str) -> dict:
    """Reduce num/den (univariate polynomials in ``var``) to lowest terms over ℚ.

    Returns the reduced numerator/denominator (as tree + string) and the cancelled common factor.
    Verifiable by cross-multiplication: reduced_num · den == reduced_den · num.
    """
    nco = _coeffs_low_to_high(num, var)
    dco = _coeffs_low_to_high(den, var)
    if nco is None or dco is None:
        return {"status": "HOLD", "reason": "numerator/denominator is not a polynomial in the variable"}
    Qr = P.QRing()
    result = P.cancel(P.UPoly(nco, Qr), P.UPoly(dco, Qr))
    rn = _coeffs_to_tree(result["num"].coeffs, var)
    rd = _coeffs_to_tree(result["den"].coeffs, var)
    common = _coeffs_to_tree(result["common"].coeffs, var)
    return {
        "status": "ok",
        "num": rn, "den": rd, "common": common,
        "num_str": SYM.tostr(rn), "den_str": SYM.tostr(rd), "common_str": SYM.tostr(common),
    }


__all__ = ["simplify", "cancel_rational"]
