# `ns_retained_harmonic_probe`

A real physical-space harmonic measurement with exact two-mode terminal support.

## Reader

\[
Q(T)=\frac1{(2\pi)^3}\int_{[0,2\pi]^3}u(x,T)\cos(k_0\cdot x+\phi)\,dx.
\]

For a real periodic velocity field,

\[
\boxed{
Q(T)=\frac12\left(\hat u_{-k_0}e^{i\phi}+\hat u_{k_0}e^{-i\phi}\right)
}
\]

so the terminal readout uses exactly the conjugate pair `+/-k0`.

The solver pulls those two modes backward through the exact Navier-Stokes triad graph and classical RK4 DAG. No learned closure is used.

## API

```json
{
  "kind": "ns_retained_harmonic_probe",
  "K": 3,
  "nu": 0.005,
  "dt": 0.0025,
  "horizon": 1,
  "wavevector": [3, 3, 3],
  "phase": 0.3,
  "verify": true
}
```

The default wavevector is `[K,K,K]`. Corner wavevectors are useful because their exact backward triad cone is smaller than an axis-aligned real probe on the tested cubes.

The response reports terminal support, exact RK4 cone sizes, structural work reduction, retained/full verification, and the imaginary residual of the real measurement.

## Claim boundary

`finite_diagnostic`; task-exact only relative to the same fixed finite Fourier-Galerkin RK4 recurrence. Runtime acceleration is benchmarked separately in `morrocwi/readout-problem-navier-stokes`.
