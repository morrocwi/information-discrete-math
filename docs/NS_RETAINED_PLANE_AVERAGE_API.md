# `ns_retained_plane_average`

A portable exact-slicing physical readout for the fixed finite Fourier-Galerkin Navier-Stokes RK4 recurrence.

## Reader

For a plane normal to axis `x`,

\[
\bar u(x,T)=\frac{1}{(2\pi)^2}\int_0^{2\pi}\int_0^{2\pi}u(x,y,z,T)\,dy\,dz.
\]

Fourier orthogonality removes every mode except

\[
(k_x,0,0),\qquad k_x\ne0.
\]

For cutoff `K`, the zero-mean cube contains

\[
(2K+1)^3-1
\]

modes, while the terminal reader uses exactly

\[
2K
\]

modes.  The same statement holds under coordinate permutation for `axis=y` or `axis=z`.

The retained solver pulls this sparse terminal support backward through all four RK4 stages using the exact ordered Navier-Stokes triads `p+q=k`.  No learned or phenomenological closure is introduced.

Because every terminal wavevector is parallel to the plane normal, incompressibility forces the velocity component parallel to that normal to vanish (up to floating arithmetic residual).  The two transverse components carry the nontrivial plane-averaged velocity.

## API

```json
{
  "kind": "ns_retained_plane_average",
  "K": 2,
  "nu": 0.005,
  "dt": 0.0025,
  "horizon": 1,
  "axis": "x",
  "coordinate": 0.7,
  "verify": true
}
```

`time` may be supplied instead of `horizon`, but it must be an integer multiple of `dt` so that the declared finite recurrence is not silently changed.

The response reports:

- `value`: the three-component plane-averaged velocity;
- `terminal_mode_count`: exactly `2K`;
- `readout_density`: `2K / ((2K+1)^3-1)`;
- `rk4_stage_ledger`: retained mode counts and triad work by step;
- `structural_work_reduction`: full ordered-triad work divided by retained ordered-triad work;
- `verification`: retained versus full finite-RK4 terminal readout gate;
- `imaginary_residual`: real-field reconstruction residual;
- `longitudinal_residual`: incompressibility residual along the plane normal;
- `compression_status = SPARSE_EXACT_RETAINED`.

## Claim boundary

This endpoint is `finite_diagnostic` and is task-exact only relative to the same fixed finite Fourier-Galerkin RK4 recurrence.  It is not an exact-in-time continuum Navier-Stokes solver and makes no regularity or singularity claim.

The portable IDM implementation reports structural work rather than NumPy/FFT timing speedups.  Performance claims belong to the executable benchmark in `morrocwi/readout-problem-navier-stokes`.
