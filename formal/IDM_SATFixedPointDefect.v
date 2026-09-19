(* ===================================================================== *)
(* IDM_SATFixedPointDefect.v                                              *)
(* Finite fixed-point defect kernel for SAT-style restriction trees.       *)
(*                                                                       *)
(* The target obeys OR self-reduction.  A candidate labeling that differs  *)
(* at the root must violate either one local OR recursion equation or one   *)
(* terminal boundary value somewhere in the finite tree.                   *)
(*                                                                       *)
(* This localizes non-equivalence to an independently checkable defect.     *)
(* It does NOT prove that every small circuit has such a defect; that is    *)
(* the remaining lower-bound obligation.                                   *)
(* ===================================================================== *)

From Coq Require Import Bool.Bool.

Module SATFixedPointDefect.

Inductive FTree : Type :=
| FLeaf : bool -> bool -> FTree
(* [FLeaf target candidate] *)
| FNode : bool -> FTree -> FTree -> FTree.
(* [FNode candidate left right] *)

Fixpoint candidate_root (t : FTree) : bool :=
  match t with
  | FLeaf _ c => c
  | FNode c _ _ => c
  end.

Fixpoint target_value (t : FTree) : bool :=
  match t with
  | FLeaf target _ => target
  | FNode _ l r => orb (target_value l) (target_value r)
  end.

Fixpoint has_defect (t : FTree) : bool :=
  match t with
  | FLeaf target c => negb (Bool.eqb c target)
  | FNode c l r =>
      orb
        (negb (Bool.eqb c (orb (candidate_root l) (candidate_root r))))
        (orb (has_defect l) (has_defect r))
  end.

Theorem no_defect_implies_exact_root :
  forall t,
    has_defect t = false ->
    candidate_root t = target_value t.
Proof.
  induction t as [target c|c l IHl r IHr].
  - simpl. intros H.
    apply Bool.negb_false_iff in H.
    now apply Bool.eqb_true_iff in H.
  - simpl. intros H.
    apply Bool.orb_false_iff in H as [Hlocal Hchildren].
    apply Bool.negb_false_iff in Hlocal.
    apply Bool.eqb_true_iff in Hlocal.
    apply Bool.orb_false_iff in Hchildren as [Hl Hr].
    specialize (IHl Hl).
    specialize (IHr Hr).
    rewrite Hlocal, IHl, IHr.
    reflexivity.
Qed.

Theorem wrong_root_forces_defect :
  forall t,
    candidate_root t <> target_value t ->
    has_defect t = true.
Proof.
  intros t Hneq.
  destruct (has_defect t) eqn:Hdef.
  - reflexivity.
  - exfalso.
    apply Hneq.
    now apply no_defect_implies_exact_root.
Qed.

Print Assumptions no_defect_implies_exact_root.
Print Assumptions wrong_root_forces_defect.

End SATFixedPointDefect.
