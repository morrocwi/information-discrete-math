"""Tests for the exact real harmonic Navier-Stokes probe."""
import idm


def test_harmonic_probe_registered_sparse_and_verified():
    assert "ns_retained_harmonic_probe" in idm.kinds()
    r = idm.solve({
        "kind": "ns_retained_harmonic_probe",
        "K": 2,
        "nu": 0.005,
        "dt": 0.0025,
        "horizon": 1,
        "wavevector": [2, 2, 2],
        "phase": 0.3,
        "verify": True,
    })
    assert r["status"] == "ok", r
    assert r["tier"] == "finite_diagnostic"
    assert r["terminal_mode_count"] == 2
    assert r["readout_density"] == 2 / r["mode_count"]
    assert r["terminal_step_cone"]["k4_modes"] == 2
    assert r["terminal_step_cone"]["k3_modes"] < r["mode_count"]
    assert r["verification"]["status"] == "PASS"
    assert r["verification"]["target_abs_error"] <= 1e-12
    assert r["structural_work_reduction"] > 1.0
    assert r["imaginary_residual"] <= 1e-12
    assert len(r["value"]) == 3


def test_harmonic_probe_time_alias():
    r = idm.solve({
        "kind": "ns_retained_harmonic_probe",
        "K": 1,
        "dt": 0.0025,
        "time": 0.005,
        "wavevector": [1, 1, 1],
        "verify": True,
    })
    assert r["status"] == "ok", r
    assert r["horizon"] == 2
    assert r["verification"]["status"] == "PASS"


def test_harmonic_probe_bad_wavevector_holds():
    r = idm.solve({
        "kind": "ns_retained_harmonic_probe",
        "K": 2,
        "wavevector": [3, 3, 3],
    })
    assert r["status"] == "HOLD"


def test_harmonic_probe_visible_in_server_openapi():
    from idm import server
    enum = server.OPENAPI["paths"]["/solve"]["post"]["requestBody"]["content"]["application/json"]["schema"]["properties"]["kind"]["enum"]
    assert "ns_retained_harmonic_probe" in enum
