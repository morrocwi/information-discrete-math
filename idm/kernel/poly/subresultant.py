"""Subresultant polynomial remainder sequence over ℚ (pillar P1.4 extension).

The naive Euclidean PRS (repeatedly taking ``a mod b``) is the textbook definition of a polynomial
remainder sequence, but over ℤ its coefficients can explode super-exponentially in degree; Collins'
**subresultant PRS** fixes that by dividing each pseudo-remainder by a specific scalar (built from
previous leading coefficients and degree drops) so every term is *exactly* the corresponding
principal subresultant polynomial, at controlled coefficient size.

Over ℚ (a field, exact ``fractions.Fraction`` throughout) that coefficient-growth problem does not
exist: ``fractions.Fraction`` never "blows up" — it is always the exact reduced rational, regardless
of how large the underlying integers get. What is left of "subresultant PRS" over a field is its
*mathematical content*: each term of the sequence is the polynomial remainder of the previous two,
which is the principal subresultant of that degree **up to a nonzero rational scalar** (Collins'
extra scaling constant is itself just some nonzero rational once you are in a field — over ℚ,
``prem(A, B) == lead(B)**(deg A - deg B + 1) * (A mod B)`` exactly, so dividing by *any* nonzero
scalar, Collins' or the trivial one used here, still lands on a scalar multiple of the same
subresultant polynomial). That scalar is invisible to both operations this module exposes:

* :func:`gcd_prs` compares polynomials via ``.monic()``, which cancels any nonzero leading-coefficient
  scalar exactly.
* :func:`resultant_prs` does not read off "the" scaling constant from the sequence at all — it
  telescopes the classical resultant-reduction identity

  ``Res(f, g) = (-1)**(deg f * deg g) * lead(g)**(deg f - deg r) * Res(g, r)``,  where ``r = f mod g``

  down the chain to the base case ``Res(f, c) = c**deg(f)`` for a nonzero constant remainder ``c`` (or
  ``Res(f, g) = 0`` outright once the chain's last nonzero remainder still has positive degree — a
  nontrivial common factor, so every one of its roots, in the splitting field, is shared by both
  original polynomials and the Sylvester determinant vanishes). This identity is exact and scalar-
  convention independent by construction: it is derived from the root-product characterization
  ``Res(f, g) = lead(f)**deg(g) * prod(g(alpha_i) for alpha_i a root of f)``, not from any particular
  normalization of the remainder sequence.

So ``subresultant_prs`` here returns the exact-field Euclidean remainder chain — honestly documented
as differing from Collins' ℤ-normalized subresultant sequence only by a per-term nonzero rational
scalar that neither downstream operation depends on.
"""

from __future__ import annotations

from typing import List

from fractions import Fraction

from .coeffring import DomainMismatch, QRing
from .univariate import UPoly, divmod_


def _check_q(a: UPoly, b: UPoly) -> None:
    if a.domain != b.domain:
        raise DomainMismatch(f"{a.domain!r} vs {b.domain!r}")
    if not isinstance(a.domain, QRing):
        raise ValueError(f"subresultant PRS is implemented over QRing (ℚ) only; got {a.domain!r}")


def _require_both_degree_ge_1(a: UPoly, b: UPoly, who: str) -> None:
    if a.degree() < 1 or b.degree() < 1:
        raise ValueError(f"{who} requires both polynomials of degree >= 1")


def subresultant_prs(a: UPoly, b: UPoly) -> List[UPoly]:
    """The polynomial remainder sequence ``A0, A1, A2, ...`` with ``A0, A1 in {a, b}`` (ordered by
    non-increasing degree) and ``A_{i+1} = A_{i-1} mod A_i`` (exact field division), stopping at the
    last NONZERO term. See the module docstring for exactly what "subresultant" means here: each
    ``A_i`` (``i >= 2``) is the principal subresultant of its degree up to a nonzero rational scalar.

    Requires both ``a`` and ``b`` to have degree >= 1 over ``QRing`` (matching the existing
    ``univariate.resultant``'s own restriction) — raises ``ValueError`` otherwise rather than
    guessing at a degree-0 convention.
    """
    _check_q(a, b)
    _require_both_degree_ge_1(a, b, "subresultant_prs")
    seq = [a, b] if a.degree() >= b.degree() else [b, a]
    while True:
        prev, cur = seq[-2], seq[-1]
        _, r = divmod_(prev, cur)
        if r.is_zero():
            break
        seq.append(r)
    return seq


def resultant_prs(a: UPoly, b: UPoly):
    """``Res(a, b)`` computed FROM ``subresultant_prs(a, b)`` by telescoping the resultant-reduction
    identity down the chain (see module docstring for the identity and its base cases). Must equal
    ``univariate.resultant(a, b)`` (the Sylvester determinant) exactly for every input pair.
    """
    _check_q(a, b)
    _require_both_degree_ge_1(a, b, "resultant_prs")
    swapped = a.degree() < b.degree()
    seq = subresultant_prs(a, b)
    last = seq[-1]

    if last.degree() >= 1:
        # the chain's last nonzero remainder still has positive degree -> a nontrivial common
        # factor of (seq[0], seq[1]) (hence of a and b) -> the resultant is exactly zero.
        res = Fraction(0)
    else:
        c = last.coeffs[0]                       # the nonzero constant terminal remainder
        res = c ** seq[-2].degree()               # base case: Res(f, c) = c ** deg(f)
        for i in range(len(seq) - 3, -1, -1):      # telescope back up to Res(seq[0], seq[1])
            m = seq[i].degree()
            n = seq[i + 1].degree()
            k = seq[i + 2].degree()
            sign = -1 if (m * n) % 2 else 1
            res = sign * (seq[i + 1].lead() ** (m - k)) * res

    if swapped:
        sign2 = -1 if (a.degree() * b.degree()) % 2 else 1
        res = sign2 * res
    return res


def gcd_prs(a: UPoly, b: UPoly) -> UPoly:
    """``gcd(a, b)`` via the last nonzero term of ``subresultant_prs(a, b)``, returned MONIC (the
    scalar the subresultant convention leaves free is exactly what ``.monic()`` strips, so this is
    directly comparable to ``univariate.gcd(a, b)``, itself returned monic).
    """
    _check_q(a, b)
    _require_both_degree_ge_1(a, b, "gcd_prs")
    seq = subresultant_prs(a, b)
    return seq[-1].monic()


__all__ = ["subresultant_prs", "resultant_prs", "gcd_prs"]
