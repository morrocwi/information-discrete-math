"""Finite observability -> continuum EPSC composition helpers.

This module deliberately separates three levels:

1. structural observability of a finite Fourier-Galerkin state;
2. a *certified* retained-state reconstruction radius ``rho``;
3. an independently certified omitted-tail radius ``beta``.

Rank saturation alone does not manufacture ``rho``.  The fail-closed composition
implemented here only returns a continuum certificate when both directional
inputs are supplied and finite.

For an orthogonal Fourier split P_N + Q_N and a reconstructed P_N-supported
state x_hat, if

    inf_g ||P_N u - g x_hat||_2 <= rho
    ||Q_N u||_2 <= beta,

where g belongs to an isometric symmetry group preserving P_N, then

    inf_g ||u - g x_hat||_2 <= sqrt(rho^2 + beta^2).

The Navier-Stokes energy-observability application uses spatial translations as
the symmetry group.  This is a finite/functional-analytic composition rule, not
a global injectivity, regularity, or Clay Millennium claim.
"""
from __future__ import annotations

import math


def _positive_int(name: str, value: int) -> int:
    value = int(value)
    if value < 1:
        raise ValueError(f"{name} must be at least 1")
    return value


def _nonnegative(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return value


def state_dimension(N: int) -> int:
    """Declared real phase-space dimension d_N=2((2N+1)^3-1)."""
    N = _positive_int("N", N)
    return 2 * ((2 * N + 1) ** 3 - 1)


def shell_squared_radii(N: int) -> tuple[int, ...]:
    """Distinct |k|^2 shell labels in the cubic cutoff, excluding k=0."""
    N = _positive_int("N", N)
    radii = set()
    for i in range(-N, N + 1):
        for j in range(-N, N + 1):
            for k in range(-N, N + 1):
                if (i, j, k) != (0, 0, 0):
                    radii.add(i * i + j * j + k * k)
    return tuple(sorted(radii))


def shell_count(N: int) -> int:
    return len(shell_squared_radii(N))


def scalar_energy_min_depth(N: int) -> int:
    """Earliest structurally possible scalar-energy saturation order."""
    return state_dimension(N) - 4


def shell_energy_min_depth(N: int) -> int:
    """Earliest structurally possible shell-energy saturation order."""
    d = state_dimension(N)
    m = shell_count(N)
    if m <= 1:
        raise ValueError("shell reader needs at least two distinct shells")
    return math.ceil((d - 3 - m) / (m - 1))


def scalar_energy_rank_ceiling(N: int, R: int) -> int:
    N = _positive_int("N", N)
    R = int(R)
    if R < 0:
        raise ValueError("R must be nonnegative")
    return min(R + 1, state_dimension(N) - 3)


def shell_energy_rank_ceiling(N: int, R: int) -> int:
    N = _positive_int("N", N)
    R = int(R)
    if R < 0:
        raise ValueError("R must be nonnegative")
    d = state_dimension(N)
    m = shell_count(N)
    return min(m + (m - 1) * R, d - 3)


def observable_to_continuum_radius(*, retained_radius: float, tail_beta: float) -> float:
    """Orthogonal composition sqrt(rho^2+beta^2)."""
    rho = _nonnegative("retained_radius", retained_radius)
    beta = _nonnegative("tail_beta", tail_beta)
    return math.hypot(rho, beta)


def observable_to_continuum_verdict(
    *,
    retained_radius: float | None,
    tail_beta: float | None,
    epsilon: float,
) -> dict:
    """Fail-closed composition gate for a declared L2 quotient-state target.

    ``retained_radius`` must already be a certified finite-state reconstruction
    radius modulo the declared symmetry.  A rank test or an unqualified point
    estimate is not accepted as a substitute.
    """
    eps = _nonnegative("epsilon", epsilon)
    if retained_radius is None:
        return {
            "status": "HOLD",
            "radius": None,
            "reason": "certified retained-state reconstruction radius is missing",
            "tier": "conditional_certificate",
        }
    if tail_beta is None:
        return {
            "status": "HOLD",
            "radius": None,
            "reason": "certified omitted-tail beta is missing",
            "tier": "conditional_certificate",
        }
    radius = observable_to_continuum_radius(
        retained_radius=retained_radius,
        tail_beta=tail_beta,
    )
    return {
        "status": "CERTIFIED" if radius <= eps else "HOLD",
        "radius": radius,
        "epsilon": eps,
        "retained_radius": float(retained_radius),
        "tail_beta": float(tail_beta),
        "reason": (
            "orthogonal retained/tail composition is within tolerance"
            if radius <= eps
            else "certified radius exceeds requested tolerance"
        ),
        "tier": "conditional_certificate",
        "scope": "L2 state modulo a declared isometric symmetry preserving the cutoff",
    }
