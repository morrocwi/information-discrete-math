"""Domain-parametrized polynomial tower (pillar P1.4, Wave 5).

``from idm.kernel import poly`` — coefficient rings (``QRing``/``ZRing``/``GFRing``) and univariate
polynomials (``UPoly`` + ``add``/``mul``/``divmod_``/``gcd``) whose result depends on the coefficient
ring, so the same computation means different things over ℚ[x], ℤ[x], and GF(p)[x]. Multivariate,
factorization, resultants, Gröbner, and algebraic/rational-function fields are later work.
"""

from __future__ import annotations

from .coeffring import DomainMismatch, QRing, ZRing, GFRing
from .univariate import UPoly, add, mul, divmod_, gcd, factor

__all__ = [
    "DomainMismatch", "QRing", "ZRing", "GFRing",
    "UPoly", "add", "mul", "divmod_", "gcd", "factor",
]
