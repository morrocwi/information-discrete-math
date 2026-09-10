import math

from idm.ns_epsilon import (
    boundary_energy,
    epsilon_completion_verdict,
    nested_cutoff_diagnostic,
    nested_readout_consistency_defect,
    taylor_green_state,
)


def test_nested_defect_zero_for_identical_shared_state():
    state = taylor_green_state(1)
    assert nested_readout_consistency_defect(state, dict(state)) == 0.0


def test_boundary_energy_is_nonnegative():
    state = taylor_green_state(1)
    assert boundary_energy(state, 1) >= 0.0


def test_epsilon_gate_fails_closed_without_tail_bound():
    verdict = epsilon_completion_verdict(delta=0.0, beta=None, epsilon=1e-6)
    assert verdict["status"] == "HOLD"
    assert verdict["tier"] == "finite_diagnostic"


def test_epsilon_gate_accepts_only_with_declared_bound():
    verdict = epsilon_completion_verdict(delta=2e-7, beta=3e-7, epsilon=1e-6)
    assert verdict["status"] == "CERTIFIED"
    assert math.isclose(verdict["total_bound"], 5e-7)


def test_small_nested_diagnostic_keeps_continuum_on_hold():
    result = nested_cutoff_diagnostic(
        K_values=(1, 2),
        nu=0.01,
        dt=0.001,
        steps=1,
        consecutive_required=1,
    )
    assert result["status"] == "finite_diagnostic"
    assert result["continuum_certificate"] == "HOLD"
    assert result["toledo"] == [
        "PROP-EPSC-01",
        "PROP-EPSC-02",
        "PROP-EPSC-03",
        "PROP-EPSC-04",
    ]
