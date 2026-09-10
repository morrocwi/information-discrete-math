# Discrete Epsilon-Completion Programme

Status: **finite-diagnostic architecture with one open certification gap**.

This note records the general mathematical/computational pattern isolated from the Readout-Navier-Stokes refinement experiments. It is deliberately domain-general. Navier-Stokes is the first worked application, not the source of a universal theorem.

## Canonical separation of roles

- **Information Discrete Mathematics (this repository):** general algorithm, diagnostics, fail-closed certification interface.
- **Toledo:** equation/definition provenance and proposal status.
- **Readout-Problem-Navier-Stokes:** NS-specific finite Galerkin implementation evidence, experiments, and benchmarks.
- **Readout Genesis:** interpretation only; finite numerical evidence here does not automatically become an ontological/root claim.

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
  If no proved `beta_K` exists, the verdict is `HOLD` for continuum/infinite-object completion.
- `PROP-EPSC-04` — **OPEN** computable omitted-information certificate target
  \[
  \|(I-P_K)x\|\le\beta_K(\mathcal R_K),\qquad \beta_K\to0.
  \]

The proposal codes are not canonical Toledo codes yet. Do not cite them as verified theorems.

## Why the programme exists

Observed stabilization under refinement is useful evidence, but it is not the same thing as a mathematical bound on everything not represented. The programme therefore separates two quantities:

1. `delta_K`: what changes on the shared finite record when one more refinement level is computed;
2. `beta_K`: what the still-unrepresented distinctions could change, bounded by a proved certificate.

Only the second closes the finite-to-infinite gap.

## Navier-Stokes instantiation

The finite production substrate is the existing `idm.ns_retained` Fourier-Galerkin RK4 recurrence. The epsilon layer does **not** introduce a second NS solver. `idm.ns_epsilon` imports that substrate and adds:

- nested-cutoff comparison;
- outer-shell boundary energy as a finite diagnostic proxy;
- an operational repeated-pass diagnostic;
- a fail-closed `CERTIFIED/HOLD` function that refuses continuum-completion certification unless a separate proved `beta_K` is supplied.

For the NS application, the finite state is

\[
X_K=\{\widehat u_k:\|k\|_\infty\le K,\ k\ne0\},
\]

and the restriction simply forgets the additional outer modes of the finer cutoff.

## Claim boundary

What is currently supported:

- direct finite computation can be performed on integer Fourier-mode records;
- nested refinements can be compared on their shared record;
- finite boundary activity can be measured;
- a software gate can refuse to promote finite stability into a continuum claim.

What remains open:

- a useful, rigorous, computable `beta_K` for general 3D Navier-Stokes states;
- a proof that any specific finite cutoff contains all continuum information to a declared tolerance;
- universal runtime acceleration;
- physical/DNS adequacy at coarse cutoffs.

The external Taylor-Green validation already records that K<=3 is far too coarse in the turbulent regime. This negative evidence is retained as part of the claim boundary rather than hidden by the short-horizon refinement diagnostic.

## Public API direction

The current module is intentionally explicit:

```python
from idm.ns_epsilon import (
    nested_cutoff_diagnostic,
    epsilon_completion_verdict,
)

finite = nested_cutoff_diagnostic(K_values=(1, 2, 3))
# finite["continuum_certificate"] == "HOLD"

verdict = epsilon_completion_verdict(
    delta=1e-8,
    beta=None,
    epsilon=1e-6,
)
# verdict["status"] == "HOLD"
```

A later unified `idm.solve()` kind should be added only after the API and evidence contract are stable enough not to overstate the open tail-certificate problem.
