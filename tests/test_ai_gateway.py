"""Track C Phase A — the AI Gateway (idm.ai): a small deterministic entrance over the full solver.

Locks that the gateway is an ENTRANCE, never a capability reduction: it routes ~11 high-level ops to
the real kinds, exposes the route, forwards tiers verbatim (no silent downgrade), returns structured
error codes, and always points at the full registry as the escalation path.
"""
import idm
from idm.results import Result


def test_ops_vocabulary_is_small_and_well_formed():
    ops = idm.ai.ops()
    assert 8 <= len(ops) <= 12                                  # the point: a small decision space
    for o in ops:
        assert o["kind"] in idm.kinds()                        # every op routes to a REAL kind
        assert set(o) == {"op", "kind", "about", "fields", "tier"}
        assert o["tier"] == idm.describe(o["kind"])["tier"]    # tier is the honest, effective tier
    assert idm.ai.op_names() == [o["op"] for o in ops]


def test_run_routes_and_exposes_the_route():
    r = idm.ai.run("factor", n=360360)
    assert isinstance(r, Result) and r.is_ok
    assert r.value == idm.solve({"kind": "factorize", "n": 360360})["value"]   # same as direct solve
    assert r["route"] == {"op": "factor", "kind": "factorize"}                 # route always exposed
    # a few more ops resolve correctly through the gateway
    assert idm.ai.run("gcd", a=48, b=36).value == 12
    assert idm.ai.run("solve_linear", A=[[2, 1], [1, 3]], b=[3, 5]).value["solution_type"] == "unique"
    assert idm.ai.run("roots", coeffs=[-2, 0, 0, 1]).is_ok
    assert "C1*e^x" in idm.ai.run("ode", coeffs=[2, -3, 1]).value["general"]


def test_tier_is_forwarded_verbatim_not_downgraded():
    # the gateway does no math; the tier it returns is exactly what idm.solve returns for that kind
    for op, kind in (("factor", "factorize"), ("shortest_path", "shortest_path"), ("ode", "linear_ode")):
        assert idm.ai.run.__module__  # sanity
        direct = idm.solve({"kind": kind, **_min_params(kind)})
        routed = idm.ai.run(op, **_min_params(kind))
        assert routed.tier == direct.tier


def test_structured_error_codes():
    # unknown op → UNKNOWN_OP + a did_you_mean suggestion + the full op list + an escalation hint
    u = idm.ai.run("factour", n=12)
    assert u.is_hold and u["error_code"] == "UNKNOWN_OP" and u["did_you_mean"] == "factor"
    assert u["ops"] == idm.ai.op_names() and "idm.solve" in u["escalate"]
    # missing required field → MISSING_PARAM
    m = idm.ai.run("factor")
    assert m.is_hold and m["error_code"] == "MISSING_PARAM"
    # a genuine solver HOLD is forwarded with the route + SOLVER_HOLD
    h = idm.ai.run("roots", coeffs=[9999, -4242, 1313, -77, 1])
    assert h.is_hold and h["error_code"] == "SOLVER_HOLD" and h["route"]["kind"] == "all_roots"


def test_gateway_never_hides_the_full_api():
    # the ~11 ops are a strict subset; the full registry is much larger and reachable via idm.solve
    routed_kinds = {o["kind"] for o in idm.ai.ops()}
    assert routed_kinds < set(idm.kinds()) and len(idm.kinds()) > 200


def test_phase_b_dry_run_and_plan():
    """Phase B: run(..., dry_run=True) and plan() return the route + problem WITHOUT executing, and the
    required/missing validate is honest (uses only truly-required p[...] fields, not optionals)."""
    # dry_run returns the plan, does not execute
    p = idm.ai.run("factor", dry_run=True, n=360360)
    assert p["dry_run"] and p["status"] == "ready"
    assert p["route"] == {"op": "factor", "kind": "factorize"}
    assert p["problem"] == {"kind": "factorize", "n": 360360} and "value" not in p

    # an optional field absent (all_roots' `force`) is NOT flagged missing → status ready
    pr = idm.ai.plan("roots", coeffs=[-2, 0, 0, 1])
    assert pr["status"] == "ready" and pr["missing"] == [] and "force" in pr["optional"]

    # a truly-required field absent → needs_params
    pm = idm.ai.plan("solve_linear", A=[[1]])
    assert pm["status"] == "needs_params" and pm["missing"] == ["b"]

    # unknown op → HOLD/UNKNOWN_OP with a suggestion
    pu = idm.ai.plan("factour")
    assert pu["status"] == "HOLD" and pu["error_code"] == "UNKNOWN_OP" and pu["did_you_mean"] == "factor"


def test_phase_b_route_free_form_and_structured():
    """Phase B route(): free-form strings via idm.parse, and structured {op}/{kind} dicts, all map to a
    plan; an unclassifiable request HOLDs honestly."""
    # free-form string → parsed to a kind → mapped to the gateway op
    r = idm.ai.route("factor 360360")
    assert r["status"] == "ready" and r["route"] == {"op": "factor", "kind": "factorize"}
    assert r["problem"]["n"] == 360360 and r["source"] == "factor 360360"

    # structured {"op": ...} and {"kind": ...} dicts
    assert idm.ai.route({"op": "roots", "coeffs": [-2, 0, 0, 1]})["status"] == "ready"
    assert idm.ai.route({"kind": "factorize", "n": 12})["route"]["op"] == "factor"

    # a REAL kind outside the gateway's ops still routes (op=None) — never a capability reduction
    outside = idm.ai.route({"kind": "char_poly", "matrix": [[1, 2], [3, 4]]})
    assert outside["status"] == "ready" and outside["route"] == {"op": None, "kind": "char_poly"}

    # a bogus kind → HOLD/UNKNOWN_KIND (validated), not a silent "ready"
    bogus = idm.ai.route({"kind": "definitely_not_a_kind", "x": 1})
    assert bogus["status"] == "HOLD" and bogus["error_code"] == "UNKNOWN_KIND"

    # unclassifiable / odd inputs → HOLD, never a crash
    for junk in ("what is the meaning of life", None, 42, [], {}, {"foo": "bar"}):
        r = idm.ai.route(junk)
        assert r["status"] == "HOLD" and r.get("error_code") in ("UNCLASSIFIED", "UNKNOWN_KIND"), junk


def _min_params(kind):
    import tests.test_properties as tp
    return tp.FIXTURES.get(kind, {})


def test_phase_c_benchmark_harness():
    """Phase C: the synthetic dataset + benchmark harness. The deterministic router (the oracle) is
    perfect; the harness DISCRIMINATES a weak router (proving the score is meaningful, not trivially 1)."""
    import idm

    # oracle: idm.ai.route scores 100% op-selection and 100% execution over the dataset
    r = idm.ai_bench.benchmark_router()
    assert r["n"] >= 15 and r["op_accuracy"] == 1.0 and r["exec_accuracy"] == 1.0
    assert r["failures"] == []

    # the harness discriminates: a dumb router that always says "factor" scores far below the oracle
    dumb = idm.ai_bench.score(lambda request: "factor")
    assert dumb["op_accuracy"] < 0.3 and len(dumb["failures"]) > 10

    # a router can return a bare op string OR a plan/route dict — both are scored (accepts either shape)
    via_dict = idm.ai_bench.score(idm.ai.route)
    via_str = idm.ai_bench.score(lambda req: (idm.ai.route(req).get("route") or {}).get("op"))
    assert via_dict["op_accuracy"] == via_str["op_accuracy"] == 1.0
