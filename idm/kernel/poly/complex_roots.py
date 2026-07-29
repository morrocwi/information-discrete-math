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


# ── performance fence (deterministic, no wall-clock — golden/tests stay reproducible) ──────────────
# The cost of resolving one SQUARE-FREE factor of degree n is driven by its degree-n² resultants (which
# are Sturm-isolated). Two things push it into minutes: (1) a DEGREE cliff — a degree-7 factor resolves
# in seconds, a degree-8 one in minutes even for tiny coefficients, because its resultant is degree 64;
# (2) COEFFICIENT growth, but only *through* that degree-n² resultant — so coefficient bit-length costs
# in proportion to the resultant degree, NOT on its own (a degree-2 factor with even 40-bit coefficients
# resolves in well under a second — its resultant is only degree 4). The fence therefore caps the DEGREE
# directly and caps the interaction ``n²·bits`` (which already scales bit-length by the resultant
# degree); there is deliberately NO standalone bit-length cap, because that wrongly rejects fast
# low-degree/large-coefficient factors. The defaults keep every capability that currently returns in
# ≲15s and HOLD (never hang) on the "large-coefficient high-degree" inputs; widen the caps via
# ``all_roots(..., fence=<dict>)`` or disable with ``fence=None``.
#
# The fence has TWO layers, both deterministic (no wall-clock, so golden/tests stay reproducible):
#   LAYER 1 — a free *static* pre-check on the input (degree, coefficient bit-length), before any work.
#   LAYER 2 — a HEURISTIC check on the BUILT resultant's coefficient bit-size, measured after the (cheap
#     ~0.03s) resultant construction but before the expensive Sturm isolation. The dominant cost is
#     isolating the degree-n² resultant; its coefficient bit-size is a *rough* proxy for that cost — good
#     enough to catch the egregious cases (the quartic [9999,-4242,1313,-77,1] has small input
#     coefficients but a 73-bit degree-16 resultant that isolates in minutes → HOLD) without over-blocking
#     the fast ones (fixtures ≤ 39 resultant-bits; a ~58-bit quartic still resolves in ~8s, so the cap
#     sits at 64 with margin).
#   NOT a tight bound (disclosed): Sturm-isolation runtime is genuinely *not* a monotone function of
#     resultant bit-size — a degree-6 resultant at 57 bits isolates in ~2s while a degree-49 one at 55
#     bits can take over a minute. So the cap both lets some slow large-degree/low-bit inputs through
#     (e.g. x⁷−20) and would HOLD a rare fast input above it (recover with ``force``). A *tight*
#     deterministic bound needs a computed work budget counting the actual Sturm sign-evaluations — an
#     open increment (#65), out of scope here. This layer only removes the worst multi-minute hangs.
# Together the layers keep every fixture + the ≲15s capability and remove the worst hangs; widen the caps
# via ``all_roots(..., fence=<dict>)`` or disable with ``fence=None``.
_ROOTS_FENCE = {
    "max_factor_degree": 7,   # resultant degree n² ≤ 49; degree-8+ factors run for minutes
    "max_mix": 350,           # cap on n²·input-bits: cheap first filter (deg-5 ~20-bit → 500 HOLDs)
    "max_resultant_bits": 64, # HEURISTIC cap on the BUILT resultant's coefficient bit-size (rough proxy,
                              # not a tight bound): fixtures ≤ 39, ~58-bit quartic ≈ 8s allowed, [9999,…] ≈ 73 → HOLD
}


def _coeff_bits(qcoeffs) -> int:
    """Max bit-length of a rational-coefficient list (numerator + denominator), ≥ 1."""
    return max((abs(c.numerator).bit_length() + abs(c.denominator).bit_length()) for c in qcoeffs) if qcoeffs else 1


def _fence_factor(n: int, qcoeffs, fence) -> None:
    """Raise :class:`ComplexRootsHOLD` BEFORE the expensive resultant/Sturm work when a square-free
    factor of degree ``n`` is projected to run for minutes. Deterministic; ``fence=None`` disables it."""
    if not fence:
        return
    b = _coeff_bits(qcoeffs)
    if n > fence["max_factor_degree"]:
        raise ComplexRootsHOLD(
            f"square-free factor of degree {n} exceeds the performance fence (max_factor_degree="
            f"{fence['max_factor_degree']}): its degree-{n * n} resultants would run for minutes. "
            f"Pass all_roots(..., fence=None) to force, or widen 'max_factor_degree'.")
    if n * n * b > fence["max_mix"]:
        raise ComplexRootsHOLD(
            f"square-free factor (degree {n}, {b}-bit coefficients) has n²·bits={n * n * b} over the "
            f"performance fence (max_mix={fence['max_mix']}) — projected to run for tens of seconds to "
            f"minutes. Pass fence=None to force, or widen 'max_mix'.")


def _fence_resultant(Rx, Ry, fence) -> None:
    """Layer-2 fence (HEURISTIC, not a tight bound): HOLD when the BUILT resultants' coefficient bit-size
    is large enough that Sturm isolation is *likely* slow, even though the input coefficients were small
    (e.g. a quartic whose degree-16 resultant carries 73-bit coefficients). Measured after the cheap
    build, before the expensive isolation. Deterministic (a function of the resultants only); resultant
    bit-size is only a rough proxy for isolation time, so this removes the worst hangs but is not exact —
    ``fence=None`` disables it."""
    if not fence or "max_resultant_bits" not in fence:
        return
    rb = max(_coeff_bits(Rx.coeffs), _coeff_bits(Ry.coeffs))
    if rb > fence["max_resultant_bits"]:
        raise ComplexRootsHOLD(
            f"the built resultant carries {rb}-bit coefficients, over the performance fence "
            f"(max_resultant_bits={fence['max_resultant_bits']}): Sturm-isolating a degree-{Rx.degree()} "
            f"resultant this large is likely slow (a heuristic size proxy, not a precise runtime bound). "
            f"Pass all_roots(..., fence=None) to force, or widen 'max_resultant_bits'.")


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


def _roots_of_squarefree(coeffs, fence=_ROOTS_FENCE) -> list:
    """All DISTINCT roots (real + complex) of a SQUARE-FREE ℚ-polynomial as exact rectangle enclosures.
    Requires the isolated count to equal the degree, else HOLDs — callers pass square-free factors.
    HOLDs deterministically (never hangs) BEFORE the degree-n² resultant work on inputs the performance
    fence projects to run for minutes; ``fence=None`` disables the fence."""
    qcoeffs = [Q(c) for c in coeffs]
    p = _P(coeffs)
    n = p.degree()
    if n < 1:
        return []
    _fence_factor(n, qcoeffs, fence)                  # deterministic perf fence — HOLD, don't hang
    P, Qd = _bivar_PQ(qcoeffs)
    try:
        Rx = _resultant_poly(P, Qd, n, in_x=True)
        Ry = _resultant_poly(P, Qd, n, in_x=False)
        _fence_resultant(Rx, Ry, fence)                           # layer-2 fence — HOLD before Sturm isolation
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


def all_roots(coeffs, fence=_ROOTS_FENCE) -> dict:
    """Every root of the ℚ-polynomial ``coeffs`` (low→high), real and complex, as exact rational-rectangle
    enclosures WITH MULTIPLICITY. Each root: ``re``/``im`` = {min_poly, interval, approx, is_rational},
    ``is_real``, ``multiplicity``, ``verified``. Certified complete: Σ multiplicity == degree (else HOLD).
    Works by finding the DISTINCT roots of each square-free factor and tagging them with its multiplicity —
    so it handles repeated roots too, and each factor is lower-degree (also faster).

    ``fence`` (default :data:`_ROOTS_FENCE`) is the deterministic performance fence applied per square-free
    factor: it HOLDs (never hangs) BEFORE the degree-n² resultant work on a "large-coefficient high-degree"
    factor projected to run for minutes. Pass ``fence=None`` to disable it, or a dict with wider caps."""
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
        for r in _roots_of_squarefree([str(c) for c in g.coeffs], fence=fence):
            r["multiplicity"] = i
            out.append(r)
    out.sort(key=lambda d: (d["re"]["approx"], d["im"]["approx"]))
    total = sum(r["multiplicity"] for r in out)       # completeness certificate: roots·mult == degree
    if total != n:
        raise ComplexRootsHOLD(f"roots with multiplicity sum to {total} but degree is {n} — incomplete")
    num_real = sum(r["multiplicity"] for r in out if r["is_real"])
    return {"degree": n, "roots": out, "num_real": num_real, "num_complex": total - num_real,
            "num_distinct": len(out)}
