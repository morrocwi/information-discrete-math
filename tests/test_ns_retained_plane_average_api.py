"""Tests for exact sparse plane-average Navier-Stokes readout."""
import idm


def test_plane_average_registered_sparse_and_verified():
    assert "ns_retained_plane_average" in idm.kinds()
    r = idm.solve({
        "kind": "ns_retained_plane_average",
        "K": 1,
        "nu": 0.005,
        "dt": 0.0025,
        "horizon": 1,
        "axis": "x",
        "coordinate": 0.37,
        "verify": True,
    })
    assert r["status"] == "ok", r
    assert r["tier"] == "finite_diagnostic"
    assert r["backend"] == "portable_direct_retained"
    assert r["mode_count"] == 26
    assert r["terminal_mode_count"] == 2
    assert abs(r["readout_density"] - 2 / 26) < 1e-15
    assert r["compression_status"] == "SPARSE_EXACT_RETAINED"
    assert r["verification"]["status"] == "PASS"
    assert r["verification"]["target_abs_error"] <= 1e-12
    assert r["structural_work_reduction"] > 1.0
    assert r["imaginary_residual"] <= 1e-12
    assert r["longitudinal_residual"] <= 1e-12
    assert len(r["value"]) == 3


def test_plane_average_time_alias_and_axes():
    r = idm.solve({
        "kind": "ns_retained_plane_average",
        "K": 1,
        "dt": 0.0025,
        "time": 0.005,
        "axis": "z",
        "coordinate": 1.1,
        "verify": True,
    })
    assert r["status"] == "ok", r
    assert r["horizon"] == 2
    assert r["terminal_mode_count"] == 2
    assert r["verification"]["status"] == "PASS"
    assert r["longitudinal_residual"] <= 1e-12


def test_plane_average_invalid_time_and_axis_hold():
    bad_time = idm.solve({
        "kind": "ns_retained_plane_average",
        "K": 1,
        "dt": 0.0025,
        "time": 0.003,
        "axis": "x",
    })
    assert bad_time["status"] == "HOLD"

    bad_axis = idm.solve({
        "kind": "ns_retained_plane_average",
        "K": 1,
        "axis": "q",
    })
    assert bad_axis["status"] == "HOLD"


def test_plane_average_visible_in_server_openapi():
    from idm import server
    enum = server.OPENAPI["paths"]["/solve"]["post"]["requestBody"]["content"]["application/json"]["schema"]["properties"]["kind"]["enum"]
    assert "ns_retained_plane_average" in enum
