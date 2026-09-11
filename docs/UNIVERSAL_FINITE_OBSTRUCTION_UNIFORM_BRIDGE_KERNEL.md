# Universal Finite Obstruction / Uniform Bridge Kernel

**Status:** shared research specification; theorem targets are OPEN unless explicitly marked otherwise  
**Date:** 2026-09-11  
**Primary role:** generic finite-first machinery for cross-domain Clay research  
**Source program:** `morrocwi/readout-problem-navier-stokes/CLAY_MULTI_PROBLEM_FINITE_BRIDGE_PROGRAM.md`

> This document does not claim any Millennium Prize Problem is solved. It isolates reusable finite mathematics that can be instantiated in Navier--Stokes, P vs NP, and other domains. A domain adapter plus a separate bridge theorem is always required before a Clay-level conclusion.

---

## 1. Mission

The shared proof architecture is

```text
finite/local object
    -> finite law / finite defect
    -> independently checkable certificate
    -> uniform theorem over the admissible finite family
    -> explicit domain bridge
    -> global / Clay statement
```

The kernel exists to prevent two invalid jumps:

```text
many finite examples  -/->  all finite objects
all finite objects     -/->  global/continuum theorem
```

These are tracked separately as the **Finite Uniformity Bridge** and the **Global Semantic Bridge**.

P2 adds a third mandatory distinction:

```text
small local/adjacent discrepancy  -/->  all-refinement Cauchy control
finite defect existence            -/->  efficient constructive capture
```

These failures are recorded in `docs/CLAY_P2_NEGATIVE_CONTROLS.md`.

---

## 2. Generic finite object

For each finite index `n`, a domain adapter should supply a record of the conceptual form

\[
\mathcal K_n=(X_n,G_n,L_n,D_n,V_n,R_{n,m},\eta_{n,m},\beta_{n,m},M_n).
\]

Interpretation:

- `X_n`: finite state / candidate space;
- `G_n`: declared symmetry or representation-equivalence action;
- `L_n`: local or finite consistency law;
- `D_n`: finite defect / obstruction function;
- `V_n`: finite verifier for a proposed defect/certificate;
- `R_{n,m}`: restriction / projection / comparison map from a refined object `m` to `n`;
- `eta_{n,m}`: certified compatibility budget;
- `beta_{n,m}`: certified newly-admitted-information / extension budget;
- `M_n`: strict certified conclusion margin.

No field is assumed to exist automatically. A domain adapter must state which fields are meaningful and which are absent.

After P2, a domain using cross-resolution control must additionally distinguish a local budget such as `eta_{n,n+1}` from an **all-refinement tail/Cauchy modulus**. The former does not imply the latter.

---

## 3. Proposal identifiers

The following identifiers are **proposal identifiers only**, not canonical Toledo equation codes.

### PROP-FUB-01 — Finite certificate kernel schema

**Tier:** Definition / program specification.

A valid finite certificate lane declares finite objects, symmetries, local laws, defects, a checker, and the evidence tier of each component.

No global conclusion follows from this definition alone.

### PROP-FUB-02 — Robust certified margin gate

**Tier:** generic finite core partly **PASS / `Th_coqc`**; domain instantiation remains separate.

Target form:

\[
M_n > E_n \Longrightarrow \mathrm{PASS},
\qquad
M_n \le E_n \Longrightarrow \mathrm{HOLD},
\]

where `E_n` is the total certified uncertainty/remainder budget.

The P1 artifact `formal/IDM_FiniteObstructionSafeCore.v` machine-checks the finite strict-margin, fail-closed, finite error-composition, finite-chain composition, invariant certificate-transport, and local-checker-soundness kernels. Dedicated Coq 8.20 CI verifies the promoted theorems are closed under the global context.

This does not supply any domain-specific error bound, witness, uniform theorem, or global bridge automatically.

### PROP-FUB-03 — Finite obstruction principle

**Tier:** OPEN; naive unrestricted form rejected by P2.

The unrestricted schema

\[
\mathsf{GlobalFailure}
\Longrightarrow
\exists n<\infty\;\exists w_n:\mathsf{FiniteWitness}(n,w_n)
\]

is false for arbitrary global properties. P2 gives the elementary counterexample `a_n=n`: global boundedness fails while every finite prefix is bounded.

A viable domain theorem must therefore expose a finite-detectability hypothesis:

\[
\boxed{
\mathsf{GlobalFailure}
+\mathsf{FiniteDetectabilityHypotheses}
\Longrightarrow
\exists n<\infty\;\exists w_n:\mathsf{VerifiedFiniteWitness}(n,w_n).
}
\]

Possible forms include a safety/separation theorem, quantitative blow-up alternative, compactness/closedness mechanism, or another domain-specific theorem proving that target failure cannot remain invisible at every finite stage.

The finite-detectability premise is load-bearing and must pass `PROP-FUB-06`; it may not merely restate the target failure in different notation.

### PROP-FUB-04 — Constructive uniform capture principle

**Tier:** OPEN; defect-existence-only form rejected in the generic black-box model by P2.

The target cannot be merely

\[
D_n(X)\ne0\Longrightarrow\mathsf{EfficientCapture}_n(X).
\]

A single hidden defect in a black-box universe of size `2^n` already shows why: a polynomial-size generic support may have exponentially small hit probability.

A viable constructive target must declare the access model and the structure used by the constructor or sampler:

\[
\boxed{
D_n(X)\ne0
+\mathsf{StructuredAccess}_n(X)
+\mathsf{ResourceBoundedConstructor}_n
\Longrightarrow
\mathsf{CaptureMargin}_n(X).
}
\]

For the P-vs-NP lane, the required margin remains of inverse-polynomial scale, for example

\[
1-q_X\ge 1/\operatorname{poly}(n),
\]

with no SAT/equivalence/MCSP oracle or hidden exponential enumeration.

This proposal is load-bearing for the P-vs-NP direct-sample lane and may have analogues in finite singularity-witness programs.

### PROP-FUB-05 — Cross-resolution compatibility / extension principle

**Tier:** OPEN generic schema; adjacent/local-only form rejected by P2.

Finite local statements may include

\[
\|R_{n,m}X_m-X_n\|\le\eta_{n,m}
\]

and

\[
\Delta_{n,m}\le\beta_{n,m}.
\]

But `eta_{n,n+1}->0` alone is not enough. Harmonic partial sums have adjacent differences tending to zero while cumulative drift is unbounded. The P1/P2 formal finite-chain kernels likewise make explicit that local budgets add along a chain and can grow without a tail bound.

A viable all-resolution target therefore needs an explicit uniform modulus, for example

\[
\boxed{
\forall\varepsilon>0\;\exists N_\varepsilon\;\forall M\ge N\ge N_\varepsilon:
\|R_{N,M}X_M-X_N\|<\varepsilon,
}
\]

or a summable extension envelope with arbitrarily small remaining tail. The exact formulation is domain-dependent.

No completed infinite object is assumed inside the finite proof core. A separate global semantic bridge must still prove what the uniform finite control implies about the target object or target theorem.

### PROP-FUB-06 — Non-vacuity / hidden-target audit

**Tier:** Definition / mandatory research gate.

For every bridge premise `A` used to imply a Clay target `T`, audit whether establishing `A` is genuinely more structured than proving `T` directly.

A bridge is placed on HOLD if it merely renames the target difficulty, hides an oracle, assumes the desired continuum regularity, or embeds an equivalent unrestricted lower bound without providing a new route to prove it.

P2 adds two explicit non-vacuity checks:

1. a finite-witness theorem must identify why the target failure is finitely detectable;
2. a constructive-capture theorem must identify the candidate access model and the resource-bounded mechanism producing non-negligible coverage.

---

## 4. Navier--Stokes adapter

**Direct active lane.**

Candidate mapping:

```text
X_n             -> finite Fourier--Galerkin state X_N
G_n             -> full declared reader/dynamics symmetry group
R_{n,m}         -> coarse projection P_N X_M
eta_{n,m}       -> cross-resolution compatibility certificate
beta_{n,m}      -> scale-extension / omitted-information certificate
D_n             -> regularity-sensitive finite obstruction
```

P2 warning: neither small adjacent cross-resolution error nor compatibility in a weak state norm is automatically a regularity theorem. A useful NS obstruction must be tied by a proved PDE argument to the regularity class required by the Clay statement.

### Load-bearing target NS-FUB-A1

\[
\boxed{
\mathsf{FiniteTimeSingularity}
\Longrightarrow
\exists N<\infty:\mathsf{CertifiedFiniteFailure}_N
}
\]

**Status:** OPEN.

The finite failure must be a PDE-relevant, regularity-sensitive obstruction, not merely sensor/readout non-identifiability or failure of one inverse chart.

A promising strengthened route is to identify a finite certificate family whose uniform success gives both:

1. an all-refinement Cauchy/tail modulus; and
2. a regularity-sensitive uniform bound or criterion strong enough, through a separate proved adapter, to yield classical regularity on the requested interval.

Only then does the contrapositive become a meaningful singularity-witness theorem.

### Load-bearing target NS-FUB-A2

\[
\boxed{
\forall N<\infty:\neg\mathsf{CertifiedFiniteFailure}_N
\Longrightarrow
\mathsf{NoFiniteTimeSingularity}
}
\]

**Status:** OPEN / bridge target.

The antecedent must be independently provable and pass PROP-FUB-06.

---

## 5. P vs NP adapter

**Direct active lane.**

For SAT and candidate circuit `C`, the existing restriction recursion gives a finite local defect interface such as

\[
\Delta_C(F,x)=
C(F)\oplus\left(C(F|_{x=0})\lor C(F|_{x=1})\right),
\]

with terminal-boundary conditions.

The existing P-vs-NP research lane already separates local defect existence from the hard problem of constructive capture.

P2 sharpens that separation: a local defect may exist while generic black-box capture is exponentially rare. Any successful constructor must exploit transparent SAT/circuit structure and certify its resource bound.

### Load-bearing target PNP-FUB-A1

For every polynomial size bound `p`, find an input length `n` such that every candidate circuit `C` with `|C|<=p(n)` admits an efficiently generated/sampled locally verifiable defect with inverse-polynomial capture margin, without SAT/equivalence/MCSP or hidden exponential enumeration.

Equivalent ADC-style target:

\[
1-q_C\ge 1/\operatorname{poly}(n).
\]

**Status:** OPEN; essentially the unrestricted circuit-lower-bound frontier.

This target must pass PROP-FUB-06: the constructor may not hide the target hardness.

---

## 6. Candidate Yang--Mills adapter

**Status:** exploratory candidate third lane; no Clay-level adapter is established here.

Tentative mapping:

```text
finite index       -> lattice/regulator scale
G_n                -> gauge symmetry
R_{n,m}            -> refinement/coarse-graining map
eta/beta            -> scale/continuum compatibility and remainder control
margin              -> candidate uniform positive spectral-gap margin
```

Required before promotion to a direct lane:

1. precise finite regulated object;
2. exact gauge-quotient treatment;
3. scale-refinement maps;
4. finite spectral-gap certificate;
5. all-refinement Cauchy/tail control rather than adjacent refinement agreement only;
6. uniform positive lower-gap theorem candidate;
7. explicit continuum Yang--Mills bridge.

A nonzero finite-lattice numerical gap is not a Clay mass-gap theorem.

---

## 7. Probe adapters

The following are adversarial probes of the generic kernel, not direct Clay claims.

### Riemann Hypothesis

Ask whether an off-critical zero would imply a finite, certifiably detectable obstruction and whether any all-height propagation principle exists. Finite-height zero checks alone are insufficient.

### Birch--Swinnerton--Dyer

Treat arithmetic and analytic invariants as independent readouts and ask whether a generic finite bridge can force equality. Agreement on computed curves is insufficient.

### Hodge Conjecture

Ask whether non-representability or representability admits a finite obstruction/witness architecture with a universal bridge. No such bridge is currently established in this program.

---

## 8. Research order

1. Audit existing finite lemmas and counterexamples. **P0 completed.**
2. Formalize the smallest sound version of PROP-FUB-01/02/06. **P1 safe finite core completed at machine-checked tier.**
3. Stress-test the abstractions on both NS and P vs NP.
4. Search aggressively for counterexamples to PROP-FUB-03/04/05 before proving stronger versions. **P2 active; naive forms narrowed by explicit controls.**
5. Isolate one load-bearing domain lemma per direct lane: NS-FUB-A1/A2 and PNP-FUB-A1.
6. Only after the shared kernel survives both lanes, build a precise Yang--Mills adapter.
7. Use RH/BSD/Hodge as negative/positive transfer probes, not as narrative analogies.

---

## 9. Claim discipline

Use only:

- `PASS` — executable finite verification passed;
- `DERIVED` — proved from declared assumptions;
- `OPEN` — theorem not proved;
- `HOLD` — evidence/assumptions insufficient;
- `REFUTED` — a precisely stated candidate implication has a valid counterexample in its declared model.

Every Clay-level implication requires all of:

```text
domain theorem
+ uniform theorem
+ explicit bridge theorem
+ target-statement verification
```

If any link is missing, Clay status remains OPEN.

A counterexample to a naive generic schema narrows the programme; it does not refute a strengthened domain theorem with additional hypotheses.

---

## 10. Formal evidence and current backlog

### P1 safe finite core — PASS / `Th_coqc`

`formal/IDM_FiniteObstructionSafeCore.v` contains machine-checked finite kernels for:

1. strict-margin PASS soundness/completeness;
2. fail-closed HOLD behavior when a certificate or strict margin is absent;
3. finite error-budget monotonicity and additive composition;
4. finite compatibility-budget composition across a finite chain;
5. certificate transport under an explicitly declared verifier-invariance hypothesis;
6. local finite-defect checker soundness under an explicitly declared checker-soundness hypothesis.

See `docs/CLAY_P1_SAFE_CORE_FORMAL.md`.

### P2 negative controls — evidence tracked separately

`formal/IDM_FiniteObstructionNegativeControls.v` and `research/clay_bridge/negative_controls.py` test why the missing hypotheses above are necessary and why naive FUB-03/04/05 forms are too broad. See `docs/CLAY_P2_NEGATIVE_CONTROLS.md`.

### Remaining load-bearing OPEN work

- strengthened `PROP-FUB-03`: prove finite detectability in a concrete domain;
- strengthened `PROP-FUB-04`: construct efficient structure-aware capture, especially for PNP;
- strengthened `PROP-FUB-05`: prove a true all-refinement Cauchy/tail modulus in a concrete domain;
- `NS-FUB-A1/A2`;
- `PNP-FUB-A1`.
