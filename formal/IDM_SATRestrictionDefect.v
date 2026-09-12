(* ===================================================================== *)
(* IDM_SATRestrictionDefect.v                                             *)
(* Quantitative local-to-global kernels for Boolean restriction trees.     *)
(*                                                                       *)
(* Full tree: root disagreement is bounded by all local OR defects plus    *)
(* exact leaf errors.                                                      *)
(* Partial tree: exact leaf errors may be replaced by separately certified *)
(* frontier budgets.  Unknown frontier error must not be silently set to 0. *)
(*                                                                       *)
(* These are finite Boolean analogues of propagating certified local        *)
(* discrepancy through a declared reader.  They do NOT prove a circuit     *)
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
  destruct a, b, c; cbv [bdist]; repeat constructor.
Qed.

Lemma orb_lipschitz_l1 :
  forall a b c d,
    bdist (orb a b) (orb c d) <= bdist a c + bdist b d.
Proof.
  intros a b c d.
  destruct a, b, c, d; cbv [bdist]; repeat constructor.
Qed.

(* Coq-version-robust zero-distance elimination. *)
Lemma bdist_zero_eq :
  forall a b,
    bdist a b = 0 -> a = b.
Proof.
  intros a b H.
  destruct a, b; cbv [bdist] in H; try reflexivity; discriminate.
Qed.

(* --------------------------------------------------------------------- *)
(* Full restriction tree.                                                *)
(* --------------------------------------------------------------------- *)

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
  apply bdist_zero_eq.
  lia.
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

(* --------------------------------------------------------------------- *)
(* Partial restriction tree with frontier error budgets.                  *)
(* --------------------------------------------------------------------- *)

Inductive PTree : Type :=
| PLeaf : bool -> bool -> nat -> PTree
(* [PLeaf target candidate certified_budget] *)
| PNode : bool -> PTree -> PTree -> PTree.
(* [PNode candidate left right] *)

Fixpoint pcandidate_root (t : PTree) : bool :=
  match t with
  | PLeaf _ c _ => c
  | PNode c _ _ => c
  end.

Fixpoint ptarget_value (t : PTree) : bool :=
  match t with
  | PLeaf target _ _ => target
  | PNode _ l r => orb (ptarget_value l) (ptarget_value r)
  end.

Fixpoint frontier_budget_sum (t : PTree) : nat :=
  match t with
  | PLeaf _ _ budget => budget
  | PNode c l r =>
      bdist c (orb (pcandidate_root l) (pcandidate_root r))
      + frontier_budget_sum l + frontier_budget_sum r
  end.

Fixpoint frontier_budgets_valid (t : PTree) : Prop :=
  match t with
  | PLeaf target c budget => bdist c target <= budget
  | PNode _ l r => frontier_budgets_valid l /\ frontier_budgets_valid r
  end.

Theorem partial_root_error_bounded_by_frontier :
  forall t,
    frontier_budgets_valid t ->
    bdist (pcandidate_root t) (ptarget_value t)
      <= frontier_budget_sum t.
Proof.
  induction t as [target c budget|c l IHl r IHr].
  - simpl. intros H. exact H.
  - simpl. intros [Hl Hr].
    specialize (IHl Hl).
    specialize (IHr Hr).
    pose proof (bdist_triangle
      c
      (orb (pcandidate_root l) (pcandidate_root r))
      (orb (ptarget_value l) (ptarget_value r))) as Htri.
    pose proof (orb_lipschitz_l1
      (pcandidate_root l) (pcandidate_root r)
      (ptarget_value l) (ptarget_value r)) as Hor.
    lia.
Qed.

Theorem zero_partial_budget_implies_exact_root :
  forall t,
    frontier_budgets_valid t ->
    frontier_budget_sum t = 0 ->
    pcandidate_root t = ptarget_value t.
Proof.
  intros t Hvalid Hz.
  pose proof (partial_root_error_bounded_by_frontier t Hvalid) as H.
  rewrite Hz in H.
  apply bdist_zero_eq.
  lia.
Qed.

Print Assumptions bdist_triangle.
Print Assumptions orb_lipschitz_l1.
Print Assumptions root_error_bounded_by_defects.
Print Assumptions zero_defect_implies_exact_root.
Print Assumptions wrong_root_forces_positive_defect.
Print Assumptions partial_root_error_bounded_by_frontier.
Print Assumptions zero_partial_budget_implies_exact_root.

End SATRestrictionDefect.
