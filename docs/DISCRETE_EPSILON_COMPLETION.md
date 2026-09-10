# Discrete Epsilon-Completion Programme

Status: **partially closed by target/readout refinement**. Rigorous computable omitted-tail certificates exist for a Leray-Hopf spacetime norm and for several conditional/a-posteriori terminal settings. The current end-to-end finite-RK4-to-continuum bridge is isolated as one explicit validated-numerics obligation: `PROP-EPSC-15`.

## Repository roles

- **Information Discrete Mathematics:** algorithm, finite refinement, fail-closed gates, reusable certificate code and finite residual machinery.
- **Toledo:** proposal/equation provenance and tier/status.
- **Readout-Problem-Navier-Stokes:** NS-specific analytic derivations, finite witnesses, reproduction, standalone EPSC manuscript and claim boundary.
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

and if the required `beta`, target assumptions, or adapter certificate is missing, return `HOLD`.

## 2. Terminal finite-record no-go

For a finite Fourier cube `P_K`, terminal retained coefficients alone do not identify the omitted tail over the unrestricted divergence-free `L2` class. Put a divergence-free conjugate pair at

\[
q=(K+1,0,0),
\]

entirely outside the retained cube. Its amplitude may be scaled arbitrarily while `P_Ku` is unchanged. A useful universal terminal `beta_K` therefore cannot be a function of retained terminal coefficients alone without additional admissible-class or dynamical information.

## 3. Unconditional spacetime Leray-Hopf certificate

For an unforced Leray-Hopf solution on the `2*pi` periodic three-torus,

\[
\|(I-P_K)u(t)\|_2^2
\le \frac{1}{(K+1)^2}\|\nabla u(t)\|_2^2,
\]

and the energy inequality gives

\[
\boxed{
\|(I-P_K)u\|_{L^2(0,T;L^2_x)}
\le
\frac{\|u_0\|_2}{\sqrt{2\nu}(K+1)}
}.
\]

This `beta_K` is explicit, computable and tends to zero without a global-smoothness assumption. For `f in L2(0,T;H^{-1})`, a conservative forced analogue is

\[
\boxed{
\beta_{K,f}^{ST}
=
\frac1{K+1}
\sqrt{\frac{\|u_0\|_2^2}{\nu}
+\frac{\|f\|_{L^2_tH^{-1}}^2}{\nu^2}}
}.
\]

A Lipschitz readout `Q` inherits the certified error:

\[
\|Q(u)-Q(P_Ku)\|\le L_Q\beta_K.
\]

For the time-average `ubar=(1/T) int_0^T u dt`, the tail is at most `beta_K/sqrt(T)`.

## 4. Conditional terminal Sobolev certificate

If a separate certificate supplies

\[
\||\nabla|^s u(T)\|_2\le M_s(T),
\qquad s>0,
\]

then

\[
\boxed{
\|(I-P_K)u(T)\|_2
\le
\frac{M_s(T)}{(K+1)^s}
}.
\]

The Fourier-tail step is elementary; obtaining a globally valid pointwise `H^s` bound in 3-D is the difficult part.

## 5. Terminal energy-budget certificate

The terminal no-go concerns low-mode coefficients alone. Navier-Stokes supplies a richer retained record: retained terminal energy plus accumulated retained viscous dissipation. For the **actual** unforced Leray-Hopf projection,

\[
\boxed{
\|(I-P_K)u(T)\|_2^2
\le
\|u_0\|_2^2
-\|P_Ku(T)\|_2^2
-2\nu\int_0^T\|\nabla P_Ku(t)\|_2^2dt
}.
\]

A fail-closed directional-bound version uses

\[
U_0\ge\|u_0\|_2,
\qquad
L_K(T)\le\|P_Ku(T)\|_2,
\qquad
\underline D_K\le\nu\int_0^T\|\nabla P_Ku\|_2^2dt,
\]

and returns

\[
\boxed{
\beta_K^{EB}
=
\sqrt{U_0^2-L_K(T)^2-2\underline D_K}
}.
\]

A materially negative radicand means the directional certificates are inconsistent and the verdict is `HOLD`; it is not clamped into a false zero bound.

For exact projections,

\[
(\beta_K^{EB})^2
=
\|(I-P_K)u(T)\|_2^2
+2\nu\int_0^T\|\nabla(I-P_K)u\|_2^2dt
+\mathcal D_E(T),
\]

where

\[
\mathcal D_E(T)
=
\|u_0\|_2^2-\|u(T)\|_2^2
-2\nu\int_0^T\|\nabla u\|_2^2dt
\ge0.
\]

Thus `lim beta_K^2 = D_E(T)` for this particular budget. Under independently justified energy equality the floor vanishes.

## 6. Residual-based Galerkin-to-continuum adapter

The energy-budget theorem concerns the actual continuum projection, not a raw Galerkin output. To avoid silently identifying them, EPSC now uses a standard relative-energy adapter.

Let `v(t)` be a smooth divergence-free finite Fourier comparison path and define

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
\le
e^{A_T}\left(e_0^2+\frac{B_T}{\nu}\right)
}.
\]

If `v(T)` is supported in the retained cube, then `(I-P_K)v(T)=0`, hence

\[
\boxed{
\|(I-P_K)u(T)\|_2
\le
e^{A_T/2}\sqrt{e_0^2+B_T/\nu}
}.
\]

This supplies a terminal continuum `beta_K` from a **certified comparison path plus certified residual summaries**, without assuming that the numerical trajectory equals `P_Ku`.

## 7. Finite unresolved residual tape

For an exact `K`-supported Fourier-Galerkin path, the retained Galerkin equations cancel the projected part of the full-equation residual. The unresolved nonlinear output is supported inside the finite `2K` cube. For omitted mode `q`,

\[
\widehat r_q
=P_q\left[i\sum_{p+s=q}(s\cdot\widehat v_p)\widehat v_s\right],
\qquad \|q\|_\infty>K,
\]

and

\[
\|r\|_{H^{-1}}^2
=\sum_{q\ne0}\frac{|\widehat r_q|^2}{|q|^2}.
\]

Both are finite computations for fixed cutoff. A conservative finite Fourier bound also gives

\[
\|\nabla v\|_\infty\le\sum_k |k|\,|\widehat v_k|.
\]

Therefore the analytic adapter reduces the remaining numerical problem to certified continuous-time enclosure of finite quantities.

## 8. Implementation

Existing evolution code is reused; no second NS solver is introduced.

```text
idm/ns_retained.py                 finite Fourier-Galerkin evolution
idm/ns_epsilon.py                  nested defect + fail-closed epsilon gate
idm/ns_tail_certificate.py         spacetime / H^s / readout tail certificates
idm/ns_terminal_certificate.py     terminal energy-budget certificate
idm/ns_relative_energy_adapter.py  finite residual + relative-energy helper layer
```

Tests include:

```text
tests/test_ns_tail_certificate.py
tests/test_ns_terminal_certificate.py
tests/test_ns_relative_energy_adapter.py
```

The terminal APIs intentionally accept certified directional bounds or certified residual summaries, not unqualified raw numerical fields.

## 9. Toledo lineage

The live proposal family now runs through `PROP-EPSC-15`:

- `PROP-EPSC-01..09` — nested defect, target-indexed tail, spectral/spacetime/readout family;
- `PROP-EPSC-10` — terminal Leray-Hopf energy-budget certificate;
- `PROP-EPSC-11` — energy-defect floor / energy-equality closure;
- `PROP-EPSC-12` — Galerkin-to-continuum retained-record adapter obligation;
- `PROP-EPSC-13` — residual-based Leray relative-energy adapter;
- `PROP-EPSC-14` — finite Fourier unresolved residual tape;
- `PROP-EPSC-15` — **OPEN** validated RK4 continuous-time residual enclosure.

These are proposal identifiers and tier/provenance records, not automatically canonical verified Toledo theorem codes.

## 10. Current frontier: validated RK4 continuous-time enclosure

The current production solver stores floating-point RK4 node/stage data. Nodewise residual samples cannot certify the time integrals appearing in `A_T` and `B_T`. The remaining end-to-end numerical bridge is therefore

```text
floating-point RK4 tape
        |
        | PROP-EPSC-15 (OPEN)
        v
validated continuous-time finite Fourier interpolation v_h(t)
        |
        | certified A_T <= A_bar_T, B_T <= B_bar_T
        v
PROP-EPSC-13 relative-energy adapter
        |
        v
terminal continuum L2 beta_K
        |
        v
fail-closed epsilon certificate
```

A practical validated implementation may use a piecewise-polynomial RK4 continuous extension, outward-rounded interval coefficient enclosures, interval evaluation of finite triad residuals on each time cell, and certified integration of resulting nonnegative upper majorants. That validated interval layer is **not yet claimed complete**.

## Paper and NS evidence

The NS repository contains the standalone manuscript

`paper/EPSC_NAVIER_STOKES_CERTIFICATES.tex`

plus focused proof notes, reproduction checkers and the generated Volume-7 ledger. The manuscript deliberately separates standard analytic ingredients from project-specific EPSC architecture and finite diagnostics.

## Claim boundary

Supported at standard analytic (`Dr`) tier are the terminal non-identifiability obstruction, spectral tail inequality, explicit Leray-Hopf spacetime tail certificate, Lipschitz readout lift, conditional terminal `H^s` certificate, terminal energy-budget certificate, its energy-defect-floor analysis, and the relative-energy adapter under its stated hypotheses. Finite code checks validate only the finite algebra/instances they execute.

Still open are the validated continuous-time RK4 enclosure required for an end-to-end certificate from the current floating-point solver, unconditional pointwise global regularity in 3-D, physical/DNS adequacy of coarse cutoffs, and the global smoothness-versus-blow-up question itself.

`PROP-EPSC-04` is therefore **partially resolved by target/record refinement, not universally solved**, and `PROP-EPSC-15` is the sharp current implementation frontier.
