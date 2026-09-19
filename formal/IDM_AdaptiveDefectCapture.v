(* ===================================================================== *)
(* IDM_AdaptiveDefectCapture.v                                            *)
(* Exact finite mass kernel for candidate-adaptive defect capture.          *)
(*                                                                       *)
(* A finite weighted witness family represents an adaptive distribution    *)
(* after denominators are cleared.  [hit_mass] is weight on locally        *)
(* checkable defects; [miss_mass] is weight on non-defects.                 *)
(*                                                                       *)
(*   miss_mass < total_mass                                                *)
(*                ==> some positive-weight local defect exists.            *)
(*                                                                       *)
(* This is the exact finite q<1 gate, with q = miss/total.  Quantitative    *)
(* sampling/runtime claims require a separately constructed efficiently    *)
(* samplable distribution and a lower bound on 1-q.                        *)
(* No circuit lower bound or P <> NP claim is made here.                    *)
(* ===================================================================== *)

From Coq Require Import Lists.List Bool.Bool Arith.Arith Lia.
Import ListNotations.

Module AdaptiveDefectCapture.

Section Mass.

  Variable W : Type.
  Variable defect : W -> bool.
  Variable weight : W -> nat.

  Fixpoint total_mass (xs : list W) : nat :=
    match xs with
    | [] => 0
    | x :: t => weight x + total_mass t
    end.

  Fixpoint hit_mass (xs : list W) : nat :=
    match xs with
    | [] => 0
    | x :: t =>
        (if defect x then weight x else 0) + hit_mass t
    end.

  Fixpoint miss_mass (xs : list W) : nat :=
    match xs with
    | [] => 0
    | x :: t =>
        (if defect x then 0 else weight x) + miss_mass t
    end.

  Lemma total_mass_split :
    forall xs,
      total_mass xs = hit_mass xs + miss_mass xs.
  Proof.
    induction xs as [|x t IH].
    - reflexivity.
    - simpl.
      destruct (defect x); simpl; lia.
  Qed.

  Lemma hit_mass_positive_has_witness :
    forall xs,
      0 < hit_mass xs ->
      exists w,
        In w xs /\
        defect w = true /\
        0 < weight w.
  Proof.
    induction xs as [|x t IH]; intros Hpos.
    - simpl in Hpos. lia.
    - simpl in Hpos.
      destruct (defect x) eqn:Hd.
      + destruct (Nat.eq_dec (weight x) 0) as [Hz|Hnz].
        * rewrite Hz in Hpos. simpl in Hpos.
          apply IH in Hpos.
          destruct Hpos as [w [Hin [Hdef Hw]]].
          exists w. repeat split; try assumption.
          right. exact Hin.
        * exists x. repeat split.
          -- left. reflexivity.
          -- exact Hd.
          -- lia.
      + apply IH in Hpos.
        destruct Hpos as [w [Hin [Hdef Hw]]].
        exists w. repeat split; try assumption.
        right. exact Hin.
  Qed.

  (* Exact finite q<1 gate after clearing denominators:
       q = miss_mass / total_mass < 1
     is represented without division by miss_mass < total_mass. *)
  Theorem miss_lt_total_yields_defect :
    forall xs,
      miss_mass xs < total_mass xs ->
      exists w,
        In w xs /\
        defect w = true /\
        0 < weight w.
  Proof.
    intros xs Hlt.
    apply hit_mass_positive_has_witness.
    pose proof (total_mass_split xs) as Hsplit.
    lia.
  Qed.

  (* A cleared-denominator inverse-polynomial capture certificate.
     [total <= p * hit] is exactly hit/total >= 1/p when total>0.  It in
     particular guarantees a positive-weight defect. *)
  Theorem bounded_capture_yields_defect :
    forall xs p,
      0 < total_mass xs ->
      total_mass xs <= p * hit_mass xs ->
      exists w,
        In w xs /\
        defect w = true /\
        0 < weight w.
  Proof.
    intros xs p Htotal Hbound.
    apply hit_mass_positive_has_witness.
    destruct (hit_mass xs) eqn:Hhit.
    - simpl in Hbound. lia.
    - lia.
  Qed.

End Mass.

Print Assumptions total_mass_split.
Print Assumptions hit_mass_positive_has_witness.
Print Assumptions miss_lt_total_yields_defect.
Print Assumptions bounded_capture_yields_defect.

End AdaptiveDefectCapture.
