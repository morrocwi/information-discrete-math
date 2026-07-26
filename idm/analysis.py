"""idm.analysis — finite-discrete analysis: root-finding, optimization, interpolation, sums, spectra.

Finite iterations and finite readouts throughout (Newton/bisection, golden-section, Lagrange, finite
partial sums + Euler–Maclaurin/Richardson, finite 2-D grids, Faddeev–LeVerrier + Durand–Kerner). No
completed limit is formed; results are `finite_diagnostic` to a declared tolerance.
"""
from fractions import Fraction as Q
from . import functions as F
from . import exact as X

import mpmath as mp
mp.mp.dps = 40
R = mp.mpf


def root_find(f, a=None, b=None, x0=None, tol=mp.mpf("1e-30"), it=200):
    """a real root of f: bisection on [a,b] if a sign change is bracketed, else Newton from x0."""
    if a is not None and b is not None:
        fa, fb = f(R(a)), f(R(b))
        if fa * fb <= 0:
            lo, hi = R(a), R(b)
            for _ in range(it):
                mid = (lo + hi) / 2; fm = f(mid)
                if abs(fm) < tol: return mid
                if fa * fm <= 0: hi = mid
                else: lo, fa = mid, fm
            return (lo + hi) / 2
    x = R(x0 if x0 is not None else (R(a) + R(b)) / 2 if a is not None else 0)
    for _ in range(it):
        fx = f(x); dfx = F.derivative(f, x)
        if dfx == 0: break
        nx = x - fx / dfx
        if abs(nx - x) < tol: return nx
        x = nx
    return x


def minimize_1d(f, a, b, it=200):
    """minimizer of a unimodal f on [a,b] by golden-section search (finite)."""
    a, b = R(a), R(b); g = (mp.sqrt(5) - 1) / 2
    c = b - g * (b - a); d = a + g * (b - a); fc, fd = f(c), f(d)
    for _ in range(it):
        if fc < fd: b, d, fd = d, c, fc; c = b - g * (b - a); fc = f(c)
        else: a, c, fc = c, d, fd; d = a + g * (b - a); fd = f(d)
    x = (a + b) / 2; return x, f(x)


def interpolate(points, x):
    """Lagrange interpolation through (xi, yi) evaluated at x — exact ℚ when the data is rational."""
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    rational = all(float(v) == v for v in xs + ys + [x]) and all(
        isinstance(v, (int, Q)) or (isinstance(v, float) and v.is_integer()) for v in xs + ys)
    if rational:
        xq = [Q(v) for v in xs]; yq = [Q(v) for v in ys]; X0 = Q(x); tot = Q(0)
        for i in range(len(points)):
            term = yq[i]
            for j in range(len(points)):
                if j != i: term *= (X0 - xq[j]) / (xq[i] - xq[j])
            tot += term
        return tot
    xm = [R(v) for v in xs]; ym = [R(v) for v in ys]; X0 = R(x); tot = R(0)
    for i in range(len(points)):
        term = ym[i]
        for j in range(len(points)):
            if j != i: term *= (X0 - xm[j]) / (xm[i] - xm[j])
        tot += term
    return tot


def series_sum(term, N=2000, tail=None):
    """finite partial sum Σ_{n=1}^{N} term(n) (+ optional Euler–Maclaurin tail correction)."""
    S = mp.fsum(term(n) for n in range(1, N + 1))
    return S + (tail(N) if tail else 0)


def zeta(s, N=3000):
    """ζ(s): s>1 by finite sum + Euler–Maclaurin; ζ(0)=−1/2; negative integers by ζ(−n)=−B_{n+1}/(n+1)."""
    s = mp.mpf(str(s))
    if s == 0: return mp.mpf(-1) / 2
    if s < 1 and s == int(s):
        n = int(-s); return -X.bernoulli(n + 1) / (n + 1)      # exact ℚ (regularized)
    S = mp.fsum(mp.mpf(k) ** (-s) for k in range(1, N + 1))
    tail = N ** (1 - s) / (s - 1) - N ** (-s) / 2 + s * N ** (-s - 1) / 12
    return S + tail


def regularized_sum(power=1, e=mp.mpf("1/40")):
    """the regularized value of 1^p+2^p+3^p+… = ζ(−p): a finite smoothed sum Σ n^p e^{−εn}, its explicit
    pole p!/ε^{p+1} subtracted, and the remaining O(ε) tail sent to zero by a Richardson tableau. (The
    small-ε expansion is p!/ε^{p+1} + ζ(−p) + O(ε), with no intermediate poles.)"""
    p = int(power); pole = X.factorial(p)
    def g(ee):
        Nn = int(80 / float(ee))
        S = mp.fsum(mp.mpf(n) ** p * mp.e ** (-ee * n) for n in range(1, Nn))
        return S - pole / ee ** (p + 1)
    col = [g(e / 2 ** j) for j in range(9)]
    for q in range(1, 9):
        col = [(2 ** q * col[i + 1] - col[i]) / (2 ** q - 1) for i in range(len(col) - 1)]
    return col[-1]


def double_integral(f, ax, bx, ay, by, N=200):
    """∫∫ f(x,y) dx dy on a finite [ax,bx]×[ay,by] grid (composite midpoint)."""
    ax, bx, ay, by = R(ax), R(bx), R(ay), R(by); hx = (bx - ax) / N; hy = (by - ay) / N; s = R(0)
    for i in range(N):
        xi = ax + (i + mp.mpf("0.5")) * hx
        for j in range(N):
            yj = ay + (j + mp.mpf("0.5")) * hy; s += f(xi, yj)
    return s * hx * hy


def char_poly(A):
    """characteristic polynomial coefficients (low→high, monic) via Faddeev–LeVerrier — exact over ℚ."""
    n = len(A); M = [[Q(x) for x in row] for row in A]
    I = [[Q(1) if i == j else Q(0) for j in range(n)] for i in range(n)]
    c = [Q(1)]; Mk = [row[:] for row in M]; trace = lambda T: sum(T[i][i] for i in range(n))
    coeffs = [Q(1)]                                            # leading (x^n)
    for k in range(1, n + 1):
        ck = -trace(Mk) / k; coeffs.append(ck)
        if k < n:
            T = [[Mk[i][j] + (ck if i == j else 0) for j in range(n)] for i in range(n)]
            Mk = X.mat_mul(M, T)
    return list(reversed(coeffs))                             # low→high


def poly_roots(coeffs, it=500, tol=mp.mpf("1e-28")):
    """all (complex) roots of a polynomial (coeffs low→high) by Durand–Kerner — finite iteration."""
    c = [mp.mpf(str(v)) if not isinstance(v, complex) else v for v in coeffs]
    while len(c) > 1 and c[-1] == 0: c = c[:-1]
    n = len(c) - 1
    if n <= 0: return []
    lead = c[-1]; mon = [ci / lead for ci in c]
    def P(z):
        r = mon[-1]
        for a in reversed(mon[:-1]): r = r * z + a
        return r
    roots = [mp.mpc(0.4, 0.9) ** k for k in range(n)]
    for _ in range(it):
        moved = mp.mpf(0)
        for i in range(n):
            num = P(roots[i]); den = mp.mpc(1)
            for j in range(n):
                if j != i: den *= (roots[i] - roots[j])
            delta = num / den; roots[i] -= delta; moved = max(moved, abs(delta))
        if moved < tol: break
    return roots


def eigenvalues(A):
    """eigenvalues of a square matrix: exact ℚ characteristic polynomial, then Durand–Kerner roots."""
    return poly_roots(char_poly(A))


def gradient(f, point, names, h=mp.mpf("1e-15")):
    """∇f at a point — finite central differences per named variable (f takes keyword args)."""
    g = []
    for i, nm in enumerate(names):
        pu = dict(zip(names, point)); pd = dict(zip(names, point))
        pu[nm] = R(point[i]) + h; pd[nm] = R(point[i]) - h
        g.append((f(**pu) - f(**pd)) / (2 * h))
    return g


def convolution(a, b):
    """discrete convolution (a * b)[k] = Σ a[i] b[k-i] — finite, exact when inputs are rational."""
    a = [Q(x) if float(x) == x and (isinstance(x, int) or (isinstance(x, float) and x.is_integer())) else R(x) for x in a]
    b = [Q(x) if float(x) == x and (isinstance(x, int) or (isinstance(x, float) and x.is_integer())) else R(x) for x in b]
    out = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b): out[i + j] = out[i + j] + ai * bj
    return out


def arc_length(f, a, b, N=2000):
    """arc length ∫_a^b √(1+f'(x)²) dx — finite quadrature with finite derivative."""
    a, b = R(a), R(b); h = (b - a) / N; s = R(0)
    for i in range(N):
        x = a + (i + mp.mpf("0.5")) * h
        d = F.derivative(f, x); s += mp.sqrt(1 + d * d)
    return s * h


def fixed_point(g, x0, it=500, tol=mp.mpf("1e-28")):
    """a fixed point of g (x = g(x)) by finite iteration from x0."""
    x = R(x0)
    for _ in range(it):
        nx = g(x)
        if abs(nx - x) < tol: return nx
        x = nx
    return x
