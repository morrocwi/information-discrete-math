import math

from idm.ns_tail_certificate import (
    conditional_hs_tail_beta,
    finite_spectral_tail_and_hs,
    leray_forced_spacetime_tail_beta,
    leray_unforced_spacetime_tail_beta,
    lipschitz_readout_tail_beta,
    omitted_wavenumber_floor,
    terminal_nonidentifiability_witness,
    time_average_tail_beta,
)


def test_omitted_wavenumber_floor_for_cube():
    assert omitted_wavenumber_floor(0) == 1.0
    assert omitted_wavenumber_floor(4) == 5.0
    assert omitted_wavenumber_floor(4, kappa0=2.0) == 10.0


def test_finite_spectral_tail_inequality():
    state = {
        (1, 0, 0): (0j, 2 + 0j, 0j),
        (2, 1, 0): (1 + 1j, 0j, 0j),
        (4, 0, 0): (0j, 3 + 0j, 0j),
        (-4, 0, 0): (0j, 3 + 0j, 0j),
    }
    r = finite_spectral_tail_and_hs(state, K=2, s=1.0)
    assert r["passes"] is True
    assert r["actual_tail_l2"] == math.sqrt(18.0)
    assert r["bound"] >= r["actual_tail_l2"]


def test_unforced_leray_beta_decays_exactly_like_inverse_cutoff():
    b4 = leray_unforced_spacetime_tail_beta(K=4, nu=0.01, initial_l2_norm=2.0)
    b9 = leray_unforced_spacetime_tail_beta(K=9, nu=0.01, initial_l2_norm=2.0)
    assert math.isclose(b4 / b9, 2.0, rel_tol=1e-14)
    assert math.isclose(b4, 2.0 / (math.sqrt(0.02) * 5.0), rel_tol=1e-14)


def test_forced_leray_beta_formula():
    b = leray_forced_spacetime_tail_beta(
        K=3,
        nu=0.5,
        initial_l2_norm=2.0,
        forcing_l2_hminus1_norm=1.0,
    )
    expected = math.sqrt(4.0 / 0.5 + 1.0 / 0.25) / 4.0
    assert math.isclose(b, expected, rel_tol=1e-14)


def test_conditional_terminal_hs_certificate():
    assert conditional_hs_tail_beta(K=4, hs_norm_bound=10.0, s=1.0) == 2.0
    assert conditional_hs_tail_beta(K=4, hs_norm_bound=25.0, s=2.0) == 1.0


def test_time_average_and_readout_lifts():
    assert time_average_tail_beta(spacetime_beta=6.0, duration=9.0) == 2.0
    assert lipschitz_readout_tail_beta(state_beta=2.0, lipschitz_constant=3.5) == 7.0


def test_terminal_nonidentifiability_witness_is_outside_cutoff_and_scalable():
    a = terminal_nonidentifiability_witness(K=4, amplitude=1.0)
    b = terminal_nonidentifiability_witness(K=4, amplitude=10.0)
    assert max(abs(x) for x in a["q"]) == 5
    assert a["retained_projection_change_l2"] == 0.0
    assert a["divergence_free"] is True
    assert math.isclose(b["coefficient_tail_l2"] / a["coefficient_tail_l2"], 10.0)
