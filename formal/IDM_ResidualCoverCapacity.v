(* ===================================================================== *)
(* IDM_ResidualCoverCapacity.v                                            *)
(* Exact finite one-rule capacity kernel for residual cover debt.          *)
(*                                                                       *)
(* A prefix of selected cover rules may already cover some universe        *)
(* elements.  If, after appending one new rule [r], a tail covers every    *)
(* still-uncovered element, then before appending [r] the enlarged tail    *)
(* [r :: tail] covers every still-uncovered element.                       *)
(*                                                                       *)
(* Therefore one newly selected rule can reduce the minimum number of      *)
(* additional cover rules required by at most one.  The file proves the    *)
(* certificate-transfer kernel, not existence/growth of a hard SAT cover.  *)
(* No circuit lower bound or P <> NP claim is made here.                   *)
(* ===================================================================== *)

From Coq Require Import Lists.List Bool.Bool.
Import ListNotations.

Module ResidualCoverCapacity.

Section Cover.

  Variables U Rule : Type.
  Variable hit : Rule -> U -> bool.

  Fixpoint coveredb (rules : list Rule) (u : U) : bool :=
    match rules with
    | [] => false
    | r :: rs => orb (hit r u) (coveredb rs u)
    end.

  Lemma coveredb_app :
    forall xs ys u,
      coveredb (xs ++ ys) u = orb (coveredb xs u) (coveredb ys u).
  Proof.
    induction xs as [|x xs IH]; intros ys u; simpl.
    - reflexivity.
    - rewrite IH. now rewrite orb_assoc.
  Qed.

  Definition covers_remaining (prefix tail : list Rule) : Prop :=
    forall u,
      coveredb prefix u = false ->
      coveredb tail u = true.

  (** One-rule capacity theorem at the certificate level.  If [tail]
      suffices after adding [r] to the prefix, then [r::tail] suffices
      before adding it. *)
  Theorem one_rule_capacity :
    forall prefix r tail,
      covers_remaining (prefix ++ [r]) tail ->
      covers_remaining prefix (r :: tail).
  Proof.
    intros prefix r tail Hafter u Hprefix.
    unfold covers_remaining in Hafter.
    simpl.
    destruct (hit r u) eqn:Hr.
    - reflexivity.
    - simpl.
      apply Hafter.
      rewrite coveredb_app.
      rewrite Hprefix. simpl. exact Hr.
  Qed.

  (** The length of the before-tail certificate is exactly one larger. *)
  Theorem one_rule_capacity_length :
    forall prefix r tail,
      covers_remaining (prefix ++ [r]) tail ->
      exists before_tail,
        covers_remaining prefix before_tail /\
        length before_tail = S (length tail).
  Proof.
    intros prefix r tail H.
    exists (r :: tail).
    split.
    - now apply one_rule_capacity.
    - reflexivity.
  Qed.

End Cover.

Print Assumptions coveredb_app.
Print Assumptions one_rule_capacity.
Print Assumptions one_rule_capacity_length.

End ResidualCoverCapacity.
