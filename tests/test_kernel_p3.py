#!/usr/bin/env python3
"""IDM Symbolic Kernel v2 — Wave 2 (pillar P1.3): pattern matcher & rewrite engine.

Run: PYTHONPATH=. python3 -m pytest tests/test_kernel_p3.py -q
"""

from __future__ import annotations

from fractions import Fraction as Q

from idm import kernel as K
from idm import symbolic as SYM
from idm.kernel.engine import GuardVerdict


X = ("var", "x")


# ------------------------------------------------------------------ match / substitute (item 9)
def test_pow_pow_pattern_matches_and_substitutes():
    pat = ("pow", ("pow", K.Wildcard("b"), K.Wildcard("a")), K.Wildcard("c"))
    expr = ("pow", ("pow", X, Q(2)), Q(3))
    env = K.match(pat, expr)
    assert env is not None
    assert env["b"] == X and env["a"] == Q(2) and env["c"] == Q(3)
    # substitute the collapse template back
    out = K.substitute(lambda e: ("pow", e["b"], ("mul", [e["a"], e["c"]])), env)
    assert out == ("pow", X, ("mul", [Q(2), Q(3)]))


def test_match_rejects_wrong_shape():
    pat = ("pow", ("pow", K.Wildcard("b"), K.Wildcard("a")), K.Wildcard("c"))
    assert K.match(pat, ("pow", X, Q(3))) is None          # not a nested pow
    assert K.match(pat, ("func", "sin", X)) is None


# ------------------------------------------------------------------ domain_gate (item 10)
def test_domain_gate_integer_on_constant_and_symbol():
    g = K.domain_gate("integer", on="c")
    empty = K.AssumptionSet.empty()
    assert g.check({"c": Q(3)}, empty) is GuardVerdict.SAFE          # concrete integer
    assert g.check({"c": Q(1, 2)}, empty) is GuardVerdict.UNKNOWN    # concrete non-integer
    assert g.check({"c": ("var", "c")}, empty) is GuardVerdict.UNKNOWN   # symbol, no fact -> fail-closed
    asm = K.parse_assumptions({"c": ["integer"]})
    assert g.check({"c": ("var", "c")}, asm) is GuardVerdict.SAFE    # symbol with the fact


def test_domain_gate_positive_and_or_combination():
    g = K.domain_gate("integer", on="c") | K.domain_gate("positive", on="b")
    empty = K.AssumptionSet.empty()
    assert g.check({"c": Q(1, 2), "b": Q(5)}, empty) is GuardVerdict.SAFE     # b positive const
    assert g.check({"c": Q(1, 2), "b": ("var", "x")}, empty) is GuardVerdict.UNKNOWN
    asm = K.parse_assumptions({"x": ["positive"]})
    assert g.check({"c": Q(1, 2), "b": ("var", "x")}, asm) is GuardVerdict.SAFE


# ------------------------------------------------------------------ gated rewrite (item 11)
def test_collapse_fires_on_integer_outer_exponent():
    res = K.rewrite(("pow", ("pow", X, Q(2)), Q(3)), K.RS_CORE_NORMALIZE)
    assert res.value == ("pow", X, Q(6))   # (x^2)^3 -> x^(2*3), constants folded
    assert "pow_pow_collapse" in res.fired


def test_collapse_gated_off_without_assumption():
    # (x^(1/2))^(1/2): outer exp non-integer, base not known positive -> NOT collapsed (fail-closed)
    e = ("pow", ("pow", X, Q(1, 2)), Q(1, 2))
    res = K.rewrite(e, K.RS_CORE_NORMALIZE)
    assert res.value == e            # unchanged
    assert res.fired == ()


def test_collapse_fires_under_positive_assumption():
    e = ("pow", ("pow", X, Q(1, 2)), Q(1, 2))
    asm = K.parse_assumptions({"x": ["positive"]})
    res = K.rewrite(e, K.RS_CORE_NORMALIZE, assumptions=asm)
    assert res.value == ("pow", X, Q(1, 4))   # (x^(1/2))^(1/2) -> x^(1/4), constants folded
    assert "pow_pow_collapse" in res.fired


def test_gate_prevents_a_value_changing_rewrite():
    # (x^2)^(1/2) -> x is UNSAFE: at x=-3 the two sides differ. The gate must refuse.
    e = ("pow", ("pow", X, Q(2)), Q(1, 2))
    res = K.rewrite(e, K.RS_CORE_NORMALIZE)          # no assumption
    assert res.value == e                            # refused -> unchanged
    collapsed = ("pow", X, Q(1))                      # what an UNGATED collapse would produce
    at = {"x": -3}
    assert float(SYM.evaluate(e, at)) != float(SYM.evaluate(collapsed, at))  # ≈3 vs -3


# ------------------------------------------------------------------ symbolic.simplify hook (item 12)
def test_simplify_default_is_unchanged_byte_identical():
    # no assumptions -> today's behavior preserved (unconditional nested-power collapse still happens)
    assert SYM.simplify(SYM.parse("(x**2)**3")) == ("pow", X, Q(6))
    assert SYM.simplify(SYM.parse("x + x")) == ("mul", [Q(2), X])
    assert SYM.simplify(SYM.parse("sin(0)")) == Q(0)


def test_simplify_with_assumptions_gates_the_collapse():
    e = ("pow", ("pow", X, Q(2)), Q(1, 2))
    empty = K.AssumptionSet.empty()
    # gated OFF (x not known positive, outer exp 1/2 non-integer) -> nested power kept
    assert SYM.simplify(e, assumptions=empty) == e
    # with x positive -> safe to collapse: (x^2)^(1/2) = x^1 = x
    asm = K.parse_assumptions({"x": ["positive"]})
    assert SYM.simplify(e, assumptions=asm) == X


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
