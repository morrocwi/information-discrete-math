"""Discrete epsilon-completion diagnostics for finite Navier-Stokes mode records.

This module builds on :mod:`idm.ns_retained`; it does not create a second
Navier-Stokes solver.  The finite evolution remains the same direct
Fourier-Galerkin RK4 recurrence already implemented there.

Toledo proposal lineage (registered 2026-09-10):
- PROP-EPSC-01  nested readout consistency defect
- PROP-EPSC-02  NS Fourier boundary-energy diagnostic
- PROP-EPSC-03  fail-closed epsilon-completion acceptance gate
- PROP-EPSC-04  computable omitted-information tail certificate target (OPEN)

Claim scope
-----------
``finite_diagnostic`` unless a caller supplies a separately proved omitted-tail
bound.  Nested-cutoff agreement and small boundary energy do NOT by themselves
certify a continuum Navier-Stokes solution.
"""
from __future__ import annotations

import math
from typing import Callable, Iterable

from .ns_retained import cube_modes, full_rk4_step, triads_by_output

Mode = tuple[int, int, int]
Vec = tuple[complex, complex, complex]
State = dict[Mode, Vec]


def taylor_green_state(K: int) -> State:
    """Return Taylor-Green initial data directly as finite Fourier records."""
    modes = cube_modes(K)
    state: State = {k: (0j, 0j, 0j) for k in modes}
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                k = (sx, sy, sz)
                if k in state:
                    state[k] = (-1j * sx / 8.0, 1j * sy / 8.0, 0j)
    return state


def evolve_full_finite(
    state: State,
    *,
    K: int,
    nu: float,
    dt: float,
    steps: int,
) -> State:
    """Advance the existing finite Fourier-Galerkin RK4 recurrence."""
    if K < 1:
        raise ValueError("K must be >= 1")
    if nu < 0:
        raise ValueError("nu must be nonnegative")
    if dt <= 0:
        raise ValueError("dt must be positive")
    if steps < 0:
        raise ValueError("steps must be nonnegative")

    modes = cube_modes(K)
    triads = triads_by_output(modes)
    out = dict(state)
    for _ in range(steps):
        out = full_rk4_step(out, dt, nu, modes, triads)
    return out


def nested_readout_consistency_defect(
    coarse: State,
    fine: State,
) -> float:
    """PROP-EPSC-01: L2 disagreement on the shared finite mode records."""
    common = set(coarse).intersection(fine)
    if not common:
        raise ValueError("coarse and fine states have no shared modes")
    total = 0.0
    for k in common:
        a = coarse[k]
        b = fine[k]
        total += sum(abs(a[i] - b[i]) ** 2 for i in range(3))
    return math.sqrt(total)


def boundary_energy(state: State, K: int) -> float:
    """PROP-EPSC-02: energy on ||k||_infinity == K.

    This is a diagnostic proxy for unresolved activity, not a proved tail bound.
    """
    return 0.5 * sum(
        sum(abs(v[i]) ** 2 for i in range(3))
        for k, v in state.items()
        if max(abs(k[0]), abs(k[1]), abs(k[2])) == K
    )


def epsilon_completion_verdict(
    *,
    delta: float,
    epsilon: float,
    beta: float | None = None,
) -> dict:
    """PROP-EPSC-03: fail-closed certification verdict.

    ``beta`` is the proved omitted-information bound requested by PROP-EPSC-04.
    If it is absent, the function returns HOLD even when ``delta`` is tiny.
    """
    if epsilon < 0 or delta < 0:
        raise ValueError("epsilon and delta must be nonnegative")
    if beta is None:
        return {
            "status": "HOLD",
            "tier": "finite_diagnostic",
            "reason": "no proved omitted-information bound beta_K is available",
            "delta": float(delta),
            "beta": None,
            "epsilon": float(epsilon),
        }
    if beta < 0:
        raise ValueError("beta must be nonnegative")
    total = float(delta + beta)
    return {
        "status": "CERTIFIED" if total <= epsilon else "HOLD",
        "tier": "conditional_certificate",
        "reason": "delta_K + beta_K compared with the declared tolerance",
        "delta": float(delta),
        "beta": float(beta),
        "total_bound": total,
        "epsilon": float(epsilon),
    }


def nested_cutoff_diagnostic(
    *,
    K_values: Iterable[int] = (1, 2, 3),
    nu: float = 0.01,
    dt: float = 0.005,
    steps: int = 1,
    epsilon_delta: float = 1e-6,
    epsilon_boundary: float = 1e-8,
    consecutive_required: int = 2,
    initial_state_factory: Callable[[int], State] = taylor_green_state,
) -> dict:
    """Run the operational nested-cutoff diagnostic.

    Passing this diagnostic is NOT a continuum certificate.  It reports only
    finite nested agreement plus the finite boundary-energy proxy.  Use
    :func:`epsilon_completion_verdict` with a separately proved ``beta`` for a
    certification claim.
    """
    Ks = tuple(int(K) for K in K_values)
    if not Ks or any(K < 1 for K in Ks):
        raise ValueError("K_values must contain positive integers")
    if any(b <= a for a, b in zip(Ks, Ks[1:])):
        raise ValueError("K_values must be strictly increasing")
    if epsilon_delta < 0 or epsilon_boundary < 0:
        raise ValueError("diagnostic tolerances must be nonnegative")
    if consecutive_required < 1:
        raise ValueError("consecutive_required must be >= 1")

    rows = []
    previous = None
    consecutive = 0
    first_pass = None
    confirmed_K = None

    for K in Ks:
        initial = initial_state_factory(K)
        terminal = evolve_full_finite(initial, K=K, nu=nu, dt=dt, steps=steps)
        delta = None if previous is None else nested_readout_consistency_defect(previous, terminal)
        edge = boundary_energy(terminal, K)
        passes = bool(
            delta is not None
            and delta <= epsilon_delta
            and edge <= epsilon_boundary
        )

        if passes:
            consecutive += 1
            if first_pass is None:
                first_pass = K
            if consecutive >= consecutive_required and confirmed_K is None:
                confirmed_K = K
        else:
            consecutive = 0
            first_pass = None

        rows.append({
            "K": K,
            "mode_count": len(terminal),
            "delta_K": delta,
            "boundary_energy": edge,
            "diagnostic_pass": passes,
        })
        previous = terminal

    return {
        "status": "finite_diagnostic",
        "continuum_certificate": "HOLD",
        "reason": "PROP-EPSC-04 omitted-information bound is not supplied",
        "nu": nu,
        "dt": dt,
        "steps": steps,
        "epsilon_delta": epsilon_delta,
        "epsilon_boundary": epsilon_boundary,
        "consecutive_required": consecutive_required,
        "first_passing_K": first_pass if confirmed_K is not None else None,
        "confirmed_K": confirmed_K,
        "rows": rows,
        "toledo": ["PROP-EPSC-01", "PROP-EPSC-02", "PROP-EPSC-03", "PROP-EPSC-04"],
    }
