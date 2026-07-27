#!/usr/bin/env python3
"""IDM Symbolic Kernel v2 — Wave 1 (pillar P1.2): assumption & domain engine.

Run: PYTHONPATH=. python3 -m pytest tests/test_kernel_p2.py -q
"""

from __future__ import annotations

from fractions import Fraction as Q

import pytest

from idm import kernel as K
from idm import symbolic as SYM
from idm.kernel.assumptions import _RULES


def _aset(symbol, *pred_kinds):
    dom = K.SymbolDomain()
    for k in pred_kinds:
        dom = dom.add(K.Predicate(k))
    return K.AssumptionSet.empty().with_domain(symbol, dom)


# ------------------------------------------------------------------ closure (item 6)
def test_closure_is_idempotent():
    a = _aset("x", K.PredKind.EVEN)
    once = K.closure(a)
    twice = K.closure(once)
    assert once == twice


def test_closure_derives_the_number_tower():
    a = K.closure(_aset("n", K.PredKind.EVEN))
    kinds = a.get("n").kinds()
    for expected in (K.PredKind.EVEN, K.PredKind.INTEGER, K.PredKind.RATIONAL, K.PredKind.REAL):
        assert expected in kinds


def test_prime_derives_positive_integer_nonzero():
    a = K.closure(_aset("p", K.PredKind.PRIME))
    kinds = a.get("p").kinds()
    for expected in (K.PredKind.INTEGER, K.PredKind.POSITIVE, K.PredKind.NONNEG, K.PredKind.NONZERO):
        assert expected in kinds


def test_contradiction_raises():
    a = _aset("x", K.PredKind.POSITIVE, K.PredKind.NEGATIVE)
    with pytest.raises(K.DomainContradiction):
        K.closure(a)


def test_no_numeric_infinity_in_intervals():
    # POSITIVE means (0, no-upper-bound) — the upper bound is None, never a numeric +inf
    iv = K.closure(_aset("x", K.PredKind.POSITIVE)).get("x").interval()
    assert iv.lo == Q(0) and iv.lo_closed is False
    assert iv.hi is None


# ------------------------------------------------------------------ query/entails per rule (item 7)
@pytest.mark.parametrize("premise,concl", [(sorted(p, key=lambda k: k.value)[0], c) for p, c in _RULES])
def test_each_rule_entails_forward_and_is_unknown_without_premise(premise, concl):
    # with the premise asserted, the conclusion is entailed (TRUE)
    with_premise = _aset("x", premise)
    assert K.query(with_premise, "x", K.Predicate(concl)).verdict is K.Verdict.TRUE
    # with NOTHING asserted, the same conclusion is UNKNOWN — never guessed TRUE
    empty = K.AssumptionSet.empty()
    assert K.query(empty, "x", K.Predicate(concl)).verdict is K.Verdict.UNKNOWN


def test_query_false_on_contradiction():
    a = _aset("x", K.PredKind.NEGATIVE)
    assert K.query(a, "x", K.Predicate(K.PredKind.POSITIVE)).verdict is K.Verdict.FALSE


def test_entails_all_or_nothing():
    a = _aset("x", K.PredKind.PRIME)
    need = K.SymbolDomain().add(K.Predicate(K.PredKind.POSITIVE)).add(K.Predicate(K.PredKind.INTEGER))
    assert K.entails(a, need, "x") is True
    need2 = need.add(K.Predicate(K.PredKind.EVEN))
    assert K.entails(a, need2, "x") is False   # prime does not entail even


# ------------------------------------------------------------------ domain_of_expr (item 8)
def test_log_requires_positive_argument():
    a = K.domain_of_expr(SYM.parse("log(x)"))
    assert a.get("x").has(K.PredKind.POSITIVE)


def test_sqrt_requires_nonneg_argument():
    a = K.domain_of_expr(SYM.parse("sqrt(x)"))
    assert a.get("x").has(K.PredKind.NONNEG)


def test_negative_power_requires_nonzero_base():
    a = K.domain_of_expr(SYM.parse("x**-1"))
    assert a.get("x").has(K.PredKind.NONZERO)


def test_domain_of_expr_ignores_safe_expression():
    a = K.domain_of_expr(SYM.parse("x**2 + 2*x + 1"))
    assert a.get("x").preds == frozenset()   # a polynomial imposes no domain requirement


def test_parse_assumptions_forms():
    a = K.parse_assumptions({"x": ["real", "positive"]})
    assert a.get("x").has(K.PredKind.POSITIVE) and a.get("x").has(K.PredKind.NONZERO)
    b = K.parse_assumptions(["n:even"])
    assert b.get("n").has(K.PredKind.INTEGER)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
