"""Domain-parametrized polynomial tower (pillar P1.4, Wave 5).

``from idm.kernel import poly`` — coefficient rings (``QRing``/``ZRing``/``GFRing``) and univariate
polynomials (``UPoly`` + ``add``/``mul``/``divmod_``/``gcd``) whose result depends on the coefficient
ring, so the same computation means different things over ℚ[x], ℤ[x], and GF(p)[x]. Multivariate,
factorization, resultants, Gröbner, and algebraic/rational-function fields are later work.
"""

from __future__ import annotations

from .coeffring import DomainMismatch, QRing, ZRing, GFRing
from .univariate import (
    UPoly, add, mul, divmod_, gcd, factor, derivative, cancel, resultant, discriminant,
    sturm_chain, count_real_roots, isolate_real_roots, square_free_factorization,
)
from .partial_fractions import PartialFraction, apart, together, extended_gcd
from .summation import gosper_sum
from .eigen import characteristic_polynomial, real_eigenvalues
from .subresultant import subresultant_prs, resultant_prs, gcd_prs
from .interpolate import lagrange, newton
from .matrix_minpoly import minimal_polynomial, eval_poly_at_matrix
from .factorize import factor_over_Q
from .linsolve import LinearSolution, rref, linear_solve, matvec
from .limits import LimitResult, rational_limit, rational_limit_oneside
from .ode_linear import ODESolution, solve_linear_ode

__all__ = [
    "DomainMismatch", "QRing", "ZRing", "GFRing",
    "UPoly", "add", "mul", "divmod_", "gcd", "factor",
    "derivative", "cancel", "resultant", "discriminant",
    "sturm_chain", "count_real_roots", "isolate_real_roots", "square_free_factorization",
    "PartialFraction", "apart", "together", "extended_gcd", "gosper_sum",
    "characteristic_polynomial", "real_eigenvalues",
    "subresultant_prs", "resultant_prs", "gcd_prs", "lagrange", "newton",
    "minimal_polynomial", "eval_poly_at_matrix", "factor_over_Q",
    "LinearSolution", "rref", "linear_solve", "matvec",
    "LimitResult", "rational_limit", "rational_limit_oneside",
    "ODESolution", "solve_linear_ode",
]
