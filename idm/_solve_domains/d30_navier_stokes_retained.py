# portable task-conditioned finite Fourier-Galerkin Navier-Stokes RK4
from idm._solve_core import *  # noqa: F401,F403
from idm import ns_retained as NSR
from idm import ns_retained_physical as NSP
from idm import ns_retained_plane as NSPN
from idm import ns_retained_harmonic as NSH


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
    K = int(p.get("K", 2)); nu = float(p.get("nu", 0.005)); dt = float(p.get("dt", 0.0025))
    horizon = _resolve_horizon(p, dt)
    target_mode = tuple(int(x) for x in p.get("target_mode", (1, 0, 0)))
    seed = int(p.get("seed", 20260909)); target_energy = float(p.get("target_energy", 0.125))
    verify = bool(p.get("verify", True)); initial_state = p.get("initial_state")
    r = NSR.solve_task_mode(K=K, nu=nu, dt=dt, horizon=horizon, target_mode=target_mode,
                            seed=seed, target_energy=target_energy, initial_state=initial_state, verify=verify)
    verification = r.get("verification")
    if verification is not None and verification.get("status") != "PASS":
        return {"kind": "ns_retained_rk4", "status": "HOLD",
                "reason": "retained/full finite-RK4 verification gate failed",
                "verification": verification, "tier": "finite_diagnostic"}
    return {"kind": "ns_retained_rk4", "status": "ok", "value": _norm(r["target_value"]),
            "method": "task-conditioned retained Fourier-Galerkin RK4 (portable direct-triad backend)",
            "target_mode": r["target_mode"], "mode_count": r["mode_count"],
            "ordered_triads": r["ordered_triads"], "horizon": r["horizon"],
            "rk4_stage_ledger": r["rk4_stage_ledger"], "retained_triad_work": r["retained_triad_work"],
            "full_triad_work": r["full_triad_work"], "structural_work_reduction": r["structural_work_reduction"],
            "verification": verification, "claim_scope": r["claim_scope"], "backend": "portable_direct_retained"}


@kind("ns_retained_physical", "finite_diagnostic")
def _ns_retained_physical(p):
    K = int(p.get("K", 2)); nu = float(p.get("nu", 0.005)); dt = float(p.get("dt", 0.0025))
    horizon = _resolve_horizon(p, dt)
    readout = str(p.get("readout", "velocity")).strip().lower()
    if readout != "velocity":
        raise ValueError("portable physical API currently supports readout='velocity' only")
    r = NSP.solve_physical_velocity(K=K, nu=nu, dt=dt, horizon=horizon, point=p["point"],
                                    component=p.get("component"), seed=int(p.get("seed", 20260909)),
                                    target_energy=float(p.get("target_energy", 0.125)),
                                    initial_state=p.get("initial_state"))
    return {"kind": "ns_retained_physical", "status": "ok", "value": _norm(r["value"]),
            "method": "physical-space finite Fourier readout after full portable RK4 (dense exact reader)",
            "readout": "velocity", "point": r["point"], "component": r["component"],
            "mode_count": r["mode_count"], "terminal_mode_count": r["terminal_mode_count"],
            "readout_density": r["readout_density"], "horizon": r["horizon"],
            "rk4_stage_ledger": r["rk4_stage_ledger"], "retained_triad_work": r["retained_triad_work"],
            "full_triad_work": r["full_triad_work"], "structural_work_reduction": r["structural_work_reduction"],
            "compression_status": r["compression_status"], "verification": r["verification"],
            "readout_obstruction": r["readout_obstruction"], "claim_scope": r["claim_scope"], "backend": r["backend"]}


@kind("ns_retained_plane_average", "finite_diagnostic")
def _ns_retained_plane_average(p):
    K = int(p.get("K", 2)); nu = float(p.get("nu", 0.005)); dt = float(p.get("dt", 0.0025))
    horizon = _resolve_horizon(p, dt)
    r = NSPN.solve_plane_average_velocity(K=K, nu=nu, dt=dt, horizon=horizon,
        axis=str(p.get("axis", "x")).strip().lower(), coordinate=float(p.get("coordinate", 0.0)),
        seed=int(p.get("seed", 20260909)), target_energy=float(p.get("target_energy", 0.125)),
        initial_state=p.get("initial_state"), verify=bool(p.get("verify", True)))
    verification = r.get("verification")
    if verification is not None and verification.get("status") != "PASS":
        return {"kind": "ns_retained_plane_average", "status": "HOLD",
                "reason": "retained/full finite-RK4 plane-readout verification gate failed",
                "verification": verification, "tier": "finite_diagnostic"}
    return {"kind": "ns_retained_plane_average", "status": "ok", "value": _norm(r["value"]),
            "method": "exact sparse plane-average velocity readout with triad pullback through portable RK4",
            "readout": "plane_average_velocity", "axis": r["axis"], "coordinate": r["coordinate"],
            "mode_count": r["mode_count"], "terminal_mode_count": r["terminal_mode_count"],
            "readout_density": r["readout_density"], "horizon": r["horizon"],
            "rk4_stage_ledger": r["rk4_stage_ledger"], "retained_triad_work": r["retained_triad_work"],
            "full_triad_work": r["full_triad_work"], "structural_work_reduction": r["structural_work_reduction"],
            "compression_status": r["compression_status"], "verification": verification,
            "imaginary_residual": r["imaginary_residual"], "longitudinal_residual": r["longitudinal_residual"],
            "readout_identity": r["readout_identity"], "claim_scope": r["claim_scope"], "backend": r["backend"]}


@kind("ns_retained_harmonic_probe", "finite_diagnostic")
def _ns_retained_harmonic_probe(p):
    K = int(p.get("K", 2)); nu = float(p.get("nu", 0.005)); dt = float(p.get("dt", 0.0025))
    horizon = _resolve_horizon(p, dt)
    wavevector = p.get("wavevector", [K, K, K])
    r = NSH.solve_harmonic_probe(K=K, nu=nu, dt=dt, horizon=horizon, wavevector=wavevector,
        phase=float(p.get("phase", 0.0)), seed=int(p.get("seed", 20260909)),
        target_energy=float(p.get("target_energy", 0.125)), initial_state=p.get("initial_state"),
        verify=bool(p.get("verify", True)))
    verification = r.get("verification")
    if verification is not None and verification.get("status") != "PASS":
        return {"kind": "ns_retained_harmonic_probe", "status": "HOLD",
                "reason": "retained/full finite-RK4 harmonic-probe verification gate failed",
                "verification": verification, "tier": "finite_diagnostic"}
    return {"kind": "ns_retained_harmonic_probe", "status": "ok", "value": _norm(r["value"]),
            "method": "exact real cosine volume-correlation readout with triad pullback through portable RK4",
            "readout": "harmonic_velocity_correlation", "wavevector": r["wavevector"], "phase": r["phase"],
            "mode_count": r["mode_count"], "terminal_mode_count": r["terminal_mode_count"],
            "readout_density": r["readout_density"], "terminal_step_cone": r["terminal_step_cone"],
            "horizon": r["horizon"], "rk4_stage_ledger": r["rk4_stage_ledger"],
            "retained_triad_work": r["retained_triad_work"], "full_triad_work": r["full_triad_work"],
            "structural_work_reduction": r["structural_work_reduction"], "compression_status": r["compression_status"],
            "verification": verification, "imaginary_residual": r["imaginary_residual"],
            "readout_identity": r["readout_identity"], "claim_scope": r["claim_scope"], "backend": r["backend"]}
