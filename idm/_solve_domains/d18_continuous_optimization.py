# continuous optimization
from idm._solve_core import *  # noqa: F401,F403

@kind("gradient_descent")
def _gd(p):
    vs = p["vars"]; f = _mfn(p["f"], vs)
    return _ok("gradient_descent", OPT.gradient_descent(f, [_val(v) for v in p["x0"]]), "steepest descent + backtracking line search")
@kind("newton_min")
def _nmin(p):
    vs = p["vars"]; f = _mfn(p["f"], vs)
    return _ok("newton_min", OPT.newton_min(f, [_val(v) for v in p["x0"]]), "Newton: x ← x − H⁻¹∇f (finite gradient & Hessian)")
@kind("newton_system")
def _nsys(p):
    vs = p["vars"]; Fs = [_mfn(e, vs) for e in p["F"]]
    return _ok("newton_system", OPT.newton_system(Fs, [_val(v) for v in p["x0"]]), "Newton with finite-difference Jacobian")
@kind("least_squares", "Th_coqc")
def _lsq(p): return _ok("least_squares", OPT.least_squares(p["A"], p["b"]), "exact-ℚ normal equations (AᵀA)x=Aᵀb")
@kind("lagrange_min")
def _lag(p):
    vs = p["vars"]; f = _mfn(p["f"], vs); gs = [_mfn(e, vs) for e in p["constraints"]]
    return _ok("lagrange_min", OPT.lagrange_min(f, gs, [_val(v) for v in p["x0"]]), "Newton on the KKT system (Lagrange multipliers)")
