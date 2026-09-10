# Observable-to-Continuum Certificate

Status: **analytic composition rule plus finite helper implementation**. The quantitative inversion from energy Lie jets to a certified retained-state radius remains open.

## 1. Two different completeness questions

For a Fourier cutoff `P_N`, finite energy observability and discrete epsilon-completion answer different questions.

- **Inner completeness:** do the declared finite observations identify the retained finite state, modulo unavoidable symmetry?
- **Outer completeness:** how large can the omitted component `(I-P_N)u` still be?

The NS energy-observability programme addresses the first question. EPSC addresses the second. They are complementary, not interchangeable.

## 2. Finite structural observability

For the declared cubic Fourier-Galerkin state,

\[
d_N=2((2N+1)^3-1).
\]

For total energy `E`, the Lie-jet rank satisfies

\[
\operatorname{rank}D\mathcal E_R\le\min(R+1,d_N-3),
\qquad
R_E^{\min}=d_N-4.
\]

For the full shell-energy reader `I in R^{m_N}`,

\[
\operatorname{rank}D\mathcal J_R
\le
\min(m_N+(m_N-1)R,d_N-3),
\]

\[
R_I^{\min}
=
\left\lceil\frac{d_N-3-m_N}{m_N-1}\right\rceil.
\]

Exact modular certificates in the NS repository attain the translation ceiling at the earliest structurally allowed order in four recorded cases:

```text
N=1  total energy   R=48   rank=49
N=1  shell energy   R=23   rank=49
N=2  total energy   R=244  rank=245
N=3  shell energy   R=39   rank=681
```

This yields local finite-state completeness modulo spatial translations at generic free-action states in those certified cases. It does **not** give a quantitative reconstruction radius.

## 3. Orthogonal composition theorem

Assume a finite observation/inversion layer supplies a reconstructed retained state `x_hat_N` and a certified quotient-state radius

\[
\inf_{g\in G}\|P_Nu(T)-g\widehat x_N\|_2\le\rho_N,
\]

where `G` is an isometric symmetry group preserving the cutoff. Assume independently that EPSC supplies

\[
\|(I-P_N)u(T)\|_2\le\beta_N.
\]

Because the retained and omitted Fourier components are orthogonal,

\[
\boxed{
\inf_{g\in G}\|u(T)-g\widehat x_N\|_2
\le
\sqrt{\rho_N^2+\beta_N^2}.
}
\]

This is the registered `PROP-EPSC-17` observable-to-continuum composition rule.

The corresponding fail-closed tolerance test is

\[
\sqrt{\rho_N^2+\beta_N^2}\le\varepsilon.
\]

If either `rho_N` or `beta_N` lacks a proof/certificate, the verdict is `HOLD`.

## 4. Why rank saturation is not enough

A full quotient rank establishes local differential identifiability. It does not automatically provide:

- a constructive inverse;
- a certified neighborhood on which the inverse branch is unique;
- a condition-number bound;
- robustness to noisy energy samples or numerical differentiation;
- a certified `rho_N`.

Therefore the next inner-side frontier is `PROP-EPSC-18`: produce a certified energy-jet inversion radius. The practical noisy version is `PROP-EPSC-19`.

## 5. Relation to EPSC-15 and EPSC-16

`PROP-EPSC-15` and `PROP-EPSC-16` are not observability problems.

- `PROP-EPSC-15` supplies one exact finite-tape-to-comparison-path enclosure construction.
- `PROP-EPSC-16` asks how to make that path certificate tight and scalable at larger cutoff/horizon.
- `PROP-EPSC-18` asks how to reconstruct the retained finite state from compressed energy observations with a certified radius.
- `PROP-EPSC-19` asks how to propagate measurement/noise uncertainty through that inverse and then through EPSC.

The larger programme is therefore

```text
energy measurements
    -> certified finite reconstruction radius rho_N      [inner side]
    -> retained Fourier state / comparison path
    -> certified omitted-tail radius beta_N              [outer side]
    -> sqrt(rho_N^2 + beta_N^2)
    -> continuum tolerance verdict
```

## 6. Implementation

`idm/ns_observable_to_continuum.py` provides:

- finite dimension and shell-count bookkeeping;
- structural scalar/shell depth ceilings;
- orthogonal `sqrt(rho^2+beta^2)` composition;
- a fail-closed certificate gate.

It intentionally does not pretend to solve the open inverse problem. Supplying a rank value where a certified `rho_N` is required is not accepted.

## 7. Claim boundary

This bridge does not prove the all-resolution observability conjecture, global injectivity of energy jets, stable recovery from noisy high-order derivatives, physical sensor realizability, global regularity of three-dimensional Navier-Stokes, or the Clay Millennium problem.
