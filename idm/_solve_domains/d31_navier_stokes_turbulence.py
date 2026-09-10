# finite Navier--Stokes turbulence readouts
# Solver-surface owner: this registered kind is intentionally included in the
# generated fixture/capability/golden manifests; the sync workflow keeps those
# public surfaces single-sourced from the live registry.
from idm._solve_core import *  # noqa: F401,F403
from idm import ns_turbulence as NST


def _resolve_horizon(p, dt):
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


@kind("ns_turbulence_energy_flux", "finite_diagnostic")
def _ns_turbulence_energy_flux(p):
    K = int(p.get("K", 2))
    nu = float(p.get("nu", 0.005))
    dt = float(p.get("dt", 0.0025))
    horizon = _resolve_horizon(p, dt)
    cutoff = float(p.get("cutoff", 1.0))
    r = NST.solve_energy_flux(
        K=K,
        nu=nu,
        dt=dt,
        horizon=horizon,
        cutoff=cutoff,
        seed=int(p.get("seed", 20260909)),
        target_energy=float(p.get("target_energy", 0.125)),
        initial_state=p.get("initial_state"),
        verify=bool(p.get("verify", True)),
    )
    verification = r.get("verification")
    if verification is not None and verification.get("status") != "PASS":
        return {
            "kind": "ns_turbulence_energy_flux",
            "status": "HOLD",
            "reason": "finite turbulence energy-flux verification gate failed",
            "verification": verification,
            "tier": "finite_diagnostic",
        }
    return {
        "kind": "ns_turbulence_energy_flux",
        "status": "ok",
        "value": r["value"],
        "method": "finite Fourier-Galerkin nonlinear-transfer energy-flux readout",
        "readout": "turbulence_energy_flux",
        "cutoff": r["cutoff"],
        "cutoff_squared": r["cutoff_squared"],
        "sign_convention": r["sign_convention"],
        "included_mode_count": r["included_mode_count"],
        "required_terminal_state_modes": r["required_terminal_state_modes"],
        "mode_count": r["mode_count"],
        "readout_density": r["readout_density"],
        "required_state_density": r["required_state_density"],
        "transfer_sum_low": r["transfer_sum_low"],
        "shells": r["shells"],
        "initial_state_constraints": r["initial_state_constraints"],
        "horizon": r["horizon"],
        "rk4_stage_ledger": r["rk4_stage_ledger"],
        "retained_triad_work": r["retained_triad_work"],
        "full_triad_work": r["full_triad_work"],
        "structural_work_reduction": r["structural_work_reduction"],
        "verification": verification,
        "readout_identity": r["readout_identity"],
        "claim_scope": r["claim_scope"],
        "backend": r["backend"],
    }