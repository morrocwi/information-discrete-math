#!/usr/bin/env python3
"""prove_it.py — DON'T TRUST THE CLAIMS. RUN THIS.  (python3 prove_it.py)

The minimal, light, but BRUTAL test that captures the roots of continuum mathematics. Every "ours"
value is computed with ONLY finite, discrete, rational operations (+ - * / , finite sums, finite
differences). NO continuum special-function call (no exp(), quad(), zeta(), gamma(), pi constant, ...)
ever PRODUCES our answer. (√ is an algebraic finite operation, allowed; the "standard" reference column
does use exp/pi/etc. — that is the textbook value we compare AGAINST, not our computation.)

If our finite-discrete numbers match, then on EVERY root of the continuum — the number π and e, the
derivative, the integral (1-D and multi-D), the limit, the infinite series, the ODE, the PDE, and even a
divergent series — the completed continuum was never formed, only read out of the finite discrete.

Then:  1) run this and be surprised  →  2) `bash formal/verify.sh` (axiom-free Coq, be convinced)  →
       3) read textbook/INFORMATION_DISCRETE_MATHEMATICS.md for the full derivations.
"""
import sys, math
try:
    import mpmath as mp
    mp.mp.dps = 40; R = mp.mpf; SQRT = mp.sqrt
    PI_STD, E_STD = mp.pi, mp.e; ZETA2_STD = mp.pi ** 2 / 6
    NS = lambda x, n=13: mp.nstr(x, n); ENGINE = "mpmath (40-digit arbitrary-precision finite arithmetic)"
except Exception:
    R = float; SQRT = math.sqrt; PI_STD, E_STD = math.pi, math.e; ZETA2_STD = math.pi ** 2 / 6
    NS = lambda x, n=13: f"{x:.11g}"; ENGINE = "float (pip install mpmath for more digits)"

# ---------- finite-discrete primitives (NO continuum function is ever called to make an answer) ----------
def exp_finite(x, N=60):                    # e^x from Σ_{k<=N} x^k/k!  (finite Taylor sum)
    x = R(x); term = R(1); s = R(1)
    for k in range(1, N + 1): term = term * x / k; s += term
    return s
def negexp(y): return R(1) / exp_finite(y, 180)     # e^{-y}, y>=0, reciprocal of a positive series (no cancellation)
def arctan_finite(x, N=400):                # arctan via Σ (-1)^k x^{2k+1}/(2k+1)  (finite series)
    x = R(x); s = R(0); p = x; x2 = x * x
    for k in range(N): s += (R(-1) ** k) * p / (2 * k + 1); p *= x2
    return s
PI_OURS = 16 * arctan_finite(R(1) / 5) - 4 * arctan_finite(R(1) / 239)   # π as a FINITE readout (Machin),
#   computed once here and reused downstream (4-D integral, heat kernel) so NO mp.pi ever makes an answer.
def D_eps(f, x, h=None):                    # derivative = finite central difference (the framework's D_ε)
    if h is None: h = R(10) ** R(-12)
    return (f(x + h) - f(x - h)) / (2 * h)
def richardson(seq, M=4, K=13):             # limit = A8-stable plateau via Richardson on h=1/n
    col = [R(seq(M * 2 ** j)) for j in range(K)]
    for p in range(1, K):
        col = [((1 << p) * col[i + 1] - col[i]) / ((1 << p) - 1) for i in range(len(col) - 1)]
    return col[-1]
def digits(a, b):
    a, b = R(a), R(b)
    if a == b: return 40
    e = abs(a - b) / max(R(1), abs(b))
    try: return max(0, int(-math.log10(float(e))))
    except Exception: return 0

rows = []
def rec(root, name, ours, std, how): rows.append((root, name, ours, std, digits(ours, std), how))

# ---------- THE ROOTS OF THE CONTINUUM, each captured by a finite-discrete readout ----------
# e  and  π  themselves
rec("constant e", "e = Σ 1/k!", exp_finite(1), E_STD, "finite Taylor sum")
rec("constant π", "π = 16·arctan(1/5) − 4·arctan(1/239)",
    PI_OURS, PI_STD, "finite Machin arctan series")
# derivative
rec("derivative", "d/dx e^x at x=1", D_eps(lambda t: exp_finite(t), R(1)), E_STD,
    "finite Taylor e^x + finite-difference D_ε (checked vs independent e)")
# integral (1-D)
def gauss(L=6, N=6000):
    h = R(2 * L) / N; s = R(0)
    for i in range(N + 1): s += (R(1) if 0 < i < N else R(1) / 2) * negexp((-R(L) + i * h) ** 2)
    return s * h
rec("integral (1-D)", "∫_{-∞}^∞ e^{-x²} dx = √π", gauss(), SQRT(PI_STD), "finite Riemann sum, series integrand")
# integral (multi-D — 4-D spacetime)
def gauss4d(L=8, N=8000):                   # ∫_{ℝ⁴} e^{-r²} = π², radial ∫ 2π²r³e^{-r²}dr (all 4 dims via r³)
    h = R(L) / N; s = R(0)                  # the 2π² solid-angle uses our FINITE π (PI_OURS), not mp.pi
    for i in range(N + 1):
        r = i * h; s += (R(1) if 0 < i < N else R(1) / 2) * 2 * PI_OURS ** 2 * r ** 3 * negexp(r * r)
    return s * h
rec("integral (4-D)", "∫_{ℝ⁴} e^{-r²} d⁴x = π²", gauss4d(), PI_STD ** 2, "finite radial Riemann sum (4-D), finite π")
# limit
rec("limit", "lim (1+1/n)^n = e", richardson(lambda n: (1 + R(1) / n) ** n), E_STD, "finite + Richardson (A8 plateau)")
# infinite series
def zeta2(Nn=200):
    S = sum((R(1) / n ** 2 for n in range(1, Nn + 1)), R(0))
    return S + R(1) / Nn - R(1) / (2 * Nn ** 2) + R(1) / (6 * Nn ** 3)   # Euler–Maclaurin tail
rec("infinite series", "ζ(2) = Σ 1/n² = π²/6", zeta2(), ZETA2_STD, "finite partial sum + Euler–Maclaurin tail")
# ODE
def rk4_exp(N=200):
    h = R(1) / N; y = R(1)
    for _ in range(N):
        k1 = y; k2 = y + h * k1 / 2; k3 = y + h * k2 / 2; k4 = y + h * k3
        y += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return y
rec("ODE", "y'=y, y(0)=1 ⇒ y(1)=e", rk4_exp(), E_STD, "finite RK4 (= I_ε of the field)")
# PDE (heat) — finite stencil + Richardson
def heat_exact(x, t, pi=PI_STD): return negexp((R(x) * R(x)) / (4 * t)) / SQRT(4 * pi * t)  # pi=PI_OURS for 'ours'
def heat_grid(dx, t0, t1, L=6):
    r = R(1) / 4; dt = r * dx * dx; ns = int(round(float((t1 - t0) / dt)))
    Nn = int(round(2 * L / float(dx))) + 1; mid = Nn // 2
    u = [heat_exact(-R(L) + i * dx, t0, PI_OURS) for i in range(Nn)]   # seed with our finite π (no mp.pi in 'ours')
    for _ in range(ns):
        u = [u[0]] + [u[i] + r * (u[i - 1] - 2 * u[i] + u[i + 1]) for i in range(1, Nn - 1)] + [u[Nn - 1]]
    return u[mid]
t0, t1 = R(1) / 5, R(1) / 2
h1, h2 = heat_grid(R(1) / 20, t0, t1), heat_grid(R(1) / 40, t0, t1)
rec("PDE (heat)", "u_t=u_xx, u(0,0.5)", (4 * h2 - h1) / 3, heat_exact(0, t1), "explicit finite-difference stencil + Richardson")
# divergent series (the shock) — 1+2+3+… = −1/12, extracted by a FINITE smoothed-sum reading
rec("divergent series", "1+2+3+… (regularized) = −1/12",
    (lambda e: (S1 := sum((n * negexp(e * n) for n in range(1, int(80 / float(e)))), R(0)),
                S2 := sum((n * negexp((e / 2) * n) for n in range(1, int(160 / float(e)))), R(0)),
                # remove 1/ε² pole via Richardson: T = (4·(S2 − 4/ε²) − (S1 − 1/ε²))/3  → constant −1/12
                ((4 * (S2 - 4 / e ** 2) - (S1 - 1 / e ** 2)) / 3))[-1])(R(1) / 40),
    R(-1) / 12, "finite smoothed sum Σ n·e^{−εn}, pole removed by Richardson")

# ---------- report ----------
print("=" * 100)
print(f"  prove_it.py — engine: {ENGINE}   (every 'ours' value below is FINITE-DISCRETE ONLY)")
print("=" * 100)
print(f"  {'root of the continuum':18} {'test':30} {'ours (finite)':17} {'standard':13} {'dig':>4}")
print("  " + "-" * 96)
ok = 0
for root, name, ours, std, dig, how in rows:
    good = dig >= 6; ok += good
    print(f"  {root:18} {name:30} {NS(ours):17} {NS(std,11):13} {dig:>3}  {'PASS' if good else 'FAIL'}")
print("  " + "-" * 96)
print(f"  {ok}/{len(rows)} roots of the continuum reproduced to >=6 digits — ONLY finite-discrete operations,")
print(f"  NO exp/quad/zeta/gamma/pi call produced any 'ours' answer. The continuum was never formed.")
print(f"  VERDICT: {'the roots of the continuum are captured by finite readouts — TRUSTWORTHY on these tests' if ok==len(rows) else 'CHECK FAILURES'}.")
print("=" * 100)
sys.exit(0 if ok == len(rows) else 1)
