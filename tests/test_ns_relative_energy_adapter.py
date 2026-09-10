import math

from idm.ns_relative_energy_adapter import (
    finite_galerkin_nonlinear_residual_hminus1,
    fourier_grad_linf_upper,
    k_supported_terminal_tail_beta,
    relative_energy_adapter_bounds,
    retained_energy_tape_from_adapter,
)


def test_zero_residual_zero_initial_error_certifies_zero_error():
    r = relative_energy_adapter_bounds(
        nu=0.1,
        initial_l2_error_upper=0.0,
        grad_linf_time_integral_upper=10.0,
        residual_hminus1_l2_squared_integral_upper=0.0,
    )
    assert r["status"] == "CERTIFIED_BOUND"
    assert r["terminal_l2_error_upper"] == 0.0
    t = k_supported_terminal_tail_beta(adapter_result=r)
    assert t["beta"] == 0.0


def test_relative_energy_formula_matches_declared_bound():
    r = relative_energy_adapter_bounds(
        nu=0.5,
        initial_l2_error_upper=0.1,
        grad_linf_time_integral_upper=0.2,
        residual_hminus1_l2_squared_integral_upper=0.03,
    )
    expected_sq = math.exp(0.4) * (0.01 + 0.03 / 0.5)
    assert math.isclose(r["sup_l2_error_squared_upper"], expected_sq, rel_tol=1e-14)
    assert math.isclose(r["terminal_l2_error_upper"], math.sqrt(expected_sq), rel_tol=1e-14)


def test_adapter_fails_closed_on_exponential_overflow_regime():
    r = relative_energy_adapter_bounds(
        nu=0.1,
        initial_l2_error_upper=1.0,
        grad_linf_time_integral_upper=400.0,
        residual_hminus1_l2_squared_integral_upper=0.0,
    )
    assert r["status"] == "HOLD"


def test_energy_tape_directional_bounds():
    r = relative_energy_adapter_bounds(
        nu=1.0,
        initial_l2_error_upper=0.1,
        grad_linf_time_integral_upper=0.0,
        residual_hminus1_l2_squared_integral_upper=0.0,
    )
    tape = retained_energy_tape_from_adapter(
        comparison_terminal_l2_norm=2.0,
        comparison_grad_l2_time_norm=3.0,
        adapter_result=r,
    )
    assert tape["status"] == "CERTIFIED_BOUND"
    assert math.isclose(tape["retained_terminal_l2_norm_lower"], 1.9, rel_tol=1e-14)
    assert tape["retained_grad_l2_time_norm_lower"] <= 3.0


def test_fourier_grad_linf_upper_single_mode():
    state = {(2, 0, 0): (0j, 3 + 4j, 0j)}
    assert fourier_grad_linf_upper(state) == 10.0


def test_shear_mode_has_zero_unresolved_nonlinear_residual():
    # v=(0,sin x,0): q.u_p=0 for all active collinear q/p modes.
    state = {
        (1, 0, 0): (0j, -0.5j, 0j),
        (-1, 0, 0): (0j, 0.5j, 0j),
    }
    r = finite_galerkin_nonlinear_residual_hminus1(state, K=1)
    assert math.isclose(r["residual_hminus1_norm"], 0.0, abs_tol=1e-15)


def test_generic_two_mode_state_produces_finite_residual_summary():
    # Divergence-free coefficients with a nontrivial q.u_p interaction.
    state = {
        (1, 0, 0): (0j, 1 + 0j, 0j),
        (-1, 0, 0): (0j, 1 + 0j, 0j),
        (0, 1, 0): (1 + 0j, 0j, 0j),
        (0, -1, 0): (1 + 0j, 0j, 0j),
    }
    r = finite_galerkin_nonlinear_residual_hminus1(state, K=1)
    assert r["residual_hminus1_norm"] >= 0.0
    assert math.isfinite(r["residual_hminus1_norm"])
    assert r["residual_modes"] > 0
