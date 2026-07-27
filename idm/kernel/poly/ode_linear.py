"""Exact general solution of a linear, constant-coefficient, homogeneous ODE (pillar P2, CAS-grade).

For an ODE ``a_n y^(n) + … + a_1 y' + a_0 y = 0`` with constant coefficients, the general solution is
read off the CHARACTERISTIC POLYNOMIAL ``p(r) = a_n r^n + … + a_1 r + a_0`` exactly:

  * each real root ``ρ`` of multiplicity ``m``    → basis ``e^{ρx}, x e^{ρx}, …, x^{m-1} e^{ρx}``
  * each complex-conjugate pair ``α ± βi`` (mult m) → basis ``x^k e^{αx} cos(βx)``, ``x^k e^{αx} sin(βx)``

The characteristic polynomial is factored EXACTLY over ℚ (:func:`factor_over_Q`), so:

  * degree-1 irreducible factors give the exact rational roots (with multiplicity);
  * degree-2 irreducible factors give the exact conjugate pair — ``α = -b/2`` (rational) and
    ``β² = (4c - b²)/4`` (rational) for a negative discriminant, or the two irrational real roots
    ``(-b ± √disc)/2`` for a positive one;
  * a degree-≥3 irreducible factor has roots not expressible by the radicals this kernel offers, so
    the solver HOLDs on that factor rather than fabricating a closed form — an honest fence.

The result lists every basis function of the solution space (its dimension equals the ODE order),
each tagged with its exact data, plus a human-readable general solution ``C₁·… + C₂·… ``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction as Q
from math import isqrt
from typing import List, Optional, Sequence

from .coeffring import QRing
from .factorize import factor_over_Q
from .univariate import UPoly


@dataclass(frozen=True)
class ODESolution:
    """The exact general solution of a linear constant-coefficient homogeneous ODE.

    ``status`` is ``"solved"`` (every characteristic factor resolved) or ``"partial"`` (a degree-≥3
    irreducible factor was left unresolved — its factor is listed in ``unresolved``).  ``basis`` is the
    list of basis functions spanning the solution space; ``general`` is the human-readable combination.
    """

    status: str
    order: int
    basis: List[dict]
    general: str
    unresolved: List[str] = field(default_factory=list)


def _fmt_q(x: Q) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def _exp_factor(rho: Q) -> str:
    if rho == 0:
        return "1"
    if rho == 1:
        return "e^x"
    if rho == -1:
        return "e^(-x)"
    return f"e^({_fmt_q(rho)}*x)"


def _xpow(k: int) -> str:
    return "" if k == 0 else ("x*" if k == 1 else f"x^{k}*")


def _sqrt_str(q: Q) -> str:
    """Render √q, collapsing a perfect rational square to its exact rational root (so √1 → '1')."""
    sn, sd = isqrt(q.numerator), isqrt(q.denominator)
    if sn * sn == q.numerator and sd * sd == q.denominator:
        return _fmt_q(Q(sn, sd))
    return f"sqrt({_fmt_q(q)})"


def solve_linear_ode(coeffs: Sequence[object]) -> ODESolution:
    """Exact general solution of ``Σ coeffs[i] · y^(i) = 0``.

    ``coeffs`` are the constant coefficients low-order-first: ``coeffs[i]`` multiplies the ``i``-th
    derivative (``coeffs[0]·y + coeffs[1]·y' + …``), which is exactly the characteristic polynomial in
    ``r``.  Raises ``ValueError`` on an empty/degenerate operator; otherwise returns an
    :class:`ODESolution` (``"partial"`` when a degree-≥3 irreducible factor is left unresolved).
    """
    D = QRing()
    c = [Q(x) for x in coeffs]
    while len(c) > 1 and c[-1] == 0:                        # drop zero leading (highest-derivative) terms
        c = c[:-1]
    if len(c) <= 1 or all(x == 0 for x in c):
        raise ValueError("need a genuine differential operator (order >= 1)")
    order = len(c) - 1

    char = UPoly(c, D)
    _lead, factors = factor_over_Q(char)

    basis: List[dict] = []
    unresolved: List[str] = []
    terms: List[str] = []
    ci = 0

    for g, mult in factors:
        deg = g.degree()
        gc = list(g.coeffs)                                 # monic, low-order first
        if deg == 1:
            rho = -gc[0]                                    # root of (r + gc0) = -gc0  (monic: gc1 = 1)
            for k in range(mult):
                ci += 1
                term = f"{_xpow(k)}{_exp_factor(rho)}"
                basis.append({"type": "real", "root": _fmt_q(rho), "poly_power": k, "term": term})
                terms.append(f"C{ci}*{term}")
        elif deg == 2:
            b, cc = gc[1], gc[0]                             # r^2 + b r + cc (monic)
            disc = b * b - 4 * cc
            if disc < 0:
                alpha = -b / 2
                beta_sq = (4 * cc - b * b) / 4               # β² exact ℚ
                for k in range(mult):
                    exp_a = _exp_factor(alpha)
                    exp_a = "" if exp_a == "1" else exp_a + "*"
                    beta_str = _sqrt_str(beta_sq)
                    arg = "x" if beta_str == "1" else f"{beta_str}*x"
                    for trig in ("cos", "sin"):
                        ci += 1
                        term = f"{_xpow(k)}{exp_a}{trig}({arg})"
                        basis.append({"type": "complex", "alpha": _fmt_q(alpha),
                                      "beta_squared": _fmt_q(beta_sq), "poly_power": k,
                                      "trig": trig, "term": term})
                        terms.append(f"C{ci}*{term}")
            else:
                # irreducible over ℚ with disc > 0: two irrational real roots (-b ± √disc)/2
                half_b = -b / 2
                for sign, sgnstr in ((1, "+"), (-1, "-")):
                    root_expr = f"({_fmt_q(half_b)} {sgnstr} sqrt({_fmt_q(disc)})/2)"
                    for k in range(mult):
                        ci += 1
                        term = f"{_xpow(k)}e^({root_expr}*x)"
                        basis.append({"type": "real_irrational", "root_expr": root_expr,
                                      "poly_power": k, "term": term})
                        terms.append(f"C{ci}*{term}")
        else:
            unresolved.append(f"irreducible degree-{deg} factor (roots not in radicals)")

    status = "solved" if not unresolved else "partial"
    general = " + ".join(terms) if terms else "0"
    return ODESolution(status, order, basis, general, unresolved)


__all__ = ["ODESolution", "solve_linear_ode"]
