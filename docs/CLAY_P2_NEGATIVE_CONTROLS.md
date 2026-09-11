# Clay P2 — Adversarial Negative Controls for Finite Bridges

**Date:** 2026-09-11  
**Status:** candidate P2 evidence until dedicated CI passes  
**Tracker:** `morrocwi/information-discrete-math#126`  
**Scope:** falsify over-broad versions of `PROP-FUB-03/04/05`; do not promote any Clay conclusion.

P1 established a machine-checked safe finite composition core. P2 asks a different question: which tempting global bridge statements are false without extra hypotheses?

The answer is already nontrivial. Three naive bridge patterns fail.

---

## 1. Naive FUB-03 fails: global failure need not have a finite-prefix violation

Consider the sequence

\[
a_n=n.
\]

Define the global target property

\[
\mathsf{Bounded}(a):\iff \exists B\;\forall n\;a_n\le B.
\]

It fails. For any proposed `B`, the explicit index `B+1` violates the bound.

But every finite prefix passes the corresponding finite property:

\[
\forall N\;\exists B_N\;\forall n\le N:\ a_n\le B_N,
\]

simply with `B_N=N`.

Therefore the unrestricted schema

```text
GlobalFailure
  -> some natural finite-prefix failure
```

is false in general.

The Coq artifact `formal/IDM_FiniteObstructionNegativeControls.v` encodes this example through:

- `every_finite_prefix_bounded`;
- `rising_not_globally_bounded`;
- `finite_prefixes_do_not_force_global_boundedness`.

### Required repair to PROP-FUB-03

A useful finite-obstruction theorem must carry a **finite-detectability hypothesis** specific to the target property. Depending on the domain this may be a safety property, finite separation theorem, compactness/closedness mechanism, quantitative blow-up alternative, or another explicit theorem showing that target failure cannot remain invisible at every finite stage.

Thus the strengthened research shape is not

\[
\mathsf{GlobalFailure}\Rightarrow\exists\mathsf{FiniteWitness}
\]

for arbitrary global properties, but rather

\[
\boxed{
\mathsf{GlobalFailure}
+\mathsf{FiniteDetectabilityHypotheses}
\Longrightarrow
\exists n,w_n:\mathsf{VerifiedFiniteWitness}(n,w_n).
}
\]

The finite-detectability premise itself is load-bearing and must pass the non-vacuity audit.

---

## 2. Naive FUB-05 fails: small adjacent discrepancies do not imply a global compatible limit

Take harmonic partial sums

\[
H_n=\sum_{k=1}^n\frac1k.
\]

The adjacent discrepancy tends to zero:

\[
H_n-H_{n-1}=\frac1n\to0.
\]

Nevertheless the cumulative drift is unbounded. At dyadic indices,

\[
H_{2^m}\ge 1+\frac m2,
\]

because each block

\[
2^{j-1}<k\le2^j
\]

contains `2^{j-1}` terms, each at least `1/2^j`, so each block contributes at least `1/2`.

The exact Python control `research/clay_bridge/negative_controls.py` verifies these inequalities with rational arithmetic at finite dyadic scales.

A simpler fully formal finite control is also included: unit local error budgets compose to an arbitrarily large chain budget. The Coq theorems

- `unit_step_chain_sum`;
- `local_step_bounds_do_not_give_uniform_chain_bound`

show that local bounds alone do not provide a chain-length-independent global bound.

### Required repair to PROP-FUB-05

It is not enough to know only

\[
\eta_{N,N+1}\to0.
\]

A serious all-resolution bridge needs an explicitly uniform tail statement, for example a Cauchy modulus

\[
\boxed{
\forall\varepsilon>0\;\exists N_\varepsilon\;\forall M\ge N\ge N_\varepsilon:
 d(R_{N,M}X_M,X_N)<\varepsilon,
}
\]

or a summable envelope whose remaining tail can be made arbitrarily small:

\[
\sum_{k\ge N}\eta_k\to0.
\]

The exact form is domain-dependent, but **adjacent error going to zero is insufficient**.

---

## 3. Naive FUB-04 fails: defect existence does not imply efficient generic capture

Consider a black-box witness universe of size

\[
M=2^n
\]

with exactly one defect location.

Any deterministic support containing only `k<M` queried points leaves at least one possible defect location unseen. Under a uniform random hidden defect, the capture probability of a fixed `k`-point support is at most

\[
\frac{k}{2^n}.
\]

For polynomial `k=\operatorname{poly}(n)`, this can be exponentially small rather than inverse-polynomial.

`research/clay_bridge/negative_controls.py` constructs an unseen defect for finite black-box universes and checks an exact rational calibration at `n=40`, `k=n^3`.

### Interpretation boundary

This is **not** a circuit lower bound and does not rule out a structure-aware SAT/circuit refuter. Its role is narrower and important: a generic theorem cannot infer efficient capture merely from the proposition “a defect exists.”

### Required repair to PROP-FUB-04

Any constructive-capture theorem must specify at least:

1. the access model to the candidate and defect landscape;
2. the exploitable structure producing the support/distribution;
3. the time/size/sampling resource bound;
4. the certified hit probability or deterministic coverage guarantee;
5. a guard against hidden SAT/equivalence/MCSP or exhaustive search.

A useful form therefore looks like

\[
\boxed{
D_n(X)\ne0
+\mathsf{StructuredAccess}(X)
+\mathsf{PolynomialConstructor}
\Longrightarrow
1-q_X\ge 1/\operatorname{poly}(n).
}
\]

The structure and constructor are the hard content, not bookkeeping.

---

## 4. Two P1 assumptions are necessary, not cosmetic

### 4.1 Symmetry transport needs verifier invariance

P1 proved certificate transport only under an explicit invariant-verifier hypothesis. P2 supplies a two-state counterexample:

```text
state = bool
symmetry action = flip
verifier = accept only false
```

The verifier passes at `false` and fails after the symmetry sends it to `true`.

Coq theorem: `transport_can_fail_without_invariance`.

Therefore quotient/symmetry transport must never omit the invariance premise.

### 4.2 Local defect acceptance needs checker soundness

Take a verifier that always returns `true` while the declared defect predicate is always false.

Coq theorem: `checker_can_accept_without_soundness`.

Therefore an accepted certificate has no semantic force unless checker soundness is separately proved.

---

## 5. Consequence for the Navier--Stokes lane

P2 rules out a particularly tempting weak route:

```text
small adjacent finite-resolution discrepancy
  -> global regularity
```

That implication is unsupported. Even a genuine all-scale compatibility theorem in a weak norm is not automatically a regularity theorem.

For `NS-FUB-A1`, the finite failure class therefore has to be **regularity-sensitive**. The programme should search for a finite certificate family whose uniform exclusion yields a norm/criterion strong enough to force the required classical regularity, rather than relying on energy or weak-state compatibility alone.

A candidate structural target is:

```text
uniform regularity-sensitive finite bound
+ all-refinement Cauchy modulus
+ certified finite-to-target adapter
    -> classical regularity on the requested time interval.
```

Only after such an implication is proved does its contrapositive become a meaningful finite singularity-witness theorem.

This section is a research-direction consequence, not a proved `NS-FUB-A1` theorem.

---

## 6. Consequence for the P-vs-NP lane

P2 sharpens the meaning of `PNP-FUB-A1`:

```text
wrong circuit has a local defect
```

is not enough. The missing theorem must exploit transparent circuit/SAT structure to construct or sample a defect with polynomial resources and inverse-polynomial margin.

The black-box control explains why the resource/access model cannot be omitted. It does not weaken the already established finite restriction-defect interface; it isolates the true quantified breakthrough more cleanly.

---

## 7. P2 status matrix

| Naive statement | P2 status | Required repair |
|---|---|---|
| arbitrary global failure always yields a finite-prefix failure | **REFUTED candidate**, pending Coq CI promotion | finite-detectability/domain hypothesis |
| adjacent compatibility error tending to zero yields a global compatible object | **REFUTED candidate**, analytic + exact finite control pending CI | Cauchy modulus / summable tail / equivalent uniform control |
| existence of a defect yields efficient generic black-box capture | **REFUTED candidate in black-box model**, exact finite control pending CI | structured access + constructive resource bound + hit margin |
| PASS transports across symmetry without verifier invariance | **REFUTED candidate**, pending Coq CI promotion | explicit invariance |
| checker acceptance implies a true defect without checker soundness | **REFUTED candidate**, pending Coq CI promotion | explicit checker soundness |

No strengthened `PROP-FUB-03/04/05` theorem is proved here. Their status remains OPEN after narrowing.

---

## 8. Promotion gate

P2 evidence is promoted only if:

1. `formal/verify_clay_negative_controls.sh` compiles the Coq controls under 8.20 and every promoted theorem is closed under the global context;
2. `research/clay_bridge/negative_controls.py` passes using exact rational/integer finite checks;
3. the Clay governance acknowledgement records the status narrowing;
4. Toledo receives provenance/status notes but no Clay proposal is promoted to solved.
