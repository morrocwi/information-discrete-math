# Discrete Epsilon-Completion Programme

Status: **end-to-end finite-tape adapter constructed for the declared periodic Fourier setting; observable-to-continuum composition registered through `PROP-EPSC-19`**.

Rigorous computable omitted-tail certificates exist for a Leray-Hopf spacetime norm and for several conditional/a-posteriori terminal settings. `PROP-EPSC-15`, formerly the missing numerical bridge, is supplied by an exact-dyadic piecewise-linear comparison path built from recorded RK4 nodes. `PROP-EPSC-17` composes a certified retained-state reconstruction radius with an EPSC omitted-tail radius. The open problems are now separated: outer certificate tightness/scaling (`PROP-EPSC-16`), quantitative energy-jet inversion (`PROP-EPSC-18`), and noise-stable measurement-to-continuum propagation (`PROP-EPSC-19`).

## Repository roles

- **Information Discrete Mathematics:** algorithms, finite refinement, fail-closed gates, reusable certificate and composition code.
- **Toledo:** proposal/equation provenance and tier/status.
- **Readout-Problem-Navier-Stokes:** NS-specific analysis, energy observability, finite witnesses, reproduction and manuscripts.
- **Readout Genesis:** interpretation/application map only; no automatic promotion to root ontology.

## 1. General EPSC object

The certificate target must name a target space/readout `Y`, retained record `R_K`, and assumptions `A`:

\[
\|(I-P_K)x\|_Y\le\beta_{K,Y}(\mathcal R_K;\mathcal A),
\qquad
\beta_{K,Y}\to0.
\]

Nested agreement

\[
\delta_K=\|R_Kx_{K+1}-x_K\|
\]

is useful evidence but does not by itself bound what remains outside the represented state. The fail-closed rule is

\[
\delta_K+\beta_{K,Y}\le\varepsilon
\Longrightarrow
\mathrm{CERTIFIED}_\varepsilon(Y),
\]

and if a required tail, assumption, retained-state certificate or adapter is absent, the system returns `HOLD`.

## 2. Terminal finite-record no-go

For a finite Fourier cube `P_K`, terminal retained coefficients alone do not identify the omitted tail over the unrestricted divergence-free `L2` class. A divergence-free conjugate pair can be placed at

\[
q=(K+1,0,0)
\]

entirely outside the retained cube and scaled arbitrarily without changing `P_Ku`. Hence a useful universal terminal `beta_K` cannot be a function of retained terminal coefficients alone without additional admissible-class or dynamical information.

## 3. Unconditional spacetime Leray-Hopf certificate

For an unforced Leray-Hopf solution on the normalized `2*pi` periodic three-torus,

\[
\|(I-P_K)u(t)\|_2^2
\le\frac{1}{(K+1)^2}\|\nabla u(t)\|_2^2,
\]

and the energy inequality gives

\[
\boxed{
\|(I-P_K)u\|_{L^2(0,T;L^2_x)}
\le
\frac{\|u_0\|_2}{\sqrt{2\nu}(K+1)}.
}
\]

This `beta_K` is explicit and tends to zero without a global-smoothness assumption. A conservative forced analogue for `f in L2(0,T;H^{-1})` is

\[
\beta_{K,f}^{ST}
=
\frac1{K+1}
\sqrt{\frac{\|u_0\|_2^2}{\nu}
+\frac{\|f\|_{L^2_tH^{-1}}^2}{\nu^2}}.
\]

Lipschitz readouts inherit the corresponding state-space bound.

## 4. Conditional terminal Sobolev certificate

If a separate certificate supplies

\[
\||\nabla|^s u(T)\|_2\le M_s(T),\qquad s>0,
\]

then

\[
\boxed{
\|(I-P_K)u(T)\|_2\le\frac{M_s(T)}{(K+1)^s}.
}
\]

The spectral step is elementary; obtaining a globally valid pointwise `H^s` bound in 3-D is the difficult part.

## 5. Terminal energy-budget certificate

For the actual unforced Leray-Hopf projection,

\[
\boxed{
\|(I-P_K)u(T)\|_2^2
\le
\|u_0\|_2^2-\|P_Ku(T)\|_2^2
-2\nu\int_0^T\|\nabla P_Ku(t)\|_2^2dt.
}
\]

A fail-closed directional version accepts

\[
U_0\ge\|u_0\|_2,
\quad
L_K(T)\le\|P_Ku(T)\|_2,
\quad
\underline D_K\le\nu\int_0^T\|\nabla P_Ku\|_2^2dt,
\]

and returns

\[
\beta_K^{EB}=\sqrt{U_0^2-L_K(T)^2-2\underline D_K}.
\]

A materially negative radicand means the directional certificates are inconsistent and must return `HOLD`. The asymptotic floor of this particular budget is the energy-inequality defect; under independently justified energy equality that floor vanishes.

## 6. Residual-based finite-path-to-continuum adapter

To avoid silently identifying a Galerkin output with the continuum projection, let `v(t)` be a divergence-free comparison path and define

\[
r=\partial_t v+P[(v\cdot\nabla)v]-\nu\Delta v-Pf,
\]

\[
A_T=2\int_0^T\|\nabla v\|_\infty dt,
\qquad
B_T=\int_0^T\|r\|_{H^{-1}}^2dt.
\]

For a Leray-Hopf solution `u`, the standard relative-energy/Gronwall estimate gives

\[
\boxed{
\sup_{0\le t\le T}\|u(t)-v(t)\|_2^2
\le e^{A_T}\left(e_0^2+\frac{B_T}{\nu}\right).
}
\]

If `v(T)` is retained-cutoff supported, then

\[
\boxed{
\|(I-P_K)u(T)\|_2
\le e^{A_T/2}\sqrt{e_0^2+B_T/\nu}.
}
\]

The continuum implication is analytic (`Dr`). The project-specific numerical obligation is to supply certified `A_T` and `B_T` for the declared finite tape.

## 7. PROP-EPSC-15: exact continuous-time enclosure of an RK4 tape

For every stored binary64 Fourier coefficient, take its exact IEEE-754 dyadic rational value, apply the Fourier Leray projector in exact rational arithmetic, and call the resulting nodes `v_n`. Between consecutive nodes define

\[
v_h(t_n+\theta h)=(1-\theta)v_n+\theta v_{n+1},
\qquad0\le\theta\le1.
\]

This path is continuous, finite Fourier-supported and exactly divergence-free. Its coefficients are affine in normalized time, so the quadratic convection term and full residual are degree at most two on each cell. Consequently

\[
\|r_h\|_{H^{-1}}^2
\]

is degree at most four and its time integral can be evaluated exactly as a rational number. A coefficientwise Fourier `l1` majorant bounds the gradient integral, `exp(A_bar)` is enclosed by a rational Taylor/geometric-remainder bound, and reported square roots are rounded upward by integer arithmetic.

Thus

```text
stored binary64 RK4 node tape
    -> exact dyadic capture + exact Leray projection
    -> continuous piecewise-linear Fourier path v_h(t)
    -> rigorous A_bar_T and B_bar_T
    -> PROP-EPSC-13 relative-energy theorem (Dr)
    -> terminal continuum L2 / omitted-tail beta_K
```

The path's PDE residual is explicitly paid for in `B_bar`; the RK4 recurrence is not pretended to be the exact PDE flow.

The independent short Taylor-Green witness at `K=1`, `nu=0.01`, `dt=0.01`, `T=0.05` reports approximately

\[
\overline A_T=0.599550229412277,
\qquad
\overline B_T=9.736386925864618\times10^{-5},
\qquad
\beta_T\le0.1331648457569634.
\]

These are certificate values for the declared short comparison path, not a turbulence/DNS adequacy claim.

## 8. Energy observability: the inner-completeness side

The companion NS observability programme asks a different question: whether energy observations determine the state **inside** a fixed Fourier cutoff.

For cutoff `N`, the declared finite real dimension is

\[
d_N=2((2N+1)^3-1).
\]

The total-energy and shell-energy Lie jets obey

\[
\operatorname{rank}D\mathcal E_R\le\min(R+1,d_N-3),
\]

\[
\operatorname{rank}D\mathcal J_R
\le\min(m_N+(m_N-1)R,d_N-3).
\]

Exact modular certificates attain the translation ceiling at the earliest structurally admissible order in four recorded cases: `N=1` total energy, `N=1` shell energies, `N=2` total energy and `N=3` shell energies. This yields local finite-state completeness modulo translations at those cases. It does **not** yield a quantitative reconstruction radius. The all-resolution earliest-saturation assertion remains `PROP-NSOBS-07` OPEN.

## 9. PROP-EPSC-17: observable-to-continuum orthogonal composition

Suppose a certified finite inversion returns a retained state `x_hat_N` and quotient-state radius

\[
\inf_{g\in G}\|P_Nu(T)-g\widehat x_N\|_2\le\rho_N,
\]

where `G` is an isometric symmetry group preserving the cutoff. Suppose EPSC independently supplies

\[
\|(I-P_N)u(T)\|_2\le\beta_N.
\]

The retained and omitted Fourier errors are orthogonal, hence

\[
\boxed{
\inf_{g\in G}\|u(T)-g\widehat x_N\|_2
\le\sqrt{\rho_N^2+\beta_N^2}.
}
\]

For the NS energy-reader application `G=T^3` is spatial translation. This is the `PROP-EPSC-17` composition theorem. It is sharper than a generic `rho_N+beta_N` triangle bound.

A final fail-closed tolerance rule is therefore

\[
\sqrt{\rho_N^2+\beta_N^2}\le\varepsilon.
\]

If either directional certificate is missing, return `HOLD`.

## 10. Why observability rank is not rho_N

Full local quotient rank establishes local differential identifiability, but does not automatically supply a constructive inverse, branch control, a certified neighborhood, conditioning, noise robustness, or a numerical reconstruction radius. Therefore rank saturation must never be substituted for `rho_N`.

The new inner-side frontiers are:

- `PROP-EPSC-18` — construct a quantitative certified inverse from energy Lie jets to a retained-state quotient radius `rho_N`;
- `PROP-EPSC-19` — propagate certified measurement/differentiation uncertainty through that inverse and the final continuum composition.

See `docs/OBSERVABLE_TO_CONTINUUM_CERTIFICATE.md`.

## 11. Implementation

```text
idm/ns_retained.py                    finite Fourier-Galerkin evolution
idm/ns_epsilon.py                     nested defect + fail-closed epsilon gate
idm/ns_tail_certificate.py            spacetime / H^s / readout tail certificates
idm/ns_terminal_certificate.py        terminal energy-budget certificate
idm/ns_relative_energy_adapter.py     relative-energy + finite residual helpers
idm/ns_rk4_path_certificate.py        exact-dyadic piecewise-linear A/B enclosure
idm/ns_observable_to_continuum.py     observability bookkeeping + rho/beta composition
```

Focused tests include

```text
tests/test_ns_epsilon.py
tests/test_ns_tail_certificate.py
tests/test_ns_terminal_certificate.py
tests/test_ns_relative_energy_adapter.py
tests/test_ns_rk4_path_certificate.py
tests/test_ns_observable_to_continuum.py
```

## 12. Toledo lineage and current frontiers

The EPSC proposal family now runs through `PROP-EPSC-19`:

- `PROP-EPSC-01..09` — nested/refinement, spectral, spacetime and readout family;
- `PROP-EPSC-10..12` — terminal energy-budget family and broad adapter obligation;
- `PROP-EPSC-13` — residual-based Leray relative-energy adapter;
- `PROP-EPSC-14` — finite Fourier residual tape;
- `PROP-EPSC-15` — exact-dyadic piecewise-linear continuous-time RK4-tape enclosure;
- `PROP-EPSC-16` — **OPEN** high-cutoff tightness/scaling refinement;
- `PROP-EPSC-17` — observable-to-continuum orthogonal composition;
- `PROP-EPSC-18` — **OPEN** certified energy-jet inversion radius;
- `PROP-EPSC-19` — **OPEN** noise-stable measurement-to-continuum certificate.

The companion energy-observability proposal family is `PROP-NSOBS-01..08`; `PROP-NSOBS-07` is the explicit all-resolution saturation conjecture.

These are proposal/provenance identifiers, not automatically canonical verified Toledo theorem codes.

The open frontiers must remain distinct:

```text
PROP-NSOBS-07  all-resolution earliest-order energy-observability saturation
PROP-EPSC-16   scalable/tight outer path certification
PROP-EPSC-18   certified quantitative energy-jet inversion
PROP-EPSC-19   noise-stable measurement-to-continuum propagation
```

## Claim boundary

Supported at analytic (`Dr`) tier are the standard spectral/energy/relative-energy consequences under their stated assumptions and the orthogonal `rho/beta` composition theorem. Finite executable checks validate only the finite algebra and recorded instances they actually run.

Still open are all-resolution observability saturation, a certified quantitative/noise-stable energy-jet inverse, high-cutoff certificate tightness/scaling, unconditional pointwise global regularity in 3-D, physical/DNS adequacy of coarse cutoffs, and the global smoothness-versus-blow-up question itself.

`PROP-EPSC-04` is resolved for several declared reader/record classes, not universally for arbitrary terminal retained coefficients. `PROP-EPSC-15` supplies a concrete finite-tape bridge. The current research programme is therefore a set of separated certification frontiers rather than one undifferentiated finite-to-continuum gap.
