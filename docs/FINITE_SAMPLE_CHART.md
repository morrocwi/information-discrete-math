# Finite sample-chart leading-term and conditioning certificates

This note records reusable finite-dimensional observation facts used by the Navier--Stokes EPSC measurement lane.

Suppose a finite analytic observation channel has

\[
y_s(ht,x)=\sum_{n\ge0}a_{s,n}(x)(ht)^n.
\]

Assume a square local jet chart is built by taking, for each channel `s`, the contiguous Taylor rows

\[
D a_{s,0},\ldots,D a_{s,r_s}.
\]

Now sample channel `s` at `r_s+1` distinct finite nodes `t_{s,0},...,t_{s,r_s}`. The corresponding sample Jacobian determinant has its first possible nonzero term at

\[
p=\sum_s\frac{r_s(r_s+1)}2,
\]

and the coefficient of `h^p` is

\[
\boxed{
\det J_{\rm jet}\prod_s\det V_s,
\qquad
(V_s)_{jn}=t_{s,j}^n.
}
\]

Therefore, if the declared jet determinant is nonzero and the sample nodes are distinct in every channel, the leading coefficient is nonzero. Once analyticity of the underlying finite flow/output is independently justified, there exists `eta>0` such that every sufficiently small nonzero `|h|<eta` gives a locally invertible sample-time chart.

## Exact conditioning of sample -> Taylor -> scaled chart

Structural invertibility does not imply useful conditioning. For one channel with `m` distinct nodes, write

\[
V_{jn}=t_j^n,
\qquad
D_h=\operatorname{diag}(1,h,\ldots,h^{m-1}),
\qquad
S=\operatorname{diag}(s_0,\ldots,s_{m-1}).
\]

For a degree-`m-1` polynomial or truncated Taylor model, samples satisfy

\[
y=V D_h a,
\]

so reconstructing the declared scaled coefficients `z=Sa` gives

\[
\boxed{z=S D_h^{-1}V^{-1}y.}
\]

The exact induced infinity norm of this reconstruction operator is therefore

\[
\boxed{
\kappa_\infty(h)
=
\left\|S D_h^{-1}V^{-1}\right\|_\infty
=
\max_n |s_n|\,|h|^{-n}\sum_j |(V^{-1})_{nj}|.
}
\]

Hence if the sample-space measurement error obeys `||e||_inf<=sigma`, then

\[
\|\delta z\|_\infty\le\kappa_\infty(h)\,\sigma.
\]

If the true analytic observation is not exactly the truncated polynomial and a separately certified sample-space remainder radius `r_sample` is available, then the same finite linear map yields

\[
\|\delta z\|_\infty
\le
\kappa_\infty(h)(\sigma+r_{\rm sample}).
\]

This formula makes an important distinction explicit. Taking `h` very small can guarantee structural sample-chart invertibility while simultaneously making recovery of high-order Taylor rows numerically and statistically ill-conditioned because of the factor `|h|^{-n}`. That does **not** imply the direct sample map itself is unusable; it says that reconstructing a high-order Taylor/derivative chart as an intermediate representation can be a poor measurement interface. A direct sample-map inverse can have very different conditioning and must be certified separately.

The implementation is `idm/finite_sample_chart.py`. It now supplies exact rational Vandermonde inversion and exact `kappa_inf` for the finite interpolation operator. It still does not invent an explicit analyticity radius, flow remainder, branch certificate, direct sample-map inverse, sensor model or continuum adapter.

For the current fixed-`N=1` Navier--Stokes shell-energy application, the channel lengths are `24,24,1`, so

\[
p=276+276=552.
\]

The domain-specific exact modular witness, the row scaling used by that application, and its conditioning diagnostics remain owned by `morrocwi/readout-problem-navier-stokes`; this IDM module contains only reusable finite algebra.
