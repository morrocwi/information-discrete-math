# certified computation
from idm._solve_core import *  # noqa: F401,F403

@kind("geometric_series", "Th_coqc")
def _gs(p): return _readout("geometric_series", C.geom_series(Fraction(str(p["r"])), Fraction(str(p.get("eps", "1/1000000000000")))), "geometric series, exact ℚ error r^N/(1-r) — Th_coqc")
@kind("exp")
def _ex(p): return _readout("exp", C.exp(p["x"], _eps(p)), "finite Taylor tail bound (|x|≤½) — Th_coqc")
@kind("integral")
def _integ(p): return _readout("integral", INT.integrate(_fn(p["f"]), p["a"], p["b"], _eps(p)),
                               "double-exponential DE quadrature (tanh/exp/sinh–sinh), a-posteriori certified")
@kind("improper_integral")
def _iimp(p): return _readout("improper_integral", INT.integrate(_fn(p["f"]), p.get("a", "-inf"), p.get("b", "inf"), _eps(p)),
                              "exp–sinh / sinh–sinh DE (semi/doubly-infinite), a-posteriori certified")
@kind("singular_integral")
def _ising(p): return _readout("singular_integral", INT.integrate(_fn(p["f"]), p["a"], p["b"], _eps(p)),
                               "tanh–sinh DE — clusters nodes so fast it absorbs endpoint singularities")
@kind("oscillatory_integral")
def _iosc(p): return _readout("oscillatory_integral", INT.integrate(_fn(p["f"]), p["a"], p["b"], _eps(p, "1e-10"), max_level=13),
                              "high-level DE quadrature")
@kind("gauss_quadrature")
def _igq(p): return _ok("gauss_quadrature", INT.gauss_legendre(_fn(p["f"]), _val(p["a"]), _val(p["b"]), int(p.get("n", 64))),
                        f"{p.get('n', 64)}-point Gauss–Legendre (finite nodes)")
@kind("residue_integral")
def _ires(p):
    r = INT.residue_sum(p["num"], p["den"])
    return _ok("residue_integral", r, "2πi·Σ residues in the upper half-plane (∫_{-∞}^∞ of a rational function)")
@kind("multidim_integral")
def _ind(p):
    names = p.get("vars") or [f"x{i}" for i in range(len(p["bounds"]))]
    f = lambda *pt: F.evaluate(str(p["f"]), **dict(zip(names, pt)))
    return _ok("multidim_integral", INT.integrate_nd(f, [[_val(a), _val(b)] for a, b in p["bounds"]], int(p.get("n", 40))),
               "nested Gauss–Legendre over the box (RCP for coupled high-D)")
@kind("certified_limit")
def _cl(p): return _readout("certified_limit", C.richardson(_seq(p["seq"]), _eps(p)), "Richardson with a-posteriori contraction certificate")
