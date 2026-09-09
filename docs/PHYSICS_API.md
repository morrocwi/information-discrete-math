# IDM Physics

`idm.physics` is the physics-facing adapter layer over the existing `idm.solve()` engine.
It does not create a second numerical solver and it does not treat the continuum as a
computation primitive.

## Core call

```python
import idm

r = idm.physics.solve(
    model="navier_stokes",
    readout="harmonic_probe",
    K=2,
    nu=0.005,
    dt=0.0025,
    horizon=1,
    wavevector=[2, 2, 2],
    phase=0.3,
    verify=True,
)
```

The structured-dict form is equivalent:

```python
r = idm.physics.solve({
    "model": "navier_stokes",
    "readout": "fourier_mode",
    "K": 2,
    "horizon": 1,
    "target_mode": [1, 0, 0],
})
```

## Mandatory equation lineage

A `PhysicsAdapter` cannot be registered unless it declares all three fields:

```text
toledo_root
equation_parent
derivation_tier
```

Every result echoes these fields, even when the underlying solve returns `HOLD`.
For the current Navier--Stokes adapters the lineage is:

```text
toledo_root          = root/EQ-008
equation_parent      = PROP-URCF-01
equation_parent_alias= EQ-URCF-TURB-004
derivation_tier      = derived_finite_galerkin
```

This lineage must not be read backwards.  Navier--Stokes supplies the physical dynamics.
Toledo supplies the retained-operator structural lineage into which the exact finite
Navier--Stokes retained equation fits.

The finite retained identity is

\[
\dot I + L_\nu I = \eta^{NS},
\]

with

\[
L_\nu=\operatorname{diag}(2\nu q_1,\ldots,2\nu q_m).
\]

The Toledo retained-response parent has the structural form

\[
\tau_R\dot I_R+L_RI_R=S_R+\eta_R.
\]

For the unforced finite Navier--Stokes adapter,

\[
I_R=I,\qquad L_R=\tau_RL_\nu,\qquad S_R=0,\qquad
\eta_R=\tau_R\eta^{NS}.
\]

## Discrete-native rule

Every admitted adapter records

```text
continuum_primitive = false
computation_semantics = finite_discrete
```

and registration rejects `continuum_primitive=True`.
A continuum PDE may be the source description of a model, but execution must occur after
a declared finite translation.  For the current Navier--Stokes model that translation is
the finite Fourier--Galerkin system used by the existing retained RK4 solvers.

## Current Navier--Stokes readouts

| Physics readout | Underlying IDM kind |
|---|---|
| `fourier_mode` | `ns_retained_rk4` |
| `point_velocity` | `ns_retained_physical` |
| `plane_average_velocity` | `ns_retained_plane_average` |
| `harmonic_probe` | `ns_retained_harmonic_probe` |
| `turbulence_energy_flux` | `ns_turbulence_energy_flux` |

The turbulence readout is downstream of the same finite nonlinear Navier--Stokes
dynamics.  It evaluates

\[
\Pi(\kappa)=-\sum_{|k|\le\kappa}
\operatorname{Re}\!\left(\overline{\hat u_k}\cdot N_k(\hat u)\right),
\]

with positive flux meaning nonlinear energy leaves the low-mode set.  See
`docs/NS_TURBULENCE_API.md` for its retained-dependency and verification contract.

Aliases such as `model="ns"`, `readout="mode"`, `readout="plane_average"`,
`readout="harmonic"`, and `readout="flux"` normalize to the registered names.

## Discovery

```python
idm.physics.models()
idm.physics.adapters()
idm.physics.describe("navier_stokes")
idm.physics.describe("navier_stokes", "turbulence_energy_flux")
```

## Result lineage

A successful or held physics result includes fields such as:

```text
physics_model
physics_readout
physics_adapter_kind
toledo_root
equation_parent
equation_parent_alias
derivation_tier
source_equation
continuum_primitive
computation_semantics
equation_lineage
```

The ordinary solver `tier` and the physics `derivation_tier` are deliberately distinct.
For example, the equation route can be `derived_finite_galerkin` while a numerical run is
still honestly labelled `finite_diagnostic`.

## Claim boundary

`idm.physics` currently provides one physical dynamics model: finite Fourier--Galerkin
periodic incompressible Navier--Stokes, with direct field readouts and a first turbulence
readout.  It is not a continuum-exact Navier--Stokes solver, not a Millennium-problem
claim, and not a general-purpose physics engine yet.  The registry is intended to admit
future finite/discrete adapters without losing their Toledo/equation lineage.
