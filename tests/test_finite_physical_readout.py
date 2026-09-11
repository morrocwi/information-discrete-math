from fractions import Fraction

from idm.finite_physical_readout import (
    physicalize_readout_certificate,
    rational_sqrt_upper,
    turnover_time_scale,
)


def test_turnover_time_scale():
    assert turnover_time_scale(length_scale=2, velocity_scale=4) == Fraction(1, 2)


def test_inner_sensor_to_physical_rho_without_tail():
    out = physicalize_readout_certificate(
        sample_spacing_nondimensional=Fraction(1, 20),
        time_scale=Fraction(2),
        observation_scale=Fraction(25),
        state_scale=Fraction(5),
        inverse_factor_nondimensional=Fraction(3),
        sensor_radius_physical=Fraction(1, 100),
        forward_model_radius_physical=Fraction(1, 200),
        retained_norm_factor=Fraction(2),
    )
    assert out["sample_spacing_physical"] == Fraction(1, 10)
    assert out["sensor_radius_nondimensional"] == Fraction(1, 2500)
    assert out["forward_model_radius_nondimensional"] == Fraction(1, 5000)
    assert out["rho_coordinate_nondimensional"] == Fraction(9, 5000)
    assert out["rho_retained_nondimensional"] == Fraction(9, 2500)
    assert out["rho_retained_physical"] == Fraction(9, 500)
    assert out["outer_status"] == "HOLD"
    assert out["epsilon_physical_upper"] is None


def test_outer_rho_beta_to_physical_epsilon():
    out = physicalize_readout_certificate(
        sample_spacing_nondimensional=Fraction(1, 10),
        time_scale=1,
        observation_scale=1,
        state_scale=2,
        inverse_factor_nondimensional=2,
        sensor_radius_physical=Fraction(1, 100),
        retained_norm_factor=3,
        tail_radius_nondimensional=Fraction(1, 50),
        tail_certified=True,
        sqrt_decimal_digits=12,
    )
    # rho_coord=1/50, rho_ret=3/50, beta=1/50.
    assert out["epsilon_nondimensional_squared"] == Fraction(1, 250)
    assert out["epsilon_physical_squared"] == Fraction(2, 125)
    assert out["epsilon_physical_upper"] ** 2 >= out["epsilon_physical_squared"]
    assert out["status"] == "CERTIFIED"
    assert out["outer_status"] == "CERTIFIED"


def test_uncertified_tail_fails_closed():
    out = physicalize_readout_certificate(
        sample_spacing_nondimensional=Fraction(1, 10),
        time_scale=1,
        observation_scale=1,
        state_scale=1,
        inverse_factor_nondimensional=1,
        sensor_radius_physical=0,
        tail_radius_nondimensional=Fraction(1, 10),
        tail_certified=False,
    )
    assert out["outer_status"] == "HOLD"
    assert out["epsilon_physical_upper"] is None


def test_sqrt_upper_is_outward():
    r = rational_sqrt_upper(Fraction(2), decimal_digits=8)
    assert r * r >= 2
    assert (r - Fraction(1, 10**8)) ** 2 < 2
