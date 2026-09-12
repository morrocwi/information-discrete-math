(*
  IDM_ReaderDomainFoundation.v

  Genesis Reader-Domain Foundation v1 — safe generic kernel.

  Scope:
  - reader/indistinguishability correspondence (T1)
  - closure operator and saturation invariance (T2)
  - future-reader dynamic stability / quotient well-definedness kernel (T3/T4)
  - sufficiency => kernel inclusion (T5; factorisation itself is Toledo CAN-165)
  - question monotonicity and joint-question intersection (T6/T7)
  - binary closure-lattice laws for closed reader families
  - finite strict-refinement termination with explicit hypotheses (safe C.05 replacement kernel)
  - stable finite-depth reader equivalence equals all-future reader equivalence

  Claim boundary:
  This file proves generic finite/discrete mathematics only. It contains no
  continuum premise and no Clay conclusion. Domain encodings and semantic
  bridges are separate obligations.
*)

From Coq Require Import List Arith Lia.
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
