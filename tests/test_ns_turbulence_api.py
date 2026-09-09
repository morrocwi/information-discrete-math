import math

import idm
from idm import ns_retained as NSR
from idm import ns_turbulence as NST


def test_modal_nonlinear_transfer_conserves_total_energy_on_default_finite_state():
    modes = NSR.cube_modes(1)
    triads = NSR.triads_by_output(modes)
    state = NSR.deterministic_state(modes, seed=20260909, target_energy=0.125)
    transfer = NST.nonlinear_transfer_by_mode(state, modes, triads)
    assert abs(sum(transfer.values())) <= 1e-12


def test_energy_flux_solver_matches_full_finite_rk4():
    r = NST.solve_energy_flux(
        K=1,
        nu=0.005,
        dt=0.0025,
        horizon=1,
        cutoff=1.0,
        verify=True,
    )
    assert math.isfinite(r["value"])
    assert r["included_mode_count"] > 0
    assert r["required_terminal_state_modes"] >= r["included_mode_count"]
    assert r["verification"]["status"] == "PASS"
    assert r["verification"]["retained_full_flux_abs_error"] <= 1e-12
    assert r["verification"]["nonlinear_total_transfer_abs"] <= 1e-12


def test_flux_at_cutoff_covering_all_modes_is_zero_up_to_floating_error():
    r = NST.solve_energy_flux(
        K=1,
        nu=0.005,
        dt=0.0025,
        horizon=1,
        cutoff=math.sqrt(3.0),
        verify=True,
    )
    assert r["included_mode_count"] == r["mode_count"]
    assert abs(r["value"]) <= 1e-12


def test_public_solver_kind_reports_turbulence_readout():
    r = idm.solve({
        "kind": "ns_turbulence_energy_flux",
        "K": 1,
        "nu": 0.005,
        "dt": 0.0025,
        "horizon": 1,
        "cutoff": 1.0,
        "verify": True,
    })
    assert r.status == "ok"
    assert r["readout"] == "turbulence_energy_flux"
    assert r["verification"]["status"] == "PASS"
    assert "not continuum turbulence" in r["claim_scope"]


def test_invalid_nonphysical_user_state_holds_fail_closed():
    r = idm.solve({
        "kind": "ns_turbulence_energy_flux",
        "K": 1,
        "nu": 0.005,
        "dt": 0.0025,
        "horizon": 1,
        "cutoff": 1.0,
        "initial_state": [
            {"k": [1, 0, 0], "u": [[1, 0], [0, 0], [0, 0]]},
        ],
    })
    assert r.status == "HOLD"
