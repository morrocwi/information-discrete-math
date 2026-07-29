"""idm.convenience — typed one-call wrappers over :func:`idm.solve`.

Each wrapper builds the structured ``{"kind": ...}`` problem for a common task and returns a
:class:`idm.results.Result`, so a programmer can write ``idm.factorize(360360).value`` instead of
hand-assembling the dict and remembering the exact field names. These are thin, honest shims — they add
no math and no new kind; every one dispatches through the same ``solve`` the REST server and CI use.
"""
from __future__ import annotations

from .solve import solve


def factorize(n):
    """Prime factorization of an integer ``n`` (kind ``factorize``, ``Th_coqc``)."""
    return solve({"kind": "factorize", "n": n})


def gcd(a, b):
    """Greatest common divisor of integers ``a``, ``b`` (kind ``gcd``, ``Th_coqc``)."""
    return solve({"kind": "gcd", "a": a, "b": b})


def solve_integral(f, a, b, eps=1e-8):
    """Certified definite integral ``∫_a^b f dx`` to tolerance ``eps`` (kind ``integral``). ``f`` is an
    expression string; ``a``/``b`` are numbers or strings."""
    return solve({"kind": "integral", "f": f, "a": a, "b": b, "eps": eps})


def integrate_rational(num, den):
    """Exact symbolic ∫ of a rational function ``num(x)/den(x)`` (coeffs low→high, kind
    ``integrate_rational``)."""
    return solve({"kind": "integrate_rational", "num": num, "den": den})


def solve_matrix(A, b):
    """The complete exact ℚ solution set of ``A x = b`` — unique, an infinite family, or inconsistent
    (kind ``matrix_solve``)."""
    return solve({"kind": "matrix_solve", "A": A, "b": b})


def eigenvalues(matrix):
    """Eigenvalues of a rational ``matrix`` (kind ``eigenvalues``). For exact algebraic eigenvalues with
    multiplicity use ``solve({"kind": "exact_eigenvalues", ...})``."""
    return solve({"kind": "eigenvalues", "matrix": matrix})


def solve_roots(coeffs):
    """Every root (real AND complex) of a ℚ-polynomial as exact enclosures, with multiplicity (coeffs
    low→high, kind ``all_roots``). HOLDs (never hangs) on very large-coefficient high-degree inputs."""
    return solve({"kind": "all_roots", "coeffs": coeffs})


def solve_ode(coeffs):
    """Exact general solution of a linear constant-coefficient homogeneous ODE from its characteristic
    coefficients (low→high, kind ``linear_ode``)."""
    return solve({"kind": "linear_ode", "coeffs": coeffs})


__all__ = ["factorize", "gcd", "solve_integral", "integrate_rational", "solve_matrix",
           "eigenvalues", "solve_roots", "solve_ode"]
