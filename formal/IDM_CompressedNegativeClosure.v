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

Print Assumptions neg_cert_sound.
Print Assumptions true_state_has_no_negative_certificate.
Print Assumptions shared_child_reuse.

End CompressedNegativeClosure.
