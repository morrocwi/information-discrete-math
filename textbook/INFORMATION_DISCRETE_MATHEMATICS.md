# Information Discrete Mathematics & Calculus
## A Foundation from the Retained Difference — axioms, definitions, operators, theorems, principles, and a complete discrete calculus

**Developed by Yaoharee Lahtee.**

> **Edition note (v1.0.0 — release; completeness-first, proofs next).** This release organises the
> existing knowledge base and re-synthesises it from the latest findings into one coherent
> foundation, so it can be **used to do physics calculations precisely** in the readout-first
> framework. It prioritises **complete coverage** — from the roots up through a full information
> discrete calculus, the powerful analytic tools, and the reconciliations with the external record.
> **Proofs are stated by reference to the machine-checked witnesses where they exist and are
> otherwise `[results-first]` sketches deferred to the next version (v-proofs).** The goal is the
> closed, usable skeleton, not yet the full proof tower.

## Contents

- **Part 0** — Foundations of the foundation (the commitment; injected infinities/zeros)
- **Part 0.5** — The reader, resolution, and coarse-graining (the substrate: `A`, `G_λ`, admissible `E=Ẽ∘G_λ`, sets/functions/equality, S-layers, A8)
- **Part I** — Retained-Distinction Logic (RDL)
- **Part II** — The primitive `δ_R` and the genesis of number (`RD1–RD9`, `D`)
- **Part III** — The number tower `ℤ→ℚ→ℝ` (the continuum as a readout)
- **Part IV** — Geometry from retained difference (distance = resistance; angle = overlap)
- **Part V** — The retained-information operator `L_R` (`B(Φ,Φ)=I(Φ)`)
- **Part VI** — The continuum as a readout; the injected-infinity diagnosis
- **Part VII** — Complete operator reference (`¬∧∨→↔∀∃`, `= ≠ < ≤`, `+ − × ÷ ^ √ log`); §7.0 the information language
- **Part VIII** — Information discrete calculus (`D_ε`, `I_ε`, FTCC, series, spectral window)
- **Part IX** — Powerful tools re-adapted (Ramanujan summation, Euler–Maclaurin, zeta reg., q-calculus, …)
- **Part X** — Integrated extensions (pairs/products/functions from `δ_R`; cardinality; analysis; probability; geometry-from-the-graph; and reconciliations with causal-set theory, network/spectral-graph theory, Bishop, category theory, Shannon)
- **Part XI** — Closing the continuum (discrete derivative/integral/limit/ODE/special-function; the closure theorem)
- **Part XII** — Abstract algebra as retained symmetry (group = `Aut(F,O)`; ring/field; Lagrange; Galois)
- **Part XIII** — Linear algebra as the algebra of `L_R` (ℚ-vector space; metric; determinant; exact solve)
- **Part XIV** — Complex analysis as the rotation-readout of retained phase (`i` = quarter-turn; roots of unity; holomorphy; residue)
- **Part XV** — Combinatorics & graph theory (the native home of `δ_R`; `L_R` connectivity; matrix–tree; Euler χ)
- **Part XVI** — Measure theory & functional analysis (discrete measure; `L^p`; finite spectral theorem; Riesz)
- **Part XVII** — Category theory in the readout vocabulary (`G_λ` reflector; fibration; setoids; finite Yoneda)
- **Part XVIII** — Statistics & inference (retained-frequency estimation; a test IS a verdict; Bayesian reweighting)
- **Part XIX** — Optimization (gradient = `D_ε`; convexity; Lagrange; exact-`ℚ` linear programming)
- **Part XX** — The continuum-maya bridge (the continuum constructed as a readout, `Λ`, and computed with; exact FTCC core)
- **Part XXI** — The frontier without the continuum: paradox dissolution (topology · manifolds · PDE — the decisive stance)
- **Appendices A/B/C** — contaminated-concept table · machine-checked theorem index · axiom-dependence discipline
- **Appendices D/E** — validation: 1000 problems ประถม→ปริญญาเอก (1000/1000) · 100 continuous problems reproduced from the discrete (100/100)

## Using this to calculate physics (the release purpose)

To compute a physical quantity in this framework: (1) declare the **resolution `λ`/`ε`** and the
**admissible readout** `E=Ẽ∘G_λ` (Part 0.5); (2) express the quantity in the **operator language**
(Part VII §7.0) and the **causal finite-`ε` calculus** (Part VIII: `D_ε`, `I_ε`, FTCC) — never a
continuum primitive; (3) read spectra / mass-ratios / distances from `L_R` and Born-rule **overlap
fractions**, not from angles or coordinates (Parts IV–V, VII); (4) if a divergent or asymptotic
expression appears, use the **re-adapted tools of Part IX** (regularization = the finite retained
readout), declaring the limit only after an **A8 stability** proof; (5) tier every result
(`Th_coqc`/`finite_diagnostic`/`Dr`/`+ℝ-Open`) and refuse the continuum endpoints. The pre-write
checklist of the companion skill enforces this.

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
- **`Th_coqc-elig`** / **`finite_diagnostic`** — a finite, decidable computation or proof *eligible* for
  Coq (all objects finite lists over decidable-equal `ℚ`) but not necessarily checked yet; or a numeric
  readout reproduced to a **declared tolerance**. The working tag from Part VIII onward.
- **`Dr`** — a stance / definition / interpretation over checked pieces (design-narrative).
- **`+ℝ-Open`** (a.k.a. **`Open`**) — genuinely unsettled, or needs the completed continuum (`+reals`).
  Stated and predicted as a readout, never smuggled in as a premise.

**The load-bearing rule.** Never assert *all/every/universal* over a finite witness set without
tagging `Dr`. Never put a continuum name on a finite analogue. Never claim to *solve* a continuum
question — diagnose it as a non-readout and predict the readout. The boundary between the provable
and the Open **is** the boundary of the infinity axioms.

## Notation

`δ_R` primitive retained difference · `D` the naturals-as-semiring · `ℤ,ℚ,ℝ` the number tower ·
`≺` retained order · `L_R` the graph Laplacian (retained-information operator) · `⟨·,·⟩_G` the
retained inner product · `Th` theorem, `Def` definition, `Ax` axiom, `Pr` principle ·
`Verdict(ACCEPT/HOLD/BLOCK)` the fail-closed result type and `eq_eps`/`solve_obstruction` the numeric-
honesty discipline of `tools/idm_discipline.py` (truthy only on `ACCEPT`; used from Part XVIII on).

> **On the `Th_coqc` witnesses (warrant disclosure).** Most `Th_coqc` citations of a bare witness file
> (`RD.v`, `RDL.v`, …) point to the **external machine-checked corpora** — `research_universal_solver`,
> `readout_genesis`, `readout_universe` — where those `coqc`-verified proofs live (Appendix B/C). In
> addition, this repository now ships its **own** axiom-free witnesses in **`formal/IDM_FiniteWitnesses.v`**
> (Coq 8.20; `coqc` exit 0, `Print Assumptions` = *Closed under the global context* for every result) —
> currently the operator keystone Th 5.1 `B(Φ,Φ)=I(Φ)` (`IDM_Keystone.v`), plus Th 10.1 (Kuratowski pair
> injectivity), §15.2 handshake, §15.3 pigeonhole, §17.2 finite-Yoneda, §12.2 semiring distributivity
> (`IDM_FiniteWitnesses.v`). Where no witness exists yet, the tag is `Th_coqc-elig` (eligible, not yet
> checked), never a bare `Th_coqc`.

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

## 0.3 What a number, a unit, a symbol, and an equation ARE (a philosophy of mathematics)

Every mathematical object admits **two levels of account, and is never only one** — a distinction of
pure philosophy of mathematics (designation vs constitution; token vs type), not of any doctrine.

- **The conventional (designative) level** — what the object is *as it appears to a reader*: a
  **readout** `r=O(X)` at a declared resolution `λ`, an admissible designation `E=Ẽ∘G_λ`.
- **The ultimate (constitutive) level** — what it is *in its root constitution*: **retained
  distinction** `δ_R=(a♯b)` and the structure `L_R` it induces. Meaning is generated *downstream* of
  the retained trace; a domain name is a **translation** `q_D` (with `q_D∘F=F♯∘q_D`), **never a new
  root** [epistemic-foundation synthesis, Lahtee 2026].

Read through both levels:

- A **number** is neither a Platonic object nor a bare mark. It is a **readout-invariant of a
  retained-distinction structure**: the numeral *designates*, the equivalence class `[X]` under
  reader-equivalence (`X∼X' ⟺ O(X)=O(X')`) *constitutes*. (`π`, `φ` are the worked case — §4.4.)
- A **unit** is not physical stuff; it is a **calibration/gauge on readouts** — a choice of scale on
  the retained metric `⟨·,·⟩_G`. Changing units is a reader-relabelling that preserves every readout:
  a redundancy, not a fact.
- A **symbol** is not the thing; it is a **stable reader-label** for an equivalence class. One class
  may bear many symbols; use ≠ mention, token ≠ type.
- An **equation** `A=B` is not a metaphysical identity of objects; it is the **admissible
  indistinguishability** of two constructions to every reader (`O(A)=O(B)`) at a declared resolution —
  the operational `=` of §0.5.3 / §7.0.

**So the old dispute is sidestepped (`Dr` — this framework's reading, not a claim to have settled the philosophy-of-mathematics literature).** The number is not an abstract object floating free of any reader
(against Platonism), nor an empty inscription (against strict formalism), nor merely a useful fiction
(against fictionalism): it is the **invariant of a reading** — conventional in its appearance,
constitutive in its retained structure, and neither without the other. **Governing principle:** never
import a mathematical object as a primitive premise; *earn* it as a downstream readout of retained
distinction, tier-tagged.

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

## 4.4 The constants of geometry are readout-invariants of quotient grammars — geometry closed

The recurring constants of geometry are **not** signatures imposed on nature, nor a catalogue of
coincidences; each is the **invariant of a recurring quotient grammar** — it appears only after a
structural reduction, and is refused where the reduction fails. *(Lahtee 2026, `π,φ` standalone
synthesis; tiers below are exactly its claim-gate ledger.)*

- **`π` = the calibrated invariant of compact retained closure** (order-reversal witness `Th_coqc`-elig; the metric-calibration route is `+ℝ-Open`). Two roots,
  one number: (i) an involutive nontrivial adjacent **order reversal** carries the exchange factor
  `r=−1=e^{iπ}` (Th 4.4, exact under the ordered-tape axioms; the same `k`-odd witness that forces
  `k=3` → SU(3), §II); (ii) a continuous compact transport closes on a **topological circle** `θ∈ℝ/Tℤ` and an **isotropic
  Euclidean metric calibration** gives `C/R=2π`. **This second route uses the completed real circle, so it
  is `+ℝ-Open`, not `Th_coqc`** — it is stated and predicted, not proved axiom-free (§10.9). The native,
  contamination-free content of `π` is route (i), the finite order-reversal phase; `π` is *not* inserted at
  the root — route (i) is what compact closure reads out, and route (ii) is its continuum readout.
- **`φ` = the Perron invariant of minimal closure-continuation transfer (`Th_coqc`).** The least
  nontrivial two-step transfer `K_F=[[1,1],[1,0]]` (Fibonacci) has characteristic `λ²−λ−1=0`, so its
  Perron–Frobenius eigenvalue is `φ=(1+√5)/2` (Th 4.5, algebraically exact). Independently, the
  retained-history fusion sector (gates H1–H7 → a unitary fusion category) forces the minimal
  noninvertible frontier `τ⊗τ≅1⊕τ` with **`FPdim(τ)=φ`** — a *fusion/history* dimension, **not** an
  ordinary carrier dimension (Cor 4.1: no finite-dimensional fibre functor, since `d²=1+d` has no
  integer solution). `φ` is irrational *because* it is a history dimension, not a count.
- **The golden rotation `θ_G=2π/φ²≈137.5°`** (`Th_coqc`-elig: exact algebra + number theory). Combining a compact
  phase (`π`) with the minimal-memory transfer (`φ`) gives nonresonant generation on a closed phase;
  its continued fraction `[1;1,1,…]` is extremal for rational approximation (Hurwitz–Markov), which is
  the precise, `Dr`-fenced meaning of "most irrational" — it *delays* low-order phase locking. **Do
  not** read this as "every spiral/growth system is golden": the *universal golden nature* claim is
  **rejected** (negative controls: compact closure without minimal transfer gives `π` without `φ`;
  minimal transfer on a line gives `φ` without `π`; an arbitrary logarithmic spiral has a free growth
  rate; a Fibonacci count can be purely combinatorial).
- **Why the same constants recur across domains (the closure principle, `Dr`).** if domains `D_a` each
  admit a translation `q_a:D_a→Q` to a shared structural quotient, and the observables factor through
  it (`O_a=Õ∘q_a`), the *same* invariant appears in all of them **without any system transmitting a
  number to another** — recurrence is quotient-equivalence, not numerical transmission. "`π` is return;
  `φ` is growth" made precise: `π` = calibrated invariant of compact closure, `φ` = Perron invariant
  of minimal closure-continuation transfer.

**Geometry closes here, uncontaminated** (its *finite* content; the completed-manifold/topology frontier stays `+ℝ-Open`, §10.9): distance is retained resistance (§4.1); betweenness is
Tarski over the discrete metric (§4.2); angle is the overlap fraction, never a continuum degree
(§4.2); curvature is the second retained difference with a discrete Gauss–Bonnet/Bianchi (§10.10); and
its constants (`π,φ,θ_G`) are readout-invariants of quotient grammars — each derived, tier-fenced, and
free of any injected continuum, Platonic constant, or "universal golden" overclaim.

---

# Part V — The retained-information operator (information is the central axis)

## 5.1 The keystone (Def 5.1 + Th 5.1)

- **Def 5.1 (retained-information density).** `I(Φ) :=` the distinguishability of neighbouring
  retained states of the field `Φ` on the graph.
- **Th 5.1 (keystone — `Th_coqc`, witness `formal/IDM_Keystone.v: keystone_B_eq_I`).** **`B(Φ,Φ) = I(Φ)`**:
  the operator's Dirichlet energy **is** the retained-information functional. In the edge assembly of
  `L_R = D_W − W` this is the identity `ΦᵀL_RΦ = Σ_edges w·(Φ_i − Φ_j)²`, proved axiom-free over `ℚ`
  (`Print Assumptions` = *Closed under the global context*); its companion `keystone_nonneg` shows
  `L_R` is positive semidefinite (the retained metric is a genuine seminorm). *Information — not length,
  not energy — is the central quantity; geometry and distance are readouts OF it.*

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
forward reference. **Base already machine-checked (economize):** the semiring the pair layer stands on
is `formal/RD.v` (`RD3_succ_ne_zero`, `RD4_succ_inj`, `add_assoc`, `add_comm`, `mul_add` distributive,
`Th_coqc`); only the Kuratowski pair / product / function step below is the new sketch.

- **Singleton / pair fibers.** for `a,b` in fiber `X` at resolution `λ`: `{a}_λ`, `{a,b}_λ` are
  sub-fibers selected by finitely many `∼_λ`-classes (fiber-formation is already licensed, §0.5.3).
- **Ordered pair (`δ_R`-Kuratowski).** `(a,b)_λ := {{a}_λ, {a,b}_λ}`; degeneracy `a =_λ b` is *detected*
  as a `δ_R` count (`|outer|=1` vs `2`), not hidden. **Th 10.1 (injectivity, `Th_coqc` — witness `formal/IDM_FiniteWitnesses.v: kuratowski_pair_inj`):**
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
- **Same size** = an admissible bijection `≈_λ`. **Th 10.3 (`Th_coqc`, witness `formal/IDM_FiniteWitnesses2.v: same_set_same_size`):** for `NoDup` lists,
  same members ⇒ equal count (equinumerosity = admissible bijection), by finite induction — axiom-free.
- **Potential infinite** = a `δ_R`-generated tape `Tape(n+1)=σ(Tape n)`, each stage finite with
  `Counting(Tape n)=n+1`. **Th 10.4 (`Th_coqc`, witness `formal/IDM_FiniteWitnesses2.v: tape_count_succ` / `tape_no_terminal`):**
  strict growth ⇒ no terminal stage (an unbounded *process*, no completed object).
- **Actual infinite refused — analytically.** **Th 10.5 (`Th_coqc`, witness `formal/IDM_FiniteWitnesses2.v: no_infinite_readout`):** `∀ l:list A, ∃n, length l = n`.
  Every readout inhabits `list A`, which has *no infinite inhabitant* — actual `∞` is excluded because
  the readout type never had room for it, not by fiat. *(Cantor-style comparison of two tapes' growth
  is per-schema `finite_diagnostic`, not one closed theorem.)*

## 10.3 Finite satisfaction `⊨_λ` (and an honest downgrade)

- **Th 10.6 (`Th_coqc`-elig):** `⊨_λ` — a decidable, computable Tarski recursion of satisfaction on a
  finite domain + finite formula at a fixed coarse-graining level. **Existing witness to REUSE (economize):**
  the readout-bivalence consistency layer is already machine-checked — `formal/RD_ConPA_ReadoutBivalence.v`
  (`soundnessC_param`, `consistencyC_param`, `Con_PA_classical_param`, `Th_coqc`); only the general
  finite `⊨_λ` recursion is the new sketch, and it builds on that file.
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
for integral tails). The uniform pattern below, repeated five times, **is** the rung: (1) a *decidable*
finite-`ε` predicate over `ℚ`, (2) a *stability witness* (a computable modulus map, or an explicit
Euler–Maclaurin remainder bound), (3) only then a *declared* `ε→0` readout — never a bare limit
primitive. This closes the panel-flagged stub with all five sub-rungs stated, not just sketched.

### 10.5.1 Sequence limit (finite-`ε` Cauchy first)

- **Def 10.5a (`ε`-stability).** For `a : D → ℚ` and `ε ∈ ℚ_{>0}`, `a` is **`ε`-stable from `N`** iff
  `∀ m,n ≥ N, |a_m ⊖ a_n| ≤ ε`. `N_ε(a)` := least such `N`, when it exists — a **decidable, bounded
  search** for any concrete computable bound, hence checkable per `(a, ε)` instance. **Tier:
  `finite_diagnostic`.**
- **Th 10.10 (declared-stability limit, `Th_coqc`-elig scaffold / `+ℝ-Open` at the quantifier).** If
  `ε ↦ N_ε(a)` is itself an admissible (computable) *modulus map* — witnessed, not merely asserted to
  exist for every `ε` — define the readout limit `L(a)` as the `∼_λ`-class of the eventual band
  `⋂_ε [a_{N_ε}⊖ε, a_{N_ε}⊕ε]`. This is the `ε→0` statement, licensed **only** once the modulus map is
  exhibited — the Bishop "Cauchy-with-modulus" move (§10.7), re-derived here as the A8 stability
  declaration. **Per-witnessed-instance: `finite_diagnostic`. The unrestricted "`∀` sequence `∃`
  modulus" existence claim (classical Cauchy completeness with no witness supplied) stays `+ℝ-Open`** —
  ties to §10.9.

### 10.5.2 Series convergence (partial sums + Euler–Maclaurin tail)

- **Def.** `S_n := I_1 a[n]` (§8.2 antidifference / discrete FTC) — the finite partial sum, already
  primitive, no new object.
- **Th 10.11 (series = sequence-limit stability of `(S_n)`).** Convergence of `Σ a` is *by definition*
  `ε`-stability (10.5a) of the partial-sum sequence `(S_n)` — no independent series primitive is
  introduced, closing a common redundancy. **Tier: `finite_diagnostic`**, same status as 10.5a.
- **Euler–Maclaurin upgrade.** For `a` extending to a `D_ε`-differentiable `f` (10.5.4), §9.2's exact
  remainder `R_{m,ε}` gives an **explicit, computable** `N_ε` formula — replacing an existential
  Cauchy claim with a constructed witness. This is the concrete route by which many closed-form series
  move from `+ℝ-Open` (bare existence) to `finite_diagnostic` (explicit modulus) — the "Euler–Maclaurin-
  based" stability condition this rung is scoped to supply.

### 10.5.3 Continuity algebra (`(δ_R, ε)`-continuity, closed under `+ · ∘`)

- **Def 10.5b.** `f = Ẽ∘G_λ` is **`ε`-continuous at `x` with modulus `η`** iff `∀x'` with `x' ∼_η x`
  (i.e. `|x'⊖x| ≤ η`), `|f(x')⊖f(x)| ≤ ε` — a finite, decidable pointwise bound, no limit invoked.
- **Th 10.12 (algebra closure, `Th_coqc`-elig).** Explicit bound arithmetic, each step a triangle-
  inequality identity in `ℚ` (decidable order, no LEM/choice/funext — `field_simplify`-class):
  - sum: `(f+g)` is `(ε₁+ε₂)`-continuous at modulus `min(η₁,η₂)`;
  - product (bounded `f,g`): `(f·g)` is `(|f(x)|ε₂+|g(x)|ε₁+ε₁ε₂)`-continuous at `min(η₁,η₂)`;
  - composition: `(g∘f)` is `ε₂`-continuous at the modulus `η₁` that `f` needs to land inside `g`'s own
    `(ε₂, η₂)` pair — a finite chain of two decidable searches, not an infinite regress.
  *Proof sketch (why axiom-free-eligible):* every inequality above is a finite arithmetic fact over
  `ℚ` reached by `⊖`-triangle-inequality plus case-split on the (decidable) order `≤` — no non-
  constructive step, so the Coq witness needs only `Qorder`/`field_simplify; lra`-class tactics, no
  classical axiom.
- **Continuum rung.** "`∀ε>0 ∃η>0`" continuity is licensed exactly as 10.5a: `Th_coqc`-eligible **once**
  `η(ε)` is an admissible modulus map (available in closed form for the `D_ε`-algebra-closed primitives
  of Th 10.8); **`+ℝ-Open` in general** — unwitnessed `ε–δ` existence is the named Open item (§10.9).

### 10.5.4 Derivative (`D_ε` exact algebra ⊢ declared-stability rung)

- **Primitive (unchanged).** `D_ε f := (f[n]⊖f[n−1])/ε` (causal secant, §8.1/§0.5.4).
- **Th 10.8 (restated, `Th_coqc` AS STATED — the exact finite-`ε` algebra, zero `O(ε)` residue):**
  `D_ε(f+g)=D_εf+D_εg` · `D_ε(f·g)[n]=f[n]D_εg[n]+g[n−1]D_εf[n]` ·
  `D_ε(g∘f)[n]=Δg[f[n−1],f[n]]·D_εf[n]` (secant slope across the actual jump) ·
  **FTCC** `I_ε(D_εf)[N]=f[N]−f[0]` exactly (telescoping). Each discharges by `field_simplify; ring` /
  finite induction — no `Reals`, axiom-free.
- **Def 10.5c (finite-`ε` differentiability, the new rung).** `f` is **finite-`ε` differentiable at `x`**
  iff the `ε`-indexed family `(D_{ε_k} f(x))_k`, `ε_k → 0` an admissible refinement sequence, is
  `ε'`-stable in the sense of 10.5a — i.e. the difference-quotient family must itself pass the Cauchy-
  stability test **before** `f'(x) := lim_{ε→0} D_ε f(x)` is licensed. This is the declared-stability
  gate the task asks for, applied to the derivative.
- **Th 10.13.** For `f` built from primitives closed under Th 10.8's algebra, the modulus for Def 10.5c
  is computable *from the algebra itself* (chain of secant bounds through `+ · ∘`) — **`finite_diagnostic`,
  `Th_coqc`-eligible per closed-form `f`.** General existence for an arbitrary admissible `f` — no
  algebraic modulus supplied — stays **`+ℝ-Open`**: this is the one place, flagged already at Th 10.8,
  where the secant-slope reading of `D_ε(g∘f)` can silently diverge from the naive difference-quotient
  reading if resolution is not matched between `f` and `g`; restated here explicitly as the derivative
  rung's Open boundary, not smoothed over.

### 10.5.5 Integral (`I_ε` exact FTCC ⊢ Euler–Maclaurin-certified rung)

- **Primitive (unchanged).** `I_ε f[a,b]` = the retained aggregation / antidifference (§8.2), with
  **FTCC** `I_ε(D_εf)[N]=f[N]⊖f[0]` exact (Th 10.8) — no `O(ε)` residue, algebraic telescoping.
- **Def 10.5d (finite-`ε` integrability, the new rung).** `f` is **finite-`ε` integrable on `[a,b]`**
  iff the family `(I_ε f[a,b])`, indexed by an admissible shrinking `ε`, is Cauchy-stable (10.5a) — and
  that stability is **certified**, not asserted, via the §9.2 exact Euler–Maclaurin identity
  `I_ε f[a,b] = (ε/2)[f(b)+f(a)] + Σ_{k=1}^m (B_{2k}/(2k)!) ε^{2k} [D_ε^{2k−1}f(b) − D_ε^{2k−1}f(a)] +
  R_{m,ε}`, giving an **explicit computable bound** `|I_ε f − I_{ε/2} f| ≤` (Bernoulli-term sum) `+
  R_{m,ε}` — this is the "Euler–Maclaurin/FTCC-based" stability condition the task names, made literal.
- **Th 10.14.** For `f` with a declared bound on `D_ε^{2k−1}f` over `[a,b]` up to order `m` (an
  explicit, checkable `finite_diagnostic` hypothesis — a finite list of numeric bounds, not a
  quantifier), `R_{m,ε} → 0` as `ε→0` is machine-checkable at each declared `m`: **`finite_diagnostic`,
  upgrading to `Th_coqc`-eligible for polynomial/rational `f`** where the Bernoulli tail is exactly
  finite (`m` can be taken large enough that `R_{m,ε}=0` identically — no genuine limit needed for this
  class). `∫_a^b f := lim_{ε→0} I_ε f[a,b]` is licensed **only** after this certificate is produced.
  **General `f` with unbounded higher `D_ε`-derivatives stays `+ℝ-Open`** — no certificate, no license.

### 10.5.6 Summary (the rung, once)

| Sub-rung | Finite-`ε` primitive | Stability witness | `ε→0` readout tier |
|---|---|---|---|
| 10.5.1 limit | `ε`-stability `N_ε(a)` (Def 10.5a) | computable modulus map `ε↦N_ε` | `finite_diagnostic` (witnessed) / `+ℝ-Open` (bare `∃`) |
| 10.5.2 series | partial sum `S_n=I_1a[n]` + 10.5a | Euler–Maclaurin `R_{m,ε}` (explicit `N_ε`) | `finite_diagnostic` |
| 10.5.3 continuity | `(ε,η)`-continuity (Def 10.5b) | `η(ε)` modulus, closed under `+·∘` (Th 10.12) | `Th_coqc`-elig (algebra) / `+ℝ-Open` (unwitnessed `ε–δ`) |
| 10.5.4 derivative | `D_ε f` exact algebra (Th 10.8) | Def 10.5c Cauchy-stability of the `D_ε` family | `finite_diagnostic`/`Th_coqc`-elig (closed-form `f`) / `+ℝ-Open` (general) |
| 10.5.5 integral | `I_ε f` exact FTCC (Th 10.8) | Def 10.5d Euler–Maclaurin remainder bound | `finite_diagnostic`/`Th_coqc`-elig (poly/rational `f`) / `+ℝ-Open` (general) |

*Open (named, tied to §10.9):* general `ε–δ` / Cauchy-modulus existence with **no** exhibited witness,
for an unrestricted admissible `f` — the frontier this skeleton fences rather than hides.

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
  "order + number = geometry"; `I_ε` over the chain recovers the finite-`ε` line-element. **This is
  already machine-checked IN-HOUSE (`Th_coqc`, economize — do not re-derive): `formal/InfoCausalPartialOrder_attempt.v`**
  proves `rank` (= minimal-step), `prec_irrefl` / `prec_trans_thm` / `prec_asymm` (a strict partial
  order), and `in_diamond` (the interval `0≺z≺3`) with its members counted — the diamond-volume-by-
  counting identity as an internal theorem, not merely an external citation. **Local
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
  carrier · **the info-operator keystone `B(Φ,Φ)=I(Φ)`** (Dirichlet energy = retained information — **Th 5.1, now `Th_coqc`**, local witness `formal/IDM_Keystone.v`) ·
  **DEC toolkit** (discrete exterior calculus around `L_R`, 9 tools, minimal-cell scope) · **π and φ as
  readout-invariants** (reconstruction limits, not root objects; `Dr`). *(Witnesses: `RD.v`, `RDL.v`,
  `RDL_Distinguishability.v`, `RDL_CausalOrder.v`, `RDL_GenesisLink.v`, `RDL_SpineGraph*.v`,
  `URCF_RD_All.v`, `DEC_TOOLKIT.md`.)*

## 10.10 Geometry from the causal graph (network/graph theory + the QG export, reconciled)

*(From the resume run: network/spectral-graph reconciliation + the causal-quantum-gravity spine export.)*

- **Resistance distance = our distance (Th 10.15, `Th_coqc`).** `d_λ(i,j) := (e_i − e_j)ᵀ L_R⁺ (e_i − e_j) ∈ ℚ`
  (`L_R⁺` the pseudoinverse) — the graph resistance distance IS the retained-resistance metric of §4.1,
  now a *forced rational geometry* of the causal graph. Distance stops being primitive. *(Klein–Randić
  1993; Doyle–Snell 1984.)*
- **`L_R` structural facts to REUSE (Th_coqc).** `L_R` rational, symmetric, PSD; **nullity = number of
  connected components** (`lap_kills_constants` generalized); **Kirchhoff / matrix-tree** (spanning-tree
  count = any cofactor); `L_sym`, `L_rw` are rescalings of the same operator. *(Spectral/algebraic graph
  theory: Chung 1997; Godsil–Royle 2001.)*
- **Random walk / heat kernel = `D_ε` / `I_ε` / FTCC (`finite_diagnostic`).** the discrete heat step
  `(1 − τ L_R)` and the random walk on the graph are instances of the causal calculus (Part VIII) — the
  transition operator is `I_ε` of the Laplacian flow; no new machinery.
- **Discrete curvature = second `δ_R`** (combinatorial defect-sum `Th_coqc`-elig; the `2π`/radian-angle Gauss–Bonnet form is a `+ℝ-Open` continuum readout, §4.4). curvature is the second retained
  difference; a **discrete Gauss–Bonnet** and a **discrete Bianchi** (abelian, from commuting finite
  differences) hold; **Forman–Ricci** `F(e)=4−deg(u)−deg(v)` is native graph curvature with *zero*
  continuum limit — offered *after the source repo's honest retraction of eight attempts to force a
  Schwarzschild curvature onto `L_R`* (a worked non-readout-discipline case study). *(Forman 2003;
  Bombelli et al. for the order-signature.)*
- **Discrete Lorentzian signature + boost-invariant box symbol (Th_coqc).** a sign (−1 timelike / +1
  spacelike) on each causal edge gives a causal bilinear form invariant under order-preserving
  relabelling ("discrete boosts"): `box_quad(a_tt,a_xx) = −2a_tt + 2a_xx` transforms exactly as
  `(g²(1−v²))·box_quad` (`=1` under the Minkowski constraint) — self-adjointness, Euclidean reduction,
  and boost-invariance all `Th_coqc/ℚ`. **Fences:** box=dispersion is a *bounded restatement* (M,K
  posited), NOT a one-root derivation; the continuum `□`-limit is `Open`; QNM ~0.1–1.2% match is
  `finite_diagnostic` only (transcendental target = non-readout). *(cqg spine export.)*
- **Spectral ceiling / `τ_c` floor (Th_coqc).** a Rayleigh-quotient bound gives the spectral ceiling
  without any eigenvalue-existence theory — the exact `λ₂` (Cheeger/Fiedler) as a real number stays
  `+ℝ-Open`; use Sturm brackets for a `ℚ`-enclosure instead.

## 10.11 Mined from readout_universe and readout_genesis (logic dynamics + root axioms)

- **Logic as residual flow (`finite_diagnostic`, readout_universe C1–C3).** inference is a **monotone
  descent**: under constant evidence a Lyapunov functional `V` decreases to `0` (C1: `V→8.2e-26`, 0
  violations); a settled conclusion **revises** under an evidence flip (C2: `+1→−1`). So *proof itself
  is a discrete gradient flow of retained distinction* — the dynamical face of Part I's logic.
- **Vagueness / Sorites, machine-checked axiom-free (`Th_coqc`, `code/UPL_Sorites.v`, readout_universe
  C7).** the sorites is resolved on the monotone scope without a sharp cutoff — reuse this witness for
  the book's treatment of a "gap ≠ assertion" (Ax-RDL4): a heap-predicate is a coarse-grained readout,
  not a knife-edge.
- **The nine root axioms `RD1–RD9` ("the information DNA", readout_genesis PART I / readout_universe
  v2.0).** the exact same `RD1–RD9` that generate `D` (Part II) are the shared root of both repos —
  confirming the number tower's axioms are the canonical foundation, not this book's invention.
- **Geometry-dominance defect bound (`finite_diagnostic`, readout_genesis).** the living-geometry mixing
  current (`II.8a`) carries a *computable* defect bound (per-operator boundary `h_exact≈0.6827`) — a
  concrete finite readout of "how much geometry moved", usable in Part IV/X's curvature layer.

## 10.12 Reconciliation with Shannon information theory (กระทบยอด)

*(Shannon 1948; Cover–Thomas 2006; Kolmogorov 1965; Chaitin 1966.)*
- **Entropy = expected retained-distinction count (`Dr`/`Th_coqc`-elig).** `H = Σ p_i · log_2(1/p_i)`
  is the *expected number of binary distinctions (bits)* to name one retained state — literally the
  expectation (§10.6) of the `log` operator (§7.3). Information "is" retained distinction; entropy is
  its retained average. **Native, not imported.**
- **Channel = coarse-graining `G_λ`.** a noisy channel is exactly a `G_λ` that discards sub-resolution
  distinctions; capacity = the most retained distinction that survives it.
- **Data-processing inequality = coarse-graining monotonicity (`Th_coqc`-elig).** post-processing
  (another admissible map through `G_λ`) can never *increase* retained distinguishability:
  `I(X;Z) ≤ I(X;Y)` for `X→Y→Z` — a one-line consequence of `E = Ẽ∘G_λ` (composition of coarse-grainings
  loses, never gains). This makes the DPI a theorem about admissible descriptions.
- **Kolmogorov complexity = minimal generating record.** the complexity of a readout = the length of
  the shortest `δ_R`-record whose self-composition (`^`, §7.3) regenerates it — the same "generator
  readout" as `√`/`log`, now on programs. Randomness = a record with no shorter generator (a
  non-compressible retained distinction).

## 10.9 The honest Open frontier (`+ℝ-Open` / `Dr` — named, not hidden)

Continuum limit `L_R → □` (d'Alembertian) · a full **topos** completeness of the substrate ·
**Hauptvermutung** (uniqueness of a faithful causet embedding) · the **strong** law of large numbers ·
`π`/`φ` as exact objects (they stay readout-invariants) · general `ε–δ` existence without a stability
witness. These are the declared boundary; the book states them as Open and predicts the readout, per
Part 0.

---

# Part XI — Closing the continuum: nothing computed by "infinity" is left standing

Parts VI and VIII established *that* the continuum is a readout; this Part discharges the promise
operationally. For every operation classical analysis defines through a completed limit — derivative,
integral, limit, differential equation, special function — we give a **finite-ε discrete method that
returns the same benchmark answer without the continuum as a primitive**. The `ε→0` *statement* stays
`+ℝ-Open` (A8); the *readout* — the number — is reproduced at finite `ε`. **Global result: 100/100
world-benchmark continuous problems reproduced** (Appendix E). No computation is left that requires an
actual infinity.

## 11.1 The discrete derivative (replaces the difference-quotient limit)

`D_ε f[n] = (f[n]−f[n−1])/ε` (causal/backward) or the central `(f[n+1]−f[n−1])/2ε`; the ε→0 primitive
derivative is refused, and **Richardson extrapolation** `(4·D_{ε/2}−D_ε)/3` removes the leading `O(ε)`
so the finite readout matches `f′` to machine precision. The exact algebraic rules (`Th_coqc`, §8/§10.5)
are the *native* content: `D_ε(f+g)=D_εf+D_εg`, `D_ε(fg)[n]=f[n]D_εg+g[n−1]D_εf`, chain via the secant
slope — **zero `O(ε)` residue**, no continuum. *(Validated: 16/16 derivatives, Appendix E.B.)*

## 11.2 The discrete integral (replaces the Riemann/Lebesgue continuum integral)

Aggregation `I_ε` = prefix sum; the composite trapezoid `I_ε f = ε(½f_0 + f_1 + … + ½f_N)` with the
first **Euler–Maclaurin** endpoint correction `−ε²/12·(f′_N−f′_a)` (§9.2) reproduces `∫` to high order.
**FTCC** `I_ε D_ε f = f[N]−f[0]` is exact by telescoping (`Th_coqc`). Improper/oscillatory integrals are
closed by **admissible reparametrization** (`∫₀^1 ln(1/x)dx` via `x=e^{−t}` → `∫₀^∞ t e^{−t}dt`; `Γ(½)`
via `x=t²` → `2∫₀^∞ e^{−t²}dt`) and by **half-period summation + Euler acceleration** for conditionally
convergent tails (Dirichlet `∫₀^∞ sinx/x = π/2`). *(Each `∞` bound is a **finite truncation to a declared cutoff** plus the E–M/acceleration tail — `finite_diagnostic`; the completed `∫₀^∞` stays `+ℝ-Open`.)* *(Validated: 34/34 integrals, Appendix E.A.)*

## 11.3 The discrete limit (replaces the ε–δ limit taken as a primitive)

A limit is a **declared, post-stability readout**, never a definitional given (A8). The finite-ε method
evaluates the sequence at `n = M·2^j` and applies **Richardson extrapolation on `h=1/n`**, killing each
term of the asymptotic expansion in `1/n` successively — so `(1+1/n)^n→e`, `H_n−ln n→γ`,
`n(e^{1/n}−1)→1`, `(n!)^{1/n}/n→1/e` are all recovered to `1e−6+` from purely finite data. The value is
the **A8 plateau**, tagged `finite_diagnostic`; the completed `ε→0` object stays `+ℝ-Open`.
*(Validated: 15/15 limits, Appendix E.C.)*

## 11.4 The discrete ODE (replaces the continuous initial-value problem)

`y′=f(x,y)` **is** the difference equation `y[n+1]=y[n]+I_ε(f)` — the continuous ODE was only ever a
stability limit of this. RK4 is the fourth-order `I_ε` quadrature of the vector field across one step;
run to the endpoint it reproduces the exact closed form (`y′=y⇒e`, `y′=2xy⇒e^{x²}`, `y′=1/(1+x²)⇒`
`arctan`, Riccati `y′=y²⇒1/(1−x)`). No continuum flow is invoked — only accumulated retained steps.
*(Validated: 12/12 ODEs, Appendix E.D.)*

## 11.5 Discrete special functions (replaces continuum special functions)

Each "transcendental" function is a **convergent discrete process** — a series, a quadrature, or a
continued fraction — never a continuum primitive: `Γ` = discrete quadrature of `t^{s−1}e^{−t}` (or the
factorial recurrence); `ζ(s)` = Euler–Maclaurin-accelerated partial sum (giving `ζ(2)=π²/6`, `ζ(4)=π⁴/90`,
`ζ(3)` Apéry, `ζ(½)` regularized); `erf` = its Maclaurin series; `Catalan`, `Li₂`, elliptic `K`, Bessel
`J₀` = their defining discrete sums/products; the Wallis product and Dirichlet `Si(∞)=π/2` from finite
acceleration. *(Validated: 23/23 special-function values, Appendix E.E.)*

## 11.6 Closure theorem (the continuum is dispensable)

> **Closure (`Dr`, computationally witnessed).** Every continuum computation tested — derivative,
> integral, limit, ODE, special-function value — is reproduced by a finite-ε discrete method to the
> declared tolerance, using only `ℚ`-data, `D_ε`, `I_ε`, admissible reparametrization, and
> A8-declared acceleration. The continuum enters *nowhere* as a primitive; it is recovered *everywhere*
> as a readout. Witness: **100/100**, `validation/hundred_continuum_problems.py` (Appendix E).

This does **not** claim the classical `ε→0` existence theorems (they stay `+ℝ-Open`, §10.9); it claims
the strictly stronger operational fact that *the answers those theorems name are obtained without the
limit being taken as real*. The honest fence: the readout is reproduced; the completed continuum is
still declared Open and predicted, per Part 0.

---

# Part XII — Abstract algebra as retained symmetry (group · ring · field)

Algebra is not a theory of abstract symbols floating above nothing; in this foundation it is the
**bookkeeping of the relabelings that preserve every readout**. Structure comes first (`δ_R`, the
operators of Part VII), and algebra is the study of its symmetries and closures.

## 12.1 A group is the automorphisms of a retained structure

For a retained structure `F` with reader `O`, define the **admissible automorphisms**
`Aut(F,O) := { g : g relabels F and O(g·X)=O(X) for all readouts }` — the reversible relabelings that
change no distinction any reader can detect (gauge-type redundancies, §III of the `π`/`φ` synthesis).

- **Group axioms are theorems, not decrees.** Composition of readout-preserving relabelings is
  readout-preserving (closure); it is associative because relabeling-composition is; the empty relabel
  is the identity; readout-preservation is reversible (each `g` has `g⁻¹`). **Th 12.1
  (`Th_coqc`-elig):** `(Aut(F,O), ∘)` satisfies the group axioms — each step a finite decidable check
  on `∼_λ`-classes. No axiom is imported; the group *is* the symmetry of a reading.
- **Finite groups only, as readouts.** A group is presented by its finite Cayley table — a finite
  readout. Infinite/continuous groups (Lie groups) are `+ℝ-Open`: their finite-dimensional
  *representations* are the readouts we admit (§12.3), not the completed manifold.
- **Symmetry = indistinguishability under a relabel** ties directly to the `L_R` kernel (§V): elements
  a reader cannot separate sit in one orbit.

## 12.2 Rings and fields are the operator algebra, already grounded

The number tower *is* the worked example, so this chapter only makes the abstract shape explicit:

- A **ring** = a carrier with `⊕` (an abelian group, §7) and `⊗` (a monoid, §7) linked by distributivity
  — all of which are the retained-operator laws of Part VII. **`D` is a commutative semiring** (RD1–9,
  `Th_coqc`); **`ℤ` is a ring** (Grothendieck completion, §III); **`ℚ` is a field** (field of fractions,
  `÷` total except `÷0` refused, §7). **Th 12.2 (`Th_coqc`-elig, mined):** these hold with the ring/field
  axioms as *derived* identities of `⊕,⊗,÷`, not primitives.
- **`÷0` is the one refused operation** — a field is "`ℚ` minus the non-readout `1/0`", exactly the
  partition-with-no-parts refusal (§7). The field structure is honest about its one hole.

## 12.3 Representations, order, and solvability

- **Representation = action on retained amplitudes.** A representation sends group elements to admissible
  operators on a `ℚ`-space of retained states; its **dimension is an integer** (a carrier count). This is
  why `SU(3)` appears with `k=3` from the ordered-tape odd-closure witness (§II), and why the fusion
  dimension `FPdim(τ)=φ` is explicitly **not** an ordinary representation dimension (§4.4, Cor 4.1) — the
  integrality of ordinary dimensions is a `Th_coqc`-elig finite fact.
- **Lagrange / orbit–counting = finite counting theorems.** `|H|` divides `|G|`; orbit size divides
  `|G|` — **Th 12.3 (`Th_coqc` for the cyclic case — witness `formal/IDM_FiniteWitnesses2.v: lagrange_order_div`:
  the order `n/gcd(g,n)` divides `|ℤ_n|=n`; the general Cayley-coset partition is `Th_coqc`-elig):** a
  decidable finite readout.
- **Galois solvability = radical-tower reachability (`Dr`).** A readout is "solvable by radicals" iff it
  is reachable from `ℚ` by a finite tower of `⊕,⊗,÷,^,√` (§7 operators). The abstract correspondence
  (solvable group ↔ radical tower) is `Dr`/`finite_diagnostic` here — stated as the framework's reading,
  with the general theorem over the completed field left `+ℝ-Open`.

---

# Part XIII — Linear algebra as the algebra of `L_R`

Linear algebra is not an add-on; the central object of this whole foundation — the
retained-information operator `L_R` (Part V) — *is* a linear operator, and its spectral theory is where
"information is the central axis" becomes computational.

## 13.1 Vector spaces over `ℚ` (finite, no smuggled completeness)

A **retained vector space** is finite `ℚ`-linear combinations of retained states — closure under `⊕`
and `ℚ`-scaling (§7). Basis = a maximal set of mutually distinguishable states (a `δ_R`-independent
set); **dimension = the number of retained distinctions** (`Th_coqc`-elig, a finite count). Completeness
of the space (Hilbert-space limits) is **`+ℝ-Open`** — we work in the `ℚ`-dense core and take the
completion only as a declared readout (A8).

## 13.2 The retained metric, `L_R`, and the spectral readout

- **Inner product = the positive retained metric** `⟨x,y⟩_G = xᵀ G y`, `G≻0` (§III of the `π`/`φ`
  synthesis, Eq. 4). It makes retained load nonnegative and fixes which relabelings are admissible
  (the automorphisms of Part XII are the `G`-isometries).
- **`L_R = D_W − W`** (graph Laplacian, Part V) is the canonical self-adjoint operator. Its keystone is
  `B(Φ,Φ)=I(Φ)` — the Dirichlet energy *equals* the retained information (the keystone **Th 5.1**, `Th_coqc`, witness `formal/IDM_Keystone.v`). Its
  **kernel is the indistinguishability space** (constant-on-components readouts); its **spectrum is the
  set of retained modes**; its **Perron–Frobenius eigenvalue** carries the dominant retained scale (the
  `φ` of the minimal transfer `K_F`, §4.4).
- **Determinant = signed retained volume; rank = retained-distinction count.** Both are exact `ℚ`
  computations (validated, Appendix D.L3); **matrix–tree** links `det` of an `L_R` minor to spanning
  trees (§15.3).

## 13.3 Solving linear systems (exact, no continuum)

`Ax=b` over `ℚ` is solved by finite Gaussian elimination — an **exact `Th_coqc`-elig** procedure with
no rounding and no limit. Eigenvalue/eigenvector computation for the finite `L_R` is a finite readout;
the only `+ℝ-Open` step is the completion to real spectra of an infinite operator (the continuum limit
`L_R→□`, §10.9).

---

# Part XIV — Complex analysis as the rotation-readout of retained phase

The complex numbers are introduced here **without** the mystical "`√(−1)`". A complex number is a
retained **phase**, and `i` is the generator of a quarter-turn — an order-4 element of the rotation
readout, nothing more occult than the order-reversal sign of §4.4.

## 14.1 `ℂ` as `ℚ`-pairs with a rotation operator

`ℂ_ℚ := ℚ×ℚ` with `⊕` componentwise and `⊗` the rotation-scaling `(a,b)·(c,d)=(ac−bd, ad+bc)`. Then
**`i=(0,1)` is the quarter-turn**: `i²=(−1,0)` because two quarter-turns are a half-turn — the same
order-reversal that carries phase `π` (§4.4, Th 4.4). **`i=(0,1)` is defined constructively as the positive quarter-turn, not as a square root of a negative
real** — the contamination "`√−1` as a real-line object" is refused. (Order 4 alone fixes only the pair
`{i,−i}`; singling out `i` needs the orientation choice built into `(0,1)`.) The object is a
finite cyclic phase. `e^{iθ}` is the **compact-closure readout** `U(θ)` with `U(θ+2π)=U(θ)` (Eq. 11 of
the `π`/`φ` synthesis).

## 14.2 Roots of unity, Euler's identity, and closure

- **Roots of unity = finite cyclic readouts.** The `n`-th roots are the `ℤ_n` phase group (validated,
  Appendix D.L4; `ℤ_3={1,e^{2πi/3},e^{4πi/3}}` is exactly the Standard-Model center quotient, §III of
  the synthesis, Eq. 14). Finite, exact.
- **Euler's identity `e^{iπ}+1=0`** is the order-reversal invariant `e^{iπ}=−1` (§4.4) — a
  `Th_coqc`-elig algebraic fact about the compact phase, not a statement needing the real exponential's
  completion.

## 14.3 Holomorphy, contours, and residues (discrete)

- **Holomorphic = a phase-transport that closes.** A map is admissible-analytic when its transport
  `U'_{j←i}=h_j U_{j←i} h_i⁻¹` (Eq. 5) has trivial holonomy on contractible cycles; the **holonomy**
  `H_C=∏_{e∈C} U_e` (Eq. 6) records whether translations close consistently.
- **Contour integral = `I_ε` around a finite cycle; the winding number is a retained integer count.**
  Cauchy's theorem is the closure condition (a distinction transported around a closed path returns to the
  same readout class ⇒ zero net accumulation). The **winding number** `n(C,a)` is an integer property of
  the cycle (a retained turning count); the **residue** `Res(f,a)` is a *distinct* object — the Laurent
  coefficient `a₋₁` of the function, generally not an integer. The residue theorem multiplies them:
  `∮_C f dz = 2πi·Σ_k n(C,a_k)·Res(f,a_k)` — both sides finite readouts (`Dr`/`finite_diagnostic`). Full
  complex analysis over the completed plane
  (analytic continuation, the ℝ/ℂ-completeness theorems) stays **`+ℝ-Open`**, per Part 0.

---

# Part XV — Combinatorics and graph theory (the native home of `δ_R`)

This Part is last only in order, not in fundamentality: `δ_R=(a♯b)` **is an edge**, so a retained
structure **is a graph**, and counting distinctions is the most native computation in the whole book.
Everything here sits at the native tier (`Th_coqc`-elig — finite, decidable, over `ℚ`).

## 15.1 Counting is retained-distinction counting

`Counting_λ(S)=|[S]_λ|` (§10.2) — the de-duplicated count of `∼_λ`-classes, always a finite natural.
Binomial/multinomial coefficients count admissible selections; **Catalan numbers, partitions, Stirling
numbers, Bernoulli numbers** are all validated finite readouts (Appendix D.L3–L5). Generating functions
are **readout-series** — the same finite-`ε` series objects of Part IX, now indexing combinatorial
families.

## 15.2 Graphs, the Laplacian, and connectivity

A graph *is* the retained structure. `L_R=D_W−W` is its Laplacian (Part V); therefore every
graph-theoretic invariant is an `L_R` readout:

- **Connectivity = `ker L_R`.** The number of connected components equals `dim ker L_R` (constant-on-
  component vectors) — the kernel is literally the indistinguishability space (§V). `Th_coqc`-elig.
- **Spectral gap = `λ₂(L_R)`** controls mixing/expansion — the same spectral quantity that the
  particle-graph diagnosis reads (`falsify_particle_graph`, memory) and that the `π`/`φ` transfer
  selects (§4.4).

## 15.3 Trees, Euler characteristic, and finite guarantees

- **Matrix–tree theorem.** The number of spanning trees `= det` of any cofactor of `L_R` — a bridge to
  linear algebra (§13.2), an exact `ℚ` determinant (`Th_coqc`-elig).
- **Euler characteristic `χ=V−E+F`** and the **discrete Gauss–Bonnet / Bianchi** identities (§10.10)
  make curvature a second retained difference summing to a topological invariant — geometry and
  combinatorics meet with no continuum (`Th_coqc`-elig in the mined DEC toolkit).
- **Pigeonhole and Ramsey-type bounds** are finite existence readouts: with more distinctions than
  classes, two must collide — a one-line `δ_R` counting argument (`Th_coqc`, witness
  `formal/IDM_FiniteWitnesses.v: pigeonhole`; the handshake identity `Σdeg=2|E|` is `handshake_lemma`).

**Breadth closure.** With Parts XII–XV the foundation now carries dedicated, tier-honest chapters for
algebra, linear algebra, complex analysis, and combinatorics/graph theory — each derived from `δ_R`,
`L_R`, and the Part VII operators, none importing a continuum primitive. The remaining declared frontier
(topology/topos, Hauptvermutung, completed continuum limits, exact `π`/`φ` objects) stays `+ℝ-Open`
(§10.9), stated and predicted, never smuggled in.

---

# Part XVI — Measure theory and functional analysis (the discrete floor of analysis)

Measure and function-space theory are usually built on a completed σ-algebra and a complete normed
space. Here both are **readouts of the discrete**: a measure is a retained count, an integral is `I_ε`
against it, and the operator theory is the finite spectral theory of `L_R` (Part XIII). Completeness is
the one place the continuum enters, and it is fenced `+ℝ-Open`.

## 16.1 Measure = retained count; integral = `I_ε` against it

- **Discrete measure.** `μ_λ(S) := I_ε(1_S)` — the retained count of admissible cells in `S` (§10.6).
  It is **finitely additive by construction** (`Th_coqc`-elig): disjoint fibers add their counts.
  σ-additivity is the **A8-stable limit** of finite additivity — stated, and `+ℝ-Open` for the completed
  σ-algebra (a countable union that "lands" is a non-readout).
- **Integral.** `∫ f dμ_λ := I_ε(f·1_S)` — the Lebesgue integral is the readout of this finite retained
  sum; the classical `∫` is recovered by the continuum-maya bridge (Part XX target) wherever A8-stable.
- **Measurable function is *replaced by* the admissible map** `E=Ẽ∘G_λ` (§0.5) — a stipulated discrete
  substitute, not proven equal to classical measurability (which is the strictly stronger σ-algebra
  preimage condition): here measurability is admissibility at
  the declared resolution; no separate σ-algebra machinery is imported.

## 16.2 `L^p`, the retained inner product, and finite functional analysis

- **`L^p` norm = retained-`p` aggregation** `‖f‖_p := (I_ε |f|^p)^{1/p}`; `‖·‖_2` comes from the positive
  retained metric `⟨f,g⟩_G = I_ε(f̄ g)` (Part XIII). **Cauchy–Schwarz** `|⟨f,g⟩| ≤ ‖f‖₂‖g‖₂` is a finite
  `Th_coqc`-elig inequality over `ℚ` (discrete sum form).
- **Bounded operator = finite retained coupling.** On the `ℚ`-space, an operator is a finite matrix;
  `L_R` is self-adjoint, and the **spectral theorem holds exactly** for the finite `L_R` (`Th_coqc`-elig, finite linear algebra; orthonormal
  retained-mode basis, real `ℚ`-approx eigenvalues — Part XIII). The completion to an infinite Hilbert
  space and its spectral measure are `+ℝ-Open`.
- **Riesz representation (finite).** Every admissible linear functional on the finite `ℚ`-space is
  `f ↦ ⟨v,f⟩_G` for a unique retained `v` — `Th_coqc`-elig, by finite linear algebra. The infinite-
  dimensional Riesz theorem is `+ℝ-Open`.

---

# Part XVII — Category theory in the readout vocabulary

The substrate's universal properties are categorical, and §10.7 already identified the pieces. This Part
makes them a chapter: category theory here is the theory of **admissible maps between retained
structures**, with `G_λ` the organizing functor. It is the abstract restatement of the readout-first
principle, not an external framework imported on top.

## 17.1 The category of retained structures

- **Category `𝓡`.** Objects = retained structures (`G_λ`-fibers); morphisms = admissible maps
  `E=Ẽ∘G_λ`; composition = map composition (associative); identities = the trivial relabel. A finite
  presentation is a finite readout (`Th_coqc`-elig).
- **`G_λ` is an idempotent reflector** (endofunctor with `G_λ∘G_λ ≅ G_λ`, `finite_diagnostic`, §10.7) —
  coarse-graining is a categorical reflection onto the admissible subcategory.
- **`E=Ẽ∘G_λ` reads as a Kan-extension / comma factorization** (`Dr` — the factorization exists; the
  universal property is stated as the framework's reading, not proved here): every admissible description
  factors through the reflector.

## 17.2 Fibrations, congruences, and the finite Yoneda reading

- **Sets-as-`G_λ`-fibers = a Grothendieck fibration** (indexed-set semantics); **`=_λ` = a coequalizer /
  smallest congruence** (§10.7) — categorical restatements, tier `Dr` (no universal-property proof given here). **Admissible descriptions are setoids** — the direct Coq vehicle
  (`Th_coqc`-elig; the setoid mechanization lives in the external corpus, no local witness).
- **Functor = readout-preserving map; natural transformation = an admissible family** of such maps.
- **Finite Yoneda (the readout-first principle, categorically):** a retained object is determined, up to
  `∼_λ`, by the family of its admissible readouts `⟨O(g·−)⟩` — "an object *is* its readouts"
  (`Th_coqc` for the finite readout-vector fact — witness `formal/IDM_FiniteWitnesses.v: finite_yoneda`;
  the full enriched Yoneda is `Dr`).
- **`+ℝ-Open`:** a **topos** structure on the substrate is explicitly **not** claimed (§10.7 caveat).

---

# Part XVIII — Statistics and inference (bounded-reader inference, fail-closed)

Above probability (§10.6) sits inference: estimating and testing from finite retained data. In this
framework inference is done by a **bounded reader** who returns a **verdict**, never an omniscient
pronouncement on a "true parameter" — the reader/resolution discipline of Part 0.5, applied here as a
**bounded-judge law** for statistics (every tester is itself a bounded reader), unified
with the numeric-honesty discipline (`idm_discipline`).

## 18.1 Estimation as retained-frequency readout

- **Estimator = retained readout.** The sample mean is `Ĉ_N = I_ε(sample)/N`; consistency is the **A8
  plateau** of `Ĉ_N` (the LLN of §10.6). A **confidence interval** is a **declared-resolution interval**
  around the retained estimate — its width is the declared `ε`, not a claim about a completed sampling
  distribution.
- **Bayesian update = retained reweighting.** Posterior `∝` prior `×` likelihood is a reweighting of
  retained-distinction mass; the **Born-rule normalization** `p_i=|a_i|²/Σ|a_j|²` (§10.6, `Th_coqc` in the corpus; Part V Pr 5.1) is
  the special normalized case. Tier `finite_diagnostic`/`Dr`.

## 18.2 A hypothesis test IS a verdict

A test returns a **`Verdict(ACCEPT/HOLD/BLOCK)`** (`idm_discipline`), fail-closed:

- **ACCEPT** — the effect reads **distinct at the declared resolution** (`¬ eq_eps` on the retained
  contrast); **HOLD** — underpowered / budget-exhausted / assumptions unread (never a silent "no
  effect"); **BLOCK** — a modelling assumption is violated (e.g. a sorites/non-transitivity trap in the
  comparison chain, `eq_chain_guard`). The `p`-value is a declared-resolution overlap fraction, not a
  gate to be crossed. This eliminates the silent-wrong-answer class (a `HOLD` is not a `NULL`).
- **Bounded-judge law.** The tester is itself a bounded reader; "significance" is a readout at declared
  resolution, never a truth certificate (`Dr`).

---

# Part XIX — Optimization (retained stationarity, obstruction-zeroing)

Optimization is finding where a retained cost stops changing, at a declared resolution. Its objects are
the tools this book already ships: the gradient is `D_ε`, the search is `I_ε` of the descent field, and
the stopping test is a fail-closed verdict.

## 19.1 Gradient, convexity, stationarity

- **Gradient = `D_ε`.** The objective `J` is a retained cost readout; its gradient is the finite
  difference `D_ε J` (exact in the causal form, §8). **Stationarity** is `D_ε J = 0` at the declared
  resolution — solved by **obstruction-zeroing** (`solve_obstruction`, `idm_discipline`), which returns
  `ACCEPT` only when the residual reads zero and `HOLD` otherwise.
- **Convexity = nonnegative retained second difference.** `D_ε² J ≥ 0` (a decidable `ℚ` sign check)
  certifies that **any retained stationary point is a global minimum, *if one exists*** (`Th_coqc`-elig);
  it does **not** give existence or uniqueness on its own (`J=x` is convex with no minimum; `J=const` has
  every point a minimizer). **Uniqueness needs *strict* convexity `D_ε²J > 0`** (plus boundedness/
  coercivity for existence). Convexity is a finite readout, not a statement about a smooth Hessian over `ℝ`.

## 19.2 Constrained optimization and linear programming

- **Lagrange multipliers = retained stationarity on the admissible fiber.** Constrained optimality is
  `D_ε J = Σ λ_k D_ε g_k` on the `G_λ`-fiber cut out by the constraints; the KKT feasibility /
  complementary-slackness check is `Th_coqc`-elig (a finite `ℚ` verdict); its equivalence to the classical
  KKT theorem is `Dr`.
- **Linear programming = exact `ℚ` vertex enumeration.** The optimum sits at a polytope vertex; simplex
  is an **admissible path on the polytope graph** (ties to `L_R`/graph, Part XV) with exact `ℚ`
  pivots — `Th_coqc`-elig, no floating error.
- **Gradient descent = `I_ε` of the negative-gradient field** (an ODE, §11.4); convergence is the **A8
  plateau**, reported as a fail-closed verdict (`HOLD` if the budget ends before the plateau). Continuous
  convex analysis over `ℝ` (subdifferentials, completed minimizers) stays `+ℝ-Open`.

*(Validated: `validation/breadth2_problems.py`, 34/34 — Cauchy–Schwarz, finite spectral theorem, Riesz,
`G_λ` idempotence, finite Yoneda, LLN plateau, Bayesian/Born normalization, test-verdict ACCEPT/HOLD,
sorites BLOCK, convexity, obstruction-solve, exact-`ℚ` LP, gradient descent, Lagrange.)*

**Breadth closure (extended).** With Parts XVI–XIX the foundation adds measure/functional analysis,
category theory, statistics/inference, and optimization — each derived from `δ_R`, `L_R`, `I_ε`/`D_ε`,
and the verdict discipline, none importing a continuum primitive. The completed-continuum pieces
(σ-algebra limits, infinite Hilbert spaces, topos structure, continuous convex analysis) are named
`+ℝ-Open` (§10.9), and the **continuum-maya bridge** (Part XX, backlog) is the capstone that will
construct the continuum layer *as a readout* and prove it computes identically.

---

# Part XX — The continuum-maya bridge (the continuum constructed as a readout, and computed with)

The book's central claim — *the continuum is a readout of the discrete* — is here made a **constructive,
testable bridge**, not merely a stance. We build the continuum layer explicitly *from* the discrete, as
an **appearance** (a readout), and show it computes the classical continuum answers identically wherever
those answers exist.

## 20.1 The construction `Λ`: discrete data → continuum-appearance

Define the bridge map
`Λ : (finite-ε discrete computation) → (continuum-appearance value)`
as the **A8-stable readout** of the finite-ε data — the plateau reached by the declared accelerator
(`limit_eps` / Euler–Maclaurin / Richardson, Part XI, `tools/idm_tools.py`). `Λ` is **total on
A8-stable inputs** and **refuses — returns `HOLD`** (a `Verdict`, `idm_discipline`) where no plateau
exists. So the continuum `Λ` builds is exactly the **computable appearance**; it never forms a
completed non-readout.

## 20.2 Faithfulness: the constructed continuum computes identically

- **Exact core (`Th_coqc`, witness `formal/IDM_Bridge.v`).** For the fundamental operation — the
  Fundamental Theorem — the bridge is **exact, zero residue**: `I_ε(D_ε f) = f[N] − f[0]` (FTCC,
  `FTCC_exact` / `FTCC_eps_exact`, proved axiom-free over `ℚ`; the `ε` cancels for every declared
  `ε ≠ 0`). The continuum's FTC is *recovered as a finite telescoping readout* — no limit is taken.
- **Numeric faithfulness (`finite_diagnostic`).** For derivative, integral, limit, ODE, and
  special-function operations, `Λ` reproduces the classical continuum value on every A8-stable case —
  **witnessed at 100/100** (Appendix E) and 34/34 (Appendix, Parts XVI–XIX).
- **Faithfulness statement (`Dr`, computationally witnessed).** *`Λ(discrete op) = classical continuum
  op` wherever the classical operation exists*, and the set where `Λ` refuses (`HOLD`) is **exactly**
  the `+ℝ-Open` non-readouts (§10.9). This upgrades the empirical 100/100 into a stated bridge
  property; the exact rung is machine-checked, the numeric rung is validated, and no completed
  continuum is ever formed.

## 20.3 The maya clause (honesty)

The constructed continuum is a **readout of the discrete** (conventional truth, §0.3) — an appearance,
never the ultimate object. The bridge is **one-way faithful** (discrete → appearance): it *predicts*
the readout on the Open frontier rather than closing it. Nothing here claims the classical `ε→0`
existence theorems; it claims the strictly operational fact that **the answers those theorems name are
obtained without the limit being taken as real.**

---

# Part XXI — The frontier without the continuum: paradox dissolution (a decisive stance)

Topology, differential geometry (manifolds), and PDE were listed `+ℝ-Open` (§10.9). This Part states
the **decisive position**: that mark is **not a computational gap** — it is the *deliberate refusal to
reify a non-readout*. **The actual continuum is not needed for *computing* any of these** — the
continuum-maya (Part XX, finite-ε) **computes them all, robustly**; for *stating and deciding* the
classical completed-continuum existence/uniqueness/cardinality questions themselves we take no position
and form no such object (they stay `+ℝ-Open` **by choice**). Every classical *paradox* in these areas is
an **artifact of injecting a non-readout into the computation**, dissolved the moment the injection is
refused — the classical question about the *object* is not thereby answered, only declined.

## 21.1 Stance: computation is fully covered, the continuum is optional

- **Topology** — the practical invariants are already discrete/combinatorial: connectivity `= ker L_R`
  (§15.2), Euler characteristic `χ = V−E+F` (§15.3), homology of a simplicial complex (finite linear
  algebra over `ℚ`). No completed point-set continuum is needed to compute them.
- **Manifolds / differential geometry** — curvature is the **second retained difference** with a
  **discrete Gauss–Bonnet** (§10.10, DEC toolkit): the vertex angle defects sum to `2πχ`. The **π-free
  content** is combinatorial and `Th_coqc`-elig — *the total defect is a topological invariant fixed by
  `χ`*; writing it with `2π` and radian incident angles is the **continuum readout** (route (ii) of §4.4,
  `+ℝ-Open`), a `finite_diagnostic` value at declared precision, not an exact `ℚ` readout.
- **PDE** — every PDE is *actually computed* by discretization (not "solved" in the classical
  existence/uniqueness sense); the finite-ε schemes of Part XI (`D_ε`,
  `I_ε`, the difference-equation ODE, §11.4) **are** the computation. The "continuum limit `L_R→□`"
  (§10.9) is the *appearance*; the computation lives at finite `ε`.

**So the stance is decisive:** we do not need the actual continuum to compute topology, geometry, or
PDE — the maya suffices, robustly, at every case that has an answer. What stays `+ℝ-Open` is only the
*completed continuum object itself*, which we **decline to form** — and that declination is precisely
where the paradoxes are dissolved.

## 21.2 Paradox dissolution — each paradox is an injected non-readout

Every famous paradox of the continuum arises from injecting a **non-readout** (`I1–I4` infinities /
`Z1–Z4` zeros, Part 0; the Axiom-of-Choice over an uncountable domain). Refuse the injection and the
paradox does not arise; the maya still returns the practical value. *(Diagnoses are `Dr`; the
computed values are `finite_diagnostic`.)*

| paradox (area) | injected non-readout | readout-first dissolution | the maya still computes |
|---|---|---|---|
| **Zeno** (motion/divisibility) | `I2` infinite subdivision `h→0` | finite `τ_c` floor (Th 2.9); motion = finite discrete steps | `I_ε` sums the finitely-many steps exactly |
| **Banach–Tarski** (topology/measure) | uncountable AC + **non-measurable sets** | a non-measurable set has **no admissible `G_λ` description** — it is not a readout; AC-over-uncountable is refused | `μ_λ` is always finitely additive; no readout is ever duplicated |
| **Continuum Hypothesis** (set theory) | the completed uncountable `|ℝ|` + intermediate cardinals | `|ℝ|` as a completed cardinal is a non-readout; only finite/countable retained counts exist (§10.2) | **dissolved, not decided** — the question never arises for readouts |
| **Weierstrass** (nowhere-differentiable) | completed `h→0` limit | at declared `λ` every readout function has a finite `D_ε`; "nowhere differentiable" is an `h→0` artifact | `D_ε` returns the slope at the declared resolution |
| **Gabriel's Horn** (finite volume, infinite area) | `I3/I4` reached `+∞` | both quantities are **finite readouts at the declared cutoff**; `+∞` is never reached | `I_ε` computes both to the cutoff — no paradox |
| **Koch / fractal** (infinite perimeter) | `I2` infinite iteration | finite iteration count; perimeter is finite at declared resolution | `I_ε` at resolution `λ` gives the finite perimeter |
| **Thomson's lamp / supertask** | completed infinite sequence | no completed infinite process (Th 10.4–10.5); the "final state" is a non-readout | the state after any *finite* stage is a plain readout |
| **Russell's paradox** (foundations) | unrestricted comprehension (set of all sets) | sets are `G_λ`-fibers (admissible, finite, no self-membership, §10.1); the paradoxical object is a non-readout | set operations on admissible fibers are decidable |
| **Skolem** (countable model of "uncountable") | absolute "uncountable" | "uncountable" is **readout-relative**, not an absolute property; no contradiction at the readout level | — |
| **Navier–Stokes blow-up / non-uniqueness** (PDE) | the completed continuum solution | the blow-up lives in the `+ℝ-Open` completed limit; the finite-`ε` scheme (run within its stability bound) returns a finite value at declared `λ` — the classical existence question is declined, not decided | the difference scheme (§11.4) computes the flow at declared `λ` |

**The decisive reading.** These are not open problems the framework *fails*; they are non-readouts the
framework *declines to inject*. The paradox is the symptom of the injection; refusing the injection is
the cure. The continuum-maya (Part XX) then supplies every value the working mathematician actually
needs — so the continuum is, for computation, **optional**. *(Honesty fence: this dissolves the
paradoxes and computes the readouts; it does not claim to have decided the classical questions in their
own completed-continuum terms — declining to form that object is the whole point, §0.3, §10.9.)*

## 21.3 The three frontier areas, made explicit — the paradox, and the computation that never hits it

*(Each is demonstrated numerically in `validation/paradox_dissolution.py`. Diagnoses `Dr`; computed
values `finite_diagnostic`; the discrete Gauss–Bonnet identity's π-free/combinatorial content is `Th_coqc`-elig, its `2π`/radian-angle form is a `+ℝ-Open` continuum readout — §4.4.)*

### Topology — the paradox: **Banach–Tarski** (a solid ball cut into finitely many pieces and
reassembled into *two* identical balls; measure is created from nothing).
- **Where it comes from:** the pieces are **non-measurable sets**, built with the Axiom of Choice over
  an *uncountable* index — pure non-readouts (`I1` + uncountable AC). Volume is "created" only because
  the pieces have no admissible volume readout to begin with.
- **Why our computation never hits it:** a readout region is a `G_λ`-fiber with a retained count
  `μ_λ = I_ε(1_S)`; **`μ_λ` is finitely additive by construction** (§16.1), so a finite decomposition
  and reassembly **conserves the count exactly** — you cannot read out `1` piece as `2`. The
  non-measurable "pieces" simply have no `G_λ` description, so they are never formed. *Computed:* split
  any finite region into disjoint parts and recombine — `μ_λ(whole) = Σ μ_λ(parts)` on the nose,
  every time (no doubling possible).

### Manifolds / differential geometry — the paradox: **curvature requires a smooth limit** (the
"how can a *polyhedron* have curvature — it's flat faces and sharp corners?" tension, and the
dependence of classical curvature on an `h→0` that never terminates).
- **Where it comes from:** injecting the smooth chart and `h→0` (`I2`) to define curvature pointwise on
  a continuum manifold.
- **Why our computation never hits it:** curvature is the **angle defect** concentrated at a vertex —
  a finite retained second difference — and **discrete Gauss–Bonnet** ties it to topology:
  `Σ_vertices (2π − Σ incident angles) = 2π·χ` (§10.10). No chart, no `h→0`. *Computed (`finite_diagnostic`
  — the `2π`/radian-angle form is the continuum readout, route (ii) of §4.4, `+ℝ-Open`):* for a
  tetrahedron the vertex defects sum to `4π = 2π·2` (χ = 2); for a cube likewise `2π·2`. The **exact,
  π-free** statement is combinatorial: the total defect is a topological invariant fixed by `χ`, with the
  surface built of flat faces.

### PDE — the paradox: **Navier–Stokes blow-up / ill-posedness** (does a smooth solution exist for all
time, or can it become singular — infinite velocity — in finite time?).
- **Where it comes from:** the question is posed in the **completed continuum**; the "blow-up" is a
  reached `+∞` (`I3`) inside an idealized `ℝ³×ℝ` that is itself a non-readout.
- **Why our computation never hits it:** a PDE **is** a difference equation (§11.4); the finite-`ε`
  scheme `y[n+1] = y[n] + I_ε(field)`, **run at a resolution satisfying the scheme's own declared
  stability bound (A8 — e.g. `r=αΔt/Δx² ≤ 1/2` for the explicit heat stencil)**, returns a finite readout
  at every step *inside that stability window* — there is no `+∞` to reach. *(Outside the window the
  explicit scheme itself diverges numerically; that is a discretization-stability failure, orthogonal to
  and not evidence of a continuum blow-up.)* *Computed (`finite_diagnostic`, at a stable `r`):* the LINEAR
  MODEL PDEs — heat `uₜ=uₓₓ` (explicit stencil, `r=0.25`) decaying a bump to its declared floor, and a
  transport step advancing at finite speed — return finite fields for all `n`, no blow-up. **Navier–Stokes
  itself (nonlinear, vortex-stretching) is not run here**; its completed-continuum existence/uniqueness
  question stays `+ℝ-Open` **by choice** — a distinct, declined question about a non-readout — while the
  finite-`ε` value the engineer needs is computed without paradox.

**Summary of the stance for the three areas:** the paradox is always in the *completed-continuum object*
(non-measurable set · smooth-limit curvature · reached `+∞`), never in the *computation*. Refuse the
object, keep the computation: topology by `μ_λ`/`L_R`, geometry by discrete Gauss–Bonnet, PDE by
finite-`ε` schemes — **all three computed robustly, none producing its paradox.**

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

**Local witnesses (this repo, `formal/*.v` — Coq 8.20, all axiom-free / *Closed under the global context*):** `formal/IDM_Keystone.v`: `keystone_B_eq_I` (Th 5.1, `B(Φ,Φ)=I(Φ)`) + `keystone_nonneg` (`L_R` PSD). `formal/IDM_FiniteWitnesses2.v`: `same_set_same_size` (Th 10.3), `tape_count_succ` (Th 10.4), `no_infinite_readout` (Th 10.5), `lagrange_order_div` (§12.3). `formal/IDM_FiniteWitnesses.v`: `kuratowski_pair_inj` (Th 10.1, §10.1) · `handshake_lemma` (§15.2) · `pigeonhole` (§15.3) · `finite_yoneda` (§17.2) · `semiring_distrib` (§12.2). Reproduce: `cd formal && coqc -q IDM_FiniteWitnesses.v` then `Print Assumptions`.

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

# Appendix D — Validation: 1000 problems, ประถม → ปริญญาเอก (the release dogfood)

The framework is exercised on **1000 problems across five levels**, each solved by a
framework-consistent method (exact `ℚ` operators / discrete causal calculus `D_ε`,`I_ε`,FTCC /
regularization-residue / asymptotics) and checked against an **independent reference**
(`fractions`, `sympy`, `mpmath`). Runnable: `validation/thousand_problems.py`.

| level | area | pass |
|---|---|---|
| **L1 ประถม** | arithmetic, fractions, order (`⊕⊗÷`) | 200/200 |
| **L2 มัธยม** | `^`,`√`, quadratics, arith/geom series, gcd, mod, discrete-`log` | 200/200 |
| **L3 ปริญญาตรี** | FTCC & causal product rule (exact `ℚ`), Faulhaber `Σiᵖ`, binomial, determinants, Stirling | 200/200 |
| **L4 ปริญญาโท** | `ζ(2k)` & `γ` via Euler–Maclaurin, recurrences, roots of unity, Chebyshev/LLN, Bernoulli | 200/200 |
| **L5 ปริญญาเอก** | `ζ(−1)=−1/12`, Abel/η sums, Apéry `ζ(3)`, Ramanujan `1/π`, partition asymptotics, continued fractions, Catalan, saddle-point Stirling | 200/200 |
| | **TOTAL** | **1000/1000 (100%)** |

**Honest reading (tier-aware).** L1–L3 are largely **exact `ℚ`** — there the framework's *own*
computation *is* the answer, so these validate the operator and discrete-calculus layers (FTCC and the
causal product rule hold with **zero residue**, `Th_coqc`). L4–L5 are **genuine numeric-vs-reference**:
finite-`ε` partial sums + Euler–Maclaurin reproduce `ζ(2k)`, `γ`, `ζ(3)` to `~1e-8`; regularization
gives `ζ(−1)=−1/12`, `1−1+1−…=1/2` (`finite_diagnostic`, post-A8-stability); Hardy–Ramanujan `p(n)` and
Stirling are **leading-order** (few-%), disclosed as such. An earlier draft showed 2 misses; detailed analysis found the CAUSE was **not the mathematics** but a
fragile test-harness step (`sympy.nsimplify`, a float→symbolic *heuristic*, was misused to compare
exact large rationals). Replaced by exact `ℚ` equality (`exact_eq`) — the robust long-term fix — after
which the suite is **1000/1000**. *(The lesson is itself the framework's: an exact readout must be
compared as an exact readout, never through a floating-point guess.)* *The framework computes the standard mathematics, grade-school
to frontier, without ever making the continuum a primitive.*

# Appendix E — Validation: 100 world-class CONTINUOUS problems reproduced from the discrete

**Purpose.** Appendix D showed the framework computes standard mathematics; this appendix discharges the
strongest claim — that the **continuum itself is dispensable**. Every problem here is one classical
analysis defines through a completed limit (integral, derivative, limit, ODE, special function); each is
solved by a **finite-ε discrete method only** (`I_ε` quadrature + Euler–Maclaurin, `D_ε` + Richardson,
finite-ε limit + Richardson-on-`1/n`, RK4 difference-equation, discrete series/quadrature) and checked
against the world benchmark. Suite: `validation/hundred_continuum_problems.py` (deterministic, 30-digit
`mpmath` reference; each method is a genuine discrete computation — no continuum solver is called).

| block | area | method (discrete) | pass |
|---|---|---|---|
| **A** | definite & improper integrals (`∫₀^1`, Gaussian, oscillatory, `∫₀^∞`) | `I_ε` trapezoid + Euler–Maclaurin; admissible reparametrization | 34/34 |
| **B** | derivatives at a point (polynomial, transcendental, `xˣ`) | `D_ε` central + Richardson | 16/16 |
| **C** | limits (`(1+1/n)ⁿ→e`, `H_n−ln n→γ`, `(n!)^{1/n}/n→1/e`, …) | finite-ε + Richardson on `h=1/n` (A8 plateau) | 15/15 |
| **D** | ODEs (linear, Riccati, `y′=2xy⇒e^{x²}`, `y′=1/(1+x²)⇒arctan`) | RK4 = 4th-order `I_ε` of the vector field | 12/12 |
| **E** | special functions (`Γ`, `ζ(s)`, `erf`, `Catalan`, `Li₂`, elliptic `K`, Bessel `J₀`, Wallis, Dirichlet) | defining discrete series / quadrature / product | 23/23 |
| | | **TOTAL** | **100/100 (100%)** |

**Honest reading (tier-aware).** The exact-`ℚ` rungs (FTCC, `D_ε` rules) carry `Th_coqc`; the numeric
rungs are `finite_diagnostic` — the *readout* is reproduced to the declared tolerance (`1e-6`–`1e-10`
typical; `1e-3`–`1e-4` disclosed per-line for genuinely singular integrands), while the completed `ε→0`
existence stays `+ℝ-Open` (§10.9). Two harness pitfalls were caught and fixed for the long term: (1) an
endpoint Euler–Maclaurin correction that stepped **outside** `[a,b]` and returned a complex value —
fixed to a one-sided *inward* difference; (2) a benchmark with a **sign error** in a Taylor coefficient
(`n⁴(cos(1/n)−1+1/2n²)→+1/24`, not `−1/24`) — the framework had the correct sign; the reference was
corrected. **The continuum enters nowhere as a primitive and is recovered everywhere as a readout — the
operational meaning of "closing the continuum" (Part XI).**

---

## Roadmap (honest frontier — what this edition states vs. what remains)

**Stated & machine-checked:** RDL logic; `δ_R→D→ℤ→ℚ→ℝ` to the ordered-field / Cauchy-complete /
lattice level; discrete calculus; metric-space + betweenness geometry; the Laplacian operator
mechanics; the non-readout theorems and the endpoint principle; **the operator keystone `B(Φ,Φ)=I(Φ)`
(Th 5.1, now machine-checked — `formal/IDM_Keystone.v`).** **Deferred / imported (`+ℝ`/`Open`):** the full continuum
derivative-integral tower, continuum geometry (manifolds, curvature), and the physical readouts
(spectra → masses) built on top.

---
*Information Discrete Mathematics — developed by **Yaoharee Lahtee**. Readout-not-truth applied to
the foundations, from the retained difference up. AI-assisted; the core stance and results are the
author's. Tiers are honest; where the continuum enters it is flagged, never smuggled.*
