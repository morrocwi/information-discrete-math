"""idm.kernel.poly.algebraic — EXACT real algebraic-number arithmetic over ℚ (WP2, Increment 1).

An algebraic number here is a **root of a ℚ-polynomial, kept exact** — never a float. It is represented
by ``AlgReal(poly, lo, hi)``:

* ``poly`` — a monic, ℚ-irreducible (or degree-1, for a rational) ``UPoly`` = its **minimal polynomial**;
* ``(lo, hi]`` — an **isolating rational interval** containing exactly one real root of ``poly``, the one
  this object denotes. ``lo, hi`` are exact ``Fraction``s.

Everything is exact over ℚ: arithmetic (``+ − × ÷``, integer powers) produces the minimal polynomial of
the result via a **power-basis dependency** in ``ℚ(α,β)`` (linear algebra over ℚ, no float), then
**re-isolates** the correct root by Sturm bisection of the operand intervals. Comparison / equality /
sign are decided by exact interval refinement, never by decimals. So a degree-≥3 irrational root is a
first-class object that adds, multiplies, divides, compares, and **substitutes back** to verify the
equation — which is exactly the WP2 closure criterion.

Scope of Increment 1: **real** algebraic numbers. Complex algebraic numbers, number fields ℚ(α), towers,
and ℚ(x) coercion are later WP2 increments (declared, not silently absent). Division/inverse of 0 and any
step that cannot be certified **HOLD** (raise ``AlgebraicHOLD``) rather than guess.
"""
from __future__ import annotations

from fractions import Fraction as Q

from .coeffring import QRing
from .univariate import UPoly, isolate_real_roots, count_real_roots
from .factorize import factor_over_Q, FactorizationBudgetExceeded

# Kronecker candidate budget for isolating a result's minimal polynomial. Bounds the combinatorial
# divisor search so a hard high-degree combination fails closed (HOLD) instead of hanging — Increment 1
# targets low-degree exact algebraic arithmetic; higher degrees are a later WP2 increment.
_FACTOR_BUDGET = 3_000

_QR = QRing()


class AlgebraicHOLD(Exception):
    """Raised when an exact algebraic operation cannot be certified (e.g. division by zero)."""


def _P(coeffs):
    """UPoly over ℚ from low→high coefficients (ints/Fractions/str)."""
    return UPoly([Q(c) for c in coeffs], _QR)


def _peval(poly: UPoly, x) -> Q:
    """Evaluate ``poly`` at rational ``x`` — exact (Horner)."""
    x = Q(x)
    acc = Q(0)
    for c in reversed(poly.coeffs):
        acc = acc * x + c
    return acc


def _sgn(v: Q) -> int:
    return (v > 0) - (v < 0)


# ---------------------------------------------------------------------------------------------------
# The exact real algebraic number
# ---------------------------------------------------------------------------------------------------
class AlgReal:
    """A real algebraic number: minimal polynomial ``poly`` + isolating rational interval ``(lo, hi]``."""

    __slots__ = ("poly", "lo", "hi")

    def __init__(self, poly: UPoly, lo, hi):
        self.poly = poly
        self.lo = Q(lo)
        self.hi = Q(hi)

    # ---- constructors -------------------------------------------------------------------------
    @staticmethod
    def from_rational(r) -> "AlgReal":
        r = Q(r)
        return AlgReal(_P([-r, 1]), r - 1, r)          # root of x - r, isolated in (r-1, r]

    @staticmethod
    def real_roots(coeffs) -> list["AlgReal"]:
        """All DISTINCT real roots of the ℚ-polynomial ``coeffs`` (low→high), each as an exact AlgReal
        carrying its own irreducible minimal polynomial. Sorted ascending."""
        p = _P(coeffs)
        if p.degree() < 1:
            return []
        _lead, facs = factor_over_Q(p)
        out: list[AlgReal] = []
        for irr, _mult in facs:
            if irr.degree() < 1:
                continue
            for lo, hi in isolate_real_roots(irr):
                out.append(AlgReal(irr, *_strict(irr, lo, hi)))
        out.sort(key=_cmp_key)
        return out

    @staticmethod
    def rootof(coeffs, k: int) -> "AlgReal":
        """The ``k``-th real root (0-indexed, ascending) of the ℚ-polynomial ``coeffs``."""
        roots = AlgReal.real_roots(coeffs)
        if not (0 <= k < len(roots)):
            raise AlgebraicHOLD(f"real root index {k} out of range (found {len(roots)} real roots)")
        return roots[k]

    # ---- basic queries ------------------------------------------------------------------------
    @property
    def is_rational(self) -> bool:
        return self.poly.degree() == 1

    def as_rational(self):
        """The exact ``Fraction`` if this number is rational, else ``None``."""
        if not self.is_rational:
            return None
        c0, c1 = self.poly.coeffs[0], self.poly.coeffs[1]     # c1·x + c0 = 0
        return -c0 / c1

    def min_poly_coeffs(self):
        return [Q(c) for c in self.poly.coeffs]

    def refine(self, width) -> "AlgReal":
        """Return the same number with its isolating interval refined to no wider than ``width``."""
        lo, hi = _refine(self.poly, self.lo, self.hi, Q(width))
        return AlgReal(self.poly, lo, hi)

    def to_float(self, dps: int = 30):
        """A disclosed, NON-exact decimal readout (for display only)."""
        import mpmath as mp
        with mp.workdps(dps + 5):
            if self.is_rational:                                  # exact rational → its own value
                q = self.as_rational()
                return mp.mpf(q.numerator) / q.denominator
            r = self.refine(Q(1, 10) ** (dps + 2))                # irrational → midpoint of a tight bracket
            mlo = mp.mpf(r.lo.numerator) / r.lo.denominator
            mhi = mp.mpf(r.hi.numerator) / r.hi.denominator
            return (mlo + mhi) / 2

    def verify(self) -> bool:
        """Substitute-back certificate: the minimal polynomial has exactly one real root in (lo, hi] and
        brackets a sign change there (or the endpoint is the exact rational root). Exact over ℚ."""
        if self.is_rational:
            return _peval(self.poly, self.as_rational()) == 0
        slo, shi = _sgn(_peval(self.poly, self.lo)), _sgn(_peval(self.poly, self.hi))
        return slo != 0 and shi != 0 and slo != shi and count_real_roots(self.poly, self.lo, self.hi) == 1

    # ---- ordering / equality (exact, by interval refinement) ----------------------------------
    def sign(self) -> int:
        if self.is_rational:
            return _sgn(self.as_rational())
        lo, hi = self.lo, self.hi
        for _ in range(10000):
            if lo > 0:
                return 1
            if hi < 0:
                return -1
            lo, hi = _refine(self.poly, lo, hi, (hi - lo) / 2)   # 0 is never a root of an irreducible deg>1
        raise AlgebraicHOLD("could not determine sign (interval refinement stalled)")

    def _cmp(self, other: "AlgReal") -> int:
        if self.is_rational and other.is_rational:
            return _sgn(self.as_rational() - other.as_rational())
        if self.poly == other.poly:                    # same minimal polynomial
            if _overlap(self.lo, self.hi, other.lo, other.hi):
                return 0                               # same isolated root ⇒ equal
            return -1 if self.hi <= other.lo else 1    # distinct roots of the same poly, already disjoint
        # different minimal polynomials ⇒ different numbers ⇒ decide by the exact sign of the difference
        # (well-defined and non-zero here, since distinct minimal polynomials denote distinct values).
        return (self - other).sign()

    def __eq__(self, other):
        return isinstance(other, AlgReal) and self._cmp(other) == 0

    def __lt__(self, other):
        return self._cmp(other) < 0

    def __le__(self, other):
        return self._cmp(other) <= 0

    def __hash__(self):
        return hash(tuple(self.poly.coeffs))

    # ---- arithmetic ---------------------------------------------------------------------------
    def __neg__(self) -> "AlgReal":
        neg = _P([c * (Q(-1) ** i) for i, c in enumerate(self.poly.coeffs)])   # roots → −root
        return AlgReal(neg.monic(), -self.hi, -self.lo)

    def __add__(self, other) -> "AlgReal":
        other = _coerce(other)
        if self.is_rational and other.is_rational:
            return AlgReal.from_rational(self.as_rational() + other.as_rational())
        if other.is_rational:
            return _shift(self, other.as_rational())
        if self.is_rational:
            return _shift(other, self.as_rational())
        return _combine(self, other, "sum")

    __radd__ = __add__

    def __sub__(self, other):
        return self + (-_coerce(other))

    def __rsub__(self, other):
        return _coerce(other) + (-self)

    def inv(self) -> "AlgReal":
        if self.sign() == 0:
            raise AlgebraicHOLD("division by zero (algebraic number is 0)")
        if self.is_rational:
            return AlgReal.from_rational(1 / self.as_rational())
        rec = _P(list(reversed(self.poly.coeffs)))     # reciprocal polynomial: roots → 1/root
        r = self.refine((self.hi - self.lo))           # ensure sign-definite endpoints
        while not (r.lo > 0 or r.hi < 0):
            r = r.refine((r.hi - r.lo) / 2)
        lo, hi = (1 / r.hi, 1 / r.lo)                  # 1/(lo,hi] with constant sign
        return AlgReal(rec.monic(), min(lo, hi), max(lo, hi))

    def __mul__(self, other) -> "AlgReal":
        other = _coerce(other)
        if self.is_rational and other.is_rational:
            return AlgReal.from_rational(self.as_rational() * other.as_rational())
        if other.is_rational:
            return _scale(self, other.as_rational())
        if self.is_rational:
            return _scale(other, self.as_rational())
        return _combine(self, other, "prod")

    __rmul__ = __mul__

    def __truediv__(self, other):
        return self * _coerce(other).inv()

    def __rtruediv__(self, other):
        return _coerce(other) * self.inv()

    def __pow__(self, n: int) -> "AlgReal":
        if not isinstance(n, int):
            raise AlgebraicHOLD("only integer powers are supported")
        if n < 0:
            return self.inv() ** (-n)
        result = AlgReal.from_rational(1)
        base = self
        e = n
        while e:                                        # exact fast exponentiation
            if e & 1:
                result = result * base
            e >>= 1
            if e:
                base = base * base
        return result

    def __repr__(self):
        return f"AlgReal(min_poly={self.poly.coeffs}, in=({self.lo},{self.hi}])"


# ---------------------------------------------------------------------------------------------------
# helpers — coercion, isolation, interval refinement
# ---------------------------------------------------------------------------------------------------
def _coerce(x) -> AlgReal:
    if isinstance(x, AlgReal):
        return x
    return AlgReal.from_rational(x)


def _cmp_key(a: AlgReal):
    """Sort key (exact ℚ): the value itself if rational, else the midpoint of a refined bracket."""
    if a.is_rational:
        return a.as_rational()
    r = a.refine(Q(1, 10 ** 6))
    return (r.lo + r.hi) / 2


def _overlap(alo, ahi, blo, bhi) -> bool:
    return not (ahi <= blo or bhi <= alo)


def _strict(poly: UPoly, lo, hi):
    """Ensure a strict sign change at the endpoints (irreducible deg>1 has no rational root, so the
    isolating interval from Sturm already has non-zero, opposite-sign endpoints; this is a guard)."""
    lo, hi = Q(lo), Q(hi)
    if poly.degree() == 1:
        return lo, hi
    slo, shi = _sgn(_peval(poly, lo)), _sgn(_peval(poly, hi))
    if slo == 0 or shi == 0 or slo == shi:
        lo, hi = _refine(poly, lo, hi, (hi - lo))       # one bisection pass to settle endpoints
    return lo, hi


def _refine(poly: UPoly, lo, hi, width):
    """Bisect the isolating interval ``(lo, hi]`` of a simple root of ``poly`` until no wider than
    ``width`` — exact rational bisection by sign (or Sturm count for safety)."""
    lo, hi = Q(lo), Q(hi)
    width = Q(width)
    if poly.degree() == 1:
        root = -poly.coeffs[0] / poly.coeffs[1]          # collapse to the EXACT rational root
        return root, root
    slo = _sgn(_peval(poly, lo))
    if slo == 0:                                        # lo is exactly the root (rational): pin it
        return lo, lo
    guard = 0
    while hi - lo > width and guard < 20000:
        guard += 1
        mid = (lo + hi) / 2
        smid = _sgn(_peval(poly, mid))
        if smid == 0:                                   # mid is the exact root
            return mid, mid
        if slo != smid:                                 # root in (lo, mid]
            hi = mid
        else:                                           # root in (mid, hi]
            lo = mid
    return lo, hi


def _shift(a: AlgReal, r: Q) -> AlgReal:
    """α + r for rational r: minimal polynomial p(x − r), interval shifted by r. Exact."""
    r = Q(r)
    p = a.poly
    # p(x - r) via Horner in (x - r): coefficients by repeated synthetic expansion
    shifted = _poly_compose_linear(p, Q(1), -r)         # p(1·x + (−r)) = p(x − r)
    return AlgReal(shifted.monic(), a.lo + r, a.hi + r)


def _scale(a: AlgReal, s: Q) -> AlgReal:
    """α · s for rational s ≠ 0: minimal polynomial p(x/s)·s^deg, interval scaled by s. Exact."""
    s = Q(s)
    if s == 0:
        return AlgReal.from_rational(0)
    p = a.poly
    n = p.degree()
    scaled = _P([c * (s ** (n - i)) for i, c in enumerate(p.coeffs)])   # root_i → s·root_i
    lo, hi = a.lo * s, a.hi * s
    return AlgReal(scaled.monic(), min(lo, hi), max(lo, hi))


def _poly_compose_linear(p: UPoly, a: Q, b: Q) -> UPoly:
    """Return p(a·x + b) as a UPoly (exact)."""
    # Evaluate by Horner with polynomial argument (a·x + b): acc = acc·(a·x+b) + c
    D = _QR
    arg = UPoly([b, a], D)
    acc = UPoly([D.zero()], D)
    from .univariate import add as _add, mul as _mul
    for c in reversed(p.coeffs):
        acc = _add(_mul(acc, arg), UPoly([c], D))
    return acc


# ---------------------------------------------------------------------------------------------------
# the core: minimal polynomial of α∘β via a power-basis dependency in ℚ(α,β), then re-isolation
# ---------------------------------------------------------------------------------------------------
def _combine(a: AlgReal, b: AlgReal, kind: str) -> AlgReal:
    coeffs = _elim(a.poly, b.poly, kind)                # a polynomial R with R(α∘β) = 0
    return _isolate_value(coeffs, a, b, kind)


def _elim(pa: UPoly, pb: UPoly, kind: str):
    """Coefficients (low→high, ℚ) of a polynomial that γ = α∘β satisfies, where α,β are roots of the
    monic pa,pb. Method: express powers of γ in the ℚ-basis {α^i β^j : i<m, j<n} of ℚ(α,β) and find the
    least linear dependency — pure exact linear algebra over ℚ, no resultant machinery, no float."""
    pa, pb = pa.monic(), pb.monic()
    m, n = pa.degree(), pb.degree()
    a_red = [-c for c in pa.coeffs[:-1]]                # α^m = Σ a_red[t]·α^t
    b_red = [-c for c in pb.coeffs[:-1]]               # β^n = Σ b_red[t]·β^t
    dim = m * n

    def ix(i, j):
        return i * n + j

    def mul_alpha(v):
        out = [Q(0)] * dim
        for i in range(m):
            for j in range(n):
                c = v[ix(i, j)]
                if c == 0:
                    continue
                if i + 1 < m:
                    out[ix(i + 1, j)] += c
                else:
                    for t in range(m):
                        out[ix(t, j)] += c * a_red[t]
        return out

    def mul_beta(v):
        out = [Q(0)] * dim
        for i in range(m):
            for j in range(n):
                c = v[ix(i, j)]
                if c == 0:
                    continue
                if j + 1 < n:
                    out[ix(i, j + 1)] += c
                else:
                    for t in range(n):
                        out[ix(i, t)] += c * b_red[t]
        return out

    if kind == "sum":
        def times_gamma(v):
            va, vb = mul_alpha(v), mul_beta(v)
            return [va[k] + vb[k] for k in range(dim)]
    else:                                               # "prod"
        def times_gamma(v):
            return mul_beta(mul_alpha(v))

    one = [Q(0)] * dim
    one[ix(0, 0)] = Q(1)
    powers = [one]
    cur = one
    for _ in range(dim):
        cur = times_gamma(cur)
        powers.append(cur)
    return _min_dependency(powers)


def _min_dependency(powers):
    """Given vectors powers[0], powers[1], … (each length ``dim``), find the least ``k`` for which
    powers[0..k] are linearly dependent over ℚ and return the monic dependency coefficients
    ``[c_0, …, c_k]`` with Σ c_i·powers[i] = 0 — i.e. the minimal polynomial of γ (exact ℚ Gaussian)."""
    dim = len(powers[0])
    basis = []          # list of (pivot_col, reduced_vector, combo) — combo expresses vector via powers[0..]
    for k, pk in enumerate(powers):
        vec = list(pk)
        combo = [Q(0)] * (k + 1)
        combo[k] = Q(1)
        for pcol, bvec, bcombo in basis:               # reduce against existing pivots
            if vec[pcol] != 0:
                f = vec[pcol]                           # bvec is normalized to 1 at pcol
                vec = [vec[t] - f * bvec[t] for t in range(dim)]
                for t in range(len(bcombo)):
                    combo[t] -= f * bcombo[t]
        # find a pivot column
        pivot = next((t for t in range(dim) if vec[t] != 0), None)
        if pivot is None:                               # dependency: combo · powers = 0
            # trim trailing zeros, make monic (highest index coeff = 1)
            c = combo
            while len(c) > 1 and c[-1] == 0:
                c.pop()
            lead = c[-1]
            return [ci / lead for ci in c]
        inv = 1 / vec[pivot]
        vec = [x * inv for x in vec]
        combo = [x * inv for x in combo]
        basis.append((pivot, vec, combo))
    raise AlgebraicHOLD("no dependency found (unexpected: ℚ(α,β) has dimension ≤ mn)")


def _isolate_value(coeffs, a: AlgReal, b: AlgReal, kind: str) -> AlgReal:
    """Given a polynomial ``coeffs`` that γ = α∘β satisfies, pick γ's minimal polynomial (an irreducible
    ℚ-factor) and an isolating interval, by refining α,β until exactly one factor's real root lies in the
    interval-arithmetic enclosure of γ."""
    R = _P(coeffs)
    try:
        _lead, facs = factor_over_Q(R, budget=_FACTOR_BUDGET)
    except FactorizationBudgetExceeded as ex:
        raise AlgebraicHOLD(
            f"result minimal polynomial (degree {R.degree()}) exceeds the Increment-1 factorization "
            f"budget — higher-degree exact algebraic arithmetic is a later WP2 increment ({ex})")
    cands = [irr for irr, _m in facs if irr.degree() >= 1]
    ra, rb = a, b
    for _ in range(400):
        vlo, vhi = _value_interval(ra, rb, kind)
        w = vhi - vlo                                   # isolate factor roots to the SAME width, so the
        matches = []                                    # candidate roots separate as the value interval does
        for f in cands:
            roots = isolate_real_roots(f, width=w) if w > 0 else isolate_real_roots(f)
            for rlo, rhi in roots:
                if _overlap(rlo, rhi, vlo, vhi):
                    matches.append((f, rlo, rhi))
        if len(matches) == 1:
            f, rlo, rhi = matches[0]
            lo, hi = max(rlo, vlo), min(rhi, vhi)       # tighten to the shared bracket
            if hi <= lo:                                # degenerate corner: fall back to the factor's own
                lo, hi = rlo, rhi
            return AlgReal(f, *_strict(f, lo, hi))
        ra = ra.refine((ra.hi - ra.lo) / 2)
        rb = rb.refine((rb.hi - rb.lo) / 2)
    raise AlgebraicHOLD("could not isolate the result root (refinement budget exhausted)")


def _value_interval(a: AlgReal, b: AlgReal, kind: str):
    """Exact interval enclosure of α∘β from the operand isolating intervals."""
    alo, ahi, blo, bhi = a.lo, a.hi, b.lo, b.hi
    if kind == "sum":
        return alo + blo, ahi + bhi
    corners = [alo * blo, alo * bhi, ahi * blo, ahi * bhi]
    return min(corners), max(corners)
