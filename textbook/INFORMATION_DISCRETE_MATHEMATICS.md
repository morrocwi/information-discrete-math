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
