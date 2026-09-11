# Finite direct-sample branch certificate

This note records the reusable finite theorem used by the Navier--Stokes EPSC measurement lane. It contains no continuum state and assumes no completed infinity.

Let

\[
S:B(z,r)\subset\mathbb R^d\to\mathbb R^d
\]

be differentiable on a convex infinity-norm ball, and let `A` be a fixed invertible preconditioner. Suppose a separate validated calculation supplies

\[
q\ge \sup_{x\in B(z,r)}\|I-A DS(x)\|_\infty,
\qquad q<1.
\]

Let `y_model` approximate `S(z)` with certified radius `tau`; let raw observed data `y_obs` have sensor radius `sigma`; and let

\[
d=\|y_{obs}-y_{model}\|_\infty,
\qquad
\delta=d+\sigma+\tau.
\]

If

\[
\boxed{\|A\|_\infty\delta+qr\le r,}
\]

then for every exact data vector `y` in the declared raw-data uncertainty box the map

\[
T_y(x)=x-A(S(x)-y)
\]

is a contraction and maps `B(z,r)` into itself. Hence Banach's fixed-point theorem gives one unique solution of `S(x)=y` inside that declared local branch. In particular,

\[
\boxed{
\|x-z\|_\infty
\le
\frac{\|A\|_\infty}{1-q}\,\delta.
}
\]

This is stronger than assuming `branch_certified=True` as an external input: the raw-data self-map inequality itself certifies existence and uniqueness *inside the local branch*. It does not rule out roots outside the branch.

The fail-closed implementation is `idm/finite_sample_branch.py`. It returns `HOLD` if `q>=1` or if the raw-data box is too large for the self-map gate. Domain-specific callers remain responsible for certifying the Jacobian defect, forward-model remainder and sensor uncertainty.

For the current Navier--Stokes application, the intended chain is

\[
\text{finite energy samples}
\to
\text{direct finite sample map}
\to
(q<1+\text{self-map gate})
\to
\rho_N.
\]

Any omitted-mode or continuum certificate is a separate outer adapter and is not a premise of this finite theorem.
