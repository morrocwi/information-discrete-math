#!/usr/bin/env python3
"""IDM Symbolic Kernel v2 — Wave 0 (pillar P1.1): expression tree + number tower.

Run: PYTHONPATH=. python3 -m pytest tests/test_kernel_p1.py -q
"""

from __future__ import annotations

from fractions import Fraction as Q

import pytest

import idm
from idm import kernel as K
from idm import symbolic as SYM


# ------------------------------------------------------------------ tiers (item 1)
def test_tier_vocabulary_matches_solve_literals():
    assert {t.value for t in K.Tier} == {
        "Th_coqc", "exact", "finite_diagnostic", "+R-Open", "Dr",
    }
    # the tiers solve.py actually stamps must all exist
    for used in ("Th_coqc", "exact", "finite_diagnostic"):
        assert K.Tier(used).value == used


def test_hold_error_is_internal_only():
    assert issubclass(K.DomainUnsafeRewrite, K.HoldError)
    assert issubclass(K.ResourceBudgetExceeded, K.HoldError)
    assert K.DomainUnsafeRewrite("x").reason == "x"


# ------------------------------------------------------------------ hashcons / interning (item 2)
def test_structural_hash_is_stable():
    a = K.Const(Q(1, 3))
    b = K.Const(Q(1, 3))
    assert a._hash == b._hash
    assert a == b and hash(a) == hash(b)


def test_intern_collapses_equal_trees_to_one_object():
    def build():
        return K.Add([K.Symbol("x"), K.Const(1)])
    t1, t2 = build(), build()
    assert t1 is not t2         # independently constructed
    assert t1 == t2             # but structurally equal
    table = K.InternTable()
    i1 = table.intern(t1)
    i2 = table.intern(t2)
    assert i1 is i2             # interning reduces equality to identity


def test_canonical_order_is_deterministic():
    # operand order is canonicalized, so two build orders give the same tree
    ab = K.Add([K.Symbol("a"), K.Symbol("b")])
    ba = K.Add([K.Symbol("b"), K.Symbol("a")])
    assert ab == ba and ab._order == ba._order


# ------------------------------------------------------------------ nodes (item 3)
def test_nonreadout_leaves_flagged():
    assert K.Undefined("0/0").is_nonreadout is True
    assert K.Infinity(1).is_nonreadout is True
    assert K.ComplexInfinity().is_nonreadout is True
    assert K.Add([K.Symbol("x"), K.Const(1)]).is_nonreadout is False
    assert K.Const(1).is_nonreadout is False


def test_node_equality_is_structural():
    e1 = K.Pow(K.Symbol("x"), K.Const(2))
    e2 = K.Pow(K.Symbol("x"), K.Const(2))
    e3 = K.Pow(K.Symbol("x"), K.Const(3))
    assert e1 == e2 and e1 != e3
    assert K.Func("sin", (K.Symbol("x"),)) == K.Func("sin", (K.Symbol("x"),))
    assert K.Func("sin", (K.Symbol("x"),)) != K.Func("cos", (K.Symbol("x"),))


# ------------------------------------------------------------------ numbers (item 4)
def test_int_rational_coercion_roundtrip():
    up = K.coerce_up(K.ExactInteger(5), K.ExactRational)
    assert up.status == "ok" and up.tier == K.Tier.EXACT
    assert up.value == K.ExactRational(Q(5))
    down = K.coerce_down(up.value, K.ExactInteger)
    assert down.status == "ok" and down.value == K.ExactInteger(5)


def test_coercion_to_ball_downgrades_tier_honestly():
    cert = K.coerce_up(K.ExactRational(Q(1, 3)), K.RealBall, prec_dps=30)
    assert cert.tier == K.Tier.FINITE_DIAGNOSTIC   # never EXACT — the R6/R9 honesty guarantee
    assert cert.tier != K.Tier.EXACT


def test_coerce_down_holds_when_not_exact():
    down = K.coerce_down(K.ExactRational(Q(1, 3)), K.ExactInteger)
    assert down.status == K.HOLD and down.value is None


def test_from_python_rejects_float():
    with pytest.raises(TypeError):
        K.from_python(0.1)
    assert K.from_python(4) == K.ExactInteger(4)
    assert K.from_python(Q(1, 2)) == K.ExactRational(Q(1, 2))


def test_const_rejects_non_readout_values():
    # A Const must never launder a finite-precision ball or a Certificate into an "exact" leaf.
    with pytest.raises(TypeError):
        K.Const(0.1)
    with pytest.raises(TypeError):
        K.Const(K.RealBall("lo", "hi", 30))
    with pytest.raises(TypeError):
        K.Const(K.Certificate(None, "ok", K.Tier.EXACT))
    # exact rungs are accepted
    assert K.Const(K.ExactRational(Q(1, 3))).value == K.ExactRational(Q(1, 3))


# ------------------------------------------------------------------ legacy bridge (item 5)
_FIXTURES = ["x", "x + 1", "x*y + 3", "sin(x)", "x**2 + 2*x + 1", "1/3", "exp(x) + log(x)"]


@pytest.mark.parametrize("src", _FIXTURES)
def test_kernel_level_roundtrip_is_identity(src):
    e = K.from_legacy(SYM.parse(src))
    # to_legacy preserves structure; from_legacy re-canonicalizes deterministically -> same Expr
    assert K.from_legacy(K.to_legacy(e)) == e


@pytest.mark.parametrize("src", ["sin(x)", "x**3", "exp(x)"])
def test_legacy_roundtrip_identity_on_order_insensitive(src):
    t = SYM.parse(src)
    assert K.to_legacy(K.from_legacy(t)) == t


def test_to_legacy_rejects_nonlegacy_node():
    rel = K.Relation("<=", K.Symbol("x"), K.Const(0))
    with pytest.raises(ValueError):
        K.to_legacy(rel)


# ------------------------------------------------------------------ non-regression
def test_kernel_import_does_not_disturb_registry():
    import importlib
    before = set(idm.kinds())
    importlib.import_module("idm.kernel")   # re-import must not mutate the solve registry
    after = set(idm.kinds())
    assert before == after, "importing idm.kernel changed the solve registry"
    assert len(after) > 200, "registry unexpectedly small — is the domain package loaded?"  # not a hardcoded exact count
    assert idm.solve({"kind": "constant", "name": "pi"})["status"] in ("ok", "CERTIFIED")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
