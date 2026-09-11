"""Exact finite adapter from nondimensional readout certificates to declared physical units.

This module does not create a physical model.  It only converts an already-certified
finite inverse/tail statement once the caller explicitly declares the nondimensional
scales used by that model.

If

    t_phys = T0 * t,
    y_phys = Y0 * y,
    x_phys = X0 * x,

then a physical sensor radius sigma_phys corresponds to sigma=sigma_phys/Y0.  Given a
certified nondimensional inverse factor K, the retained coordinate radius is

    rho_coord = K * (sigma_phys + tau_phys) / Y0.

If a declared finite norm adapter Cret satisfies

    ||retained error|| <= Cret * ||coordinate error||_inf,

then

    rho_ret_phys = X0 * Cret * rho_coord.

If a separately certified nondimensional omitted-tail radius beta is supplied in the
same physical state norm, the exact squared physical completion bound is

    epsilon_phys^2 <= X0^2 * ((Cret*rho_coord)^2 + beta^2).

An outward rational square-root upper bound is returned as well.  No continuum tail is
manufactured: if beta is absent or not independently certified, the outer result is
HOLD while the inner physical radius remains available.
"""
from __future__ import annotations

import math
from fractions import Fraction


def _q(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def _positive(name: str, x) -> Fraction:
    q = _q(x)
    if q <= 0:
        raise ValueError(f"{name} must be positive")
    return q


def rational_sqrt_upper(x, *, decimal_digits: int = 18) -> Fraction:
    """Return an outward decimal-rational upper bound for sqrt(x)."""
    q = _q(x)
    if q < 0:
        raise ValueError("square-root argument must be nonnegative")
    if q == 0:
        return Fraction(0)
    if decimal_digits < 0:
        raise ValueError("decimal_digits must be nonnegative")
    scale = 10 ** decimal_digits
    target = q.numerator * scale * scale
    den = q.denominator
    m = math.isqrt(target // den)
    while m * m * den < target:
        m += 1
    return Fraction(m, scale)


def turnover_time_scale(*, length_scale, velocity_scale) -> Fraction:
    """Standard advective time scale T0=L/U."""
    L = _positive("length_scale", length_scale)
    U = _positive("velocity_scale", velocity_scale)
    return L / U


def physicalize_readout_certificate(
    *,
    sample_spacing_nondimensional,
    time_scale,
    observation_scale,
    state_scale,
    inverse_factor_nondimensional,
    sensor_radius_physical,
    forward_model_radius_physical=0,
    retained_norm_factor=1,
    tail_radius_nondimensional=None,
    tail_certified: bool = False,
    sqrt_decimal_digits: int = 18,
) -> dict:
    """Convert a finite nondimensional measurement certificate into physical units.

    The function is deliberately fail-closed for the outer completion.  ``tail_certified``
    must be true whenever ``tail_radius_nondimensional`` is used to report epsilon_phys.
    """
    h = _q(sample_spacing_nondimensional)
    if h <= 0:
        raise ValueError("sample_spacing_nondimensional must be positive")
    T0 = _positive("time_scale", time_scale)
    Y0 = _positive("observation_scale", observation_scale)
    X0 = _positive("state_scale", state_scale)
    K = _positive("inverse_factor_nondimensional", inverse_factor_nondimensional)
    Cret = _positive("retained_norm_factor", retained_norm_factor)
    sigma_phys = _q(sensor_radius_physical)
    tau_phys = _q(forward_model_radius_physical)
    if sigma_phys < 0 or tau_phys < 0:
        raise ValueError("physical uncertainty radii must be nonnegative")

    sigma = sigma_phys / Y0
    tau = tau_phys / Y0
    rho_coord = K * (sigma + tau)
    rho_ret = Cret * rho_coord
    rho_phys = X0 * rho_ret

    out = {
        "status": "INNER_CERTIFIED",
        "sample_spacing_nondimensional": h,
        "sample_spacing_physical": T0 * h,
        "time_scale": T0,
        "observation_scale": Y0,
        "state_scale": X0,
        "sensor_radius_physical": sigma_phys,
        "forward_model_radius_physical": tau_phys,
        "sensor_radius_nondimensional": sigma,
        "forward_model_radius_nondimensional": tau,
        "inverse_factor_nondimensional": K,
        "retained_norm_factor": Cret,
        "rho_coordinate_nondimensional": rho_coord,
        "rho_retained_nondimensional": rho_ret,
        "rho_retained_physical": rho_phys,
        "epsilon_physical_squared": None,
        "epsilon_physical_upper": None,
        "outer_status": "HOLD",
        "reason": "inner finite measurement radius converted using declared scales; outer completion requires a separately certified tail",
    }

    if tail_radius_nondimensional is None:
        return out

    beta = _q(tail_radius_nondimensional)
    if beta < 0:
        raise ValueError("tail_radius_nondimensional must be nonnegative")
    if not tail_certified:
        return {
            **out,
            "tail_radius_nondimensional": beta,
            "reason": "tail radius was supplied but not independently certified; outer completion remains HOLD",
        }

    eps2_nd = rho_ret * rho_ret + beta * beta
    eps2_phys = X0 * X0 * eps2_nd
    eps_phys = rational_sqrt_upper(eps2_phys, decimal_digits=sqrt_decimal_digits)
    return {
        **out,
        "status": "CERTIFIED",
        "tail_radius_nondimensional": beta,
        "tail_certified": True,
        "epsilon_nondimensional_squared": eps2_nd,
        "epsilon_physical_squared": eps2_phys,
        "epsilon_physical_upper": eps_phys,
        "outer_status": "CERTIFIED",
        "reason": "declared physical scales applied to a certified finite inverse radius and an independently certified tail radius",
    }
