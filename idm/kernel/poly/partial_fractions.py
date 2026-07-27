"""Square-free partial fraction decomposition over ℚ (pillar P1.4, on top of Wave 5's UPoly tower).

``apart(num, den)`` decomposes a rational function ``num/den`` exactly (fractions.Fraction only, never
a float) into

    num/den  =  poly  +  Σ_i Σ_{j=1..m_i}  A_{i,j}(x) / g_i(x)^j

where ``den = lead · ∏ g_i^{m_i}`` is the **square-free** factorization of ``den``
(:func:`idm.kernel.poly.univariate.square_free_factorization`) — each ``g_i`` monic, square-free, and
pairwise coprime — and every numerator ``A_{i,j}`` has degree strictly less than ``deg(g_i)``.

This is *square-free* partial fractions, not full irreducible partial fractions: distinct
coprime irreducible factors that happen to share the same multiplicity are combined into one
square-free block ``g_i`` and are **not** split further into one term per irreducible factor. That is
intentional and matches the task's own scope note — square-free is enough; we never claim (or need) a
full irreducible factorization over ℚ, which is a much harder, separate problem.

Method
------
1. Polynomial division ``num = q·den + r`` (``divmod_``) peels off the improper part; everything below
   works on the strictly-proper remainder ``r`` (``deg r < deg den``).
2. ``square_free_factorization(den)`` gives ``lead`` and monic pairwise-coprime ``g_i`` with
   multiplicities ``m_i``. Write ``h_i = g_i^{m_i}`` — the ``h_i`` are pairwise coprime too.
3. **Multi-denominator split** (CRT-style, via the *extended Euclidean algorithm* / Bezout identity
   built here from ``divmod_``): iteratively peel one ``h_i`` at a time off the running coprime product
   using ``s·h_i + t·rest = 1``, which gives ``current/(h_i·rest) = current·t/h_i + current·s/rest``
   — an EXACT rational-function identity at every step, regardless of numerator degree. Reducing each
   raw numerator modulo its ``h_i`` (via ``divmod_``) yields a proper numerator *and* a polynomial
   remainder that is folded back into the overall polynomial part — so the final ``poly`` is correct by
   construction, with no separate cancellation argument needed.
4. **Single-denominator split**: for each proper numerator ``rem_i`` over ``h_i = g_i^{m_i}``, a
   "digit expansion in base ``g_i``" (repeated ``divmod_`` by ``g_i``) writes
   ``rem_i = Σ_{k=0}^{m_i-1} d_k · g_i^k`` with every ``deg d_k < deg g_i``; dividing through by
   ``g_i^{m_i}`` gives ``A_{i,j} = d_{m_i - j}`` for ``j = 1..m_i``.

``together(decomposition)`` recombines a decomposition back into a single ``(num, den)`` pair over a
common denominator, purely from the decomposition's own data (it does not need the original
``num``/``den``) — an independent reconstruction used to verify ``apart`` by cross-multiplication.

Honest limitations (HOLD, not silent wrong answers)
----------------------------------------------------
- Coefficients must live in ``QRing`` (ℚ) — the same restriction ``square_free_factorization`` already
  carries (characteristic-0 field). Any other domain raises ``ValueError``.
- ``den`` must be nonzero (``ValueError`` otherwise) and must share ``num``'s domain (``ValueError`` on
  mismatch).
- No further splitting of a square-free block into irreducible factors is attempted — see the "square-free
  is enough" note above. Callers wanting fully split partial fractions (e.g. one term per linear factor)
  need a separate irreducible-factorization layer this module does not provide.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from .coeffring import QRing
from .univariate import UPoly, add, mul, divmod_, square_free_factorization


# ---------------------------------------------------------------------------------------- small helpers

def _neg_poly(p: UPoly) -> UPoly:
    D = p.domain
    return UPoly([D.neg(c) for c in p.coeffs], D)


def _sub(a: UPoly, b: UPoly) -> UPoly:
    return add(a, _neg_poly(b))


def _one(D) -> UPoly:
    return UPoly([D.one()], D)


def _zero(D) -> UPoly:
    return UPoly([D.zero()], D)


def _power(g: UPoly, m: int) -> UPoly:
    """g^m by repeated multiplication (m >= 0)."""
    D = g.domain
    acc = _one(D)
    for _ in range(m):
        acc = mul(acc, g)
    return acc


# ---------------------------------------------------------------------------------------- extended Euclid

def extended_gcd(a: UPoly, b: UPoly) -> Tuple[UPoly, UPoly, UPoly]:
    """The extended Euclidean algorithm over a field domain, built from ``divmod_``/``mul``/``add``.

    Returns ``(s, t, g)`` with ``s·a + t·b == g == gcd(a, b)`` EXACTLY (``g`` is whatever
    ``divmod_``'s Euclidean remainder chain produces — not necessarily monic; callers that need a
    normalized Bezout identity, e.g. ``s·a + t·b == 1`` for coprime inputs, should scale by
    ``1/g.lead()`` themselves — :func:`_bezout_one` below does exactly that).
    """
    D = a.domain
    if a.domain != b.domain:
        raise ValueError(f"extended_gcd: domain mismatch {a.domain!r} vs {b.domain!r}")
    r0, r1 = a, b
    s0, s1 = _one(D), _zero(D)
    t0, t1 = _zero(D), _one(D)
    while not r1.is_zero():
        q, rem = divmod_(r0, r1)
        r0, r1 = r1, rem
        s0, s1 = s1, _sub(s0, mul(q, s1))
        t0, t1 = t1, _sub(t0, mul(q, t1))
    return s0, t0, r0


def _bezout_one(a: UPoly, b: UPoly) -> Tuple[UPoly, UPoly]:
    """``s, t`` with ``s·a + t·b == 1``, given ``a`` and ``b`` are coprime (their gcd is a nonzero
    constant). Raises ``ValueError`` if they are not actually coprime — a defensive check; the only
    caller (``apart``) only ever invokes this on distinct square-free blocks ``h_i``, which are
    pairwise coprime by construction of :func:`square_free_factorization`.
    """
    D = a.domain
    s, t, g = extended_gcd(a, b)
    if g.degree() != 0:
        raise ValueError("_bezout_one: inputs are not coprime (gcd has positive degree)")
    inv = D.div(D.one(), g.coeffs[0])
    scale = lambda p: UPoly([D.mul(c, inv) for c in p.coeffs], D)
    return scale(s), scale(t)


# ---------------------------------------------------------------------------------------- decomposition

@dataclass
class PartialFraction:
    """``num/den == poly + Σ A/g^j`` for each ``(g, j, A)`` in ``terms`` (``deg A < deg g`` always)."""
    poly: UPoly
    terms: List[Tuple[UPoly, int, UPoly]]


def apart(num: UPoly, den: UPoly) -> PartialFraction:
    """Square-free partial fraction decomposition of ``num/den`` over ℚ. See module docstring."""
    if den.domain != num.domain:
        raise ValueError(f"apart: numerator/denominator domain mismatch {num.domain!r} vs {den.domain!r}")
    D = den.domain
    if not isinstance(D, QRing):
        raise ValueError(f"apart: square-free partial fractions need QRing (ℚ); got {D!r}")
    if den.is_zero():
        raise ValueError("apart: zero denominator")

    quotient, r = divmod_(num, den)          # num = quotient*den + r, deg r < deg den
    lead, factors = square_free_factorization(den)   # den = lead * prod g_i^m_i, g_i monic square-free

    # r/den == (r/lead)/f  where f = den/lead is monic == prod g_i^m_i
    r_scaled = UPoly([D.div(c, lead) for c in r.coeffs], D)

    h_list = [(g, m, _power(g, m)) for (g, m) in factors]   # h_i = g_i^m_i

    poly_part = quotient
    proper_terms: List[Tuple[UPoly, int, UPoly, UPoly]] = []   # (g_i, m_i, h_i, raw numerator over h_i)

    if len(h_list) == 1:
        g, m, h = h_list[0]
        proper_terms.append((g, m, h, r_scaled))
    elif len(h_list) >= 2:
        current = r_scaled
        for idx in range(len(h_list) - 1):
            g_i, m_i, h_i = h_list[idx]
            rest = _one(D)
            for (_, _, hh) in h_list[idx + 1:]:
                rest = mul(rest, hh)
            s, t = _bezout_one(h_i, rest)      # s*h_i + t*rest == 1
            proper_terms.append((g_i, m_i, h_i, mul(current, t)))
            current = mul(current, s)
        g_last, m_last, h_last = h_list[-1]
        proper_terms.append((g_last, m_last, h_last, current))
    # len(h_list) == 0: den is a nonzero constant times 1 -- r must already be 0, nothing to split.

    terms: List[Tuple[UPoly, int, UPoly]] = []
    for g, m, h, raw_num in proper_terms:
        q_i, rem_i = divmod_(raw_num, h)       # raw_num = q_i*h + rem_i, deg rem_i < deg h
        poly_part = add(poly_part, q_i)        # exact identity: folds any "leftover" quotient back in

        # digit expansion of rem_i in base g: rem_i = sum_k digits[k] * g^k, deg digits[k] < deg g
        cur = rem_i
        digits: List[UPoly] = []
        for _ in range(m):
            qd, rd = divmod_(cur, g)
            digits.append(rd)
            cur = qd
        for j in range(1, m + 1):
            A = digits[m - j]
            if not A.is_zero():
                terms.append((g, j, A))

    return PartialFraction(poly=poly_part, terms=terms)


def together(decomposition: PartialFraction) -> Tuple[UPoly, UPoly]:
    """Recombine a :class:`PartialFraction` back into a single ``(num, den)`` pair over a common
    denominator — built only from ``decomposition`` itself (an independent reconstruction path used to
    verify ``apart`` by cross-multiplication against the original ``num``/``den``).
    """
    poly = decomposition.poly
    terms = decomposition.terms
    D = poly.domain

    if not terms:
        return poly, _one(D)

    # group terms by g_i (UPoly has no __hash__, so key on its coefficient tuple)
    order: List[tuple] = []
    groups: dict = {}
    for g, j, A in terms:
        key = tuple(g.coeffs)
        if key not in groups:
            groups[key] = {"g": g, "items": {}}
            order.append(key)
        groups[key]["items"][j] = A

    group_list = []
    common_den = _one(D)
    for key in order:
        g = groups[key]["g"]
        items = groups[key]["items"]
        maxj = max(items.keys())
        h = _power(g, maxj)
        group_list.append((g, h, maxj, items))
        common_den = mul(common_den, h)

    total_num = _zero(D)
    for i, (g, h, maxj, items) in enumerate(group_list):
        # numerator of this group's contribution over its own h = g^maxj
        N = _zero(D)
        for j, A in items.items():
            N = add(N, mul(A, _power(g, maxj - j)))
        # the rest of the common denominator (product of every OTHER group's h)
        other = _one(D)
        for k, (_, h2, _, _) in enumerate(group_list):
            if k != i:
                other = mul(other, h2)
        total_num = add(total_num, mul(N, other))

    full_num = add(mul(poly, common_den), total_num)
    return full_num, common_den


__all__ = ["PartialFraction", "apart", "together", "extended_gcd"]
