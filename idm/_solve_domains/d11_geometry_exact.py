# geometry (exact ℚ + √)
from idm._solve_core import *  # noqa: F401,F403

@kind("dot", "Th_coqc")
def _dot(p): return _ok("dot", X.dot(p["u"], p["v"]), "Σ uᵢvᵢ exact ℚ")
@kind("cross", "Th_coqc")
def _cr(p):
    u, v = p["u"], p["v"]; r = X.cross2(u, v) if len(u) == 2 else X.cross3(u, v)
    return _ok("cross", r, "cross product exact ℚ")
@kind("polygon_area", "Th_coqc")
def _par2(p): return _ok("polygon_area", X.polygon_area(p["points"]), "shoelace formula exact ℚ")
@kind("triangle_area", "Th_coqc")
def _ta(p): return _ok("triangle_area", X.triangle_area(p["a"], p["b"], p["c"]), "shoelace exact ℚ")
@kind("vector_norm")
def _vn(p): return _ok("vector_norm", mp.sqrt(float(X.dot(p["v"], p["v"]))) if _HAVE else float(X.dot(p["v"], p["v"])) ** 0.5, "√(Σvᵢ²) (squared part exact ℚ)")
@kind("distance")
def _dist(p):
    pv = [Fraction(str(x)) for x in p["p"]]; qv = [Fraction(str(x)) for x in p["q"]]
    d2 = sum((a - b) ** 2 for a, b in zip(pv, qv))
    return _ok("distance", mp.sqrt(float(d2)) if _HAVE else float(d2) ** 0.5, "√Σ(pᵢ−qᵢ)² (squared part exact ℚ)")
