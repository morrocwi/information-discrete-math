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

## 3. Quantitative certificate: finite dual mass

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

## 5. Critical asymptotic fence: a fixed global dual cannot be the final theorem

The exact finite dual is useful, but the branch already contains the stronger no-go in `FUSION_DUAL_RESISTANCE.md`: for the general non-monotone fusion setting, a **single fixed distribution / fractional dual** has only linear asymptotic power. In normalized form,

\[
\frac{1}{\sup_p\operatorname{kill}_{\mu}(p)}\le 8n+8.
\]

Therefore the programme

\[
\text{one target-only global dual }y^{(n)}
\quad\Longrightarrow\quad
\text{superpolynomial circuit lower bound}
\]

is not the correct unrestricted route. The finite dual remains a regression/certificate tool, but its fixed-distribution objective cannot be promoted into the missing SAT theorem.

This is important for the EPSC analogy: the quantitative certificate must be attached to the **actual admissible branch / candidate object**, not frozen globally in advance.

## 6. Correct imported quantitative target: candidate-adaptive certificate

After a candidate circuit `C` is exposed, let `Gamma_C` be the actual fusion/semantic-generation rules induced by that circuit. The candidate-adaptive analogue is to construct

\[
\mu_C
\]

from the declared circuit DAG / lineage, without a SAT oracle or equivalence oracle, such that

\[
\boxed{
\forall p\in\Gamma_C:
\operatorname{kill}_{\mu_C}(p)<\frac1{|\Gamma_C|}.
}
\]

Then the union bound gives positive probability that a semi-filter survives every rule in `Gamma_C`; hence the candidate family is not a cover.

In dual language, instead of one global feasible vector against **all** rules, we seek a candidate-conditioned certificate whose load is small against the rules that the exposed circuit actually generated.

The EPSC-style pattern is now:

```text
candidate circuit C declared
        -> structural lineage / projection gate
        -> construct candidate-specific certificate mu_C
        -> certify all local loads on Gamma_C
        -> derive a surviving semantic obstruction
        -> otherwise HOLD
```

This is directly analogous to using a separately certified finite branch before applying the quantitative inverse inequality.

## 7. Remaining load-bearing theorem

The preferred frontier is therefore an **Adaptive Lineage Readout Adversary** / **Adaptive Semantic Generation Adversary**:

\[
C\longmapsto \mu_C
\]

constructed transparently from `C` such that, for every polynomial-size incorrect candidate family in the target SAT sequence,

\[
\max_{p\in\Gamma_C}\operatorname{kill}_{\mu_C}(p)<1/|\Gamma_C|.
\]

The construction must satisfy all of the following:

1. use the existentially projected target, not pre-projection witness diversity;
2. use actual candidate lineage / sharing information;
3. not call SAT, target equivalence, minimum circuit size, or a known survivor oracle;
4. remain valid for unrestricted fanout/sharing in the declared Boolean basis;
5. provide a locally checkable quantitative certificate, with HOLD on failed gates.

This adaptive construction is **OPEN**. The current corpus does not prove `SAT notin P/poly` or `P != NP`.
