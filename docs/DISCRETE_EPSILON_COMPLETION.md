# Discrete Epsilon-Completion Programme

Status: **partially closed by target/readout refinement**. Rigorous computable omitted-tail certificates now exist for (i) a Leray-Hopf spacetime norm and (ii) a prescribed terminal time when a certified retained energy tape is available. A certified adapter from the project's finite Galerkin trajectory to the actual continuum projected tape remains open.

## Repository roles

- **Information Discrete Mathematics:** algorithm, finite refinement, fail-closed gates, reusable certificate code.
- **Toledo:** proposal/equation provenance and tier status.
- **Readout-Problem-Navier-Stokes:** NS-specific analytic derivations, finite witnesses, reproduction and claim boundary.
- **Readout Genesis:** interpretation only; no automatic promotion to root ontology.

## 1. General EPSC object

The certificate target must name a target space/readout `Y` and assumptions `A`:

\[
\|(I-P_K)x\|_Y\le\beta_{K,Y}(\mathcal R_K;\mathcal A),
\qquad
\beta_{K,Y}\to0.
\]

Nested agreement

\[
\delta_K=\|R_Kx_{K+1}-x_K\|
\]

is useful evidence but does not by itself bound what remains outside the represented state.

The fail-closed rule remains:

\[
\delta_K+\beta_K\le\varepsilon
\Longrightarrow
\mathrm{ACCEPT}_\varepsilon,
\]

and if the required `beta_K` or adapter hypothesis is missing, return `HOLD`.

## 2. Terminal finite-record no-go

For a finite Fourier cube `P_K`, terminal retained coefficients alone do not identify the omitted tail over the unrestricted divergence-free `L2` class. Put a divergence-free conjugate pair at

\[
q=(K+1,0,0),
\]

entirely outside the retained cube. Its amplitude may be scaled arbitrarily while `P_Ku` is unchanged.

Thus a useful universal terminal `beta_K` cannot be a function of retained terminal coefficients alone without additional admissible-class information.

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

This `beta_K` is explicit, computable and tends to zero without a global-smoothness assumption.

For `f in L2(0,T;H^{-1})`, a conservative forced analogue is

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

## 5. Prescribed terminal-time energy-budget certificate

The terminal no-go concerns low-mode terminal coefficients alone. Navier-Stokes supplies a richer finite record: retained terminal energy plus accumulated retained viscous dissipation.

For the **actual** unforced Leray-Hopf projection,

\[
\boxed{
\|(I-P_K)u(T)\|_2^2
\le
\|u_0\|_2^2
-
\|P_Ku(T)\|_2^2
-
2\nu\int_0^T\|\nabla P_Ku(t)\|_2^2dt
}.
\]

A fail-closed directional-bound version takes

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

If the radicand is materially negative, the inputs are mutually inconsistent and the verdict is `HOLD`; never clamp such a result to zero.

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
\ge0
\]

is the energy-inequality slack. Hence

\[
\lim_{K\to\infty}(\beta_K^{EB})^2=\mathcal D_E(T).
\]

If energy equality is independently justified, `D_E(T)=0` and this terminal certificate tends to zero.

## 6. Implementation

Existing evolution code is reused; no second NS solver is introduced.

```text
idm/ns_retained.py              finite Fourier-Galerkin evolution
idm/ns_epsilon.py               nested defect + fail-closed epsilon gate
idm/ns_tail_certificate.py      spacetime / H^s / readout tail certificates
idm/ns_terminal_certificate.py  terminal energy-budget certificate
```

Tests:

```text
tests/test_ns_tail_certificate.py
tests/test_ns_terminal_certificate.py
```

The terminal API intentionally accepts **certified directional bounds**, not raw numerical fields, because the theorem concerns the actual continuum projection.

## 7. Toledo lineage

- `PROP-EPSC-01..09`: `morrocwi/toledo/registry/proposals/discrete_epsilon_completion.json`
- `PROP-EPSC-10`: terminal Leray-Hopf energy-budget certificate
- `PROP-EPSC-11`: energy-defect floor / energy-equality closure
- `PROP-EPSC-12`: **OPEN** finite-Galerkin -> continuum retained-energy-tape adapter

The latter three are in `registry/proposals/discrete_epsilon_completion_terminal_energy.json`.

## 8. Current frontier

The main problem has moved from “invent some `beta_K`” to a much sharper bridge:

```text
project finite Galerkin trajectory
        |
        | PROP-EPSC-12: certified directional adapter error (OPEN)
        v
actual continuum projected terminal energy/dissipation tape
        |
        | PROP-EPSC-10
        v
rigorous terminal beta_K
```

Nested-cutoff stability can help diagnose this adapter, but it is not itself the adapter theorem.

## Claim boundary

Supported at standard analytic (`Dr`) tier:

- terminal low-mode records alone are non-identifying over an unrestricted divergence-free `L2` class;
- the spectral `H^s -> L2` tail inequality;
- explicit Leray-Hopf `L2_tL2_x` tail certificates;
- Lipschitz readout lifts;
- a terminal tail certificate conditional on a pointwise `H^s` bound;
- a prescribed terminal-time a-posteriori energy-budget bound from certified retained energy/dissipation data;
- asymptotic closure of that energy-budget certificate under energy equality.

Still open:

- the certified Galerkin-to-continuum adapter needed to feed the current finite solver into the terminal continuum theorem;
- unconditional pointwise global regularity in 3-D;
- physical/DNS adequacy of coarse cutoffs;
- global smoothness versus finite-time singularity of full 3-D Navier-Stokes.

`PROP-EPSC-04` is therefore **partially resolved, not universally solved**.
