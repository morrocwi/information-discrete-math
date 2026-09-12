# Genesis Reader–Domain Foundation v1

**Status:** FREEZE CANDIDATE — formal/CI and F6 gates must pass before this document may be relabelled `FROZEN`  
**Date:** 2026-09-12  
**Mathematical proof owner:** `morrocwi/information-discrete-math`  
**Ontology lens:** `morrocwi/readout_genesis`  
**Provenance/status authority:** `morrocwi/toledo`  
**Toledo proposal review:** `morrocwi/toledo#36`

> This foundation is domain-independent infrastructure. It does not solve, or claim to solve, any Millennium Prize Problem. Finite theorem, domain theorem, finite-uniform bridge, global semantic bridge and exact Clay target remain separate obligations.

## 1. Reuse-first result

This work follows Toledo `TG-RFG-01`:

```text
Toledo lookup
  -> Genesis compatibility
  -> reuse existing object
  -> derive only the missing piece
  -> PROPOSAL
```

Existing Toledo anchors reused rather than duplicated:

- CAN-007 / `weld/M.03.v1`: future-reader equivalence;
- CAN-006 / `weld/M.02.v1`: dynamic commutation/weld target;
- CAN-034 / `weld/E.06.v1`: sufficiency/invariant gate;
- CAN-165 / `EQ-002/M.01.v1`: fiber constancy and factorisation;
- `EQ-001/C.05.v1`: finite refinement target, currently `open_prop`;
- `EQ-001/C.07.v1`: quotient fixed points can hide source cycles/currents;
- `EQ-001/C.13.v1`: signature factorisation;
- `EQ-001/C.16.v1`: structure and lineage are distinct.

The new material is the smallest missing Reader–Domain theorem packet and a safe finite-refinement repair kernel. It remains a Toledo **PROPOSAL** until issue #36 completes the normal registry audit.

## 2. Definition Freeze v1

For a retained finite/discrete world, let the root dynamics be a state type `S`, declared actions `U`, and transitions `F_u : S -> S`. Domain names and domain-final equations are not root primitives.

For a fixed experiment value type, an experiment is a finite readout

\[
E:S\to V.
\]

A declared experiment family `\mathcal E` induces indistinguishability

\[
\operatorname{Eq}(\mathcal E)(s,t)
\iff
\forall E\in\mathcal E:\ E(s)=E(t).
\]

For a relation `R` on states, the admissible observable family is

\[
\operatorname{Obs}(R)
=
\{E\mid R\subseteq\ker E\}.
\]

Reader saturation is

\[
\operatorname{Cl}(\mathcal E)
=
\operatorname{Obs}(\operatorname{Eq}(\mathcal E)).
\]

A question/domain is therefore a readout quotient induced by declared future experiments, not a new root ontology.

### Semantic/constructive firewall

**Tier: `Th_coqc` — formalized, axiom-free (2026-09-13 update).** `Section ConstructiveFirewall`
in `formal/IDM_ReaderDomainFoundation.v` (immediately after `ReaderDomainCore`) now carries this
subsection's discipline as real Coq identifiers, among the axiom-free identifiers in section 3.
**Toledo status:** `NEW DERIVATION / PROPOSAL, not yet in Toledo` — child of `TG-RFG-01` (issue
`morrocwi/toledo#36`), sitting beside this file's existing Galois-correspondence family, not a
standalone object.

The section reuses `Family`, `Experiment`, `EqOf`, `family_subset`, `rel_equiv` verbatim from
`ReaderDomainCore` and introduces a single abstract, uninterpreted resource predicate
`Variable Constructive : Experiment -> Prop` — never instantiated, never given intro/elim rules
beyond what `Family`/`EqOf` already have. It formalizes, and only formalizes, a bookkeeping fact
about which sub-family of experiments `EqOf` is allowed to range over once membership is filtered
by `Constructive`; it says nothing about what `Constructive` means operationally, what it can
decide, or any separation result:

\[
\mathcal A_{\rm sem} := \mathcal A_{\rm ambient},\qquad
\mathcal A_{\rm con} := \{\,e\in\mathcal A_{\rm ambient} \mid \mathrm{Constructive}(e)\,\}.
\]

`A_sem` may define the semantic question; `A_con` is the resource-bounded constructive experiment
universe. A constructive proof may not silently call a semantic oracle outside `A_con`. Two
theorems are proved:

- **`A_con_subseteq_A_sem`** — the trivial inclusion \(\mathcal A_{\rm con}\subseteq\mathcal
  A_{\rm sem}\), by construction.
- **`constructive_closure_invariant`** — if two candidate experiment-families are both confined to `A_con` and
  agree on every constructive experiment, their induced `EqOf` relations are the *same relation*:
  `EqOf` cannot "see" any experiment outside what `Constructive` already licensed. This is a
  closure/definitional fact about `EqOf`'s quantifier scope, exactly parallel to
  `T2_eq_closure_invariant`, proved by plain `intros`/`destruct`/`apply` (no induction, no
  classical axioms, no reference to computability).

Both identifiers are axiom-free (`Print Assumptions`: "Closed under the global context") and are
included in the promoted theorem list (section 3, 34 identifiers as of the Finite-Bottleneck RDLB
addition in §5b) and in `formal/verify_reader_domain_foundation.sh`'s `THEOREMS` array. **Claim
boundary (unchanged in
scope):** no P-vs-NP-shaped claim, no computational-hardness premise or conclusion — domain
instantiation of `Constructive` (what actually counts as "constructive" in a given application,
e.g. polynomial-time decidability or lab-performability) remains a separate obligation.

**Not to be confused with:** Toledo `registry/proposals/semantic_closure_accounting_p_vs_np_v0_1.json`
(`PROP-SCA-PNP-01..06`), also gated under `TG-RFG-01`, which is a genuinely different, still-open
P-vs-NP-adjacent circuit-level result about semantic-channel/oracle bookkeeping. The two share
vocabulary ("oracle", "semantic universe") by coincidence of domain, not by any shared theorem,
proof, or object — this subsection's result is a family/`EqOf` congruence fact, unrelated to
circuit-ledger accounting.

### Partial actions

Applications with partial actions must make inadmissibility explicit (for example by a blocked state/readout) rather than silently deleting the branch.

## 3. Formal theorem packet

Source: `formal/IDM_ReaderDomainFoundation.v`.

Promoted theorem targets are accepted only if `formal/verify_reader_domain_foundation.sh` reports `Closed under the global context` for every theorem.

### T1 — Eq–Obs correspondence

\[
\mathcal E\subseteq\operatorname{Obs}(R)
\iff
R\subseteq\operatorname{Eq}(\mathcal E).
\]

Identifier: `T1_eq_obs_correspondence`.

### T2 — Reader closure

The formal kernel proves extensivity, monotonicity and idempotence of `Cl`, plus saturation invariance

\[
\operatorname{Eq}(\operatorname{Cl}(\mathcal E))
=
\operatorname{Eq}(\mathcal E).
\]

Identifiers include `T2_closure_extensive`, `T2_closure_monotone`, `T2_eq_closure_invariant`, `T2_closure_idempotent`.

### T3/T4 — Future stability and dynamic weld well-definedness

For all-future reader equivalence,

\[
s\sim_Q t\Longrightarrow F_u(s)\sim_QF_u(t).
\]

This is the relational well-definedness condition required before the quotient transition `F_u^#` can be named; in ordinary quotient semantics it licenses the CAN-006 commuting square.

Identifiers: `T3_future_equivalence_dynamic_stability`, `T4_dynamic_weld_well_defined`, `T4b_quotient_commuting_square`.

**Precision note (peer-review, 2026-09-12):** `T4_dynamic_weld_well_defined` is definitionally identical to `T3_future_equivalence_dynamic_stability` (same statement, same proof by direct application) — it is not a second, independent result. It supplies the *congruence property* that a well-defined quotient map `F_u^#` requires, but on its own does not construct a quotient type, a projection `q`, or `F_u^#`, and does not itself instantiate the equation `q∘F_u = F_u^#∘q`.

**Update (2026-09-13):** that gap is now closed by `T4b_quotient_commuting_square`, added in the same file. It defines the quotient type `QState` (states up to `FutureEq`), the canonical projection `proj` (`q`), the induced transition `Fsharp` (`F^#`), and proves the commuting square `q∘F_u = F^#_u∘q` — stated pointwise on class membership so no functional-extensionality or proof-irrelevance axiom is needed. Axiom-free (`Print Assumptions`: "Closed under the global context"), included in the promoted theorem list (§3 below, 20 identifiers as of this update; 22 after the constructive-firewall addition below; 25 after the RDLB abstract-layer addition in §5a; now 34 after the Finite-Bottleneck RDLB addition in §5b). This is the first concrete Coq instance of Toledo CAN-006 (`weld/M.02.v1`) supplied by this Foundation — an occurrence, not a new weld object.

### T5 — Sufficiency kernel inclusion

For a candidate representation `rho`, sufficiency means

\[
\rho(s)=\rho(t)\Longrightarrow s\sim_Qt,
\]

hence

\[
\ker\rho\subseteq\sim_Q.
\]

Identifier: `T5_sufficiency_kernel_inclusion`.

The existence of the corresponding factor map is not duplicated here; Toledo CAN-165 is the canonical factorisation object.

### T6 — Question monotonicity

\[
\mathcal E_A\subseteq\mathcal E_B
\Longrightarrow
\operatorname{Eq}(\mathcal E_B)
\subseteq
\operatorname{Eq}(\mathcal E_A).
\]

Identifier: `T6_question_monotonicity`.

### T7 — Joint question

The joint question is defined at the experiment level:

\[
\operatorname{Eq}(\mathcal E_A\cup\mathcal E_B)
=
\operatorname{Eq}(\mathcal E_A)
\cap
\operatorname{Eq}(\mathcal E_B).
\]

Identifier: `T7_joint_question_intersection`.

This does **not** silently create mixed interventions. Mixed-action experiments are additional experiments and must be declared explicitly.

## 4. Reader–Domain closure algebra

A closed reader family satisfies

\[
\operatorname{Cl}(\mathcal C)=\mathcal C.
\]

The formal packet proves:

- closure is itself closed;
- binary meet of closed families is family intersection;
- binary join is closure of family union.

Identifiers: `closure_is_closed`, `closed_intersection`, `closed_join`.

Under a fixed admissible experiment universe this gives the binary closure-lattice structure required by the project. No claim is made here that every domain-specific bridge exists.

## 5. Safe finite-refinement kernel (C.05 repair)

The current Toledo wrapper `EQ-001/C.05.v1` quantifies over arbitrary `refine_step` and arbitrary `is_closed` and states unconditional termination. That statement is too broad to prove.

The Foundation therefore does **not** force-close C.05 v1. It proves the safe missing theorem:

Let a partition representation carry a natural block count bounded by `N`. If every non-closed refinement step strictly increases that block count, and closedness is decidable, then repeated refinement terminates after finitely many steps.

Formally the assumptions are:

\[
\forall P:\ b(P)\le N,
\]

and

\[
\neg Closed(P)\Longrightarrow b(P)<b(refine(P)).
\]

Then

\[
\forall P\ \exists k:\ Closed(refine^k(P)).
\]

Identifier: `finite_strict_refinement_terminates`.

A second formal result connects semantic and constructive readings: if finite-depth future equivalence reaches a fixed point at depth `n`, that relation is exactly all-future reader equivalence.

Identifier: `stable_depth_exact_future`.

Toledo issue #36 is the governed place to decide whether the present C.05 row is revised/superseded by this strengthened statement.

## 5a. RDLB v0.1 — abstract accumulated-capacity accounting

**Tier: `Th_coqc` — formalized, axiom-free (2026-09-13 addition).** `Section RDLBAbstractLayer` in
`formal/IDM_ReaderDomainFoundation.v` (immediately after `FiniteStrictRefinement`). **Toledo
status:** `NEW DERIVATION / PROPOSAL, not yet in Toledo` — the reuse-pipeline lookup
(Toledo → Genesis compatibility → reuse → derive-only-the-delta → mark PROPOSAL) found no existing
Toledo object covering this exact nat-valued Demand/Capacity accounting law, so it is registered
here as a proposal candidate, not cited as an equation anywhere else.

This is a wholly abstract, generic finite/discrete-math layer: `Question`, `Reader`, `Dem`, `Cap`,
`Sufficient`, and `combine` are free `Variable`s/`Context` types, never instantiated. All
quantities are `nat` (`List.length`, `+`, `*`, `<=` only) — no continuum concept appears, so the
section is IDM-clean by construction and implicates no discrete-replacement-table entry.

**Claim boundary (explicit, generic finite/discrete math only):**

- No linear algebra of any kind (no Jacobian, no rank, no matrix, no norm) is used or implied here.
- No Navier-Stokes / energy-observability specialization is made here. `readout-problem-navier-stokes`
  and its `ns_energy_observability.json` artifact are cited by name only, as the motivating future
  application — their content is never restated or relied on as a premise. Any NS-specific
  instantiation of `Dem`/`Cap`/`Sufficient`/`combine` remains a wholly separate, unaddressed
  obligation.
- No computational-hardness or complexity-class premise or conclusion of any kind, and in
  particular **no P-vs-NP-shaped claim of any kind**. `Sufficient`, `Dem`, `Cap`, `combine` stay
  opaque throughout; nothing here decides, bounds, or reasons about time/space complexity, circuit
  size, or any resource model. **PNP-RDLB remains permanently OPEN**, per the founder's own
  Finite-Clay Programme rule, and is not touched, narrowed, or answered by anything in this section.

**Disambiguation from Toledo `PROP-SCA-PNP-03/06/07/08/09`** (registry/proposals/
`semantic_closure_accounting_p_vs_np_v0_1*.json`, the reuse-pipeline lookup's nearest hit): that
cluster is a distinct, still-open P-vs-NP-adjacent proposal about circuit/oracle-level
semantic-channel accounting. RDLB v0.1 shares only surface vocabulary with it (Demand, capacity, an
accumulation bound, a depth/round divergence) by coincidence of subject matter — zero shared
theorem, zero shared proof, zero shared Coq object. No claim, premise, or conclusion of
`PROP-SCA-PNP-03/06/07/08/09` is made, used, restated, or implied here.

**Further reuse-pipeline near-hits, checked and ruled out** (statements read directly, not just
matched by keyword, per EPIS-REUSE-PIPELINE's "keyword hits are NOT matches" rule): Toledo
`CAN-181` (`A.8/M.08.v1`, `PublicOutputVelocity ≤ VerificationCapacity` in a bottleneck-
inversion/epistemic-debt economics reading) shares C1's `Dem ≤ Cap` shape but has no
fold-accumulation law and sits in an unrelated domain — kept only as a same-form-different-theory
note, not a duplicate. `CAN-054` (`EQ-015/H.06.v1`, rank-bounded LoRA factorization) and `CAN-065`
(`weld/H.06.v1`, a domain-weld defect vector) were read directly and are unrelated mechanisms.
`weld/W.04.v1`/`weld/W.11.v1` (validation-capacity-as-a-function objects) share only the word
"capacity". None of these is reused as a parent; none is duplicated here.

**Genesis compatibility** (EPIS-REUSE-PIPELINE step 2): no existing Readout Genesis gate or section
was found treating a Demand/Capacity accumulation law, formally or informally (checked via a
keyword sweep of `READOUT_GENESIS_CORE.md` for "capacity"/"demand"). RDLB v0.1 is therefore new
infrastructure with no Genesis-side classification yet — not an instantiation of an existing gate.

**Parentage (intellectual only, not a `Require`):** the `Sufficient`/`Dem` shape is motivated by
this file's own `T5_sufficiency_kernel_inclusion` (§SufficiencyKernel above) and
`T6_question_monotonicity` (§ReaderDomainCore above) — a sufficient reader must dominate whatever
the question demands, and adding reading power can only add to what is already settled. Those two
theorems are cited as intellectual parents only; RDLB v0.1's theorems are self-contained over their
own local `Hypothesis`es and are not proved from them.

**The accounting law and its consequences.** Two accepted (not derived) accounting hypotheses:

\[
\mathrm{Sufficient}(R,Q)\Longrightarrow \mathrm{Dem}(Q)\le\mathrm{Cap}(R)
\qquad\text{(RDLB-C1, sufficiency-capacity law)}
\]
\[
\mathrm{Cap}(\mathrm{combine}(A,B))\le\mathrm{Cap}(A)+\mathrm{Cap}(B)
\qquad\text{(RDLB-C2, block-accumulation subadditivity)}
\]

plus a baseline bound `Cap(base) <= c0` and a uniform per-round throughput bound
`forall r, Cap(r) <= c`. A reader `built blocks` is the left fold `combine` of a list of block
readers starting from `base`. From these, three real theorems are proved (not assumed):

- **`RDLB_T1_accumulation_bound`** — `Sufficient (built blocks) Q -> Dem Q <= Cap base + list_sum (map Cap blocks)`,
  via the helper lemmas `cap_fold_bound`/`cap_built_bound` (subadditivity carried through the fold
  by list induction) composed with RDLB-C1.
- **`RDLB_T2_round_bound`** — `Sufficient (built blocks) Q -> Dem Q <= c0 + length blocks * c`, the
  same bound collapsed to a multiplication form under uniform per-round throughput (via the helper
  lemma `list_sum_caps_le_length_mul`). Read informally as `Dem Q <= c0 + R*c`, i.e. (for `c > 0`
  and `Dem Q > c0`) equivalent to `R >= ceil((Dem Q - c0)/c)` — stated and proved directly in
  multiplication form, so no `Nat.div`/ceiling machinery is needed.
- **`RDLB_W_capacity_deficit_witness`** — the contrapositive corollary of T2: a strict capacity
  deficit `c0 + length blocks * c < Dem Q` rules out sufficiency for *any* reader built from that
  many rounds.

All three (plus their supporting `Definition`s/`Lemma`s) are axiom-free (`Print Assumptions`:
"Closed under the global context" — the section's own `Hypothesis`es are correctly promoted to
ordinary extra function arguments on section close, never global axioms). The three `Theorem`
identifiers are included in the promoted theorem list (§3) and in
`formal/verify_reader_domain_foundation.sh`'s `THEOREMS` array, bringing the total to 25.

## 5b. Finite-Bottleneck RDLB — finite ℚ-matrix linear algebra

**Tier: `Th_coqc` — formalized, axiom-free through `TOL3_sum_rank`; explicit-Hypothesis concession
from `K4_codim_bound` (2026-09-13 addition).** `Section FiniteBottleneckRDLB` in
`formal/IDM_ReaderDomainFoundation.v` (immediately after `RDLBAbstractLayer`). **Toledo status:**
`NEW DERIVATION / PROPOSAL, not yet in Toledo`. **Framing (founder override):** this section
replaces an earlier, discarded Jacobian-based design outright — there is no Jacobian, derivative,
tangent space, or continuum object anywhere below. Every object is a `nat`-indexed `ℚ`-matrix or
`ℚ`-vector, reusing `IDM_Matrix.v`'s existing `Mat := nat -> nat -> Q`, `Sum`, `mmul`, `mid`,
`mid_left`, `madd` rather than re-deriving matrix algebra — the file now carries
`Require Import IDM_Matrix.` for exactly this reuse. Following `IDM_Matrix.v`'s own convention, a
matrix's shape is never encoded in its type; it is carried as separate `nat` arguments in each
lemma statement.

**Definitional-choice note — what "rank", "kernel", and "codimension" mean here, and their scope**
(read before citing any identifier below):

- **`meqR p r A B`** — rectangular entrywise equality on the `p x r` window (a generalization of
  `IDM_Matrix.v`'s implicitly-square `meq`).
- **`rank_le p r k M := exists C D, meqR p r M (mmul k C D)`** — *factorization rank*, not
  row-reduction/linear-independence rank: "`M` (`p x r`) factors through a `k`-dimensional middle."
  This is a genuine, non-tautological property for an arbitrary `M` (most `k`-factorizations do not
  exist); it becomes trivial only for a matrix that already *is* such a factorization by
  construction (e.g. `mmul m B A`, TOL-2 below) — that triviality is TOL-2's content, not a flaw.
  A second, *separately genuine but explicitly unused* corollary, `rank_le_trivial_upper`, records
  that any `p x r` matrix has `rank_le p r p M` (via `mid_left`) — this is a fact about the shape of
  a constraint matrix, never about the true dimension of its kernel, and it is never invoked to
  justify `K4_codim_bound`.
- **`mvmul n A x`** — matrix-vector product contracting over the shared inner dimension `n`.
  **`InKer d m A x`** — `x` is annihilated by the first `m` rows of the (`d`-column) matrix `A`;
  this is a kernel-*membership* predicate on a single vector, not a subspace-dimension claim.
- **`Subspace := Vec -> Prop`** and **`HasCodimLe : Subspace -> nat -> Prop`** (from `K4_codim_bound`
  onward) — an *uninterpreted* relation, exactly as `Sufficient`/`Cap` are left abstract in
  `RDLBAbstractLayer`. Nothing below defines what "codimension" *is*; `HasCodimLe S c` is read only
  as "the two named Hypotheses below license concluding `c` as an upper bound for `S`." No basis,
  linear independence, or vector-space-dimension machinery exists anywhere in Toledo/IDM today, and
  none is introduced here.

**Claim boundary (explicit, finite ℚ-linear-algebra math only):**

- No Jacobian, derivative, tangent space, or continuum object of any kind, anywhere in the section.
- No Navier-Stokes / energy-observability specialization is made here, and no NS-specific
  instantiation of `AA`, `BB`, `mm`, or `d` is made anywhere — same disclaimer as `RDLBAbstractLayer`
  §5a, and for the same reason (this is generic infrastructure, not a domain instance).
- No computational-hardness or complexity-class premise or conclusion of any kind, and in
  particular **no P-vs-NP-shaped claim of any kind**. **PNP-RDLB remains permanently OPEN**, exactly
  as declared in §5a; nothing in this section touches, narrows, or answers it in either direction.

**Toledo `CAN-054` disambiguation (EPIS-REUSE-PIPELINE step 1, read directly, not by keyword):**
`CAN-054` (`EQ-015/H.06.v1`, "Selective retention as a rank-bounded factorized update (Human
LoRA)") states `rank_Q(B_nA_n) <= m_n` as part of its own root statement, and was checked as the
nearest candidate parent for `TOL2_rank_bound`. Its own Coq file
(`coq/canonical/EQ_015__H_06_v1.v`) was read in full: it does **not** prove a general
factorization-rank bound — `CAN_054_finite_bottleneck` is only the `nat`-pair predicate
`0 < rank_n < dim_n`, and `CAN_054_finite_bottleneck_satisfiable` only exhibits the single witness
pair `(1,2)`; there is no `rank_le`-shaped object there to reuse. **`TOL2_rank_bound` below is
therefore proved fresh in this section, not reused from `CAN-054`'s Coq** — `CAN-054` is cited as
the intellectual motivation for the *name* "finite-bottleneck rank bound" only, never as a
`Require`d premise, and none of its Coq identifiers (`CAN_054_gate_weight_valid`,
`CAN_054_retained_update`, `CAN_054_finite_bottleneck*`, `CAN_054_Open_empirical_programme`) are
duplicated. **Guardrail:** `CAN-054` is a Human-LoRA-*specific* empirical model (its own tier is
`definition / theorem (rank bounds, proved in-article) / hypothesis-Open (empirical programme)`);
the bridge from that specific model to an *arbitrary computation* or *any NS/PNP instantiation* is
a wholly separate, unproved obligation that this section does not attempt and does not narrow.

**Genesis compatibility** (step 2): no existing Readout Genesis gate or section treats a
factorization-rank / kernel-inclusion law; this section is new infrastructure with no Genesis-side
classification yet — not an instantiation of an existing gate.

**Genuinely derived (real theorems, no Hypothesis beyond `IDM_Matrix.v`'s own axiom-free base):**

- **`TOL2_rank_bound`** — `rank_le d d m (mmul m B A)`, the keystone triviality that a matrix
  already built as a factorization satisfies its own rank bound (`exists B, A`; `reflexivity`).
- **`mv_mmul_assoc`** — `mvmul q (mmul p A B) x i == mvmul p A (mvmul q B x) i`, via the new finite
  double-sum-interchange lemma `Sum_double_swap` (induction on the outer sum) plus two constant-
  factoring helpers `Sum_mul_const_l`/`Sum_mul_const_r`.
- **`K1_kernel_inclusion`** (TOL-5) — `InKer d m A x -> InKer d d (mmul m B A) x`: kernel inclusion
  for one bottleneck, from `mv_mmul_assoc` + `Sum_ext_lt` + `Sum_zero`.
- **`TOL4_no_collapse`** — a no-early-collapse form: given `meqR d d (madd O (mmul m B A)) O`
  (the `B.A` contribution already agrees entrywise with the zero-shift `O`), the two readers induce
  the same `mvmul`. The `InKer d m A x` hypothesis is scenario framing, not load-bearing in this
  particular proof; the entrywise `meqR` hypothesis is what the conclusion rests on.
- **`K2_each`**, **`K3_sum`** (K2/K3) — the *N*-fold form over an abstract index family `{I : Type}`,
  `AA BB : I -> Mat`, `mm : I -> nat` sharing ambient dimension `d`: if `x` is in every bottleneck's
  kernel (`InKerAll x`), it is in the kernel of each `mmul (mm i) (BB i) (AA i)` (K2), and in the
  kernel of any finite `fold_left madd`-sum of them (K3), via list induction using K2 plus the new
  `mvmul`-additivity-over-`madd` lemma `mvmul_madd`.
- **`rank_le_add`** (TOL-3/F2, binary case) — `rank_le p r k1 M1 -> rank_le p r k2 M2 -> rank_le p r
  (k1+k2) (madd M1 M2)`, via new horizontal/vertical block-concatenation `Definition`s `hcat`/`vcat`
  and the new reindexing lemma `Sum_split` (`Sum (a+b) f == Sum a f + Sum b (fun k => f (a+k))`).
- **`TOL3_sum_rank`** (*N*-fold) — the sum of finitely many rank-`mm i` bottleneck matrices has
  `rank_le` bounded by `list_sum (map mm Is)`, by list induction over `rank_le_add` with a
  `k=0` base case (`rank_le_zero`, from the zero matrix).

**Honest concession, from `K4_codim_bound` onward:** proving true subspace codimension (the
dimension of an intersection of kernels inside `ℚ^d`) needs basis/independence theory that exists
nowhere in Toledo/IDM today (confirmed above). Rather than fake it via `rank_le_trivial_upper`
(genuine but about the constraint matrix's own shape, never the kernel's true dimension), this
section introduces the abstract `Subspace`/`HasCodimLe` pair above and two named Hypotheses:

\[
\mathrm{HasCodimLe}(\mathrm{InKer}\,d\,m\,A,\ m)
\qquad\text{(RDLB-K4-Ax-single, one bottleneck's codim bound)}
\]
\[
\mathrm{HasCodimLe}(S_1,c_1)\wedge\mathrm{HasCodimLe}(S_2,c_2)\Rightarrow
\mathrm{HasCodimLe}(S_1\wedge S_2,\,c_1+c_2)
\qquad\text{(RDLB-K4-Ax-inter, subadditivity)}
\]

- **`K4_codim_bound`** — is genuinely *derived* from those two Hypotheses by structural list
  induction, but its statement is deliberately about the **finite, list-scoped intersection**
  `InKerListSub Is` (a `Fixpoint` on `list I` built with a `RDLB_K4_Ax_single`-at-`m=0` base case),
  **not** the unrestricted `InKerAll` (quantified over the whole, possibly-infinite index type `I`).
  Extending the bound to `InKerAll` for an arbitrary `Is` would additionally require `HasCodimLe` to
  respect logical/extensional equivalence of its `Subspace` argument — a real but *unstated* closure
  property neither named Hypothesis grants; adding a third, undisclosed Hypothesis to paper over
  that gap would contradict this section's own two-Hypothesis ledger, so it is deliberately **not**
  done. That extension is left explicitly **OPEN**, not silently assumed.
- **`RDLB_S2_Ax`** (S1→S2) — one further named Hypothesis: if the joint kernel `InKerAll` is
  trivial (`x == 0`), the ambient dimension `d` is bounded by the sum of bottleneck ranks — the
  classical "injective ⟹ domain-dim ≤ codomain-dim" fact, same missing-theory class as K4.
  **`TOL_RDLB_close`** is its immediate, one-line corollary (`exact (RDLB_S2_Ax d Is)`), not a
  further derivation.

**Honest ledger:** derived as real theorems, no Hypothesis beyond `IDM_Matrix.v`'s own axiom-free
lemma base — `meqR`, `rank_le`, `TOL2_rank_bound`, `Sum_double_swap`, `Sum_split`, `mv_mmul_assoc`,
`K1_kernel_inclusion`, `TOL4_no_collapse`, `K2_each`, `K3_sum`, `rank_le_add`, `TOL3_sum_rank`, and
the list-scoped form of `K4_codim_bound`. Assumed as explicit, named Hypotheses —
`RDLB_K4_Ax_single`/`RDLB_K4_Ax_inter` (the two K4 codimension laws) and `RDLB_S2_Ax` (S2's
injectivity-bound law); `TOL_RDLB_close` rests on the latter alone. All nine promoted `Theorem`
identifiers (`TOL2_rank_bound`, `K1_kernel_inclusion`, `TOL4_no_collapse`, `K2_each`, `K3_sum`,
`rank_le_add`, `TOL3_sum_rank`, `K4_codim_bound`, `TOL_RDLB_close`) are axiom-free (`Print
Assumptions`: "Closed under the global context" — the section's `Hypothesis`es/`Variable`s are
correctly promoted to ordinary extra function arguments on section close, never global axioms), are
included in the promoted theorem list (§3) and in
`formal/verify_reader_domain_foundation.sh`'s `THEOREMS` array, bringing the total to 34.

## 6. F6 Maker–Checker calibration

Executable bundle:

- `research/reader_domain/maker_records.json`
- `research/reader_domain/checker_labels.json`
- `research/reader_domain/f6_topology_calibration.py`

The files physically separate maker readouts from checker topology labels. Maker partitions are frozen before checker labels are loaded.

The calibration is intentionally fail-able:

1. `R0 = structure + homology` must false-merge `S^3` and the Poincare homology sphere, and also collide `L(5,1)` with `L(5,2)`.
2. `R1 = R0 + pi1 certificate` must split the `S^3`/Poincare collision but still collide the two lens spaces.
3. `R2 = R1 + linking-form signature` must exactly match the frozen checker classes.

F6 passes iff the final defect vector is

\[
(false\ merge,false\ split,leakage,unresolved)=(0,0,0,0)
\]

**on this frozen benchmark only**.

Not established by F6:

- raw triangulation -> readout encoding;
- universal 3-manifold homeomorphism classification;
- a new proof of the Poincare conjecture;
- any Clay conclusion.

Those remain separate domain/encoding obligations.

## 7. Foundation audit

The freeze gate fails if any of the following occurs:

1. **Root contamination:** continuum objects, domain-final equations or target answers are imported as root primitives.
2. **Target leakage:** checker labels or target conclusions appear in maker features/readers.
3. **Semantic-oracle leakage:** a constructive lane calls an experiment outside its declared constructive universe.
4. **Silent partiality:** inadmissible actions are discarded rather than represented/declared.
5. **Lineage collapse:** provenance is discarded when a declared future reader uses it.
6. **Readout = truth collapse:** `s ~_Q t` is treated as ontological identity; Toledo C.07 forbids this inference.
7. **Claim promotion:** finite/native results are presented as global/domain/Clay theorems without explicit bridge evidence.

## 8. Freeze condition

The Foundation may be relabelled `FROZEN` only when all six gates are simultaneously satisfied:

```text
F1  definitions frozen
F2  T1–T7 + closure algebra axiom-free in Coq CI
F3  safe finite-refinement kernel axiom-free in Coq CI
F4  Reader–Domain algebra assembled without duplicate Toledo objects
F5  F6 Maker–Checker calibration PASS with expected negative controls
F6  governance / anti-circularity audit PASS and Toledo proposal issue open or registered
```

After freeze, Clay/domain lanes may change only their declared question/readers, constructive resource model and domain-specific target property. They may not redesign `Eq`, `Obs`, `Cl`, the information order or joint-question rule merely to make a target theorem pass.

## 9. Claim ceiling

Even after Foundation freeze:

\[
\text{Reader–Domain Foundation}
\neq
\text{domain theorem}
\neq
\text{uniform theorem}
\neq
\text{global semantic bridge}
\neq
\text{Clay conclusion}.
\]

This document freezes infrastructure, not Millennium-problem answers.
