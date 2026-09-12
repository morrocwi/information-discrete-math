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
included in the promoted theorem list (section 3, now 25 identifiers) and in
`formal/verify_reader_domain_foundation.sh`'s `THEOREMS` array. **Claim boundary (unchanged in
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

**Update (2026-09-13):** that gap is now closed by `T4b_quotient_commuting_square`, added in the same file. It defines the quotient type `QState` (states up to `FutureEq`), the canonical projection `proj` (`q`), the induced transition `Fsharp` (`F^#`), and proves the commuting square `q∘F_u = F^#_u∘q` — stated pointwise on class membership so no functional-extensionality or proof-irrelevance axiom is needed. Axiom-free (`Print Assumptions`: "Closed under the global context"), included in the promoted theorem list (§3 below, 20 identifiers as of this update; 22 after the constructive-firewall addition below; now 25 after the RDLB abstract-layer addition in §5a). This is the first concrete Coq instance of Toledo CAN-006 (`weld/M.02.v1`) supplied by this Foundation — an occurrence, not a new weld object.

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
