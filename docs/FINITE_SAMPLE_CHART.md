# Finite sample-chart leading-term certificate

This note records a reusable finite-dimensional observation fact used by the Navier--Stokes EPSC measurement lane.

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

The implementation is `idm/finite_sample_chart.py`. It certifies only the exact finite leading coefficient and fails closed when the jet determinant vanishes or sample nodes repeat. It does not invent an explicit `eta`, conditioning bound, noise tolerance or branch certificate.

For the current fixed-`N=1` Navier--Stokes shell-energy application, the channel lengths are `24,24,1`, so

\[
p=276+276=552.
\]

The domain-specific exact modular witness and analytic-flow interpretation remain owned by `morrocwi/readout-problem-navier-stokes`; this IDM module contains only the reusable finite algebra.
