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

**Tier: `[Dr]` — declared discipline, not yet formalized in Coq.** No type, definition, or theorem
in `formal/IDM_ReaderDomainFoundation.v` corresponds to this subsection; it is not among the 19
axiom-free identifiers in section 3. It is a required discipline for any application (e.g. a
P-vs-NP-adjacent constructive lane) built on top of this Foundation, stated here so applications
inherit it, but it carries no Coq-verified content of its own until someone formalizes it.

Applications must distinguish:

\[
\mathcal A_{\rm con}\subseteq\mathcal A_{\rm sem}.
\]

`A_sem` may define the semantic question; `A_con` is the resource-bounded constructive experiment universe. A constructive proof may not silently call a semantic oracle outside `A_con`.

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

Identifiers: `T3_future_equivalence_dynamic_stability`, `T4_dynamic_weld_well_defined`.

**Precision note (peer-review, 2026-09-12):** `T4_dynamic_weld_well_defined` is definitionally identical to `T3_future_equivalence_dynamic_stability` (same statement, same proof by direct application) — it is not a second, independent result. It supplies the *congruence property* that a well-defined quotient map `F_u^#` requires, but this file does not itself construct a quotient type, a projection `q`, or `F_u^#`, and does not literally instantiate or prove the equation `q∘F_u = F_u^#∘q`. The CAN-006 commuting-square correspondence is a standard corollary of congruence, not a separately machine-checked object here. Do not read T4 as formal evidence that the commuting square has been verified for any concrete `q`/`F^#`.

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
