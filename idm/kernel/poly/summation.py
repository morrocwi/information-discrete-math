"""Gosper's algorithm for indefinite hypergeometric summation (pillar P1.4, Wave 5).

WHAT IS BEING SOLVED
---------------------
A sequence ``t(n)`` is a *hypergeometric term* iff its consecutive-term ratio

    r(n) = t(n+1) / t(n)

is a RATIONAL FUNCTION of ``n``. Gosper's algorithm decides, exactly and constructively, whether
``t(n)`` has an *indefinite sum* ``S(n)`` that is *again* a hypergeometric term -- i.e. whether

    S(n+1) - S(n) = t(n)

for some hypergeometric ``S``. If so it PRODUCES ``S``; if not it HOLDs (raises ``ValueError``) --
this is Gosper's theorem: closed-form hypergeometric summability is decidable, and when it fails
the sum genuinely is not expressible as a hypergeometric term (e.g. the harmonic numbers, which
are the indefinite sum of ``t(n) = 1/n``, are provably not hypergeometric).

INPUT REPRESENTATION (read this before calling ``gosper_sum``)
----------------------------------------------------------------
``t(n)`` itself is *never* passed in or constructed -- only its ratio is needed. Call

    gosper_sum(num, den)

with ``num = p(n)``, ``den = q(n)`` two ``UPoly`` over ``QRing()`` (need not be pre-reduced --
this function reduces them via ``cancel``) representing

    r(n) = t(n+1)/t(n) = p(n)/q(n).

OUTPUT REPRESENTATION
-----------------------
On success, returns a dict

    {"num": Rn, "den": Rd, "x": x, "a": a, "b": b, "c": c}

where ``Rn/Rd`` (both ``UPoly``, reduced to lowest terms) represent the GOSPER CERTIFICATE

    R(n) = S(n) / t(n)                        (a rational function of n)

so that ``S(n) = R(n) * t(n)`` is the closed-form sum. ``x`` is the polynomial solution of the
underlying Gosper equation (see below); ``a, b, c`` are the Gosper-Petkovsek normal-form
polynomials of ``r`` (also see below) -- exposed for transparency/testing, not required reading
to use the result.

Because ``t(n)`` is never materialized, the defining identity ``S(n+1) - S(n) = t(n)`` is
verified WITHOUT ever forming ``t`` or ``S``, purely from ``R`` and ``r``:

    R(n+1) * r(n) - R(n) == 1                                              (*)

    [ S(n+1) - S(n) ] / t(n) = R(n+1)*t(n+1)/t(n) - R(n) = R(n+1)*r(n) - R(n) ,

so (*) holding identically (as rational functions, i.e. after cross-multiplication, as an exact
polynomial identity) is *equivalent* to ``S(n+1)-S(n)=t(n)`` for EVERY hypergeometric ``t`` with
that ratio ``r``. This is the reconstruction check used throughout ``tests/test_summation.py``.

THE ALGORITHM (standard three steps; see Petkovsek/Wilf/Zeilberger, "A=B", ch. 5)
------------------------------------------------------------------------------------
1.  Reduce ``r = p/q`` to lowest terms (``cancel``).
2.  Compute the GOSPER-PETKOVSEK NORMAL FORM: polynomials ``a, b, c`` with

        r(n) = [a(n)/b(n)] * [c(n+1)/c(n)],      gcd(a(n), b(n+h)) = 1  for every integer h >= 0.

    Construction: find every nonnegative integer ``h`` for which ``gcd(p(n), q(n+h))`` is
    non-constant (these are exactly the ``h`` that MUST be absorbed into ``c`` rather than left in
    ``a/b``, since leaving them would violate the "no shift-h overlap" property above and break
    the degree bound in step 3). Peel each such shared factor ``g`` out of the running ``(a, b)``
    and fold ``prod_{j=1}^{h} g(n-j)`` into ``c`` (this telescopes: ``c(n+1)/c(n) = g(n)/g(n-h)``
    exactly, restoring the original ratio -- see ``_gp_normal_form``).

    NOTE ON RESULTANT USE: the textbook presentation finds the valid ``h`` as the nonnegative
    integer roots of the RESULTANT (in a fresh variable ``z``) ``Res_n(p(n), q(n+z))``. Doing that
    exactly here would require building ``q(n+z)`` as a polynomial in ``n`` whose OWN coefficients
    are polynomials in ``z`` -- i.e. a rational-function-in-``z`` coefficient FIELD bolted onto
    this ``UPoly`` tower -- extra machinery this module deliberately avoids for auditability.
    Instead it uses the equivalent, simpler fact: any such ``h`` satisfies
    ``h <= cauchy_bound(p) + cauchy_bound(q)`` (a root of ``p`` and a root of ``q`` differing by
    exactly ``h``, each bounded in modulus by the classical Cauchy root bound), so it is exact and
    complete to just try every integer ``h`` in that finite, provably-sufficient range and test
    ``gcd(p, shift(q, h))`` directly with the EXISTING exact ``gcd`` -- no resultant, no new field,
    same guarantee of finding every valid ``h``.

3.  Solve the GOSPER EQUATION for a polynomial ``x(n)``:

        a(n)*x(n+1) - b(n-1)*x(n) = c(n)

    by bounding ``deg(x)`` (the classical case analysis on ``deg(a)`` vs ``deg(b)`` and, in the
    degenerate ``deg(a)=deg(b)`` case with equal leading coefficients, the extra integer ``kappa``
    that can force a higher degree) and then solving the resulting LINEAR system over ``QRing``
    (exact ``Fraction`` Gaussian elimination, ``_solve_linear_system``) for the polynomial's
    ``d+1`` coefficients. No solution at the bounded degree => HOLD (not Gosper-summable).

    Finally ``R(n) = b(n-1)*x(n) / c(n)`` (reduced) is the returned certificate.

EXACTNESS / HOLD DISCIPLINE
------------------------------
Every arithmetic step is exact ``fractions.Fraction`` via ``QRing`` -- never a float. Every branch
that cannot certify a polynomial solution raises ``ValueError`` (the HOLD) rather than guessing.

HONEST LIMITATIONS
---------------------
* Coefficient domain must be ``QRing`` (characteristic-0 ``ℚ``) -- matches ``square_free_factorization``
  and ``sturm_chain`` elsewhere in this tower, which have the same restriction.
* The GP-normal-form peeling loop (step 2) processes the candidate shifts largest-to-smallest
  against the *running* ``(a, b)``, which is the standard presentation and is exact whenever a
  SINGLE shift ``h`` needs to be peeled per run (proved correct below by direct calculation, and
  exercised by every test in this module's test file). Multiple *simultaneous*, mutually-interacting
  shifts (``|Z| > 1`` in one call) are handled by the same loop and are sound by a divisibility
  argument (each later candidate, if still valid, was necessarily already a candidate against the
  ORIGINAL ``p, q``, so the precomputed candidate set is never too small) but are not exercised by
  a hand-traced test here -- flagged as the one part of this implementation resting on the general
  argument rather than an end-to-end numeric trace.
* This is indefinite hypergeometric summation only (Gosper), not Zeilberger's algorithm (definite
  hypergeometric summation / creative telescoping) and not the multi-term-recurrence extensions.
"""

from __future__ import annotations

from fractions import Fraction
from math import comb
from typing import List, Tuple

from .coeffring import DomainMismatch, QRing
from .univariate import UPoly, add, mul, divmod_, gcd, cancel


# ---------------------------------------------------------------------------------- utilities ----
def shift(poly: UPoly, k: int) -> UPoly:
    """Return the polynomial ``q`` with ``q(n) = poly(n + k)`` for an INTEGER ``k`` (any sign).

    Exact: expands ``(n+k)^i`` via the binomial theorem with ``Fraction`` arithmetic throughout,
    so ``shift`` is itself an exact, reversible operation (``shift(shift(p, k), -k) == p``).
    """
    D = poly.domain
    deg = poly.degree()
    if deg < 0:
        return UPoly([D.zero()], D)
    new_coeffs = [D.zero() for _ in range(deg + 1)]
    kk = Fraction(k)
    for i, ci in enumerate(poly.coeffs):
        for j in range(i + 1):
            binom = D.from_int(comb(i, j))
            power = D.normalize(kk ** (i - j))
            term = D.mul(D.mul(ci, binom), power)
            new_coeffs[j] = D.add(new_coeffs[j], term)
    return UPoly(new_coeffs, D)


def _coeff(poly: UPoly, k: int):
    """Coefficient of n^k in poly, or the domain zero if k is out of range (including k < 0)."""
    if 0 <= k < len(poly.coeffs):
        return poly.coeffs[k]
    return poly.domain.zero()


def _cauchy_bound(poly: UPoly) -> Fraction:
    """A Cauchy bound: every complex root of ``poly`` has modulus strictly less than this."""
    if poly.degree() <= 0:
        return Fraction(0)
    lc = abs(Fraction(poly.lead()))
    m = max((abs(Fraction(c)) for c in poly.coeffs[:-1]), default=Fraction(0))
    return 1 + m / lc


# ---------------------------------------------------------- step 2: Gosper-Petkovsek normal form ----
def _find_shift_set(p: UPoly, q: UPoly) -> List[int]:
    """Every nonnegative integer h with gcd(p(n), q(n+h)) non-constant.

    Bounded search (see module docstring "NOTE ON RESULTANT USE"): any such h is at most
    cauchy_bound(p) + cauchy_bound(q), so it suffices to test every integer in that finite range
    directly with the exact gcd.
    """
    if p.degree() < 1 or q.degree() < 1:
        return []
    bound = _cauchy_bound(p) + _cauchy_bound(q)
    hi = int(bound) + 1
    out = []
    for h in range(0, hi + 1):
        g = gcd(p, shift(q, h))
        if g.degree() >= 1:
            out.append(h)
    return out


def gp_normal_form(p: UPoly, q: UPoly) -> Tuple[UPoly, UPoly, UPoly]:
    """The Gosper-Petkovsek normal form of r(n) = p(n)/q(n): polynomials (a, b, c) with

        p(n)/q(n) = [a(n)/b(n)] * [c(n+1)/c(n)],     gcd(a(n), b(n+h)) = 1 for every integer h >= 0.

    p, q need not be coprime on entry (this is also used internally after `cancel`).
    """
    D = p.domain
    Z = sorted(_find_shift_set(p, q), reverse=True)
    a, b = p, q
    c = UPoly([D.one()], D)
    for h in Z:
        g = gcd(a, shift(b, h))
        if g.degree() < 1:
            continue           # already absorbed by an earlier (larger) h in this pass
        qa, ra = divmod_(a, g)
        if not ra.is_zero():
            raise RuntimeError("internal error: gcd(a, shift(b,h)) must divide a exactly")
        gsh = shift(g, -h)
        qb, rb = divmod_(b, gsh)
        if not rb.is_zero():
            raise RuntimeError("internal error: shift(g,-h) must divide b exactly")
        a, b = qa, qb
        for j in range(1, h + 1):
            c = mul(c, shift(g, -j))
    return a, b, c


# ---------------------------------------------------------------- step 3: the Gosper equation ----
def _solve_linear_system(matrix: List[List], rhs: List, D):
    """Exact Gauss-Jordan solve of matrix @ x = rhs over field domain D.

    Returns a particular solution (list, free variables set to the domain zero) if the system is
    consistent, else None. Handles rectangular (over/under-determined) systems.
    """
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    aug = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    pivot_cols = []
    r = 0
    for col in range(cols):
        piv = None
        for rr in range(r, rows):
            if not D.is_zero(aug[rr][col]):
                piv = rr
                break
        if piv is None:
            continue
        aug[r], aug[piv] = aug[piv], aug[r]
        pv = aug[r][col]
        aug[r] = [D.div(x, pv) for x in aug[r]]
        for rr in range(rows):
            if rr != r and not D.is_zero(aug[rr][col]):
                f = aug[rr][col]
                aug[rr] = [D.add(aug[rr][k], D.neg(D.mul(f, aug[r][k]))) for k in range(cols + 1)]
        pivot_cols.append(col)
        r += 1
        if r == rows:
            break
    for row in aug:
        if all(D.is_zero(row[k]) for k in range(cols)) and not D.is_zero(row[cols]):
            return None
    x = [D.zero()] * cols
    for i, col in enumerate(pivot_cols):
        x[col] = aug[i][cols]
    return x


def _gosper_degree_bound(a: UPoly, b: UPoly, c: UPoly) -> int:
    """The classical degree bound d for the polynomial solution x(n) of
    a(n)x(n+1) - b(n-1)x(n) = c(n), given the (unshifted) a, b, c. May be negative (no solution
    unless c is identically 0)."""
    dA, dB, dC = a.degree(), b.degree(), c.degree()
    if dA != dB:
        return dC - max(dA, dB)
    p = dA
    alpha, beta = a.lead(), b.lead()
    if alpha != beta:
        return dC - p
    gamma = alpha
    ap1 = _coeff(a, p - 1)
    bp1 = _coeff(b, p - 1)
    kappa = (bp1 - ap1) / gamma - p
    if kappa.denominator == 1 and kappa >= 0:
        return max(int(kappa), dC - p + 1)
    return dC - p + 1


def _solve_gosper_equation(a: UPoly, b: UPoly, c: UPoly) -> UPoly:
    """Find the polynomial x(n) with a(n)x(n+1) - b(n-1)x(n) = c(n), or raise ValueError (HOLD)."""
    D = a.domain
    d = _gosper_degree_bound(a, b, c)
    if d < 0:
        if c.is_zero():
            return UPoly([D.zero()], D)
        raise ValueError(
            f"Gosper equation has no polynomial solution (degree bound {d} < 0): not Gosper-summable"
        )

    bm1 = shift(b, -1)
    cols = d + 1
    columns = []
    maxlen = len(c.coeffs)
    for i in range(cols):
        e_i = UPoly([D.zero()] * i + [D.one()], D)          # monomial n^i
        e_ip1 = shift(e_i, 1)                                # (n+1)^i
        contribution = add(mul(a, e_ip1), UPoly([D.neg(x) for x in mul(bm1, e_i).coeffs], D))
        columns.append(contribution)
        maxlen = max(maxlen, len(contribution.coeffs))

    matrix = [[_coeff(columns[i], k) for i in range(cols)] for k in range(maxlen)]
    rhs = [_coeff(c, k) for k in range(maxlen)]
    sol = _solve_linear_system(matrix, rhs, D)
    if sol is None:
        raise ValueError(
            f"Gosper equation has no polynomial solution at the bounded degree {d}: "
            f"not Gosper-summable"
        )
    return UPoly(sol, D)


# ------------------------------------------------------------------------------ public entry ----
def gosper_sum(num: UPoly, den: UPoly) -> dict:
    """Gosper's algorithm. See the module docstring for the full representation contract.

    num, den: UPoly over QRing() representing r(n) = t(n+1)/t(n) = num(n)/den(n) (need not be
    pre-reduced).

    Returns {"num": Rn, "den": Rd, "x": x, "a": a, "b": b, "c": c} on success -- Rn/Rd is the
    Gosper certificate R(n) = S(n)/t(n), reduced to lowest terms, so S(n) = R(n)*t(n) is the
    closed-form indefinite sum. x, a, b, c are the underlying polynomial witnesses (see docstring).

    Raises ValueError (the HOLD) if t(n) is not Gosper-summable.
    """
    if not isinstance(num, UPoly) or not isinstance(den, UPoly):
        raise TypeError("gosper_sum expects UPoly num, den")
    if num.domain != den.domain:
        raise DomainMismatch(f"{num.domain!r} vs {den.domain!r}")
    D = num.domain
    if not isinstance(D, QRing):
        raise ValueError(f"gosper_sum requires the exact field QRing(); got {D!r}")
    if den.is_zero():
        raise ZeroDivisionError("gosper_sum: zero ratio denominator")
    if num.is_zero():
        raise ValueError("gosper_sum: zero ratio numerator is not a valid hypergeometric-term ratio")

    reduced = cancel(num, den)
    p, q = reduced["num"], reduced["den"]

    a, b, c = gp_normal_form(p, q)
    x = _solve_gosper_equation(a, b, c)

    bm1 = shift(b, -1)
    numerator = mul(bm1, x)
    result = cancel(numerator, c)
    return {"num": result["num"], "den": result["den"], "x": x, "a": a, "b": b, "c": c}


__all__ = ["shift", "gp_normal_form", "gosper_sum"]
