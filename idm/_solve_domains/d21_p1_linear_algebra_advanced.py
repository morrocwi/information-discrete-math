# P1 — linear algebra (advanced)
from idm._solve_core import *  # noqa: F401,F403

@kind("matrix_exp")
def _mexp(p): return _ok("matrix_exp", X.matrix_exp(p["matrix"]), "e^A = Σ A^k/k! (finite series)")
@kind("null_space", "Th_coqc")
def _null(p): return _ok("null_space", X.null_space(p["matrix"]), "kernel basis from RREF (exact ℚ)")
@kind("hermite_normal_form", "Th_coqc")
def _hnf(p): return _ok("hermite_normal_form", X.hermite_normal_form(p["matrix"]), "column HNF (exact ℤ)")
@kind("smith_normal_form", "Th_coqc")
def _snf(p): return _ok("smith_normal_form", X.smith_normal_form(p["matrix"]), "invariant factors d₁|d₂|… (exact ℤ)")
