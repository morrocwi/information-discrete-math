"""idm.special — the continuum's special functions, each a FINITE readout.

Bessel/Airy by finite power series, the orthogonal polynomials by their finite three-term recurrences,
the exponential/sine/cosine integrals and Fresnel functions by finite series, the complete elliptic
integrals by the arithmetic–geometric mean (a finite iteration), the hypergeometric functions by finite
truncated series, Lambert W by finite Newton, and the Dirichlet/polylog family by finite sums with
Euler–Maclaurin/acceleration. No continuum library call (mp.besselj, mp.gamma, …) produces a value; the
constants π, γ used inside are themselves finite readouts. mpmath.mpf is the arithmetic engine.
"""
from . import functions as F
from .exact import factorial, binomial
import mpmath as mp
_DPS = 40                                                # this module's declared working precision
mp.mp.dps = _DPS
R = mp.mpf
_TINY = R(10) ** (-mp.mp.dps - 5)
PI = F.pi()
GAMMA_E = None
def _euler():                                            # Euler–Mascheroni γ as a finite readout
    global GAMMA_E
    if GAMMA_E is None:
        # compute at the module's FIXED precision, never the ambient global dps — this constant is
        # cached process-wide, so caching it at whatever precision a caller happened to leave would
        # make every γ-dependent readout (E1, Ei, digamma, …) depend on call order.
        with mp.workdps(_DPS):
            N = 2000; H = mp.fsum(R(1) / n for n in range(1, N + 1))
            GAMMA_E = H - F.log(R(N)) - R(1) / (2 * N) + R(1) / (12 * N ** 2)
    return GAMMA_E


def _gamma(z): return __import__("provefull._kernel", fromlist=["gamma_finite"]).gamma_finite(z)
def gamma(z): return _gamma(R(z))
def beta(a, b): return _gamma(R(a)) * _gamma(R(b)) / _gamma(R(a) + R(b))

def digamma(x):
    x = R(x); acc = R(0)
    while x < 10: acc -= 1 / x; x += 1                    # recurrence ψ(x)=ψ(x+1)−1/x up to the asymptotic regime
    return acc + F.log(x) - 1 / (2 * x) - 1 / (12 * x ** 2) + 1 / (120 * x ** 4) - 1 / (252 * x ** 6)


# ---------------------------------------------------------------- Bessel (finite series) ----
def bessel_J(n, x):
    n = int(n); x = R(x); term = (x / 2) ** n / factorial(n); s = R(0); m = 0; sign = 1
    while True:
        s += sign * term; m += 1
        term = term * (x / 2) ** 2 / (m * (m + n)); sign = -sign
        if abs(term) < _TINY and m > 2: break
    return s
def bessel_I(n, x):
    n = int(n); x = R(x); term = (x / 2) ** n / factorial(n); s = R(0); m = 0
    while True:
        s += term; m += 1; term = term * (x / 2) ** 2 / (m * (m + n))
        if abs(term) < _TINY and m > 2: break
    return s


# ---------------------------------------------------------------- orthogonal polynomials (recurrences) ----
def legendre_P(n, x):
    x = R(x); p0, p1 = R(1), x
    if n == 0: return p0
    for k in range(2, n + 1): p0, p1 = p1, ((2 * k - 1) * x * p1 - (k - 1) * p0) / k
    return p1
def hermite_H(n, x):                                     # physicists'
    x = R(x); h0, h1 = R(1), 2 * x
    if n == 0: return h0
    for k in range(2, n + 1): h0, h1 = h1, 2 * x * h1 - 2 * (k - 1) * h0
    return h1
def laguerre_L(n, x, alpha=0):
    x = R(x); a = R(alpha); l0, l1 = R(1), 1 + a - x
    if n == 0: return l0
    for k in range(2, n + 1): l0, l1 = l1, ((2 * k - 1 + a - x) * l1 - (k - 1 + a) * l0) / k
    return l1
def chebyshev_T(n, x):
    x = R(x); t0, t1 = R(1), x
    if n == 0: return t0
    for k in range(2, n + 1): t0, t1 = t1, 2 * x * t1 - t0
    return t1
def chebyshev_U(n, x):
    x = R(x); u0, u1 = R(1), 2 * x
    if n == 0: return u0
    for k in range(2, n + 1): u0, u1 = u1, 2 * x * u1 - u0
    return u1


# ---------------------------------------------------------------- exp/trig integrals & Fresnel ----
def _erf(x): return F.erf(R(x))
def erf(x): return _erf(x)
def erfc(x): return 1 - _erf(x)
def Ei(x):                                               # exponential integral, x>0
    x = R(x); s = R(0); term = R(1); k = 1
    while True:
        term *= x / k; add = term / k; s += add; k += 1
        if abs(add) < _TINY and k > 3: break
    return _euler() + F.log(abs(x)) + s
def E1(x):                                               # E1(x) = -Ei(-x) for x>0
    x = R(x); s = R(0); term = R(1); k = 1; sign = -1
    while True:
        term *= x / k; add = sign * term / k; s += add; k += 1; sign = -sign
        if abs(add) < _TINY and k > 3: break
    return -_euler() - F.log(x) - s
def li(x): return Ei(F.log(R(x)))                        # logarithmic integral
def Si(x):
    x = R(x); term = x; s = R(0); n = 0; sign = 1
    while True:
        add = sign * term / (2 * n + 1); s += add; n += 1
        term = term * x * x / ((2 * n) * (2 * n + 1)); sign = -sign
        if abs(add) < _TINY and n > 2: break
    return s
def Ci(x):
    x = R(x); term = R(1); s = R(0); n = 1; sign = -1
    while True:
        term = term * x * x / ((2 * n - 1) * (2 * n)) if n > 1 else x * x / 2
        add = sign * term / (2 * n); s += add; n += 1; sign = -sign
        if abs(add) < _TINY and n > 3: break
    return _euler() + F.log(x) + s
def fresnel_S(x):
    x = R(x); s = R(0); n = 0; sign = 1
    while True:
        num = (PI / 2) ** (2 * n + 1) * x ** (4 * n + 3)
        add = sign * num / (factorial(2 * n + 1) * (4 * n + 3)); s += add; n += 1; sign = -sign
        if abs(add) < _TINY and n > 2: break
    return s
def fresnel_C(x):
    x = R(x); s = R(0); n = 0; sign = 1
    while True:
        num = (PI / 2) ** (2 * n) * x ** (4 * n + 1)
        add = sign * num / (factorial(2 * n) * (4 * n + 1)); s += add; n += 1; sign = -sign
        if abs(add) < _TINY and n > 2: break
    return s


# ---------------------------------------------------------------- elliptic integrals (AGM) ----
def _agm(a, b):
    a, b = R(a), R(b)
    for _ in range(60):                                  # AGM converges quadratically — 60 iters is full precision
        a, b = (a + b) / 2, mp.sqrt(a * b)
    return a
def elliptic_K(m):
    """complete elliptic integral of the first kind, parameter m=k². K = π/(2·AGM(1,√(1−m)))."""
    return PI / (2 * _agm(1, mp.sqrt(1 - R(m))))
def elliptic_E(m):
    """complete elliptic integral of the second kind, parameter m. E = K·(1 − Σ 2^{n-1} c_n²) via the
    descending AGM (c_0²=m, c_n=(a_{n-1}−b_{n-1})/2)."""
    m = R(m); a, b = R(1), mp.sqrt(1 - m); s = m / 2; p = R(1)
    for _ in range(60):                                  # c_n → 0 quadratically; later 2^{n-1}c_n² terms vanish
        c = (a - b) / 2; s += p * c * c; p *= 2; a, b = (a + b) / 2, mp.sqrt(a * b)
    return PI / (2 * a) * (1 - s)


# ---------------------------------------------------------------- hypergeometric (finite series) ----
def hyp2f1(a, b, c, x):
    a, b, c, x = R(a), R(b), R(c), R(x); term = R(1); s = R(0); n = 0
    while True:
        s += term; term = term * (a + n) * (b + n) / ((c + n) * (n + 1)) * x; n += 1
        if abs(term) < _TINY and n > 3: break
        if n > 100000: break
    return s
def hyp1f1(a, b, x):
    a, b, x = R(a), R(b), R(x); term = R(1); s = R(0); n = 0
    while True:
        s += term; term = term * (a + n) / ((b + n) * (n + 1)) * x; n += 1
        if abs(term) < _TINY and n > 3: break
    return s


# ---------------------------------------------------------------- Airy (finite series) ----
def airy_Ai(x):
    x = R(x); c1 = 1 / (3 ** (R(2) / 3) * _gamma(R(2) / 3)); c2 = 1 / (3 ** (R(1) / 3) * _gamma(R(1) / 3))
    f = R(0); tf = R(1); g = R(0); tg = R(1); k = 0
    while k < 400:
        f += tf; g += tg
        tf = tf * x ** 3 / ((3 * k + 2) * (3 * k + 3))
        tg = tg * x ** 3 / ((3 * k + 3) * (3 * k + 4)); k += 1
        if abs(tf) < _TINY and abs(tg * x) < _TINY and k > 3: break
    return c1 * f - c2 * (x * g)
def lambert_W(x, branch=0):
    x = R(x); w = F.log(1 + x) if x > 0 else R(x)
    for _ in range(80):
        ew = F.exp(w); f = w * ew - x
        w2 = w - f / (ew * (w + 1) - (w + 2) * f / (2 * w + 2))
        if abs(w2 - w) < _TINY: return w2
        w = w2
    return w


# ---------------------------------------------------------------- Dirichlet / polylog ----
def polylog(s, x, N=200000):
    s, x = R(s), R(x)
    if abs(x) >= 1: return _zeta(s)
    tot = R(0); xk = x; k = 1
    while k < N:
        t = xk / R(k) ** s; tot += t
        if abs(t) < _TINY and k > 3: break
        xk *= x; k += 1
    return tot
def _zeta(s, N=3000):
    s = R(s); S = mp.fsum(R(k) ** (-s) for k in range(1, N + 1))
    return S + N ** (1 - s) / (s - 1) - N ** (-s) / 2 + s * N ** (-s - 1) / 12
def dirichlet_eta(s):
    s = R(s)
    if abs(s - 1) < R(10) ** -20: return F.log(2)          # η(1)=ln2 (removes the ζ pole)
    return (1 - 2 ** (1 - s)) * _zeta(s)
def dirichlet_beta(s, N=4000):
    s = R(s); S = mp.fsum(R(-1) ** k / R(2 * k + 1) ** s for k in range(N))
    return S + R(-1) ** N / R(2 * N + 1) ** s / 2          # endpoint averaging (alternating acceleration)
def hurwitz_zeta(s, a, N=3000):
    s, a = R(s), R(a); S = mp.fsum((k + a) ** (-s) for k in range(N))
    return S + (N + a) ** (1 - s) / (s - 1) - (N + a) ** (-s) / 2
