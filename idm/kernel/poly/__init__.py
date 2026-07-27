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

__all__ = [
    "DomainMismatch", "QRing", "ZRing", "GFRing",
    "UPoly", "add", "mul", "divmod_", "gcd", "factor",
    "derivative", "cancel", "resultant", "discriminant",
    "sturm_chain", "count_real_roots", "isolate_real_roots", "square_free_factorization",
    "PartialFraction", "apart", "together", "extended_gcd", "gosper_sum",
    "characteristic_polynomial", "real_eigenvalues",
]
