# Information Discrete Mathematics & Calculus
## A Foundation from the Retained Difference — axioms, definitions, operators, theorems, principles, and a complete discrete calculus

**Developed by Yaoharee Lahtee.**

> **Edition note (v0.2 — completeness-first).** This edition prioritises **complete coverage** of
> the findings, definitions, operators, and results — from the roots up through a full *information
> discrete calculus*. **Proofs are stated by reference to the machine-checked witnesses where they
> exist and are otherwise deferred to the next version (v-proofs);** where a result is asserted
> ahead of its proof it is marked `[results-first]`. The goal here is the closed skeleton, not the
> full proof tower — the proofs come next.

> A world-class mathematical foundation built from ONE primitive — the *retained difference* — and
> carried, by definition-and-theorem, up to the number tower, discrete analysis, geometry, and the
> operator of information, with the continuum recovered as a *readout* of the discrete root. Every
> statement carries an honest tier. The machine-checked core is axiom-free over ℚ; where the
> continuum enters, it is flagged, never smuggled.

---

## How to read this book — the tier discipline (never collapse)

Every numbered result is tagged:

- **`Th_coqc`** — machine-checked in Coq, **axiom-free over ℚ** (`Print Assumptions` = *Closed under
  the global context*; a non-vacuous witness). Named witnesses point to the verified corpus.
- **`Th_coqc+classic`** — machine-checked, resting only on the single isolated axiom `classic`
  (excluded middle) in the classical layer.
- **`+ℝ-axioms`** — machine-checked but importing `Coq.Reals` (the 2 real-analysis axioms); NOT
  axiom-free — a *readout* rung, honestly flagged.
- **`Dr`** — a stance / definition / interpretation over checked pieces (design-narrative).
- **`Open`** — genuinely unsettled, or needs the continuum (`+reals`).

**The load-bearing rule.** Never assert *all/every/universal* over a finite witness set without
tagging `Dr`. Never put a continuum name on a finite analogue. Never claim to *solve* a continuum
question — diagnose it as a non-readout and predict the readout. The boundary between the provable
and the Open **is** the boundary of the infinity axioms.

## Notation

`δ_R` primitive retained difference · `D` the naturals-as-semiring · `ℤ,ℚ,ℝ` the number tower ·
`≺` retained order · `L_R` the graph Laplacian (retained-information operator) · `⟨·,·⟩_G` the
retained inner product · `Th` theorem, `Def` definition, `Ax` axiom, `Pr` principle.

---

# Part 0 — Foundations of the foundation

## 0.1 The one commitment (Pr 0.1, `Dr`)

> **Everything an agency ever reads is a finite retained difference — a *readout*, rational and
> discrete. The continuum (ℝ), infinite divisibility, and `+∞` are non-readouts: real as boundaries,
> never as appearances.**

This is a stance, not a proof that classical mathematics is wrong; a classical realist may hold the
continuum ontologically actual. We adopt the commitment and follow it to the end. Its mechanical
witness: the entire core is `Print Assumptions`-Closed *precisely because* it refuses the infinity
axioms (`Require Reals` is where they would enter).

## 0.2 The injected infinities and zeros (Def 0.2)

An "open/hard/paradoxical" problem is, until shown otherwise, an **artifact of a silently injected
non-readout**. Name it before deferring:

- **I1** ℝ-completeness (LUB/Dedekind) · **I2** infinite divisibility `h→0` · **I3** infinite scale
  separation `Re,Λ→∞` · **I4** actual `+∞`.
- **Z1** the point `r=0` · **Z2** reached continuum `h=0` · **Z3** absolute rest `v=0,T=0` · **Z4**
  the true void.
- **Pr 0.2 (reciprocity, `Dr`).** `1/0=∞`: zero and infinity are one non-readout seen from two
  sides; they appear together at every singularity. A finite reader lives strictly *between* the
  refused endpoints and touches neither. *A refused endpoint being unreadable is the system working,
  not a wall to break through.*

---

# Part 0.5 — The reader, resolution, and coarse-graining (the substrate)

Before number or logic can be *used*, we fix **who reads** and **at what resolution**. This Part
supplies the collection / function / equality substrate — *grounded in coarse-graining, not assumed* —
and the finite-resolution discipline that lets analysis proceed without ever injecting the continuum.
*(Integrates the author's earlier* **Causal Calculus: Primitive Aggregation under Finite Causal
Access** *— Lahtee 2026, DOI 10.5281/zenodo.18164015 — whose still-usable core is extracted here.)*

## 0.5.1 Access & coarse-graining (Def 0.5.1)

`IR` — the world, **never read directly**. Access map **`A : IR → I_acc`** to the accessible
information states. Coarse-grain family **`G_λ : I_acc → I_λ`**, `λ` a resolution. A reader sees only
`I_λ` — what survives coarse-graining at its resolution.

## 0.5.2 Admissible description (Def 0.5.2 — the formal readout)

`E` is **admissible at resolution `λ`** iff there is `Ẽ` with **`E = Ẽ ∘ G_λ`** — the result does NOT
distinguish what `G_λ` discards. **Consequence:** answers are free of any `ε→0` limit; sub-resolution
differences are *not perceived*. This is `readout-not-truth` made operational: a reading is admissible
exactly when it **factors through the coarse-graining**.

## 0.5.3 The collection / function / equality substrate (induced by `G_λ`)

- **collections / sets** := the fibers of `G_λ` (a "set" is a class of `I_acc`-states identified at
  resolution `λ`).
- **functions / maps** := **admissible maps** — those that factor through `G_λ`.
- **equivalence `∼_λ`** := `G_λ(x)=G_λ(y)` (indistinguishable at `λ`); **ordered pairs / products /
  quotients** are the corresponding admissible constructions.
- **equality `=`** := mutual indistinguishability to every reader — the finest `∼_λ` — now
  **non-circular**: grounded in the coarse-grain fibers, not defined using `=` itself (this repairs
  Def 7.2). *This is the sets-and-functions layer a foundation needs, **induced by coarse-graining
  rather than posited**.*

## 0.5.4 Causal order (S2)

reference `s_0`; **`t(s) := min #steps(s_0 → s)`** — the minimal-step metric (= distance as retained
resistance, Def 4.1); **`s ⪯ s' ⟺ t(s) ≤ t(s')`**; the **causal index** `n := t(s_n)` generates the
tape; resolutions `ε_t, ε_x > 0`.

## 0.5.5 The layer & infinity discipline (the tier system, operationalized)

- Layers: **S1** (pre-theoretic — descriptions, resolution, admissibility) · **S2** (causal order) ·
  **S3+** (constructed operators / equations at declared finite resolution).
- **A11** — declare the layer of every result. **A8 (infinity discipline)** — *work at finite `ε`
  first; take `ε→0` (or `N→∞`) ONLY after a stability proof, and declare it.* **CMG** — effective,
  resolution-dependent scope; no fundamental claims. **A8 is the analysis discipline that lets the
  whole calculus be built without ever making an actual infinity primitive.**

## 0.5.6 Honest metatheory note (declared, not hidden)

This substrate still uses ordinary **finitary logic** (propositional connectives, quantifiers,
induction on indices) as its meta-language, and the machine-checked corpus is verified in **Coq's
type theory (CIC)**. "One primitive" means the **philosophical** primitive (`δ_R` — retained
distinction under finite access); the *metalogic* in which its theorems are proved is declared here,
not smuggled. The refusal of the continuum is a refusal to make it a **primitive appearance**, not a
denial that a finitary metatheory is in use.

---

# Part I — Retained-Distinction Logic (RDL)

The logic must tolerate a local contradiction without collapse, because a reader may hold conflicting
retained records before resolution.

## 1.1 Axioms of RDL (Ax-RDL, paraconsistent)

- **Ax-RDL1 (distinction).** The basic judgement is a *distinction* `a ▷ b` (a is told apart from b),
  not a truth value.
- **Ax-RDL2 (contradiction = obstruction).** A contradiction is a *nonzero obstruction* `⊥_o`, an
  object, not a licence to derive everything.
- **Ax-RDL3 (non-explosion).** From `p ∧ ¬p` one may NOT derive an arbitrary `q` (`ex falso` is
  rejected).
- **Ax-RDL4 (gap ≠ assertion).** Absence of a distinction (a gap) is not the assertion of its
  negation.
- **Ax-RDL5 (classical limit).** When every obstruction is zero, RDL reduces to classical logic.

## 1.2 Theorems of RDL (`Th_coqc`, axiom-free — witness `formal/RDL.v`, 8 theorems)

- **Th 1.1 (soundness).** RDL's calculus is sound for its retained-distinction semantics.
- **Th 1.2 (non-explosion).** `p ∧ ¬p ⊬ q` for arbitrary `q`. *(the core paraconsistency guarantee)*
- **Th 1.3 (contradiction = obstruction).** A contradiction denotes a nonzero obstruction object.
- **Th 1.4 (gap ≠ assertion).** A truth-value gap is provably distinct from an assertion.
- **Th 1.5 (classical limit).** Zero-obstruction RDL ≡ classical propositional logic.
- **Th 1.6 (non-triviality).** RDL has a model with a genuine (non-zero) obstruction — it is not
  vacuous.

---

# Part II — The primitive and the genesis of number

## 2.1 The primitive (Def 2.1, `Dr` → `Th_coqc` realization)

**`δ_R`** — *a retained difference exists*. Ontologically primitive; nothing is assumed below it.
Its realization is machine-checked: **Th 2.1 (`primordial_difference_exists`, `Th_coqc`)** — a first
distinction exists, witnessed by `succ 0 ≠ 0`.

## 2.2 Axioms of Retained Difference (Ax-RD1…RD9)

The engine `D` is generated by:

- **RD1** there is a ground `0` (no prior distinction).
- **RD2** a successor `succ` (retain one more distinction).
- **RD3** `succ n ≠ 0` (a retained tick is never the ground). *(witness `RD3_succ_ne_zero`)*
- **RD4** `succ` is injective (distinct histories stay distinct).
- **RD5** induction: a property holding at `0` and closed under `succ` holds throughout.
- **RD6–RD9** the recursion clauses defining `⊕` (retained addition) and `⊗` (retained composition)
  and the order `≺` from `succ`.

## 2.3 The naturals `D` (`Th_coqc`, axiom-free — witness `RD.v`, `RDL_Distinguishability.v`)

- **Th 2.2 (semiring).** `(D,⊕,⊗,0,1)` is a commutative semiring.
- **Th 2.3 (total order + well-ordering + strong induction).** `(D,≺)` is a total order, well-ordered.
- **Th 2.4 (isomorphism).** `toNat : D → ℕ` is a semiring-and-order **isomorphism** `D ≅ ℕ`.
- **Th 2.5 (elementary equivalence).** `D ≡ ℕ` via a full first-order satisfaction transfer.
- **Th 2.6 (`D` models PA; `Con_PA`).** `D ⊨` first-order Peano Arithmetic, and **PA is consistent**
  (consistency-from-a-model), axiom-free.
- **Th 2.7 (`Con_PA_classical`, `Th_coqc+classic`).** The classical frontier of consistency is closed
  on the single axiom `classic`.
- **Th 2.8 (second-order categoricity).** Dedekind categoricity of the second-order theory.
- **Th 2.9 (discrete floor, `Th_coqc`).** `¬∃z, 0 ≺ z ≺ succ 0` — nothing lies below the first tick.
  **Principle (Pr 2.1):** *density / the continuum is provably ABSENT at the root*; the continuum can
  only ever be a later readout.

---

# Part III — The number tower (each rung a readout of the last)

## 3.1 The integers `ℤ` (`Th_coqc`, axiom-free — Grothendieck completion of `D`)

- **Def 3.1.** `ℤ := (D×D)/∼` with `(a,b)∼(c,d) ⟺ a⊕d = c⊕b`; value homomorphism to the standard ℤ.
- **Th 3.1.** `(ℤ,+,·,0,1)` is a commutative **ring** (`zadd_neg` additive inverse, `zmul_assoc`,
  `zmul_distrib_l`, all up to `zeq`).

## 3.2 Discrete calculus over `ℤ` (`Th_coqc`, axiom-free — *calculus with no reals*)

- **Def 3.2.** difference `Δf(n) := f(n+1) ⊖ f(n)`; sum `Σ`.
- **Th 3.2 (discrete FTC, both directions).** `FTC`, `FTC_inverse` (telescoping): `Σ` and `Δ` are
  mutually inverse.
- **Th 3.3 (discrete Leibniz).** `Δ(f·g) = f·Δg + (Sg)·Δf` (product rule), no continuum needed.

## 3.3 The rationals `ℚ` (`Th_coqc`, axiom-free — field of fractions of `ℤ`)

- **Def 3.3.** `ℚ := (ℤ×ℤ_{≠0})/∼`; value homomorphism into the standard ℚ.
- **Th 3.4.** `(ℚ,+,·)` is a **field**: `qadd_neg`, `qmul_assoc`, `qmul_distrib_l`, and the
  **multiplicative inverse `qmul_inv`**. The ladder `D` semiring → `ℤ` ring → `ℚ` field is verified
  end-to-end (69 constructive theorems, axiom-free).

## 3.4 The reals `ℝ` — the continuum AS a readout (`Th_coqc`, axiom-free unless noted)

- **Def 3.4.** `ℝ :=` Bishop **regular Cauchy sequences of `ℚ`**: `f:ℕ⁺→ℚ` with
  `|f n − f m| ≤ 1/n + 1/m`. Equality `Req` (an equivalence). Injection `inj_Q : ℚ ↪ ℝ`.
- **Th 3.5 (ordered field up to `Req`).** `ℝ` is a commutative ring, ordered (`Rle` partial order,
  antisymmetric; strict `Rlt` irreflexive/transitive), **multiplication** (`Rmul` well-defined,
  associative, distributive) and **reciprocals for every real apart from 0** (`Rinv_gen`,
  `Rmul_inv_gen`, either sign). *(the ladder `D→ℤ→ℚ→ℝ` closed at the field level, axiom-free)*
- **Th 3.6 (Cauchy-completeness).** `R_complete` / `R_complete_metric` — every real Cauchy sequence
  has an **explicitly constructed** limit (the diagonal `L n := X(2n)(6n)`): *the continuum point is
  read off the discrete rational approximants.* **This is the thesis of the book, machine-checked.**
- **Th 3.7 (constructive order).** `Rlt` is **cotransitive** (`Rlt_cotrans`) — the constructive
  substitute for trichotomy.
- **Th 3.8 (lattice).** binary `Rmax`/`Rmin` with universal properties — the constructive finite
  suprema/infima.
- **Pr 3.1 (honest non-constructivity, explicitly marked).** Full **trichotomy**, a **total `≤`**,
  and the **classical least-upper-bound property** are each **NOT constructively valid** — they imply
  an omniscience principle (LPO/WLPO). Cotransitivity + Cauchy-completeness + the finite lattice are
  their correct constructive replacements. *(To assume LUB is to inject I1.)*
- **Th 3.9 (`+ℝ-axioms` where continuum analysis is used).** ε–δ continuity `Rcontinuous_at`, the
  metric-space laws (`Rdist_triangle`), Lipschitz operations — machine-checked as *derived rungs*;
  the full derivative/integral tower and continuum geometry remain **imported** (`Open`/`+reals`),
  honestly deferred.

**Principle (Pr 3.2, the tower).** `δ_R → D → ℤ → ℚ → ℝ`: each rung is *defined from* the previous;
the continuum is the last rung and is a **readout** of the discrete root, never its substrate.
π, e, φ are **readout-invariants** (Appendix A), diagnostics that reconstruction succeeded — only
their finite ℚ-approximants ever appear (Th A.1: `InfoIrrationalNonReadout` — √2 is a non-readout).

---

# Part IV — Geometry from retained difference

## 4.1 Distance (Def 4.1, `Th_coqc` core)

Distance **enters not as a coordinate difference** but as **accumulated retained resistance along the
optimal path**:
`dist(x,y) := min over paths x⇝y of Σ (edge resistances)`.

- **Th 4.1 (metric-space laws).** `dist(x,x)=0`, symmetry, non-negativity, and the **triangle
  inequality** — the last *because a detour cannot be cheaper than the direct optimum*. (`dist_*`,
  L¹ product metric `dist2_*`.)
- **Th 4.2 (Tarski betweenness).** `Betw(x,y,z)` axiomatized and proved on the discrete metric — the
  synthetic-geometry primitive, with no real coordinates.

## 4.2 Angle without the continuum (Def 4.2, `Th_coqc`) — *the contamination this book most guards*

The textbook **angle** (`acos`/`atan2`, degrees) requires ℝ-completeness = I1 and is refused. In its
place:

- **Def 4.2a (overlap fraction).** for retained states `v, e`:
  `overlap(v,e) := |⟨v,e⟩_G|² / (⟨v,v⟩_G · ⟨e,e⟩_G)` — a **Born-rule ratio**, rational (`+,·,÷`
  only), no trig, no π, no ℝ. This is the quantity `cos²θ` would have given, arrived at without ever
  injecting the continuum.
- **Def 4.2b (turning number).** a rotation is a **rational fraction of one full cycle**, not a real
  angle. Mixing/holonomy read out as overlap fractions or turning numbers.

## 4.3 The relation graph and the operator `L_R` (`Th_coqc`, axiom-free — `RDL_CausalOrder.v`)

- **Def 4.3.** the retained relation graph; the interval count `N(x,y) = toNat y − toNat x − 1`
  (`Ncount_eq`), `N=0 ⇔` no event between.
- **Th 4.3 (Laplacian mechanics).** `L_R` (=`lap`/`B`) is **symmetric** (`B_sym`), **PSD**
  (`B_self_nonneg`), its **kernel ⊇ constants** (`lap_kills_constants` — row-sum-zero =
  conservation), **linear** (`lap_linear`), equals **div-grad** (`lap_is_div_grad`), and satisfies
  **summation-by-parts** (`sbp`).
- **Th 4.4 (energy non-increase).** the per-node equation of motion makes the readout energy
  monotone non-increasing (`list_energy_nonincreasing`).

---

# Part V — The retained-information operator (information is the central axis)

## 5.1 The keystone (Def 5.1 + Th 5.1)

- **Def 5.1 (retained-information density).** `I(Φ) :=` the distinguishability of neighbouring
  retained states of the field `Φ` on the graph.
- **Th 5.1 (keystone — target, `Th_coqc` in progress).** **`B(Φ,Φ) = I(Φ)`**: the operator's
  Dirichlet energy **is** the retained-information functional. *Information — not length, not energy
  — is the central quantity; geometry and distance are readouts OF it.* (Phase-2 of the operator
  program; the Laplacian mechanics Th 4.3–4.4 are the completed Phase-0.)

## 5.2 Readouts of the operator

- **Th 5.2 (metric as readout).** geometry (distances, spectra) is recovered from `L_R` — geometry is
  a readout of the information operator, not a prior stage.
- **Th 5.3 (quantum readout, `+ℝ carrier`).** completely-positive trace-preserving (CPTP) channels
  are the information-preserving quantum readout layer over the same field.
- **Pr 5.1 (mass/spectrum principle).** physical spectra and mass ratios are read from `L_R`'s
  spectrum and from Born-rule overlap ratios — **never** from continuum angles, coordinates, or a
  smooth free-parameter coordinate (which carries no content: a smooth bijection of a knob is a
  coordinate, not an observable).

---

# Part VI — The continuum as a readout, and the diagnosis of "open" problems

## 6.1 The diagnosis move (Pr 6.1, `Dr`)

When a problem involves infinity, **diagnose the injection first** (I1–I4 / Z1–Z4); the openness is
usually its artifact. Then **dissolve** it (the continuum is not what appears) and **predict the
discrete appearance** — a falsifiable statement — rather than defer to a non-readout.

- **Worked pattern (Navier–Stokes, `Th_coqc` bricks).** `InfoGlobalLaminarReadout` +
  `InfoDiffusionMaxPrinciple` + `InfoMonotoneMaxPrinciple` ⇒ global-in-time laminarisation;
  `InfoSkewNotMonotone` ⇒ a skew (energy-conserving) advection is *never* monotone — so `L²`
  conservation and the `L∞` maximum principle cannot both come from one advection. That trade-off
  *is* the hardness, now a theorem; the continuum "blow-up" needs I2+I3+I4 even to be posed.

## 6.2 The endpoint principle (Th 6.1, `Th_coqc` for `×`, `Dr` general —
`InfoOperatorLosesPropertyAtEndpoints`)

Every finite-property-preserving operator **loses a defining property at each refused endpoint**: at
`0` it loses cancellation and invertibility; at `∞` there is no element to act on (`ℚ` has no maximal
value). Consistent infinities in classical mathematics each *pay this price* (limits never touch ∞;
`ℵ₀+1=ℵ₀` drops cancellation; extended reals drop totality; ZFC drops unrestricted comprehension).
So the discrete/finite interior is the **only** region where operators keep all their properties —
by necessity, not taste.

---

# Part VII — Complete operator reference (self-contained; no other math text is needed)

Every operator used anywhere is **defined here from the primitive**, with its domain, its
recursion, its governing theorems, and its discrete-honest boundary (which inputs are refused
non-readouts). Nothing is imported from an outside textbook — this Part closes the operator set.

## 7.0 The information language of every operator (the PRIMARY meaning — the old language is refused)

**Principle (Pr 7.0, `Dr`).** Every mathematical operator is, first, a **mode of retained
distinction** — an operation on *readouts*, not on continuum quantities. Its ordinary textbook
meaning ("add magnitudes", "multiply lengths", "the angle between two vectors") is only the machine
**shadow**. This book gives each operator its **information meaning** as the primary reading; the
recursions in 7.1–7.5 are merely its machine realization. **No operator keeps its old-world
semantics.**

| operator | information meaning (the new language — read this first) |
|---|---|
| `¬` | **obstruction reversal** — flip which side of a distinction is retained |
| `∧` | **joint retention** — both distinctions held at once (the meet of two records) |
| `∨` | **admissible retention** — either distinction suffices (the join) |
| `→` | **retained transport** — a distinction at `p` carried, by a reader-transform, to one at `q` |
| `↔` | **mutual transport** — each record inferable from the other |
| `∀` | **retention across the whole tape** — holds at every retained position |
| `∃` | **a constructible witness distinction** — a reader can exhibit one |
| `=` | **mutual indistinguishability** — no reader can tell them apart (`O(x)=O(y)` for every `O`) |
| `≠` / `#` | **a witnessed distinction** — some reader does tell them apart |
| `≺` | **retained precedence** — the arrow of accumulated record ("came before") |
| `⊕` (`+`) | **accumulation** — merge two retained records into one longer record (total distinctions retained) |
| `⊖` (`−`) | **cancellation / debt** of retained distinction — remove record; below the ground the record becomes **signed** (a directed debt) — this is *what `ℤ` is* |
| `⊗` (`×`) | **replication / composition** of distinction-structure — lay `b` copies of `a`'s pattern end to end; the tensor of two retained patterns (distinctions of distinctions) |
| `÷` | **equal partition** of a retained record into `b` indistinguishable parts (the inverse of replication); `÷0` = partition into *no* parts = no reader-record = **refused** |
| `^` | **self-composition** — iterate the replication-operator on its own output; the retained record of a process re-reading itself |
| `√` / `ⁿ√` | **generator readout** — recover the pattern whose self-composition yields the record; usually a **non-readout** (no finite record generates it), only its approach appears |
| `log` / `log_a` | **retained-distinction count** — how many replications (self-compositions) of `a`'s pattern produce the record; the record LENGTH; the **native unit of information (bits when `a=2`)** — inverse of `^` |
| `\|·\|` | **magnitude of retained distinction**, direction discarded |
| `Δ` | **local change** of retained distinction (the increment of record between adjacent ticks) |
| `Σ` | **accumulated retained record** (the total distinction up to a tick) |
| `⟨·,·⟩_G` | **shared retained distinction** — the co-retention of two records |
| overlap fraction | **readable co-retention** (Born-rule) — the only "angle", and it is not an angle |

**In one line:** arithmetic is the **bookkeeping of accumulated, replicated, partitioned, and
cancelled retained distinction**; logic is the **algebra of distinction combinators**; comparison is
**reader-(in)distinguishability**. The continuum readings — length, magnitude, area, angle — are
refused as primary and appear only as later readouts (Part III, VIII). *(This is the operator layer
of the project's readout lexicon; keep the two in sync.)*

## 7.1 Logic operators (on RDL judgements — Part I)

- **`¬` negation** — `¬p` flips `p`'s obstruction polarity; NOT `ex falso` (Ax-RDL3). `¬¬p ⊢ p`
  only in the classical limit (Th 1.5).
- **`∧` conjunction** — `p ∧ q` retains both distinctions; `obstruction(p∧q) =` the join of the two.
  Commutative, associative, idempotent (`Th_coqc`, `RDL.v`).
- **`∨` disjunction** — `p ∨ q` retains either distinction; De Morgan up to obstruction.
- **`→` implication** — `p → q :=` the retained transformation carrying `p`'s distinction to `q`'s.
  (`p→q ≡ ¬p∨q` **only** in the classical limit — do not assume it paraconsistently.)
- **`↔` biconditional** — `(p→q) ∧ (q→p)`.
- **`∀` universal** (over `D`) — `∀n.φ(n) := φ(0)` and `φ` closed under `succ` (grounded in RD5
  induction).
- **`∃` existential** — `∃n.φ(n) :=` a witness `n` is **constructible** (constructive existence; no
  pure excluded-middle existence).

## 7.2 Equality and order operators

- **`=` equality** — Def (readout-equivalence): `x = y ⟺ O(x)=O(y)` for every readout `O`
  (indistinguishable to every reader); on `D`, structural via `succ`-recursion. Reflexive,
  symmetric, transitive, and **substitutive** (Leibniz). (`Th_coqc`.)
- **`≠` / `#` apartness** — `¬(x=y)`; constructively, a genuine distinction is exhibited (on `ℝ`,
  apartness `x # y` is primitive, `≠` its negation-form).
- **`≺ / ⪯` order** — Def on `D`: `a ≺ b ⟺ ∃k≠0, a⊕k=b`. Total, well-ordered (Th 2.3). Lifted
  compatibly to `ℤ, ℚ`; on `ℝ` the strict `Rlt` is **cotransitive** (Th 3.7) and `Rle` a partial
  order — **no total `≤` constructively** (Pr 3.1).
- **`< ≤ > ≥`** := the `≺ / ⪯` instances per number system.

## 7.3 Arithmetic operators (each defined from `succ`, recursively)

- **`⊕` addition (`+`)** — `a⊕0 := a`; `a⊕succ(b) := succ(a⊕b)`. **Th 7.1:** commutative,
  associative, cancellative, `0` identity (semiring, Th 2.2). Lifted to `ℤ/ℚ/ℝ` as `+`.
- **`⊖` subtraction (`−`)** — total on `ℤ` as `a ⊕ (−b)`, `−b` the additive inverse (Grothendieck,
  Th 3.1). On `D` it is **PARTIAL** (truncated: `a⊖b` defined only when `b ⪯ a`) — *subtraction
  below zero is refused; that refusal is exactly where `ℤ` is born.*
- **`⊗` multiplication (`×`)** — `a⊗0 := 0`; `a⊗succ(b) := (a⊗b)⊕a`. **Th 7.2:** commutative,
  associative, distributes over `⊕`, `1` identity (semiring). Lifted to `ℤ` (ring), `ℚ/ℝ` (field).
- **`÷` division** — on `ℚ`: `a÷b := a ⊗ b⁻¹`, `b⁻¹` the multiplicative inverse (Th 3.4, `qmul_inv`),
  **defined iff `b ≠ 0`**. **`÷0` is REFUSED** — the endpoint principle (Th 6.1): at `0` the operator
  loses invertibility; `1/0` is the reciprocal non-readout to `∞` (Pr 0.2), never a value. On `D/ℤ`:
  **Euclidean division** `a = q⊗b ⊕ r` with `0 ⪯ r ≺ b` (quotient + remainder), total for `b ≠ 0`.
- **`^` exponentiation (ยกกำลัง)** — `a^0 := 1`; `a^succ(n) := a^n ⊗ a` (iterated `⊗`). **Th 7.3:**
  `a^(m⊕n) = a^m ⊗ a^n`, `(a^m)^n = a^(m⊗n)`, `(a⊗b)^n = a^n ⊗ b^n`. Integer exponents on `ℚ`:
  `a^(−n) := 1/a^n` (`a ≠ 0`). **Rational / real exponents are a READOUT:** `a^(p/q)` is the root
  (7.3 root); `a^x` for `x ∈ ℝ` is the limit of `a^(ℚ-approximants)` — the finite approximants
  appear, the "value" is a readout-invariant. Convention `0^0 := 1` (empty product), stated.
- **`√ / ⁿ√` root (รูท)** — `ⁿ√a :=` the `r` with `r^n = a` (`r ⪰ 0` for even `n`). **Th 7.4:** when
  `a` is an `n`-th power in `ℚ`, `ⁿ√a ∈ ℚ` (exact readout). **Otherwise `ⁿ√a` is a NON-READOUT**
  (Th A.1, `InfoIrrationalNonReadout`: `√2 ∉ ℚ`) — only its regular Cauchy sequence of
  `ℚ`-approximants appears; "`√2` the number" is a boundary, never an appearance. It is *computed* by
  a discrete bisection/Newton sequence over `ℚ` that converges by Cauchy-completeness (Th 3.6) — no
  `ℝ` is needed to run it.

- **`log_a` logarithm — the retained-distinction count (the information unit)** — Def: `log_a(x) :=`
  the `n` with `a^n = x`, i.e. **how many self-compositions of `a` generate the record `x`** — the
  inverse of `^`. On `D/ℤ`: the **discrete logarithm** `⌊log_a x⌋ = ` the largest `n` with `a^n ⪯ x`,
  total for `a ⪰ 2`, `x ⪰ 1`. **Th 7.5:** `log_a(x⊗y)=log_a x ⊕ log_a y`, `log_a(x^k)=k·log_a x`,
  `log_a(1)=0` — replication becomes accumulation (`⊗ → ⊕`): the log **linearises composition**. When
  `x` is not an exact power of `a`, `log_a x` is a **non-readout** (only its `ℚ`-approximant appears,
  computed by a discrete bisection over exponents). **Information meaning (primary):** `log_2 N` is
  the number of **binary distinctions (bits)** needed to name one of `N` retained states — the record
  LENGTH; the entropy `H = Σ p_i · log_2(1/p_i)` (Part V) is the *expected retained-distinction count*.
  `log` is therefore the native unit of this book's "information" — it measures retained distinction
  in bits. `log_a(0)` and `log_a` of a non-positive record are **refused** (no generating count exists
  — the `0`/`∞` endpoint, Th 6.1).

## 7.4 Derived operators (all reduce to 7.1–7.3)

- **`|·|` absolute value** — `|a| := a` if `a ⪰ 0` else `⊖a`; non-negative, `|a⊕b| ⪯ |a|⊕|b|`.
- **`gcd / lcm`** — from Euclidean division (7.3 `÷`).
- **`Δ` difference, `Σ` sum** — the discrete-calculus operators (Th 3.2–3.3), inverse to each other.
- **`⟨·,·⟩_G` inner product, `‖·‖_G` norm** — `‖x‖_G := √⟨x,x⟩_G` (root over `ℚ`, a readout if
  irrational); the **overlap fraction** (Def 4.2a) is the ONLY angle-like operator — trig-free.

## 7.5 The refused operations (the endpoint boundary, made explicit — Th 6.1)

`÷0` (loses invertibility) · a supremum/exponent reaching `∞` (`D` has no maximal element) · `ⁿ√`
of a non-`n`-th-power **as an exact value** (a non-readout) · any limit that "lands" at `∞` or an
exact `0`. All refused as non-readouts; only the finite `ℚ`-approach appears. **This closes the
operator set:** every total operation is defined from `succ`; every partial one has its refused
inputs named — so no external mathematics is required to evaluate any expression in this book.

---

# Part VIII — Information Discrete Calculus (the calculus of retained difference; `[results-first]`)

The calculus built entirely on the difference `Δ` and sum `Σ` operators over `ℚ` (no reals) — the
discrete analogue **and root** of continuum calculus; continuum calculus is recovered last, as a
readout. Results and definitions are stated here; proofs are v-proofs (next version).

## 8.1 Sequences, shift, difference

- **Def.** a sequence is a map `f : D → F` (`F = ℚ` or a field). Shift `E f(n) := f(n+1)`.
- **Def.** forward difference `Δf := (E−1)f`, i.e. `Δf(n)=f(n+1)⊖f(n)`; backward `∇f(n)=f(n)⊖f(n−1)`;
  higher `Δᵏ`. **Newton forward-difference (discrete Taylor):**
  `f(n) = Σ_{k} \binom{n}{k} Δᵏf(0)` — exact, finite, no limit.

## 8.2 Sum, the discrete FTC, and integration-by-parts

- **Def.** antidifference `Σ_a^b f := f(a)⊕…⊕f(b−1)`.
- **Th 8.1 (discrete FTC).** `Σ_a^b Δf = f(b)⊖f(a)` (telescoping) and `Δ(Σf)=f` (Th 3.2).
- **Th 8.2 (summation by parts).** `Σ f·Δg = f·g ⊖ Σ (Eg)·Δf` — discrete integration by parts.

## 8.3 Falling powers — the natural discrete monomials

- **Def.** falling factorial `n^{(k)} := n(n−1)…(n−k+1)`, `n^{(0)}:=1`.
- **Th 8.3 (discrete power rule).** `Δ n^{(k)} = k·n^{(k−1)}` and `Σ n^{(k)} = n^{(k+1)}/(k+1)` —
  the clean power rule holds for **falling** powers (WHY they, not ordinary powers, are the discrete
  monomials). Stirling numbers convert ordinary ↔ falling powers.

## 8.4 Difference equations (the discrete ODEs)

- **Def.** linear difference equation `Σ_i c_i f(n+i) = g(n)`; solved by characteristic roots
  (homogeneous) + a particular part.
- **Def.** the discrete exponential `2^n` (eigenfunction of `E`) and the retained growth law
  `Δf = a·f ⟹ f(n)=f(0)(1+a)^n` — the discrete root of `e^{ax}`; the continuum `e` is its `h→0`
  readout (+ℝ).

## 8.5 Formal series, generating functions, discrete transforms

- **Def.** ordinary / exponential **generating functions** as `ℚ`-formal power series (formal — no
  convergence, hence no continuum needed).
- **Def.** the **Z-transform** (discrete Laplace); the **discrete Fourier** on `n`-th roots-of-unity
  **read out as overlap fractions / turning numbers** (Def 4.2) — never continuum angles.

## 8.6 The calculus of the graph operator `L_R` (discrete exterior calculus)

- **Def.** coboundary `d`, its adjoint `δ`, gradient/divergence/curl, the **Hodge** decomposition and
  **harmonic forms** — the discrete de Rham complex over `ℚ`.
- **Def.** discrete **Green's function** of `L_R`; the **heat step** `(1 − τ L_R)`; the **spine wave**
  `M∂²_t + D∂_t + K·L_R` (Part V's operator in motion) — all exact over `ℚ`.

## 8.7 Continuum calculus as the last readout (`+ℝ-axioms`)

- The continuum derivative `f'(x)=lim_{h→0} Δf/h` and integral `∫` are recovered as **readouts** of
  `Δ / Σ` under `h→0` sampling — the final rung, flagged `+ℝ`, never the primitive. `InfoContinuumLimit`.

## 8.8 The information reading (why it is *information* calculus)

`Δ` = local change of distinction, `Σ` = accumulated retained record, `L_R` = information diffusion;
energy and action are readouts of the information functional (Th 5.1). **Discrete calculus is the
calculus of retained-information flow** — continuum calculus is what a finite reader reconstructs
from it.

---

# Part IX — Powerful Tools, Re-adapted (Regularization, Asymptotics, Transforms, Deformations)

Under readout-not-truth there is no completed infinite object to sum, integrate, or continue; what exists is a finite reader's *retained aggregation* of discrete data at a declared resolution. Every tool below is therefore re-read as one operation — split a finite readout into a **window-tracking bulk** (discarded, non-readout) and a **window-stable residue** (kept), and declare the limit only after proving stability (Discipline **A8**). Regularization is not "assigning a value to infinity"; it *is* the mathematics of finite retained aggregation.

## A. Divergent aggregation as retained readout

**§9.1 Ramanujan summation.** The Ramanujan value is not the sum of the series but the resolution-independent residue of the finite prefix-sum $I_1f[N]=\sum_{n\le N}f[n]$. Factor $I_1f[N]=A_\varepsilon(N)\oplus C_\varepsilon(f)\oplus R_p(N)$, with $A_\varepsilon$ the window-growing envelope (integral + boundary derivative corrections), $R_p(N)\to0$ the truncation error, and $C_\varepsilon(f)$ the stable residue. Declare $R\!\sum f=C_\varepsilon(f)$ only after proving $c_N=I_1f[N]-A_\varepsilon(N)$ is Cauchy under window-refinement. Buys the flagship $R\!\sum n=\zeta(-1)=-1/12$ as a *finite* computation, with the firewall against "1+2+3+⋯ = −1/12." **Tier: finite_diagnostic.**

**§9.2 Euler–Maclaurin.** The exact ($R_m$-attached) sum↔integral bridge, re-founded as the first nontrivial corollary of FTCC ($I_\varepsilon D_\varepsilon f=f$) via the finite operator algebra $E_\varepsilon=(1-\varepsilon D_\varepsilon)^{-1}$:
$$I_\varepsilon f[a,b]=\tfrac{\varepsilon}{2}[f(b)+f(a)]+\sum_{k=1}^{m}\tfrac{B_{2k}}{(2k)!}\varepsilon^{2k}\!\left[D_\varepsilon^{2k-1}f(b)-D_\varepsilon^{2k-1}f(a)\right]+R_{m,\varepsilon}.$$
Bernoulli numbers are finite rational data; the divergent $m\to\infty$ tail is un-coarse-graining without bound, so truncating at retained order $m^\ast$ is a $G_{\lambda(m^\ast)}$ choice. This is the constructive engine realizing the regularization hook at every finite order. **Tier: finite_diagnostic** (interpretive layer Dr).

**§9.3 Zeta / analytic regularization.** Build the two-parameter readout $\zeta_\lambda(s;N)=\sum_{n\le N}n^{-s}e^{-\lambda n}$ — manifestly $E=\tilde E\circ G_\lambda$ with $G_\lambda=e^{-\lambda n}$ discarding the sub-resolution tail (S1). Euler–Maclaurin splits it into $\lambda$-divergent poles plus a regulator-independent residue; when regulator-independence is *proved*, that residue is $\zeta(-s)$. The operator version regularizes $\det A=\prod\lambda_i$ as $\det_\zeta A=\exp(-\zeta_A'(0))$. The pole at $s=1$ is the framework correctly *refusing* a readout where none is stable. **Tier: finite_diagnostic** (physical application Dr).

**§9.4 Abel, Borel, Cesàro.** Each regulator is a coarse-graining parameter $\lambda$. Cesàro: $C_N=\tfrac1N I_\varepsilon(s)[N]$, a finite mean; report its plateau. Abel: $G_x[a][n]=a[n]x^n$ suppresses indices past $n^\ast\sim1/\ln(1/x)$. Borel: $B_N(t)=\sum_{n\le N}\tfrac{a_n}{n!}t^n$ then discrete aggregation $S_\varepsilon=\varepsilon\sum_k e^{-k\varepsilon}B(k\varepsilon)$. All read: the family $\{E_\lambda[a]\}$ has a stable value $S$ once $\lambda$ crosses a *declared* threshold; the raw sum is never computed. The canonical teaching example for why A8 exists (forget the stability declaration and "prove" $1-1+1-\cdots$ is both 0 and 1). **Tier: finite_diagnostic.**

**§9.5 Generating functions.** $\mathbb Q[[x]]$ is already finite-discrete: it is the inverse limit of decidable rings $\mathbb Q[x]/(x^{N+1})$, with $G_N$ truncation and $[x^n](A\!\cdot\!B)=\sum_{k\le n}a_kb_{n-k}$ a finite sum. Multiply-by-$x$ is the causal shift ($I_\varepsilon$-side), $(A-a_0)/x$ the backward-difference dual; solving a linear recurrence via $A(x)\cdot(1-\sum c_kx^k)=$ data is FTCC made combinatorial. Evaluating a rational closed form at a divergence point $x_0$ is the same regularization move — licensed only post-stability. **Tier: finite_diagnostic** (evaluation-at-a-point Dr).

**§9.6 Ramanujan Master Theorem, mock theta, partition asymptotics.** RMT is A8 on the *coefficient axis*: from retained $\{\phi(0),\dots,\phi(N)\}$ form $f_\varepsilon(x)$, take the finite Mellin readout $M_\varepsilon(s)$, and declare $\Gamma(s)\phi(-s)$ only after a growth-bound stability proof. Hardy–Ramanujan–Rademacher $p(n)\sim\frac{1}{4n\sqrt3}e^{\pi\sqrt{2n/3}}$ is the case A8 *passes* — Rademacher's convergent tail certifies the discard. Mock theta functions are the case it *fails*: the sub-leading discrepancy from modularity survives every finite resolution and must be carried explicitly as Zwegers' shadow. Gives A8 falsifiable teeth. **Tier: finite_diagnostic.**

## B. Asymptotics and transforms

**§9.7 Mellin transform & master theorem.** Read $q$—no, read $s$ as a probe-exponent and the transform as a coarse-graining on a geometric log-grid: $M_\varepsilon[f](s)=\sum_n f_\varepsilon[n]x_n^{s-1}(x_n-x_{n-1})$, an $I_\varepsilon$ aggregation. The "fundamental strip" becomes the **retained-distinguishability band** (found by A8 stability testing). The harmonic-sum factorization $M_\varepsilon[S]=F^\ast(s)M_\varepsilon[f]$ with $F^\ast(s)=\sum_k\lambda_k\mu_k^{-s}$; contour-shift = resolution change, residues = zeta/Ramanujan-type finite retained values. **Tier: finite_diagnostic.**

**§9.8 Watson, Laplace, stationary-phase, saddle-point.** Set $\varepsilon=1/\lambda$; the large parameter is inverse resolution. Discretize: $I_\varepsilon=\varepsilon\sum_{n\le N}f(n\varepsilon)e^{-n}=\sum_k a_k\varepsilon^{k+1}S_N(k)$, $S_N(k)=\sum n^k e^{-n}$ with a provable geometric tail (S1 discard). Declaring the bound then $N\to\infty$ recovers Watson's $\sum a_k k!/\lambda^{k+1}$ — each term labeled a coarse-graining moment. Laplace/stationary-phase use the finite argmin of $D_\varepsilon^2\phi$ and a discrete Gauss sum; the divergent asymptotic series ties back to §9.1–9.4. **Tier: finite_diagnostic** (saddle-point in ℂ, general optimal-truncation: Dr/Open).

## C. Deformations and finite representations

**§9.9 Umbral & finite-difference calculus.** On the $\varepsilon$-falling-factorial basis $x^{\underline n}_\varepsilon=\prod_{j<n}(x-j\varepsilon)$ the causal difference is *exact*, not limiting: $D_\varepsilon x^{\underline n}_\varepsilon=n\,x^{\underline{n-1}}_\varepsilon$, giving exact telescoped power-sums and the Newton forward reconstruction $f(x)=\sum_n \frac{x^{\underline n}_\varepsilon}{n!\varepsilon^n}D_\varepsilon^{(n)}f[x_0]$. Stirling numbers are the resolution-deformation dictionary between $x^n$ and the readout-native basis; $B_n$ measures the basis-correction Faulhaber needs. **Tier: mixed** — finite core Th_coqc-eligible; the $\zeta(-n)=-B_{n+1}/(n+1)$ bridge is an import (Dr/Open), never merged with it.

**§9.10 q-calculus.** Same causal scaffolding on a *geometric* lattice $\Lambda_q=\{x_0q^n\}$ — resolution measured as a ratio, not an absolute step. $D_qf[n]$ is $D_\varepsilon$ with local $\varepsilon_n=x_0q^{n-1}(1-q)$; $I_qf(a)=a(1-q)\sum q^n f(aq^n)$ is $I_\varepsilon$ with the $q^n$ factor making the "infinite" sum a genuinely finite retained aggregate (S1 tail explicit). $q\to1$ is the disciplined continuum recovery, proved not assumed. **Tier: finite_diagnostic.**

**§9.11 Continued fractions.** The CF algorithm *is* the access operator: each step emits one integer $a_k=\lfloor x_k\rfloor$, $x_{k+1}=1/(x_k-a_k)$, aggregated by the prefix matrix product $M_n=\prod\begin{psmallmatrix}a_k&1\\1&0\end{psmallmatrix}$. Depth $n$ is $\lambda$; $p_n/q_n$ is the *optimal* finite rational readout at denominator budget $q_n$, with $|x-p_n/q_n|<1/(q_nq_{n+1})$ as the resolution-deformation metric. Periodicity (Lagrange) is itself a finite stability certificate. **Tier: finite_diagnostic** (finite $n$ Th_coqc; general $n\to\infty$ +ℝ(Open)).

**§9.12 Padé approximants.** A rational-function sibling of the scalar regularizers: from a retained coefficient window $(c_0^\varepsilon,\dots,c_N^\varepsilon)$, solve the finite Padé linear system for $[L/M]$. Poles geometrize S1's discarded tail as singularity locations. Convergence as $N\to\infty$ holds only under structural hypotheses (de Montessus); the diagonal is genuinely **Open** for unclassified $f$ (Baker–Gammel–Wills refuted, Lubinsky 2003). **Tier: split** — construction Th_coqc, convergence Dr/+ℝ(Open); spurious Froissart poles are artifacts, never reported as structure.

---

## References

- Ramanujan (notebooks, letters to Hardy, c. 1910–1918); G. H. Hardy, *Divergent Series*, Oxford: Clarendon Press, 1949, Ch. XIII.
- L. Euler, "Methodus generalis summandi progressiones," *Comm. Acad. Sci. Petrop.*, 1738; C. Maclaurin, *A Treatise of Fluxions*, Edinburgh, 1742; Graham, Knuth & Patashnik, *Concrete Mathematics*, 2nd ed., 1994, §9.5.
- B. Riemann, "Über die Anzahl der Primzahlen unter einer gegebenen Grösse," *Monatsber. Berliner Akad.*, 1859; S. W. Hawking, "Zeta Function Regularization of Path Integrals in Curved Spacetime," *Commun. Math. Phys.* 55 (1977), 133–148.
- E. Cesàro (1890); N. H. Abel (1826); É. Borel, "Mémoire sur les séries divergentes," *Ann. Sci. ENS*, 1899; Hardy, *Divergent Series*, 1949.
- A. de Moivre, *Miscellanea Analytica*, 1730; L. Euler, *Introductio in Analysin Infinitorum*, 1748; H. S. Wilf, *generatingfunctionology*, 2nd ed., 1994; Flajolet & Sedgewick, *Analytic Combinatorics*, CUP, 2009.
- RMT: Hardy, *Ramanujan: Twelve Lectures*, CUP, 1940, Ch. XI; Amdeberhan et al., *Ramanujan J.* 29 (2012), 103–120. Mock theta: Ramanujan (last letter, 1920); S. Zwegers, PhD thesis, Utrecht, 2002. Partitions: Hardy & Ramanujan, *Proc. LMS* 17 (1918), 75–115; H. Rademacher, *Proc. LMS* 43 (1937), 241–254.
- R. H. Mellin (1902, 1910); Flajolet, Gourdon & Zimmermann, "The Mellin Transform and Asymptotics: Harmonic Sums," *TCS* 144 (1995), 3–58; E. W. Barnes (1908).
- Laplace (1774); W. Thomson/Kelvin (1887); P. Debye (1909); G. N. Watson (1918); Bender & Orszag, *Advanced Mathematical Methods*, 1978; Copson, *Asymptotic Expansions*, CUP, 1965; de Bruijn, *Asymptotic Methods in Analysis*, 1958.
- I. Newton, *Methodus Differentialis*, 1711; J. Bernoulli, *Ars Conjectandi*, 1713; J. Stirling, *Methodus Differentialis*, 1730; J. Blissard (1861); Rota, Kahaner & Odlyzko, *JMAA* 42 (1973), 684–760; Roman & Rota, *Adv. Math.* 27 (1978), 95–188; S. Roman, *The Umbral Calculus*, Academic Press, 1984.
- F. H. Jackson, *Trans. Roy. Soc. Edinburgh* 46 (1908), 253–281; *Quart. J. Pure Appl. Math.* 41 (1910), 193–203; Kac & Cheung, *Quantum Calculus*, Springer, 2002.
- L. Euler, "De fractionibus continuis dissertatio," *Comm. Acad. Sci. Petrop.* 9 (1744/1750); A. Ya. Khinchin, *Continued Fractions*, 3rd ed., Univ. of Chicago Press, 1964.
- H. Padé, *Ann. Sci. ENS*, 3e série, 9 (1892); Baker & Graves-Morris, *Padé Approximants*, 2nd ed., CUP, 1996; D. S. Lubinsky (2003).

> *Every tool above is re-adapted to this framework (finite-ε, coarse-graining, A8) and the original is cited; none is used in its continuum-primitive form. This is the operator/analysis power layer — the book carries the world's hard tools without importing the continuum.*

---

# Part X — Integrated extensions (sets & functions, cardinality, analysis, probability, reconciliations)

This Part closes the foundation's remaining gaps and reconciles it with the external record. **Honest
global status:** the `create` results below (§10.1–10.6) are **Th_coqc-ELIGIBLE proof SKETCHES** — the
tier tag is the *target*; each needs an actual `coqc` + `Print Assumptions` single-file check before it
is cited as verified. The mined items (§10.8) and the cotransitivity/setoid results are the currently
machine-checked core. No external validation is invoked (horizontal-knowledge policy).

## 10.1 The pair–product–relation–function layer, from `δ_R` (closes the biggest "not-standalone" blocker)

Built strictly from prior primitives (number tower, `G_λ`-fibers, `∼_λ`, `δ_R`) — a strict DAG, no
forward reference. *(In-framework construction; `Th_coqc`-eligible sketch.)*

- **Singleton / pair fibers.** for `a,b` in fiber `X` at resolution `λ`: `{a}_λ`, `{a,b}_λ` are
  sub-fibers selected by finitely many `∼_λ`-classes (fiber-formation is already licensed, §0.5.3).
- **Ordered pair (`δ_R`-Kuratowski).** `(a,b)_λ := {{a}_λ, {a,b}_λ}`; degeneracy `a =_λ b` is *detected*
  as a `δ_R` count (`|outer|=1` vs `2`), not hidden. **Th 10.1 (injectivity, `Th_coqc`-elig):**
  `(a,b)=(c,d) ⟺ a=_λc ∧ b=_λd`, by a finite case-split on `|{·,·}|∈{1,2}` — every step a decidable
  finite readout.
- **Cartesian product.** `X ×_λ Y := {(a,b)_λ : a∈X, b∈Y}` by finite enumeration (A8: no infinite
  product; `λ→0` deferred `+ℝ-Open`); `|X×Y| = |X|·|Y|`.
- **Relation** = an admissible sub-fiber of the product — literally `E=Ẽ∘G_λ` applied to `X×Y`.
- **Function** = a relation `R` with `IsFunction(R) :≡ ∀a∈X ∃!_λ b∈Y, (a,b)∈R` (`∃!_λ` a finite
  decidable search). **Th 10.2 (coincidence — closes the blocker, `Th_coqc`-elig):**
  `AdmissibleMap(X,Y) ≅ {R : IsFunction(R)}` via the graph `G(E)`; the `∼_λ`-respecting construction
  forces representative-independence. **Axiom-free eligibility:** all objects are finite lists over
  decidable-equal `ℚ`; only `List` + decidable equality, no LEM / choice / funext.

## 10.2 Cardinality and the potential-vs-actual infinite

*(In-framework; type-level refusal is a framework-native observation.)*
- **Count = retained distinctions.** `Counting_λ(S) := |[S]_λ|` (de-duplicated `∼_λ`-classes) — always
  a finite natural, never a primitive `∞`.
- **Same size** = an admissible bijection `≈_λ`. **Th 10.3 (`Th_coqc`):** for `NoDup` lists,
  `equinum ⟺ length equal`, by finite induction — axiom-free.
- **Potential infinite** = a `δ_R`-generated tape `Tape(n+1)=σ(Tape n)`, each stage finite with
  `Counting(Tape n)=n+1`. **Th 10.4 (`Th_coqc`):** `tape_count_succ` ⇒ strict growth ⇒ no terminal
  stage (an unbounded *process*, no completed object).
- **Actual infinite refused — analytically.** **Th 10.5 (`Th_coqc`):** `∀ l:list A, ∃n, length l = n`.
  Every readout inhabits `list A`, which has *no infinite inhabitant* — actual `∞` is excluded because
  the readout type never had room for it, not by fiat. *(Cantor-style comparison of two tapes' growth
  is per-schema `finite_diagnostic`, not one closed theorem.)*

## 10.3 Finite satisfaction `⊨_λ` (and an honest downgrade)

- **Th 10.6 (`Th_coqc`-elig):** `⊨_λ` — a decidable, computable Tarski recursion of satisfaction on a
  finite domain + finite formula at a fixed coarse-graining level.
- **Downgrade (honest):** the earlier "`D ⊨ PA`" (full first-order Peano) and "`D ≡ ℕ`" (elementary
  equivalence / nonstandard models) are **`+ℝ-Open`** — they quantify over the completed standard model
  and are NOT reproven here; only `⊨_λ` is claimed.

## 10.4 RDL boundary-tie — making the logic load-bearing

- **Th 10.7 (`Th_coqc`-elig):** `D`'s semiring closure **requires RDL's non-explosion**, not classical
  logic — a boundary distinction (a state at the semiring frontier) is held without collapse only
  because `ex falso` is refused (Ax-RDL3). This is the one rung that makes Part I (logic) *load-bearing*
  for Part II (number), answering the review's "RDL is decorative" finding.

## 10.5 Real analysis via A8 (the finite-ε rung skeleton)

Every base definition is finite-`ε` over `ℚ`; the `ε→0` continuum statement is gated behind a **named,
declared** stability proof (finite-`ε` Cauchy for limits/series/derivatives; discrete Euler–Maclaurin
for tails).
- **Sequence limit / series convergence / continuity algebra** — `finite_diagnostic` (limits `+ℝ-Open`
  until a stability witness): a `(δ_R, ε)`-continuity pair closed under sum/product/composition; series
  = finite partial sums + Euler–Maclaurin tail bound (§9.2).
- **Genuinely new (Th 10.8, `Th_coqc` AS STATED):** in the native *causal / secant* form the `D_ε`
  rules are **EXACT** finite-`ε` identities over `ℚ` (zero `O(ε)` residue):
  `D_ε(f+g)=D_εf+D_εg` · `D_ε(f·g)[n]=f[n]D_εg[n]+g[n−1]D_εf[n]` ·
  `D_ε(g∘f)[n]=Δg[f[n−1],f[n]]·D_εf[n]` (secant slope across the actual jump) ·
  **FTCC** `I_ε(D_εf)[N]=f[N]−f[0]` exactly (telescoping). Each discharges by `field_simplify; ring` /
  finite induction — no `Reals`, axiom-free. *Open:* general `ε–δ` existence without a stability
  witness stays `+ℝ-Open`; the secant≈difference-quotient step is the one place classical intuition can
  silently diverge if resolution is not matched — flagged, not smoothed.

## 10.6 Probability and measure as retained frequency (a discrete measure theory)

*(New chapter-companion to the discrete calculus; `Dr`, LLN `Th_coqc`-eligible.)*
- **measure** `μ_λ := I_ε(indicator)` — a coarse-grained retained count; **probability** `p_i =
  |amp_i|²/Σ|amp_j|²` (Born-rule, already `Th_coqc` in the corpus) is the special normalized case;
  **expectation** = retained average; **law of large numbers** = A8 stability of the empirical mean
  (the plateau of `C_N=(1/N)I_ε(s)[N]`). Kolmogorov's axioms appear as theorems about admissible
  retained counts, not primitives. *(Strong LLN stays `+ℝ-Open`.)*

## 10.7 Reconciliations with the external record (กระทบยอด)

- **Causal set theory** (Bombelli–Lee–Meyer–Sorkin 1987, *PRL* 59, 521; Sorkin 2003, gr-qc/0309009),
  `finite_diagnostic`. **ADOPT re-adapted:** an admissible causal order `≺_λ` over `∼_λ`-fibers plus
  `δ_R` counting fixes the readout geometry — `Vol_λ(interval(x,y)) := #{z : x≺_λ z≺_λ y}` restates
  "order + number = geometry"; `I_ε` over the chain recovers the finite-`ε` line-element. **Local
  finiteness** re-adapted: a `G_λ`-fiber between any causal pair is finite — a *structural* reason
  sub-`λ` resolution is unreachable, strengthening A8. **CONFLICT (do not blend):** causets take
  discreteness as ontological substrate; we do not (discreteness is a readout fact at declared `λ`;
  the continuum is a non-readout). **Sorkin's Hauptvermutung stays `+ℝ-Open`** (§10.9); sprinkling is
  cited as a `Dr` template for the stability step, not adopted as mechanism.
- **Constructive / Bishop analysis** (Bishop 1967; Bishop–Bridges 1985; Bridges–Richman 1987; Simpson
  2009). **Th 10.9 (`Th_coqc`):** **cotransitivity** is the constructive substitute for trichotomy,
  matching A8. Bishop reals (Cauchy-with-modulus) = our `ℝ`-as-readout (`Dr`); **located sets** ↔
  admissible distance maps on `G_λ`-fibers; **LPO/WLPO/LLPO** rejected — the same move as A8's ban on
  pre-stability limits (`finite_diagnostic`). **What we add beyond Bishop:** limits are a *derived,
  declared, post-stability* readout (not a definitional primitive), and a genuine discrete calculus
  (`D_ε, I_ε`, FTCC, `δ_R`) Bishop lacks.
- **Category / type theory** (Mac Lane 1998; Grothendieck SGA1; Jacobs 1999; Johnstone 2002;
  Hofmann–Streicher 1998; HoTT 2013; Coq `Coq.Classes.Setoid`). `G_λ` is an **idempotent endofunctor /
  reflector** (`finite_diagnostic`); the admissible description `E=Ẽ∘G_λ` is a **comma-category /
  Kan-extension** factorization (`Th_coqc`-elig); sets-as-`G_λ`-fibers = a **Grothendieck fibration**
  (indexed-set semantics); equality `=_λ` = a **coequalizer / smallest congruence**. **Admissible
  descriptions are Setoids** — the direct Coq formalization vehicle (`Th_coqc`). **CAVEAT (`+ℝ-Open`):**
  a **topos** structure is explicitly NOT claimed.

## 10.8 Mined confirmations from the machine-checked corpus (research_universal_solver)

Each is an existing `Th_coqc` witness that grounds a textbook claim:
- **RD1–RD9 → `D ≅ ℕ`** (Peano-compatibility) · **RDL** 4-valued paraconsistent core (Belnap–Dunn FDE) ·
  **cosmogenesis order backbone** (`δ_R` → asymmetry → temporal order → `τ_c` seed → atomicity) ·
  **causal order `≺` and `L_R` structural facts** (bridge to the spine `K·L_R`) · **genesis-chain
  integration (M2) + readout-lossiness (CG-05A)** · **coupled discrete-spine stability** on the graph
  carrier · **the info-operator keystone `B(Φ,Φ)=I(Φ)`** (Dirichlet energy = retained information) ·
  **DEC toolkit** (discrete exterior calculus around `L_R`, 9 tools, minimal-cell scope) · **π and φ as
  readout-invariants** (reconstruction limits, not root objects; `Dr`). *(Witnesses: `RD.v`, `RDL.v`,
  `RDL_Distinguishability.v`, `RDL_CausalOrder.v`, `RDL_GenesisLink.v`, `RDL_SpineGraph*.v`,
  `URCF_RD_All.v`, `DEC_TOOLKIT.md`.)*

## 10.9 The honest Open frontier (`+ℝ-Open` / `Dr` — named, not hidden)

Continuum limit `L_R → □` (d'Alembertian) · a full **topos** completeness of the substrate ·
**Hauptvermutung** (uniqueness of a faithful causet embedding) · the **strong** law of large numbers ·
`π`/`φ` as exact objects (they stay readout-invariants) · general `ε–δ` existence without a stability
witness. These are the declared boundary; the book states them as Open and predicts the readout, per
Part 0.

---

# Appendix A — The contaminated-concept → discrete-replacement table

| contaminated concept | injection | discrete-correct replacement |
|---|---|---|
| real number ℝ / completeness | I1 | ℝ = readout (regular Cauchy of ℚ); √2, π non-readouts (`InfoIrrationalNonReadout`) |
| the point (`r=0`) | Z1 | a node / retained distinction (graph vertex) |
| zero as occupied | Z1/Z3 | refused non-readout, or the `L_R` kernel = indistinguishability (not a void) |
| `+∞` / `N→∞` / limit that lands | I3/I4 | ℚ has no `+∞`; a limit is the finite approach, never the endpoint |
| infinite divisibility `h→0` | I2 | finite step / `τ_c` floor (Th 2.9) |
| angle / degree | I1 (inverse trig) | overlap fraction (Def 4.2a) / turning number (Def 4.2b) |
| continuity / smooth (ε–δ over ℝ) | I1+I2 | discrete Lipschitz; ε–δ is a derived `+ℝ` rung (Th 3.9) |
| distance = coordinate difference | ℝ-frame | accumulated retained resistance along optimal path (Def 4.1) |
| line / continuum as substrate | primitive continuum | continuum = readout of the discrete graph (Pr 3.2) |
| π, e, φ as numbers | transcendental-as-real | readout-invariants (`Pi_as_Readout_Invariant`) |
| trichotomy / total ≤ / LUB | LPO/WLPO omniscience | cotransitivity + Cauchy-complete + finite lattice (Th 3.7–3.8, Pr 3.1) |
| derivative / integral = continuum limit | I2 | discrete `Δ`,`Σ`, discrete FTC (Th 3.2–3.3) |
| operator on a continuum (`∂²`) | I2 | graph Laplacian `L_R` (Th 4.3); `∂²` a `+ℝ` readout |

# Appendix B — Machine-checked theorem index (tier · witness)

`RDL.v` (RDL logic, 8 thm, `Th_coqc`) · `RD.v` + `RDL_Distinguishability.v` (D semiring/order/PA/
discrete-floor, `Th_coqc`; `Con_PA_classical` `+classic`) · number ladder `ℤ/ℚ/ℝ`
(`PGFT_Roots_of_Mathematics_and_Geometry` corpus, **123 constructive theorems axiom-free**, classical
capstone on `classic` alone) · `RDL_CausalOrder.v` (`lap`,`B` mechanics, `Th_coqc`) ·
`InfoIrrationalNonReadout`, `InfoZeroInfinityReciprocal`, `InfoAgencyZeroNonReadout`,
`InfoOperatorLosesPropertyAtEndpoints` (non-readout theorems, `Th_coqc`) · continuum-analysis rungs
(`RDL_ContinuumLimit`, `RDL_TaylorLimit`) `+ℝ-axioms`.

# Appendix C — Axiom-dependence discipline

Author `.v` files with **explicit ∀-premises, never `Section`/`Hypothesis`** (the source-scan reads
those as axioms). A result true only because its premises have no ℚ witness is a *schematic
conditional* — say so. `coqc` exit 0 + `Print Assumptions` *Closed* is the only ticket to `Th_coqc`.

---

## Roadmap (honest frontier — what this edition states vs. what remains)

**Stated & machine-checked:** RDL logic; `δ_R→D→ℤ→ℚ→ℝ` to the ordered-field / Cauchy-complete /
lattice level; discrete calculus; metric-space + betweenness geometry; the Laplacian operator
mechanics; the non-readout theorems and the endpoint principle. **In progress:** the operator
keystone `B(Φ,Φ)=I(Φ)` (Th 5.1). **Deferred / imported (`+ℝ`/`Open`):** the full continuum
derivative-integral tower, continuum geometry (manifolds, curvature), and the physical readouts
(spectra → masses) built on top.

---
*Information Discrete Mathematics — developed by **Yaoharee Lahtee**. Readout-not-truth applied to
the foundations, from the retained difference up. AI-assisted; the core stance and results are the
author's. Tiers are honest; where the continuum enters it is flagged, never smuggled.*
