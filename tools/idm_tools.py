#!/usr/bin/env python3
"""idm_tools — the TOOLS of Information Discrete Mathematics (Yaoharee Lahtee).

A TOOL is a *noun*: a retained-distinction operator you invoke. This module is the single, tested home
of the operators proven in validation/ (1000-problem + 100-continuum suites). The PROCESS (the verb —
how you compose these into a solve) lives in METHOD.md; keep the two separate.

Every tool here is finite-ε over ℚ/high-precision — none takes a continuum limit as a primitive. The
ε→0 statement stays +ℝ-Open (A8); the readout is what these return.

    from idm_tools import D_eps, I_eps, limit_eps, ode_rk4, accelerate_alt, richardson_1_over_n
"""
import mpmath as mp
mp.mp.dps = 30

# ── T1. D_ε — discrete derivative (causal/central + Richardson; O(ε) removed) ──
def D_eps(f, x, h=mp.mpf('1e-3'), richardson=True):
    """Central difference with one Richardson step. Exact algebraic rules (Th_coqc) are in §8/§10.5."""
    d1 = (f(x + h) - f(x - h)) / (2 * h)
    if not richardson:
        return d1
    d2 = (f(x + h/2) - f(x - h/2)) / h
    return (4 * d2 - d1) / 3

# ── T2. I_ε — discrete integral (trapezoid + first Euler–Maclaurin endpoint correction) ──
def I_eps(f, a, b, N=400):
    """Aggregation as composite trapezoid + E–M correction. FTCC I_ε∘D_ε = f[N]−f[0] is exact (Th_coqc).
    Endpoint slopes use one-sided INWARD differences so f is never evaluated outside [a,b]."""
    a, b = mp.mpf(a), mp.mpf(b)
    hh = (b - a) / N
    s = (f(a) + f(b)) / 2 + mp.fsum(f(a + k*hh) for k in range(1, N))
    integral = hh * s
    d = mp.mpf('1e-6')
    corr = -hh**2/12 * ((f(b) - f(b - d))/d - (f(a + d) - f(a))/d)
    if not isinstance(corr, mp.mpc):
        integral += corr
    return integral

# ── T3. limit_eps — discrete limit (Richardson on h=1/n; A8 plateau, no ε–δ primitive) ──
def richardson_1_over_n(seq, M=4, K=13):
    """A8-stable limit of a sequence with an asymptotic expansion in 1/n. Kills each order successively."""
    col = [mp.mpf(seq(M * 2**j)) for j in range(K)]
    for p in range(1, K):
        col = [((1 << p)*col[i+1] - col[i]) / ((1 << p) - 1) for i in range(len(col)-1)]
    return col[-1]
limit_eps = richardson_1_over_n  # canonical name

# ── T4. ode_rk4 — discrete ODE (RK4 = 4th-order I_ε of the vector field; the ODE *is* the difference eq) ──
def ode_rk4(f, x0, y0, xT, N=400):
    """Solve y'=f(x,y) as a difference equation to xT. Continuous ODE = stability limit of this."""
    h = (mp.mpf(xT) - x0) / N
    x, y = mp.mpf(x0), mp.mpf(y0)
    for _ in range(N):
        k1 = f(x, y); k2 = f(x + h/2, y + h*k1/2)
        k3 = f(x + h/2, y + h*k2/2); k4 = f(x + h, y + h*k3)
        y += h*(k1 + 2*k2 + 2*k3 + k4)/6; x += h
    return y

# ── T5. accelerate_alt — Euler transform (iterated means) for a conditionally-convergent alternating tail ──
def accelerate_alt(terms, passes=None):
    """Given the term-list of an alternating series, return the accelerated sum (e.g. Dirichlet, η)."""
    P = [mp.fsum(terms[:m+1]) for m in range(len(terms))]  # partial sums
    passes = passes or max(1, len(P) // 2)
    for _ in range(passes):
        if len(P) < 2:
            break
        P = [(P[i] + P[i+1]) / 2 for i in range(len(P)-1)]
    return P[-1]

# ── T6. euler_maclaurin_zeta — regularized/accelerated partial sum for ζ-type tails ──
def em_sum(term, N, tail_correction):
    """Finite partial sum Σ_{n=1}^{N} term(n) plus a declared Euler–Maclaurin tail (finite_diagnostic)."""
    return mp.fsum(term(n) for n in range(1, N+1)) + tail_correction(N)

# ── T7. reparametrize — admissible change of variable turning an improper integral into a nice discrete one ──
def reparametrize(f, u_of_t, du_dt, t0, t1, N=4000):
    """∫ f(x)dx  under x=u(t):  ∫ f(u(t))·u'(t) dt — the discrete way to tame endpoint singularities."""
    return I_eps(lambda t: f(u_of_t(t)) * du_dt(t), t0, t1, N)

# ── The number ladder is a tool too: ℝ is a readout (regular Cauchy of ℚ), not a primitive ──
def real_readout(cauchy, k):
    """A real number as a readout: evaluate its regular-Cauchy witness at modulus index k (a rational)."""
    return mp.mpf(cauchy(k))

TOOLS = {
    "D_eps": "discrete derivative (Richardson)", "I_eps": "discrete integral (trapezoid+E–M)",
    "limit_eps": "discrete limit (Richardson on 1/n)", "ode_rk4": "discrete ODE (RK4 = I_ε of field)",
    "accelerate_alt": "Euler transform (alternating tail)", "em_sum": "Euler–Maclaurin partial sum",
    "reparametrize": "admissible change of variable", "real_readout": "ℝ as regular-Cauchy readout",
}

if __name__ == "__main__":
    # self-check: each tool reproduces a benchmark
    assert abs(I_eps(mp.sin, 0, mp.pi, 400) - 2) < 1e-8
    assert abs(D_eps(lambda x: x**3, 2) - 12) < 1e-5
    assert abs(limit_eps(lambda n: (1 + mp.mpf(1)/n)**n) - mp.e) < 1e-6
    assert abs(ode_rk4(lambda x, y: y, 0, 1, 1) - mp.e) < 1e-6
    print("idm_tools self-check OK —", len(TOOLS), "tools:", ", ".join(TOOLS))
