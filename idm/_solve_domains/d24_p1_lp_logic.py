# P1 — LP / logic
from idm._solve_core import *  # noqa: F401,F403

@kind("linear_program")
def _lp(p):
    r = CO.linear_program(p["c"], p["A"], p["b"], p.get("sense", "max"))
    # the LP verdict (optimal / infeasible / unbounded) is a computed OUTCOME, kept in value; the
    # top-level status is 'ok' because the solve itself succeeded (detecting infeasibility is a result,
    # not a refusal).
    return {"kind": "linear_program", "status": "ok", "value": _norm(r), "tier": "exact",
            "method": "two-phase exact rational simplex (Bland's rule)"}
@kind("sat", "Th_coqc")
def _sat(p):
    r = CO.sat(p["clauses"], p.get("n_vars"))
    return {"kind": "sat", "status": "ok" if r["satisfiable"] else "HOLD", "value": r, "tier": "Th_coqc",
            "method": "DPLL with unit propagation"}
