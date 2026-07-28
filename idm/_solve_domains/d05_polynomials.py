# polynomials
from idm._solve_core import *  # noqa: F401,F403

@kind("poly_eval", "Th_coqc")
def _pe(p): return _ok("poly_eval", X.poly_eval(p["coeffs"], Fraction(str(p["x"]))), "Horner (exact ℚ)")
@kind("rational_roots", "Th_coqc")
def _rr(p): return _ok("rational_roots", X.rational_roots(p["coeffs"]), "rational-root theorem (exact)")
@kind("poly_roots")
def _prt(p): return _ok("poly_roots", AN.poly_roots(p["coeffs"]), "Durand–Kerner (all complex roots)")
