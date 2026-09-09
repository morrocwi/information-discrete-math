"""Portable finite task-conditioned Fourier-Galerkin Navier-Stokes RK4.

This module is deliberately standard-library only so it can live inside the IDM
core solver. It implements the same finite triad-dependency pullback used by
the executable NS retained-fold benchmark, but does not claim the benchmark's
NumPy timing speedups.

Claim scope:
- fixed finite Fourier cube {-K,...,K}^3 minus {0};
- unforced incompressible Fourier-Galerkin Navier-Stokes recurrence;
- classical explicit RK4;
- terminal readout = one Fourier velocity mode;
- task exactness is relative to the same finite RK4 recurrence.

No learned closure and no continuum regularity/singularity claim.
"""
from __future__ import annotations

import math
import random
from typing import Iterable

Mode = tuple[int, int, int]
Vec = tuple[complex, complex, complex]


def cube_modes(K: int) -> list[Mode]:
    return [
        (i, j, k)
        for i in range(-K, K + 1)
        for j in range(-K, K + 1)
        for k in range(-K, K + 1)
        if (i, j, k) != (0, 0, 0)
    ]


def triads_by_output(modes: Iterable[Mode]) -> dict[Mode, tuple[tuple[Mode, Mode], ...]]:
    modes = list(modes)
    mode_set = set(modes)
    out = {}
    for k in modes:
        pairs = []
        for p in modes:
            q = (k[0] - p[0], k[1] - p[1], k[2] - p[2])
            if q in mode_set:
                pairs.append((p, q))
        out[k] = tuple(pairs)
    return out


def dependency_expand(
    triads: dict[Mode, tuple[tuple[Mode, Mode], ...]],
    outputs: Iterable[Mode],
) -> set[Mode]:
    """One exact triad dependency pullback D(S)."""
    outputs = tuple(outputs)
    out = set(outputs)
    for k in outputs:
        for p, q in triads[k]:
            out.add(p)
            out.add(q)
    return out


def _vadd(a: Vec, b: Vec) -> Vec:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _vscale(c: complex, a: Vec) -> Vec:
    return (c * a[0], c * a[1], c * a[2])


def _vdot_real_k(k: Mode, a: Vec) -> complex:
    return k[0] * a[0] + k[1] * a[1] + k[2] * a[2]


def _project(a: Vec, k: Mode) -> Vec:
    k2 = k[0] * k[0] + k[1] * k[1] + k[2] * k[2]
    dot = _vdot_real_k(k, a)
    return (
        a[0] - k[0] * dot / k2,
        a[1] - k[1] * dot / k2,
        a[2] - k[2] * dot / k2,
    )


def _canonical_half(k: Mode) -> bool:
    for x in k:
        if x > 0:
            return True
        if x < 0:
            return False
    return False


def deterministic_state(
    modes: list[Mode],
    seed: int = 20260909,
    target_energy: float = 0.125,
) -> dict[Mode, Vec]:
    """Deterministic real-field (conjugate-symmetric), divergence-free state."""
    rng = random.Random(seed)
    mode_set = set(modes)
    state: dict[Mode, Vec] = {k: (0j, 0j, 0j) for k in modes}
    done: set[Mode] = set()

    for k in modes:
        if k in done or not _canonical_half(k):
            continue
        neg = (-k[0], -k[1], -k[2])
        if neg not in mode_set:
            raise ValueError("mode cube is not conjugate symmetric")
        z = tuple(
            complex(rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0))
            for _ in range(3)
        )
        zp = _project(z, k)  # type: ignore[arg-type]
        state[k] = zp
        state[neg] = (zp[0].conjugate(), zp[1].conjugate(), zp[2].conjugate())
        done.add(k)
        done.add(neg)

    energy = 0.5 * sum(
        abs(v[0]) ** 2 + abs(v[1]) ** 2 + abs(v[2]) ** 2
        for v in state.values()
    )
    if energy <= 0:
        raise ValueError("generated zero-energy state")
    scale = math.sqrt(target_energy / energy)
    return {k: _vscale(scale, v) for k, v in state.items()}


def _decode_complex(z) -> complex:
    if isinstance(z, (int, float)):
        return complex(z)
    if isinstance(z, (list, tuple)) and len(z) == 2:
        return complex(float(z[0]), float(z[1]))
    if isinstance(z, dict) and "re" in z and "im" in z:
        return complex(float(z["re"]), float(z["im"]))
    raise ValueError("complex component must be number, [re,im], or {re,im}")


def parse_state(modes: list[Mode], rows) -> dict[Mode, Vec]:
    """Parse JSON-friendly rows [{k:[...],u:[[re,im],...]}]."""
    state = {k: (0j, 0j, 0j) for k in modes}
    mode_set = set(modes)
    for row in rows:
        k = tuple(int(x) for x in row["k"])
        if len(k) != 3 or k not in mode_set:
            raise ValueError(f"state mode {k} outside retained cube")
        u = row["u"]
        if len(u) != 3:
            raise ValueError("each velocity mode needs 3 complex components")
        state[k] = (_decode_complex(u[0]), _decode_complex(u[1]), _decode_complex(u[2]))
    return state


def rhs_selected(
    state: dict[Mode, Vec],
    outputs: Iterable[Mode],
    triads: dict[Mode, tuple[tuple[Mode, Mode], ...]],
    nu: float,
) -> dict[Mode, Vec]:
    """Direct ordered-triad Galerkin RHS for named output modes."""
    out = {}
    for k in outputs:
        conv: Vec = (0j, 0j, 0j)
        for p, q in triads[k]:
            up = state[p]
            uq = state[q]
            qdot = _vdot_real_k(q, up)
            term = _vscale(1j * qdot, uq)
            conv = _vadd(conv, term)
        conv = _project(conv, k)
        k2 = k[0] * k[0] + k[1] * k[1] + k[2] * k[2]
        visc = _vscale(-nu * k2, state[k])
        out[k] = _vadd(_vscale(-1.0, conv), visc)
    return out


def _state_with_increment(
    state: dict[Mode, Vec],
    deriv: dict[Mode, Vec],
    factor: float,
) -> dict[Mode, Vec]:
    out = dict(state)
    for k, dv in deriv.items():
        out[k] = _vadd(state[k], _vscale(factor, dv))
    return out


def _rk4_pullback_sets(triads, terminal: set[Mode]):
    K4 = set(terminal)
    K3 = dependency_expand(triads, K4)
    K2 = dependency_expand(triads, K3)
    K1 = dependency_expand(triads, K2)
    S0 = dependency_expand(triads, K1)
    return S0, K1, K2, K3, K4


def retained_rk4_step(
    state: dict[Mode, Vec],
    dt: float,
    nu: float,
    triads,
    terminal: set[Mode],
):
    """Compute only RK4 stage modes required by the terminal output set."""
    S0, K1, K2, K3, K4 = _rk4_pullback_sets(triads, terminal)

    k1 = rhs_selected(state, K1, triads, nu)
    y2 = _state_with_increment(state, k1, 0.5 * dt)
    k2 = rhs_selected(y2, K2, triads, nu)
    y3 = _state_with_increment(state, k2, 0.5 * dt)
    k3 = rhs_selected(y3, K3, triads, nu)
    y4 = _state_with_increment(state, k3, dt)
    k4 = rhs_selected(y4, K4, triads, nu)

    out = dict(state)
    for k in K4:
        combo = _vadd(
            _vadd(k1[k], _vscale(2.0, k2[k])),
            _vadd(_vscale(2.0, k3[k]), k4[k]),
        )
        out[k] = _vadd(state[k], _vscale(dt / 6.0, combo))

    work = (
        sum(len(triads[k]) for k in K1)
        + sum(len(triads[k]) for k in K2)
        + sum(len(triads[k]) for k in K3)
        + sum(len(triads[k]) for k in K4)
    )
    return out, {
        "input_modes": len(S0),
        "stage_modes": [len(K1), len(K2), len(K3), len(K4)],
        "triad_work": work,
    }, S0


def full_rk4_step(state: dict[Mode, Vec], dt: float, nu: float, modes, triads):
    allset = set(modes)
    return retained_rk4_step(state, dt, nu, triads, allset)[0]


def _target_diff(a: Vec, b: Vec) -> float:
    return math.sqrt(sum(abs(a[i] - b[i]) ** 2 for i in range(3)))


def solve_task_mode(
    *,
    K: int,
    nu: float,
    dt: float,
    horizon: int,
    target_mode: Mode,
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
        raise ValueError(
            f"horizon must be in 1..{max_horizon} for the portable API guard"
        )
    if dt <= 0:
        raise ValueError("dt must be positive")
    if nu < 0:
        raise ValueError("nu must be nonnegative")

    modes = cube_modes(K)
    target_mode = tuple(int(x) for x in target_mode)
    if target_mode not in set(modes):
        raise ValueError("target_mode lies outside the retained Fourier cube")
    triads = triads_by_output(modes)

    state = (
        parse_state(modes, initial_state)
        if initial_state is not None
        else deterministic_state(modes, seed=seed, target_energy=target_energy)
    )
    full_initial = dict(state)

    step_terminals = [None] * horizon
    terminal = {target_mode}
    for n in range(horizon - 1, -1, -1):
        step_terminals[n] = set(terminal)
        terminal = _rk4_pullback_sets(triads, terminal)[0]

    ledger = []
    for n in range(horizon):
        state, info, _ = retained_rk4_step(
            state, dt, nu, triads, step_terminals[n]
        )
        ledger.append(info)

    target_value = state[target_mode]
    full_triad_per_rhs = sum(len(triads[k]) for k in modes)
    full_work = 4 * horizon * full_triad_per_rhs
    retained_work = sum(row["triad_work"] for row in ledger)

    verification = None
    if verify:
        full = full_initial
        for _ in range(horizon):
            full = full_rk4_step(full, dt, nu, modes, triads)
        err = _target_diff(target_value, full[target_mode])
        verification = {
            "target_abs_error": err,
            "gate": 1e-12,
            "status": "PASS" if err <= 1e-12 else "FAIL",
        }

    return {
        "target_mode": list(target_mode),
        "target_value": target_value,
        "mode_count": len(modes),
        "ordered_triads": full_triad_per_rhs,
        "horizon": horizon,
        "rk4_stage_ledger": ledger,
        "retained_triad_work": retained_work,
        "full_triad_work": full_work,
        "structural_work_reduction": (
            float(full_work) / retained_work if retained_work else float("inf")
        ),
        "verification": verification,
        "claim_scope": (
            "task-exact relative to the same fixed finite Fourier-Galerkin RK4 recurrence"
        ),
    }
