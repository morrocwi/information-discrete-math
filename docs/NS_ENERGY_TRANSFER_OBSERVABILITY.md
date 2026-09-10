# Energy-transfer observability bridge for finite Navier-Stokes

Status: mixed `Dr` / `finite_diagnostic` / `Open`. This document narrows open work; it does not convert finite observability into a continuum theorem.

## 1. Exact shell balance

For the unforced or prescribed-forcing finite Fourier-Galerkin system, let

\[
I_s(t)=\frac12\sum_{|k|^2=s}|\widehat u_k(t)|^2
\]

under the repository's declared normalization. The shell-energy balance has the form

\[
\dot I_s=T_s-2\nu s I_s+F_s,
\]

where `T_s` is the nonlinear inter-shell transfer and `F_s` is a declared shell-energy input. In the unforced closed finite system,

\[
\sum_s T_s=0.
\]

The nonlinear term redistributes total kinetic energy between shells; viscosity dissipates it. This is standard finite Navier-Stokes energy bookkeeping, not an originality claim.

## 2. Transfer is the first energy jet in different coordinates

For known `nu` and prescribed `F`,

\[
T=\dot I+2\nu S I-F,\qquad S=\operatorname{diag}(s_1,\dots,s_m).
\]

Hence the paired observations `(I,T)` and `(I,\dot I)` are related by an invertible affine block-triangular map. Their Jacobians have exactly the same rank. Therefore transfer variables do **not** manufacture new local information beyond the first shell-energy derivative.

This correction matters: transfer is useful because it exposes the mechanism and admits integral/window formulations, not because it evades the observability rank ceiling.

The conservation identity `sum_s T_s=0` is the explicit reason a new shell-derivative block contributes at most `m-1` independent directions, matching the structural ceiling already registered as `PROP-NSOBS-03`.

## 3. Window balance: a route that does not differentiate measurements

Integrating the shell balance over `[t0,t1]` gives

\[
\int_{t_0}^{t_1}T_s\,dt
=I_s(t_1)-I_s(t_0)+2\nu s\int_{t_0}^{t_1}I_s\,dt-\int_{t_0}^{t_1}F_s\,dt.
\]

If the four terms on the right have certified interval radii `r_1,r_0,r_I,r_F`, then

\[
\operatorname{rad}\!\left(\int T_sdt\right)
\le r_1+r_0+2\nu s\,r_I+r_F.
\]

This closes one subproblem inside `PROP-EPSC-19`: nonlinear transfer can be observed through a certified finite-time balance without numerically constructing high-order derivatives. It does **not** close the full noisy state inversion.

## 4. Exact quantitative inverse in the analytic triad subcase

The repository's three-mode analytic subcase uses reduced invariants `(x,y,z,r)` and coefficient

\[
c_a=\frac{3}{10},\qquad |a|^2=1.
\]

The first shell-energy derivative satisfies

\[
J_{1,a}=2c_a r-2\nu x,
\]

so

\[
r=\frac{J_{1,a}+2\nu x}{2c_a}.
\]

With certified absolute input radii `sigma_J` and `sigma_x`,

\[
|r-\widehat r|
\le
\frac{\sigma_J+2\nu\sigma_x}{2|c_a|}.
\]

At `nu=1/200`, this becomes

\[
|r-\widehat r|\le \frac53\sigma_J+\frac1{60}\sigma_x.
\]

Thus `EPSC-18` has a genuine quantitative witness on this reduced triad model. The full `N=1` 52-real-dimensional cube, and arbitrary `N`, remain open.

## 5. All-N kinematic triad connectivity lemma

Let

\[
K_N=\{k\in\mathbb Z^3:0<\|k\|_\infty\le N\}.
\]

For every `N>=2` and every boundary mode `k` with `||k||_infinity=N`, one can construct `p in K_{N-1}` and `q in K_N` such that

\[
p+q=k
\]

and `p,q` are non-collinear.

Construction. Choose a coordinate `i` with `|k_i|=N`.

* If `k` has a nonzero component transverse to `i`, take `p=sgn(k_i)e_i` and `q=k-p`.
* If `k=+-N e_i` is an axis mode, take a transverse unit vector `p=e_j`, `j!=i`, and `q=k-p`.

In both cases `p` lies in the old cube, `q` remains in the new cube, and `p x q != 0`. Non-collinearity is enough for a nontrivial Navier-Stokes interaction for suitable divergence-free polarizations.

Consequently every newly added boundary mode is kinematically attached to the previous cutoff, and every newly appearing energy shell has a transfer-hypergraph edge to an old shell. The implementation exhaustively checks the constructive witness through `N=8`.

This is **not** an all-N observability theorem. It removes a connectivity obstruction only. `PROP-NSOBS-07` is reduced to the harder issue: algebraic independence/nonvanishing of enough observable minors after symmetry is factored out.

## 6. What is now closed and what remains open

Closed/narrowed pieces:

- shell transfer balance and total-transfer conservation;
- exact affine equivalence of `(I,T)` and `(I,dI/dt)` for the declared forcing scope;
- a derivative-free finite-window transfer observable with certified radius propagation;
- a quantitative inverse radius for the existing analytic triad subcase;
- all-N kinematic connection of every new boundary mode to the old cutoff.

Still open:

- `PROP-EPSC-18` for the full finite Fourier quotient: certified branch/gauge-fixed inversion with an explicit `rho_N`;
- `PROP-EPSC-19` for the full noisy measurement-to-state inverse, although derivative-free window transfer removes one avoidable source of noise amplification;
- `PROP-NSOBS-07`: all-N earliest-order saturation; connectivity alone does not prove rank;
- `PROP-EPSC-16`: high-cutoff cost/tightness of the outer continuum certificate, which is a separate frontier.

The intended chain is therefore

\[
\text{shell energy windows}
\to\text{certified transfer summaries}
\to\text{gauge-fixed finite inverse }(\widehat x_N,\rho_N)
\to\beta_N
\to\sqrt{\rho_N^2+\beta_N^2}.
\]

If the inverse radius or the tail radius is missing, the end-to-end status remains `HOLD`.
