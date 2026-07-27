"""Assumption & domain engine (pillar P1.2, Wave 1).

A finite, closed-vocabulary predicate closure + exact-ℚ interval arithmetic — no SAT/SMT, no
theorem prover. Every module that reasons about a symbol (simplify / solve / integrate / limit /
series / rewrite) consults the SAME ``AssumptionSet`` through :func:`query` / :func:`entails`, and a
domain-sensitive identity asks :func:`domain_of_expr` what a subexpression requires.

Readout-first: every interval endpoint is a finite ``Fraction`` or the explicit ``None`` = "no bound
asserted" sentinel — never a literal ``+∞`` and never a continuum ℝ value. The closure rule table is
monotone (rules only ADD predicates), so an incomplete table under-infers → the query defaults to
``UNKNOWN`` → the caller HOLDs. Failure is always toward HOLD, never toward a wrong answer.

Wave-1 scope: ``PredKind``/``Interval``/``Predicate``/``SymbolDomain``/``AssumptionSet``/``closure``/
``query``/``entails``/``domain_of_expr``. The ``safe_rewrite``/``resolve``/``ConditionedValue`` seam
(which the rewrite engine calls) lands with P1.3.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction as Q
from typing import Optional, Tuple

MAX_PREDS_PER_SYMBOL = 24


class PredKind(Enum):
    EVEN = "even"
    ODD = "odd"
    INTEGER = "integer"
    RATIONAL = "rational"
    REAL = "real"
    PRIME = "prime"
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NONNEG = "nonneg"
    NONPOS = "nonpos"
    NONZERO = "nonzero"
    IN_INTERVAL = "in_interval"


class Verdict(Enum):
    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"


class DomainContradiction(Exception):
    """Raised by :func:`closure` when a symbol's asserted+derived predicates cannot coexist."""


@dataclass(frozen=True, slots=True)
class Interval:
    """Exact-ℚ interval. ``lo=None`` / ``hi=None`` means 'no bound asserted' — NEVER a numeric ±∞."""

    lo: Optional[Q] = None
    hi: Optional[Q] = None
    lo_closed: bool = True
    hi_closed: bool = True

    def is_empty(self) -> bool:
        if self.lo is None or self.hi is None:
            return False
        if self.lo > self.hi:
            return True
        return self.lo == self.hi and not (self.lo_closed and self.hi_closed)

    def intersect(self, other: "Interval") -> Optional["Interval"]:
        # lower bound = the tighter (larger) of the two lows
        if self.lo is None:
            lo, lc = other.lo, other.lo_closed
        elif other.lo is None:
            lo, lc = self.lo, self.lo_closed
        elif self.lo > other.lo:
            lo, lc = self.lo, self.lo_closed
        elif other.lo > self.lo:
            lo, lc = other.lo, other.lo_closed
        else:
            lo, lc = self.lo, (self.lo_closed and other.lo_closed)
        if self.hi is None:
            hi, hc = other.hi, other.hi_closed
        elif other.hi is None:
            hi, hc = self.hi, self.hi_closed
        elif self.hi < other.hi:
            hi, hc = self.hi, self.hi_closed
        elif other.hi < self.hi:
            hi, hc = other.hi, other.hi_closed
        else:
            hi, hc = self.hi, (self.hi_closed and other.hi_closed)
        result = Interval(lo, hi, lc if lo is not None else True, hc if hi is not None else True)
        return None if result.is_empty() else result


# sign predicate -> its exact-ℚ interval
_SIGN_INTERVAL = {
    PredKind.POSITIVE: Interval(Q(0), None, lo_closed=False),
    PredKind.NEGATIVE: Interval(None, Q(0), hi_closed=False),
    PredKind.NONNEG: Interval(Q(0), None, lo_closed=True),
    PredKind.NONPOS: Interval(None, Q(0), hi_closed=True),
}


@dataclass(frozen=True, slots=True)
class Predicate:
    kind: PredKind
    params: Tuple = ()          # e.g. an Interval for IN_INTERVAL
    asserted: bool = True       # True = caller asserted; False = derived by closure()

    def as_derived(self) -> "Predicate":
        return Predicate(self.kind, self.params, asserted=False)


@dataclass(frozen=True, slots=True)
class SymbolDomain:
    preds: frozenset = field(default_factory=frozenset)

    def kinds(self) -> frozenset:
        return frozenset(p.kind for p in self.preds)

    def has(self, kind: PredKind) -> bool:
        return any(p.kind is kind for p in self.preds)

    def add(self, p: Predicate) -> "SymbolDomain":
        new = self.preds | {p}
        if len(new) > MAX_PREDS_PER_SYMBOL:
            raise DomainContradiction(f"predicate cap {MAX_PREDS_PER_SYMBOL} exceeded")
        return SymbolDomain(new)

    def interval(self) -> Interval:
        acc = Interval()
        for p in self.preds:
            iv = None
            if p.kind is PredKind.IN_INTERVAL and p.params:
                iv = p.params[0]
            elif p.kind in _SIGN_INTERVAL:
                iv = _SIGN_INTERVAL[p.kind]
            if iv is not None:
                merged = acc.intersect(iv)
                if merged is None:
                    return Interval(Q(1), Q(0))  # canonical empty
                acc = merged
        return acc

    def is_contradictory(self) -> bool:
        k = self.kinds()
        for a, b in ((PredKind.POSITIVE, PredKind.NEGATIVE),
                     (PredKind.POSITIVE, PredKind.NONPOS),
                     (PredKind.NEGATIVE, PredKind.NONNEG),
                     (PredKind.EVEN, PredKind.ODD)):
            if a in k and b in k:
                return True
        return self.interval().is_empty()


@dataclass(frozen=True, slots=True)
class AssumptionSet:
    domains: Tuple[Tuple[str, SymbolDomain], ...] = ()

    @staticmethod
    def empty() -> "AssumptionSet":
        return AssumptionSet(())

    def get(self, symbol: str) -> SymbolDomain:
        for name, dom in self.domains:
            if name == symbol:
                return dom
        return SymbolDomain()

    def with_domain(self, symbol: str, d: SymbolDomain) -> "AssumptionSet":
        others = tuple((n, dm) for n, dm in self.domains if n != symbol)
        return AssumptionSet(tuple(sorted(others + ((symbol, d),))))

    def merge(self, other: "AssumptionSet") -> "AssumptionSet":
        names = {n for n, _ in self.domains} | {n for n, _ in other.domains}
        out = self
        for name in names:
            merged = SymbolDomain(self.get(name).preds | other.get(name).preds)
            out = out.with_domain(name, merged)
        return closure(out)


class DomainVerdict:
    __slots__ = ("verdict", "evidence")

    def __init__(self, verdict: Verdict, evidence: str = ""):
        self.verdict = verdict
        self.evidence = evidence


# ---- closure rule table (monotone: premises ⊆ kinds ⇒ ADD conclusion) ----
_RULES: Tuple[Tuple[frozenset, PredKind], ...] = (
    (frozenset({PredKind.EVEN}), PredKind.INTEGER),
    (frozenset({PredKind.ODD}), PredKind.INTEGER),
    (frozenset({PredKind.INTEGER}), PredKind.RATIONAL),
    (frozenset({PredKind.RATIONAL}), PredKind.REAL),
    (frozenset({PredKind.PRIME}), PredKind.INTEGER),
    (frozenset({PredKind.PRIME}), PredKind.POSITIVE),
    (frozenset({PredKind.POSITIVE}), PredKind.NONNEG),
    (frozenset({PredKind.POSITIVE}), PredKind.NONZERO),
    (frozenset({PredKind.NEGATIVE}), PredKind.NONPOS),
    (frozenset({PredKind.NEGATIVE}), PredKind.NONZERO),
)


def closure(a: AssumptionSet) -> AssumptionSet:
    """Forward-chaining fixed point over the fixed rule table. Idempotent. Raises on contradiction."""

    out = a
    for symbol, _ in a.domains:
        dom = out.get(symbol)
        changed = True
        while changed:
            changed = False
            kinds = dom.kinds()
            for premise, concl in _RULES:
                if premise <= kinds and concl not in kinds:
                    dom = dom.add(Predicate(concl, asserted=False))
                    kinds = dom.kinds()
                    changed = True
        if dom.is_contradictory():
            raise DomainContradiction(f"contradictory domain for {symbol!r}: {sorted(k.value for k in dom.kinds())}")
        out = out.with_domain(symbol, dom)
    return out


def query(a: AssumptionSet, symbol: str, pred: Predicate) -> DomainVerdict:
    """Trichotomy: TRUE if entailed, FALSE if contradicted, else UNKNOWN. Never guesses."""

    a = closure(a)
    dom = a.get(symbol)
    kinds = dom.kinds()
    if pred.kind in kinds:
        return DomainVerdict(Verdict.TRUE, "asserted or derived")
    # interval entailment for sign predicates
    if pred.kind in _SIGN_INTERVAL:
        want = _SIGN_INTERVAL[pred.kind]
        have = dom.interval()
        if have.intersect(want) == have and not have.is_empty() and (have.lo is not None or have.hi is not None):
            # `have` is already inside `want`
            if _contains(want, have):
                return DomainVerdict(Verdict.TRUE, "interval entails sign")
    # contradiction ⇒ FALSE
    contra = {
        PredKind.POSITIVE: {PredKind.NEGATIVE, PredKind.NONPOS},
        PredKind.NEGATIVE: {PredKind.POSITIVE, PredKind.NONNEG},
        PredKind.NONNEG: {PredKind.NEGATIVE},
        PredKind.NONPOS: {PredKind.POSITIVE},
        PredKind.EVEN: {PredKind.ODD},
        PredKind.ODD: {PredKind.EVEN},
    }.get(pred.kind, set())
    if contra & kinds:
        return DomainVerdict(Verdict.FALSE, "contradicted")
    return DomainVerdict(Verdict.UNKNOWN, "not entailed")


def _contains(outer: Interval, inner: Interval) -> bool:
    lo_ok = outer.lo is None or (inner.lo is not None and (inner.lo > outer.lo or (inner.lo == outer.lo and (outer.lo_closed or not inner.lo_closed))))
    hi_ok = outer.hi is None or (inner.hi is not None and (inner.hi < outer.hi or (inner.hi == outer.hi and (outer.hi_closed or not inner.hi_closed))))
    return lo_ok and hi_ok


def entails(a: AssumptionSet, condition: SymbolDomain, symbol: str) -> bool:
    """True iff every predicate in ``condition`` is entailed (Verdict.TRUE) for ``symbol``."""

    return all(query(a, symbol, p).verdict is Verdict.TRUE for p in condition.preds)


# ---- construction helpers ----
_NAME_TO_KIND = {k.value: k for k in PredKind}


def predicate(kind, *params) -> Predicate:
    if isinstance(kind, str):
        kind = _NAME_TO_KIND[kind]
    return Predicate(kind, tuple(params))


def parse_assumptions(spec) -> AssumptionSet:
    """``{"x": ["real", "positive"]}`` or ``["x:real", "n:integer"]`` -> a closed AssumptionSet."""

    a = AssumptionSet.empty()
    if isinstance(spec, dict):
        items = spec.items()
    else:
        items = []
        for entry in spec:
            sym, _, preds = entry.partition(":")
            items.append((sym.strip(), [p.strip() for p in preds.split(",") if p.strip()]))
    for sym, preds in items:
        dom = a.get(sym)
        for pname in preds:
            dom = dom.add(predicate(pname))
        a = a.with_domain(sym, dom)
    return closure(a)


def _rational_const(node) -> Optional[Q]:
    """Exact ℚ value of a constant legacy subtree, or None if it contains a variable/function/root."""

    if isinstance(node, Q):
        return node
    if isinstance(node, int):
        return Q(node)
    if not isinstance(node, tuple) or not node:
        return None
    tag = node[0]
    if tag == "add":
        total = Q(0)
        for t in node[1]:
            v = _rational_const(t)
            if v is None:
                return None
            total += v
        return total
    if tag == "mul":
        prod = Q(1)
        for t in node[1]:
            v = _rational_const(t)
            if v is None:
                return None
            prod *= v
        return prod
    if tag == "pow":
        b = _rational_const(node[1])
        e = _rational_const(node[2])
        if b is None or e is None or e.denominator != 1:
            return None
        try:
            return b ** int(e)
        except ZeroDivisionError:
            return None
    return None


# ---- domain requirements implied by an expression (legacy idm.symbolic tuple tree) ----
def domain_of_expr(expr, a: Optional[AssumptionSet] = None) -> AssumptionSet:
    """Bottom-up walk emitting the domain a subexpression REQUIRES to be a real readout.

    Phase-1 named cases only: ``log``/``ln`` ⇒ POSITIVE(arg); ``sqrt`` ⇒ NONNEG(arg); ``pow`` with a
    negative exponent ⇒ NONZERO(base); ``pow`` with a non-integer exponent ⇒ NONNEG(base). Emitted on
    the symbol when the arg/base is a bare symbol (compound-arg requirements are deferred).
    """

    out = AssumptionSet.empty() if a is None else a
    reqs: list[tuple[str, PredKind]] = []

    def sym_name(node):
        return node[1] if isinstance(node, tuple) and node and node[0] == "var" else None

    def walk(node):
        if not isinstance(node, tuple) or not node:
            return
        tag = node[0]
        if tag == "func" and node[1] in ("log", "ln"):
            s = sym_name(node[2])
            if s:
                reqs.append((s, PredKind.POSITIVE))
        elif tag == "func" and node[1] == "sqrt":
            s = sym_name(node[2])
            if s:
                reqs.append((s, PredKind.NONNEG))
        elif tag == "pow":
            base, exp = node[1], node[2]
            s = sym_name(base)
            exp_val = _rational_const(exp)
            if s and exp_val is not None:
                if exp_val < 0:
                    reqs.append((s, PredKind.NONZERO))
                elif exp_val.denominator != 1:
                    reqs.append((s, PredKind.NONNEG))
        for child in node[1:]:
            if isinstance(child, tuple):
                walk(child)
            elif isinstance(child, list):
                for c in child:
                    walk(c)

    walk(expr)
    for s, kind in reqs:
        out = out.with_domain(s, out.get(s).add(Predicate(kind)))
    return closure(out)


__all__ = [
    "PredKind", "Verdict", "Interval", "Predicate", "SymbolDomain", "AssumptionSet",
    "DomainVerdict", "DomainContradiction", "MAX_PREDS_PER_SYMBOL",
    "closure", "query", "entails", "predicate", "parse_assumptions", "domain_of_expr",
]
