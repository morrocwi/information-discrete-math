# Finite branch-conditioned measurement inverse

Status: reusable finite-first certificate primitive.

This layer begins **after** a finite local observation chart and a common inverse branch have been certified. It deliberately contains no continuum object and does not assume a completed infinite state.

Let

\[
H:B\subset\mathbb R^d\to\mathbb R^d
\]

be a finite chart on a certified convex branch `B`, let `A` be a fixed rational preconditioner, and let `J(B)` be a valid interval enclosure of `DH` on that branch. If

\[
q:=\sup_{x\in B}\|I-A DH(x)\|_\infty<1,
\]

then

\[
\|x-z\|_\infty
\le
\frac{\|A\|_\infty}{1-q}
\|H(x)-H(z)\|_\infty
\qquad(x,z\in B).
\]

If measured chart data `y` satisfies

\[
\|y-H(x)\|_\infty\le\sigma
\]

and a candidate `z` satisfies

\[
\|H(z)-y\|_\infty\le\tau,
\]

then

\[
\boxed{
\|x-z\|_\infty
\le
\frac{\|A\|_\infty}{1-q}(\sigma+\tau).
}
\]

`idm/finite_measurement_inverse.py` implements this as `certified_branch_chart_state_radius`. It returns `HOLD` unless both of the following are explicit:

1. the common branch has independently been certified, and
2. the exact finite interval inverse gate proves `q<1`.

The module does **not** infer a branch from the observations, convert raw time-series samples into a chosen high-order chart, or attach an omitted-tail/continuum certificate. Those are separate adapters.

## Navier--Stokes application boundary

The current NS application has a fixed-`N=1` 49-dimensional symmetry-fixed shell-energy chart with a reproduced `10^-17` branch box and `q_1<1`. The NS repository specializes this generic helper to propagate uncertainty in that selected scaled chart into a retained-state radius. Raw finite-window/sample -> chart uncertainty plus branch capture remains open there.

This separation is intentional:

```text
raw finite samples/windows
    -> chart uncertainty + branch certificate        [domain-specific, may be OPEN]
    -> finite branch-conditioned state radius         [this IDM primitive]
    -> optional omitted-tail / continuum adapter      [separate]
```

The finite-native core is therefore valid independently of whether a continuum interpretation is later requested.
