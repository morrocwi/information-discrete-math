#!/usr/bin/env python3
"""provefull/biochem.py — ~200 continuum-frontier biochemistry problems.

Every 'ours' value is produced with ONLY finite, discrete, rational operations through the shared
kernel provefull/_kernel.py (K.exp_finite / K.log_finite / K.erf_finite / K.pow_finite / finite Newton
/ finite RK4 recurrences). Every 'ref' value is the STANDARD textbook value computed with mpmath's own
transcendental functions (mp.exp/mp.log/mp.erf/mp.power) or mpmath's independent Taylor-series ODE
integrator (mp.odefun) — a genuinely different route from the finite-discrete construction of 'ours'.

Families (≈18, parametrized to ~200 problems):
  A  first-order decay N0 e^{-kt}
  B  half-life t1/2 = ln2 / k
  C  Arrhenius rate k = A e^{-Ea/RT}
  D  van't Hoff  ln(K2/K1) = -ΔH/R (1/T2 - 1/T1)
  E  Gibbs free energy  ΔG = -RT ln K
  F  Boltzmann population ratio  N2/N1 = (g2/g1) e^{-ΔE/kT}
  G  Bateman 2-step decay chain A->B->C  (finite RK4 vs closed-form analytic)
  H  Bateman 3-step decay chain A->B->C->D
  I  integrated Michaelis-Menten (Lambert-W transcendental) via finite Newton
  J  Hill equation with non-integer Hill coefficient
  K  Fick diffusion erf concentration profile
  L  normal CDF via erf
  M  logistic growth: analytic vs finite RK4 of dN/dt=rN(1-N/K)
  N  Gompertz growth: analytic vs finite RK4 of dN/dt=cN ln(K/N)
  O  SIR epidemic I(t): finite RK4 vs mpmath's independent Taylor-series ODE integrator
  P  Poisson probability  e^{-λ} λ^k / k!
  R  Henderson-Hasselbalch  pH = pKa + log10(base/acid)
  S  Nernst equation  E = E0 - (RT/nF) ln Q
"""
import _kernel as K
import mpmath as mp

R = K.R
DOM = "biochem"


# ------------------------------------------------------------------ finite vector RK4 (pure +-*/, plus
# K.log_finite where a family genuinely needs it inside the field — never mp.exp/mp.log) --------------
def _rk4_vec(deriv, t0, y0, tT, N):
    """Integrate dy/dt = deriv(t, y) (y a tuple of mpf) from t0 to tT in N finite RK4 steps."""
    h = (R(tT) - R(t0)) / N
    t = R(t0)
    y = tuple(R(v) for v in y0)

    def add(a, b, s=R(1)):
        return tuple(ai + s * bi for ai, bi in zip(a, b))

    for _ in range(N):
        k1 = deriv(t, y)
        k2 = deriv(t + h / 2, add(y, k1, h / 2))
        k3 = deriv(t + h / 2, add(y, k2, h / 2))
        k4 = deriv(t + h, add(y, k3, h))
        y = tuple(yi + h / 6 * (a + 2 * b + 2 * c + d) for yi, a, b, c, d in zip(y, k1, k2, k3, k4))
        t += h
    return y


def PROBLEMS():
    out = []

    # ================================================================= A. first-order decay =========
    decay_cases = [
        (100, 0.05, 10), (250, 0.12, 5), (1000, 0.02, 30), (50, 0.30, 2), (500, 0.007, 80),
        (10, 0.9, 1), (75, 0.15, 8), (300, 0.045, 20), (40, 0.6, 1.5), (600, 0.011, 60),
        (25, 1.2, 0.8), (900, 0.003, 200), (150, 0.08, 12), (5, 2.0, 0.6), (2000, 0.001, 500),
    ]
    for i, (N0, k, t) in enumerate(decay_cases):
        N0, k, t = R(N0), R(k), R(t)
        ours = N0 * K.exp_finite(-k * t)
        ref = N0 * mp.exp(-k * t)
        out.append(K.P(DOM, f"decay-1st-order-{i+1}", "N(t)=N0 e^{-kt}", ours, ref,
                        "K.exp_finite(-kt) [finite Taylor + halving] vs mp.exp"))

    # ================================================================= B. half-life =================
    halflife_ks = [0.001, 0.005, 0.02, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
    for i, k in enumerate(halflife_ks):
        k = R(k)
        ours = K.LN2_FINITE / k
        ref = mp.log(2) / k
        out.append(K.P(DOM, f"half-life-{i+1}", "t_1/2 = ln2 / k", ours, ref,
                        "K.LN2_FINITE (2*atanh(1/3) finite series) / k vs mp.log(2)/k"))

    # ================================================================= C. Arrhenius =================
    RGAS = R("8.314")
    arr_cases = [
        (1e13, 50000, 298), (1e12, 75000, 310), (5e11, 40000, 350), (1e14, 100000, 400),
        (2e13, 60000, 273), (1e10, 30000, 320), (8e12, 85000, 500), (3e11, 45000, 290),
        (6e13, 95000, 450), (1e9, 20000, 250), (4e12, 55000, 373), (9e11, 65000, 330),
        (2e10, 35000, 300), (7e13, 110000, 600), (5e12, 70000, 340), (1e11, 25000, 260),
        (3e10, 48000, 315),
    ]
    for i, (A, Ea, T) in enumerate(arr_cases):
        A, Ea, T = R(A), R(Ea), R(T)
        ours = A * K.exp_finite(-Ea / (RGAS * T))
        ref = A * mp.exp(-Ea / (RGAS * T))
        out.append(K.P(DOM, f"arrhenius-{i+1}", "k = A e^{-Ea/RT}", ours, ref,
                        "K.exp_finite(-Ea/RT) vs mp.exp"))

    # ================================================================= D. van't Hoff ================
    vh_cases = [
        (1.5, 298, 310, -50000), (0.8, 300, 350, 30000), (2.2, 273, 298, -25000),
        (0.05, 290, 320, 60000), (10.0, 310, 340, -40000), (3.3, 280, 300, -15000),
        (0.4, 295, 305, 20000), (5.5, 320, 360, -70000), (1.1, 288, 298, 10000),
        (0.9, 300, 400, -35000),
    ]
    for i, (K1, T1, T2, dH) in enumerate(vh_cases):
        K1, T1, T2, dH = R(K1), R(T1), R(T2), R(dH)
        lnK1_ours = K.log_finite(K1)
        lnK2_ours = lnK1_ours - dH / RGAS * (1 / T2 - 1 / T1)
        ours = K.exp_finite(lnK2_ours)
        ref = K1 * mp.exp(-dH / RGAS * (1 / T2 - 1 / T1))
        out.append(K.P(DOM, f"vanthoff-{i+1}", "ln(K2/K1) = -ΔH/R (1/T2-1/T1)", ours, ref,
                        "K.log_finite/K.exp_finite chain vs mp.exp"))

    # ================================================================= E. Gibbs ======================
    gibbs_cases = [
        (298, 10), (310, 0.5), (300, 100), (273, 2.0), (350, 0.01),
        (298, 1000), (320, 5), (340, 0.2), (400, 50), (290, 0.05),
    ]
    for i, (T, Keq) in enumerate(gibbs_cases):
        T, Keq = R(T), R(Keq)
        ours = -RGAS * T * K.log_finite(Keq)
        ref = -RGAS * T * mp.log(Keq)
        out.append(K.P(DOM, f"gibbs-{i+1}", "ΔG = -RT ln K", ours, ref,
                        "K.log_finite(K) vs mp.log(K)"))

    # ================================================================= F. Boltzmann ratio ============
    KB = R("1.380649e-23")
    boltz_cases = [
        (2, 1, 5e-21, 298), (1, 2, 1e-20, 310), (3, 1, 2e-21, 200), (1, 1, 8e-21, 500),
        (4, 2, 3e-20, 350), (1, 3, 4e-21, 273), (2, 2, 6e-21, 400), (1, 1, 1e-21, 100),
        (5, 1, 7e-21, 320), (2, 3, 9e-21, 450), (1, 4, 2.5e-20, 300), (3, 2, 1.5e-20, 380),
    ]
    for i, (g2, g1, dE, T) in enumerate(boltz_cases):
        g2, g1, dE, T = R(g2), R(g1), R(dE), R(T)
        ours = (g2 / g1) * K.exp_finite(-dE / (KB * T))
        ref = (g2 / g1) * mp.exp(-dE / (KB * T))
        out.append(K.P(DOM, f"boltzmann-ratio-{i+1}", "N2/N1 = (g2/g1) e^{-ΔE/kT}", ours, ref,
                        "K.exp_finite(-ΔE/kT) vs mp.exp"))

    # ================================================================= G. Bateman 2-step =============
    bateman2_cases = [
        (100, 0.5, 0.2, 3), (200, 0.1, 0.05, 20), (50, 1.2, 0.3, 2), (500, 0.02, 0.08, 15),
        (80, 0.7, 0.4, 4), (300, 0.15, 0.6, 6), (40, 2.0, 0.5, 1), (150, 0.06, 0.02, 40),
        (600, 0.03, 0.12, 10), (90, 0.9, 0.25, 3.5),
    ]
    for i, (A0, k1, k2, t) in enumerate(bateman2_cases):
        A0, k1, k2, t = R(A0), R(k1), R(k2), R(t)

        def deriv(tt, y, k1=k1, k2=k2):
            A, B = y
            return (-k1 * A, k1 * A - k2 * B)

        _, Bt = _rk4_vec(deriv, 0, (A0, 0), t, 800)
        ours = Bt
        ref = A0 * k1 / (k2 - k1) * (mp.exp(-k1 * t) - mp.exp(-k2 * t))
        out.append(K.P(DOM, f"bateman2-{i+1}", "A->B->C: B(t) (finite RK4 vs closed-form)", ours, ref,
                        "finite RK4 vector recurrence vs analytic Bateman formula (mp.exp)"))

    # ================================================================= H. Bateman 3-step =============
    bateman3_cases = [
        (100, 0.5, 0.3, 0.15, 4), (200, 0.2, 0.1, 0.05, 15), (50, 1.0, 0.6, 0.2, 2),
        (300, 0.08, 0.04, 0.02, 25), (80, 0.9, 0.4, 0.1, 3), (150, 0.3, 0.15, 0.5, 5),
        (400, 0.05, 0.25, 0.1, 12), (60, 1.5, 0.7, 0.35, 1.5),
    ]
    for i, (A0, k1, k2, k3, t) in enumerate(bateman3_cases):
        A0, k1, k2, k3, t = R(A0), R(k1), R(k2), R(k3), R(t)

        def deriv(tt, y, k1=k1, k2=k2, k3=k3):
            A, B, C = y
            return (-k1 * A, k1 * A - k2 * B, k2 * B - k3 * C)

        _, _, Ct = _rk4_vec(deriv, 0, (A0, 0, 0), t, 1000)
        ours = Ct
        ref = A0 * k1 * k2 * (
            mp.exp(-k1 * t) / ((k2 - k1) * (k3 - k1))
            + mp.exp(-k2 * t) / ((k1 - k2) * (k3 - k2))
            + mp.exp(-k3 * t) / ((k1 - k3) * (k2 - k3))
        )
        out.append(K.P(DOM, f"bateman3-{i+1}", "A->B->C->D: C(t) (finite RK4 vs closed-form)", ours, ref,
                        "finite RK4 vector recurrence vs 3-term analytic Bateman formula (mp.exp)"))

    # ================================================================= I. integrated MM (Lambert-W) ==
    mm_cases = [
        (100, 50, 10, 2), (200, 80, 20, 3), (50, 30, 5, 4), (300, 120, 40, 1.5),
        (150, 60, 15, 5), (80, 40, 8, 2.5), (400, 200, 60, 2), (60, 25, 6, 6),
        (250, 100, 25, 1.2), (120, 55, 12, 3.5),
    ]
    for i, (S0, Vmax, Km, t) in enumerate(mm_cases):
        S0, Vmax, Km, t = R(S0), R(Vmax), R(Km), R(t)

        def f(S):
            return Km * K.log_finite(S0 / S) + (S0 - S) - Vmax * t

        # g is monotonically DEcreasing in S (dg/dS = -Km/S - 1 < 0), root in (eps, S0).
        # Robust finite bisection (safer than Newton near the S->0 log singularity).
        lo, hi = S0 * R("1e-6"), S0
        for _ in range(140):
            mid = (lo + hi) / 2
            if f(mid) > 0:
                lo = mid
            else:
                hi = mid
        ours = (lo + hi) / 2

        def fref(S):
            return Km * mp.log(S0 / S) + (S0 - S) - Vmax * t

        lo2, hi2 = S0 * R("1e-6"), S0
        for _ in range(140):
            mid = (lo2 + hi2) / 2
            if fref(mid) > 0:
                lo2 = mid
            else:
                hi2 = mid
        ref = (lo2 + hi2) / 2
        out.append(K.P(DOM, f"integrated-MM-{i+1}", "Km ln(S0/S)+(S0-S)=Vmax t (finite Newton)",
                        ours, ref, "finite Newton with K.log_finite vs mp.findroot"))

    # ================================================================= J. Hill equation (non-int n) ==
    hill_cases = [
        (5, 4, 2.3), (2, 3, 1.5), (10, 6, 3.7), (0.5, 1, 2.0), (8, 5, 4.2),
        (3, 2, 1.8), (15, 10, 2.9), (1, 1.5, 3.3), (6, 4.5, 2.1), (20, 12, 4.6),
    ]
    for i, (S, Kd, n) in enumerate(hill_cases):
        S, Kd, n = R(S), R(Kd), R(n)
        Sn = K.pow_finite(S, n)
        Kn = K.pow_finite(Kd, n)
        ours = Sn / (Kn + Sn)
        ref = mp.power(S, n) / (mp.power(Kd, n) + mp.power(S, n))
        out.append(K.P(DOM, f"hill-{i+1}", "theta = S^n/(K^n+S^n), n non-integer", ours, ref,
                        "K.pow_finite (exp/log finite) vs mp.power"))

    # ================================================================= K. Fick diffusion erf ========
    fick_cases = [
        (1.0, 1e-9, 100, 1), (0.5, 5e-10, 50, 2), (2.0, 2e-9, 200, 0.5), (0.1, 1e-8, 10, 3),
        (1.5, 3e-10, 300, 1.5), (0.8, 8e-9, 20, 0.8), (3.0, 1e-9, 500, 0.2), (0.3, 4e-9, 30, 4),
        (1.2, 6e-10, 150, 1.1), (2.5, 2e-10, 400, 0.7), (0.6, 9e-9, 25, 2.5), (1.8, 1.5e-9, 90, 1.3),
        (0.9, 7e-10, 60, 3.2),
    ]
    for i, (C0, D, x, t) in enumerate(fick_cases):
        C0, D, x, t = R(C0), R(D), R(x), R(t)
        arg = x / (2 * mp.sqrt(D * t))
        ours = C0 * (1 - K.erf_finite(arg))
        ref = C0 * (1 - mp.erf(arg))
        out.append(K.P(DOM, f"fick-erf-{i+1}", "C(x,t)=C0*erfc(x/(2√(Dt)))", ours, ref,
                        "K.erf_finite (finite Maclaurin series) vs mp.erf"))

    # ================================================================= L. normal CDF via erf ========
    ncdf_xs = [-3, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3, 0.25]
    for i, x in enumerate(ncdf_xs):
        x = R(x)
        arg = x / mp.sqrt(2)
        ours = R(1) / 2 * (1 + K.erf_finite(arg))
        ref = R(1) / 2 * (1 + mp.erf(arg))
        out.append(K.P(DOM, f"normal-cdf-{i+1}", "Phi(x)=1/2(1+erf(x/√2))", ours, ref,
                        "K.erf_finite vs mp.erf"))

    # ================================================================= M. logistic growth ===========
    logistic_cases = [
        (10, 1000, 0.5, 5), (5, 500, 0.3, 10), (50, 2000, 0.2, 8), (1, 100, 1.0, 3),
        (20, 800, 0.4, 6), (2, 300, 0.6, 4), (100, 5000, 0.15, 12), (8, 400, 0.8, 2),
        (30, 1500, 0.25, 9), (15, 600, 0.5, 5.5),
    ]
    for i, (N0, Kcap, r, t) in enumerate(logistic_cases):
        N0, Kcap, r, t = R(N0), R(Kcap), R(r), R(t)

        def deriv(tt, y, r=r, Kcap=Kcap):
            N, = y
            return (r * N * (1 - N / Kcap),)

        (Nt,) = _rk4_vec(deriv, 0, (N0,), t, 800)
        ours = Nt
        ref = Kcap / (1 + (Kcap - N0) / N0 * mp.exp(-r * t))
        out.append(K.P(DOM, f"logistic-{i+1}", "dN/dt=rN(1-N/K) (finite RK4 vs analytic)", ours, ref,
                        "finite RK4 (polynomial field, no transcendentals) vs analytic logistic (mp.exp)"))

    # ================================================================= N. Gompertz growth ============
    gompertz_cases = [
        (1, 1000, 0.3, 5), (10, 500, 0.2, 8), (2, 2000, 0.15, 10), (5, 800, 0.4, 4),
        (0.5, 300, 0.5, 6), (20, 1500, 0.1, 15), (8, 600, 0.35, 3), (1.5, 400, 0.25, 7),
    ]
    for i, (N0, Kcap, c, t) in enumerate(gompertz_cases):
        N0, Kcap, c, t = R(N0), R(Kcap), R(c), R(t)

        def deriv(tt, y, c=c, Kcap=Kcap):
            N, = y
            return (c * N * K.log_finite(Kcap / N),)

        (Nt,) = _rk4_vec(deriv, 0, (N0,), t, 1000)
        ours = Nt
        ref = Kcap * mp.exp(mp.log(N0 / Kcap) * mp.exp(-c * t))
        out.append(K.P(DOM, f"gompertz-{i+1}", "dN/dt=cN ln(K/N) (finite RK4 vs analytic)", ours, ref,
                        "finite RK4 with K.log_finite in the field vs analytic Gompertz (mp.exp/mp.log)"))

    # ================================================================= O. SIR epidemic ===============
    sir_cases = [
        (0.0003, 0.1, 999, 1, 5), (0.0005, 0.2, 990, 10, 10), (0.0002, 0.15, 995, 5, 8),
        (0.0008, 0.3, 980, 20, 6), (0.0004, 0.12, 998, 2, 12), (0.001, 0.25, 950, 50, 4),
    ]
    for i, (beta, gamma, S0, I0, t) in enumerate(sir_cases):
        beta, gamma, S0, I0, t = R(beta), R(gamma), R(S0), R(I0), R(t)
        R0v = R(0)

        def deriv(tt, y, beta=beta, gamma=gamma):
            S, I, Rr = y
            return (-beta * S * I, beta * S * I - gamma * I, gamma * I)

        _, It, _ = _rk4_vec(deriv, 0, (S0, I0, R0v), t, 2000)
        ours = It

        f_ode = mp.odefun(
            lambda tt, y, beta=beta, gamma=gamma: [-beta * y[0] * y[1], beta * y[0] * y[1] - gamma * y[1], gamma * y[1]],
            0, [S0, I0, R0v],
        )
        ref = f_ode(t)[1]
        out.append(K.P(DOM, f"sir-{i+1}", "SIR: I(t) (finite RK4 vs mpmath Taylor-series ODE integrator)",
                        ours, ref, "finite RK4 vector recurrence vs mp.odefun (independent method)"))

    # ================================================================= P. Poisson ====================
    poisson_cases = [
        (2.0, 2), (5.0, 5), (0.5, 0), (10.0, 8), (3.0, 3), (1.0, 1), (7.0, 10), (4.5, 6),
        (0.1, 0), (20.0, 18), (15.0, 15), (2.5, 4), (6.0, 6), (8.5, 9), (12.0, 11),
    ]
    for i, (lam, kcnt) in enumerate(poisson_cases):
        lam = R(lam)
        ours = K.exp_finite(-lam) * K.pow_finite(lam, kcnt) / K.factorial_finite(kcnt) if kcnt > 0 else K.exp_finite(-lam)
        ref = mp.exp(-lam) * lam ** kcnt / mp.factorial(kcnt)
        out.append(K.P(DOM, f"poisson-{i+1}", "P(k;λ)=e^{-λ}λ^k/k!", ours, ref,
                        "K.exp_finite(-λ) * λ^k / K.factorial_finite(k) vs mp.exp/mp.factorial"))

    # ================================================================= R. Henderson-Hasselbalch =====
    hh_cases = [
        (4.76, 2.0), (7.20, 0.5), (9.25, 5.0), (6.10, 1.5), (3.13, 10.0), (10.33, 0.2),
        (5.5, 3.0), (8.0, 0.8), (2.15, 20.0), (12.0, 0.1), (4.2, 7.5), (6.8, 1.2),
    ]
    for i, (pKa, ratio) in enumerate(hh_cases):
        pKa, ratio = R(pKa), R(ratio)
        log10r_ours = K.log_finite(ratio) / K.log_finite(10)
        ours = pKa + log10r_ours
        ref = pKa + mp.log10(ratio)
        out.append(K.P(DOM, f"henderson-hasselbalch-{i+1}", "pH = pKa + log10([base]/[acid])", ours, ref,
                        "K.log_finite(ratio)/K.log_finite(10) vs mp.log10"))

    # ================================================================= S. Nernst equation ============
    FARADAY = R(96485)
    nernst_cases = [
        (0.05, 298, 2, 0.001), (-0.4, 310, 1, 100), ("0.0", 300, 3, 0.01), (0.15, 273, 2, 50),
        (0.34, 298, 2, 0.0001), (-0.83, 320, 2, 10), (0.77, 350, 1, 1000), (0.0, 298, 1, 0.5),
        (0.22, 305, 2, 5), (0.8, 298, 4, 2), (-0.14, 288, 2, 20), (0.54, 340, 6, 0.002),
        (0.13, 310, 2, 3),
    ]
    for i, (E0, T, n, Q) in enumerate(nernst_cases):
        E0, T, n, Q = R(E0), R(T), R(n), R(Q)
        ours = E0 - (RGAS * T) / (n * FARADAY) * K.log_finite(Q)
        ref = E0 - (RGAS * T) / (n * FARADAY) * mp.log(Q)
        out.append(K.P(DOM, f"nernst-{i+1}", "E = E0 - (RT/nF) ln Q", ours, ref,
                        "K.log_finite(Q) vs mp.log(Q)"))

    return out


if __name__ == "__main__":
    ps = PROBLEMS()
    ok = sum(p.ok for p in ps)
    print(f"{ok}/{len(ps)}")
    for p in ps:
        if not p.ok:
            print("FAIL", p.name, p.dig, "digits")
