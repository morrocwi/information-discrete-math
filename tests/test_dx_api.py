"""Track B — programmer developer-experience: the Result wrapper + typed convenience wrappers.

Locks that Result stays a backward-compatible dict (the solver, REST server, and golden snapshots all
depend on dict behaviour) while adding typed accessors, and that the one-call wrappers dispatch to the
right kind.
"""
import json

import pytest

import idm
from idm.results import Result, SolveHold


def test_result_is_a_backward_compatible_dict():
    r = idm.solve({"kind": "factorize", "n": 360360})
    assert isinstance(r, Result) and isinstance(r, dict)
    # every dict access still works, identically to a plain dict
    assert r["status"] == "ok" and r.get("tier") == "exact"
    assert json.dumps(r) == json.dumps(dict(r))            # serialises identically → golden-safe
    assert r == dict(r)                                     # dict-equality against a plain dict
    assert r.to_dict() == dict(r) and type(r.to_dict()) is dict


def test_result_typed_accessors():
    r = idm.solve({"kind": "gcd", "a": 48, "b": 36})
    assert r.status == "ok" and r.is_ok and not r.is_hold
    assert r.value == 12 and r.tier is not None
    assert r.kind == "gcd" and r.reason is None             # accessors never raise on a missing key


def test_result_hold_and_raise_for_hold():
    h = idm.solve({"kind": "definitely_not_a_kind"})
    assert h.is_hold and not h.is_ok and h.value is None
    assert isinstance(h.reason, str) and h.reason
    with pytest.raises(SolveHold):
        h.raise_for_hold()
    # on success, raise_for_hold returns self so it chains
    assert idm.solve({"kind": "factorize", "n": 97}).raise_for_hold().value == {"97": 1}


def test_typed_convenience_wrappers_dispatch_correctly():
    assert idm.factorize(360360).value == idm.solve({"kind": "factorize", "n": 360360})["value"]
    assert idm.gcd(48, 36).value == 12
    assert idm.solve_matrix([[2, 1], [1, 3]], [3, 5]).is_ok
    assert idm.solve_roots([1, 0, 1]).status == "ok"
    assert idm.solve_ode([2, -3, 1]).status in ("ok", "HOLD")
    assert idm.integrate_rational([1], [1, 0, 1]).status in ("ok", "HOLD")
    # every wrapper returns a Result
    for r in (idm.factorize(10), idm.gcd(4, 6), idm.solve_roots([1, 0, 1]),
              idm.solve_matrix([[1]], [1]), idm.eigenvalues([[2, 0], [0, 3]])):
        assert isinstance(r, Result)


def test_result_classifies_the_full_status_space():
    """is_ok / is_hold / is_open cover every status the solver actually emits — not just ok/HOLD.
    Regression for reviewer #93: a REFUTED counterexample (definitive, has a value) is is_ok; an
    open-tail +R_OPEN readout (no plain value) is is_open, NOT is_ok."""
    import tests.test_properties as tp

    # REFUTED — a definitive counterexample (value=False + witness): resolved, so is_ok, NOT hold/open
    ref = idm.solve({"kind": "polynomial_positivity",
                     "polynomial": "x**4*y**2 + x**2*y**4 + 1 - 4*x**2*y**2", "variables": ["x", "y"]})
    assert ref.status == "REFUTED" and ref.value is False
    assert ref.is_ok and not ref.is_hold and not ref.is_open

    # +R_OPEN — an open-tail readout with no plain value: is_open, NOT is_ok/is_hold
    opn = idm.solve(dict(kind="l2_readout", **tp.FIXTURES["l2_readout"]))
    assert opn.status == "+R_OPEN" and opn.value is None
    assert opn.is_open and not opn.is_ok and not opn.is_hold

    # the three predicates are mutually exclusive for these, and ok/HOLD stay correct
    ok = idm.solve({"kind": "factorize", "n": 12})
    hold = idm.solve({"kind": "not_a_kind"})
    assert ok.is_ok and not ok.is_hold and not ok.is_open
    assert hold.is_hold and not hold.is_ok and not hold.is_open


def test_public_exports_present():
    for name in ("Result", "SolveHold", "factorize", "gcd", "solve_integral", "integrate_rational",
                 "solve_matrix", "eigenvalues", "solve_roots", "solve_ode", "kinds"):
        assert name in idm.__all__ and hasattr(idm, name), name
