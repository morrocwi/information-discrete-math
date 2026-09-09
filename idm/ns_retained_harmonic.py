"""Exact real harmonic physical probe for finite retained Navier-Stokes RK4.

The physical readout is the periodic volume correlation

    Q(T) = < u(x,T) cos(k0.x + phase) >_x

which depends exactly on the conjugate Fourier pair +/-k0.  That gives a real,
physical-space linear measurement with terminal support of only two modes.
The pair is pulled backward through the exact RK4/NS triad dependency graph;
no closure is introduced.
"""
from __future__ import annotations

import cmath
import math

from . import ns_retained as NSR


def _pullback_step(triads, terminal):
    K4 = set(terminal)
    K3 = NSR.dependency_expand(triads, K4)
    K2 = NSR.dependency_expand(triads, K3)
    K1 = NSR.dependency_expand(triads, K2)
    S0 = NSR.dependency_expand(triads, K1)
    return S0


def _probe_readout(state, k0, phase):
    km = tuple(-x for x in k0)
    ep = cmath.exp(1j * phase)
    em = cmath.exp(-1j * phase)
    # <u cos(k0.x+phase)> = 1/2 (u_-k0 e^{i phase} + u_k0 e^{-i phase})
    out = []
    for j in range(3):
        out.append(0.5 * (state[km][j] * ep + state[k0][j] * em))
    return tuple(out)


def _vec_diff(a, b):
    return math.sqrt(sum(abs(a[j] - b[j]) ** 2 for j in range(3)))


def solve_harmonic_probe(
    *,
    K: int,
    nu: float,
    dt: float,
    horizon: int,
    wavevector,
    phase: float = 0.0,
    seed: int = 20260909,
    target_energy: float = 0.125,
    initial_state=None,
    verify: bool = True,
    max_K: int = 3,
    max_horizon: int = 3,
):
    if K < 1 or K > max_K:
        raise ValueError(f"K must be in 1..{max_K} for the portable API guard")
    if horizon < 1 or horizon > max_horizon:
        raise ValueError(f"horizon must be in 1..{max_horizon} for the portable API guard")
    if dt <= 0:
        raise ValueError("dt must be positive")
    if nu < 0:
        raise ValueError("nu must be nonnegative")

    k0 = tuple(int(x) for x in wavevector)
    if len(k0) != 3 or k0 == (0, 0, 0):
        raise ValueError("wavevector must be a nonzero integer 3-vector")

    modes = NSR.cube_modes(K)
    mode_set = set(modes)
    km = tuple(-x for x in k0)
    if k0 not in mode_set or km not in mode_set:
        raise ValueError("+/- wavevector must lie inside the retained Fourier cube")
    triads = NSR.triads_by_output(modes)
    terminal = {k0, km}

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

    value_complex = _probe_readout(state, k0, float(phase))
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
        full_value = _probe_readout(full, k0, float(phase))
        err = _vec_diff(value_complex, full_value)
        verification = {
            "target_abs_error": err,
            "gate": 1e-12,
            "status": "PASS" if err <= 1e-12 else "FAIL",
        }

    # Expose the terminal step's exact stage-cone sizes so readout design can be audited.
    K4 = set(terminal)
    K3 = NSR.dependency_expand(triads, K4)
    K2 = NSR.dependency_expand(triads, K3)
    K1 = NSR.dependency_expand(triads, K2)
    S0 = NSR.dependency_expand(triads, K1)

    return {
        "value": value_real,
        "wavevector": list(k0),
        "phase": float(phase),
        "mode_count": len(modes),
        "terminal_mode_count": 2,
        "readout_density": 2 / len(modes),
        "terminal_step_cone": {
            "input_modes": len(S0),
            "k1_modes": len(K1),
            "k2_modes": len(K2),
            "k3_modes": len(K3),
            "k4_modes": len(K4),
        },
        "horizon": horizon,
        "rk4_stage_ledger": ledger,
        "retained_triad_work": retained_work,
        "full_triad_work": full_work,
        "structural_work_reduction": (
            float(full_work) / retained_work if retained_work else float("inf")
        ),
        "verification": verification,
        "imaginary_residual": imag_residual,
        "compression_status": "SPARSE_EXACT_RETAINED",
        "backend": "portable_direct_retained",
        "readout_identity": (
            "real cosine volume correlation reads exactly the conjugate Fourier pair +/-wavevector"
        ),
        "claim_scope": (
            "task-exact real harmonic volume correlation relative to the same fixed finite Fourier-Galerkin RK4 recurrence"
        ),
    }
