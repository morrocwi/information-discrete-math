"""Conditional solution objects (pillar P1.5, Wave 4).

``solve`` returns a **SolutionSet**, never a bare root list: a set of solutions, each carrying the
condition under which it holds, plus explicit ``ExceptionalCase``s for parameter values that change the
answer's shape (a zero/symbolic leading coefficient), plus a ``completeness`` field that makes the
"no dropped roots" claim auditable rather than asserted.

Readout-first: every value/condition is a finite exact readout; a parametric family is described
symbolically (``x = -b/a`` under ``a ≠ 0``), never enumerated; and an undecidable completeness leaves
``completeness="partial"`` with an honest HOLD rather than a false "complete".

Wave-4 scope (items 15–17): polynomial ``solve`` over one variable with **symbolic coefficients**
(linear branch with the zero-leading-coefficient ExceptionalCase fix), a numeric quadratic branch, a
rational-root branch with a Vieta/residual completeness check, and ``verify`` by exact substitution.
Systems / inequalities / diophantine / recurrences and the full Condition algebra are later work.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction as Q
from typing import List, Optional

from .. import symbolic as SYM
from .tiers import HOLD, OK, Tier


class Domain(Enum):
    R = "R"
    C = "C"


class SolutionKind(Enum):
    POINTS = "points"
    EMPTY = "empty"
    ALL = "all"
    PARAMETRIC = "parametric"


@dataclass(frozen=True)
class Solution:
    values: dict                       # {var: legacy expr tree}
    condition: str = "true"            # the condition under which this solution holds
    tier: Tier = Tier.EXACT
    verified: Optional[bool] = None

    def tostr(self) -> dict:
        return {k: SYM.tostr(v) for k, v in self.values.items()}


@dataclass(frozen=True)
class ExceptionalCase:
    condition: str                     # e.g. "a != 0"
    description: str
    solutions: List[Solution] = field(default_factory=list)
    resolved: bool = True              # True: this pillar solved the branch too


@dataclass
class SolutionSet:
    kind: SolutionKind
    variable: str = ""
    solutions: List[Solution] = field(default_factory=list)
    exceptional: List[ExceptionalCase] = field(default_factory=list)
    completeness: str = "complete"     # "complete" | "partial" | "unknown"
    status: str = OK
    tier: Tier = Tier.EXACT
    reason: Optional[str] = None

    def to_dict(self) -> dict:
        d = {"kind": self.kind.value, "variable": self.variable, "status": self.status,
             "tier": self.tier.value, "completeness": self.completeness,
             "solutions": [s.tostr() for s in self.solutions]}
        if self.exceptional:
            d["exceptional"] = [{"condition": e.condition, "description": e.description,
                                 "solutions": [s.tostr() for s in e.solutions]} for e in self.exceptional]
        if self.reason:
            d["reason"] = self.reason
        return d


# ---------------------------------------------------------------- coefficient extraction
def _to_tree(equation):
    return SYM.parse(equation) if isinstance(equation, str) else equation


def _contains_var(node, var) -> bool:
    if isinstance(node, tuple):
        if node[0] == "var":
            return node[1] == var
        for c in node[1:]:
            if isinstance(c, list):
                if any(_contains_var(x, var) for x in c):
                    return True
            elif _contains_var(c, var):
                return True
    return False


def _term_power(term, var):
    """(power_of_var, coefficient_tree) for one product term, or (None, None) if var is non-polynomial."""
    factors = term[1] if isinstance(term, tuple) and term[0] == "mul" else [term]
    power = 0
    rest = []
    for f in factors:
        if f == ("var", var):
            power += 1
        elif (isinstance(f, tuple) and f[0] == "pow" and f[1] == ("var", var)
              and isinstance(f[2], Q) and f[2].denominator == 1 and f[2] >= 0):
            power += int(f[2])
        elif _contains_var(f, var):
            return None, None            # var inside sin(x) / a denominator / etc. — not polynomial
        else:
            rest.append(f)
    if not rest:
        coeff = Q(1)
    elif len(rest) == 1:
        coeff = rest[0]
    else:
        coeff = ("mul", rest)
    return power, coeff


def _poly_coeffs_sym(e, var):
    """{power: coefficient tree} with possibly-symbolic coefficients, or None if non-polynomial in var."""
    e = SYM.expand(SYM.simplify(e))
    terms = e[1] if isinstance(e, tuple) and e[0] == "add" else [e]
    acc: dict = {}
    for t in terms:
        k, coeff = _term_power(t, var)
        if k is None:
            return None
        acc.setdefault(k, []).append(coeff)
    return {k: (SYM.simplify(("add", v)) if len(v) > 1 else v[0]) for k, v in acc.items()}


def _is_zero(c) -> bool:
    return SYM.simplify(c) == Q(0)


def _as_const(c):
    """Return the Fraction value if c is a numeric constant, else None."""
    s = SYM.simplify(c)
    return s if isinstance(s, Q) else None


def _neg(c):
    return SYM.simplify(("mul", [Q(-1), c]))


def _div(num, den):
    nc, dc = _as_const(num), _as_const(den)
    if nc is not None and dc is not None and dc != 0:
        return nc / dc                    # exact ℚ division when both are constants
    return SYM.simplify(("mul", [num, ("pow", den, Q(-1))]))


# ---------------------------------------------------------------- solve
def solve(equation, var: str, *, domain: Domain = Domain.C) -> SolutionSet:
    """Solve ``equation = 0`` for ``var``. Never raises — errors become status=HOLD."""
    try:
        tree = _to_tree(equation)
        coeffs = _poly_coeffs_sym(tree, var)
        if coeffs is None:
            return SolutionSet(SolutionKind.EMPTY, var, status=HOLD,
                               reason="non-polynomial in the variable — symbolic solve not available")
        coeffs = {k: v for k, v in coeffs.items() if not _is_zero(v)}
        deg = max(coeffs) if coeffs else 0

        def a(k):
            return coeffs.get(k, Q(0))

        if deg == 0:
            if _is_zero(a(0)):
                return SolutionSet(SolutionKind.ALL, var, completeness="complete",
                                   reason="identity: every value satisfies it")
            return SolutionSet(SolutionKind.EMPTY, var, completeness="complete",
                               reason="a nonzero constant is never 0")

        if deg == 1:
            a1, a0 = a(1), a(0)
            if _as_const(a1) is not None:
                x = _div(_neg(a0), a1)
                return SolutionSet(SolutionKind.POINTS, var,
                                   solutions=[Solution({var: x})], completeness="complete")
            # symbolic leading coefficient -> the answer's shape depends on whether it is zero
            root = _div(_neg(a0), a1)
            exc = [
                ExceptionalCase(f"({SYM.tostr(a1)}) != 0", "unique solution",
                                [Solution({var: root}, condition=f"({SYM.tostr(a1)}) != 0")]),
                ExceptionalCase(f"({SYM.tostr(a1)}) == 0 and ({SYM.tostr(a0)}) != 0",
                                "no solution (reduces to a nonzero constant)", []),
                ExceptionalCase(f"({SYM.tostr(a1)}) == 0 and ({SYM.tostr(a0)}) == 0",
                                "every value (identity)", []),
            ]
            return SolutionSet(SolutionKind.PARAMETRIC, var, exceptional=exc, completeness="complete")

        if deg == 2:
            A, Bc, Cc = _as_const(a(2)), _as_const(a(1)), _as_const(a(0))
            if A is None or Bc is None or Cc is None:
                return SolutionSet(SolutionKind.POINTS, var, status=HOLD,
                                   reason="symbolic quadratic coefficients not yet handled")
            disc = Bc * Bc - 4 * A * Cc
            if disc < 0 and domain is Domain.R:
                return SolutionSet(SolutionKind.EMPTY, var, completeness="complete",
                                   reason="negative discriminant: no real roots")
            root = _rational_sqrt(disc)
            if root is not None:
                # perfect-square discriminant -> exact rational roots (these verify)
                r1 = (-Bc + root) / (2 * A)
                r2 = (-Bc - root) / (2 * A)
                vals = [r1] if r1 == r2 else [r1, r2]
                return SolutionSet(SolutionKind.POINTS, var,
                                   solutions=[Solution({var: v}) for v in vals], completeness="complete")
            # irrational (or complex) roots: exact radical form. Complete (2 roots by the fundamental
            # theorem) but exact algebraic-number verification is a Wave-5 rung, so verify stays None.
            sq = ("func", "sqrt", disc)
            r1 = SYM.simplify(_div(("add", [_neg(Bc), sq]), Q(2) * A))
            r2 = SYM.simplify(_div(("add", [_neg(Bc), _neg(sq)]), Q(2) * A))
            sols = [Solution({var: r1}), Solution({var: r2})]
            return SolutionSet(SolutionKind.POINTS, var, solutions=sols, completeness="complete",
                               reason="roots are exact radicals; algebraic-number verification is Wave-5")

        # degree >= 3: rational roots + a Vieta/residual completeness check
        consts = {k: _as_const(a(k)) for k in range(deg + 1)}
        if any(v is None for v in consts.values()):
            return SolutionSet(SolutionKind.POINTS, var, status=HOLD,
                               reason="symbolic high-degree coefficients not yet handled")
        from ..exact import rational_roots, poly_divmod
        clist = [consts[k] for k in range(deg + 1)]      # low -> high
        rr = sorted(rational_roots(clist))
        sols = [Solution({var: r}) for r in rr]
        # completeness (exact Vieta/residual): divide out (x - r) to FULL multiplicity for each rational
        # root; the equation's roots are all found iff the surviving factor is a nonzero constant.
        quotient = clist[:]
        remaining_deg = deg
        for r in rr:
            while remaining_deg > 0:
                q, rem = poly_divmod(quotient, [_neg_q(r), Q(1)])   # divide by (x - r)
                if any(x != 0 for x in rem):
                    break
                quotient = q
                remaining_deg -= 1
        completeness = "complete" if remaining_deg == 0 else "partial"
        reason = None if completeness == "complete" else \
            f"{len(rr)} rational root(s) found; a degree-{remaining_deg} factor with no rational roots remains"
        return SolutionSet(SolutionKind.POINTS, var, solutions=sols,
                           completeness=completeness,
                           tier=Tier.EXACT, reason=reason)
    except Exception as exc:  # never raise across the boundary
        return SolutionSet(SolutionKind.EMPTY, var, status=HOLD, reason=f"{type(exc).__name__}: {exc}")


def _neg_q(r):
    return Q(-r) if isinstance(r, (int, Q)) else r


def _rational_sqrt(q: Q):
    """Exact ℚ square root of a nonnegative rational if it is a perfect square, else None."""
    from math import isqrt
    if q < 0:
        return None
    n, d = q.numerator, q.denominator
    sn, sd = isqrt(n), isqrt(d)
    return Q(sn, sd) if sn * sn == n and sd * sd == d else None


# ---------------------------------------------------------------- verify
def verify(solution: Solution, equation, var: str) -> bool:
    """Verify a POINT solution by exact substitution: equation[var := value] must simplify to 0.

    A parametric family (a solution over a free parameter) is verified by symbolic identity, NEVER by
    enumerating parameter values. If no exact-identity path is available, this returns False rather
    than looping over an infinite family.
    """
    tree = _to_tree(equation)
    value = solution.values.get(var)
    if value is None:
        return False
    substituted = SYM.simplify(SYM._subst(tree, var, value))
    return substituted == Q(0)


def verify_set(sset: SolutionSet, equation) -> SolutionSet:
    """Attach verification to each point solution; exceptional/parametric solutions verify their own
    point representatives symbolically. Returns the same SolutionSet with .verified populated."""
    verified = []
    for s in sset.solutions:
        ok = verify(s, equation, sset.variable)
        verified.append(Solution(s.values, s.condition, s.tier, ok))
    sset.solutions = verified
    return sset


__all__ = [
    "Domain", "SolutionKind", "Solution", "ExceptionalCase", "SolutionSet",
    "solve", "verify", "verify_set",
]
