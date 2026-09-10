(* ===================================================================== *)
(* IDM_SATRestrictionDefect.v                                             *)
(* Quantitative local-to-global kernel for Boolean restriction trees.      *)
(*                                                                       *)
(* A candidate label at an internal node should equal OR of its two child  *)
(* labels; a leaf candidate should equal the declared terminal truth.      *)
(* The root disagreement is bounded by the sum of all local defects.       *)
(*                                                                       *)
(* This is the finite Boolean analogue of propagating certified local      *)
(* discrepancy through a declared reader.  It does NOT prove a circuit     *)
(* lower bound or P <> NP.                                                 *)
(* ===================================================================== *)

From Coq Require Import Bool.Bool Arith.Arith Lia.

Module SATRestrictionDefect.

Definition bdist (a b : bool) : nat :=
  if Bool.eqb a b then 0 else 1.

Lemma bdist_triangle :
  forall a b c,
    bdist a c <= bdist a b + bdist b c.
Proof.
  intros a b c.
  destruct a, b, c; simpl; lia.
Qed.

Lemma orb_lipschitz_l1 :
  forall a b c d,
    bdist (orb a b) (orb c d) <= bdist a c + bdist b d.
Proof.
  intros a b c d.
  destruct a, b, c, d; simpl; lia.
Qed.

Inductive LTree : Type :=
| LLeaf : bool -> bool -> LTree
(* [LLeaf target candidate] *)
| LNode : bool -> LTree -> LTree -> LTree.
(* [LNode candidate left right] *)

Fixpoint candidate_root (t : LTree) : bool :=
  match t with
  | LLeaf _ c => c
  | LNode c _ _ => c
  end.

Fixpoint target_value (t : LTree) : bool :=
  match t with
  | LLeaf target _ => target
  | LNode _ l r => orb (target_value l) (target_value r)
  end.

Fixpoint defect_count (t : LTree) : nat :=
  match t with
  | LLeaf target c => bdist c target
  | LNode c l r =>
      bdist c (orb (candidate_root l) (candidate_root r))
      + defect_count l + defect_count r
  end.

Theorem root_error_bounded_by_defects :
  forall t,
    bdist (candidate_root t) (target_value t) <= defect_count t.
Proof.
  induction t as [target c|c l IHl r IHr].
  - simpl. unfold bdist. destruct c, target; reflexivity.
  - simpl.
    pose proof (bdist_triangle
      c
      (orb (candidate_root l) (candidate_root r))
      (orb (target_value l) (target_value r))) as Htri.
    pose proof (orb_lipschitz_l1
      (candidate_root l) (candidate_root r)
      (target_value l) (target_value r)) as Hor.
    lia.
Qed.

Theorem zero_defect_implies_exact_root :
  forall t,
    defect_count t = 0 ->
    candidate_root t = target_value t.
Proof.
  intros t Hz.
  pose proof (root_error_bounded_by_defects t) as H.
  rewrite Hz in H.
  unfold bdist in H.
  destruct (Bool.eqb (candidate_root t) (target_value t)) eqn:Heq.
  - now apply Bool.eqb_true_iff in Heq.
  - simpl in H. lia.
Qed.

Theorem wrong_root_forces_positive_defect :
  forall t,
    candidate_root t <> target_value t ->
    1 <= defect_count t.
Proof.
  intros t Hneq.
  pose proof (root_error_bounded_by_defects t) as H.
  unfold bdist in H.
  destruct (Bool.eqb (candidate_root t) (target_value t)) eqn:Heq.
  - apply Bool.eqb_true_iff in Heq. contradiction.
  - simpl in H. exact H.
Qed.

Print Assumptions bdist_triangle.
Print Assumptions orb_lipschitz_l1.
Print Assumptions root_error_bounded_by_defects.
Print Assumptions zero_defect_implies_exact_root.
Print Assumptions wrong_root_forces_positive_defect.

End SATRestrictionDefect.
