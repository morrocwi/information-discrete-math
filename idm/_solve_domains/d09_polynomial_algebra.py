# polynomial algebra
from idm._solve_core import *  # noqa: F401,F403

@kind("poly_add", "Th_coqc")
def _pa(p): return _ok("poly_add", X.poly_add(p["a"], p["b"]), "exact ℚ")
@kind("poly_mul", "Th_coqc")
def _pmul(p): return _ok("poly_mul", X.poly_mul(p["a"], p["b"]), "exact ℚ convolution")
@kind("poly_divmod", "Th_coqc")
def _pdm(p): q, r = X.poly_divmod(p["a"], p["b"]); return _ok("poly_divmod", {"quotient": q, "remainder": r}, "exact ℚ long division")
@kind("poly_gcd", "Th_coqc")
def _pg(p): return _ok("poly_gcd", X.poly_gcd(p["a"], p["b"]), "Euclid over ℚ[x]")
@kind("poly_derivative", "Th_coqc")
def _pdv(p): return _ok("poly_derivative", X.poly_derivative(p["coeffs"]), "exact ℚ")
@kind("poly_integral", "Th_coqc")
def _pig(p): return _ok("poly_integral", X.poly_integral(p["coeffs"]), "exact ℚ (constant 0)")
@kind("poly_from_roots", "Th_coqc")
def _pfr(p): return _ok("poly_from_roots", X.poly_from_roots(p["roots"]), "∏(x−rᵢ) exact ℚ")
@kind("polynomial_positivity", "exact")
def _ppos(p):
    from idm import positivity as POS
    r = POS.positivity_certificate(str(p["polynomial"]), list(p["variables"]), p.get("domain", "R"))
    r["kind"] = "polynomial_positivity"
    return r
