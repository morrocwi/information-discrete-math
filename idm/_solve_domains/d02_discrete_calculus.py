# discrete calculus
from idm._solve_core import *  # noqa: F401,F403

@kind("derivative")
def _d(p): return _ok("derivative", F.derivative(_fn(p["f"]), _val(p["x"])), "finite central difference D_ε + Richardson")
@kind("limit")
def _lim(p): return _ok("limit", F.limit(_seq(p["seq"])), "Richardson on h=1/n (A8 plateau)")
@kind("ode")
def _ode(p): return _ok("ode", F.ode(_fn2(p["f"]), _val(p["x0"]), _val(p["y0"]), _val(p["xT"])), "finite RK4 (= I_ε of the field)")
@kind("double_integral")
def _di(p): return _ok("double_integral", AN.double_integral(_fn2(p["f"]), _val(p["ax"]), _val(p["bx"]), _val(p["ay"]), _val(p["by"]), int(p.get("N", 200))), "finite 2-D midpoint grid")
@kind("series_sum")
def _ss(p): return _ok("series_sum", AN.series_sum(_seq(p["term"]), int(p.get("N", 2000))), "finite partial sum")
@kind("zeta")
def _z(p): return _ok("zeta", AN.zeta(p["s"]), "ζ: Euler–Maclaurin (s>1) / −B_{n+1}/(n+1) (s≤0)")
@kind("regularized_sum")
def _rs(p): return _ok("regularized_sum", AN.regularized_sum(int(p.get("power", 1))), "smoothed sum Σn^p e^{−εn}, pole removed (ζ(−p))")
@kind("root_find")
def _rf(p): return _ok("root_find", AN.root_find(_fn(p["f"]), p.get("a"), p.get("b"), p.get("x0")), "bisection / finite Newton")
@kind("minimize")
def _mn(p):
    x, fx = AN.minimize_1d(_fn(p["f"]), _val(p["a"]), _val(p["b"])); return _ok("minimize", {"argmin": x, "min": fx}, "golden-section search")
@kind("interpolate")
def _ip(p): return _ok("interpolate", AN.interpolate(p["points"], p["x"]), "Lagrange interpolation (exact ℚ when rational)")
