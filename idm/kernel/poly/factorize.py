"""Full factorization of a univariate polynomial over ℚ into IRREDUCIBLE factors, EXACT
(pillar P1.4, independent attempt C).

Builds ``factor_over_Q`` purely by composing exact building blocks already in :mod:`univariate` and
:mod:`interpolate` — no modular arithmetic, no GF(p) reduction, no Hensel lifting, and never a float:

  1. :func:`~idm.kernel.poly.univariate.square_free_factorization` (Yun's algorithm) peels ``p`` into
     ``lead(p) · ∏ gᵢ^i`` with each ``gᵢ`` monic, square-free, and pairwise coprime. This is where all
     multiplicities come from — everything downstream only ever sees a SQUARE-FREE cofactor, and a
     divisor of a square-free polynomial is itself square-free, so no step below ever has to worry
     about repeated factors.

  2. Each square-free monic ``gᵢ`` is split into its DISTINCT monic irreducible factors by
     :func:`_factor_monic`:

       - FAST PATH — :func:`~idm.kernel.poly.univariate.factor` pulls out ``(x - r)`` for every
         RATIONAL root ``r`` (rational-root theorem, exact), to full multiplicity (here always 1,
         since ``gᵢ`` is square-free).
       - KRONECKER — whatever remains (degree ``d ≥ 2``, provably no rational root) is split by the
         classical bounded-degree divisor method, the one genuinely new technique this module adds:
         for trial degree ``e = 1 .. ⌊d/2⌋`` pick ``e + 1`` small integer nodes ``0, 1, -1, 2, -2, …``;
         clear denominators of the cofactor to get an INTEGER-coefficient polynomial ``F`` with the
         same roots (and hence the same factor structure, up to the constant that was cleared); every
         genuine integer-coefficient factor of ``F`` must send each node to a value dividing ``F`` at
         that node (`h(xᵢ) | F(xᵢ)`), so enumerate every tuple of divisors (both signs) of the node
         values, interpolate each tuple to a candidate polynomial (exact Lagrange interpolation through
         those ``e+1`` points — the unique polynomial of degree ``< e+1`` through them), and accept a
         candidate iff it is nonconstant, has degree exactly ``e``, and — the ONLY proof obligation that
         actually matters — divides the (monic, rational) cofactor with EXACT zero remainder under
         :func:`~idm.kernel.poly.univariate.divmod_`. If a node value is ``0`` the node itself is an
         (unexpected, but handled) rational root, handled directly as a linear factor. If no candidate
         at any degree ``e ≤ ⌊d/2⌋`` divides the cofactor, the cofactor is IRREDUCIBLE over ℚ — a
         reducible polynomial always has a factor of degree ``≤ ⌊d/2⌋`` on at least one side of any
         split, so exhausting that range without a hit is a genuine proof, not a heuristic stop.
         Interpolation only ever GENERATES a candidate; the exact ``divmod_`` zero-remainder check is
         what actually certifies it as a factor, so a gap in candidate coverage could at worst report
         "irreducible" for something reducible (caught by the reconstruction/irreducibility tests),
         never accept a wrong factor.

Every accepted split immediately re-derives monic factors (`h.monic()`, and the matching cofactor from
`divmod_`, which is monic automatically because `lead(h) · lead(cofactor) = lead(f) = 1`), so the
product identity is exact and verifiable at every level, not just at the end.
"""

from __future__ import annotations

from itertools import product as _product
from math import gcd as _int_gcd
from typing import List, Optional, Tuple

from .coeffring import QRing
from .univariate import UPoly, divmod_, factor, square_free_factorization
from .interpolate import lagrange


# =============================================================================================== helpers
def _kronecker_nodes(count: int) -> List[int]:
    """The first ``count`` Kronecker evaluation nodes: ``0, 1, -1, 2, -2, …`` — small integers, kept
    small on purpose so the node VALUES (and hence their divisor lists) stay small too."""
    nodes = [0]
    k = 1
    while len(nodes) < count:
        nodes.append(k)
        if len(nodes) < count:
            nodes.append(-k)
        k += 1
    return nodes


def _signed_divisors(n: int) -> List[int]:
    """Every divisor of the nonzero integer ``n``, both signs. ``n == 0`` is a caller error — a node
    value of 0 means that node is itself a root, and the caller handles that case separately (every
    integer "divides" 0, so an infinite list would be the only honest answer here)."""
    n = abs(n)
    if n == 0:
        raise ValueError("_signed_divisors(0) is undefined")
    small: List[int] = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            small.append(i)
            if i != n // i:
                small.append(n // i)
        i += 1
    out: List[int] = []
    for d in small:
        out.append(d)
        out.append(-d)
    return out


def _clear_denominators(f: UPoly) -> UPoly:
    """A ``UPoly`` with INTEGER (as ``Fraction`` with denominator 1) coefficients, PRIMITIVE (integer
    content 1), and the exact same roots as ``f`` — obtained by multiplying ``f`` through by the LCM
    of its coefficients' denominators, then dividing out the integer content. Used only to compute
    small, honest node values for the Kronecker divisor search; every candidate it produces is still
    independently verified by an exact ``divmod_`` against the ORIGINAL cofactor ``f``, so imprecision
    here can only narrow the search, never let a wrong factor through."""
    D = f.domain
    lcm_den = 1
    for c in f.coeffs:
        lcm_den = lcm_den * c.denominator // _int_gcd(lcm_den, c.denominator)
    scaled = [int(c * lcm_den) for c in f.coeffs]
    content = 0
    for x in scaled:
        content = _int_gcd(content, abs(x))
    content = content or 1
    ints = [x // content for x in scaled]
    return UPoly([D.from_int(x) for x in ints], D)


# =============================================================================================== Kronecker
def _eval_int(F: UPoly, x: int) -> int:
    """Horner evaluation of the integer-coefficient ``UPoly`` ``F`` at the integer ``x``, as a plain
    Python ``int`` (every coefficient and every partial sum is an exact integer by construction)."""
    acc = 0
    for c in reversed(F.coeffs):
        acc = acc * x + int(c)
    return acc


def _kronecker_split(f: UPoly) -> Optional[Tuple[UPoly, UPoly]]:
    """``f``: monic ``UPoly`` over QRing, square-free, degree ``d ≥ 2``, with no rational root.

    Returns ``(h, q)`` — both MONIC, ``divmod_(f, h) == (q, 0)`` exactly, ``1 ≤ deg(h) ≤ d - 1`` — the
    first proper factor pair found by exhausting every candidate at every trial degree
    ``e = 1 .. ⌊d/2⌋``. Returns ``None`` (⇒ ``f`` is IRREDUCIBLE over ℚ) only after that entire search
    space has been exhausted with no candidate dividing ``f``.
    """
    D = f.domain
    d = f.degree()
    F = _clear_denominators(f)               # integer-coefficient, same roots as f

    for e in range(1, d // 2 + 1):
        nodes = _kronecker_nodes(e + 1)
        vals: List[int] = []
        zero_root: Optional[int] = None
        for x in nodes:
            v = _eval_int(F, x)
            if v == 0:
                zero_root = x
                break
            vals.append(v)

        if zero_root is not None:
            h = UPoly([D.neg(D.from_int(zero_root)), D.one()], D)
            q, r = divmod_(f, h)
            if r.is_zero() and 1 <= q.degree() <= d - 1:
                return h.monic(), q
            continue

        divisor_lists = [_signed_divisors(v) for v in vals]
        tried = set()
        for combo in _product(*divisor_lists):
            h_cand = lagrange(list(zip(nodes, combo)))
            if h_cand.degree() != e:
                continue
            key = tuple(h_cand.coeffs)
            if key in tried:
                continue
            tried.add(key)
            h_monic = h_cand.monic()
            q, r = divmod_(f, h_monic)
            if r.is_zero() and 1 <= q.degree() <= d - 1:
                return h_monic, q                # q is monic automatically: lead(h_monic)*lead(q)=lead(f)=1
    return None


def _factor_monic(f: UPoly) -> List[UPoly]:
    """``f``: monic ``UPoly`` over QRing, SQUARE-FREE (a divisor of a square-free radical — so this
    recursion never itself needs to worry about repeated factors: any divisor of a square-free
    polynomial is square-free). Returns the list of its monic irreducible factors over ℚ, each once
    (up to the caller attaching the outer multiplicity that came from :func:`square_free_factorization`).
    """
    d = f.degree()
    if d <= 0:
        return []
    if d == 1:
        return [f]

    res = factor(f)                            # fast path: every RATIONAL root, to full multiplicity
    linear = [g for g, m in res["factors"] for _ in range(m)]
    remaining = res["remaining"]                # monic; degree 0 iff f split completely into linear factors

    if remaining.degree() <= 0:
        return linear
    if remaining.degree() == 1:
        return linear + [remaining]

    split = _kronecker_split(remaining)
    if split is None:
        return linear + [remaining]             # remaining is irreducible over ℚ
    h, q = split
    return linear + _factor_monic(h) + _factor_monic(q)


# =============================================================================================== public API
def factor_over_Q(p: UPoly) -> Tuple:
    """Factor ``p`` (a ``UPoly`` over ``QRing`` = ℚ) into IRREDUCIBLE factors, EXACTLY.

    Returns ``(lead, [(g_1, m_1), ..., (g_k, m_k)])`` — every ``g_i`` MONIC and IRREDUCIBLE over ℚ,
    the ``g_i`` pairwise DISTINCT, every ``m_i >= 1``, and, exactly (via :func:`~idm.kernel.poly.
    univariate.mul`)::

        p == UPoly([lead], QRing()) * g_1**m_1 * ... * g_k**m_k

    A nonzero CONSTANT ``p`` returns ``(lead, [])`` — no irreducible factors, ``p`` IS the unit
    ``lead``. The ZERO polynomial raises ``ValueError`` (0 = lead · anything for every lead, so "the"
    factorization is undefined). A non-``QRing`` domain raises ``ValueError``.

    ALGORITHM: square-free decomposition (Yun) composed with, per square-free bucket, rational-root
    extraction then Kronecker's bounded-degree divisor method for whatever has no rational root left
    — see the module docstring for the full description. Exact ``fractions.Fraction`` arithmetic
    throughout; never a float; no modular/GF(p) reduction; no Hensel lifting.
    """
    if not isinstance(p.domain, QRing):
        raise ValueError(f"factor_over_Q requires a UPoly over QRing (ℚ); got {p.domain!r}")
    if p.is_zero():
        raise ValueError("factor_over_Q: the zero polynomial has no factorization")

    lead, sqfree = square_free_factorization(p)
    out: List[Tuple[UPoly, int]] = []
    for g, mult in sqfree:
        for irr in _factor_monic(g):
            out.append((irr, mult))
    return lead, out


__all__ = ["factor_over_Q"]
