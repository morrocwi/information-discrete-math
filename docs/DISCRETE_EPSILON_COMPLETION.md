# Discrete Epsilon-Completion Programme

Status: **end-to-end finite-tape adapter constructed for the declared periodic Fourier setting**. Rigorous computable omitted-tail certificates exist for a Leray-Hopf spacetime norm and for several conditional/a-posteriori terminal settings. `PROP-EPSC-15`, previously the missing numerical bridge, is now supplied by an exact-dyadic piecewise-linear comparison path built from the recorded RK4 node tape. The standard relative-energy transfer remains analytic (`Dr`) rather than machine-checked. High-cutoff tightness and cost are the new engineering frontier (`PROP-EPSC-16`).

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

A Lipschitz readout `Q` inherits the certified error, and a time-average inherits the corresponding `1/sqrt(T)` factor.

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

For the **actual** unforced Leray-Hopf projection,

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

A materially negative radicand means the directional certificates are inconsistent and the verdict is `HOLD`; it is not clamped into a false zero bound. The asymptotic floor of this particular energy-budget certificate is the energy-inequality defect; under independently justified energy equality that floor vanishes.

## 6. Residual-based finite-path-to-continuum adapter

To avoid silently identifying a Galerkin output with the continuum projection, EPSC uses a standard relative-energy adapter. Let `v(t)` be a divergence-free comparison path with the required regularity and define

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
\le e^{A_T/2}\sqrt{e_0^2+B_T/\nu}.
} 
\]

The continuum implication is analytic (`Dr`). The project-specific numerical obligation is to provide certified `A_T` and `B_T` from the actual recorded finite tape.

## 7. PROP-EPSC-15: exact continuous-time enclosure of an RK4 tape

The missing numerical bridge can be supplied without pretending that the RK4 recurrence is the exact PDE flow and without reconstructing an unknown continuum trajectory.

For every stored binary64 Fourier coefficient, take its **exact IEEE-754 dyadic rational value**. Apply the Fourier Leray projector in exact rational arithmetic and call the resulting node records `v_n`. Between consecutive nodes define

\[
v_h(t_n+\theta h)=(1-\theta)v_n+\theta v_{n+1},
\qquad 0\le\theta\le1.
\]

This path is continuous, finite Fourier-supported and exactly divergence-free. Its time derivative is piecewise constant. Because every Fourier coefficient is affine in `theta`, the quadratic convection term is degree at most two:

\[
P[(v_h\cdot\nabla)v_h]
=C_0+C_1\theta+C_2\theta^2.
\]

Therefore the full residual on a cell,

\[
r_h=\partial_t v_h+P[(v_h\cdot\nabla)v_h]-\nu\Delta v_h-Pf,
\]

is degree at most two in `theta`, supported on a finite Fourier cube, and

\[
\|r_h\|_{H^{-1}}^2
\]

is a degree-at-most-four polynomial whose time integral can be evaluated **exactly as a rational number**. For the normalized `2*pi` torus the implementation uses

\[
\|r_h\|_{H^{-1}}^2
=\sum_{q\ne0}\frac{|\widehat r_q|^2}{|q|^2}.
\]

A rigorous gradient majorant is obtained from

\[
\|\nabla v_h\|_\infty
\le \sum_{k,i,j}|k_j|\,|\widehat v_{k,i}|
\le \sum_{k,i,j}|k_j|
\left(|\Re\widehat v_{k,i}|+|\Im\widehat v_{k,i}|\right),
\]

and convexity of absolute value gives an exact endpoint-based cell integral for this majorant. Finally, `exp(A_bar)` is enclosed from above with an exact rational Taylor partial sum plus a geometric remainder, and the reported decimal square root is rounded upward by integer arithmetic.

Thus the chain is now

```text
stored binary64 RK4 node tape
        |
        | exact dyadic capture + exact Leray projection
        v
continuous piecewise-linear finite Fourier path v_h(t)
        |
        | exact rational residual integration + rigorous gradient majorant
        v
A_T <= A_bar_T,  B_T <= B_bar_T
        |
        | PROP-EPSC-13 (analytic Dr relative-energy theorem)
        v
terminal continuum L2 / omitted-tail beta_K
```

The PDE residual of the comparison path is **not hidden**: interpolation error, time-discretization error, and the difference between the finite path and an exact Navier-Stokes trajectory all enter `B_bar`.

## 8. Implementation

```text
idm/ns_retained.py                 finite Fourier-Galerkin evolution
idm/ns_epsilon.py                  nested defect + fail-closed epsilon gate
idm/ns_tail_certificate.py         spacetime / H^s / readout tail certificates
idm/ns_terminal_certificate.py     terminal energy-budget certificate
idm/ns_relative_energy_adapter.py  analytic adapter + snapshot residual helpers
idm/ns_rk4_path_certificate.py     exact-dyadic piecewise-linear A/B enclosure
```

Tests include:

```text
tests/test_ns_tail_certificate.py
tests/test_ns_terminal_certificate.py
tests/test_ns_relative_energy_adapter.py
tests/test_ns_rk4_path_certificate.py
```

The path-certificate API returns `CERTIFIED_SUMMARIES` only after exact divergence and zero-mean residual preconditions pass. Its finite arithmetic is separate from the analytic continuum theorem that consumes those summaries.

## 9. Executed finite witness

The independent NS reproduction checker executes the same construction on a short Taylor-Green `K=1` RK4 tape (`nu=0.01`, `dt=0.01`, `T=0.05`). In the recorded run it produced exact divergence-free nodes and zero-mean residual, with conservative finite summaries approximately

\[
\overline A_T=5.9955022941\times10^{-1},
\qquad
\overline B_T=9.7363869259\times10^{-5},
\]

and terminal relative-energy upper radius approximately

\[
\beta_T\le1.3316484576\times10^{-1}.
\]

These are **certificate values for that finite short run**, not a claim that `K=1` is a physically adequate turbulence resolution. A shear-decay sanity case independently checks that the certified radius dominates the known analytic terminal error.

## 10. Toledo lineage

The proposal family now runs through `PROP-EPSC-16`:

- `PROP-EPSC-01..09` — nested defect, target-indexed tail, spectral/spacetime/readout family;
- `PROP-EPSC-10` — terminal Leray-Hopf energy-budget certificate;
- `PROP-EPSC-11` — energy-defect floor / energy-equality closure;
- `PROP-EPSC-12` — broad Galerkin-to-continuum retained-record adapter obligation;
- `PROP-EPSC-13` — residual-based Leray relative-energy adapter;
- `PROP-EPSC-14` — finite Fourier residual tape;
- `PROP-EPSC-15` — exact-dyadic piecewise-linear continuous-time RK4-tape enclosure;
- `PROP-EPSC-16` — **OPEN** high-cutoff tightness/scaling refinement.

These are proposal identifiers and provenance/tier records, not automatically canonical verified Toledo theorem codes.

## 11. Current frontier

The logical missing link identified by EPSC-15 is no longer “how do we turn node samples into a continuous-time certified residual?” A concrete construction now does that for the declared finite periodic Fourier tape.

The remaining practical research problem is whether the bound can stay computationally affordable and non-vacuous as `K` and `T` grow. The current Fourier `l1` gradient majorant and the relative-energy exponential are deliberately conservative. Improving their tightness, using block/shell structure, interval FFTs, higher-order exact/validated continuous extensions, or retained readouts belongs to `PROP-EPSC-16`; none of those optimisations is required for the correctness of the present small finite certificate.

## Claim boundary

Supported at standard analytic (`Dr`) tier are the terminal non-identifiability obstruction, spectral tail inequality, explicit Leray-Hopf spacetime tail certificate, Lipschitz readout lift, conditional terminal `H^s` certificate, terminal energy-budget certificate, its energy-defect-floor analysis, and the relative-energy adapter under its stated hypotheses. `PROP-EPSC-15` adds a finite exact-rational construction of the required continuous-time summaries from a recorded Fourier node tape; its executed instances are `finite_diagnostic`.

Still open are high-cutoff tightness/scaling, unconditional pointwise global regularity in 3-D, physical/DNS adequacy of coarse cutoffs, and the global smoothness-versus-blow-up question itself.

`PROP-EPSC-04` is therefore **resolved for several declared reader/record classes, not universally for arbitrary terminal retained coefficients**, and `PROP-EPSC-16` is the current engineering frontier.
