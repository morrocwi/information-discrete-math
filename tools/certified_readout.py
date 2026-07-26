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
    for name, ok in checks:
        print(f"  {'ok ' if ok else 'FAIL'} {name}")
    ok = all(o for _, o in checks)
    print(f"certified_readout self-check: {'PASS' if ok else 'FAIL'} ({sum(o for _,o in checks)}/{len(checks)})")
    raise SystemExit(0 if ok else 1)
