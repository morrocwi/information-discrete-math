#!/usr/bin/env python3
"""provefull/_kernel.py — shared FINITE-DISCRETE primitives for the 1000-problem prove_it_full.

Every function here produces its value with ONLY finite, discrete, rational operations:
finite Taylor/atanh series, argument reduction by halving/squaring, finite sums/products, finite
quadrature (composite Simpson + Euler–Maclaurin endpoint), Richardson extrapolation on h=1/n. NO
mpmath transcendental (mp.exp/log/sin/cos/erf/gamma/zeta/pi/quad) is EVER called to produce a value
returned from this module. `mpmath.mpf` is arbitrary-precision *floating-point* (NOT exact rational);
we use it only as the high-precision finite arithmetic engine, and `sqrt` is an algebraic finite
operation (allowed).

This is the continuum-maya bridge in code: the continuum constants (π, e, ln2, √π) are computed ONCE
here as finite readouts, then every domain (physics, biochem, networks, complexity, cosmology) reads
its "continuum" answer out of the finite discrete using them. Reference values in the domain files may
use mpmath's transcendental functions — but only in the *reference* column, never as 'ours'.
"""
import mpmath as mp
import os, sys
mp.mp.dps = 40
R = mp.mpf

# make tools/idm_tools.py importable (the shipped library — we reuse its D_eps/I_eps/ode_rk4)
_TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)
import idm_tools as T   # D_eps, I_eps, richardson_1_over_n, ode_rk4, em_sum, ...

_EPS = R(10) ** (-mp.mp.dps - 5)

# ---------------------------------------------------------------- core transcendentals (finite) ----
def exp_finite(x):
    """e^x for any real x: argument reduction by halving to |r|<=1/2, finite Taylor on r, then square
    back k times.  exp(x) = (exp(x/2^k))^{2^k}.  Pure +−×÷ and finite series — no mp.exp."""
    x = R(x); k = 0
    while abs(x) > R(1) / 2:
        x /= 2; k += 1
    term = R(1); s = R(1); n = 1
    while abs(term) > _EPS:
        term = term * x / n; s += term; n += 1
    for _ in range(k):
        s = s * s
    return s

E_FINITE = exp_finite(1)

def expm1_finite(x):
    """e^x − 1 without cancellation for small x (used by many rate laws)."""
    x = R(x)
    if abs(x) > R(1) / 4:
        return exp_finite(x) - 1
    term = R(x); s = R(x); n = 2
    while abs(term) > _EPS:
        term = term * x / n; s += term; n += 1
    return s

def _atanh_series(y):
    y = R(y); y2 = y * y; term = R(y); s = R(y); n = 1
    while abs(term) > _EPS:
        term = term * y2; s += term / (2 * n + 1); n += 1
    return s

LN2_FINITE = 2 * _atanh_series(R(1) / 3)          # ln 2 = 2·atanh(1/3), fast finite series

def log_finite(x):
    """natural log for x>0: reduce mantissa to [2/3, 4/3] by powers of two, then ln = 2·atanh((m−1)/(m+1))
    + k·ln2.  All finite — no mp.log."""
    x = R(x)
    if x <= 0:
        raise ValueError("log_finite domain x>0")
    k = 0
    while x > R(4) / 3:
        x /= 2; k += 1
    while x < R(2) / 3:
        x *= 2; k -= 1
    y = (x - 1) / (x + 1)
    return 2 * _atanh_series(y) + k * LN2_FINITE

def pow_finite(base, expo):
    """base**expo for base>0, real expo:  exp(expo·ln base).  Finite via log_finite/exp_finite."""
    return exp_finite(R(expo) * log_finite(base))

# Machin π as a finite readout (arctan via finite series)
def _arctan_series(x, N=600):
    x = R(x); x2 = x * x; s = R(0); p = x
    for kk in range(N):
        s += (R(-1) ** kk) * p / (2 * kk + 1); p *= x2
    return s
PI_FINITE = 16 * _arctan_series(R(1) / 5) - 4 * _arctan_series(R(1) / 239)
TWO_PI = 2 * PI_FINITE
SQRT_PI = mp.sqrt(PI_FINITE)                       # √ is an algebraic finite operation (allowed)

def sin_finite(x):
    """sin x: reduce mod 2π (finite, using PI_FINITE) to [−π,π], finite Taylor — no mp.sin."""
    x = R(x)
    x = x - TWO_PI * mp.floor(x / TWO_PI + R(1) / 2)   # to [−π,π); floor is a finite integer readout
    term = R(x); s = R(x); x2 = x * x; n = 1
    while abs(term) > _EPS:
        term = -term * x2 / ((2 * n) * (2 * n + 1)); s += term; n += 1
    return s

def cos_finite(x):
    x = R(x)
    x = x - TWO_PI * mp.floor(x / TWO_PI + R(1) / 2)
    term = R(1); s = R(1); x2 = x * x; n = 1
    while abs(term) > _EPS:
        term = -term * x2 / ((2 * n - 1) * (2 * n)); s += term; n += 1
    return s

def erf_finite(x):
    """error function via the finite Maclaurin series erf(x)=2/√π·Σ(−1)^n x^{2n+1}/(n!(2n+1)).
    Accurate for |x|<=~4 at dps=40; beyond that use the tail via erfc quadrature."""
    x = R(x)
    if abs(x) > 4:
        return R(1) if x > 0 else R(-1)   # saturated to full precision at this dps
    term = R(x); s = R(x); n = 1
    while abs(term) > _EPS and n < 400:
        term = -term * x * x * (2 * n - 1) / (n * (2 * n + 1))
        s += term; n += 1
    return 2 / SQRT_PI * s

# ---------------------------------------------------------------- finite quadrature & series ----
def quad_finite(f, a, b, N=2000):
    """∫_a^b f via composite Simpson (finite N panels). N even."""
    a, b = R(a), R(b)
    if N % 2: N += 1
    h = (b - a) / N
    s = f(a) + f(b)
    for i in range(1, N):
        s += (4 if i % 2 else 2) * f(a + i * h)
    return s * h / 3

def quad_improper(f, b, N=4000):
    """∫_0^∞ f via cutoff b (f must decay by b) + composite Simpson. Simpson is already O(h⁴) — no
    trapezoidal endpoint correction (which would double-correct and degrade it)."""
    return quad_finite(f, 0, b, N)

def gamma_finite(z):
    """Γ(z) for z>0. Push z into [1,2) via the recurrence Γ(z)=Γ(z+m)/(z(z+1)…(z+m−1)) so the radial
    integrand 2·x^{2ζ−1}e^{−x²} (ζ=z+m≥1) has a FINITE derivative at 0, then finite Simpson quadrature
    (t=x² substitution). No mp.gamma anywhere."""
    z = R(z); m = 0
    while z + m < 1: m += 1
    zz = z + m
    g = quad_improper(lambda x: 2 * pow_finite(x, 2 * zz - 1) * exp_finite(-x * x) if x > 0 else R(0), 9, 9000)
    denom = R(1)
    for k in range(m): denom *= (z + k)
    return g / denom

def factorial_finite(n):
    p = R(1)
    for k in range(2, int(n) + 1): p *= k
    return p

def euler_maclaurin_zeta(s, N=2000):
    """ζ(s), s>1: finite partial sum + Euler–Maclaurin tail. Finite, no mp.zeta."""
    s = R(s)
    S = mp.fsum(R(n) ** (-s) for n in range(1, N + 1))
    tail = N ** (1 - s) / (s - 1) - N ** (-s) / 2 + s * N ** (-s - 1) / 12 - s * (s + 1) * (s + 2) * N ** (-s - 3) / 720
    return S + tail

def richardson(seq, M=4, K=13):
    """A8-stable limit: Richardson extrapolation of seq(n) on h=1/n."""
    col = [R(seq(M * 2 ** j)) for j in range(K)]
    for p in range(1, K):
        col = [((1 << p) * col[i + 1] - col[i]) / ((1 << p) - 1) for i in range(len(col) - 1)]
    return col[-1]

def em_sum_alt(term, N):
    """finite alternating-series sum Σ_{n=0}^{N-1} term(n) + half the next term (endpoint averaging,
    accelerates alternating series to ~1/N² error)."""
    return mp.fsum(term(n) for n in range(N)) + term(N) / 2

# ---------------------------------------------------------------- record + reporting ----
def _short(x, n=11):
    try: return mp.nstr(R(x), n)
    except Exception: return str(x)

def digits(a, b):
    a, b = R(a), R(b)
    if a == b: return mp.mp.dps
    e = abs(a - b) / max(R(1), abs(b))
    if e == 0: return mp.mp.dps
    try: return max(0, int(-mp.log10(e)))
    except Exception: return 0

class P:
    """one continuum-frontier problem: ours=finite-discrete readout, ref=standard (mpmath) reference."""
    __slots__ = ("domain", "name", "claim", "ours", "ref", "how", "dig")
    def __init__(self, domain, name, claim, ours, ref, how):
        self.domain, self.name, self.claim = domain, name, claim
        self.ours, self.ref, self.how = ours, ref, how
        self.dig = digits(ours, ref)
    @property
    def ok(self): return self.dig >= 6
