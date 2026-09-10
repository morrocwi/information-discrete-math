"""Energy-transfer observability helpers for finite Fourier-Galerkin Navier-Stokes.

This module deliberately separates exact finite balance algebra from the still-open
problem of a certified inverse for the full Fourier state.  It does not infer a
continuum state from energy data and it does not identify informational language
with SI energy without a domain adapter.

For a prescribed/unforced finite shell-energy balance

    dI_s/dt = T_s - 2 nu s I_s + F_s,

the transfer vector is algebraically recoverable from the first energy jet.  The
same identity can be integrated over a time window to avoid differentiating noisy
measurements.  A small analytic triad subcase also admits an explicit quantitative
inverse for its four reduced invariants; that subcase is a witness for the broader
EPSC-18/19 programme, not a solution of the full-cube inverse problem.
"""
from __future__ import annotations

import math
from typing import Sequence


def _nonnegative(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return value


def _same_length(*seqs: Sequence[float]) -> int:
    n = len(seqs[0])
    if any(len(s) != n for s in seqs[1:]):
        raise ValueError("all shell arrays must have the same length")
    return n


def shell_transfer_from_jet(
    shell_energy: Sequence[float],
    shell_energy_derivative: Sequence[float],
    *,
    viscosity: float,
    shell_squared_radii: Sequence[int],
    shell_forcing: Sequence[float] | None = None,
) -> tuple[float, ...]:
    """Recover T from dI/dt = T - 2 nu s I + F.

    ``shell_forcing`` must be a known additive shell-energy input.  An uncertain or
    state-dependent forcing term requires its own certified enclosure and must not
    be silently treated as exact data.
    """
    nu = _nonnegative("viscosity", viscosity)
    n = _same_length(shell_energy, shell_energy_derivative, shell_squared_radii)
    if shell_forcing is None:
        shell_forcing = [0.0] * n
    _same_length(shell_energy, shell_forcing)
    out = []
    for I, dI, s, F in zip(
        shell_energy, shell_energy_derivative, shell_squared_radii, shell_forcing
    ):
        s = int(s)
        if s < 1:
            raise ValueError("shell squared radii must be positive integers")
        out.append(float(dI) + 2.0 * nu * s * float(I) - float(F))
    return tuple(out)


def integrated_shell_transfer(
    start_energy: Sequence[float],
    end_energy: Sequence[float],
    energy_time_integral: Sequence[float],
    *,
    viscosity: float,
    shell_squared_radii: Sequence[int],
    forcing_time_integral: Sequence[float] | None = None,
) -> tuple[float, ...]:
    """Compute integral T_s dt without differentiating the energy data.

    The exact balance identity is

        integral T_s dt
          = I_s(t1)-I_s(t0) + 2 nu s integral I_s dt - integral F_s dt.
    """
    nu = _nonnegative("viscosity", viscosity)
    n = _same_length(
        start_energy, end_energy, energy_time_integral, shell_squared_radii
    )
    if forcing_time_integral is None:
        forcing_time_integral = [0.0] * n
    _same_length(start_energy, forcing_time_integral)
    return tuple(
        float(I1)
        - float(I0)
        + 2.0 * nu * int(s) * float(Iint)
        - float(Fint)
        for I0, I1, Iint, s, Fint in zip(
            start_energy,
            end_energy,
            energy_time_integral,
            shell_squared_radii,
            forcing_time_integral,
        )
    )


def integrated_shell_transfer_radius(
    start_energy_radius: Sequence[float],
    end_energy_radius: Sequence[float],
    energy_integral_radius: Sequence[float],
    *,
    viscosity: float,
    shell_squared_radii: Sequence[int],
    forcing_integral_radius: Sequence[float] | None = None,
) -> tuple[float, ...]:
    """Propagate certified interval radii through the integrated balance."""
    nu = _nonnegative("viscosity", viscosity)
    n = _same_length(
        start_energy_radius,
        end_energy_radius,
        energy_integral_radius,
        shell_squared_radii,
    )
    if forcing_integral_radius is None:
        forcing_integral_radius = [0.0] * n
    _same_length(start_energy_radius, forcing_integral_radius)
    return tuple(
        _nonnegative("start_energy_radius", r0)
        + _nonnegative("end_energy_radius", r1)
        + 2.0 * nu * int(s) * _nonnegative("energy_integral_radius", rI)
        + _nonnegative("forcing_integral_radius", rF)
        for r0, r1, rI, s, rF in zip(
            start_energy_radius,
            end_energy_radius,
            energy_integral_radius,
            shell_squared_radii,
            forcing_integral_radius,
        )
    )


def triad_reduced_r_estimate(
    *,
    shell_energy_x: float,
    shell_energy_derivative_a: float,
    viscosity: float = 1.0 / 200.0,
) -> float:
    """Explicit inverse for the repository's analytic three-mode subcase.

    For a=(1,0,0), c_a=3/10 and |a|^2=1,

        J1_a = 2 c_a r - 2 nu x,

    hence r=(J1_a+2 nu x)/(2 c_a).
    """
    nu = _nonnegative("viscosity", viscosity)
    c_a = 3.0 / 10.0
    return (
        float(shell_energy_derivative_a) + 2.0 * nu * float(shell_energy_x)
    ) / (2.0 * c_a)


def triad_reduced_r_radius(
    *,
    shell_energy_x_radius: float,
    shell_energy_derivative_a_radius: float,
    viscosity: float = 1.0 / 200.0,
) -> float:
    """Certified absolute-error radius for the reduced-triad r inverse."""
    nu = _nonnegative("viscosity", viscosity)
    sx = _nonnegative("shell_energy_x_radius", shell_energy_x_radius)
    sj = _nonnegative(
        "shell_energy_derivative_a_radius", shell_energy_derivative_a_radius
    )
    c_a = 3.0 / 10.0
    return (sj + 2.0 * nu * sx) / (2.0 * abs(c_a))


def boundary_old_triad_witness(k: tuple[int, int, int], N: int):
    """Construct a non-collinear old-mode triad witness for every boundary mode.

    For N>=2 and ||k||_infinity=N, return p in K_{N-1} and q in K_N such
    that p+q=k and p,q are non-collinear.  This is a kinematic coupling lemma:
    it does not prove observability-rank saturation or nonzero transfer at every
    state, because amplitudes and cancellations still matter.
    """
    N = int(N)
    if N < 2:
        raise ValueError("N must be at least 2")
    if k == (0, 0, 0) or max(abs(v) for v in k) != N:
        raise ValueError("k must be a nonzero boundary mode with ||k||_infinity=N")

    i = next(j for j, v in enumerate(k) if abs(v) == N)
    p_list = [0, 0, 0]
    transverse = any(k[j] != 0 for j in range(3) if j != i)
    if transverse:
        p_list[i] = 1 if k[i] > 0 else -1
    else:
        p_list[(i + 1) % 3] = 1

    p = tuple(p_list)
    q = tuple(k[j] - p[j] for j in range(3))
    cross = (
        p[1] * q[2] - p[2] * q[1],
        p[2] * q[0] - p[0] * q[2],
        p[0] * q[1] - p[1] * q[0],
    )

    assert max(abs(v) for v in p) <= N - 1
    assert q != (0, 0, 0) and max(abs(v) for v in q) <= N
    assert tuple(p[j] + q[j] for j in range(3)) == k
    assert cross != (0, 0, 0)
    return p, q
