# Discrete Epsilon-Completion Programme

Status: **partially closed**.  A rigorous computable omitted-tail certificate now exists for an important Navier-Stokes completion space, while arbitrary terminal-state completion remains open.

This note records the general mathematical/computational pattern isolated from the Readout-Navier-Stokes refinement experiments. It is deliberately domain-general. Navier-Stokes is the first worked application, not the source of a universal theorem.

## Canonical separation of roles

- **Information Discrete Mathematics (this repository):** general algorithm, diagnostics, fail-closed certification interface, and reusable spectral-tail certificate helpers.
- **Toledo:** equation/proposal provenance and proposal status.
- **Readout-Problem-Navier-Stokes:** NS-specific proof note, finite Galerkin evidence, reproduction and claim boundary.
- **Readout Genesis:** interpretation only; application results do not automatically become ontological/root claims.

## Toledo proposal lineage

Registered 2026-09-10 in `morrocwi/toledo/registry/proposals/discrete_epsilon_completion.json`:

- `PROP-EPSC-01` — Nested Readout Consistency Defect
  \[
  \delta_K=\|R_Kx_{K+1}-x_K\|.
  \]
- `PROP-EPSC-02` — Navier-Stokes Fourier boundary-energy diagnostic
  \[
  E_{\partial K}=\frac12\sum_{\|k\|_\infty=K}|\widehat u_k|^2.
  \]
- `PROP-EPSC-03` — fail-closed epsilon-completion gate
  \[
  \delta_K+\beta_K\le\varepsilon\Longrightarrow \mathrm{ACCEPT}_\varepsilon.
  \]
- `PROP-EPSC-04` — general computable omitted-information certificate target.

The important 2026-09-10 refinement is that `PROP-EPSC-04` must be indexed by the **declared target norm/readout**. It is impossible in one form and provable in another.

## 1. Terminal finite-record no-go

Finite Fourier records alone do not identify the full omitted terminal tail over an unrestricted divergence-free `L2` class.

For any cutoff `K`, choose an omitted integer mode

\[
q=(K+1,0,0)
\]

and a nonzero vector `a` perpendicular to `q`. Adding a conjugate pair at `q,-q` changes no retained coefficient with `||k||_infinity <= K`, but changes the omitted `L2` tail by an arbitrarily scalable amount.

Therefore no function of the retained terminal coefficients alone can give a universal useful bound

\[
\|(I-P_K)u(T)\|_2\le\beta_K(P_Ku(T)),\qquad \beta_K\to0,
\]

without extra assumptions or an independently certified global regularity/budget quantity.

This is not a weakness of a particular solver. It is an identifiability obstruction.

## 2. Positive closure in spacetime `L2_t L2_x`

Let `u` be a Leray-Hopf weak solution of unforced incompressible Navier-Stokes on the `2*pi` periodic three-torus, with viscosity `nu>0`, and let `P_K` retain the Fourier cube `||k||_infinity <= K`.

Every omitted mode satisfies

\[
|k|_2\ge K+1.
\]

Hence, mode by mode,

\[
\|(I-P_K)u(t)\|_2^2
\le \frac{1}{(K+1)^2}\|\nabla u(t)\|_2^2.
\]

The Leray-Hopf energy inequality gives

\[
\frac12\|u(t)\|_2^2+
u\int_0^t\|\nabla u(s)\|_2^2\,ds
\le\frac12\|u_0\|_2^2.
\]

Therefore

\[
\boxed{
\|(I-P_K)u\|_{L^2(0,T;L^2_x)}
\le
\beta_K^{\mathrm{ST}}
:=
\frac{\|u_0\|_2}{\sqrt{2\nu}(K+1)}
}
\]

and

\[
\beta_K^{\mathrm{ST}}\to0.
\]

This is exactly the missing finite-to-infinite pattern for the **declared spacetime norm**: the right-hand side is finite, computable from input data and the cutoff, and does not require global smoothness of the 3-D solution.

For forcing `f in L2(0,T;H^{-1})`, Young's inequality yields the explicit conservative bound

\[
\boxed{
\beta_{K,f}^{\mathrm{ST}}
=
\frac{1}{K+1}
\sqrt{
\frac{\|u_0\|_2^2}{\nu}
+
\frac{\|f\|_{L^2_tH^{-1}}^2}{\nu^2}
}
}
\]

under the same Fourier normalization.

## 3. Readout lift

If a declared readout `Q` is Lipschitz in the certified state norm with constant `L_Q`, then

\[
\|Q(u)-Q(P_Ku)\|
\le L_Q\beta_K^{\mathrm{ST}}.
\]

A concrete example is the time-averaged field

\[
\bar u=\frac1T\int_0^T u(t)\,dt,
\]

for which Cauchy-Schwarz gives

\[
\|(I-P_K)\bar u\|_2
\le\frac{\beta_K^{\mathrm{ST}}}{\sqrt T}.
\]

Thus finite Fourier records can certify a whole family of finite readouts of the weak trajectory even though arbitrary terminal reconstruction remains unavailable.

## 4. Conditional terminal certificate

If a separate argument certifies at time `T`

\[
\||\nabla|^s u(T)\|_2\le M_s(T),\qquad s>0,
\]

then the same spectral argument gives

\[
\boxed{
\|(I-P_K)u(T)\|_2
\le\frac{M_s(T)}{(K+1)^s}
}
\]

and this terminal `beta_K` tends to zero. The unresolved 3-D difficulty has therefore been isolated: **the spectral tail step is easy; obtaining a globally valid pointwise high-regularity bound is the hard part**.

This is the correct place to connect to the Navier-Stokes regularity problem. The epsilon-completion programme does not bypass that regularity requirement for arbitrary terminal state.

## 5. Implementation

Reusable certificate machinery now lives in:

```text
idm/ns_tail_certificate.py
```

The module provides:

- `leray_unforced_spacetime_tail_beta`
- `leray_forced_spacetime_tail_beta`
- `conditional_hs_tail_beta`
- `time_average_tail_beta`
- `lipschitz_readout_tail_beta`
- `terminal_nonidentifiability_witness`
- `finite_spectral_tail_and_hs`

The existing finite solver remains in `idm.ns_retained`; no second Navier-Stokes evolution implementation was introduced.

## 6. How the fail-closed gate changes

For a spacetime/readout target whose assumptions are satisfied, the gate may now receive a proved `beta`:

```python
from idm.ns_epsilon import epsilon_completion_verdict
from idm.ns_tail_certificate import leray_unforced_spacetime_tail_beta

beta = leray_unforced_spacetime_tail_beta(
    K=63,
    nu=0.01,
    initial_l2_norm=1.0,
)

verdict = epsilon_completion_verdict(
    delta=1e-8,
    beta=beta,
    epsilon=1e-2,
)
```

For a requested terminal full state with no verified `H^s` bound, the verdict must still be `HOLD`.

## Claim boundary

What is now supported analytically:

- finite retained terminal coefficients alone do not identify an unrestricted omitted terminal tail;
- a computable `1/(K+1)` omitted-tail certificate exists for Leray-Hopf trajectories in `L2(0,T;L2_x)`;
- that certificate lifts to Lipschitz readouts, including the time-averaged field;
- a terminal certificate follows conditionally from any separately verified pointwise `H^s` bound.

What remains open:

- a useful unconditional terminal-time `beta_K` for arbitrary 3-D Navier-Stokes states at an arbitrary prescribed time;
- a proof that a particular coarse cutoff is physically/DNS adequate in turbulent regimes;
- global smoothness or finite-time singularity of the full 3-D equation.

The distinction is intentional: **`PROP-EPSC-04` is partially closed by target-space refinement, not universally solved.**
