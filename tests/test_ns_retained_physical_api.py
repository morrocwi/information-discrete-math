"""API tests for exact physical-space finite Navier-Stokes readouts."""
import idm


def test_ns_retained_physical_registered_dense_exact_reader():
    assert "ns_retained_physical" in idm.kinds()
    r = idm.solve({
        "kind": "ns_retained_physical",
        "K": 1,
        "nu": 0.005,
        "dt": 0.0025,
        "horizon": 1,
        "point": [0.2, 0.3, 0.4],
        "readout": "velocity",
    })
    assert r["status"] == "ok"
    assert r["tier"] == "finite_diagnostic"
    assert r["backend"] == "portable_full_rk4"
    assert r["compression_status"] == "DENSE_READOUT_FULL_RK4"
    assert r["terminal_mode_count"] == r["mode_count"]
    assert r["readout_density"] == 1.0
    assert abs(r["structural_work_reduction"] - 1.0) <= 1e-15
    assert len(r["value"]) == 3


def test_ns_retained_physical_time_alias_matches_horizon():
    base = {
        "kind": "ns_retained_physical",
        "K": 1,
        "nu": 0.005,
        "dt": 0.0025,
        "point": [0.2, 0.3, 0.4],
        "readout": "velocity",
    }
    a = idm.solve({**base, "horizon": 2})
    b = idm.solve({**base, "time": 0.005})
    assert a["status"] == "ok" and b["status"] == "ok"
    assert a["value"] == b["value"]
    assert a["horizon"] == b["horizon"] == 2


def test_ns_retained_physical_nonintegral_time_holds():
    r = idm.solve({
        "kind": "ns_retained_physical",
        "K": 1,
        "dt": 0.0025,
        "time": 0.004,
        "point": [0.2, 0.3, 0.4],
    })
    assert r["status"] == "HOLD"
    assert "integer multiple of dt" in r["reason"]


def test_ns_retained_physical_component_readout():
    r = idm.solve({
        "kind": "ns_retained_physical",
        "K": 1,
        "horizon": 1,
        "point": [0.1, -0.2, 0.5],
        "component": "x",
    })
    assert r["status"] == "ok"
    assert isinstance(r["value"], dict) and "re" in r["value"] and "im" in r["value"]


def test_ns_physical_kind_visible_in_server_openapi():
    from idm import server
    enum = server.OPENAPI["paths"]["/solve"]["post"]["requestBody"]["content"]["application/json"]["schema"]["properties"]["kind"]["enum"]
    assert "ns_retained_physical" in enum
