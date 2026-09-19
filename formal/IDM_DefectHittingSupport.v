(* ===================================================================== *)
(* IDM_DefectHittingSupport.v                                             *)
(* Polynomial hitting support -> inverse-polynomial defect capture.        *)
(*                                                                       *)
(* This is a finite reduction kernel.  If an efficiently constructed       *)
(* support S_C contains at least one locally verifiable defect whenever     *)
(* candidate C is wrong, and |S_C| <= p, then uniform sampling from S_C     *)
(* has defect mass at least 1/p.                                           *)
(*                                                                       *)
(* The theorem DOES NOT construct such a support for SAT circuits.          *)
(* That constructor is the load-bearing open problem.                      *)
(* ===================================================================== *)

From Coq Require Import Lists.List Bool.Bool Arith.Arith Lia.
Import ListNotations.

Module DefectHittingSupport.

Section HittingSupport.

  Variables Candidate Cert : Type.
  Variable wrong : Candidate -> Prop.
  Variable verify : Candidate -> Cert -> bool.
  Variable support : Candidate -> list Cert.

  Fixpoint hit_count (c : Candidate) (xs : list Cert) : nat :=
    match xs with
    | [] => 0
    | z :: t => (if verify c z then 1 else 0) + hit_count c t
    end.

  Lemma verified_member_gives_positive_hit :
    forall c xs z,
      In z xs ->
      verify c z = true ->
      1 <= hit_count c xs.
  Proof.
    intros c xs.
    induction xs as [|a t IH]; intros z Hin Hv.
    - contradiction.
    - simpl in Hin. destruct Hin as [Heq | Hin].
      + subst a. simpl. rewrite Hv. lia.
      + simpl. destruct (verify c a); simpl.
        * lia.
        * specialize (IH z Hin Hv). lia.
  Qed.

  Hypothesis support_hits_wrong :
    forall c,
      wrong c ->
      exists z,
        In z (support c) /\ verify c z = true.

  Theorem wrong_candidate_has_positive_hit :
    forall c,
      wrong c ->
      1 <= hit_count c (support c).
  Proof.
    intros c Hwrong.
    destruct (support_hits_wrong c Hwrong) as [z [Hin Hv]].
    now apply (verified_member_gives_positive_hit c (support c) z Hin Hv).
  Qed.

  (* Cleared-denominator form of
         hit_count / |support| >= 1/p
     under |support| <= p and at least one hit. *)
  Theorem polynomial_support_gives_capture_bound :
    forall c p,
      wrong c ->
      length (support c) <= p ->
      length (support c) <= p * hit_count c (support c).
  Proof.
    intros c p Hwrong Hlen.
    pose proof (wrong_candidate_has_positive_hit c Hwrong) as Hhit.
    eapply Nat.le_trans.
    - exact Hlen.
    - replace p with (p * 1) at 1 by lia.
      apply Nat.mul_le_mono_l.
      exact Hhit.
  Qed.

  Theorem polynomial_support_is_nonempty_on_wrong :
    forall c p,
      wrong c ->
      length (support c) <= p ->
      0 < length (support c).
  Proof.
    intros c p Hwrong _.
    destruct (support_hits_wrong c Hwrong) as [z [Hin _]].
    destruct (support c) as [|a t] eqn:Hs.
    - simpl in Hin. contradiction.
    - simpl. lia.
  Qed.

End HittingSupport.

Print Assumptions verified_member_gives_positive_hit.
Print Assumptions wrong_candidate_has_positive_hit.
Print Assumptions polynomial_support_gives_capture_bound.
Print Assumptions polynomial_support_is_nonempty_on_wrong.

End DefectHittingSupport.
