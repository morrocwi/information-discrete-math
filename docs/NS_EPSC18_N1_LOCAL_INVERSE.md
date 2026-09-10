# EPSC-18 milestone: full N=1 local inverse existence on a finite symmetry slice

Status: `finite_diagnostic + Dr`; practical quantitative radius remains `Open`.

This note records the reusable mathematical meaning of the Navier-Stokes `N=1` witness without importing continuum ontology into IDM.

## Finite-first statement

The native object is a finite observation map

\[
H_1:X_1\to\mathbb R^{72},
\]

where `X_1` is the 52-real-dimensional finite Fourier-Galerkin state and the 72 candidate outputs are the three shell-energy Taylor coefficients through order 23.

Spatial translations generate a three-dimensional symmetry tangent. The Navier-Stokes reproduction checker constructs, at one exact rational witness,

- a `52 x 3` translation-tangent matrix `G`;
- three coordinate gauges whose restriction to `G` is invertible;
- the resulting 49-dimensional finite coordinate slice;
- 49 observation coordinates whose `49 x 49` Jacobian minor has nonzero reduction modulo a good prime.

Because the finite map is rational and the prime does not divide any declared denominator, the nonzero modular minor certifies a nonzero characteristic-zero rational minor. Hence the finite-dimensional inverse-function theorem gives a local real inverse on the selected symmetry slice.

The important logical form is

\[
\boxed{
\text{finite state}
\to
\text{finite symmetry quotient chart}
\to
\text{finite observation minor}
\to
\det J\ne0
\to
\text{local finite inverse}.
}
\]

No object `X_infinity` is assumed or needed.

## What this closes

It closes the **local-existence** subproblem of `PROP-EPSC-18` for the complete `N=1` quotient chart: a full 49-dimensional symmetry-fixed local energy-jet inverse exists at an explicit finite witness.

It does not yet provide a measurement-ready radius `rho_1`.

## Remaining quantitative obligation

The reusable sufficient condition remains the preconditioned finite-box bound

\[
\sup_{x\in B}\|I-A D H(x)\|\le q<1.
\]

When the symmetry slice and common branch are independently certified, this yields

\[
\|x-z\|
\le
\frac{\|A\|}{1-q}\|H(x)-H(z)\|.
\]

IDM implements this fail-closed rule in `idm/certified_local_inverse.py`. The next Navier-Stokes task is therefore concrete: construct a directed-rounding interval/Krawczyk enclosure for the selected 49-dimensional chart and make `q<1` on a useful finite box.

Until that is done, the finite-native pipeline is

\[
\text{measurement}\to\text{local branch candidate}\to\texttt{HOLD}
\]

whenever a certified quantitative radius is requested.

## Relation to EPSC-17

Only after a certified retained radius `rho_1` exists may one optionally invoke an external continuum/tail adapter `beta_1` and use the orthogonal composition

\[
\sqrt{\rho_1^2+\beta_1^2}.
\]

That adapter is a separate layer. The finite-native inverse result does not depend on a completed infinite Fourier state.

## Source ownership

The exact `N=1` Galerkin/Taylor witness and reproduction evidence belong to `morrocwi/readout-problem-navier-stokes`. IDM owns the general finite inverse/certification pattern and fail-closed implementation.
