(* ===================================================================== *)
(* IDM_FusionSurvivorRefuter.v                                            *)
(* Fusion/Horn survivor -> concrete semantic mismatch dichotomy.           *)
(*                                                                       *)
(* For a target-positive point a, suppose a retained family contains every *)
(* true input/literal slice, is upward closed, preserves every AND step,    *)
(* and every retained slice is nonempty.  Then a true gate propagates its  *)
(* target-negative slice into the retained family.  At the output:          *)
(*                                                                       *)
(*   C(a)=false, or there exists u with target(u)=false and C(u)=true.      *)
(*                                                                       *)
(* Thus a preserving survivor above a yields an actual false negative or    *)
(* false positive.  The theorem is semantic; it does NOT construct the      *)
(* survivor or prove a lower bound on circuit size.                         *)
(* ===================================================================== *)

From Coq Require Import Bool.Bool.

Module FusionSurvivorRefuter.

Section Survivor.

  Variable X : Type.

  Inductive Circuit : Type :=
  | Lit : (X -> bool) -> Circuit
  | COr : Circuit -> Circuit -> Circuit
  | CAnd : Circuit -> Circuit -> Circuit.

  Fixpoint eval (c : Circuit) (x : X) : bool :=
    match c with
    | Lit f => f x
    | COr l r => orb (eval l x) (eval r x)
    | CAnd l r => andb (eval l x) (eval r x)
    end.

  Variable target : X -> bool.

  Definition neg_slice (c : Circuit) : X -> bool :=
    fun x => andb (eval c x) (negb (target x)).

  Definition subsetb (p q : X -> bool) : Prop :=
    forall x, p x = true -> q x = true.

  Variable Retained : (X -> bool) -> Prop.
  Variable a : X.

  (* Fusion "above a" seed condition for literal/input generators. *)
  Hypothesis literal_above :
    forall f,
      f a = true ->
      Retained (neg_slice (Lit f)).

  Hypothesis upward_closed :
    forall p q,
      Retained p ->
      subsetb p q ->
      Retained q.

  (* One premise per AND-lineage operation.  In the concrete fusion model
     this follows from preservation of the corresponding pair. *)
  Hypothesis and_preserved :
    forall l r,
      Retained (neg_slice l) ->
      Retained (neg_slice r) ->
      Retained (neg_slice (CAnd l r)).

  (* Equivalent to the semi-filter prohibition of the empty set, stated in
     an extraction-friendly form. *)
  Hypothesis retained_nonempty :
    forall p,
      Retained p ->
      exists x, p x = true.

  Lemma left_slice_below_or :
    forall l r,
      subsetb (neg_slice l) (neg_slice (COr l r)).
  Proof.
    intros l r x H.
    unfold neg_slice, subsetb in *.
    simpl in *.
    destruct (eval l x), (eval r x), (target x); simpl in *;
      try discriminate; reflexivity.
  Qed.

  Lemma right_slice_below_or :
    forall l r,
      subsetb (neg_slice r) (neg_slice (COr l r)).
  Proof.
    intros l r x H.
    unfold neg_slice, subsetb in *.
    simpl in *.
    destruct (eval l x), (eval r x), (target x); simpl in *;
      try discriminate; reflexivity.
  Qed.

  Theorem true_gate_retains_negative_slice :
    forall c,
      eval c a = true ->
      Retained (neg_slice c).
  Proof.
    induction c as [f|l IHl r IHr|l IHl r IHr]; intros Htrue.
    - simpl in Htrue. now apply literal_above.
    - simpl in Htrue.
      apply Bool.orb_true_iff in Htrue as [Hl | Hr].
      + eapply upward_closed.
        * now apply IHl.
        * apply left_slice_below_or.
      + eapply upward_closed.
        * now apply IHr.
        * apply right_slice_below_or.
    - simpl in Htrue.
      apply Bool.andb_true_iff in Htrue as [Hl Hr].
      apply and_preserved.
      + now apply IHl.
      + now apply IHr.
  Qed.

  Theorem survivor_yields_mismatch :
    forall c,
      target a = true ->
      (eval c a = false) \/
      (exists u,
          target u = false /\
          eval c u = true).
  Proof.
    intros c Ha.
    destruct (eval c a) eqn:Hca.
    - right.
      pose proof (true_gate_retains_negative_slice c Hca) as Hret.
      destruct (retained_nonempty (neg_slice c) Hret) as [u Hu].
      unfold neg_slice in Hu.
      apply Bool.andb_true_iff in Hu as [Hcu Hneg].
      apply Bool.negb_true_iff in Hneg.
      exists u. split; assumption.
    - left. exact Hca.
  Qed.

End Survivor.

Print Assumptions left_slice_below_or.
Print Assumptions right_slice_below_or.
Print Assumptions true_gate_retains_negative_slice.
Print Assumptions survivor_yields_mismatch.

End FusionSurvivorRefuter.
