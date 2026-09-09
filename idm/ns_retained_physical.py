"""Physical-space readouts for the portable finite Navier-Stokes RK4 solver.

This module intentionally preserves the readout logic instead of pretending that a
pointwise velocity query is sparse in Fourier coordinates.

For a fixed finite Fourier cube K,

    u(x,T) = sum_k u_hat_k(T) exp(i k.x).

Therefore an exact point-velocity readout has terminal support on every retained
Fourier mode in the cube.  The exact RRP terminal set is dense, so there is no
structural compression to claim for this reader.  The solver falls back to the
full finite RK4 recurrence and reports that fact explicitly.

Claim scope:
- fixed finite Fourier cube {-K,...,K}^3 minus {0};
- unforced incompressible Fourier-Galerkin Navier-Stokes recurrence;
- classical explicit RK4;
- exact physical velocity readout of that finite state;
- no continuum regularity/singularity claim;
- no speedup claim for the dense point-velocity reader.
"""
from __future__ import annotations

import cmath
import math

from . import ns_retained as NSR


def _validate_point(point) -> tuple[float, float, float]:
    if not isinstance(point, (list, tuple)) or len(point) != 3:
        raise ValueError("point must be [x,y,z]")
    out = tuple(float(x) for x in point)
    if not all(math.isfinite(x) for x in out):
        raise ValueError("point coordinates must be finite")
    return out  # type: ignore[return-value]


def _component_index(component):
    if component is None:
        return None
    if isinstance(component, str):
        key = component.strip().lower()
        if key in ("x", "u", "0"):
            return 0
        if key in ("y", "v", "1"):
            return 1
        if key in ("z", "w", "2"):
            return 2
    i = int(component)
    if i not in (0, 1, 2):
        raise ValueError("component must be x/y/z or 0/1/2")
    return i


def physical_velocity(state, point, modes=None):
    """Evaluate the finite Fourier series velocity at one physical point."""
    x = _validate_point(point)
    if modes is None:
        modes = state.keys()
    acc = [0j, 0j, 0j]
    for k in modes:
        phase = cmath.exp(1j * (k[0] * x[0] + k[1] * x[1] + k[2] * x[2]))
        uk = state[k]
        acc[0] += uk[0] * phase
        acc[1] += uk[1] * phase
        acc[2] += uk[2] * phase
    return (acc[0], acc[1], acc[2])


def solve_physical_velocity(
    *,
    K: int,
    nu: float,
    dt: float,
    horizon: int,
    point,
    component=None,
    seed: int = 20260909,
    target_energy: float = 0.125,
    initial_state=None,
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

    x = _validate_point(point)
    ci = _component_index(component)
    modes = NSR.cube_modes(K)
    triads = NSR.triads_by_output(modes)
    state = (
        NSR.parse_state(modes, initial_state)
        if initial_state is not None
        else NSR.deterministic_state(modes, seed=seed, target_energy=target_energy)
    )

    # Exact point velocity is dense in Fourier coordinates.  Hence the terminal
    # RRP support is every mode and the exact retained path equals the full path.
    all_modes = set(modes)
    ledger = []
    for _ in range(horizon):
        state, info, _ = NSR.retained_rk4_step(state, dt, nu, triads, all_modes)
        ledger.append(info)

    value = physical_velocity(state, x, modes)
    if ci is not None:
        value_out = value[ci]
    else:
        value_out = value

    imag_leakage = max(abs(z.imag) for z in value)
    real_field_status = "PASS" if imag_leakage <= 1e-12 else "DIAGNOSTIC_COMPLEX"
    full_triad_per_rhs = sum(len(triads[k]) for k in modes)
    full_work = 4 * horizon * full_triad_per_rhs
    used_work = sum(row["triad_work"] for row in ledger)

    return {
        "point": list(x),
        "component": component,
        "value": value_out,
        "mode_count": len(modes),
        "terminal_mode_count": len(modes),
        "readout_density": 1.0,
        "horizon": horizon,
        "rk4_stage_ledger": ledger,
        "retained_triad_work": used_work,
        "full_triad_work": full_work,
        "structural_work_reduction": (
            float(full_work) / used_work if used_work else float("inf")
        ),
        "compression_status": "DENSE_READOUT_FULL_RK4",
        "backend": "portable_full_rk4",
        "verification": {
            "finite_fourier_real_field_imaginary_leakage": imag_leakage,
            "status": real_field_status,
        },
        "readout_obstruction": (
            "exact point velocity u(x,T)=sum_k u_hat_k(T) exp(i k.x) has nonzero "
            "terminal weight on every Fourier mode, so exact RRP terminal support is dense"
        ),
        "claim_scope": (
            "exact physical readout of the same fixed finite Fourier-Galerkin RK4 recurrence; "
            "dense reader, therefore no retained speedup claim"
        ),
    }
