#!/usr/bin/env python3
"""provefull/cosmology.py — ~200 continuum-frontier COSMOLOGY problems, each computed with ONLY
finite, discrete, rational operations through provefull/_kernel.py (K.*), and checked against the
standard mpmath ('continuum') reference computed by a genuinely DIFFERENT route (adaptive quadrature,
closed-form hyperbolic/hypergeometric identities, mp.zeta/mp.gamma, ...).

Families (flat FLRW, E(z)=sqrt(Om(1+z)^3+OL), Om+OL=1 unless noted):
  A comoving distance         B luminosity distance      C angular-diameter distance
  D distance modulus          E lookback time (closed-form asinh route)
  F age of universe (closed-form asinh route)             G particle horizon (improper integral)
  H Friedmann H(z) (Newton-iterated finite sqrt vs mp.sqrt)   I critical density scaling
  J Bose–Einstein integrals ∫x^(n-1)/(e^x-1)=Γ(n)ζ(n)      K Fermi–Dirac integrals (1-2^(1-n))Γ(n)ζ(n)
  L Saha ionization S(T)=A T^1.5 exp(-E/kT)                M linear growth factor D(a) (finite integral)
  N growth rate f=dlnD/dlna (finite central difference)    O slow-roll e-folds ∫V/V' dφ
  P baryon-photon sound horizon r_s                        Q relic thermal integral Γ(s)

No mp.exp/log/sin/quad/zeta/gamma/pi/erf ever produces an 'ours' value — those appear only in 'ref'.
"""
import _kernel as K
import mpmath as mp

R = K.R

# ---------------------------------------------------------------------- finite-discrete primitives ----
def sqrt_finite(x):
    """sqrt via pure Newton–Raphson iteration (+,-,*,/ only) — NOT mp.sqrt. Argument is first reduced
    to mantissa in [1,4) by finite halving/quadrupling (so Newton always starts close, converging in a
    handful of steps regardless of how large/small x is — same reduction spirit as log_finite/exp_finite),
    then 22 Newton steps (vastly more than needed for quadratic convergence from a 2x-off seed at dps=40)."""
    x = R(x)
    if x == 0:
        return R(0)
    k = 0; y = x
    while y > 4:
        y /= 4; k += 1
    while y < 1:
        y *= 4; k -= 1
    g = R(1)
    for _ in range(22):
        g = (g + y / g) / 2
    scale = R(1)
    if k >= 0:
        for _ in range(k):
            scale *= 2
    else:
        for _ in range(-k):
            scale /= 2
    return g * scale

def ipow(x, n):
    """x**n for nonnegative integer n: finite repeated multiplication — no mp ** operator."""
    x = R(x); r = R(1)
    for _ in range(n):
        r *= x
    return r

LN10_FINITE = K.log_finite(10)
def log10_finite(x):
    return K.log_finite(x) / LN10_FINITE

def Efunc(z, Om, OL):
    """E(z) = sqrt(Om(1+z)^3 + OL) — finite route (ipow + sqrt_finite)."""
    a = 1 + R(z)
    return sqrt_finite(Om * ipow(a, 3) + OL)

def Efunc_ref(z, Om, OL):
    z = R(z)
    return mp.sqrt(Om * (1 + z) ** 3 + OL)

def Efunc_a(a, Om, OL, Or=R(0)):
    """E(a) with matter+radiation+Lambda, a in (0,1] — finite route."""
    a = R(a)
    return sqrt_finite(Om / ipow(a, 3) + Or / ipow(a, 4) + OL)

def Efunc_a_ref(a, Om, OL, Or=0):
    a = R(a)
    return mp.sqrt(Om / a ** 3 + Or / a ** 4 + OL)

C_KMS = R("299792.458")   # speed of light, km/s (a physical constant, not a continuum computation)


def PROBLEMS():
    out = []

    # ===================================================== A. comoving distance D_C(z) (25) =========
    Om_list = [R("0.20"), R("0.30"), R("0.35"), R("0.40"), R("0.50")]
    z_list = [R("0.5"), R(1), R("1.5"), R(2), R(3)]
    for Om in Om_list:
        OL = 1 - Om
        for z in z_list:
            ours = K.quad_finite(lambda zp, Om=Om, OL=OL: 1 / Efunc(zp, Om, OL), 0, z, N=140)
            ref = mp.quad(lambda zp, Om=Om, OL=OL: 1 / Efunc_ref(zp, Om, OL), [0, z])
            out.append(K.P("cosmology", f"D_C(z={z},Om={Om})",
                            "D_C(z) = ∫0^z dz'/E(z'), E=sqrt(Om(1+z')^3+OL)",
                            ours, ref, "K.quad_finite (Simpson N=140) of finite sqrt_finite E(z)"))

    # ===================================================== B. luminosity distance d_L=(1+z)D_C (15) ==
    Om_list3 = [R("0.25"), R("0.30"), R("0.40")]
    for Om in Om_list3:
        OL = 1 - Om
        for z in z_list:
            dc = K.quad_finite(lambda zp, Om=Om, OL=OL: 1 / Efunc(zp, Om, OL), 0, z, N=140)
            ours = (1 + z) * dc
            ref = (1 + z) * mp.quad(lambda zp, Om=Om, OL=OL: 1 / Efunc_ref(zp, Om, OL), [0, z])
            out.append(K.P("cosmology", f"d_L(z={z},Om={Om})",
                            "d_L(z) = (1+z)·D_C(z)",
                            ours, ref, "finite D_C times (1+z)"))

    # ===================================================== C. angular-diameter distance d_A=D_C/(1+z) 15
    for Om in Om_list3:
        OL = 1 - Om
        for z in z_list:
            dc = K.quad_finite(lambda zp, Om=Om, OL=OL: 1 / Efunc(zp, Om, OL), 0, z, N=140)
            ours = dc / (1 + z)
            ref = mp.quad(lambda zp, Om=Om, OL=OL: 1 / Efunc_ref(zp, Om, OL), [0, z]) / (1 + z)
            out.append(K.P("cosmology", f"d_A(z={z},Om={Om})",
                            "d_A(z) = D_C(z)/(1+z)",
                            ours, ref, "finite D_C divided by (1+z)"))

    # ===================================================== D. distance modulus mu = 5log10(dL)+25 (15)
    H0 = R(70)
    DH = C_KMS / H0   # Hubble distance in Mpc
    for Om in Om_list3:
        OL = 1 - Om
        for z in z_list:
            dc = K.quad_finite(lambda zp, Om=Om, OL=OL: 1 / Efunc(zp, Om, OL), 0, z, N=140)
            dl_mpc = (1 + z) * dc * DH
            ours = 5 * log10_finite(dl_mpc) + 25
            dc_ref = mp.quad(lambda zp, Om=Om, OL=OL: 1 / Efunc_ref(zp, Om, OL), [0, z])
            dl_mpc_ref = (1 + z) * dc_ref * (float(C_KMS) / float(H0))
            ref = 5 * mp.log10(dl_mpc_ref) + 25
            out.append(K.P("cosmology", f"mu(z={z},Om={Om})",
                            "distance modulus mu = 5·log10(d_L[Mpc]) + 25",
                            ours, ref, "finite D_C -> d_L, K.log_finite/ln10 for log10"))

    # ===================================================== E. lookback time (closed-form asinh) (15) =
    for Om in Om_list3:
        OL = 1 - Om
        for z in z_list:
            # finite route: direct integral t_L*H0 = int_0^z dz'/((1+z')E(z'))
            ours = K.quad_finite(lambda zp, Om=Om, OL=OL: 1 / ((1 + zp) * Efunc(zp, Om, OL)), 0, z, N=140)
            # reference route: CLOSED FORM t_L*H0 = (2/3/sqrt(OL))·[asinh(sqrt(OL/Om)) - asinh(sqrt(OL/Om)/(1+z)^1.5)]
            s = mp.sqrt(OL / Om)
            ref = (R(2) / 3 / mp.sqrt(OL)) * (mp.asinh(s) - mp.asinh(s / (1 + z) ** R("1.5")))
            out.append(K.P("cosmology", f"t_L(z={z},Om={Om})",
                            "lookback time·H0 = ∫0^z dz'/((1+z')E(z'))  [closed form via asinh]",
                            ours, ref, "K.quad_finite vs closed-form asinh identity"))

    # ===================================================== F. age of universe (closed-form asinh) (10)
    # a=t^2 removes the sqrt(a)-type endpoint singularity at a=0: da/sqrt(Om/a+OL a^2) = 2t^2 dt/sqrt(Om+OL t^6)
    Om_age = [R(x) / 100 for x in [10, 20, 30, 35, 40, 50, 60, 70, 80, 90]]
    for Om in Om_age:
        OL = 1 - Om
        ours = 2 * K.quad_finite(lambda t, Om=Om, OL=OL: t * t / sqrt_finite(Om + OL * ipow(t, 6)), 0, 1, N=120)
        s = mp.sqrt(OL / Om)
        ref = (R(2) / 3 / mp.sqrt(OL)) * mp.asinh(s)
        out.append(K.P("cosmology", f"t0*H0(Om={Om})",
                        "age·H0 = ∫0^1 da/sqrt(Om/a+OL·a^2)  [closed form: 2/(3√OL)·asinh(√(OL/Om))]",
                        ours, ref, "K.quad_finite of the smooth t=sqrt(a) reparametrization vs closed-form asinh"))

    # ===================================================== G. particle horizon (10) ====================
    # a=1/(1+z), then t=sqrt(a): D_horizon = int_0^inf dz/E(z) = int_0^1 2 dt/sqrt(Om+OL t^6)  (smooth, proper)
    for Om in Om_age:
        OL = 1 - Om
        ours = 2 * K.quad_finite(lambda t, Om=Om, OL=OL: 1 / sqrt_finite(Om + OL * ipow(t, 6)), 0, 1, N=120)
        ref = mp.quad(lambda zp, Om=Om, OL=OL: 1 / Efunc_ref(zp, Om, OL), [0, mp.inf])
        out.append(K.P("cosmology", f"D_horizon(Om={Om})",
                        "comoving particle horizon·H0/c = ∫0^∞ dz/E(z) = ∫0^1 2dt/sqrt(Om+OL t^6)",
                        ours, ref, "K.quad_finite of the smooth t=sqrt(1/(1+z)) reparametrization vs mp.quad([0,inf])"))

    # ===================================================== H. Friedmann H(z) (Newton-sqrt route) (10) =
    Om_h = [R("0.20"), R("0.30"), R("0.40"), R("0.50"), R("0.60")]
    z_h = [R(0), R(2)]
    for Om in Om_h:
        OL = 1 - Om
        for z in z_h:
            ours = H0 * Efunc(z, Om, OL)
            ref = H0 * Efunc_ref(z, Om, OL)
            out.append(K.P("cosmology", f"H(z={z},Om={Om})",
                            "H(z) = H0·sqrt(Om(1+z)^3+OL)",
                            ours, ref, "H0·sqrt_finite(Newton, 60 iters) vs H0·mp.sqrt"))

    # ===================================================== I. critical density rho_c(z) scaling (10) =
    RHOC0 = R("9.47e-27")  # kg/m^3 (H0=70 canonical), a fixed physical constant
    for Om in Om_h:
        OL = 1 - Om
        for z in z_h:
            e = Efunc(z, Om, OL)
            ours = RHOC0 * e * e
            eref = Efunc_ref(z, Om, OL)
            ref = RHOC0 * eref * eref
            out.append(K.P("cosmology", f"rho_c(z={z},Om={Om})",
                            "rho_c(z) = rho_c0 · E(z)^2",
                            ours, ref, "finite sqrt_finite E(z) squared vs mp.sqrt E(z) squared"))

    # ===================================================== J. Bose-Einstein: ∫x^(n-1)/(e^x-1)=Γ(n)ζ(n)
    for n in range(2, 9):  # n=2..8  (7 problems)
        def _bose(x, n=n):
            if x == 0:
                return R(1) if n == 2 else R(0)   # true limit x^(n-1)/(e^x-1) -> x^(n-2) as x->0
            return ipow(x, n - 1) / K.expm1_finite(x)
        ours = K.quad_improper(_bose, R(40), N=900)
        ref = mp.gamma(n) * mp.zeta(n)
        out.append(K.P("cosmology", f"BoseEinstein n={n}",
                        "∫0^∞ x^(n-1)/(e^x-1) dx = Γ(n)ζ(n)  (photon/boson number & energy density integrals)",
                        ours, ref, "K.quad_improper + K.expm1_finite vs mp.gamma·mp.zeta"))

    # ===================================================== K. Fermi-Dirac: (1-2^(1-n))Γ(n)ζ(n)  (7) ===
    for n in range(2, 9):
        ours = K.quad_improper(lambda x, n=n: (ipow(x, n - 1) / (K.exp_finite(x) + 1)) if x >= 0 else R(0),
                                R(40), N=900)
        ref = (1 - mp.mpf(2) ** (1 - n)) * mp.gamma(n) * mp.zeta(n)
        out.append(K.P("cosmology", f"FermiDirac n={n}",
                        "∫0^∞ x^(n-1)/(e^x+1) dx = (1-2^(1-n))Γ(n)ζ(n)  (neutrino number & energy density)",
                        ours, ref, "K.quad_improper + K.exp_finite vs (1-2^(1-n))·mp.gamma·mp.zeta"))

    # ===================================================== L. Saha ionization S(T) (15) ================
    EION = R("13.6")            # eV, hydrogen ionization energy
    KB = R("8.617333e-5")       # eV/K
    A_SAHA = R("2.4e21")        # cm^-3 K^-1.5, lumped (2 pi m_e k / h^2)^1.5 constant
    T_list = [R(x) for x in [3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000,
                              12000, 14000, 16000, 18000, 20000, 25000, 30000]]
    for T in T_list:
        t15 = T * sqrt_finite(T)                 # T^1.5 via finite sqrt route
        ours = A_SAHA * t15 * K.exp_finite(-EION / (KB * T))
        ref = A_SAHA * (T ** R("1.5")) * mp.exp(-float(EION) / (float(KB) * float(T)))
        out.append(K.P("cosmology", f"Saha S(T={T}K)",
                        "S(T) = A·T^1.5·exp(-E_ion/kT)  (Saha ionization equilibrium factor)",
                        ours, ref, "T·sqrt_finite(T) + K.exp_finite vs mp T**1.5 · mp.exp"))

    # ===================================================== M. linear growth factor D(a) (15) ===========
    # exact (for flat LCDM) integral form: D(a) = (5 Om/2)· E(a) · ∫0^a da'/(a' E(a'))^3
    Om_g = [R("0.20"), R("0.25"), R("0.30"), R("0.35"), R("0.45")]
    a_list = [R("0.3"), R("0.6"), R("1.0")]
    def D_finite(a, Om, OL, N=140):
        eps = R("1e-8")
        integ = K.quad_finite(lambda ap, Om=Om, OL=OL: 1 / ipow(ap * Efunc_a(ap, Om, OL), 3), eps, a, N=N)
        return (R(5) * Om / 2) * Efunc_a(a, Om, OL) * integ
    def D_ref(a, Om, OL):
        eps = 1e-8
        integ = mp.quad(lambda ap: 1 / (ap * Efunc_a_ref(ap, Om, OL)) ** 3, [eps, float(a)])
        return (5 * Om / 2) * Efunc_a_ref(a, Om, OL) * integ
    for Om in Om_g:
        OL = 1 - Om
        for a in a_list:
            ours = D_finite(a, Om, OL)
            ref = D_ref(a, Om, OL)
            out.append(K.P("cosmology", f"D_growth(a={a},Om={Om})",
                            "D(a) = (5Om/2)·E(a)·∫0^a da'/(a'E(a'))^3  (linear growth factor)",
                            ours, ref, "K.quad_finite vs mp.quad, both feeding the same closed integral form"))

    # ===================================================== N. growth rate f=dlnD/dlna (10) =============
    Om_f = [R("0.20"), R("0.30"), R("0.40"), R("0.50"), R("0.60")]
    a_f = [R("0.5"), R("1.0")]
    for Om in Om_f:
        OL = 1 - Om
        for a in a_f:
            h = R("1e-4")
            Dp = D_finite(a + h, Om, OL, N=400)
            Dm = D_finite(a - h, Om, OL, N=400)
            # finite central difference of ln D wrt ln a using K.log_finite
            dlnD = K.log_finite(Dp) - K.log_finite(Dm)
            dlna = K.log_finite(a + h) - K.log_finite(a - h)
            ours = dlnD / dlna
            # reference: D(a) via mp.quad (adaptive) instead of K.quad_finite (Simpson) — a genuinely
            # different quadrature route for D(a) itself; central difference formula may coincide.
            Dp_r = D_ref(a + h, Om, OL); Dm_r = D_ref(a - h, Om, OL)
            ref = (mp.log(Dp_r) - mp.log(Dm_r)) / (2 * h) * a
            out.append(K.P("cosmology", f"f_growth(a={a},Om={Om})",
                            "f(a) = dlnD/dlna  (linear growth rate)",
                            ours, ref, "central diff of K.log_finite(D_finite via Simpson) vs mp.log(D_ref via mp.quad)"))

    # ===================================================== O. slow-roll e-folds N=∫V/V' dφ (10) =======
    lam_list = [R("0.05"), R("0.10"), R("0.15"), R("0.20"), R("0.25")]
    phi_list = [R("8.0"), R("12.0")]
    for lam in lam_list:
        for phi_i in phi_list:
            phi_end = R("0.5")
            def VoverVp(phi, lam=lam):
                V = phi * phi + lam * ipow(phi, 4)
                Vp = 2 * phi + 4 * lam * ipow(phi, 3)
                return V / Vp
            ours = K.quad_finite(VoverVp, phi_end, phi_i, N=140)
            def VoverVp_ref(phi, lam=lam):
                V = phi * phi + float(lam) * phi ** 4
                Vp = 2 * phi + 4 * float(lam) * phi ** 3
                return V / Vp
            ref = mp.quad(VoverVp_ref, [float(phi_end), float(phi_i)])
            out.append(K.P("cosmology", f"Nefolds(lam={lam},phi_i={phi_i})",
                            "N_e = ∫_phiend^phi_i (V/V') dphi, V=phi^2+lam·phi^4  (slow-roll e-folds)",
                            ours, ref, "K.quad_finite (Simpson N=140) vs mp.quad adaptive"))

    # ===================================================== P. baryon-photon sound horizon r_s (15) =====
    Ob_list = [R("0.02"), R("0.03"), R("0.04"), R("0.05"), R("0.06")]
    Om_p = [R("0.25"), R("0.30"), R("0.35")]
    Or_fixed = R("9.0e-5")
    a_rec = R(1) / R(1101)
    for Ob in Ob_list:
        for Om in Om_p:
            OL = 1 - Om - Or_fixed
            def cs_over_a2H(a, Ob=Ob, Om=Om, OL=OL):
                Rb = (R(3) * Ob / (R(4) * R("2.47e-5"))) * a         # standard R(a)=3rho_b/4rho_gamma
                cs = 1 / sqrt_finite(3 * (1 + Rb))
                return cs / (a * a * Efunc_a(a, Om, OL, Or_fixed))
            eps = R("1e-8")
            ours = K.quad_finite(cs_over_a2H, eps, a_rec, N=120)
            def cs_over_a2H_ref(a, Ob=Ob, Om=Om, OL=OL):
                Rb = (3 * float(Ob) / (4 * 2.47e-5)) * a
                cs = 1 / mp.sqrt(3 * (1 + Rb))
                return cs / (a * a * Efunc_a_ref(a, Om, OL, Or_fixed))
            ref = mp.quad(cs_over_a2H_ref, [float(eps), float(a_rec)])
            out.append(K.P("cosmology", f"r_s(Ob={Ob},Om={Om})",
                            "r_s = ∫0^a_rec c_s(a)/(a^2 H(a)/c) da  (baryon-photon sound horizon)",
                            ours, ref, "K.quad_finite (finite sqrt_finite c_s) vs mp.quad (mp.sqrt c_s)"))

    # ===================================================== Q. relic thermal integral Γ(s) (6) ==========
    s_list = [R("1.5"), R(2), R("2.5"), R(3), R("3.5"), R(4)]
    for s in s_list:
        ours = K.gamma_finite(s)
        ref = mp.gamma(s)
        out.append(K.P("cosmology", f"Gamma(s={s}) relic",
                        "Γ(s) = ∫0^∞ x^(s-1) e^-x dx  (thermal-averaged relic freeze-out integral)",
                        ours, ref, "K.gamma_finite (finite quadrature substitution) vs mp.gamma"))

    return out


if __name__ == "__main__":
    ps = PROBLEMS()
    ok = sum(p.ok for p in ps)
    print(f"{ok}/{len(ps)}")
    for p in ps:
        if not p.ok:
            print("FAIL", p.name, p.dig, "d")
