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

The result is certified complete: the number of isolated roots (real + complex, complex in conjugate
pairs) must equal the degree, else it HOLDs. Exact complex *arithmetic* on these roots is a later increment.
"""
from __future__ import annotations

from fractions import Fraction as Q
from math import comb

from .algebraic import AlgReal, AlgebraicHOLD, _P
from .univariate import UPoly, resultant
from .factorize import lagrange
from .coeffring import QRing

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


def all_roots(coeffs) -> dict:
    """Every root of the ℚ-polynomial ``coeffs`` (low→high), real and complex, as exact rational-rectangle
    enclosures with exact real/imaginary algebraic parts. Returns a dict with ``roots`` (each: re/im as
    {min_poly, interval, approx, is_rational}, plus is_real), ``num_real``, ``num_complex``, ``degree``.
    HOLDs if completeness cannot be certified (the isolated count must equal the degree)."""
    p = _P(coeffs)
    n = p.degree()
    if n < 1:
        return {"degree": n, "roots": [], "num_real": 0, "num_complex": 0}
    P, Qd = _bivar_PQ([Q(c) for c in coeffs])
    try:
        Rx = _resultant_poly(P, Qd, n, in_x=True)
        Ry = _resultant_poly(P, Qd, n, in_x=False)
        A = AlgReal.real_roots([str(c) for c in Rx.coeffs])       # candidate real parts (exact)
        B = AlgReal.real_roots([str(c) for c in Ry.coeffs])       # candidate imaginary parts (exact)
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

    out = [{"re": _part(a), "im": _part(b), "is_real": b.sign() == 0,
            "verified": a.verify() and b.verify()} for a, b in roots]
    out.sort(key=lambda d: (d["re"]["approx"], d["im"]["approx"]))
    num_real = sum(1 for r in out if r["is_real"])
    num_complex = len(out) - num_real
    if len(out) != n:                                 # completeness certificate: all n roots accounted for
        raise ComplexRootsHOLD(
            f"isolated {len(out)} roots but degree is {n} — could not certify a complete root set")
    return {"degree": n, "roots": out, "num_real": num_real, "num_complex": num_complex}
