"""idm.kernel.poly.complex_roots — ALL roots of a ℚ-polynomial, real AND complex, as EXACT enclosures.

Completes the "degree-n polynomial → all n roots" closure (the complex half of WP3/WP6/WP11/WP13). Each
root is returned as an **exact rational-rectangle enclosure** ``[re_lo, re_hi] × [im_lo, im_hi]`` isolating
exactly one root, where the real part and the imaginary part are each an **exact real algebraic number**
(``AlgReal``, minimal polynomial + isolating interval). No float in the enclosure — only a disclosed
decimal readout for display.

Method (all over ℚ):
  * split ``p(x + iy) = P(x, y) + i·Q(x, y)`` into real bivariate polynomials over ℚ (a root is a common
    zero of P and Q);
  * the REAL parts of the roots are the real roots of ``Res_y(P, Q)`` (a univariate ℚ-poly recovered
    exactly by evaluation + Lagrange interpolation of the univariate resultant), the IMAGINARY parts are
    the real roots of ``Res_x(P, Q)`` — both isolated exactly as ``AlgReal``;
  * a candidate pair ``(a, b)`` is a genuine root iff ``P(a, b) = 0`` and ``Q(a, b) = 0``, decided by
    exact rational **interval arithmetic** over the shrinking box (scales to any degree — no algebraic
    multiplication) — a non-root pair's P- or Q-enclosure eventually excludes 0.

The resultants' real roots are isolated by **Sturm bisection of their square-free part** — polynomial-time,
NO irreducible factorization (the resultants have degree n², where factoring blows any budget). So an
irrational real/imaginary part carries a *defining* polynomial (the square-free radical, possibly
reducible) + an isolating interval — exact and refinable, though not the minimal polynomial.

The result is certified complete: the number of isolated (distinct) roots must equal the degree, else it
HOLDs. So this handles **square-free (distinct-root) ℚ-polynomials at any degree**; a polynomial with a
REPEATED root fails closed (count < degree). Exact complex *arithmetic* on these roots, the true minimal
polynomial of each part, and repeated-root multiplicity are declared later increments.
"""
from __future__ import annotations

from fractions import Fraction as Q
from math import comb

from .algebraic import AlgReal, AlgebraicHOLD, _P
from .univariate import UPoly, resultant, isolate_real_roots, square_free_factorization, mul
from .factorize import lagrange
from .coeffring import QRing


def _isolate_reals(coeffs):
    """Every real root of the ℚ-polynomial ``coeffs`` as an ``AlgReal``, by Sturm isolation of the
    SQUARE-FREE part — polynomial-time, NO irreducible factorization (the resultants here have degree n²,
    where full factoring blows any budget). A rational root is returned exactly; an irrational one carries
    the square-free polynomial as its (possibly reducible) DEFINING polynomial + an isolating interval —
    enough for an exact rectangle enclosure and Sturm refinement, which is all this module needs."""
    from idm.exact import rational_roots
    p = _P(coeffs)
    if p.degree() < 1:
        return []
    _lead, sqf = square_free_factorization(p)                     # radical = ∏ gᵢ (square-free)
    D = p.domain
    radical = UPoly([Q(1)], D)
    for g, _i in sqf:
        radical = mul(radical, g)
    from .univariate import count_real_roots
    from .algebraic import _peval
    rats = set(rational_roots([Q(c) for c in coeffs]))
    if radical.coeffs[0] == 0:                                    # rational_roots misses 0 (constant term 0)
        rats.add(Q(0))
    out = []
    for lo, hi in isolate_real_roots(radical):
        lo, hi = Q(lo), Q(hi)
        r = next((q for q in rats if lo < q <= hi), None)
        if r is not None:
            out.append(AlgReal.from_rational(r))
            continue
        # the resultant can carry SPURIOUS extra roots (e.g. an eval point where P or Q degenerated),
        # so the reducible radical may vanish at this interval's excluded endpoint lo. Nudge lo off it so
        # the interval strictly brackets its one (irrational) root — else AlgReal._refine mis-collapses.
        while _peval(radical, lo) == 0:
            mid = (lo + hi) / 2
            lo = mid if count_real_roots(radical, mid, hi) == 1 else lo   # keep the root in (lo, hi]
            if count_real_roots(radical, mid, hi) != 1:
                hi = mid
        out.append(AlgReal(radical, lo, hi))
    out.sort(key=lambda a: (a.lo + a.hi))
    return out

_QR = QRing()


class ComplexRootsHOLD(Exception):
    """Raised when the roots cannot be certified complete (e.g. factorization budget, count mismatch)."""


def _bivar_PQ(coeffs):
    """p(x+iy) = P(x,y) + i·Q(x,y); return {(i,j): coeff} dicts for xⁱyʲ (P = real part, Q = imag part)."""
    P, Qd = {}, {}
    for k, pk in enumerate(coeffs):
        pk = Q(pk)
        if pk == 0:
            continue
        for m in range(k + 1):                       # (x+iy)^k = Σ C(k,m) iᵐ x^{k-m} yᵐ
            c = pk * comb(k, m)
            key = (k - m, m)
            r = m % 4                                # iᵐ: 0→+P, 1→+Q, 2→−P, 3→−Q
            if r == 0:
                P[key] = P.get(key, Q(0)) + c
            elif r == 1:
                Qd[key] = Qd.get(key, Q(0)) + c
            elif r == 2:
                P[key] = P.get(key, Q(0)) - c
            else:
                Qd[key] = Qd.get(key, Q(0)) - c
    return P, Qd


def _eval_x(biv, xv):
    """substitute x = xv (rational) → UPoly in y."""
    xv = Q(xv)
    cy = {}
    for (i, j), c in biv.items():
        cy[j] = cy.get(j, Q(0)) + c * (xv ** i)
    d = max(cy, default=0)
    return UPoly([cy.get(t, Q(0)) for t in range(d + 1)], _QR)


def _eval_y(biv, yv):
    yv = Q(yv)
    cx = {}
    for (i, j), c in biv.items():
        cx[i] = cx.get(i, Q(0)) + c * (yv ** j)
    d = max(cx, default=0)
    return UPoly([cx.get(t, Q(0)) for t in range(d + 1)], _QR)


def _safe_res(a: UPoly, b: UPoly):
    """Univariate resultant with the constant/zero degenerate cases handled (Res(c,·)=c^deg)."""
    if a.is_zero() or b.is_zero():
        return Q(0)
    da, db = a.degree(), b.degree()
    if da == 0 and db == 0:
        return Q(1)
    if da == 0:
        return a.coeffs[0] ** db
    if db == 0:
        return b.coeffs[0] ** da
    return resultant(a, b)


def _resultant_poly(biv_P, biv_Q, n, in_x):
    """Res over the eliminated variable, recovered as a univariate ℚ-poly by evaluation + interpolation.
    ``in_x`` True → Res_y(P,Q) as a poly in x; False → Res_x(P,Q) as a poly in y."""
    K = n * n + 2                                     # ≥ the resultant's degree; over-sampling is exact
    xs = [0] + [v for k in range(1, K) for v in (k, -k)]
    ev = _eval_x if in_x else _eval_y
    pts = [(Q(xv), _safe_res(ev(biv_P, xv), ev(biv_Q, xv))) for xv in xs[:K]]
    return lagrange(pts)


def _pow_iv(lo, hi, k):
    """[lo,hi]^k over exact ℚ (interval arithmetic)."""
    rl, rh = Q(1), Q(1)
    for _ in range(k):
        cs = [rl * lo, rl * hi, rh * lo, rh * hi]
        rl, rh = min(cs), max(cs)
    return rl, rh


def _box_eval(biv, alo, ahi, blo, bhi):
    """Enclosure of the bivariate ``biv`` over the box [alo,ahi]×[blo,bhi], exact ℚ."""
    lo, hi = Q(0), Q(0)
    for (i, j), c in biv.items():
        al, ah = _pow_iv(alo, ahi, i)
        bl, bh = _pow_iv(blo, bhi, j)
        ms = [al * bl, al * bh, ah * bl, ah * bh]
        ml, mh = min(ms), max(ms)
        ts = [c * ml, c * mh]
        lo += min(ts)
        hi += max(ts)
    return lo, hi


def _roots_of_squarefree(coeffs) -> list:
    """All DISTINCT roots (real + complex) of a SQUARE-FREE ℚ-polynomial as exact rectangle enclosures.
    Requires the isolated count to equal the degree, else HOLDs — callers pass square-free factors."""
    p = _P(coeffs)
    n = p.degree()
    if n < 1:
        return []
    P, Qd = _bivar_PQ([Q(c) for c in coeffs])
    try:
        Rx = _resultant_poly(P, Qd, n, in_x=True)
        Ry = _resultant_poly(P, Qd, n, in_x=False)
        # isolate the resultants' real roots by Sturm on their square-free part — NO factoring: these
        # resultants have degree n², where irreducible factorization blows any budget.
        A = _isolate_reals([str(c) for c in Rx.coeffs])           # candidate real parts (exact enclosures)
        B = _isolate_reals([str(c) for c in Ry.coeffs])           # candidate imaginary parts
    except AlgebraicHOLD as ex:
        raise ComplexRootsHOLD(f"resultant real-root isolation exceeded the budget ({ex})")

    roots = []
    for a in A:
        for b in B:
            ar, br = a, b
            is_root = True
            for _ in range(80):                       # refine the box until 0 is excluded, or it is tiny
                pl, ph = _box_eval(P, ar.lo, ar.hi, br.lo, br.hi)
                ql, qh = _box_eval(Qd, ar.lo, ar.hi, br.lo, br.hi)
                if pl > 0 or ph < 0 or ql > 0 or qh < 0:
                    is_root = False
                    break
                if ar.hi - ar.lo < Q(1, 10 ** 20) and br.hi - br.lo < Q(1, 10 ** 20):
                    break
                ar = ar.refine((ar.hi - ar.lo) / 2)
                br = br.refine((br.hi - br.lo) / 2)
            if is_root:
                roots.append((a, b))

    def _part(r):
        return {"min_poly": [str(c) for c in r.min_poly_coeffs()],
                "interval": [str(r.lo), str(r.hi)], "approx": float(r.to_float(20)),
                "is_rational": r.is_rational}

    out = [{"re": _part(a), "im": _part(b), "is_real": b.is_rational and b.as_rational() == 0,
            "verified": a.verify() and b.verify()} for a, b in roots]
    if len(out) != n:                                 # every distinct root of this square-free factor found
        raise ComplexRootsHOLD(
            f"isolated {len(out)} roots of a degree-{n} square-free factor — could not certify complete")
    return out


def all_roots(coeffs) -> dict:
    """Every root of the ℚ-polynomial ``coeffs`` (low→high), real and complex, as exact rational-rectangle
    enclosures WITH MULTIPLICITY. Each root: ``re``/``im`` = {min_poly, interval, approx, is_rational},
    ``is_real``, ``multiplicity``, ``verified``. Certified complete: Σ multiplicity == degree (else HOLD).
    Works by finding the DISTINCT roots of each square-free factor and tagging them with its multiplicity —
    so it handles repeated roots too, and each factor is lower-degree (also faster)."""
    from .univariate import square_free_factorization
    p = _P(coeffs)
    n = p.degree()
    if n < 1:
        return {"degree": n, "roots": [], "num_real": 0, "num_complex": 0, "num_distinct": 0}
    _lead, sqf = square_free_factorization(p)          # p = lead · ∏ gᵢ^i, gᵢ square-free
    out = []
    for g, i in sqf:
        if g.degree() < 1:
            continue
        for r in _roots_of_squarefree([str(c) for c in g.coeffs]):
            r["multiplicity"] = i
            out.append(r)
    out.sort(key=lambda d: (d["re"]["approx"], d["im"]["approx"]))
    total = sum(r["multiplicity"] for r in out)       # completeness certificate: roots·mult == degree
    if total != n:
        raise ComplexRootsHOLD(f"roots with multiplicity sum to {total} but degree is {n} — incomplete")
    num_real = sum(r["multiplicity"] for r in out if r["is_real"])
    return {"degree": n, "roots": out, "num_real": num_real, "num_complex": total - num_real,
            "num_distinct": len(out)}
