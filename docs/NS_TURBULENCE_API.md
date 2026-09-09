# IDM Physics — finite Navier--Stokes turbulence readouts

The first turbulence-facing readout is `turbulence_energy_flux`.  It is a readout of
the existing finite Fourier--Galerkin Navier--Stokes dynamics; it is not a separate
turbulence closure and does not add an empirical cascade law.

## Physics identity used

For each retained Fourier mode `k`, let `N_k(u)` be the nonlinear Galerkin RHS with
viscosity removed.  The modal nonlinear energy transfer is

\[
T_k = \operatorname{Re}\left(\overline{\hat u_k}\cdot N_k(\hat u)\right).
\]

For a radial cutoff \(\kappa\), IDM uses

\[
\boxed{
\Pi(\kappa)=-\sum_{|k|\le\kappa}T_k
}
\]

so positive `Pi` means nonlinear transfer removes energy from the low-mode set
`|k| <= cutoff`.

For squared-radius shells \(q=|k|^2\), the returned shell rows also expose

\[
E_q=\frac12\sum_{|k|^2=q}|\hat u_k|^2,
\qquad
T_q=\sum_{|k|^2=q}T_k,
\qquad
D_q=2\nu q E_q,
\]

and therefore the finite shell balance

\[
\dot E_q=T_q-D_q.
\]

These equations are evaluated on the declared finite Fourier cube and the same RK4
recurrence as the existing IDM Navier--Stokes solvers.

## Python API

```python
import idm

r = idm.physics.solve(
    model="navier_stokes",
    readout="turbulence_energy_flux",
    K=2,
    nu=0.005,
    dt=0.0025,
    horizon=1,
    cutoff=1.5,
    verify=True,
)

print(r["value"])
```

Aliases `readout="flux"`, `"energy_flux"`, and `"turbulence_flux"` route to the same
registered adapter.

The lower-level solver kind is:

```python
r = idm.solve({
    "kind": "ns_turbulence_energy_flux",
    "K": 2,
    "nu": 0.005,
    "dt": 0.0025,
    "horizon": 1,
    "cutoff": 1.5,
    "verify": True,
})
```

## Retained computation

The readout does not assume that the cutoff modes alone are dynamically sufficient.
To evaluate \(T_k\) for low modes it first includes every triad input required by those
outputs, then pulls that required final-state support backward through each RK4 stage.
The result reports both:

- `readout_density`: fraction of modes directly included in the flux sum;
- `required_state_density`: fraction of final-state modes actually needed to evaluate it;
- `rk4_stage_ledger`, `retained_triad_work`, `full_triad_work`, and
  `structural_work_reduction`.

This preserves the distinction

\[
\boxed{
\text{small readout}\neq\text{small causal cone}\neq\text{runtime speedup}.
}
\]

## Verification gates

With `verify=True`, the portable solver:

1. recomputes the same readout after a full finite RK4 rollout and requires
   `retained_full_flux_abs_error <= 1e-12`;
2. checks the finite Galerkin redistribution identity
   \(\left|\sum_kT_k\right|\le10^{-12}\) on the full final state;
3. requires the supplied initial state to be divergence-free and conjugate-symmetric
   within the declared finite tolerance.

A failed gate returns `HOLD` through the public IDM solver.

## Lineage and claim boundary

The physics adapter keeps the existing Navier--Stokes/Toledo lineage:

```text
toledo_root           = root/EQ-008
equation_parent       = PROP-URCF-01
equation_parent_alias = EQ-URCF-TURB-004
derivation_tier       = derived_finite_galerkin
continuum_primitive   = false
```

The turbulence quantity is downstream of the finite nonlinear Navier--Stokes term.
The API does **not** claim:

- continuum-exact turbulence;
- a universal inertial-range law;
- Kolmogorov scaling from the root;
- a learned or autonomous shell closure;
- a Navier--Stokes Millennium result.

The current claim is only a finite Fourier--Galerkin turbulence readout, exact relative
to the same declared finite RK4 recurrence within the verification tolerance.
