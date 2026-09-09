# portable task-conditioned finite Fourier-Galerkin Navier-Stokes RK4
from idm._solve_core import *  # noqa: F401,F403
from idm import ns_retained as NSR


@kind("ns_retained_rk4", "finite_diagnostic")
def _ns_retained_rk4(p):
    K = int(p.get("K", 2))
    nu = float(p.get("nu", 0.005))
    dt = float(p.get("dt", 0.0025))
    horizon = int(p.get("horizon", 1))
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
