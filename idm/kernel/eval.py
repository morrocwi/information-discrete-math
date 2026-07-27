"""Numeric bridge (pillar P1.6, Wave 3): exact-ℚ and certified-ball evaluation of the legacy tree.

Two evaluators, both readout-first:

* :func:`evaluate_exact` — walks a legacy ``idm.symbolic`` tree over ``ExactRational`` inputs and returns
  an exact ``ExactInteger``/``ExactRational`` (tier ``exact``). A ``Func`` node (``sin``/``exp``/…) or a
  non-integer power has no exact rational value, so it HOLDs rather than silently drop to a float.
* :func:`evaluate_certified` — ball (interval) arithmetic that reuses :mod:`idm.interval`'s rigorous
  ``mpmath.iv`` primitives; every ``Func`` node is routed through :mod:`idm.interval`'s finite-primitive
  namespace, and the result is a ``RealBall`` tagged ``finite_diagnostic`` (a self-disclosing enclosure,
  never "the reals"). This is the tiered, enclosure-carrying alternative to the ``idm/symbolic.py:216``
  bypass where ``evaluate`` re-``eval``'d a string against its own namespace outside the tier
  bookkeeping (that legacy function is left intact; rerouting its callers is Phase-2 work).

``ball_add``/``ball_mul``/``ball_div``/``ball_apply`` are thin wraps of the same ``mpmath.iv`` engine
``idm.interval`` already uses, so a ball op agrees with ``interval.enclose``/``verified_range`` by
construction. Heavy ``AlgebraicNumber`` field arithmetic is deferred (out of Wave-3 scope).
"""

from __future__ import annotations

from fractions import Fraction as Q
from typing import Dict, Optional

from . import numbers as NUM
from .tiers import HOLD, OK, HoldError, Tier
from .. import interval as IVL

try:
    import mpmath as mp
    _HAVE = True
except Exception:  # pragma: no cover
    _HAVE = False


# ---------------------------------------------------------------- ball helpers
def _to_iv(b: NUM.RealBall):
    return IVL._IV.mpf([b.lo, b.hi])


def _from_iv(iv, prec: int) -> NUM.RealBall:
    lo, hi = IVL._lohi(iv)
    return NUM.RealBall(lo, hi, prec)


def _prec(*balls: NUM.RealBall) -> int:
    return max((b.prec_dps for b in balls), default=30)


def _rational_bounds(p: Q, prec_dps: int):
    """A guaranteed [lo, hi] enclosure of the exact rational ``p``, rounded OUTWARD.

    Uses mpmath.iv arithmetic (directed rounding), so a non-dyadic rational like 1/3 is bracketed —
    ``lo <= p <= hi`` always holds. A scalar round-to-nearest division would round inward and could
    exclude the true value; that would silently break the enclosure certificate.
    """
    IVL._IV.dps = prec_dps
    iv = IVL._IV.mpf(int(p.numerator)) / IVL._IV.mpf(int(p.denominator))
    return mp.mpf(iv.a), mp.mpf(iv.b)


def real_ball(value, prec_dps: int = 30) -> NUM.RealBall:
    """A point (or [lo,hi]) ball from an exact rational / int / (lo,hi) pair — a rigorous enclosure."""
    IVL._IV.dps = prec_dps
    mp.mp.dps = prec_dps
    if isinstance(value, tuple):
        lo, _ = _rational_bounds(Q(value[0]), prec_dps)   # lower endpoint rounded DOWN
        _, hi = _rational_bounds(Q(value[1]), prec_dps)   # upper endpoint rounded UP
    else:
        lo, hi = _rational_bounds(Q(value), prec_dps)
    return _from_iv(IVL._IV.mpf([lo, hi]), prec_dps)


def ball_add(a: NUM.RealBall, b: NUM.RealBall) -> NUM.RealBall:
    prec = _prec(a, b)
    IVL._IV.dps = prec
    return _from_iv(_to_iv(a) + _to_iv(b), prec)


def ball_mul(a: NUM.RealBall, b: NUM.RealBall) -> NUM.RealBall:
    prec = _prec(a, b)
    IVL._IV.dps = prec
    return _from_iv(_to_iv(a) * _to_iv(b), prec)


def ball_div(a: NUM.RealBall, b: NUM.RealBall) -> NUM.Certificate:
    if b.lo <= 0 <= b.hi:
        return NUM.Certificate(None, HOLD, Tier.FINITE_DIAGNOSTIC,
                               reason="division by an enclosure containing 0")
    prec = _prec(a, b)
    IVL._IV.dps = prec
    return NUM.Certificate(_from_iv(_to_iv(a) / _to_iv(b), prec), OK, Tier.FINITE_DIAGNOSTIC)


def ball_apply(fn_name: str, arg: NUM.RealBall) -> NUM.Certificate:
    fn = IVL._NS.get(fn_name)
    if fn is None:
        return NUM.Certificate(None, HOLD, Tier.FINITE_DIAGNOSTIC,
                               reason=f"no finite interval primitive for {fn_name!r}")
    prec = _prec(arg)
    IVL._IV.dps = prec
    try:
        return NUM.Certificate(_from_iv(fn(_to_iv(arg)), prec), OK, Tier.FINITE_DIAGNOSTIC)
    except Exception as exc:  # pragma: no cover
        return NUM.Certificate(None, HOLD, Tier.FINITE_DIAGNOSTIC,
                               reason=f"{fn_name} not defined on the enclosure: {exc}")


# ---------------------------------------------------------------- exact evaluation
def _eval_exact(node, env: Dict[str, object]) -> Q:
    if isinstance(node, (Q, int)):
        return Q(node)
    if not isinstance(node, tuple):
        raise HoldError(f"unexpected node {node!r}")
    tag = node[0]
    if tag == "var":
        if node[1] not in env:
            raise HoldError(f"unbound variable {node[1]!r}")
        return NUM.to_fraction(env[node[1]]) if hasattr(env[node[1]], "__dataclass_fields__") else Q(env[node[1]])
    if tag == "add":
        total = Q(0)
        for t in node[1]:
            total += _eval_exact(t, env)
        return total
    if tag == "mul":
        prod = Q(1)
        for f in node[1]:
            prod *= _eval_exact(f, env)
        return prod
    if tag == "pow":
        base = _eval_exact(node[1], env)
        exp = _eval_exact(node[2], env)
        if exp.denominator != 1:
            raise HoldError("non-integer power has no exact rational value; use evaluate_certified")
        if base == 0 and exp < 0:
            raise HoldError("0 to a negative power is undefined")
        return base ** int(exp)
    if tag == "func":
        raise HoldError(f"{node[1]} has no exact rational value; use evaluate_certified")
    raise HoldError(f"cannot exactly evaluate node tag {tag!r}")


def evaluate_exact(expr, env: Optional[Dict[str, object]] = None) -> NUM.Certificate:
    """Exact ℚ evaluation. Returns an ExactInteger/ExactRational Certificate, or HOLD (never a float)."""
    try:
        value = _eval_exact(expr, env or {})
    except HoldError as exc:
        return NUM.Certificate(None, HOLD, Tier.EXACT, reason=exc.reason)
    return NUM.Certificate(NUM.from_python(value), OK, Tier.EXACT)


# ---------------------------------------------------------------- certified evaluation
def _eval_ball(node, env: Dict[str, NUM.RealBall], prec: int) -> NUM.RealBall:
    if isinstance(node, (Q, int)):
        return real_ball(Q(node), prec)
    tag = node[0]
    if tag == "var":
        if node[1] not in env:
            raise HoldError(f"unbound variable {node[1]!r}")
        return env[node[1]]
    if tag == "add":
        acc = _eval_ball(node[1][0], env, prec)
        for t in node[1][1:]:
            acc = ball_add(acc, _eval_ball(t, env, prec))
        return acc
    if tag == "mul":
        acc = _eval_ball(node[1][0], env, prec)
        for f in node[1][1:]:
            acc = ball_mul(acc, _eval_ball(f, env, prec))
        return acc
    if tag == "pow":
        base = _eval_ball(node[1], env, prec)
        # exponent must be a rational constant for a certified elementary power
        try:
            exp = _eval_exact(node[2], {})
        except HoldError:
            raise HoldError("certified power needs a rational-constant exponent")
        IVL._IV.dps = prec
        if exp.denominator == 1:
            n = int(exp)
            if n == 0:
                return real_ball(Q(1), prec)
            acc = base if n > 0 else ball_div(real_ball(Q(1), prec), base).value
            if acc is None:
                raise HoldError("0 in base enclosure for a negative power")
            for _ in range(abs(n) - 1):
                acc = ball_mul(acc, base if n > 0 else ball_div(real_ball(Q(1), prec), base).value)
            return acc
        # fractional power: b^e = exp(e * log(b)) — requires base > 0
        if base.lo <= 0:
            raise HoldError("fractional power of an enclosure that is not provably positive")
        log_b = ball_apply("log", base).value
        scaled = ball_mul(real_ball(exp, prec), log_b)
        result = ball_apply("exp", scaled).value
        if result is None:
            raise HoldError("fractional power failed on the enclosure")
        return result
    if tag == "func":
        arg = _eval_ball(node[2], env, prec)
        cert = ball_apply(node[1], arg)
        if cert.value is None:
            raise HoldError(cert.reason or f"{node[1]} failed on the enclosure")
        return cert.value
    raise HoldError(f"cannot evaluate node tag {tag!r}")


def evaluate_certified(expr, env: Optional[Dict[str, NUM.RealBall]] = None,
                       prec_dps: int = 30) -> NUM.Certificate:
    """Ball-arithmetic evaluation. Every Func routes through idm.interval's finite primitives; the
    result is a RealBall tagged finite_diagnostic — a self-disclosing enclosure, never exact."""
    IVL._IV.dps = prec_dps
    try:
        ball = _eval_ball(expr, env or {}, prec_dps)
    except HoldError as exc:
        return NUM.Certificate(None, HOLD, Tier.FINITE_DIAGNOSTIC, reason=exc.reason)
    return NUM.Certificate(ball, OK, Tier.FINITE_DIAGNOSTIC)


def evaluate(expr, env: Optional[Dict] = None, *, prec_dps: int = 30) -> NUM.Certificate:
    """Try exact first; fall back to a certified ball enclosure when the tree isn't exactly rational."""
    exact = evaluate_exact(expr, env)
    if exact.status == OK:
        return exact
    ball_env = {k: (v if isinstance(v, NUM.RealBall) else real_ball(NUM.to_fraction(v)
                    if hasattr(v, "__dataclass_fields__") else Q(v), prec_dps))
                for k, v in (env or {}).items()}
    return evaluate_certified(expr, ball_env, prec_dps)


__all__ = [
    "real_ball", "ball_add", "ball_mul", "ball_div", "ball_apply",
    "evaluate_exact", "evaluate_certified", "evaluate",
]
