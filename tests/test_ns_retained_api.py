"""API tests for the portable task-conditioned Navier-Stokes RK4 kind."""
import idm


def test_ns_retained_rk4_registered_and_verified():
    assert "ns_retained_rk4" in idm.kinds()
    r = idm.solve({
        "kind": "ns_retained_rk4",
        "K": 1,
        "nu": 0.005,
        "dt": 0.0025,
        "horizon": 1,
        "target_mode": [1, 0, 0],
        "verify": True,
    })
    assert r["status"] == "ok"
    assert r["tier"] == "finite_diagnostic"
    assert r["backend"] == "portable_direct_retained"
    assert r["verification"]["status"] == "PASS"
    assert r["verification"]["target_abs_error"] <= 1e-12
    assert r["structural_work_reduction"] > 1.0
    assert len(r["value"]) == 3


def test_ns_retained_rk4_resource_guard_holds():
    r = idm.solve({
        "kind": "ns_retained_rk4",
        "K": 4,
        "horizon": 1,
        "target_mode": [1, 0, 0],
    })
    assert r["status"] == "HOLD"
    assert "portable API guard" in r["reason"]


def test_ns_kind_visible_in_server_openapi():
    from idm import server
    enum = server.OPENAPI["paths"]["/solve"]["post"]["requestBody"]["content"]["application/json"]["schema"]["properties"]["kind"]["enum"]
    assert "ns_retained_rk4" in enum
