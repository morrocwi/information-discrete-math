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

---

## 3. Proposal identifiers

The following identifiers are **proposal identifiers only**, not canonical Toledo equation codes.

### PROP-FUB-01 — Finite certificate kernel schema

**Tier:** Definition / program specification.

A valid finite certificate lane declares finite objects, symmetries, local laws, defects, a checker, and the evidence tier of each component.

No global conclusion follows from this definition alone.

### PROP-FUB-02 — Robust certified margin gate

**Tier:** generic target, with domain-specific finite instances already present elsewhere.

Target form:

\[
M_n > E_n \Longrightarrow \mathrm{PASS},
\qquad
M_n \le E_n \Longrightarrow \mathrm{HOLD},
\]

where `E_n` is the total certified uncertainty/remainder budget.

The generic theorem must make all composition assumptions explicit; no numerical evidence may be silently promoted to a theorem.

### PROP-FUB-03 — Finite obstruction principle

**Tier:** OPEN.

Target schema:

\[
\mathsf{GlobalFailure}
\Longrightarrow
\exists n<\infty\;\exists w_n:\mathsf{FiniteWitness}(n,w_n).
\]

This is not expected to hold without domain hypotheses. The research task is to identify minimal sufficient hypotheses and counterexamples.

### PROP-FUB-04 — Constructive uniform capture principle

**Tier:** OPEN.

Target schema:

\[
\forall X\in\mathcal C_n,
\quad
D_n(X)\ne0
\Longrightarrow
\mathsf{Capture}_n(X)
\]

with an explicit resource bound on constructing or sampling a verifiable witness.

This proposal is load-bearing for the P-vs-NP direct-sample lane and may have analogues in finite singularity-witness programs.

### PROP-FUB-05 — Cross-resolution compatibility / extension principle

**Tier:** OPEN generic schema.

Target finite statements:

\[
\|R_{n,m}X_m-X_n\|\le\eta_{n,m}
\]

and

\[
\Delta_{n,m}\le\beta_{n,m},
\]

with constructive control strong enough for arbitrary requested finite tolerance.

No completed infinite object is assumed inside the finite proof core.

### PROP-FUB-06 — Non-vacuity / hidden-target audit

**Tier:** Definition / mandatory research gate.

For every bridge premise `A` used to imply a Clay target `T`, audit whether establishing `A` is genuinely more structured than proving `T` directly.

A bridge is placed on HOLD if it merely renames the target difficulty, hides an oracle, assumes the desired continuum regularity, or embeds an equivalent unrestricted lower bound without providing a new route to prove it.

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

### Load-bearing target NS-FUB-A1

\[
\boxed{
\mathsf{FiniteTimeSingularity}
\Longrightarrow
\exists N<\infty:\mathsf{CertifiedFiniteFailure}_N
}
\]

**Status:** OPEN.

The finite failure must be a PDE-relevant obstruction, not merely sensor/readout non-identifiability.

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
5. uniform positive lower-gap theorem candidate;
6. explicit continuum Yang--Mills bridge.

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

1. Audit existing finite lemmas and counterexamples.
2. Formalize the smallest sound version of PROP-FUB-01/02/06.
3. Stress-test the abstractions on both NS and P vs NP.
4. Search aggressively for counterexamples to PROP-FUB-03/04/05 before proving stronger versions.
5. Isolate one load-bearing domain lemma per direct lane: NS-FUB-A1/A2 and PNP-FUB-A1.
6. Only after the shared kernel survives both lanes, build a precise Yang--Mills adapter.
7. Use RH/BSD/Hodge as negative/positive transfer probes, not as narrative analogies.

---

## 9. Claim discipline

Use only:

- `PASS` — executable finite verification passed;
- `DERIVED` — proved from declared assumptions;
- `OPEN` — theorem not proved;
- `HOLD` — evidence/assumptions insufficient.

Every Clay-level implication requires all of:

```text
domain theorem
+ uniform theorem
+ explicit bridge theorem
+ target-statement verification
```

If any link is missing, Clay status remains OPEN.

---

## 10. Immediate formalization backlog

The first formal artifact should be deliberately modest. It should encode finite records and prove only composition/logic lemmas that do not presuppose a Clay theorem, for example:

1. strict-margin soundness;
2. error-budget monotonicity;
3. quotient-respecting certificate transport;
4. finite local-defect checker soundness under declared laws;
5. finite compatibility-budget composition across a chain of resolutions;
6. explicit `HOLD` behavior when a premise is absent.

`PROP-FUB-03`, `PROP-FUB-04`, and domain Clay bridges remain OPEN until separately proved.
