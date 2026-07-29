"""idm.kernel.poly.rational_integration — EXACT symbolic integration of a rational function P(x)/Q(x).

WP8 (Increment 1). Wires the exact ℚ polynomial tower into a real symbolic integrator for rational
functions — where the elementary integrator only handled polynomials + a few linear-argument patterns.

Method (all exact over ℚ):
  1. polynomial part by division: ``P = poly·Q + R`` → ``∫poly`` directly, continue with the proper ``R/Q``;
  2. factor ``Q`` over ℚ into irreducibles ``∏ f_j^{m_j}`` (:func:`factor_over_Q`);
  3. partial fractions ``R/Q = Σ_{j,k} N_{j,k}/f_j^k`` (deg N_{j,k} < deg f_j) by **undetermined coefficients**
     — clear denominators, match coefficients, solve the exact ℚ linear system;
  4. integrate each term:
       * ``c/(x−a)``           → ``c·ln(x−a)``
       * ``c/(x−a)^k`` (k≥2)   → ``−c/((k−1)(x−a)^{k−1})`` (a rational term)
       * ``(bx+c)/(x²+px+q)``  (irreducible) → ``(b/2)·ln(x²+px+q) + K·arctan((x+p/2)/w)``, ``w=√(q−p²/4)``.

Scope: linear AND irreducible-quadratic factors to ANY multiplicity — the repeated-quadratic case uses the
reduction formula ∫du/(u²+w²)^n. Only an irreducible factor of degree ≥3 HOLDs honestly (needs algebraic-
function integration / Risch — a declared later increment). Every step is exact ℚ; verifiable by
differentiating the answer back.
"""
from __future__ import annotations

from fractions import Fraction as Q

from .univariate import UPoly, add, mul, divmod_, derivative
from .factorize import factor_over_Q, FactorizationBudgetExceeded
from .linsolve import linear_solve
from .coeffring import QRing

_QR = QRing()


class RationalIntegralHOLD(Exception):
    """Raised when the rational function is outside scope — only a degree-≥3 irreducible denominator
    factor, which needs algebraic-function / Risch integration (a declared later increment)."""


def _P(coeffs):
    return UPoly([Q(c) for c in coeffs], _QR)


def _fmt(x: Q) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def _reduce_quad(k: int, w2: Q):
    """The reduction ∫du/(u²+w²)^k = Σ_j coeff_j · u/(u²+w²)^j  +  arctan_coeff · (1/w)·arctan(u/w).
    Returns ({j: coeff_j}, arctan_coeff), exact over ℚ (w² rational). Recurrence:
        I_k = u/(2w²(k−1)(u²+w²)^{k−1}) + (2k−3)/(2w²(k−1))·I_{k−1},  I_1 = (1/w)arctan(u/w)."""
    if k == 1:
        return {}, Q(1)
    sub_terms, sub_arc = _reduce_quad(k - 1, w2)
    fac = Q(2 * k - 3) / (2 * w2 * (k - 1))
    terms = {j: fac * co for j, co in sub_terms.items()}
    terms[k - 1] = terms.get(k - 1, Q(0)) + Q(1) / (2 * w2 * (k - 1))
    return terms, fac * sub_arc


def _powpoly(g: UPoly, k: int) -> UPoly:
    acc = UPoly([Q(1)], _QR)
    for _ in range(k):
        acc = mul(acc, g)
    return acc


def integrate_rational(num_coeffs, den_coeffs, var: str = "x") -> dict:
    """∫ P/Q dx exactly for a rational function over ℚ (coeffs low→high). Returns the structured integral
    and a human-readable string, or raises :class:`RationalIntegralHOLD` outside the Increment-1 scope."""
    num, den = _P(num_coeffs), _P(den_coeffs)
    if den.is_zero():
        raise RationalIntegralHOLD("denominator is the zero polynomial")
    if num.is_zero():
        return {"integral": "0", "polynomial_part": "0", "rational_part": "0",
                "log_terms": [], "arctan_terms": [], "constant": "C"}

    # 1) polynomial part
    poly_quot, rem = divmod_(num, den)
    poly_int = _integrate_poly(poly_quot, var)

    # 2) factor the denominator
    try:
        lead, factors = factor_over_Q(den.monic(), budget=30_000)
    except FactorizationBudgetExceeded as ex:
        raise RationalIntegralHOLD(f"denominator factorization exceeded the budget ({ex})")
    den_lead = den.lead()                                  # keep the overall 1/lead scaling of the remainder
    # remainder over the monic denominator: rem/den = (rem/den_lead) / den_monic
    rem = UPoly([c / den_lead for c in rem.coeffs], _QR)
    den_monic = den.monic()

    for f, m in factors:
        if f.degree() >= 3:
            raise RationalIntegralHOLD(
                f"denominator has an irreducible degree-{f.degree()} factor (needs algebraic/Risch — later increment)")

    if rem.is_zero():
        parts = [p for p in (poly_int,) if p and p != "0"]
        return _assemble(parts, [], [], "0")

    # 3) partial fractions by undetermined coefficients over the irreducible factors
    coeffs_by_term, terms = _partial_fractions(rem, den_monic, factors)

    # 4) integrate each partial-fraction term
    log_terms, arctan_terms, rational_terms, extra = [], [], [], []
    for (f, k), N in zip(terms, coeffs_by_term):
        if f.degree() == 1:                               # (x - a)
            a = -f.coeffs[0]                              # f = x + f0, root a = -f0 (monic)
            c = N.coeffs[0] if N.coeffs else Q(0)
            if c == 0:
                continue
            if k == 1:
                log_terms.append({"coeff": _fmt(c), "arg": _linfac_str(a, var)})
            else:
                rc = -c / (k - 1)
                rational_terms.append(f"({_fmt(rc)})/({_linfac_str(a, var)})^{k - 1}")
        else:                                             # x^2 + p x + q, irreducible, multiplicity k
            p, qc = f.coeffs[1], f.coeffs[0]
            b = N.coeffs[1] if len(N.coeffs) > 1 else Q(0)
            c = N.coeffs[0] if N.coeffs else Q(0)
            quad = _quad_str(p, qc, var)
            u = _linfac_str(-p / 2, var)                  # u = x + p/2  (=(x - (-p/2)))
            # (b/2)·∫ 2u/(u²+w²)^k : a log at k=1, a rational term for k≥2
            if b != 0:
                if k == 1:
                    log_terms.append({"coeff": _fmt(b / 2), "arg": quad})
                else:
                    rational_terms.append(f"({_fmt(-(b / 2) / (k - 1))})/({quad})^{k - 1}")
            c2 = c - b * p / 2                            # remaining ∫ c2/(u²+w²)^k via the reduction formula
            if c2 != 0:
                w_sq = qc - p * p / 4                     # = -(disc)/4 > 0 for an irreducible quadratic
                red_terms, arc = _reduce_quad(k, w_sq)
                for j, co in red_terms.items():
                    rational_terms.append(f"({_fmt(c2 * co)})*({u})/({quad})^{j}")
                if arc != 0:
                    arctan_terms.append({"coeff_over_w": _fmt(c2 * arc), "w_squared": _fmt(w_sq),
                                         "shift": _fmt(p / 2), "var": var})

    parts = [poly_int] + rational_terms
    return _assemble([p for p in parts if p and p != "0"], log_terms, arctan_terms, "C")


def _integrate_poly(poly: UPoly, var: str) -> str:
    if poly.is_zero():
        return "0"
    terms = []
    for i, c in enumerate(poly.coeffs):
        if c == 0:
            continue
        nc = c / (i + 1)
        terms.append(f"({_fmt(nc)})*{var}^{i + 1}" if i + 1 > 1 else f"({_fmt(nc)})*{var}")
    return " + ".join(terms) if terms else "0"


def _linfac_str(a: Q, var: str) -> str:
    if a == 0:
        return var
    return f"{var} - {_fmt(a)}" if a > 0 else f"{var} + {_fmt(-a)}"


def _quad_str(p: Q, q: Q, var: str) -> str:
    s = f"{var}^2"
    if p != 0:
        s += f" + {_fmt(p)}*{var}" if p > 0 else f" - {_fmt(-p)}*{var}"
    if q != 0:
        s += f" + {_fmt(q)}" if q > 0 else f" - {_fmt(-q)}"
    return s


def _partial_fractions(rem: UPoly, den_monic: UPoly, factors):
    """Solve R/Q = Σ N_{j,k}/f_j^k (deg N < deg f) by undetermined coefficients — an exact ℚ linear
    system. Returns (list of N_{j,k} as UPoly, list of (f_j, k))."""
    terms = []                                            # (f, k)
    for f, m in factors:
        for k in range(1, m + 1):
            terms.append((f, k))
    # unknown columns: for each term, deg(f) unknown coefficients (x^0..x^{deg f -1} of N)
    cofactors = [(f, k, divmod_(den_monic, _powpoly(f, k))[0]) for (f, k) in terms]   # den / f^k
    ncols = sum(f.degree() for (f, _k) in terms)
    nrows = den_monic.degree()                           # match coeffs x^0 .. x^{deg-1}
    M = [[Q(0)] * ncols for _ in range(nrows)]
    col = 0
    for (f, k, cof) in cofactors:
        for t in range(f.degree()):                      # unknown = coeff of x^t in N
            contrib = mul(UPoly([Q(0)] * t + [Q(1)], _QR), cof)   # x^t · (den/f^k)
            for r in range(min(len(contrib.coeffs), nrows)):
                M[r][col] = contrib.coeffs[r]
            col += 1
    rhs = [rem.coeffs[r] if r < len(rem.coeffs) else Q(0) for r in range(nrows)]
    sol = linear_solve(M, rhs)
    if not sol.is_solvable or sol.status != "unique":
        raise RationalIntegralHOLD("partial-fraction system is not uniquely solvable (unexpected)")
    x = sol.particular
    # slice the solution back into N_{j,k}
    out, col = [], 0
    for (f, _k) in terms:
        d = f.degree()
        out.append(UPoly([x[col + t] for t in range(d)], _QR))
        col += d
    return out, terms


def _assemble(parts, log_terms, arctan_terms, const) -> dict:
    pieces = list(parts)
    for lt in log_terms:
        pieces.append(f"({lt['coeff']})*ln|{lt['arg']}|")
    for at in arctan_terms:
        pieces.append(f"({at['coeff_over_w']}/sqrt({at['w_squared']}))*"
                      f"arctan(({at['var']} + {at['shift']})/sqrt({at['w_squared']}))")
    integral = " + ".join(pieces) if pieces else "0"
    integral = integral + " + C"
    return {"integral": integral,
            "polynomial_part": parts[0] if parts else "0",
            "log_terms": log_terms, "arctan_terms": arctan_terms, "constant": "C"}
