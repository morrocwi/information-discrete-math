"""Pattern matcher & rewrite engine (pillar P1.3, Wave 2).

A small, declarative term-rewriting core that replaces ad-hoc ``if h == "pow": ...`` chains. Phase 1
operates on the LEGACY :mod:`idm.symbolic` tuple tree (``Fraction`` / ``('var',n)`` / ``('add',[..])`` /
``('mul',[..])`` / ``('pow',b,e)`` / ``('func',name,arg)``), so it can be wired into ``simplify`` without
first migrating the six ``symbolic_*`` kinds off that tree.

Every rewrite that is not *provably* domain-safe is **gated**: a ``Guard`` returns ``SAFE`` only when the
required fact is explicitly present (a concrete constant witnessing it, or an entailment in the threaded
:class:`idm.kernel.assumptions.AssumptionSet`), and ``UNKNOWN`` otherwise — fail-closed, never guessed.
This closes the exact ``idm/symbolic.py:117`` gap where ``(bᵃ)ᶜ → b^(ac)`` fired unconditionally.

Wave-2 scope: ``Wildcard``/``Pattern``/``match``/``substitute``, ``Guard``/``domain_gate``, ``Rule``/
``RuleSet``/``Strategy``/``LoopGuardConfig``, ``rewrite``/``rewrite_safe``, and one gated rule
(``pow_pow_collapse``) in ``RS_CORE_NORMALIZE``. Constant-folding, like-term, distribute, and
antiderivative rulesets are later waves.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction as Q
from typing import Callable, Dict, Optional, Tuple

from . import assumptions as A


class GuardVerdict(Enum):
    SAFE = "safe"
    UNSAFE = "unsafe"
    UNKNOWN = "unknown"   # fail-closed default


class Strategy(Enum):
    BOTTOM_UP = "bottom_up"
    FIXPOINT = "fixpoint"


@dataclass(frozen=True)
class LoopGuardConfig:
    max_passes: int = 32
    max_steps: int = 10000


DEFAULT_LOOP = LoopGuardConfig()


class Wildcard:
    """A pattern leaf that binds any subtree to ``name``."""

    __slots__ = ("name",)

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"?{self.name}"


def match(pattern, expr, env: Optional[Dict] = None) -> Optional[Dict]:
    """Structural match of a legacy-tree pattern (with Wildcards) against ``expr``. Returns bindings."""

    if env is None:
        env = {}
    if isinstance(pattern, Wildcard):
        if pattern.name in env:
            return env if env[pattern.name] == expr else None
        env = dict(env)
        env[pattern.name] = expr
        return env
    if isinstance(pattern, (Q, int)):
        return env if (isinstance(expr, (Q, int)) and Q(expr) == Q(pattern)) else None
    if isinstance(pattern, tuple):
        if not isinstance(expr, tuple) or not expr or expr[0] != pattern[0]:
            return None
        tag = pattern[0]
        if tag == "var":
            return env if expr[1] == pattern[1] else None
        if tag in ("add", "mul"):
            # positional match only (commutative matching is a later wave); require same arity
            if len(expr[1]) != len(pattern[1]):
                return None
            for p, x in zip(pattern[1], expr[1]):
                env = match(p, x, env)
                if env is None:
                    return None
            return env
        if tag == "pow":
            env = match(pattern[1], expr[1], env)
            if env is None:
                return None
            return match(pattern[2], expr[2], env)
        if tag == "func":
            if expr[1] != pattern[1]:
                return None
            return match(pattern[2], expr[2], env)
    return None


def substitute(template, env: Dict):
    """Instantiate a template (legacy tree with Wildcards, or a callable ``env -> tree``)."""

    if callable(template) and not isinstance(template, tuple):
        return template(env)
    if isinstance(template, Wildcard):
        return env[template.name]
    if isinstance(template, tuple):
        tag = template[0]
        if tag in ("add", "mul"):
            return (tag, [substitute(t, env) for t in template[1]])
        if tag == "var":
            return template
        if tag == "pow":
            return ("pow", substitute(template[1], env), substitute(template[2], env))
        if tag == "func":
            return ("func", template[1], substitute(template[2], env))
    return template


@dataclass(frozen=True)
class Guard:
    check: Callable[[Dict, A.AssumptionSet], GuardVerdict]

    def __or__(self, other: "Guard") -> "Guard":
        def combined(env, asm):
            if self.check(env, asm) is GuardVerdict.SAFE or other.check(env, asm) is GuardVerdict.SAFE:
                return GuardVerdict.SAFE
            return GuardVerdict.UNKNOWN
        return Guard(combined)

    def __and__(self, other: "Guard") -> "Guard":
        def combined(env, asm):
            if self.check(env, asm) is GuardVerdict.SAFE and other.check(env, asm) is GuardVerdict.SAFE:
                return GuardVerdict.SAFE
            return GuardVerdict.UNKNOWN
        return Guard(combined)


_PROP_TO_PRED = {
    "integer": A.PredKind.INTEGER,
    "positive": A.PredKind.POSITIVE,
    "nonneg": A.PredKind.NONNEG,
    "negative": A.PredKind.NEGATIVE,
    "nonzero": A.PredKind.NONZERO,
    "even": A.PredKind.EVEN,
    "rational": A.PredKind.RATIONAL,
    "real": A.PredKind.REAL,
}


def _const_has_prop(value, prop: str) -> bool:
    """Does a bound CONSTANT (Fraction) provably have ``prop``?"""

    if not isinstance(value, (Q, int)):
        return False
    v = Q(value)
    return {
        "integer": v.denominator == 1,
        "positive": v > 0,
        "nonneg": v >= 0,
        "negative": v < 0,
        "nonzero": v != 0,
        "even": v.denominator == 1 and int(v) % 2 == 0,
        "rational": True,
        "real": True,
    }.get(prop, False)


def domain_gate(prop: str, *, on: str) -> Guard:
    """A guard that is SAFE iff the binding for wildcard ``on`` provably has ``prop`` — either as a
    concrete constant or via the threaded assumptions. UNKNOWN otherwise (fail-closed)."""

    pred = _PROP_TO_PRED.get(prop)

    def check(env: Dict, asm: A.AssumptionSet) -> GuardVerdict:
        value = env.get(on)
        if _const_has_prop(value, prop):
            return GuardVerdict.SAFE
        if pred is not None and isinstance(value, tuple) and value and value[0] == "var":
            if A.query(asm, value[1], A.Predicate(pred)).verdict is A.Verdict.TRUE:
                return GuardVerdict.SAFE
        return GuardVerdict.UNKNOWN

    return Guard(check)


@dataclass(frozen=True)
class Rule:
    name: str
    lhs: object                     # legacy-tree pattern with Wildcards
    rhs: object                     # legacy-tree template or callable(env)->tree
    guard: Optional[Guard] = None   # None ⇒ unconditionally safe (total op only)
    tier: str = "exact"
    priority: int = 0


@dataclass(frozen=True)
class RuleSet:
    name: str
    rules: Tuple[Rule, ...]
    default_strategy: Strategy = Strategy.FIXPOINT


@dataclass
class RewriteResult:
    value: object
    status: str = "ok"              # "ok" | "HOLD" | "PARTIAL"
    tier: str = "exact"
    fired: Tuple[str, ...] = ()
    reason: Optional[str] = None


def apply_rule(rule: Rule, expr, asm: A.AssumptionSet):
    """Try ``rule`` once at the ROOT of ``expr``. Returns the rewritten tree or None (no match / not SAFE)."""

    env = match(rule.lhs, expr)
    if env is None:
        return None
    if rule.guard is not None and rule.guard.check(env, asm) is not GuardVerdict.SAFE:
        return None
    return substitute(rule.rhs, env)


def _rewrite_pass(expr, rules, asm, fired):
    """One bottom-up pass: rewrite children, then try rules at this node."""

    if isinstance(expr, tuple) and expr and expr[0] in ("add", "mul"):
        expr = (expr[0], [_rewrite_pass(c, rules, asm, fired) for c in expr[1]])
    elif isinstance(expr, tuple) and expr and expr[0] == "pow":
        expr = ("pow", _rewrite_pass(expr[1], rules, asm, fired),
                _rewrite_pass(expr[2], rules, asm, fired))
    elif isinstance(expr, tuple) and expr and expr[0] == "func":
        expr = ("func", expr[1], _rewrite_pass(expr[2], rules, asm, fired))
    for rule in rules:
        out = apply_rule(rule, expr, asm)
        if out is not None and out != expr:
            fired.append(rule.name)
            return out
    return expr


def rewrite(expr, ruleset: RuleSet, *, strategy: Optional[Strategy] = None,
            assumptions: Optional[A.AssumptionSet] = None,
            loop_guard: LoopGuardConfig = DEFAULT_LOOP) -> RewriteResult:
    """Apply ``ruleset`` over the whole tree. FIXPOINT repeats bottom-up passes until stable/bounded."""

    strat = strategy or ruleset.default_strategy
    asm = assumptions if assumptions is not None else A.AssumptionSet.empty()
    rules = tuple(sorted(ruleset.rules, key=lambda r: -r.priority))
    fired: list = []
    current = expr
    status = "ok"
    if strat is Strategy.FIXPOINT:
        for _ in range(loop_guard.max_passes):
            nxt = _rewrite_pass(current, rules, asm, fired)
            if nxt == current:
                break
            current = nxt
        else:
            status = "PARTIAL"   # bound hit without a fixed point — disclosed, not hidden
    else:
        current = _rewrite_pass(current, rules, asm, fired)
    return RewriteResult(current, status=status, fired=tuple(fired))


# ---------------------------------------------------------------- the one gated rule
def _mul_legacy(a, b):
    """Legacy product a*b, folding two rational constants."""
    if isinstance(a, (Q, int)) and isinstance(b, (Q, int)):
        return Q(a) * Q(b)
    return ("mul", [a, b])


pow_pow_collapse = Rule(
    name="pow_pow_collapse",
    lhs=("pow", ("pow", Wildcard("b"), Wildcard("a")), Wildcard("c")),
    rhs=lambda env: ("pow", env["b"], _mul_legacy(env["a"], env["c"])),
    # (bᵃ)ᶜ → b^(ac) is valid when the outer exponent c is an integer, OR the base b is positive.
    guard=domain_gate("integer", on="c") | domain_gate("positive", on="b"),
    tier="exact",
)

RS_CORE_NORMALIZE = RuleSet("RS_CORE_NORMALIZE", (pow_pow_collapse,))


def rewrite_safe(expr, assumptions: Optional[A.AssumptionSet] = None):
    """Domain-safe core normalization: returns the rewritten legacy tree (gated rules only)."""

    return rewrite(expr, RS_CORE_NORMALIZE, assumptions=assumptions).value


def pow_pow_collapse_safe(inner_base, outer_exp, assumptions: A.AssumptionSet) -> bool:
    """Is ``(inner_base^_)^outer_exp → inner_base^(_·outer_exp)`` domain-safe under ``assumptions``?

    Convenience for :func:`idm.symbolic.simplify`'s pow-case: SAFE iff the outer exponent is an integer
    constant, or the inner base is a positive constant/assumed-positive symbol.
    """

    env = {"c": outer_exp, "b": inner_base}
    guard = domain_gate("integer", on="c") | domain_gate("positive", on="b")
    return guard.check(env, assumptions) is GuardVerdict.SAFE


__all__ = [
    "GuardVerdict", "Strategy", "LoopGuardConfig", "Wildcard", "Guard",
    "Rule", "RuleSet", "RewriteResult",
    "match", "substitute", "apply_rule", "domain_gate", "rewrite", "rewrite_safe",
    "pow_pow_collapse", "RS_CORE_NORMALIZE", "pow_pow_collapse_safe",
]
