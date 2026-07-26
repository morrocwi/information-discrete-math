"""idm.transforms — integral transforms and complex analysis as finite readouts.

Laplace / Mellin / Fourier transforms by finite (double-exponential) quadrature; the inverse Laplace by
the Stehfest algorithm (a finite weighted sum of forward-transform evaluations); the DFT/inverse DFT by
a finite radix-2 FFT; the Z-transform by a finite sum; contour integrals and the argument principle by a
finite sum around a discretized circle. No completed continuum: every value is a finite combination of
finite function evaluations.
"""
from . import functions as F
from . import integrate as INT
from .exact import binomial, factorial
import mpmath as mp
mp.mp.dps = 30
R = mp.mpf


# ---------------------------------------------------------------- Laplace / Mellin / Fourier ----
def laplace_transform(f, s):
    """L{f}(s) = ∫_0^∞ f(t) e^{−st} dt, by exp–sinh DE quadrature."""
    s = R(s)
    return INT.integrate(lambda t: f(t) * F.exp(-s * t), 0, "inf", eps=R("1e-12")).q

def mellin_transform(f, s):
    """M{f}(s) = ∫_0^∞ t^{s−1} f(t) dt, by exp–sinh DE quadrature."""
    s = R(s)
    return INT.integrate(lambda t: t ** (s - 1) * f(t) if t > 0 else R(0), 0, "inf", eps=R("1e-12")).q

def fourier_transform(f, omega, T=30):
    """F{f}(ω) = ∫_{−T}^{T} f(t) e^{−iωt} dt over a finite window (f must decay), returning (re, im)."""
    omega = R(omega)
    re = INT.integrate(lambda t: f(t) * F.cos(omega * t), -T, T, eps=R("1e-11")).q
    im = INT.integrate(lambda t: -f(t) * F.sin(omega * t), -T, T, eps=R("1e-11")).q
    return mp.mpc(re, im)

def inverse_laplace(Ffun, t, M=40):
    """f(t) from F(s) by the fixed-Talbot method (Abate–Valkó): a finite sum over a deformed contour that
    wraps the poles, so it recovers even exponentially growing f. F must be complex-evaluable."""
    t = R(t); pi = mp.pi
    d0 = 2 * M / R(5)
    total = R("0.5") * mp.exp(d0) * Ffun(d0 / t)          # k=0 (real)
    for k in range(1, M):
        th = k * pi / M; cot = mp.cot(th)
        dk = (2 * k * pi / 5) * (cot + 1j)
        gk = mp.exp(dk) * (1 + 1j * (k * pi / M) * (1 + cot * cot) - 1j * cot)
        total += mp.re(gk * Ffun(dk / t))
    return 2 / (5 * t) * total


# ---------------------------------------------------------------- FFT (finite radix-2) ----
def fft(x):
    """discrete Fourier transform by radix-2 Cooley–Tukey (len a power of two), else the direct O(n²) DFT."""
    x = [mp.mpc(v) for v in x]; n = len(x)
    if n & (n - 1):
        return _dft(x, -1)
    return _fft(x, -1)
def ifft(x):
    x = [mp.mpc(v) for v in x]; n = len(x)
    y = _fft(x, 1) if not (n & (n - 1)) else _dft(x, 1)
    return [v / n for v in y]
def _fft(x, sign):
    n = len(x)
    if n == 1: return x
    ev = _fft(x[0::2], sign); od = _fft(x[1::2], sign); out = [mp.mpc(0)] * n
    for k in range(n // 2):
        w = mp.exp(sign * 2j * mp.pi * k / n) * od[k]
        out[k] = ev[k] + w; out[k + n // 2] = ev[k] - w
    return out
def _dft(x, sign):
    n = len(x)
    return [mp.fsum(x[j] * mp.exp(sign * 2j * mp.pi * k * j / n) for j in range(n)) for k in range(n)]

def z_transform(x, z):
    """X(z) = Σ_{n} x[n] z^{−n} for a finite sequence x — a finite sum."""
    z = mp.mpc(z); return mp.fsum(mp.mpc(x[n]) * z ** (-n) for n in range(len(x)))


# ---------------------------------------------------------------- contour integration ----
def contour_integral(f, center, radius, N=2000):
    """∮ f(z) dz counterclockwise around the circle |z−center|=radius, by a finite midpoint sum. z(θ)=
    center+r e^{iθ}, dz = i r e^{iθ} dθ."""
    c = mp.mpc(center); r = R(radius); s = mp.mpc(0); h = 2 * mp.pi / N
    for k in range(N):
        th = (k + R("0.5")) * h; e = mp.exp(1j * th); z = c + r * e
        s += f(z) * 1j * r * e
    return s * h

def argument_principle(f, center, radius, N=4000):
    """(1/2πi)∮ f'/f dz = (zeros − poles) of f inside the circle — returned as the nearest integer, from a
    finite contour sum with a finite-difference f'."""
    c = mp.mpc(center); r = R(radius); s = mp.mpc(0); h = 2 * mp.pi / N; d = R("1e-8")
    for k in range(N):
        th = (k + R("0.5")) * h; e = mp.exp(1j * th); z = c + r * e
        fp = (f(z + d) - f(z - d)) / (2 * d)
        s += fp / f(z) * 1j * r * e
    val = s * h / (2j * mp.pi)
    return int(mp.nint(mp.re(val)))
