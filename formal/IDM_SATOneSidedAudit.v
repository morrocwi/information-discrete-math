(* ===================================================================== *)
(* IDM_SATOneSidedAudit.v                                                 *)
(* One-sided local audit theorems for an existential OR restriction tree.  *)
(*                                                                       *)
(* Positive candidate claims need only one sound true leaf once every      *)
(* internal candidate label obeys the OR recursion. Negative claims need   *)
(* the dual universal false-leaf condition. This records the finite         *)
(* existential asymmetry; it proves no complexity-class separation.        *)
(* ===================================================================== *)

From Coq Require Import Bool.Bool.

Module SATOneSidedAudit.

Inductive CTree : Type :=
| CLeaf : bool -> bool -> CTree
(* [CLeaf target candidate] *)
| CNode : bool -> CTree -> CTree -> CTree.
(* [CNode candidate left right] *)

Fixpoint candidate_root (t : CTree) : bool :=
  match t with
  | CLeaf _ c => c
  | CNode c _ _ => c
  end.

Fixpoint target_value (t : CTree) : bool :=
  match t with
  | CLeaf target _ => target
  | CNode _ l r => orb (target_value l) (target_value r)
  end.

Fixpoint node_consistent (t : CTree) : Prop :=
  match t with
  | CLeaf _ _ => True
  | CNode c l r =>
      c = orb (candidate_root l) (candidate_root r)
      /\ node_consistent l
      /\ node_consistent r
  end.

Fixpoint true_leaf_sound (t : CTree) : Prop :=
  match t with
  | CLeaf target c => c = true -> target = true
  | CNode _ l r => true_leaf_sound l /\ true_leaf_sound r
  end.

Fixpoint false_leaf_sound (t : CTree) : Prop :=
  match t with
  | CLeaf target c => c = false -> target = false
  | CNode _ l r => false_leaf_sound l /\ false_leaf_sound r
  end.

Theorem positive_claim_sound :
  forall t,
    node_consistent t ->
    true_leaf_sound t ->
    candidate_root t = true ->
    target_value t = true.
Proof.
  induction t as [target c|c l IHl r IHr].
  - simpl. intros _ Hleaf Hc. now apply Hleaf.
  - simpl.
    intros [Hc [Hnl Hnr]] [Htl Htr] Hroot.
    rewrite Hc in Hroot.
    destruct (candidate_root l) eqn:Hl;
    destruct (candidate_root r) eqn:Hr; simpl in Hroot.
    + specialize (IHl Hnl Htl Hl).
      rewrite IHl. reflexivity.
    + specialize (IHl Hnl Htl Hl).
      rewrite IHl. reflexivity.
    + specialize (IHr Hnr Htr Hr).
      rewrite IHr. destruct (target_value l); reflexivity.
    + discriminate Hroot.
Qed.

Theorem negative_claim_sound :
  forall t,
    node_consistent t ->
    false_leaf_sound t ->
    candidate_root t = false ->
    target_value t = false.
Proof.
  induction t as [target c|c l IHl r IHr].
  - simpl. intros _ Hleaf Hc. now apply Hleaf.
  - simpl.
    intros [Hc [Hnl Hnr]] [Hfl Hfr] Hroot.
    rewrite Hc in Hroot.
    destruct (candidate_root l) eqn:Hl;
    destruct (candidate_root r) eqn:Hr; simpl in Hroot.
    + discriminate Hroot.
    + discriminate Hroot.
    + discriminate Hroot.
    + specialize (IHl Hnl Hfl Hl).
      specialize (IHr Hnr Hfr Hr).
      now rewrite IHl, IHr.
Qed.

Print Assumptions positive_claim_sound.
Print Assumptions negative_claim_sound.

End SATOneSidedAudit.
