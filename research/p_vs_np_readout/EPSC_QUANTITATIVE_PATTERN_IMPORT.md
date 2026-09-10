# Direct EPSC quantitative-pattern import into the P-vs-NP readout lane

**Scope:** this note imports a quantitative certification pattern from the finite EPSC work as a mathematical template. It does not edit the EPSC/NS files and does not claim that their inverse theorem is itself a Boolean-circuit theorem.

## 1. Imported finite quantitative equation

The finite EPSC measurement-side certificate has the form

\[
q<1
\quad\Longrightarrow\quad
\rho \le \frac{\|A\|}{1-q}(\sigma+\tau),
\]

where the branch is separately certified, `q` is a finite inverse-defect bound, `A` is a declared preconditioner, `sigma` is measurement uncertainty and `tau` is forward residual. If the branch or `q<1` gate is missing, the correct state is HOLD.

We use this equation directly as a **certificate architecture**:

```text
structural admissibility gate
        -> independently checkable quantitative defect/capacity certificate
        -> numeric conclusion
        -> HOLD when a gate is missing
```

The smooth inverse objects `A`, `DH`, and `q` are not copied into Boolean complexity without a bridge.

## 2. Boolean existential-projection replacement

For SAT the declared reader is not an inverse map but existential projection

\[
f(x)=\exists_w R(x,w).
\]

Therefore the first gate is projection itself: all witness-side distinctions erased by `exists` are removed **before** complexity accounting. `IDM_ProjectionCollapseGuard.v` and `projection_collapse_guard.py` are explicit no-go guards for violating this rule.

After projection, the current exact finite obstruction is residual fusion-cover debt

\[
D_t=\operatorname{RCD}(\mathcal U_t),
\]

with one-rule capacity

\[
D_t-D_{t+1}\le 1.
\]

`IDM_ResidualCoverCapacity.v` proves the certificate-transfer kernel.

## 3. Quantitative certificate: dual mass

For a projected target, assign nonnegative adversarial weights `y_F` subject to

\[
\sum_{F\text{ hit by }p} y_F\le 1
\qquad\text{for every admissible fusion rule }p.
\]

Then every exact cover with `k` rules satisfies

\[
\boxed{\sum_F y_F\le k}.
\]

Equivalently, with a cleared-denominator budget `B`, total integer weight `Y`, and `k` rules,

\[
Y\le kB,
\qquad
k\ge \frac{Y}{B}.
\]

The arithmetic aggregation is already formalized in `IDM_FusionDual.v`; exact rational feasibility is independently rechecked by `fusion_dual_certificate.py`.

This is the circuit-lane analogue of the EPSC quantitative step in the following precise sense:

| Finite EPSC | P-vs-NP fusion lane |
|---|---|
| branch gate | existential-projection / representation guard |
| `q<1` defect certificate | per-rule dual-load `<=1` certificate |
| `||A||/(1-q)` amplification factor | reciprocal rule budget `1/B` |
| `sigma+tau` certified discrepancy | total adversarial dual mass `Y` |
| state-radius bound `rho` | minimum-rule lower bound `k >= Y/B` |
| missing gate -> HOLD | non-projected / infeasible dual -> HOLD |

This is a direct transfer of **quantitative certificate architecture**, not an identification of Jacobians with circuits.

## 4. Projection-sensitive requirement

Two relations `R_1(x,w)` and `R_2(x,w)` with the same existential projection

\[
\exists_w R_1(x,w)=\exists_w R_2(x,w)
\]

must enter the same target-side RCD/dual computation. The exact diagnostic `projection_sensitive_dual.py` enforces this pipeline.

Mandatory negative control:

\[
R_m(x,w)=[x=w]
\]

has `2^m` distinct witness slices but

\[
\exists_w R_m(x,w)\equiv 1,
\]

so its projected residual debt and dual mass are zero. Any candidate that charges the pre-projection `2^m` diversity fails the declared readout.

## 5. The remaining load-bearing theorem

The quantitative half now has a concrete exact form. What remains is not another bookkeeping identity but an **explicit projected SAT family plus dual weights** whose certified mass beats every polynomial while every admissible gate/rule has bounded load.

A sufficient target would be a family of projected SAT instances with exact certificates

\[
y^{(n)}_F\ge0,
\qquad
\sup_p\sum_{F\text{ hit by }p}y_F^{(n)}\le B_n,
\]

and

\[
\forall c\;\forall N\;\exists n\ge N:
\qquad
\frac{\sum_F y_F^{(n)}}{B_n}>n^c.
\]

If, in addition, the fusion/semantic-generation bridge applies to every unrestricted circuit gate with constant or polynomially controlled overhead, then the dual mass becomes a genuine circuit lower-bound certificate.

That final asymptotic SAT dual construction and unrestricted-gate bridge remain **OPEN**. The present corpus does not prove `SAT notin P/poly` or `P != NP`.
