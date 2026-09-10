"""A-posteriori terminal Fourier-tail certificates from the NS energy budget.

This module complements ``idm.ns_tail_certificate``.

For an unforced Leray--Hopf solution on the periodic torus, let P_K be the
retained Fourier projection.  The energy inequality implies

    ||(I-P_K)u(T)||_2^2
      <= ||u_0||_2^2
         - ||P_K u(T)||_2^2
         - 2 nu int_0^T ||grad P_K u||_2^2 dt.

The right-hand side is computable from finite retained records IF the terminal
retained norm and accumulated retained dissipation are exact or certified
lower bounds for the actual continuum projection.  Values produced by an
uncertified Galerkin surrogate must not be silently substituted.

If the solution satisfies energy equality, this bound tends to zero as K grows.
For a general Leray--Hopf solution, the limiting floor of this particular bound
is the energy-inequality slack; the actual Fourier tail still tends to zero,
but this energy-budget certificate alone may stop shrinking.

Claim tier: standard analytic consequence of the Leray--Hopf energy inequality
(Dr until separately formalised).  This is not a Navier--Stokes regularity or
uniqueness theorem.
"""
from __future__ import annotations

import math


def _nonnegative(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return value


def leray_terminal_energy_budget_beta(
    *,
    K: int,
    initial_l2_norm_upper: float,
    retained_terminal_l2_norm_lower: float,
    resolved_viscous_dissipation_lower: float,
    consistency_tolerance: float = 1e-12,
) -> dict:
    """Return a fail-closed terminal L2-tail bound for unforced Leray--Hopf NS.

    Inputs are *certified directional bounds*:

    - ``initial_l2_norm_upper`` >= ||u_0||_2;
    - ``retained_terminal_l2_norm_lower`` <= ||P_K u(T)||_2;
    - ``resolved_viscous_dissipation_lower`` <=
          nu * int_0^T ||grad P_K u(t)||_2^2 dt.

    Then

      tail^2 <= U0^2 - L_K(T)^2 - 2 D_K.

    A negative radicand beyond tolerance means the supplied certificates are
    mutually inconsistent; the function returns HOLD rather than clamping the
    result to zero.
    """
    K = int(K)
    if K < 0:
        raise ValueError("K must be nonnegative")
    U0 = _nonnegative("initial_l2_norm_upper", initial_l2_norm_upper)
    LK = _nonnegative(
        "retained_terminal_l2_norm_lower", retained_terminal_l2_norm_lower
    )
    DK = _nonnegative(
        "resolved_viscous_dissipation_lower", resolved_viscous_dissipation_lower
    )
    tol = _nonnegative("consistency_tolerance", consistency_tolerance)

    radicand = U0 * U0 - LK * LK - 2.0 * DK
    scale = max(1.0, U0 * U0, LK * LK, 2.0 * DK)
    if radicand < -tol * scale:
        return {
            "status": "HOLD",
            "tier": "conditional_certificate",
            "K": K,
            "beta": None,
            "tail_squared_upper": None,
            "raw_radicand": radicand,
            "reason": (
                "inconsistent directional certificates: retained terminal "
                "energy plus certified resolved dissipation exceeds the "
                "declared initial-energy upper budget"
            ),
        }

    safe_radicand = max(0.0, radicand)
    return {
        "status": "CERTIFIED_BOUND",
        "tier": "conditional_certificate",
        "K": K,
        "beta": math.sqrt(safe_radicand),
        "tail_squared_upper": safe_radicand,
        "raw_radicand": radicand,
        "reason": (
            "Leray-Hopf energy inequality minus certified retained terminal "
            "energy and certified retained viscous dissipation"
        ),
        "input_contract": {
            "initial_l2_norm_upper": U0,
            "retained_terminal_l2_norm_lower": LK,
            "resolved_viscous_dissipation_lower": DK,
        },
    }


def energy_defect_floor(
    *,
    initial_l2_norm: float,
    terminal_l2_norm: float,
    total_viscous_dissipation: float,
) -> float:
    """Energy-inequality slack in squared-L2 units.

    ``total_viscous_dissipation`` means
        nu * int_0^T ||grad u||_2^2 dt.

    For an unforced Leray--Hopf solution the returned value is nonnegative:

        defect = ||u0||^2 - ||u(T)||^2 - 2 D_total.

    Under energy equality the defect is zero.  The asymptotic floor of the
    energy-budget beta^2 is this defect when exact projections are used.

    Floating-point inputs that satisfy energy equality algebraically can leave
    a few ulps of positive or negative cancellation residue.  We therefore use
    the same scale-aware consistency tolerance on both sides of zero: a defect
    whose magnitude is at most ``1e-12 * scale`` is returned as exact ``0.0``.
    This is numerical hygiene only; a materially negative budget still raises.
    """
    u0 = _nonnegative("initial_l2_norm", initial_l2_norm)
    uT = _nonnegative("terminal_l2_norm", terminal_l2_norm)
    D = _nonnegative("total_viscous_dissipation", total_viscous_dissipation)
    defect = u0 * u0 - uT * uT - 2.0 * D
    scale = max(1.0, u0 * u0, uT * uT, 2.0 * D)
    tol = 1e-12 * scale
    if defect < -tol:
        raise ValueError("inputs violate the unforced energy-inequality budget")
    if abs(defect) <= tol:
        return 0.0
    return defect