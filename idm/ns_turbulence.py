"""Finite Navier--Stokes turbulence readouts.

This module adds turbulence observables as readouts of the existing finite
Fourier--Galerkin Navier--Stokes dynamics.  It does not introduce a turbulence
closure or a new physical law.

For a Fourier mode k, let N_k(u) denote only the nonlinear Galerkin RHS
(viscosity set to zero).  The modal nonlinear energy transfer is

    T_k = Re(conj(u_k) dot N_k(u)).

For a radial cutoff kappa, the low-mode energy flux convention used here is

    Pi(kappa) = - sum_{|k| <= kappa} T_k.

Thus positive Pi means the retained low modes are losing energy through the
nonlinear term (the usual forward-cascade sign convention).  All claims are
relative to the declared finite Fourier cube and the same explicit RK4
recurrence used by idm.ns_retained.
"""
from __future__ import annotations

import math
from typing import Iterable

from . import ns_retained as NSR

Mode = NSR.Mode
Vec = NSR.Vec


def _k2(k: Mode) -> int:
    return k[0] * k[0] + k[1] * k[1] + k[2] * k[2]


def _modal_energy(u: Vec) -> float:
    return 0.5 * sum(abs(z) ** 2 for z in u)


def _real_dot_conj(a: Vec, b: Vec) -> float:
    return float((a[0].conjugate() * b[0] + a[1].conjugate() * b[1] + a[2].conjugate() * b[2]).real)


def state_constraint_residuals(state: dict[Mode, Vec], modes: Iterable[Mode]) -> dict:
    """Return divergence and real-field conjugacy residuals for a finite state."""
    modes = tuple(modes)
    mode_set = set(modes)
    div = 0.0
    conj = 0.0
    for k in modes:
        u = state[k]
        div = max(div, abs(k[0] * u[0] + k[1] * u[1] + k[2] * u[2]))
        neg = (-k[0], -k[1], -k[2])
        if neg in mode_set:
            un = state[neg]
            conj = max(conj, *(abs(un[i] - u[i].conjugate()) for i in range(3)))
    return {"divergence_max": div, "conjugate_symmetry_max": conj}


def nonlinear_transfer_by_mode(
    state: dict[Mode, Vec],
    outputs: Iterable[Mode],
    triads,
) -> dict[Mode, float]:
    """Exact-for-the-finite-algebra modal nonlinear transfer T_k.

    The nonlinear RHS is obtained from the same Galerkin kernel as the NS
    solver with nu=0, avoiding a duplicate convection formula.
    """
    outputs = tuple(outputs)
    nonlinear_rhs = NSR.rhs_selected(state, outputs, triads, nu=0.0)
    return {k: _real_dot_conj(state[k], nonlinear_rhs[k]) for k in outputs}


def _shell_accumulate(state, transfers, outputs, nu: float) -> list[dict]:
    rows = {}
    for k in outputs:
        q = _k2(k)
        row = rows.setdefault(q, {"q": q, "mode_count": 0, "energy": 0.0, "transfer": 0.0})
        row["mode_count"] += 1
        row["energy"] += _modal_energy(state[k])
        row["transfer"] += transfers[k]
    out = []
    cumulative = 0.0
    for q in sorted(rows):
        row = rows[q]
        row["dissipation"] = 2.0 * nu * q * row["energy"]
        row["energy_rate"] = row["transfer"] - row["dissipation"]
        cumulative += row["transfer"]
        row["cumulative_flux"] = -cumulative
        out.append(row)
    return out


def _evolve_required_state(state, *, horizon: int, dt: float, nu: float, triads, terminal_required: set[Mode]):
    """Backward-compile the exact finite RK4 dependency cone for a final-state support."""
    step_terminals = [None] * horizon
    terminal = set(terminal_required)
    for n in range(horizon - 1, -1, -1):
        step_terminals[n] = set(terminal)
        terminal = NSR._rk4_pullback_sets(triads, terminal)[0]

    ledger = []
    for n in range(horizon):
        state, info, _ = NSR.retained_rk4_step(state, dt, nu, triads, step_terminals[n])
        ledger.append(info)
    return state, ledger


def solve_energy_flux(
    *,
    K: int,
    nu: float,
    dt: float,
    horizon: int,
    cutoff: float,
    seed: int = 20260909,
    target_energy: float = 0.125,
    initial_state=None,
    verify: bool = True,
    max_K: int = 3,
    max_horizon: int = 3,
):
    """Compute a finite turbulence energy-flux readout at the final RK4 time."""
    if K < 1 or K > max_K:
        raise ValueError(f"K must be in 1..{max_K} for the portable API guard")
    if horizon < 1 or horizon > max_horizon:
        raise ValueError(f"horizon must be in 1..{max_horizon} for the portable API guard")
    if dt <= 0:
        raise ValueError("dt must be positive")
    if nu < 0:
        raise ValueError("nu must be nonnegative")
    cutoff = float(cutoff)
    if not math.isfinite(cutoff) or cutoff <= 0:
        raise ValueError("cutoff must be a positive finite Fourier radius")

    modes = NSR.cube_modes(K)
    triads = NSR.triads_by_output(modes)
    state = (
        NSR.parse_state(modes, initial_state)
        if initial_state is not None
        else NSR.deterministic_state(modes, seed=seed, target_energy=target_energy)
    )
    constraints = state_constraint_residuals(state, modes)
    constraint_gate = 1e-10
    if constraints["divergence_max"] > constraint_gate or constraints["conjugate_symmetry_max"] > constraint_gate:
        raise ValueError(
            "turbulence readout requires a divergence-free conjugate-symmetric finite state"
        )

    cutoff2 = cutoff * cutoff
    low_modes = {k for k in modes if _k2(k) <= cutoff2 + 1e-15}
    if not low_modes:
        raise ValueError("cutoff selects no nonzero Fourier modes")

    # T_k for k in low_modes requires u_k and every ordered triad input p,q.
    terminal_required = NSR.dependency_expand(triads, low_modes)
    initial = dict(state)
    state, ledger = _evolve_required_state(
        state,
        horizon=horizon,
        dt=dt,
        nu=nu,
        triads=triads,
        terminal_required=terminal_required,
    )

    transfers = nonlinear_transfer_by_mode(state, low_modes, triads)
    transfer_sum_low = sum(transfers.values())
    flux = -transfer_sum_low
    shell_rows = _shell_accumulate(state, transfers, low_modes, nu)

    full_triad_per_rhs = sum(len(triads[k]) for k in modes)
    full_work = 4 * horizon * full_triad_per_rhs
    retained_work = sum(row["triad_work"] for row in ledger)

    verification = None
    if verify:
        full = initial
        for _ in range(horizon):
            full = NSR.full_rk4_step(full, dt, nu, modes, triads)
        full_low_transfer = nonlinear_transfer_by_mode(full, low_modes, triads)
        full_flux = -sum(full_low_transfer.values())
        flux_err = abs(flux - full_flux)

        # Finite Galerkin convection should redistribute, not create, total energy.
        all_transfer = nonlinear_transfer_by_mode(full, modes, triads)
        conservation_residual = abs(sum(all_transfer.values()))
        gate = 1e-12
        verification = {
            "retained_full_flux_abs_error": flux_err,
            "nonlinear_total_transfer_abs": conservation_residual,
            "gate": gate,
            "status": "PASS" if flux_err <= gate and conservation_residual <= gate else "FAIL",
        }

    max_radius = max(math.sqrt(_k2(k)) for k in modes)
    return {
        "cutoff": cutoff,
        "cutoff_squared": cutoff2,
        "value": flux,
        "sign_convention": "positive = nonlinear energy leaves modes with |k| <= cutoff",
        "included_mode_count": len(low_modes),
        "required_terminal_state_modes": len(terminal_required),
        "mode_count": len(modes),
        "readout_density": len(low_modes) / len(modes),
        "required_state_density": len(terminal_required) / len(modes),
        "max_fourier_radius": max_radius,
        "transfer_sum_low": transfer_sum_low,
        "shells": shell_rows,
        "initial_state_constraints": constraints,
        "horizon": horizon,
        "rk4_stage_ledger": ledger,
        "retained_triad_work": retained_work,
        "full_triad_work": full_work,
        "structural_work_reduction": (float(full_work) / retained_work if retained_work else float("inf")),
        "verification": verification,
        "claim_scope": (
            "finite Fourier-Galerkin turbulence readout; flux is exact relative to the same fixed finite RK4 recurrence, not continuum turbulence"
        ),
        "readout_identity": "Pi(cutoff) = -sum_{|k|<=cutoff} Re(conj(u_k) dot N_k(u))",
        "backend": "portable_direct_retained_then_nonlinear_transfer",
    }


__all__ = [
    "state_constraint_residuals",
    "nonlinear_transfer_by_mode",
    "solve_energy_flux",
]
