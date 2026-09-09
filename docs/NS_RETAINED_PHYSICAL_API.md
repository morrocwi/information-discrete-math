# `ns_retained_physical` — physical-space finite Navier–Stokes readout

## Purpose

This solver kind evaluates a physical-space velocity readout after the same fixed finite Fourier-Galerkin RK4 recurrence used by the portable IDM Navier–Stokes solver.

Request:

```json
{
  "kind": "ns_retained_physical",
  "K": 2,
  "nu": 0.005,
  "dt": 0.0025,
  "horizon": 2,
  "point": [1.2, 0.7, 2.1],
  "readout": "velocity"
}
```

`time` may be supplied instead of `horizon`, but it must satisfy

\[
T = n\,\Delta t
\]

for an integer \(n\), because this API does not silently change the declared RK4 recurrence.

A component may be requested with `"component": "x"`, `"y"`, or `"z"`.

## Readout equation

For the finite Fourier state,

\[
\boxed{
 u(x^\*,T)=\sum_{k\in K_M}\widehat u_k(T)e^{ik\cdot x^\*}.
}
\]

This equation has a nonzero terminal coefficient for every Fourier mode in the retained cube. Therefore the exact terminal relevance set is

\[
\boxed{S_T=K_M}.
\]

Consequently the exact Retained Readout Pullback is already dense at the terminal layer:

\[
\boxed{
\text{readout density}=1.
}
\]

The API therefore reports

```text
compression_status = DENSE_READOUT_FULL_RK4
backend = portable_full_rk4
structural_work_reduction = 1.0
```

rather than pretending that pointwise velocity is an accelerated retained query.

## Why this negative result matters

The retained-fold architecture does not assert that every low-dimensional answer has a low-dimensional causal support. A three-number answer such as velocity at one point can still depend on the whole Fourier state.

Thus

\[
\dim Q=3
\not\Rightarrow
|S_T|\ll |K_M|.
\]

This is the physical-space counterpart of the all-future observability result in the Navier–Stokes reproduction work: readout dimensionality and state/relevance dimensionality are different objects.

## Claim scope

This kind is `finite_diagnostic` only. It computes the exact physical readout of the declared finite RK4 recurrence up to floating-point arithmetic. It does not claim continuum Navier–Stokes regularity, exact-in-time integration, or a speedup for dense point-velocity readouts.

A future approximate/band-limited physical kind must carry an explicit truncation/tolerance bound and must not reuse the exact claim of this endpoint.
