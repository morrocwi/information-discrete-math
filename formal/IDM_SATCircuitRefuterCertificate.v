(* ===================================================================== *)
(* IDM_SATCircuitRefuterCertificate.v                                     *)
(* Two-sided finite refuter-certificate kernel for SAT-style recursion.    *)
(*                                                                       *)
(* A candidate can be refuted in either direction. On a complete finite    *)
(* restriction tree, any root disagreement with the target forces either   *)
(* a local OR-recursion defect or a terminal boundary defect somewhere.    *)
(*                                                                       *)
(* Concrete SAT instantiation supplies restriction syntax and direct leaf  *)
(* truth. This proves certificate semantics only. It does NOT construct a   *)
(* refuter for every small circuit or prove a circuit lower bound.          *)
(* ===================================================================== *)

From Coq Require Import Bool.Bool.

Module SATCircuitRefuterCertificate.

Inductive RTree : Type :=
| RLeaf : bool -> bool -> RTree
(* [RLeaf target candidate] *)
| RNode : bool -> RTree -> RTree -> RTree.
(* [RNode candidate left right] *)

Fixpoint candidate_root (t : RTree) : bool :=
  match t with
  | RLeaf _ c => c
  | RNode c _ _ => c
  end.

Fixpoint target_value (t : RTree) : bool :=
  match t with
  | RLeaf target _ => target
  | RNode _ l r => orb (target_value l) (target_value r)
  end.

Inductive defect_witness : RTree -> Prop :=
| DWLeaf :
    forall target c,
      c <> target ->
      defect_witness (RLeaf target c)
| DWLocal :
    forall c l r,
      c <> orb (candidate_root l) (candidate_root r) ->
      defect_witness (RNode c l r)
| DWLeft :
    forall c l r,
      defect_witness l ->
      defect_witness (RNode c l r)
| DWRight :
    forall c l r,
      defect_witness r ->
      defect_witness (RNode c l r).

Fixpoint has_defect (t : RTree) : bool :=
  match t with
  | RLeaf target c => negb (Bool.eqb c target)
  | RNode c l r =>
      orb
        (negb (Bool.eqb c (orb (candidate_root l) (candidate_root r))))
        (orb (has_defect l) (has_defect r))
  end.

Lemma has_defect_true_yields_witness :
  forall t,
    has_defect t = true ->
    defect_witness t.
Proof.
  induction t as [target c|c l IHl r IHr].
  - simpl. intros H.
    apply Bool.negb_true_iff in H.
    apply Bool.eqb_false_iff in H.
    now apply DWLeaf.
  - simpl. intros H.
    apply Bool.orb_true_iff in H as [Hlocal|Hchildren].
    + apply Bool.negb_true_iff in Hlocal.
      apply Bool.eqb_false_iff in Hlocal.
      now apply DWLocal.
    + apply Bool.orb_true_iff in Hchildren as [Hl|Hr].
      * apply DWLeft. now apply IHl.
      * apply DWRight. now apply IHr.
Qed.

Lemma no_defect_implies_exact_root :
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

Theorem wrong_root_has_defect :
  forall t,
    candidate_root t <> target_value t ->
    defect_witness t.
Proof.
  intros t Hwrong.
  apply has_defect_true_yields_witness.
  destruct (has_defect t) eqn:Hdef.
  - reflexivity.
  - exfalso.
    apply Hwrong.
    now apply no_defect_implies_exact_root.
Qed.

(* Boolean direction split: every root disagreement is exactly one of the
   false-negative or false-positive cases. *)
Theorem wrong_root_direction :
  forall t,
    candidate_root t <> target_value t ->
    (candidate_root t = false /\ target_value t = true) \/
    (candidate_root t = true /\ target_value t = false).
Proof.
  intros t H.
  destruct (candidate_root t) eqn:Hc;
  destruct (target_value t) eqn:Ht; try contradiction.
  - right. split; reflexivity.
  - left. split; reflexivity.
Qed.

Print Assumptions has_defect_true_yields_witness.
Print Assumptions no_defect_implies_exact_root.
Print Assumptions wrong_root_has_defect.
Print Assumptions wrong_root_direction.

End SATCircuitRefuterCertificate.
