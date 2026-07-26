"""idm.integrate — the integration flagship: continuum integrals as certified finite readouts.

The workhorse is tanh–sinh (double-exponential, DE) quadrature: a single FINITE rule whose nodes cluster
so fast that it swallows endpoint singularities and, via companion transforms, semi-infinite and doubly
infinite ranges — with (near) exponential convergence. Every routine returns a value together with an
a-posteriori error estimate (the change between two DE levels) and an ACCEPT/HOLD verdict: the readout
either stabilizes below the requested tolerance, or it refuses. The DE nodes/weights are built from the
FINITE exponential (idm.functions.exp) — no continuum library call produces the answer.

    ∫_a^b (finite, incl. endpoint singularities)   → tanh–sinh
    ∫_a^∞ / ∫_{-∞}^a  (semi-infinite)               → exp–sinh
    ∫_{-∞}^∞ (doubly infinite)                       → sinh–sinh
"""
from . import functions as F
from .certified import Readout, CERTIFIED, HOLD
import mpmath as mp
mp.mp.dps = 40
R = mp.mpf
PI = F.pi()

# ---------------------------------------------------------------- the DE rules (finite sums) ----
# The abscissae/weights are INFRASTRUCTURE (sample locations of a finite rule): the value is the finite
# weighted sum Σ w·f(x) of finite integrand evaluations. Each sum starts at k=0 and walks both tails,
# stopping when the actual CONTRIBUTION w·f(x) underflows — so the finite node set adapts to the
# integrand (essential: a DE weight can grow while w·f decays). Node positions are the same finite
# numbers idm.functions.exp gives; mpmath's exponential is used for speed only.
_HALF = PI / 2

def _de_walk(term0, term, tiny):
    """Σ term(k), k from 0 outward in both directions, stopping each tail after several negligible terms."""
    total = term0
    for direction in (1, -1):
        k = direction; zeros = 0
        while True:
            val = term(k); total += val
            zeros = zeros + 1 if abs(val) < tiny else 0
            if zeros >= 4: break
            k += direction
            if abs(k) > 6000: break
    return total

def _quad_tanh_sinh(f, a, b, level):
    a, b = R(a), R(b); c = (b - a) / 2; d = (b + a) / 2; h = R(1) / 2 ** level
    tiny = R(10) ** (-mp.mp.dps - 3)
    def term(k):
        t = k * h; s = mp.sinh(t); x = mp.tanh(_HALF * s)
        w = (_HALF * mp.cosh(t)) / mp.cosh(_HALF * s) ** 2
        return w * f(d + c * x)
    return c * h * _de_walk(term(0), term, tiny / max(abs(c), R(1)))

def _quad_exp_sinh(f, a, level, sign=1):
    """∫_a^∞ (sign=+1) or ∫_{-∞}^a (sign=-1) — exp–sinh."""
    a = R(a); h = R(1) / 2 ** level; tiny = R(10) ** (-mp.mp.dps - 3)
    def term(k):
        t = k * h; s = mp.sinh(t); x = mp.exp(_HALF * s); w = _HALF * mp.cosh(t) * x
        return w * f(a + sign * x)
    return sign * h * _de_walk(term(0), term, tiny)

def _quad_sinh_sinh(f, level):
    h = R(1) / 2 ** level; tiny = R(10) ** (-mp.mp.dps - 3)
    def term(k):
        t = k * h; s = mp.sinh(t); x = mp.sinh(_HALF * s); w = _HALF * mp.cosh(t) * mp.cosh(_HALF * s)
        return w * f(x)
    return h * _de_walk(term(0), term, tiny)

# ---------------------------------------------------------------- the certified front door ----
def _INF(v):
    if isinstance(v, str):
        u = v.strip().lower()
        if u in ("inf", "+inf", "infinity", "oo", "+oo"): return "+"
        if u in ("-inf", "-infinity", "-oo"): return "-"
    return None

def integrate(f, a, b, eps=R("1e-12"), max_level=10):
    """∫_a^b f with automatic method (finite / semi-infinite / doubly infinite), DE quadrature, and an
    a-posteriori certificate. a,b may be numbers or 'inf'/'-inf'. Returns a Readout."""
    eps = R(str(eps)); ai, bi = _INF(a), _INF(b)
    if ai and bi:                                            # (-∞,∞)
        run = lambda L: _quad_sinh_sinh(f, L); how = "sinh–sinh DE"
    elif bi == "+":                                          # [a,∞)
        run = lambda L: _quad_exp_sinh(f, a, L, +1); how = "exp–sinh DE"
    elif ai == "-":                                          # (-∞,b]
        run = lambda L: _quad_exp_sinh(f, b, L, -1); how = "exp–sinh DE"
    else:                                                    # [a,b] finite (handles endpoint singularities)
        run = lambda L: _quad_tanh_sinh(f, a, b, L); how = "tanh–sinh DE"
    prev = run(3); level = 4
    while level <= max_level:
        cur = run(level); err = abs(cur - prev)
        if err <= eps:
            return Readout(cur, err, CERTIFIED, f"{how}, level {level}, |Δ between levels| ≤ ε")
        prev = cur; level += 1
    return Readout(cur, abs(cur - prev), HOLD,
                   f"{how} did not stabilize below ε by level {max_level} (est. error {mp.nstr(abs(cur-prev),3)})")

# ---------------------------------------------------------------- Gauss–Legendre (finite nodes) ----
_GL_CACHE = {}
def _gl_nodes(n):
    if n in _GL_CACHE:
        return _GL_CACHE[n]
    nodes = []
    def Pn(x):                                               # Legendre Pₙ and P'ₙ by finite recurrence
        p0, p1 = R(1), x
        for k in range(2, n + 1): p0, p1 = p1, ((2 * k - 1) * x * p1 - (k - 1) * p0) / k
        return p1, n * (x * p1 - p0) / (x * x - 1)
    for i in range(1, n + 1):
        x = mp.cos(PI * (i - R(1) / 4) / (n + R(1) / 2))     # initial guess
        for _ in range(100):
            p, dp = Pn(x); dx = -p / dp; x += dx
            if abs(dx) < R(10) ** (-mp.mp.dps): break
        _, dp = Pn(x); nodes.append((x, 2 / ((1 - x * x) * dp * dp)))
    _GL_CACHE[n] = nodes
    return nodes

def gauss_legendre(f, a, b, n=64):
    """classical n-point Gauss–Legendre on [a,b] — finite nodes (roots of Pₙ via Newton) and weights."""
    a, b = R(a), R(b); c = (b - a) / 2; d = (b + a) / 2
    return c * sum(w * f(d + c * x) for x, w in _gl_nodes(n))

# ---------------------------------------------------------------- residues / contour ----
def residue_sum(coeffs_num, coeffs_den):
    """2πi · Σ residues of (num/den) at the roots of den inside the upper half plane — for ∫_{-∞}^∞ of a
    rational function. Poles via idm.analysis.poly_roots; simple-pole residues num(p)/den'(p)."""
    from .analysis import poly_roots
    from .exact import poly_derivative, poly_eval
    from fractions import Fraction as Q
    dp = poly_derivative(coeffs_den)
    poles = poly_roots(coeffs_den)
    total = mp.mpc(0)
    for p in poles:
        if mp.im(p) > R(10) ** -20:                          # upper half plane
            num = sum(mp.mpf(str(float(coeffs_num[k]))) * p ** k for k in range(len(coeffs_num)))
            den = sum(mp.mpf(str(float(dp[k]))) * p ** k for k in range(len(dp)))
            total += num / den
    return 2 * PI * mp.mpc(0, 1) * total

# ---------------------------------------------------------------- multi-dimensional ----
def integrate_nd(f, bounds, n_per_axis=48):
    """∫ over a box ∏[aᵢ,bᵢ] by nested Gauss–Legendre. bounds = [[a1,b1],…,[ad,bd]]. Finite; for coupled
    high-dimensional integrands the retained-graph contraction (idm.rcp) is the scalable path."""
    d = len(bounds)
    def rec(dim, pt):
        if dim == d:
            return f(*pt)
        a, b = bounds[dim]
        return gauss_legendre(lambda x: rec(dim + 1, pt + [x]), a, b, n_per_axis)
    return rec(0, [])
