"""Exact sparse physical plane-average readout for finite retained Navier-Stokes RK4.

For a periodic Fourier field and a plane normal to axis a, averaging over the
other two coordinates annihilates every mode except modes parallel to a:

    u_bar_a(s,T) = sum_{k_parallel_a} u_hat_k(T) exp(i k_a s).

Hence the terminal reader is sparse: 2K modes out of (2K+1)^3-1 for the
zero-mean cube used by the portable solver.  The terminal support is pulled
back through the exact RK4 stage dependency DAG using the same NS triads as
idm.ns_retained.  No closure is introduced.

Claim scope is finite_diagnostic and relative to the same fixed finite
Fourier-Galerkin RK4 recurrence.  No continuum claim is made.
"""
from __future__ import annotations

import cmath
import math

from . import ns_retained as NSR


_AXIS = {"x": 0, "y": 1, "z": 2}


def _plane_modes(modes, axis: str):
    ai = _AXIS[axis]
    out = []
    for k in modes:
        if all(k[j] == 0 for j in range(3) if j != ai):
            out.append(k)
    return out


def _pullback_step(triads, terminal):
    K4 = set(terminal)
    K3 = NSR.dependency_expand(triads, K4)
    K2 = NSR.dependency_expand(triads, K3)
    K1 = NSR.dependency_expand(triads, K2)
    S0 = NSR.dependency_expand(triads, K1)
    return S0


def _plane_readout(state, terminal_modes, axis: str, coordinate: float):
    ai = _AXIS[axis]
    value = [0j, 0j, 0j]
    for k in terminal_modes:
        phase = cmath.exp(1j * k[ai] * coordinate)
        u = state[k]
        for j in range(3):
            value[j] += u[j] * phase
    return tuple(value)


def _vec_diff(a, b):
    return math.sqrt(sum(abs(a[j] - b[j]) ** 2 for j in range(3)))


def solve_plane_average_velocity(
    *,
    K: int,
    nu: float,
    dt: float,
    horizon: int,
    axis: str = "x",
    coordinate: float = 0.0,
    seed: int = 20260909,
    target_energy: float = 0.125,
    initial_state=None,
    verify: bool = True,
    max_K: int = 3,
    max_horizon: int = 3,
):
    axis = str(axis).strip().lower()
    if axis not in _AXIS:
        raise ValueError("axis must be one of x, y, z")
    if K < 1 or K > max_K:
        raise ValueError(f"K must be in 1..{max_K} for the portable API guard")
    if horizon < 1 or horizon > max_horizon:
        raise ValueError(f"horizon must be in 1..{max_horizon} for the portable API guard")
    if dt <= 0:
        raise ValueError("dt must be positive")
    if nu < 0:
        raise ValueError("nu must be nonnegative")

    modes = NSR.cube_modes(K)
    triads = NSR.triads_by_output(modes)
    terminal_modes = _plane_modes(modes, axis)
    terminal = set(terminal_modes)
    if not terminal:
        raise ValueError("plane reader has empty terminal support")

    state = (
        NSR.parse_state(modes, initial_state)
        if initial_state is not None
        else NSR.deterministic_state(modes, seed=seed, target_energy=target_energy)
    )
    full_initial = dict(state)

    step_terminals = [None] * horizon
    needed = set(terminal)
    for n in range(horizon - 1, -1, -1):
        step_terminals[n] = set(needed)
        needed = _pullback_step(triads, needed)

    ledger = []
    for n in range(horizon):
        state, info, _ = NSR.retained_rk4_step(
            state, dt, nu, triads, step_terminals[n]
        )
        ledger.append(info)

    value_complex = _plane_readout(state, terminal_modes, axis, coordinate)
    value_real = tuple(v.real for v in value_complex)
    imag_residual = max(abs(v.imag) for v in value_complex)

    full_triad_per_rhs = sum(len(triads[k]) for k in modes)
    full_work = 4 * horizon * full_triad_per_rhs
    retained_work = sum(row["triad_work"] for row in ledger)

    verification = None
    if verify:
        full = full_initial
        for _ in range(horizon):
            full = NSR.full_rk4_step(full, dt, nu, modes, triads)
        full_value = _plane_readout(full, terminal_modes, axis, coordinate)
        err = _vec_diff(value_complex, full_value)
        verification = {
            "target_abs_error": err,
            "gate": 1e-12,
            "status": "PASS" if err <= 1e-12 else "FAIL",
        }

    # Every retained terminal mode is parallel to the plane normal.  Leray
    # incompressibility therefore forces the velocity component along that
    # normal to zero, up to floating arithmetic residual.
    longitudinal_residual = abs(value_complex[_AXIS[axis]])

    return {
        "value": value_real,
        "axis": axis,
        "coordinate": float(coordinate),
        "mode_count": len(modes),
        "terminal_mode_count": len(terminal_modes),
        "readout_density": len(terminal_modes) / len(modes),
        "horizon": horizon,
        "rk4_stage_ledger": ledger,
        "retained_triad_work": retained_work,
        "full_triad_work": full_work,
        "structural_work_reduction": (
            float(full_work) / retained_work if retained_work else float("inf")
        ),
        "verification": verification,
        "imaginary_residual": imag_residual,
        "longitudinal_residual": longitudinal_residual,
        "compression_status": "SPARSE_EXACT_RETAINED",
        "backend": "portable_direct_retained",
        "readout_identity": (
            "plane average annihilates all Fourier modes not parallel to the plane normal"
        ),
        "claim_scope": (
            "task-exact plane-average velocity relative to the same fixed finite Fourier-Galerkin RK4 recurrence"
        ),
    }
