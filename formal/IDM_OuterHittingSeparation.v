(* ===================================================================== *)
(* IDM_OuterHittingSeparation.v                                           *)
(* Final logical transfer for candidate-adaptive outer hitting supports.   *)
(*                                                                       *)
(* If exact candidates never admit a verified defect, while every          *)
(* below-threshold candidate is hit by a finite support containing some    *)
(* verified defect, then no below-threshold candidate is exact.             *)
(*                                                                       *)
(* This is a transfer kernel only.  It does NOT construct the support,      *)
(* prove its polynomial size/time, or prove a SAT circuit lower bound.      *)
(* ===================================================================== *)

From Coq Require Import Lists.List Bool.Bool.
Import ListNotations.

Module OuterHittingSeparation.

Section Transfer.

  Variables Candidate Cert : Type.
  Variable exact : Candidate -> Prop.
  Variable below_threshold : Candidate -> Prop.
  Variable verify : Candidate -> Cert -> bool.
  Variable support : Candidate -> list Cert.

  Hypothesis exact_has_no_verified_defect :
    forall c z,
      exact c ->
      verify c z = false.

  Hypothesis support_hits_every_below_threshold_candidate :
    forall c,
      below_threshold c ->
      exists z,
        In z (support c) /\ verify c z = true.

  Theorem below_threshold_not_exact :
    forall c,
      below_threshold c ->
      ~ exact c.
  Proof.
    intros c Hsmall Hexact.
    destruct (support_hits_every_below_threshold_candidate c Hsmall)
      as [z [_ Hverify]].
    pose proof (exact_has_no_verified_defect c z Hexact) as Hfalse.
    rewrite Hverify in Hfalse.
    discriminate.
  Qed.

  Theorem exact_implies_not_below_threshold :
    forall c,
      exact c ->
      ~ below_threshold c.
  Proof.
    intros c Hexact Hsmall.
    exact ((below_threshold_not_exact c Hsmall) Hexact).
  Qed.

End Transfer.

Print Assumptions below_threshold_not_exact.
Print Assumptions exact_implies_not_below_threshold.

End OuterHittingSeparation.
