(* ===================================================================== *)
(* IDM_DecisionReadout.v                                                  *)
(* Structural lemmas for the P-vs-NP readout research lane.               *)
(*                                                                        *)
(* Scope: finite/logical structure only. These lemmas do NOT prove        *)
(* P <> NP. They establish the exact obstruction that any resource-aware  *)
(* extension must strengthen.                                             *)
(* ===================================================================== *)

Module DecisionReadout.

Section Collision.
  Variables X R : Type.
  Variable L : X -> bool.
  Variable q : X -> R.
  Variable D : R -> bool.

  Definition decision_correct : Prop :=
    forall x : X, D (q x) = L x.

  Definition mixed_fiber : Prop :=
    exists x y : X, q x = q y /\ L x <> L y.

  Lemma decision_correct_forces_label_constant_on_fibers :
    decision_correct ->
    forall x y : X, q x = q y -> L x = L y.
  Proof.
    intros Hcorrect x y Hq.
    rewrite <- (Hcorrect x), <- (Hcorrect y), Hq.
    reflexivity.
  Qed.

  Lemma mixed_fiber_blocks_exact_decoding :
    mixed_fiber -> ~ decision_correct.
  Proof.
    intros [x [y [Hq Hneq]]] Hcorrect.
    apply Hneq.
    apply (decision_correct_forces_label_constant_on_fibers Hcorrect x y Hq).
  Qed.
End Collision.

Section OneBitDegeneracy.
  Variable X : Type.
  Variable L : X -> bool.

  Definition answer_readout (x : X) : bool := L x.
  Definition identity_decoder (b : bool) : bool := b.

  Lemma one_bit_answer_readout_is_exact :
    forall x : X, identity_decoder (answer_readout x) = L x.
  Proof.
    intro x. reflexivity.
  Qed.
End OneBitDegeneracy.

Section Refinement.
  Variables X Rcoarse Rfine : Type.
  Variable L : X -> bool.
  Variable qcoarse : X -> Rcoarse.
  Variable qfine : X -> Rfine.
  Variable forget : Rfine -> Rcoarse.
  Hypothesis Hfactor : forall x : X, qcoarse x = forget (qfine x).

  Lemma sufficient_coarse_readout_lifts_to_refinement :
    forall Dcoarse : Rcoarse -> bool,
      (forall x : X, Dcoarse (qcoarse x) = L x) ->
      exists Dfine : Rfine -> bool,
        forall x : X, Dfine (qfine x) = L x.
  Proof.
    intros Dcoarse Hcorrect.
    exists (fun r => Dcoarse (forget r)).
    intro x.
    rewrite <- Hfactor.
    apply Hcorrect.
  Qed.
End Refinement.

Print Assumptions decision_correct_forces_label_constant_on_fibers.
Print Assumptions mixed_fiber_blocks_exact_decoding.
Print Assumptions one_bit_answer_readout_is_exact.
Print Assumptions sufficient_coarse_readout_lifts_to_refinement.

End DecisionReadout.
