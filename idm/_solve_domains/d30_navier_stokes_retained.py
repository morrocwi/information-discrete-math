# portable task-conditioned finite Fourier-Galerkin Navier-Stokes RK4
from idm._solve_core import *  # noqa: F401,F403
from idm import ns_retained as NSR
from idm import ns_retained_physical as NSP


def _resolve_horizon(p, dt):
    """Accept either explicit horizon or physical time, never silently change dt."""
    has_h = "horizon" in p
    has_t = "time" in p
    if has_t:
        T = float(p["time"])
        if T <= 0:
            raise ValueError("time must be positive")
        ratio = T / dt
        nearest = round(ratio)
        if nearest < 1 or abs(ratio - nearest) > 1e-12 * max(1.0, abs(ratio)):
            raise ValueError("time must be an integer multiple of dt for the fixed RK4 recurrence")
        if has_h and int(p["horizon"]) != int(nearest):
            raise ValueError("horizon and time/dt disagree")
        return int(nearest)
    return int(p.get("horizon", 1))


@kind("ns_retained_rk4", "finite_diagnostic")
def _ns_retained_rk4(p):
    K = int(p.get("K", 2))
    nu = float(p.get("nu", 0.005))
    dt = float(p.get("dt", 0.0025))
    horizon = _resolve_horizon(p, dt)
    target_mode = tuple(int(x) for x in p.get("target_mode", (1, 0, 0)))
    seed = int(p.get("seed", 20260909))
    target_energy = float(p.get("target_energy", 0.125))
    verify = bool(p.get("verify", True))
    initial_state = p.get("initial_state")

    r = NSR.solve_task_mode(
        K=K,
        nu=nu,
        dt=dt,
        horizon=horizon,
        target_mode=target_mode,
        seed=seed,
        target_energy=target_energy,
        initial_state=initial_state,
        verify=verify,
    )

    verification = r.get("verification")
    if verification is not None and verification.get("status") != "PASS":
        return {
            "kind": "ns_retained_rk4",
            "status": "HOLD",
            "reason": "retained/full finite-RK4 verification gate failed",
            "verification": verification,
            "tier": "finite_diagnostic",
        }

    return {
        "kind": "ns_retained_rk4",
        "status": "ok",
        "value": _norm(r["target_value"]),
        "method": "task-conditioned retained Fourier-Galerkin RK4 (portable direct-triad backend)",
        "target_mode": r["target_mode"],
        "mode_count": r["mode_count"],
        "ordered_triads": r["ordered_triads"],
        "horizon": r["horizon"],
        "rk4_stage_ledger": r["rk4_stage_ledger"],
        "retained_triad_work": r["retained_triad_work"],
        "full_triad_work": r["full_triad_work"],
        "structural_work_reduction": r["structural_work_reduction"],
        "verification": verification,
        "claim_scope": r["claim_scope"],
        "backend": "portable_direct_retained",
    }


@kind("ns_retained_physical", "finite_diagnostic")
def _ns_retained_physical(p):
    K = int(p.get("K", 2))
    nu = float(p.get("nu", 0.005))
    dt = float(p.get("dt", 0.0025))
    horizon = _resolve_horizon(p, dt)
    readout = str(p.get("readout", "velocity")).strip().lower()
    if readout != "velocity":
        raise ValueError("portable physical API currently supports readout='velocity' only")

    point = p["point"]
    component = p.get("component")
    seed = int(p.get("seed", 20260909))
    target_energy = float(p.get("target_energy", 0.125))
    initial_state = p.get("initial_state")

    r = NSP.solve_physical_velocity(
        K=K,
        nu=nu,
        dt=dt,
        horizon=horizon,
        point=point,
        component=component,
        seed=seed,
        target_energy=target_energy,
        initial_state=initial_state,
    )

    return {
        "kind": "ns_retained_physical",
        "status": "ok",
        "value": _norm(r["value"]),
        "method": "physical-space finite Fourier readout after full portable RK4 (dense exact reader)",
        "readout": "velocity",
        "point": r["point"],
        "component": r["component"],
        "mode_count": r["mode_count"],
        "terminal_mode_count": r["terminal_mode_count"],
        "readout_density": r["readout_density"],
        "horizon": r["horizon"],
        "rk4_stage_ledger": r["rk4_stage_ledger"],
        "retained_triad_work": r["retained_triad_work"],
        "full_triad_work": r["full_triad_work"],
        "structural_work_reduction": r["structural_work_reduction"],
        "compression_status": r["compression_status"],
        "verification": r["verification"],
        "readout_obstruction": r["readout_obstruction"],
        "claim_scope": r["claim_scope"],
        "backend": r["backend"],
    }
