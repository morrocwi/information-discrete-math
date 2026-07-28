# differential equations
from idm._solve_core import *  # noqa: F401,F403

@kind("ode_system")
def _osys(p):
    vs = p["vars"]
    # bind each state variable from vs; bind the independent variable as `t` unless a state is named
    # `t` (avoids the collision when a state variable is itself named `x`, the old independent name).
    fs = [(lambda s: (lambda t, *y: F.evaluate(
        s, **{**dict(zip(vs, y)), **({"t": t} if "t" not in vs else {})})))(s) for s in p["f"]]
    y = DEQ.ode_system(fs, _val(p["x0"]), [_val(v) for v in p["y0"]], _val(p["xT"]), int(p.get("N", 2000)))
    return _ok("ode_system", y, "vector RK4 (= I_ε of the field)")
@kind("ode_bvp")
def _bvp(p):
    q = _expr_fn(p.get("q", "0"), "x"); r = _expr_fn(p.get("r", "0"), "x")
    sol = DEQ.ode_bvp(q, r, _val(p["a"]), _val(p["b"]), _val(p["alpha"]), _val(p["beta"]), int(p.get("N", 400)))
    if "at" in p:
        xa = _val(p["at"]); i = min(range(len(sol)), key=lambda k: abs(sol[k][0] - xa))
        return _ok("ode_bvp", sol[i][1], "finite-difference tridiagonal", at=p["at"])
    return _ok("ode_bvp", [v for _, v in sol], "finite-difference tridiagonal")
@kind("pde_heat")
def _heat(p):
    init = _expr_fn(p["init"], "x"); L = _val(p["L"])
    u = DEQ.pde_heat(_val(p.get("alpha", 1)), L, _val(p["T"]), init, tuple(p.get("bc", (0, 0))),
                     int(p.get("Nx", 80)), int(p.get("Nt", 400)))
    if "at" in p:
        i = int(round(float(_val(p["at"]) / L) * (len(u) - 1))); return _ok("pde_heat", u[i], "Crank–Nicolson", at=p["at"])
    return _ok("pde_heat", u, "Crank–Nicolson (2nd order, unconditionally stable)")
@kind("pde_wave")
def _wave(p):
    init = _expr_fn(p["init"], "x"); L = _val(p["L"])
    iv = _expr_fn(p["init_vel"], "x") if "init_vel" in p else None
    u = DEQ.pde_wave(_val(p.get("c", 1)), L, _val(p["T"]), init, iv, tuple(p.get("bc", (0, 0))), int(p.get("Nx", 100)))
    if "at" in p:
        i = int(round(float(_val(p["at"]) / L) * (len(u) - 1))); return _ok("pde_wave", u[i], "explicit leapfrog", at=p["at"])
    return _ok("pde_wave", u, "explicit leapfrog (CFL-stable)")
@kind("pde_poisson")
def _pde_poisson(p):
    f = _expr_fn(p.get("f", "0"), "x", "y")
    bc = _expr_fn(p["bc"], "x", "y") if isinstance(p.get("bc"), str) else p.get("bc", 0)
    u = DEQ.pde_poisson(f, p["box"], bc, int(p.get("Nx", 40)), int(p.get("Ny", 40)))
    if "at" in p:
        x0, x1, y0, y1 = [_val(v) for v in p["box"]]; ax, ay = _val(p["at"][0]), _val(p["at"][1])
        i = int(round(float((ax - x0) / (x1 - x0)) * (len(u) - 1)))
        j = int(round(float((ay - y0) / (y1 - y0)) * (len(u[0]) - 1)))
        return _ok("pde_poisson", u[i][j], "Gauss–Seidel", at=p["at"])
    return _ok("pde_poisson", u, "Gauss–Seidel relaxation")
@kind("pde_laplace")
def _lap(p): p = {**p, "f": "0"}; return _pde_poisson(p) | {"kind": "pde_laplace"}
@kind("sturm_liouville")
def _sl(p):
    V = _expr_fn(p.get("potential", "0"), "x")
    eig = DEQ.sturm_liouville(V, _val(p["L"]), int(p.get("n_eigs", 5)), int(p.get("N", 300)))
    return _ok("sturm_liouville", eig, "finite-difference + Sturm-sequence bisection")
