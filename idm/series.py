"""idm.series — limits, series expansion, acceleration, and convergence, all as finite readouts.

Taylor/Laurent coefficients come from the Cauchy coefficient integral evaluated as a FINITE sum over
points on a circle (a discrete Fourier readout); Fourier coefficients from a finite DFT of samples;
acceleration from Wynn's ε-algorithm; convergence from finite ratio/root tests that return HOLD when the
test is inconclusive rather than guessing. Limits are Richardson plateaus. No completed limit is formed.
"""
from fractions import Fraction as Q
from . import functions as F
import mpmath as mp
mp.mp.dps = 40
R = mp.mpf


# ---------------------------------------------------------------- Taylor / Laurent (Cauchy–FFT) ----
def _deriv_k(f, x0, k, h):
    """the k-th derivative of f at x0 by the centered finite-difference stencil (order O(h²))."""
    from .exact import binomial
    return sum((-1) ** j * binomial(k, j) * f(x0 + (R(k) / 2 - j) * h) for j in range(k + 1)) / h ** k

def taylor_series(f, x0=0, n=8, h="0.05"):
    """Taylor coefficients c_0..c_n of f about x0, c_k = f^{(k)}(x0)/k!, each derivative by a centered
    finite difference with one Richardson step (real-valued; works with the framework's finite functions)."""
    x0 = R(str(x0)); h = R(str(h))
    from .exact import factorial
    out = []
    for k in range(n + 1):
        d1 = _deriv_k(f, x0, k, h); d2 = _deriv_k(f, x0, k, h / 2)
        out.append((4 * d2 - d1) / 3 / factorial(k))      # Richardson O(h⁴), then /k!
    return out

def laurent_series(f, x0=0, lo=-3, hi=3, r="1"):
    """Laurent coefficients c_k for k in [lo,hi] about x0 (same Cauchy–FFT, negative powers allowed)."""
    x0 = R(str(x0)); r = R(str(r)); n = hi - lo; M = max(4 * (n + 1), 64)
    w = mp.exp(2j * mp.pi / M); fj = [f(x0 + r * w ** j) for j in range(M)]
    return {k: mp.chop(sum(fj[j] * w ** (-j * k) for j in range(M)) / (M * r ** k)) for k in range(lo, hi + 1)}


# ---------------------------------------------------------------- Fourier series (finite DFT) ----
def fourier_series(f, period=None, n=8, L=None):
    """real Fourier coefficients a_0,{a_k},{b_k} of a P-periodic f (P=period, default 2π) by a finite DFT
    of N=4n samples: f(x) ≈ a_0/2 + Σ a_k cos(2πkx/P) + b_k sin(2πkx/P)."""
    P = R(str(period)) if period else 2 * F.pi()
    N = max(4 * n, 16); xs = [P * j / N for j in range(N)]; fv = [R(f(x)) for x in xs]
    a = []; b = []
    for k in range(n + 1):
        ck = 2 / N * sum(fv[j] * mp.cos(2 * mp.pi * k * j / N) for j in range(N))
        sk = 2 / N * sum(fv[j] * mp.sin(2 * mp.pi * k * j / N) for j in range(N))
        a.append(ck); b.append(sk)
    return {"a0": a[0], "a": a[1:], "b": b[1:]}


# ---------------------------------------------------------------- Padé approximant ----
def pade(coeffs, m, n):
    """the Padé approximant [m/n] (P of degree m over Q of degree n, Q(0)=1) from Taylor coeffs c_0…c_{m+n}.
    Solves the linear system exactly over ℚ when the coefficients are rational, else in mpf."""
    c = coeffs
    rational = all(isinstance(x, (int, Q)) or (hasattr(x, "denominator")) for x in c)
    if rational:
        c = [Q(x) for x in c]
        from .exact import solve_linear
        A = [[c[m + i - j] if 0 <= m + i - j <= m + n else Q(0) for j in range(1, n + 1)] for i in range(1, n + 1)]
        rhs = [-c[m + i] for i in range(1, n + 1)]
        qsol = solve_linear(A, rhs) if n else []
        qc = [Q(1)] + (qsol or [])
        pc = [sum(c[i - j] * qc[j] for j in range(0, min(i, n) + 1)) for i in range(m + 1)]
        return {"num": pc, "den": qc}
    A = mp.matrix([[c[m + i - j] if 0 <= m + i - j <= m + n else R(0) for j in range(1, n + 1)] for i in range(1, n + 1)]) if n else None
    rhs = mp.matrix([-c[m + i] for i in range(1, n + 1)]) if n else None
    qsol = list(mp.lu_solve(A, rhs)) if n else []
    qc = [R(1)] + qsol
    pc = [sum(R(c[i - j]) * qc[j] for j in range(0, min(i, n) + 1)) for i in range(m + 1)]
    return {"num": pc, "den": qc}


# ---------------------------------------------------------------- series acceleration ----
def accelerate(partials):
    """accelerate a sequence of partial sums to its limit by Wynn's ε-algorithm (finite table)."""
    S = [R(str(x)) for x in partials]; n = len(S)
    e = [[R(0)] * (n + 1) for _ in range(n + 1)]
    for i in range(n): e[i][0] = S[i]
    best = S[-1]
    for k in range(1, n):
        for i in range(n - k):
            d = e[i + 1][k - 1] - e[i][k - 1]
            e[i][k] = e[i + 1][k - 2] + (1 / d if d != 0 else R(0))
        if (n - k) > 0 and k % 2 == 0:
            best = e[n - k - 1][k]
    return best

def series_sum_accelerated(term, N=30):
    """Σ_{n≥0} term(n) accelerated: build N partial sums, then Wynn ε."""
    partials = []; s = R(0)
    for k in range(N):
        s += R(term(k)); partials.append(s)
    return accelerate(partials)


# ---------------------------------------------------------------- convergence test (with HOLD) ----
def convergence_test(term, N=600):
    """decide whether Σ term(n) converges by a cascade of finite tests — nth-term, ratio, then Raabe's
    test (which distinguishes the p-series the ratio test cannot) — returning CONVERGES / DIVERGES /
    HOLD (genuinely inconclusive, e.g. the harmonic boundary) rather than guessing."""
    a = [abs(R(term(n))) for n in range(1, N + 1)]
    aN, aH, aP = a[-1], a[N // 2 - 1], a[-2]
    # nth-term test: if the terms do not →0, the series diverges
    if aN > R("1e-10") and (aH == 0 or aN / aH > R("0.9")):
        return {"verdict": "DIVERGES", "test": "nth-term (terms do not →0)"}
    if aN == 0 or aP == 0:
        return {"verdict": "CONVERGES", "test": "terms vanish exactly"}
    ratio = aN / aP
    if ratio < R("0.9"):
        return {"verdict": "CONVERGES", "test": "ratio", "L": mp.nstr(ratio, 6)}
    if ratio > R("1.1"):
        return {"verdict": "DIVERGES", "test": "ratio", "L": mp.nstr(ratio, 6)}
    # ratio ≈ 1 → Raabe's test:  ρ = n·(aₙ/aₙ₊₁ − 1);  ρ>1 converges, ρ<1 diverges, ρ=1 inconclusive.
    # A stable ρ bounded above 1 (p-series) → converges; a ρ DRIFTING down toward 1 (the Bertrand series
    # 1/(n·ln n)) is on the boundary that no ratio-family test resolves → HOLD, honestly.
    rho = (N - 1) * (aP / aN - 1)
    kf = max(2, N // 8)
    rho_far = kf * (a[kf - 1] / a[kf] - 1) if a[kf] else rho
    if rho < R("0.95"):
        return {"verdict": "DIVERGES", "test": "Raabe", "rho": mp.nstr(rho, 5)}
    if rho > R("1.05") and (rho - rho_far) > R("-0.05"):
        return {"verdict": "CONVERGES", "test": "Raabe", "rho": mp.nstr(rho, 5)}
    return {"verdict": "HOLD", "test": "Raabe ρ→1 (boundary — harmonic / 1·(n·ln n)-type)",
            "rho": mp.nstr(rho, 5), "reason": "genuinely borderline — refusing to guess"}


# ---------------------------------------------------------------- limits ----
def limit_oneside(f, a, side="+", M=2, K=12):
    """lim_{x→a^{side}} f(x): Richardson plateau of f(a + side·1/n)."""
    a = R(str(a)); sgn = R(1) if side == "+" else R(-1)
    col = [f(a + sgn / (M * 2 ** j)) for j in range(K)]
    for p in range(1, K):
        col = [((1 << p) * col[i + 1] - col[i]) / ((1 << p) - 1) for i in range(len(col) - 1)]
    return col[-1]

def limit_infinity(f, M=2, K=12):
    """lim_{x→∞} f(x): Richardson on 1/n applied to g(n)=f(n)."""
    col = [R(f(R(M * 2 ** j))) for j in range(K)]
    for p in range(1, K):
        col = [((1 << p) * col[i + 1] - col[i]) / ((1 << p) - 1) for i in range(len(col) - 1)]
    return col[-1]

def lhopital(fnum, fden, a, depth=5):
    """lim f/g at a resolving 0/0 (or ∞/∞) by L'Hôpital: differentiate top and bottom (finite D_ε) until
    the ratio is determinate."""
    a = R(str(a))
    num = fnum; den = fden
    for _ in range(depth):
        nv, dv = num(a), den(a)
        if abs(dv) > R("1e-20"):
            return nv / dv
        num2, den2 = num, den
        num = (lambda g: (lambda x: F.derivative(g, x)))(num2)
        den = (lambda g: (lambda x: F.derivative(g, x)))(den2)
    return num(a) / den(a) if abs(den(a)) > 0 else R("nan")
