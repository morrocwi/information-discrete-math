"""idm.solve — public dispatch facade. Handlers: idm/_solve_domains/*.py; infrastructure: idm/_solve_core.py."""
from idm._solve_core import _REG, kind, mp, _HAVE, _CANON_DPS  # noqa: F401
from idm import _solve_domains  # noqa: F401  (side effect: registers handlers)

_COQ_BACKED = {
    "orient":            "IDM_Geometry.orient_* (orientation determinant, axiom-free)",
    "convex_hull":       "IDM_Geometry.orient_* (branches only on the proven orientation sign)",
    "point_in_polygon":  "IDM_Geometry.orient_* (proven orientation predicate; exact boundary)",
    "segments_intersect":"IDM_Geometry.orient_* (proven orientation predicate)",
    "shortest_path":     "IDM_Tropical.minplus_distrib (min-plus semiring law)",
    "widest_path":       "IDM_Tropical.maxplus_distrib (max-plus semiring law)",
    "minimax_path":      "IDM_Tropical.bottleneck_distrib (bottleneck semiring law)",
    "spanning_tree_count":"IDM_Matrix.laplacian_* (Kirchhoff via the graph Laplacian)",
    "geometric_series":  "IDM_Certified.geom_certified_identity (certified geometric-series bound)",
}
def solve(problem):
    if not isinstance(problem, dict) or "kind" not in problem:
        return {"status": "HOLD", "reason": "problem must be a dict with a 'kind' field"}
    k = problem["kind"]
    if k not in _REG:
        return {"kind": k, "status": "HOLD", "reason": f"unknown problem kind '{k}'",
                "known_kinds": sorted(_REG)}
    fn, tier = _REG[k]
    try:
        if _HAVE:
            with mp.workdps(_CANON_DPS):   # deterministic, order-independent precision (see _CANON_DPS)
                res = fn(problem)
        else:  # pragma: no cover
            res = fn(problem)
    except KeyError as ex:
        return {"kind": k, "status": "HOLD", "reason": f"missing required field {ex}"}
    except Exception as ex:
        return {"kind": k, "status": "HOLD", "reason": f"{type(ex).__name__}: {ex}"}
    res.setdefault("tier", tier)
    # tier-honesty pass: keep Th_coqc only where a named machine-checked theorem governs the result
    if res.get("tier") == "Th_coqc":
        if k in _COQ_BACKED:
            res["coq_theorem"] = _COQ_BACKED[k]
        else:
            res["tier"] = "exact"   # exact & decidable, but not individually machine-checked in Coq
    return res
def kinds():
    """the catalogue of supported problem kinds."""
    return sorted(_REG)
