(*
  IDM_ReaderDomainFoundation.v

  Genesis Reader-Domain Foundation v1 — safe generic kernel.

  Scope:
  - reader/indistinguishability correspondence (T1)
  - closure operator and saturation invariance (T2)
  - semantic/constructive experiment-universe firewall (ConstructiveFirewall:
    A_con_subseteq_A_sem, constructive_closure_invariant)
  - future-reader dynamic stability / quotient well-definedness kernel (T3/T4),
    plus the literal quotient/projection/commuting-square instantiation
    (T4b_quotient_commuting_square)
  - sufficiency => kernel inclusion (T5; factorisation itself is Toledo CAN-165)
  - question monotonicity and joint-question intersection (T6/T7)
  - binary closure-lattice laws for closed reader families
  - finite strict-refinement termination with explicit hypotheses (safe C.05 replacement kernel)
  - stable finite-depth reader equivalence equals all-future reader equivalence
  - RDLB v0.1 abstract Demand/Capacity accounting layer (RDLBAbstractLayer:
    RDLB_T1_accumulation_bound, RDLB_T2_round_bound,
    RDLB_W_capacity_deficit_witness)
  - Finite-Bottleneck RDLB: pure finite Q-matrix linear algebra over
    IDM_Matrix.v (FiniteBottleneckRDLB: TOL2_rank_bound, K1_kernel_inclusion,
    TOL4_no_collapse, K2_each, K3_sum, rank_le_add, TOL3_sum_rank,
    K4_codim_bound, TOL_RDLB_close) -- no Jacobian, no derivative, no
    continuum object anywhere; see the section header comment for the
    honest achievable-vs-Hypothesis split.

  This file's place in the programme's Master Spine (root-to-Clay architecture
  map, updated separately as new sections land here):
  readout_genesis/MASTER_SPINE.md.

  Claim boundary:
  This file proves generic finite/discrete mathematics only. It contains no
  continuum premise and no Clay conclusion. Domain encodings and semantic
  bridges are separate obligations.
*)

From Coq Require Import List Arith Lia.
Require Import QArith.
Require Import IDM_Matrix.
(* Both QArith's and IDM_Matrix.v's own top-level `Open Scope Q_scope` are
   re-triggered by these `Require Import`s and would otherwise silently
   reinterpret every bare numeral literal in the REST of this file (nat
   pattern matches on `0` included) as a `Q` numeral instead of a `nat`
   one. Close it back down immediately, after both requires; `Section
   FiniteBottleneckRDLB` below reopens it locally, for exactly the
   Q-matrix content that needs it, and closes it again at the end of
   that section. *)
Close Scope Q_scope.
Import ListNotations.
Set Implicit Arguments.

Section ReaderDomainCore.

Context {State Value : Type}.

Definition Experiment := State -> Value.
Definition Family := Experiment -> Prop.
Definition Rel := State -> State -> Prop.

Definition family_subset (A B : Family) : Prop :=
  forall e, A e -> B e.

Definition rel_subset (R T : Rel) : Prop :=
  forall s t, R s t -> T s t.

Definition family_equiv (A B : Family) : Prop :=
  forall e, A e <-> B e.

Definition rel_equiv (R T : Rel) : Prop :=
  forall s t, R s t <-> T s t.

Definition kernel (e : Experiment) : Rel :=
  fun s t => e s = e t.

Definition EqOf (E : Family) : Rel :=
  fun s t => forall e, E e -> e s = e t.

Definition ObsOf (R : Rel) : Family :=
  fun e => forall s t, R s t -> e s = e t.

Definition Cl (E : Family) : Family := ObsOf (EqOf E).

(* T1: reader-family / indistinguishability correspondence. *)
Theorem T1_eq_obs_correspondence (E : Family) (R : Rel) :
  family_subset E (ObsOf R) <-> rel_subset R (EqOf E).
Proof.
  split.
  - intros H s t HR e He.
    exact (H e He s t HR).
  - intros H e He s t HR.
    exact (H s t HR e He).
Qed.

Lemma EqOf_antitone (A B : Family) :
  family_subset A B -> rel_subset (EqOf B) (EqOf A).
Proof.
  intros HAB s t Hst e He.
  exact (Hst e (HAB e He)).
Qed.

Lemma ObsOf_antitone (R T : Rel) :
  rel_subset R T -> family_subset (ObsOf T) (ObsOf R).
Proof.
  intros HRT e He s t HR.
  exact (He s t (HRT s t HR)).
Qed.

(* T2a: closure is extensive. *)
Theorem T2_closure_extensive (E : Family) :
  family_subset E (Cl E).
Proof.
  intros e He s t Hst.
  exact (Hst e He).
Qed.

(* T2b: closure is monotone. *)
Theorem T2_closure_monotone (A B : Family) :
  family_subset A B -> family_subset (Cl A) (Cl B).
Proof.
  intros HAB e He s t Hst.
  apply He.
  intros e0 He0.
  apply Hst.
  apply HAB.
  exact He0.
Qed.

(* Saturation does not alter the induced indistinguishability relation. *)
Theorem T2_eq_closure_invariant (E : Family) :
  rel_equiv (EqOf (Cl E)) (EqOf E).
Proof.
  intros s t; split.
  - intros H e He.
    apply H.
    intros x y Hxy.
    exact (Hxy e He).
  - intros H e He.
    exact (He s t H).
Qed.

(* T2c: closure is idempotent, extensionally. *)
Theorem T2_closure_idempotent (E : Family) :
  family_equiv (Cl (Cl E)) (Cl E).
Proof.
  intro e; split.
  - intros H s t Hst.
    apply H.
    intros e0 He0.
    exact (He0 s t Hst).
  - intros H s t Hst.
    apply H.
    intros e0 He0.
    apply Hst.
    intros x y Hxy.
    exact (Hxy e0 He0).
Qed.

Definition family_union (A B : Family) : Family :=
  fun e => A e \/ B e.

Definition family_inter (A B : Family) : Family :=
  fun e => A e /\ B e.

(* T6: adding experiments can only refine indistinguishability. *)
Theorem T6_question_monotonicity (A B : Family) :
  family_subset A B -> rel_subset (EqOf B) (EqOf A).
Proof.
  intros HAB s t Hst e He.
  apply Hst.
  apply HAB.
  exact He.
Qed.

(* T7: the joint question is exactly relation intersection. *)
Theorem T7_joint_question_intersection (A B : Family) :
  rel_equiv (EqOf (family_union A B))
            (fun s t => EqOf A s t /\ EqOf B s t).
Proof.
  intros s t; split.
  - intro H; split.
    + intros e He. exact (H e (or_introl He)).
    + intros e He. exact (H e (or_intror He)).
  - intros [HA HB] e [He | He].
    + exact (HA e He).
    + exact (HB e He).
Qed.

Definition ClosedFamily (E : Family) : Prop := family_equiv (Cl E) E.

Theorem closure_is_closed (E : Family) : ClosedFamily (Cl E).
Proof.
  apply T2_closure_idempotent.
Qed.

(* Binary meet of closed reader families is their intersection. *)
Theorem closed_intersection (A B : Family) :
  ClosedFamily A -> ClosedFamily B -> ClosedFamily (family_inter A B).
Proof.
  intros HA HB e; split.
  - intro Hcl; split.
    + apply (proj1 (HA e)).
      intros s t HAt.
      apply Hcl.
      intros x [Hx _].
      exact (HAt x Hx).
    + apply (proj1 (HB e)).
      intros s t HBt.
      apply Hcl.
      intros x [_ Hx].
      exact (HBt x Hx).
  - intros [HeA HeB] s t Hst.
    exact (Hst e (conj HeA HeB)).
Qed.

(* Binary join of closed families is closure of their union. *)
Theorem closed_join (A B : Family) :
  ClosedFamily (Cl (family_union A B)).
Proof.
  apply closure_is_closed.
Qed.

End ReaderDomainCore.

Section ConstructiveFirewall.
(*
  NEW DERIVATION / PROPOSAL, not yet in Toledo — child of TG-RFG-01
  (issue morrocwi/toledo#36). Sits beside this file's existing
  Galois-correspondence family (ReaderDomainCore above), not a
  standalone object.

  What this formalizes, and only this: a bookkeeping fact about which
  sub-family of experiments a derived equivalence relation (EqOf) is
  allowed to range over, when membership is filtered by an abstract,
  uninterpreted predicate Constructive. It says nothing about what
  Constructive means operationally, what it can decide, or any
  separation result. Constructive stays a free Variable : Experiment
  -> Prop — never instantiated, never given intro/elim rules beyond
  what Family/EqOf already have.

  Claim boundary: this section proves generic finite/discrete math
  only. It contains no computational-hardness premise or conclusion
  (no P-vs-NP-shaped claim). Domain instantiation of Constructive
  (e.g. as "decidable in polynomial time", "an actually-performable
  laboratory experiment", etc.) is a separate obligation left to
  future work.

  Not to be confused with: Toledo registry/proposals/
  semantic_closure_accounting_p_vs_np_v0_1.json (PROP-SCA-PNP-01..06,
  also gated under TG-RFG-01), which is a genuinely different, still-
  open P-vs-NP-adjacent circuit-level result about semantic-channel/
  oracle bookkeeping. That cluster and this section share vocabulary
  ("oracle", "semantic universe") by coincidence of domain, not by any
  shared theorem, proof, or object; this section's result is a
  family/EqOf congruence fact, unrelated to circuit-ledger accounting.
*)

Context {State Value : Type}.
Variable Constructive : @Experiment State Value -> Prop.
Variable Ambient : @Family State Value.

Definition A_sem : Family := Ambient.

Definition A_con : Family :=
  fun e => Ambient e /\ Constructive e.

(* Trivial inclusion, by construction. *)
Theorem A_con_subseteq_A_sem :
  family_subset A_con A_sem.
Proof. intros e [Hamb _]. exact Hamb. Qed.

(* Reading (comment only, not a Coq statement): if two candidate
   experiment-families are both confined to the constructively-
   admissible universe A_con and agree on every constructive
   experiment, their induced indistinguishability relations are
   identical relations — the definition of EqOf cannot "see" any
   experiment outside what Constructive already licensed. This is a
   closure/definitional fact about EqOf's quantifier scope, exactly
   parallel to T2_eq_closure_invariant above — not a claim about
   decidability, hardness, or any complexity class. *)
Theorem constructive_closure_invariant :
  forall E1 E2 : Family,
    family_subset E1 A_con ->
    family_subset E2 A_con ->
    (forall e, Constructive e -> (E1 e <-> E2 e)) ->
    rel_equiv (EqOf E1) (EqOf E2).
Proof.
  intros E1 E2 H1 H2 Hagree.
  assert (H12 : family_subset E1 E2).
  { intros e He1. destruct (H1 e He1) as [_ Hcon]. exact (proj1 (Hagree e Hcon) He1). }
  assert (H21 : family_subset E2 E1).
  { intros e He2. destruct (H2 e He2) as [_ Hcon]. exact (proj2 (Hagree e Hcon) He2). }
  intros s t; split.
  - exact (@EqOf_antitone State Value E2 E1 H21 s t).
  - exact (@EqOf_antitone State Value E1 E2 H12 s t).
Qed.

End ConstructiveFirewall.

(*
  Claim boundary for ConstructiveFirewall (restated, section-close
  form matching the header discipline used at the top of this file):
  this section proves generic finite/discrete math only, about the
  quantifier scope of EqOf under an abstract admissibility filter. It
  contains no computational-hardness premise or conclusion — no
  P-vs-NP-shaped claim, no decidability claim about Constructive.
  Domain instantiation of Constructive (what actually counts as
  "constructive" in a given application) is a separate obligation not
  addressed here.
*)

Section FutureReaderDynamics.

Context {State Value Action Reader : Type}.
Variable step : Action -> State -> State.
Variable read : Reader -> State -> Value.

Fixpoint run_word (w : list Action) (s : State) : State :=
  match w with
  | [] => s
  | u :: ws => run_word ws (step u s)
  end.

Definition FutureEq (s t : State) : Prop :=
  forall r w, read r (run_word w s) = read r (run_word w t).

Definition ImmediateEq (s t : State) : Prop :=
  forall r, read r s = read r t.

Theorem future_eq_refl : forall s, FutureEq s s.
Proof. intros s r w; reflexivity. Qed.

Theorem future_eq_sym : forall s t, FutureEq s t -> FutureEq t s.
Proof. intros s t H r w; symmetry; apply H. Qed.

Theorem future_eq_trans : forall s t u,
  FutureEq s t -> FutureEq t u -> FutureEq s u.
Proof.
  intros s t u Hst Htu r w.
  transitivity (read r (run_word w t)); [apply Hst | apply Htu].
Qed.

(* T3: all-future equivalence is stable under every declared first action. *)
Theorem T3_future_equivalence_dynamic_stability :
  forall s t u, FutureEq s t -> FutureEq (step u s) (step u t).
Proof.
  intros s t u H r w.
  specialize (H r (u :: w)).
  simpl in H.
  exact H.
Qed.

(* T4: relational well-definedness kernel for the quotient dynamics.
   Standard quotient semantics turns this statement into q o F = F# o q. *)
Theorem T4_dynamic_weld_well_defined :
  forall u s t, FutureEq s t -> FutureEq (step u s) (step u t).
Proof.
  intros u s t H.
  apply T3_future_equivalence_dynamic_stability.
  exact H.
Qed.

(* T4b: the literal quotient, projection, induced map, and commuting square
   that T4 only licenses as a corollary. This section actually constructs
   q, F#, and proves q o F = F# o q as a machine-checked object, not just
   the congruence property. Toledo occurrence: this is the first concrete
   instantiation of weld/M.02.v1 (CAN-006) supplied by this Foundation, not
   a new weld object. No functional-extensionality or proof-irrelevance
   axiom is used: the commuting square is stated pointwise (as an iff on
   class membership), which is the standard axiom-free way to express
   equality of Prop-valued quotient classes without those axioms. *)

Definition IsFutureClass (P : State -> Prop) : Prop :=
  exists s, forall t, P t <-> FutureEq s t.

Definition QState := { P : State -> Prop | IsFutureClass P }.

(* q : the canonical projection of a state to its future-equivalence class. *)
Definition proj (s : State) : QState :=
  exist IsFutureClass (FutureEq s) (ex_intro _ s (fun t => iff_refl (FutureEq s t))).

Definition step_class (u : Action) (P : State -> Prop) : State -> Prop :=
  fun t => exists s, P s /\ FutureEq (step u s) t.

Lemma step_class_is_class :
  forall u P, IsFutureClass P -> IsFutureClass (step_class u P).
Proof.
  intros u P [s0 Hs0].
  exists (step u s0).
  intro t; split.
  - intros [s [HPs Hft]].
    assert (Hs0s : FutureEq s0 s) by (apply (Hs0 s); exact HPs).
    apply future_eq_trans with (t := step u s).
    + apply T3_future_equivalence_dynamic_stability. exact Hs0s.
    + exact Hft.
  - intro Hft.
    exists s0.
    split.
    + apply (Hs0 s0). apply future_eq_refl.
    + exact Hft.
Qed.

(* F# : the induced transition on quotient classes. *)
Definition Fsharp (u : Action) (Q : QState) : QState :=
  exist IsFutureClass (step_class u (proj1_sig Q))
    (@step_class_is_class u (proj1_sig Q) (proj2_sig Q)).

(* The literal commuting square q o F_u = F#_u o q, stated pointwise on
   class membership (axiom-free: no funext/proof-irrelevance needed). *)
Theorem T4b_quotient_commuting_square :
  forall u s t,
    proj1_sig (Fsharp u (proj s)) t <-> proj1_sig (proj (step u s)) t.
Proof.
  intros u s t. simpl. unfold step_class. split.
  - intros [s' [Hss' Hft]].
    apply future_eq_trans with (t := step u s').
    + apply T3_future_equivalence_dynamic_stability. exact Hss'.
    + exact Hft.
  - intro Hft. exists s. split.
    + apply future_eq_refl.
    + exact Hft.
Qed.

Fixpoint DepthEq (n : nat) (s t : State) : Prop :=
  match n with
  | 0 => ImmediateEq s t
  | S k => ImmediateEq s t /\ forall u, DepthEq k (step u s) (step u t)
  end.

Lemma future_eq_immediate : forall s t, FutureEq s t -> ImmediateEq s t.
Proof.
  intros s t H r.
  specialize (H r []).
  simpl in H.
  exact H.
Qed.

Lemma future_eq_implies_depth :
  forall n s t, FutureEq s t -> DepthEq n s t.
Proof.
  induction n as [|n IH]; intros s t H.
  - apply future_eq_immediate. exact H.
  - split.
    + apply future_eq_immediate. exact H.
    + intro u.
      apply IH.
      apply T3_future_equivalence_dynamic_stability.
      exact H.
Qed.

Lemma depth_immediate :
  forall n s t, DepthEq n s t -> ImmediateEq s t.
Proof.
  destruct n; simpl; intros s t H.
  - exact H.
  - exact (proj1 H).
Qed.

Definition DepthStable (n : nat) : Prop :=
  forall s t, DepthEq n s t <-> DepthEq (S n) s t.

Lemma depth_stable_successor_closed :
  forall n, DepthStable n ->
  forall s t, DepthEq n s t ->
  forall u, DepthEq n (step u s) (step u t).
Proof.
  intros n Hstable s t Hn u.
  pose proof (proj1 (Hstable s t) Hn) as Hnext.
  simpl in Hnext.
  exact (proj2 Hnext u).
Qed.

Lemma depth_stable_implies_future :
  forall n, DepthStable n ->
  forall s t, DepthEq n s t -> FutureEq s t.
Proof.
  intros n Hstable s t Hn r w.
  revert s t Hn.
  induction w as [|u ws IH]; intros s t Hn.
  - simpl.
    pose proof (@depth_immediate n s t Hn) as Himm.
    exact (Himm r).
  - simpl.
    apply IH.
    apply depth_stable_successor_closed with (n := n).
    + exact Hstable.
    + exact Hn.
Qed.

(* Exactness at any finite depth that is a fixed point of refinement. *)
Theorem stable_depth_exact_future :
  forall n, DepthStable n ->
  forall s t, DepthEq n s t <-> FutureEq s t.
Proof.
  intros n Hstable s t; split.
  - intro Hn.
    apply depth_stable_implies_future with (n := n).
    + exact Hstable.
    + exact Hn.
  - intro Hfuture.
    apply future_eq_implies_depth.
    exact Hfuture.
Qed.

End FutureReaderDynamics.

Section SufficiencyKernel.

Context {State Value Rep : Type}.
Definition RelS := State -> State -> Prop.
Variable rho : State -> Rep.

Definition KernelR : RelS := fun s t => rho s = rho t.
Definition SufficientFor (R : RelS) : Prop :=
  forall s t, rho s = rho t -> R s t.

(* T5: exact formal kernel of sufficiency; Toledo CAN-165 supplies the
   generic fiber-constancy <-> factorisation theorem once a target map is named. *)
Theorem T5_sufficiency_kernel_inclusion (R : RelS) :
  SufficientFor R -> forall s t, KernelR s t -> R s t.
Proof.
  intros H s t Hrho.
  exact (H s t Hrho).
Qed.

End SufficiencyKernel.

Section FiniteStrictRefinement.

Context {Partition : Type}.
Variable refine : Partition -> Partition.
Variable closed : Partition -> Prop.
Variable closed_dec : forall P, {closed P} + {~ closed P}.
Variable blocks : Partition -> nat.
Variable bound : nat.

Hypothesis blocks_bounded : forall P, blocks P <= bound.
Hypothesis strict_split_growth :
  forall P, ~ closed P -> blocks P < blocks (refine P).

Fixpoint iterate (n : nat) (P : Partition) : Partition :=
  match n with
  | 0 => P
  | S k => refine (iterate k P)
  end.

Lemma blocks_growth_under_no_closure :
  forall k P,
    (forall j, j < k -> ~ closed (iterate j P)) ->
    blocks P + k <= blocks (iterate k P).
Proof.
  induction k as [|k IH]; intros P Hnone.
  - simpl. lia.
  - simpl.
    assert (Hprev : forall j, j < k -> ~ closed (iterate j P)).
    { intros j Hj. apply Hnone. lia. }
    pose proof (IH P Hprev) as Hgrow.
    assert (Hnot : ~ closed (iterate k P)).
    { apply Hnone. lia. }
    pose proof (@strict_split_growth (iterate k P) Hnot) as Hstrict.
    lia.
Qed.

Lemma closed_or_none_upto :
  forall n P,
    (exists j, j <= n /\ closed (iterate j P)) \/
    (forall j, j <= n -> ~ closed (iterate j P)).
Proof.
  induction n as [|n IH]; intro P.
  - destruct (closed_dec P) as [Hc | Hnc].
    + left. exists 0. simpl. auto.
    + right. intros j Hj.
      assert (j = 0) by lia. subst j. simpl. exact Hnc.
  - destruct (IH P) as [[j [Hj Hc]] | Hnone].
    + left. exists j. split; [lia | exact Hc].
    + destruct (closed_dec (iterate (S n) P)) as [Hc | Hnc].
      * left. exists (S n). split; [lia | exact Hc].
      * right. intros j Hj.
        destruct (Nat.eq_dec j (S n)) as [Heq | Hneq].
        -- subst j. exact Hnc.
        -- apply Hnone. lia.
Qed.

(* Safe replacement kernel for the over-broad Toledo C.05 v1 hypothesis:
   finite bounded partitions + strict splitting whenever not closed imply
   termination. No termination assumption is smuggled into the premise. *)
Theorem finite_strict_refinement_terminates :
  forall P, exists k, closed (iterate k P).
Proof.
  intro P.
  destruct (closed_or_none_upto (S bound) P)
    as [[j [_ Hc]] | Hnone].
  - exists j. exact Hc.
  - exfalso.
    assert (Hgrow : blocks P + S bound <= blocks (iterate (S bound) P)).
    { apply blocks_growth_under_no_closure.
      intros j Hj. apply Hnone. lia. }
    pose proof (blocks_bounded (iterate (S bound) P)) as Hb.
    lia.
Qed.

End FiniteStrictRefinement.

Section RDLBAbstractLayer.
(*
  RDLB v0.1 -- abstract Reader-Domain accumulated-capacity accounting.

  NEW DERIVATION / PROPOSAL, not yet in Toledo.

  What this formalizes, and only this: an abstract nat-valued
  Demand/Capacity accounting law for a reader built by iteratively
  combining "block" readers, together with the finite-arithmetic
  consequences of that law (a bound on demand in terms of accumulated
  capacity, a round/length bound under uniform per-round throughput,
  and the contrapositive capacity-deficit witness). `Sufficient`,
  `Dem`, `Cap`, and `combine` are free Variables throughout this
  section -- never instantiated as circuits, Turing machines,
  resource-bounded computation models, or any other complexity-
  theoretic object. Every quantity in this section is a `nat`
  (`List.length`, `+`, `*`, `<=` only) -- no continuum concept (no
  real number, no limit, no angle, no zero-extent point) appears
  anywhere, so this section is IDM-clean by construction; no
  discrete-replacement table entries are implicated.

  Claim boundary: this section proves generic finite/discrete
  arithmetic only. It contains:
    - no linear algebra of any kind (no Jacobian, no rank, no matrix,
      no norm);
    - no Navier-Stokes / energy-observability claim of any kind (the
      `readout-problem-navier-stokes` repository and its
      `ns_energy_observability.json` artifact are cited here BY NAME
      ONLY, as the motivating application this abstract layer is
      eventually meant to serve -- their content is never restated,
      quoted, or relied on as a premise of anything below);
    - no computational-hardness or complexity-class premise or
      conclusion of any kind, and in particular no P-vs-NP-shaped
      claim of any kind. `combine`, `Sufficient`, `Dem`, and `Cap`
      stay opaque free Variables from open to close of this section;
      nothing here decides, bounds, or reasons about time/space
      complexity, circuit size, or any resource model.

  Disambiguation (required by the reuse-pipeline lookup phase already
  run for this design; see EPIS-REUSE-PIPELINE): Toledo's
  `registry/proposals/semantic_closure_accounting_p_vs_np_v0_1*.json`
  cluster (PROP-SCA-PNP-03/06/07/08/09) is a distinct, still-open
  P-vs-NP-adjacent proposal about circuit/oracle-level semantic-
  channel accounting. This section shares only surface vocabulary
  with that cluster -- Demand, capacity, an accumulation bound, a
  depth/round divergence -- by coincidence of subject matter: there is
  zero shared theorem, zero shared proof, and zero shared Coq object
  between the two. No claim, premise, or conclusion of
  PROP-SCA-PNP-03/06/07/08/09 is made, used, restated, or implied
  here, and nothing in this section resolves, narrows, or otherwise
  bears on the P-vs-NP question in any way.

  Further reuse-pipeline near-hits checked and ruled out (their
  statements were read, not just their names, per EPIS-REUSE-PIPELINE's
  "keyword hits are NOT matches" rule): Toledo CAN-181 (A.8/M.08.v1,
  "PublicOutputVelocity <= VerificationCapacity" in a bottleneck-
  inversion/epistemic-debt economics reading) shares C1's Dem<=Cap
  shape but has no fold-accumulation law and lives in an unrelated
  domain -- not content-equivalent, kept as a same-form-different-
  theory note only. CAN-054 (EQ-015/H.06.v1, rank-bounded LoRA
  factorization) and CAN-065 (weld/H.06.v1, a domain-weld defect
  vector) were checked directly and are unrelated mechanisms (rank-
  bounded update, weld defect), not a Dem/Cap accounting law.
  weld/W.04.v1 and weld/W.11.v1 (validation-capacity-as-a-function
  objects) share the word "capacity" only, different object entirely.
  None of these is reused as a parent; none is duplicated by this
  section.

  Genesis compatibility (EPIS-REUSE-PIPELINE step 2): no existing
  Readout Genesis gate or section was found treating a Demand/Capacity
  accumulation law formally or informally (checked: READOUT_GENESIS_CORE.md,
  keyword sweep for "capacity"/"demand"). This section is therefore new
  infrastructure with no Genesis-side classification yet, not an
  instantiation of an existing gate -- that classification, if any is
  warranted, is a separate, later obligation.

  Parentage (intellectual, not a `Require`): the Sufficient/Dem shape
  used below is directly motivated by this file's own
  `T5_sufficiency_kernel_inclusion` (Section SufficiencyKernel) and
  `T6_question_monotonicity` (Section ReaderDomainCore) -- a
  sufficient reader must dominate whatever the question demands, and
  adding reading power can only add to what is already settled. Those
  two theorems are cited here as the intellectual parents motivating
  the shape of `suff_cap_law` below; they are not `Require`d and are
  not used as premises of any theorem in this section, which is
  self-contained over its own local Variables and Hypotheses.
*)

Context {Question Reader : Type}.
Variable Dem : Question -> nat.
Variable Cap : Reader -> nat.
Variable Sufficient : Reader -> Question -> Prop.
Variable combine : Reader -> Reader -> Reader.
Variable base : Reader.
Variable c0 c : nat.

(* RDLB-C1 -- Sufficiency-Capacity Law (Hypothesis, not derived: this
   is the abstract accounting law this whole layer accepts as given,
   exactly as FiniteStrictRefinement above accepts blocks_bounded /
   strict_split_growth as given rather than derived). *)
Hypothesis suff_cap_law :
  forall R Q, Sufficient R Q -> Dem Q <= Cap R.

(* RDLB-C2 -- block-accumulation subadditivity (Hypothesis). *)
Hypothesis cap_subadditive :
  forall A B, Cap (combine A B) <= Cap A + Cap B.

(* Baseline / per-round throughput hypotheses, matching the
   FiniteStrictRefinement pattern (blocks_bounded style). *)
Hypothesis base_cap_le : Cap base <= c0.
Hypothesis round_cap_bound : forall r : Reader, Cap r <= c.

Definition built (blocks : list Reader) : Reader :=
  fold_left combine blocks base.

(* Local finite sum over nat, defined here rather than relied on from
   the stdlib (portable across Coq versions that may or may not ship
   List.list_sum). *)
Fixpoint list_sum (l : list nat) : nat :=
  match l with
  | [] => 0
  | x :: xs => x + list_sum xs
  end.

(* Generalized fold bound: the accumulated capacity of a left fold
   started from ANY reader R0 is bounded by Cap R0 plus the sum of
   per-block capacities. Proved by list induction using
   cap_subadditive; generalizing over the accumulator R0 is what lets
   this go through directly on fold_left's own left-to-right
   recursion, with no `rev` gymnastics needed. *)
Lemma cap_fold_bound :
  forall (blocks : list Reader) (R0 : Reader),
    Cap (fold_left combine blocks R0) <= Cap R0 + list_sum (map Cap blocks).
Proof.
  induction blocks as [| r blocks IH]; intros R0.
  - simpl. lia.
  - simpl.
    specialize (IH (combine R0 r)).
    pose proof (cap_subadditive R0 r) as Hsub.
    lia.
Qed.

(* Helper: accumulated capacity of a fold-built reader is bounded by
   base capacity plus the sum of per-block capacities. Proved from
   cap_fold_bound (via unfolding `built`) -- NOT restated as a
   hypothesis. *)
Lemma cap_built_bound :
  forall blocks : list Reader,
    Cap (built blocks) <= Cap base + list_sum (map Cap blocks).
Proof.
  intro blocks. unfold built. apply cap_fold_bound.
Qed.

(* RDLB-T1 -- accumulated-capacity bound on demand. *)
Theorem RDLB_T1_accumulation_bound :
  forall (Q : Question) (blocks : list Reader),
    Sufficient (built blocks) Q ->
    Dem Q <= Cap base + list_sum (map Cap blocks).
Proof.
  intros Q blocks Hsuff.
  pose proof (@suff_cap_law (built blocks) Q Hsuff) as H1.
  pose proof (cap_built_bound blocks) as H2.
  lia.
Qed.

(* Helper: uniform per-round throughput collapses the sum bound to a
   multiplication bound. Proved by induction using round_cap_bound. *)
Lemma list_sum_caps_le_length_mul :
  forall blocks : list Reader,
    list_sum (map Cap blocks) <= length blocks * c.
Proof.
  induction blocks as [| r blocks IH].
  - simpl. lia.
  - simpl.
    pose proof (round_cap_bound r) as Hr.
    lia.
Qed.

(* RDLB-T2 -- depth/round bound, multiplication form. Read informally
   as: Dem Q <= c0 + R * c, i.e. (when c > 0 and Dem Q > c0) this is
   equivalent to R >= ceil((Dem Q - c0)/c) -- documented here in this
   comment only; the theorem itself is stated and proved directly in
   multiplication form, via RDLB_T1 + list_sum_caps_le_length_mul +
   base_cap_le, so as to avoid any Nat.div/ceil machinery. *)
Theorem RDLB_T2_round_bound :
  forall (Q : Question) (blocks : list Reader),
    Sufficient (built blocks) Q ->
    Dem Q <= c0 + length blocks * c.
Proof.
  intros Q blocks Hsuff.
  pose proof (@RDLB_T1_accumulation_bound Q blocks Hsuff) as H1.
  pose proof (list_sum_caps_le_length_mul blocks) as H2.
  pose proof base_cap_le as H3.
  lia.
Qed.

(* RDLB-W -- capacity-deficit witness: contrapositive corollary of T2.
   Short and non-vacuous: a strict capacity deficit rules out
   sufficiency for ANY reader built from that many rounds. *)
Theorem RDLB_W_capacity_deficit_witness :
  forall (Q : Question) (blocks : list Reader),
    c0 + length blocks * c < Dem Q ->
    ~ Sufficient (built blocks) Q.
Proof.
  intros Q blocks Hdeficit Hsuff.
  apply RDLB_T2_round_bound in Hsuff.
  lia.
Qed.

End RDLBAbstractLayer.

(*
  Claim boundary for RDLBAbstractLayer (restated, section-close form
  matching the header discipline used at the top of this file, and
  the ConstructiveFirewall section above): this section proves generic
  finite/discrete arithmetic only, about nat-valued Demand/Capacity
  accounting over an abstract fold-built reader. It contains no linear
  algebra, no Navier-Stokes / energy-observability claim
  (`readout-problem-navier-stokes` is cited by name only, never
  restated), and no computational-hardness or complexity-class premise
  or conclusion of any kind -- no P-vs-NP-shaped claim. Disambiguated
  above from Toledo's PROP-SCA-PNP-03/06/07/08/09 cluster: shared
  vocabulary only, zero shared theorem/proof/object.
  `T5_sufficiency_kernel_inclusion` and `T6_question_monotonicity` are
  cited as intellectual parents of the Sufficient/Dem shape only, not
  as `Require`d premises of anything in this section. RDLB v0.1 is a
  NEW DERIVATION / PROPOSAL, not yet in Toledo. Any Navier-Stokes-
  specific instantiation of Dem/Cap/Sufficient/combine remains a
  wholly separate, unaddressed obligation; any PNP-RDLB-shaped
  question is neither raised, closed, narrowed, nor answered by this
  section in either direction. This is not a policy of declaring it
  open regardless of the facts -- it is a statement of what this
  section actually establishes: nothing here bridges the abstract
  finite Dem/Cap accounting proved above to any concrete computational-
  complexity model, so this section supports no claim, positive or
  negative, about P vs NP. Should a rigorous such bridge and a genuine
  closure ever be established elsewhere, honest reporting of that
  result is required, not suppression; this comment asserts only that
  no such bridge exists in this file.
*)

(* ===================================================================== *)
(*  Section FiniteBottleneckRDLB                                          *)
(*                                                                        *)
(*  Framing decision (per founder override, superseding two earlier,     *)
(*  now-discarded Jacobian-based attempts at this section): no Jacobian,  *)
(*  derivative, tangent space, or continuum object anywhere. Everything   *)
(*  below is a `nat`-indexed `Q`-matrix or `Q`-vector, built by REUSING   *)
(*  IDM_Matrix.v's existing `Mat := nat -> nat -> Q`, `Sum`, `mmul`,       *)
(*  `mid`, `mid_left`, `madd` rather than re-deriving matrix algebra --    *)
(*  this section's own instance of the reuse pipeline (EPIS-REUSE-        *)
(*  PIPELINE): parent objects `mmul`, `mid_left`, `Sum_ext_lt`, `Sum_zero`,*)
(*  `Sum_plus` from IDM_Matrix.v, `Require Import`ed above.               *)
(*                                                                        *)
(*  No dependent types for shapes, following IDM_Matrix.v's own           *)
(*  convention: a matrix's "shape" is never encoded in its type -- it is  *)
(*  carried as separate `nat` arguments in each lemma statement (a `Mat`  *)
(*  "is" p x r only in the sense that a lemma quantifies i<p, j<r).       *)
(*                                                                        *)
(*  Claim boundary: this section proves finite Q-linear-algebra facts     *)
(*  only. It contains no Navier-Stokes / energy-observability claim of    *)
(*  any kind, no NS-specific instantiation of any definition below, and   *)
(*  no computational-hardness or complexity-class premise or conclusion   *)
(*  of any kind -- in particular no P-vs-NP-shaped claim. PNP-RDLB stays  *)
(*  fully OPEN, exactly as in RDLBAbstractLayer above; nothing here        *)
(*  touches, narrows, or answers it in either direction.                  *)
(*                                                                        *)
(*  Reuse-pipeline lookup already run for this design (EPIS-REUSE-        *)
(*  PIPELINE step 1, Toledo): Toledo `CAN-054` (`EQ-015/H.06.v1`,          *)
(*  Selective retention as a rank-bounded factorized update (Human        *)
(*  LoRA) states `rank_Q(B_nA_n) <= m_n` as part of its own root           *)
(*  statement, and was checked as the nearest candidate parent for        *)
(*  `TOL2_rank_bound` below. Its own Coq file                             *)
(*  (`coq/canonical/EQ_015__H_06_v1.v`) was read directly, per the         *)
(*  "keyword hits are NOT matches" rule: it does NOT prove a general       *)
(*  rank-of-a-factorization bound in Coq at all -- `CAN_054_finite_       *)
(*  bottleneck` is only the nat-pair predicate `0 < rank_n < dim_n`, and   *)
(*  `CAN_054_finite_bottleneck_satisfiable` only exhibits one witness      *)
(*  pair (1,2); there is no `rank_le`-shaped definition or factorization   *)
(*  object in that file to reuse. `TOL2_rank_bound` below is therefore     *)
(*  PROVED FRESH in this section, not reused from CAN-054's Coq -- CAN-054 *)
(*  is cited as the intellectual motivation for the name finite-bottleneck *)
(*  rank bound only, never as a `Require`d premise, and this section       *)
(*  duplicates none of its Coq objects (renamed from the removed line):    *)
(*  section duplicates none of its Coq objects (`CAN_054_gate_weight_     *)
(*  valid`, `CAN_054_retained_update`, `CAN_054_finite_bottleneck*`,       *)
(*  `CAN_054_Open_empirical_programme` are untouched). Genesis             *)
(*  compatibility (step 2): no existing Readout Genesis gate treats a      *)
(*  factorization-rank / kernel-inclusion law; this section is new         *)
(*  infrastructure with no Genesis-side classification yet. `rank_le`,     *)
(*  `InKer`, TOL-2 through TOL-5, K1-K3 are therefore NEW DERIVATION /      *)
(*  PROPOSAL, not yet in Toledo.                                          *)
(*                                                                        *)
(*  Honest achievable-vs-Hypothesis split (do not read past this without  *)
(*  noting it): everything through `TOL3_sum_rank` is a REAL, fully        *)
(*  derived theorem -- no new axiom, no incomplete-proof marker, no        *)
(*  Hypothesis beyond                                                     *)
(*  the ordinary IDM_Matrix.v lemmas already `Require Import`ed. From      *)
(*  `K4_codim_bound` onward, this section is an explicit, clearly-labeled *)
(*  CONCESSION: proving true subspace codimension (the dimension of an     *)
(*  intersection of kernels inside Q^d) needs basis/independence theory    *)
(*  that exists nowhere in Toledo/IDM today. Rather than fake this via     *)
(*  the genuine-but-misleading-if-misused fact that any p x r matrix has   *)
(*  `rank_le p r p M` (witness `C := mid, D := M`, from `mid_left` --      *)
(*  recorded below as `rank_le_trivial_upper`, and NEVER used to justify   *)
(*  K4: it is a statement about the STACKED CONSTRAINT MATRIX'S OWN SHAPE, *)
(*  not about the true dimension of its nullspace), this section           *)
(*  introduces an abstract, explicitly-labeled `Subspace := Vec -> Prop`   *)
(*  and an uninterpreted relation `HasCodimLe`, exactly as `Sufficient`/    *)
(*  `Cap` are left abstract in RDLBAbstractLayer above. Two Hypotheses,    *)
(*  tagged RDLB-K4-Ax (unproven dimension-counting laws, not derived):     *)
(*  (a) a single kernel cut by m scalar equations has codim <= m; (b)      *)
(*  codim is subadditive under finite intersection. `K4_codim_bound`'s     *)
(*  own statement is deliberately about the FINITE, list-scoped            *)
(*  intersection `InKerListSub Is` it can actually derive from those two   *)
(*  Hypotheses by structural induction -- NOT about the unrestricted       *)
(*  `InKerAll` (quantified over the whole, possibly-infinite index type    *)
(*  `I`). Extending the bound to `InKerAll` for an arbitrary `Is` would    *)
(*  additionally require `HasCodimLe` to respect logical/extensional       *)
(*  equivalence of its `Subspace` argument -- a real, very mild, but       *)
(*  UNSTATED closure property this design's two named Hypotheses do not    *)
(*  grant; adding a third, undisclosed Hypothesis here to paper over that  *)
(*  gap would contradict this section's own two-Hypothesis ledger, so it   *)
(*  is deliberately NOT done -- that extension is left OPEN, flagged, and  *)
(*  not silently assumed. S1 (triviality hypothesis) to S2 (`d <= sum      *)
(*  m_i`) is stated as one further Hypothesis, tagged RDLB-S2-Ax, since    *)
(*  it is the classical injective-implies-domain-dim-le-codomain-dim      *)
(*  fact -- same missing-theory class as K4, and `TOL_RDLB_close` is its   *)
(*  immediate corollary (`exact RDLB_S2_Ax`), not a further derivation.    *)
(*                                                                        *)
(*  Precision fix (peer review, 2026-09-13): the S1 premise MUST be       *)
(*  windowed to `forall i, i < d -> x i == 0`, not `forall i, x i == 0`.   *)
(*  `Vec := nat -> Q` is index-infinite while `InKer d ...` only          *)
(*  constrains coordinates below `d`, so the unwindowed premise is        *)
(*  refutable by `x := fun k => if k =? d then 1 else 0` for EVERY        *)
(*  configuration -- making the unwindowed `RDLB_S2_Ax` provable from     *)
(*  nothing (not a real concession) and `TOL_RDLB_close` uninstantiable   *)
(*  (vacuously true, never usable). Independently confirmed non-vacuous   *)
(*  after windowing: `AA := mid`/`mm := fun _ => d` genuinely satisfies   *)
(*  the windowed premise for a nonzero-outside-d vector. The stray        *)
(*  universally-quantified `dd` (unconnected to `d` or any matrix         *)
(*  dimension) was also removed -- it was harmless only because the      *)
(*  premise was already unsatisfiable; re-adding it after windowing       *)
(*  would make the Hypothesis false, not merely unproven.                *)
(*                                                                        *)
(*  Honest ledger: derived as real theorems -- `meqR`, `rank_le`,          *)
(*  `TOL2_rank_bound`, `mv_mmul_assoc`, `K1_kernel_inclusion`,             *)
(*  `TOL4_no_collapse`, `K2_each`, `K3_sum`, `Sum_split`/block-stacking,    *)
(*  `rank_le_add`, `TOL3_sum_rank`, and the list-scoped form of            *)
(*  `K4_codim_bound`. Assumed as explicit, named Hypotheses --             *)
(*  `RDLB_K4_Ax_single`/`RDLB_K4_Ax_inter` (the two K4 codimension laws)   *)
(*  and `RDLB_S2_Ax` (S2's injectivity-bound law); `TOL_RDLB_close` rests  *)
(*  on the latter alone. IMPORTANT: this means the RDLB endpoint          *)
(*  (`TOL_RDLB_close`) rests ENTIRELY on the named Hypotheses -- none of   *)
(*  the genuinely-derived theorems above it (`TOL2_rank_bound`,           *)
(*  `K1_kernel_inclusion`, `K2_each`, `K3_sum`, `TOL3_sum_rank`) is used   *)
(*  in reaching it. Those theorems establish the kernel-inclusion and     *)
(*  rank-accounting chain in its own right; they do not feed the          *)
(*  codimension closure, which is a separate, still-open concession.      *)
(* ===================================================================== *)
Section FiniteBottleneckRDLB.
Open Scope Q_scope.

Definition Vec := nat -> Q.

(* Rectangular equality: A and B agree entrywise on the p x r window.     *)
Definition meqR (p r : nat) (A B : Mat) : Prop :=
  forall i j, (i < p)%nat -> (j < r)%nat -> A i j == B i j.

(* Matrix-vector product, contracting the shared inner dimension n.       *)
Definition mvmul (n : nat) (A : Mat) (x : Vec) : Vec :=
  fun i => Sum n (fun k => A i k * x k).

(* x lies in the kernel of the first m rows of the (n-column) matrix A.   *)
Definition InKer (d m : nat) (A : Mat) (x : Vec) : Prop :=
  forall i, (i < m)%nat -> mvmul d A x i == 0.

(* Factorization rank: M (p x r) factors through a k-dimensional middle.  *)
Definition rank_le (p r k : nat) (M : Mat) : Prop :=
  exists C D : Mat, meqR p r M (mmul k C D).

(* Genuine but NOT used for K4 (see header): any p x r matrix trivially    *)
(* has rank_le p r p M via mid_left -- a fact about the shape of the       *)
(* constraint matrix itself, not about the true dimension of its kernel.  *)
Lemma rank_le_trivial_upper : forall p r (M : Mat), rank_le p r p M.
Proof.
  intros p r M. exists mid, M. unfold meqR.
  intros i j Hi Hj. symmetry. apply mid_left. exact Hi.
Qed.

(* ---- finite double-sum interchange ---- *)
Lemma Sum_double_swap : forall n m f,
  Sum n (fun k => Sum m (fun l => f k l)) == Sum m (fun l => Sum n (fun k => f k l)).
Proof.
  induction n as [| n' IH]; intros m f.
  - assert (Hz : Sum m (fun l => Sum 0 (fun k : nat => f k l)) == Sum m (fun _ : nat => 0)).
    { apply Sum_ext. intro l. reflexivity. }
    rewrite Hz. symmetry. apply Sum_zero.
  - assert (HL : Sum (S n') (fun k => Sum m (fun l => f k l))
                 == Sum n' (fun k => Sum m (fun l => f k l)) + Sum m (fun l => f n' l)).
    { reflexivity. }
    assert (Hstep : Sum m (fun l => Sum (S n') (fun k => f k l))
                     == Sum m (fun l => Sum n' (fun k => f k l) + f n' l)).
    { apply Sum_ext. intro l. reflexivity. }
    rewrite HL, Hstep, Sum_plus, (IH m f).
    reflexivity.
Qed.

(* ---- reindexing lemma for splitting a finite sum ---- *)
Lemma Sum_split : forall (a b : nat) (f : nat -> Q),
  Sum (a+b) f == Sum a f + Sum b (fun k => f (a+k)%nat).
Proof.
  intros a b. revert a. induction b as [| b' IH]; intros a f.
  - replace (a + 0)%nat with a by lia. simpl. ring.
  - assert (Ha : (a + S b')%nat = S (a + b')) by lia.
    rewrite Ha.
    transitivity (Sum (a+b') f + f (a+b')%nat).
    + reflexivity.
    + rewrite (IH a f).
      transitivity (Sum a f + (Sum b' (fun k => f (a+k)%nat) + f (a+b')%nat)).
      * ring.
      * reflexivity.
Qed.

(* ---- TOL-2: keystone, genuinely derived (proved fresh -- see header    *)
(*      for why CAN-054's own Coq file does not supply this generally) -- *)
Theorem TOL2_rank_bound : forall (d m : nat) (A B : Mat),
  rank_le d d m (mmul m B A).
Proof. intros d m A B. exists B, A. unfold meqR. reflexivity. Qed.

(* ---- helpers: distributing a Q-constant into/out of a finite sum ---- *)
Lemma Sum_mul_const_r : forall n f c, Sum n f * c == Sum n (fun k => f k * c).
Proof. induction n as [| n' IH]; intros f c; simpl; [ ring | rewrite <- IH; ring ]. Qed.

Lemma Sum_mul_const_l : forall n f c, c * Sum n f == Sum n (fun k => c * f k).
Proof. induction n as [| n' IH]; intros f c; simpl; [ ring | rewrite <- IH; ring ]. Qed.

(* ---- mv/mmul associativity, from Sum_double_swap ---- *)
Lemma mv_mmul_assoc : forall (p q : nat) (A B : Mat) (x : Vec) i,
  mvmul q (mmul p A B) x i == mvmul p A (mvmul q B x) i.
Proof.
  intros p q A B x i.
  unfold mvmul, mmul.
  transitivity (Sum q (fun k => Sum p (fun l => A i l * B l k * x k))).
  { apply Sum_ext. intro k. apply Sum_mul_const_r. }
  transitivity (Sum p (fun l => Sum q (fun k => A i l * B l k * x k))).
  { apply Sum_double_swap. }
  apply Sum_ext. intro l.
  transitivity (Sum q (fun k => A i l * (B l k * x k))).
  { apply Sum_ext. intro k. ring. }
  symmetry. apply Sum_mul_const_l.
Qed.

(* pointwise unfolding of mvmul, kept as its own lemma so later `rewrite`s *)
(* can target one specific mvmul occurrence without disturbing others.    *)
Lemma mvmul_unfold : forall n A x i, mvmul n A x i == Sum n (fun k => A i k * x k).
Proof. intros n A x i. reflexivity. Qed.

(* ---- TOL-5/K1: kernel inclusion for one bottleneck, from               *)
(*      mv_mmul_assoc + Sum_ext_lt + Sum_zero ----                        *)
Theorem K1_kernel_inclusion : forall (d m : nat) (A B : Mat) (x : Vec),
  InKer d m A x -> InKer d d (mmul m B A) x.
Proof.
  intros d m A B x Hker i Hi.
  rewrite (mv_mmul_assoc m d B A x i).
  rewrite (mvmul_unfold m B (mvmul d A x) i).
  transitivity (Sum m (fun _ : nat => 0)).
  - apply Sum_ext_lt. intros l Hl. rewrite (Hker l Hl). ring.
  - apply Sum_zero.
Qed.

(* generic congruence: matrices agreeing entrywise on [0,d)x[0,d) give     *)
(* the same mvmul on rows i<d. *)
Lemma mvmul_meqR : forall (d : nat) (M N : Mat) (x : Vec) (i : nat),
  meqR d d M N -> (i < d)%nat -> mvmul d M x i == mvmul d N x i.
Proof.
  intros d M N x i Hmeq Hi. unfold mvmul.
  apply Sum_ext_lt. intros k Hk. rewrite (Hmeq i k Hi Hk). reflexivity.
Qed.

(* ---- TOL-4: no-early-collapse form. The InKer hypothesis is the        *)
(*      scenario framing (this is meant to be read in a situation where   *)
(*      A's kernel condition holds); the entrywise hypothesis meqR is     *)
(*      what the conclusion actually rests on. ----                       *)
Theorem TOL4_no_collapse : forall (d m : nat) (A B O : Mat) (x : Vec),
  InKer d m A x ->
  meqR d d (madd O (mmul m B A)) O ->
  forall i, (i<d)%nat -> mvmul d (madd O (mmul m B A)) x i == mvmul d O x i.
Proof.
  intros d m A B O x _ Hmeq i Hi.
  exact (@mvmul_meqR d (madd O (mmul m B A)) O x i Hmeq Hi).
Qed.

Context {I : Type} (AA BB : I -> Mat) (mm : I -> nat) (d : nat).
Definition InKerAll (x : Vec) : Prop := forall i : I, InKer d (mm i) (AA i) x.

(* ---- K2/K3: N-fold, over an abstract index family sharing ambient dim d --- *)
Theorem K2_each : forall x, InKerAll x ->
  forall i, InKer d d (mmul (mm i) (BB i) (AA i)) x.
Proof.
  intros x Hall i. exact (@K1_kernel_inclusion d (mm i) (AA i) (BB i) x (Hall i)).
Qed.

(* mvmul is additive over madd -- the "trivial mvmul-additivity lemma"    *)
(* the design calls for, used here to push InKer through a fold-sum.      *)
Lemma mvmul_madd : forall n M N x i, mvmul n (madd M N) x i == mvmul n M x i + mvmul n N x i.
Proof.
  intros n M N x i. unfold mvmul, madd.
  transitivity (Sum n (fun k => M i k * x k + N i k * x k)).
  - apply Sum_ext. intro k. ring.
  - apply Sum_plus.
Qed.

Lemma InKer_madd : forall dd m M N x, InKer dd m M x -> InKer dd m N x -> InKer dd m (madd M N) x.
Proof.
  intros dd m M N x HM HN i Hi.
  rewrite (mvmul_madd dd M N x i), (HM i Hi), (HN i Hi). ring.
Qed.

Lemma InKer_zero : forall dd m x, InKer dd m (fun _ _ : nat => 0) x.
Proof.
  intros dd m x i Hi. unfold mvmul.
  transitivity (Sum dd (fun _ : nat => 0)).
  - apply Sum_ext. intro k. ring.
  - apply Sum_zero.
Qed.

Lemma K3_fold_general : forall (Is : list I) (Z : Mat) (x : Vec),
  InKer d d Z x -> InKerAll x ->
  InKer d d (fold_left madd (map (fun i => mmul (mm i) (BB i) (AA i)) Is) Z) x.
Proof.
  induction Is as [| i0 Is' IH]; intros Z x HZ Hall.
  - simpl. exact HZ.
  - simpl. apply IH.
    + apply InKer_madd; [exact HZ | exact (@K2_each x Hall i0)].
    + exact Hall.
Qed.

Theorem K3_sum (Is : list I) : forall x, InKerAll x ->
  InKer d d (fold_left madd (map (fun i => mmul (mm i) (BB i) (AA i)) Is)
                            (fun _ _ => 0)) x.
Proof.
  intros x Hall. apply K3_fold_general; [apply InKer_zero | exact Hall].
Qed.

(* ---- TOL-3/F2: rank of a finite sum, via hcat/vcat block-stacking + Sum_split --- *)

(* horizontal / vertical block concatenation along the shared middle dim  *)
Definition hcat (k1 : nat) (C1 C2 : Mat) : Mat :=
  fun i j => if Nat.ltb j k1 then C1 i j else C2 i (j - k1)%nat.

Definition vcat (k1 : nat) (D1 D2 : Mat) : Mat :=
  fun i j => if Nat.ltb i k1 then D1 i j else D2 (i - k1)%nat j.

Lemma hcat_left : forall (k1 : nat) (C1 C2 : Mat) (i j : nat), (j < k1)%nat -> hcat k1 C1 C2 i j = C1 i j.
Proof.
  intros k1 C1 C2 i j Hj. unfold hcat.
  destruct (Nat.ltb j k1) eqn:E.
  - reflexivity.
  - exfalso. apply Nat.ltb_ge in E. lia.
Qed.

Lemma hcat_right : forall (k1 : nat) (C1 C2 : Mat) (i t : nat), hcat k1 C1 C2 i (k1+t)%nat = C2 i t.
Proof.
  intros k1 C1 C2 i t. unfold hcat.
  destruct (Nat.ltb (k1+t)%nat k1) eqn:E.
  - exfalso. apply Nat.ltb_lt in E. lia.
  - f_equal. lia.
Qed.

Lemma vcat_left : forall (k1 : nat) (D1 D2 : Mat) (i j : nat), (i < k1)%nat -> vcat k1 D1 D2 i j = D1 i j.
Proof.
  intros k1 D1 D2 i j Hi. unfold vcat.
  destruct (Nat.ltb i k1) eqn:E.
  - reflexivity.
  - exfalso. apply Nat.ltb_ge in E. lia.
Qed.

Lemma vcat_right : forall (k1 : nat) (D1 D2 : Mat) (t j : nat), vcat k1 D1 D2 (k1+t)%nat j = D2 t j.
Proof.
  intros k1 D1 D2 t j. unfold vcat.
  destruct (Nat.ltb (k1+t)%nat k1) eqn:E.
  - exfalso. apply Nat.ltb_lt in E. lia.
  - f_equal. lia.
Qed.

Theorem rank_le_add : forall (p r k1 k2 : nat) (M1 M2 : Mat),
  rank_le p r k1 M1 -> rank_le p r k2 M2 -> rank_le p r (k1+k2)%nat (madd M1 M2).
Proof.
  intros p r k1 k2 M1 M2 [C1 [D1 H1]] [C2 [D2 H2]].
  exists (hcat k1 C1 C2), (vcat k1 D1 D2).
  intros i j Hi Hj.
  unfold madd.
  rewrite (H1 i j Hi Hj), (H2 i j Hi Hj).
  unfold mmul.
  transitivity (Sum k1 (fun k => hcat k1 C1 C2 i k * vcat k1 D1 D2 k j)
                + Sum k2 (fun t => hcat k1 C1 C2 i (k1+t)%nat * vcat k1 D1 D2 (k1+t)%nat j)).
  - assert (E1 : Sum k1 (fun k => C1 i k * D1 k j)
                 == Sum k1 (fun k => hcat k1 C1 C2 i k * vcat k1 D1 D2 k j)).
    { apply Sum_ext_lt. intros k Hk.
      rewrite (@hcat_left k1 C1 C2 i k Hk), (@vcat_left k1 D1 D2 k j Hk). reflexivity. }
    assert (E2 : Sum k2 (fun t => C2 i t * D2 t j)
                 == Sum k2 (fun t => hcat k1 C1 C2 i (k1+t)%nat * vcat k1 D1 D2 (k1+t)%nat j)).
    { apply Sum_ext. intro t.
      rewrite (@hcat_right k1 C1 C2 i t), (@vcat_right k1 D1 D2 t j). reflexivity. }
    rewrite E1, E2. reflexivity.
  - symmetry. apply Sum_split.
Qed.

Lemma rank_le_zero : forall p r : nat, rank_le p r 0 (fun _ _ : nat => 0).
Proof. intros p r. exists (fun _ _ => 0), (fun _ _ => 0). intros i j Hi Hj. reflexivity. Qed.

Lemma TOL3_fold_general : forall (Is : list I) (r : nat) (Z : Mat) (k0 : nat),
  rank_le r r k0 Z ->
  (forall i, In i Is -> rank_le r r (mm i) (mmul (mm i) (BB i) (AA i))) ->
  rank_le r r (k0 + list_sum (map mm Is))%nat
    (fold_left madd (map (fun i => mmul (mm i) (BB i) (AA i)) Is) Z).
Proof.
  induction Is as [| i0 Is' IH]; intros r Z k0 HZ Hall.
  - simpl. replace (k0+0)%nat with k0 by lia. exact HZ.
  - simpl.
    assert (Hi0 : rank_le r r (mm i0) (mmul (mm i0) (BB i0) (AA i0))).
    { apply Hall. left. reflexivity. }
    assert (Hstep : rank_le r r (k0 + mm i0)%nat (madd Z (mmul (mm i0) (BB i0) (AA i0)))).
    { apply rank_le_add; [exact HZ | exact Hi0]. }
    specialize (IH r (madd Z (mmul (mm i0) (BB i0) (AA i0))) (k0 + mm i0)%nat Hstep
                  (fun i Hin => Hall i (or_intror Hin))).
    replace (k0 + (mm i0 + list_sum (map mm Is')))%nat with (k0 + mm i0 + list_sum (map mm Is'))%nat by lia.
    exact IH.
Qed.

Theorem TOL3_sum_rank (Is : list I) (r : nat) :
  (forall i, In i Is -> rank_le r r (mm i) (mmul (mm i) (BB i) (AA i))) ->
  rank_le r r (list_sum (map mm Is))%nat
    (fold_left madd (map (fun i => mmul (mm i) (BB i) (AA i)) Is) (fun _ _ => 0)).
Proof.
  intros Hall.
  pose proof (@TOL3_fold_general Is r (fun _ _ => 0) 0 (@rank_le_zero r r) Hall) as Hgen.
  simpl in Hgen. exact Hgen.
Qed.

(* ---- K4 / S1-S2 / TOL-RDLB: abstract dimension-counting, Hypotheses only --- *)
Definition Subspace := Vec -> Prop.
Variable HasCodimLe : Subspace -> nat -> Prop.

Hypothesis RDLB_K4_Ax_single : forall (dd m : nat) (A : Mat),
  HasCodimLe (InKer dd m A) m.
Hypothesis RDLB_K4_Ax_inter : forall (S1 S2 : Subspace) (c1 c2 : nat),
  HasCodimLe S1 c1 -> HasCodimLe S2 c2 ->
  HasCodimLe (fun x => S1 x /\ S2 x) (c1+c2)%nat.

(* The finite, list-scoped intersection this section can actually reason  *)
(* about (see header for why this is not the unrestricted InKerAll):      *)
(* the empty case reuses RDLB_K4_Ax_single at m=0 (vacuously true for any  *)
(* dummy matrix) rather than introducing an un-derivable `True` subspace, *)
(* so the whole induction stays inside the two given Hypotheses.          *)
Fixpoint InKerListSub (Is : list I) : Subspace :=
  match Is with
  | [] => InKer d 0 (fun _ _ : nat => 0)
  | i :: Is' => fun x => InKer d (mm i) (AA i) x /\ InKerListSub Is' x
  end.

Theorem K4_codim_bound (Is : list I) :
  HasCodimLe (InKerListSub Is) (list_sum (map mm Is))%nat.
Proof.
  induction Is as [| i0 Is' IH]; simpl.
  - apply RDLB_K4_Ax_single.
  - apply RDLB_K4_Ax_inter.
    + apply RDLB_K4_Ax_single.
    + exact IH.
Qed.

Hypothesis RDLB_S2_Ax : forall (Is : list I),
  (forall x, InKerAll x -> forall i, (i < d)%nat -> x i == 0) ->
  (d <= list_sum (map mm Is))%nat.

Theorem TOL_RDLB_close (Is : list I) :
  (forall x, InKerAll x -> forall i, (i < d)%nat -> x i == 0) ->
  (d <= list_sum (map mm Is))%nat.
Proof. exact (@RDLB_S2_Ax Is). Qed.

Close Scope Q_scope.
End FiniteBottleneckRDLB.

(*
  Claim boundary for FiniteBottleneckRDLB (section-close form, matching
  the header discipline used throughout this file): this section proves
  finite Q-matrix linear algebra only (`meqR`, `rank_le`, `InKer`,
  `mvmul`), reusing IDM_Matrix.v's `Mat`/`Sum`/`mmul`/`mid`/`madd` rather
  than re-deriving them. It contains no Jacobian, derivative, tangent
  space, or continuum object of any kind. It contains no Navier-Stokes /
  energy-observability claim (no NS-specific instantiation of `AA`, `BB`,
  `mm`, or `d` is made anywhere), and no computational-hardness or
  complexity-class premise or conclusion of any kind -- no P-vs-NP-shaped
  claim; PNP-RDLB stays fully OPEN, exactly as declared in
  RDLBAbstractLayer above. `TOL2_rank_bound` through `TOL3_sum_rank` are
  genuinely derived theorems (no Hypothesis beyond IDM_Matrix.v's own
  axiom-free lemma base). `K4_codim_bound` is genuinely derived for the
  finite, list-scoped intersection `InKerListSub Is` from the two named
  Hypotheses `RDLB_K4_Ax_single`/`RDLB_K4_Ax_inter` -- extending it to the
  unrestricted `InKerAll` over an arbitrary index type `I` is a further,
  separate obligation this section does not silently assume (it would
  need `HasCodimLe` to respect logical equivalence of its `Subspace`
  argument, a property neither named Hypothesis grants). `TOL_RDLB_close`
  is a direct corollary of the single named Hypothesis `RDLB_S2_Ax`, not a
  further derivation. Its premise is windowed to `forall i, i<d -> x i
  == 0` (peer-review fix, 2026-09-13): the earlier unwindowed form was
  vacuously refutable over `Vec := nat -> Q`'s index-infinite domain,
  which would have made `RDLB_S2_Ax` provable from nothing and
  `TOL_RDLB_close` never usable; independently confirmed non-vacuous
  after the fix. IMPORTANT: `TOL_RDLB_close`, the RDLB endpoint, rests
  ENTIRELY on `RDLB_S2_Ax` -- none of this section's genuinely-derived
  theorems (`TOL2_rank_bound`, `K1_kernel_inclusion`, `K2_each`,
  `K3_sum`, `TOL3_sum_rank`) is used in reaching it; they establish the
  kernel-inclusion/rank-accounting chain in its own right, not as an
  input to the codimension closure. This is NEW DERIVATION / PROPOSAL, not yet in
  Toledo. Toledo `CAN-054` (`EQ-015/H.06.v1`) is cited as the intellectual
  motivation for `TOL2_rank_bound`'s name only -- its own Coq file proves
  no general rank bound, so `TOL2_rank_bound` here is fresh, not reused,
  and none of CAN-054's Coq identifiers are duplicated. No claim, premise
  or conclusion of Toledo's `PROP-SCA-PNP-03/06/07/08/09` cluster is made,
  used, restated, or implied here, for the same reasons given for
  RDLBAbstractLayer above.
*)
