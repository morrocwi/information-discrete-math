(* ===================================================================== *)
(* IDM_CompressedNegativeClosure.v                                        *)
(* Soundness kernel for finite negative-closure certificates.              *)
(*                                                                       *)
(* A state admits a declared binary split.  SAT-style semantics obey      *)
(*   sat(s) = sat(left(s,c)) OR sat(right(s,c)).                           *)
(* Leaves may close only through an independently sound local rejector.    *)
(* A finite closure certificate proves the root false by induction.        *)
(*                                                                       *)
(* This file proves certificate soundness only.  It does NOT prove that    *)
(* every UNSAT instance has a polynomial-size certificate, nor any         *)
(* unrestricted circuit lower bound or P <> NP result.                     *)
(* ===================================================================== *)

From Coq Require Import Bool.Bool.

Module CompressedNegativeClosure.

Section Closure.

  Variables State Choice : Type.
  Variable sat : State -> bool.
  Variable left right : State -> Choice -> State.
  Variable leaf_reject : State -> bool.

  Hypothesis split_law :
    forall s c,
      sat s = orb (sat (left s c)) (sat (right s c)).

  Hypothesis leaf_reject_sound :
    forall s,
      leaf_reject s = true -> sat s = false.

  Inductive neg_cert : State -> Prop :=
  | NCLeaf :
      forall s,
        leaf_reject s = true ->
        neg_cert s
  | NCSplit :
      forall s c,
        neg_cert (left s c) ->
        neg_cert (right s c) ->
        neg_cert s.

  Theorem neg_cert_sound :
    forall s,
      neg_cert s ->
      sat s = false.
  Proof.
    intros s Hcert.
    induction Hcert as [s Hleaf|s c Hl IHl Hr IHr].
    - now apply leaf_reject_sound.
    - rewrite split_law.
      rewrite IHl, IHr.
      reflexivity.
  Qed.

  Theorem true_state_has_no_negative_certificate :
    forall s,
      sat s = true ->
      ~ neg_cert s.
  Proof.
    intros s Htrue Hcert.
    pose proof (neg_cert_sound s Hcert) as Hfalse.
    rewrite Htrue in Hfalse.
    discriminate.
  Qed.

  (* Logical reuse lemma.  A concrete DAG checker may store one child node
     once and reference it twice.  The inductive proposition itself does not
     claim a bound on serialized proof size; it records only semantic reuse. *)
  Theorem shared_child_reuse :
    forall s c t,
      left s c = t ->
      right s c = t ->
      neg_cert t ->
      neg_cert s.
  Proof.
    intros s c t Hl Hr Ht.
    apply (NCSplit s c).
    - rewrite Hl. exact Ht.
    - rewrite Hr. exact Ht.
  Qed.

End Closure.

(* --------------------------------------------------------------------- *)
(* Oracle-leaf guard.                                                     *)
(*                                                                       *)
(* If a purported local rejector is allowed to call the target semantics  *)
(* [sat] itself, every negative state becomes a one-step leaf by          *)
(* definition.  Therefore any asymptotic lower bound must charge/restrict  *)
(* the rejector and require independent soundness evidence.               *)
(* --------------------------------------------------------------------- *)
Section OracleLeafGuard.

  Variable State : Type.
  Variable sat : State -> bool.

  Definition semantic_oracle_reject (s : State) : bool := negb (sat s).

  Theorem semantic_oracle_reject_sound :
    forall s,
      semantic_oracle_reject s = true ->
      sat s = false.
  Proof.
    intros s H.
    unfold semantic_oracle_reject in H.
    apply Bool.negb_true_iff in H.
    exact H.
  Qed.

  Theorem every_false_state_is_oracle_leaf :
    forall s,
      sat s = false ->
      semantic_oracle_reject s = true.
  Proof.
    intros s H.
    unfold semantic_oracle_reject.
    rewrite H.
    reflexivity.
  Qed.

End OracleLeafGuard.

Print Assumptions neg_cert_sound.
Print Assumptions true_state_has_no_negative_certificate.
Print Assumptions shared_child_reuse.
Print Assumptions semantic_oracle_reject_sound.
Print Assumptions every_false_state_is_oracle_leaf.

End CompressedNegativeClosure.
