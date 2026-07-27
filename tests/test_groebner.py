#!/usr/bin/env python3
"""Gröbner bases over ℚ — CAS-grade coverage (pillar P2).

Correctness is pinned three ways without depending on an external CAS: known reduced bases for
worked examples, the defining ideal properties (every input generator and every S-polynomial reduces
to zero; the basis is monic, reduced, and idempotent under a second Buchberger pass), and ideal
membership decided by the normal form.

Run: PYTHONPATH=. python3 -m pytest tests/test_groebner.py -q
"""

from __future__ import annotations

import pytest

import idm
from idm.kernel.poly.groebner import (
    buchberger,
    in_ideal,
    normal_form,
    parse_poly,
    poly_to_str,
    reduced_groebner,
    s_polynomial,
)

V = ["x", "y"]


def _P(s, variables=V):
    return parse_poly(s, variables)


def test_parse_and_render_roundtrip():
    assert poly_to_str(_P("3*x^2*y - 1/2*y + 5"), V) == "3*x^2*y - 1/2*y + 5"
    assert poly_to_str(_P("x*y + y*x"), V) == "2*x*y"          # like terms combine
    assert poly_to_str(_P("2x^3"), V) == "2*x^3"                # implicit coefficient
    assert _P("x*y") == _P("y*x")                               # cross term, order-free


def test_parse_rejects_unknown_variable():
    with pytest.raises(ValueError):
        _P("x + z", ["x", "y"])


def test_circle_and_line_grevlex():
    G = reduced_groebner([_P("x^2+y^2-1"), _P("x-y")], "grevlex")
    assert {poly_to_str(g, V, "grevlex") for g in G} == {"y^2 - 1/2", "x - y"}


def test_unit_ideal_reduces_to_one():
    # <x, x+1> = <1> = the whole ring
    G = reduced_groebner([_P("x"), _P("x+1")], "grevlex")
    assert [poly_to_str(g, V) for g in G] == ["1"]


def test_every_generator_reduces_to_zero():
    # F ⊆ ideal(G): each input generator must have normal form 0 modulo the basis
    F = [_P("x^3-2*x*y"), _P("x^2*y-2*y^2+x")]
    G = reduced_groebner(F, "grevlex")
    for f in F:
        assert normal_form(f, G, "grevlex") == {}


def test_all_s_polynomials_reduce_to_zero():
    # the Buchberger termination criterion: for a Gröbner basis, every S-pair reduces to 0
    G = buchberger([_P("x^2+y^2-1"), _P("x-y")], "grevlex")
    for i in range(len(G)):
        for j in range(i + 1, len(G)):
            assert normal_form(s_polynomial(G[i], G[j], "grevlex"), G, "grevlex") == {}


def test_reduced_basis_is_monic_and_idempotent():
    F = [_P("x^2+x*y+1"), _P("y^2-2")]
    G = reduced_groebner(F, "lex")
    # monic: leading coefficient 1 (the max-order monomial's coeff)
    from idm.kernel.poly.groebner import _lead, _order_key
    key = _order_key("lex")
    for g in G:
        assert g[_lead(g, key)] == 1
    # idempotent: a reduced GB of a reduced GB is itself
    G2 = reduced_groebner(G, "lex")
    assert {frozenset(g.items()) for g in G} == {frozenset(g.items()) for g in G2}


def test_ideal_membership():
    F = [_P("x^2+y^2-1"), _P("x-y")]
    assert in_ideal(_P("x^2+y^2-1"), F)          # a generator is in the ideal
    assert in_ideal(_P("2*x^2+2*y^2-2"), F)      # a multiple of it too
    assert not in_ideal(_P("x"), F)              # x alone is not
    assert not in_ideal(_P("1"), F)              # the ideal is proper (not the unit ideal)


def test_lex_eliminates_a_variable():
    # lex with x > y puts a pure-y polynomial in the basis (elimination ideal ∩ ℚ[y])
    G = reduced_groebner([_P("x^2+y^2-1"), _P("x-y")], "lex")
    strs = [poly_to_str(g, V, "lex") for g in G]
    assert any("x" not in s for s in strs)       # some generator is purely in y


def test_three_variables():
    W = ["x", "y", "z"]
    F = [parse_poly(s, W) for s in ("x^2+y^2+z^2-1", "x^2+y^2+z^2-2*x", "x-2*y+3*z")]
    G = reduced_groebner(F, "lex")
    for f in F:
        assert normal_form(f, G, "lex") == {}
    assert len(G) == 3


# ---- the registered kind, end to end ----

def test_kind_basis():
    r = idm.solve({"kind": "groebner_basis", "polys": ["x^2+y^2-1", "x-y"],
                   "variables": ["x", "y"], "order": "grevlex"})
    assert r["status"] == "ok" and r["tier"] == "exact"
    assert set(r["value"]["basis"]) == {"y^2 - 1/2", "x - y"}


def test_kind_membership_query():
    r = idm.solve({"kind": "groebner_basis", "polys": ["x^2-y", "y^2-x"],
                   "variables": ["x", "y"], "member": "x^2-y"})
    assert r["value"]["member_in_ideal"] is True
    r2 = idm.solve({"kind": "groebner_basis", "polys": ["x^2-y", "y^2-x"],
                    "variables": ["x", "y"], "member": "x*y+1"})
    assert r2["value"]["member_in_ideal"] is False


def test_kind_bad_input_holds():
    assert idm.solve({"kind": "groebner_basis", "polys": ["x+w"], "variables": ["x", "y"]})["status"] == "HOLD"
    assert idm.solve({"kind": "groebner_basis", "variables": ["x"]})["status"] == "HOLD"      # no polys
    assert idm.solve({"kind": "groebner_basis", "polys": ["x+y"], "variables": ["x", "y"],
                      "order": "nonsense"})["status"] == "HOLD"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
