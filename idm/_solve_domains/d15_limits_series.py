# limits & series
from idm._solve_core import *  # noqa: F401,F403

@kind("taylor_series")
def _tay(p): return _ok("taylor_series", SER.taylor_series(_fn(p["f"]), _val(p.get("x0", 0)), int(p.get("n", 8))),
                        "f^(k)(x0)/k! by centered finite differences + Richardson")
@kind("laurent_series")
def _lau(p):
    d = SER.laurent_series(_fn(p["f"]), _val(p.get("x0", 0)), int(p.get("lo", -3)), int(p.get("hi", 3)))
    return _ok("laurent_series", {str(k): v for k, v in d.items()}, "Cauchy coefficient FFT on a circle (complex-evaluable f)")
@kind("fourier_series")
def _fou(p): return _ok("fourier_series", SER.fourier_series(_fn(p["f"]), _val(p["period"]) if "period" in p else None, int(p.get("n", 8))),
                        "finite DFT of one period")
@kind("pade", "Th_coqc")
def _pade(p): return _ok("pade", SER.pade([Fraction(str(c)) for c in p["coeffs"]], int(p["m"]), int(p["n"])),
                         "Padé [m/n] from Taylor coefficients (exact ℚ)")
@kind("series_accelerate")
def _acc(p): return _ok("series_accelerate", SER.series_sum_accelerated(_seq0(p["term"]), int(p.get("N", 30))), "Wynn ε-algorithm")
@kind("convergence_test")
def _conv(p):
    v = SER.convergence_test(_seq(p["term"]), int(p.get("N", 600)))
    return {"kind": "convergence_test", "status": "ok" if v["verdict"] != "HOLD" else "HOLD", "value": v,
            "method": "nth-term → ratio → Raabe cascade (HOLD when genuinely inconclusive)"}
@kind("limit_oneside")
def _l1(p): return _ok("limit_oneside", SER.limit_oneside(_fn(p["f"]), _val(p["a"]), p.get("side", "+")), "Richardson plateau of f(a±1/n)")
@kind("limit_infinity")
def _linf(p): return _ok("limit_infinity", SER.limit_infinity(_fn(p["f"])), "Richardson on 1/n of f(n)")
@kind("lhopital")
def _lh(p): return _ok("lhopital", SER.lhopital(_fn(p["num"]), _fn(p["den"]), _val(p["a"])), "L'Hôpital via finite derivatives")
