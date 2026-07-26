#!/usr/bin/env python3
"""prove_it_lite.py — ZERO dependencies, BRUTAL frontier.  DON'T TRUST THE CLAIMS. RUN THIS.

    python3 prove_it_lite.py          # no pip install, no mpmath, no sympy — just Python's stdlib

8 of the hardest *continuum frontiers* — the quantum blackbody integral, Apéry's constant ζ(3),
Catalan's constant, the Gaussian integral, the Wien peak (a transcendental root with no closed form),
the Basel sum, Planck's law, and the divergent series 1+2+3+…=−1/12 — each reproduced from ONLY
finite, discrete, rational operations (+ − × ÷, finite sums, finite differences, a finite Newton step)
in ordinary double precision. No third-party library. `math` is touched ONLY for the reference column
(the standard value we compare against), never to produce an 'ours' value.

These are not toy sums: they are the places physics and analysis reach for the completed continuum.
Here each is a finite readout — the continuum is never formed. If they match on your machine (they do,
to ~6–13 digits), the claim "you don't need continuum mathematics to COMPUTE the frontier" is
demonstrated by you, locally, with nothing but the interpreter.

Full precision (40 digits): prove_it.py (needs mpmath).  1000 problems across 5 domains: prove_it_full.py.
"""
import math   # reference column ONLY — the standard values to beat, never an 'ours' input

# ---------- finite-discrete primitives (pure float; NO continuum function makes an 'ours' answer) ----------
def exp_finite(x, N=170):                 # e^x = Σ x^k/k! (finite Taylor; all-positive for x≥0 → no cancellation)
    term = 1.0; s = 1.0
    for k in range(1, N + 1):
        term = term * x / k; s += term
    return s

def negexp(y): return 1.0 / exp_finite(y)          # e^{-y}, y≥0, reciprocal of a positive series (float-safe)
def expm1_finite(x):                                # e^x − 1 without cancellation near 0
    term = float(x); s = float(x); k = 2
    while abs(term) > 1e-18 and k < 200:
        term = term * x / k; s += term; k += 1
    return s

def arctan_finite(x, N=1000):             # arctan x = Σ (−1)^k x^{2k+1}/(2k+1) (finite series, |x|<1)
    s = 0.0; p = x; x2 = x * x
    for k in range(N):
        s += ((-1) ** k) * p / (2 * k + 1); p *= x2
    return s

def simpson(f, a, b, N=4000):             # finite composite Simpson quadrature
    if N % 2: N += 1
    h = (b - a) / N; s = f(a) + f(b)
    for i in range(1, N):
        s += (4 if i % 2 else 2) * f(a + i * h)
    return s * h / 3

def richardson(seq, M=2, K=9):            # limit via Richardson extrapolation on h=1/n (float-stable, modest K)
    col = [float(seq(M * 2 ** j)) for j in range(K)]
    for p in range(1, K):
        f = float(1 << p)
        col = [(f * col[i + 1] - col[i]) / (f - 1) for i in range(len(col) - 1)]
    return col[-1]

def digits(a, b):
    if a == b: return 15
    e = abs(a - b) / max(1.0, abs(b))
    return max(0, int(-math.log10(e))) if e > 0 else 15

PI_OURS = 16 * arctan_finite(1 / 5) - 4 * arctan_finite(1 / 239)   # π as a finite readout (Machin)

rows = []
def rec(root, name, ours, std, how): rows.append((root, name, ours, std, digits(ours, std), how))

# ---------- 8 BRUTAL CONTINUUM FRONTIERS (float, finite-discrete) ----------
# 1) Planck / blackbody radiation:  ∫₀^∞ x³/(eˣ−1) dx = π⁴/15  (the integral behind Stefan–Boltzmann)
planck = simpson(lambda x: 0.0 if x == 0 else x ** 3 / expm1_finite(x), 0.0, 32.0, 6000)
rec("blackbody (physics)", "∫₀^∞ x³/(eˣ−1)dx = π⁴/15", planck, math.pi ** 4 / 15, "finite Simpson + finite eˣ−1")

# 2) Wien peak: the blackbody spectrum (wavelength form) peaks where 5(1−e^{−x})=x — transcendental, NO closed form
def wien():
    x = 4.0
    for _ in range(60):                             # finite Newton on g(x)=x−5+5e^{−x}
        g = x - 5 + 5 * negexp(x); gp = 1 - 5 * negexp(x)
        x -= g / gp
    return x
rec("Wien peak (physics)", "root of 5(1−e^{−x})=x  ≈ 4.965114231", wien(), 4.965114231744276, "finite Newton iteration")

# 3) Basel sum → π:  ζ(2)=Σ1/n² = π²/6
def zeta2(N=300):
    S = sum(1.0 / n ** 2 for n in range(1, N + 1))
    return S + 1.0 / N - 1.0 / (2 * N ** 2) + 1.0 / (6 * N ** 3)   # Euler–Maclaurin tail
rec("Basel ζ(2) (analysis)", "Σ 1/n² = π²/6", zeta2(), math.pi ** 2 / 6, "finite sum + Euler–Maclaurin tail")

# 4) Apéry's constant ζ(3) — famously irrational, no elementary closed form
def zeta3(N=2000):
    S = sum(1.0 / n ** 3 for n in range(1, N + 1))
    return S + 1.0 / (2 * N ** 2) - 1.0 / (2 * N ** 3) + 1.0 / (4 * N ** 4)   # Euler–Maclaurin tail
rec("Apéry ζ(3) (analysis)", "Σ 1/n³ = 1.2020569…", zeta3(), 1.2020569031595942854, "finite sum + Euler–Maclaurin tail")

# 5) Catalan's constant G — an open-irrationality frontier constant
def catalan(N=6000):
    S = sum(((-1) ** n) / (2 * n + 1) ** 2 for n in range(N))
    return S + 0.5 * ((-1) ** N) / (2 * N + 1) ** 2                 # endpoint averaging (alternating accel.)
rec("Catalan G (analysis)", "Σ(−1)ⁿ/(2n+1)² = 0.9159655…", catalan(), 0.915965594177219015, "finite alternating sum + averaging")

# 6) Gaussian integral:  ∫_{−∞}^∞ e^{−x²} dx = √π  (the normalization behind all of statistics & QM)
def gauss(L=6.0, N=3000):
    h = 2 * L / N; s = 0.0
    for i in range(N + 1):
        s += (1.0 if 0 < i < N else 0.5) * negexp((-L + i * h) ** 2)
    return s * h
rec("Gaussian (statistics/QM)", "∫_{−∞}^∞ e^{−x²}dx = √π", gauss(), math.sqrt(math.pi), "finite Riemann sum, series integrand")

# 7) Planck photon-number integral:  ∫₀^∞ x²/(eˣ−1) dx = 2·ζ(3)  (photon number density of a blackbody)
photons = simpson(lambda x: 0.0 if x == 0 else x ** 2 / expm1_finite(x), 0.0, 32.0, 6000)
rec("photon density (cosmology)", "∫₀^∞ x²/(eˣ−1)dx = 2ζ(3)", photons, 2 * 1.2020569031595942854, "finite Simpson + finite eˣ−1")

# 8) The shock — divergent series 1+2+3+… = −1/12 (Casimir energy / string theory), from a FINITE reading
def zeta_m1(e=0.02):
    S1 = sum(n * negexp(e * n) for n in range(1, int(80 / e)))
    S2 = sum(n * negexp((e / 2) * n) for n in range(1, int(160 / e)))
    return (4 * (S2 - 4 / e ** 2) - (S1 - 1 / e ** 2)) / 3          # remove 1/ε² pole via Richardson → −1/12
rec("1+2+3+… (physics)", "regularized Σ n = −1/12", zeta_m1(), -1.0 / 12, "finite smoothed sum Σ n·e^{−εn}, pole removed")

# ---------- report ----------
print("=" * 96)
print("  prove_it_lite.py — ZERO dependencies (Python stdlib float). 8 continuum FRONTIERS, finite-discrete.")
print("=" * 96)
print(f"  {'frontier':26} {'test':34} {'ours':14} {'standard':12} {'dig':>3}")
print("  " + "-" * 92)
ok = 0
for root, name, ours, std, dig, how in rows:
    good = dig >= 6; ok += good
    print(f"  {root:26} {name:34} {ours:<14.9g} {std:<12.8g} {dig:>3}  {'PASS' if good else 'FAIL'}")
print("  " + "-" * 92)
print(f"  {ok}/{len(rows)} continuum frontiers reproduced to ≥6 digits — pure stdlib float, NO third-party library,")
print(f"  NO math.exp/pi/e produced any 'ours' answer (reference column only). The continuum was never formed.")
print("=" * 96)
raise SystemExit(0 if ok == len(rows) else 1)
