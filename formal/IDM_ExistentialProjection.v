(* ===================================================================== *)
(* IDM_ExistentialProjection.v                                            *)
(* Exact finite semantics of existential projection for the P-vs-NP lane. *)
(*                                                                       *)
(* This file is intentionally structural.  It proves only the finite       *)
(* witness-list semantics of an existential readout.  It contains no       *)
(* complexity lower bound and no P <> NP claim.                            *)
(* ===================================================================== *)

From Coq Require Import Lists.List Bool.Bool.
Import ListNotations.

Module ExistentialProjection.

Section Projection.

  Variables X W : Type.
  Variable rel : X -> W -> bool.
  Variable witnesses : list W.

  Definition exists_readout (x : X) : bool :=
    existsb (fun w => rel x w) witnesses.

  Theorem witness_implies_exists_readout_true :
    forall x w,
      In w witnesses ->
      rel x w = true ->
      exists_readout x = true.
  Proof.
    intros x w Hin Hrel.
    unfold exists_readout.
    apply existsb_exists.
    exists w. split; assumption.
  Qed.

  Theorem exists_readout_true_has_witness :
    forall x,
      exists_readout x = true ->
      exists w,
        In w witnesses /\ rel x w = true.
  Proof.
    intros x H.
    unfold exists_readout in H.
    apply existsb_exists in H.
    exact H.
  Qed.

  Theorem all_rejected_implies_exists_readout_false :
    forall x,
      (forall w, In w witnesses -> rel x w = false) ->
      exists_readout x = false.
  Proof.
    intros x Hall.
    unfold exists_readout.
    induction witnesses as [|w ws IH].
    - reflexivity.
    - simpl.
      rewrite Hall by (left; reflexivity).
      simpl.
      apply IH.
      intros w' Hin.
      apply Hall.
      right; assumption.
  Qed.

End Projection.

Print Assumptions witness_implies_exists_readout_true.
Print Assumptions exists_readout_true_has_witness.
Print Assumptions all_rejected_implies_exists_readout_false.

End ExistentialProjection.
