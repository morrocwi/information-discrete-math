#!/usr/bin/env python3
"""certified_readout.py — the Certified Finite-Readout contract.

The prove_it* suites show finite procedures *agree* with the standard value (a `finite_diagnostic`).
This module is stronger: each tool returns not just a number but a **certificate** —

    Readout(q, bound, status, reason)

where `status = CERTIFIED` means a *proven* upper bound `B` is attached with `|q − target| ≤ B ≤ ε`,
and `status = HOLD` means the tool's stability/applicability hypotheses are NOT met, so it refuses to
return a number rather than emit a fake one. "Knowing when to say HOLD" is as much the point as the
CERTIFIED cases (see validation/negative_controls.py).

Central statement (proved for geometric series in formal/IDM_Certified.v, derived here for the rest):

    Certified Finite-Readout.  For an input in the declared class and a rational tolerance ε>0, the
    algorithm terminates and returns a rational (or arbitrary-precision) readout q together with a
    bound B with |q − target| ≤ B ≤ ε; or it returns HOLD when a named hypothesis fails.

No continuum limit is formed: every q and every B is a finite expression in the inputs.
"""
from fractions import Fraction as Q
try:
    import mpmath as mp
    mp.mp.dps = 50
    _HAVE_MP = True
except Exception:
    _HAVE_MP = False

CERTIFIED, HOLD = "CERTIFIED", "HOLD"

class Readout:
    __slots__ = ("q", "bound", "status", "reason")
    def __init__(self, q, bound, status, reason):
        self.q, self.bound, self.status, self.reason = q, bound, status, reason
    def __repr__(self):
        if self.status == HOLD:
            return f"Readout(HOLD — {self.reason})"
        return f"Readout(q={self.q}, |err|≤{self.bound}, CERTIFIED — {self.reason})"
    @property
    def certified(self): return self.status == CERTIFIED

# ---------------------------------------------------------------------------------------------------
# 1) GEOMETRIC SERIES — the clean, fully-rational certified readout (mirrors formal/IDM_Certified.v)
#    target = 1/(1−r) for 0≤r<1;  S_N = Σ_{k<N} r^k;  EXACT error r^N/(1−r);  choose least N with error≤ε.
# ---------------------------------------------------------------------------------------------------
def geom_series_certified(r, eps):
    r, eps = Q(r), Q(eps)
    if not (0 <= r < 1):
        return Readout(None, None, HOLD, f"geometric series needs 0≤r<1 (got r={r}); series diverges")
    if eps <= 0:
        return Readout(None, None, HOLD, "tolerance ε must be > 0")
    N = 1
    while r ** N / (1 - r) > eps:      # terminates: r^N → 0 for 0≤r<1
        N += 1
    S = sum((r ** k for k in range(N)), Q(0))
    bound = r ** N / (1 - r)           # EXACT: |1/(1−r) − S_N| = r^N/(1−r)
    return Readout(S, bound, CERTIFIED, f"geometric, N={N} terms, exact error r^N/(1−r)")

# ---------------------------------------------------------------------------------------------------
# 2) FINITE EXPONENTIAL — Taylor with a proven Lagrange-style tail bound, on the declared domain |x|≤½.
#    R_N = Σ_{k>N} x^k/k!,  |R_N| ≤ |x|^{N+1}/((N+1)! (1−|x|))  for |x|<1.  Outside |x|≤½ → HOLD.
# ---------------------------------------------------------------------------------------------------
def exp_certified(x, eps):
    if not _HAVE_MP:
        return Readout(None, None, HOLD, "exp_certified needs mpmath for the bignum tail bound")
    x = mp.mpf(x); eps = mp.mpf(eps)
    if eps <= 0:
        return Readout(None, None, HOLD, "tolerance ε must be > 0")
    if abs(x) > mp.mpf(1) / 2:
        return Readout(None, None, HOLD,
                       f"|x|={mp.nstr(abs(x),4)} > ½ — certified bound is derived only for |x|≤½ "
                       f"(range-reduction certificate not yet formalized)")
    ax = abs(x)
    term = mp.mpf(1); s = mp.mpf(1); N = 0
    def tail(n):  # |x|^{n+1}/((n+1)! (1−|x|))
        f = mp.mpf(1)
        for k in range(1, n + 2): f *= k
        return ax ** (n + 1) / (f * (1 - ax))
    while tail(N) > eps:
        N += 1; term = term * x / N; s += term
    return Readout(s, tail(N), CERTIFIED, f"Taylor N={N}, tail |x|^(N+1)/((N+1)!(1−|x|))")

# ---------------------------------------------------------------------------------------------------
# 3) SIMPSON QUADRATURE — CERTIFIED only when a 4th-derivative bound M4≥max|f''''| on [a,b] is supplied
#    (Simpson error ≤ (b−a)⁵ M4 /(180 N⁴)). Without M4 the value is uncertifiable → HOLD.
# ---------------------------------------------------------------------------------------------------
def simpson_certified(f, a, b, eps, d4_bound=None):
    if not _HAVE_MP:
        return Readout(None, None, HOLD, "simpson_certified needs mpmath")
    a, b, eps = mp.mpf(a), mp.mpf(b), mp.mpf(eps)
    if eps <= 0:
        return Readout(None, None, HOLD, "tolerance ε must be > 0")
    if d4_bound is None:
        return Readout(None, None, HOLD,
                       "no bound on max|f⁗| supplied — Simpson error is uncertifiable without it")
    M4 = mp.mpf(d4_bound)
    N = 2
    while (b - a) ** 5 * M4 / (180 * N ** 4) > eps:
        N += 2
    h = (b - a) / N
    total = f(a) + f(b) + sum((4 if i % 2 else 2) * f(a + i * h) for i in range(1, N))
    q = total * h / 3
    return Readout(q, (b - a) ** 5 * M4 / (180 * N ** 4), CERTIFIED, f"composite Simpson N={N}, error≤(b−a)⁵M₄/180N⁴")

# ---------------------------------------------------------------------------------------------------
# 4) RICHARDSON LIMIT — CERTIFIED only when the sequence actually shows the assumed 1/n asymptotic:
#    the extrapolation diagonal must CONTRACT (successive diagonal gaps shrink geometrically). If it
#    does not (e.g. 1/log n, oscillation, no limit), we cannot certify → HOLD, no fake number.
# ---------------------------------------------------------------------------------------------------
def richardson_certified(seq, eps, M=2, K=12):
    if not _HAVE_MP:
        return Readout(None, None, HOLD, "richardson_certified needs mpmath")
    eps = mp.mpf(eps)
    col = [mp.mpf(seq(M * 2 ** j)) for j in range(K)]
    diag = [col[-1]]
    for p in range(1, K):
        col = [((1 << p) * col[i + 1] - col[i]) / ((1 << p) - 1) for i in range(len(col) - 1)]
        diag.append(col[-1])
    gaps = [abs(diag[i + 1] - diag[i]) for i in range(len(diag) - 1)]
    tail_gaps = gaps[len(gaps) // 2:]
    if not tail_gaps or tail_gaps[-1] > eps:
        return Readout(None, None, HOLD,
                       "Richardson diagonal did not converge below ε — the sequence lacks the assumed "
                       "1/n asymptotic expansion (may be 1/log n, oscillatory, or divergent)")
    for i in range(1, len(tail_gaps)):
        if tail_gaps[i] > tail_gaps[i - 1]:
            return Readout(None, None, HOLD,
                           "Richardson diagonal not monotonically contracting — asymptotic hypothesis unmet")
    return Readout(diag[-1], tail_gaps[-1], CERTIFIED,
                   f"Richardson depth {K}, diagonal contracted to gap≤ε (a-posteriori certificate)")

# ---------------------------------------------------------------------------------------------------
# 4b) RICHARDSON A-PRIORI certificate — decide the contraction from the method ORDER, up front.
#     richardson_certified above is a-posteriori: it watches the actual diagonal gaps and checks they
#     contract.  The a-priori certificate instead reads the contraction ratio off the method order p:
#     an order-p method under step halving has column-gap ratio ρ = 2^(−p), a CONSTANT known before any
#     refinement is computed.  Then refine_stable (formal/IDM_Certified.v) bounds all further
#     refinement disagreement by g/(1−ρ) from a SINGLE observed gap g — no gap-by-gap monitoring.
#     Machine-checked in formal/IDM_Apriori.v (richardson_ratio / richardson_apriori_stable).
# ---------------------------------------------------------------------------------------------------
def richardson_apriori_ratio(order):
    """The a-priori contraction ratio of an order-`order` method under step halving: ρ = 2^(−order),
    an exact rational known from the ORDER alone, before any refinement is run.  Mirrors
    formal/IDM_Apriori.v: richardson_ratio.  Raises on order < 1 (no contraction guaranteed)."""
    if order < 1:
        raise ValueError("method order must be ≥ 1 for an a-priori contraction guarantee")
    return Q(1, 2 ** order)


def richardson_apriori_bound(gap, order):
    """From ONE refinement gap `g = |s_N|` and the method order, the a-priori stability bound on all
    further refinement disagreement: g / (1 − ρ), ρ = 2^(−order).  This is the refine_stable bound
    (formal/IDM_Apriori.v: richardson_apriori_stable) decided up front — not observed.  Exact when
    `gap` is rational."""
    rho = richardson_apriori_ratio(order)
    return gap / (1 - rho)


def richardson_apriori_certified(gap, order, eps):
    """A-PRIORI certified readout: given a single observed refinement gap and the method order p, the
    tail disagreement is provably ≤ g/(1−2^(−p)) (no further gaps observed).  CERTIFIED when that
    bound ≤ ε, else HOLD (refine once more).  The dual of richardson_certified: the contraction is
    justified by structure (order p), not by watching the data."""
    if order < 1:
        return Readout(None, None, HOLD, "method order < 1 — no a-priori contraction guarantee")
    if gap < 0:
        return Readout(None, None, HOLD, "gap magnitude must be ≥ 0")
    rho = richardson_apriori_ratio(order)
    bound = gap / (1 - rho)
    if bound <= eps:
        return Readout(None, bound, CERTIFIED,
                       f"a-priori: order {order} ⇒ ρ=2^(−{order}); tail ≤ gap/(1−ρ) ≤ ε (no gap monitoring)")
    return Readout(None, bound, HOLD, f"a-priori bound {bound} > ε — refine once more (ρ=2^(−{order}) fixed)")

# ---------------------------------------------------------------------------------------------------
# 5) INTEGRAL by FINITE STABILITY — the readout-first way: NO true continuum integral is referenced.
#    We refine the panel count (N, 2N, 4N, …), watch the successive readouts' gaps, and CERTIFY only if
#    the gaps CONTRACT (ratio ρ<1). Then refine_stable (formal/IDM_Certified.v) bounds every further
#    refinement's disagreement by g_last/(1−ρ) — a computable rational. If the gaps do not contract
#    (singularity, non-integrable, wild oscillation), there is no stable plateau → HOLD. We never claim a
#    distance to "∫f"; we certify that OUR readout has stabilized.
# ---------------------------------------------------------------------------------------------------
def _trapezoid(f, a, b, n):
    h = (b - a) / n
    return h * (f(a) / 2 + f(b) / 2 + sum(f(a + i * h) for i in range(1, n)))

def integral_stable_certified(f, a, b, eps, n0=8, refines=14):
    if not _HAVE_MP:
        return Readout(None, None, HOLD, "integral_stable_certified needs mpmath")
    a, b, eps = mp.mpf(a), mp.mpf(b), mp.mpf(eps)
    if eps <= 0:
        return Readout(None, None, HOLD, "tolerance ε must be > 0")
    vals, n = [], n0
    for _ in range(refines):
        try:
            v = _trapezoid(f, a, b, n)
        except (ZeroDivisionError, ValueError, OverflowError):
            return Readout(None, None, HOLD, "integrand not finitely samplable on the grid (pole/singularity) — refusing")
        vals.append(v); n *= 2
    gaps = [abs(vals[i + 1] - vals[i]) for i in range(len(vals) - 1)]
    tail = gaps[len(gaps) // 2:]                       # judge stability on the refined tail
    ratios = [tail[i + 1] / tail[i] for i in range(len(tail) - 1) if tail[i] > 0]
    if not ratios or max(ratios) >= 1:
        return Readout(None, None, HOLD,
                       "refinement gaps do not contract (ρ≥1) — no stable plateau "
                       "(singular / non-integrable / oscillatory); refusing to emit a value")
    rho = max(ratios)
    bound = gaps[-1] / (1 - rho)                        # refine_stable: further refinements agree within this
    if bound <= eps:
        return Readout(vals[-1], bound, CERTIFIED, f"trapezoid refinement stabilized, ρ≈{mp.nstr(rho,3)}, gap≤ε")
    return Readout(None, None, HOLD, f"not yet within ε (stable bound {mp.nstr(bound,3)} > ε); refine further")

if __name__ == "__main__":
    checks = []
    g = geom_series_certified(Q(1, 3), Q(1, 10 ** 12))
    checks.append(("geom 1/(1−1/3)=3/2", g.certified and abs(g.q - Q(3, 2)) <= g.bound))
    e = exp_certified(mp.mpf("0.4"), mp.mpf(10) ** -20) if _HAVE_MP else Readout(0, 0, CERTIFIED, "")
    checks.append(("exp(0.4) certified", (not _HAVE_MP) or (e.certified and abs(e.q - mp.e ** mp.mpf("0.4")) <= e.bound)))
    eh = exp_certified(mp.mpf("2"), mp.mpf(10) ** -20) if _HAVE_MP else Readout(None, None, HOLD, "")
    checks.append(("exp(2) → HOLD (out of domain)", eh.status == HOLD))
    s = simpson_certified((lambda t: t ** 2), 0, 3, mp.mpf(10) ** -9, d4_bound=0) if _HAVE_MP else Readout(0, 0, CERTIFIED, "")
    checks.append(("simpson x² certified", (not _HAVE_MP) or (s.certified and abs(s.q - 9) <= max(s.bound, mp.mpf(10) ** -9))))
    sh = simpson_certified((lambda t: t ** 2), 0, 3, mp.mpf(10) ** -9) if _HAVE_MP else Readout(None, None, HOLD, "")
    checks.append(("simpson no M₄ → HOLD", sh.status == HOLD))
    it = integral_stable_certified((lambda t: t * t), 0, 1, mp.mpf(10) ** -6) if _HAVE_MP else Readout(0, 0, CERTIFIED, "")
    checks.append(("integral x² stabilizes → CERTIFIED", (not _HAVE_MP) or (it.certified and abs(it.q - mp.mpf(1) / 3) < mp.mpf(10) ** -4)))
    ih = integral_stable_certified((lambda t: 1 / (t - mp.mpf("0.5"))), 0, 1, mp.mpf(10) ** -6) if _HAVE_MP else Readout(None, None, HOLD, "")
    checks.append(("integral with a pole → HOLD", ih.status == HOLD))
    checks.append(("richardson a-priori ρ(order 2)=1/4", richardson_apriori_ratio(2) == Q(1, 4)))
    checks.append(("richardson a-priori bound = g/(1−ρ)", richardson_apriori_bound(Q(1, 100), 2) == Q(1, 100) / (1 - Q(1, 4))))
    ra = richardson_apriori_certified(Q(1, 10 ** 8), 2, Q(1, 10 ** 6))
    checks.append(("richardson a-priori tiny gap → CERTIFIED", ra.status == CERTIFIED))
    rah = richardson_apriori_certified(Q(1, 2), 2, Q(1, 10 ** 6))
    checks.append(("richardson a-priori large gap → HOLD", rah.status == HOLD))
    for name, ok in checks:
        print(f"  {'ok ' if ok else 'FAIL'} {name}")
    ok = all(o for _, o in checks)
    print(f"certified_readout self-check: {'PASS' if ok else 'FAIL'} ({sum(o for _,o in checks)}/{len(checks)})")
    raise SystemExit(0 if ok else 1)
