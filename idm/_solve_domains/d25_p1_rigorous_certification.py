# P1 — rigorous certification
from idm._solve_core import *  # noqa: F401,F403

@kind("interval_enclose", "Th_coqc")
def _ienc(p): return _ok("interval_enclose", IVL.enclose(p["expr"], {k: tuple(v) for k, v in p["box"].items()}),
                         "single-shot rigorous interval evaluation")
@kind("verified_range", "Th_coqc")
def _vrange(p): return _ok("verified_range", IVL.verified_range(p["expr"], p["var"], p["a"], p["b"]),
                           "rigorous [min,max] enclosure by interval subdivision")
@kind("certified_root")
def _croot(p):
    r = IVL.certified_root(p["expr"], p["var"], p["a"], p["b"])
    return {"kind": "certified_root", "status": r.get("status", "ok"), "value": _norm(r), "tier": "Th_coqc",
            "method": "interval bisection — root proven by the intermediate-value theorem"}
@kind("certified_min", "Th_coqc")
def _cmin(p): return _ok("certified_min", IVL.certified_min(p["expr"], p["var"], p["a"], p["b"]),
                         "rigorous global-minimum bracket by interval branch-and-bound")
@kind("gershgorin", "Th_coqc")
def _gersh(p): return _ok("gershgorin", IVL.gershgorin(p["matrix"]), "Gershgorin discs enclosing every eigenvalue")
