(* ===================================================================== *)
(* IDM_RobustDefectCapture.v                                              *)
(* Robust finite capture margin for approximate candidate-adaptive support. *)
(*                                                                       *)
(* This is the discrete analogue of a certified measurement/inversion      *)
(* margin: an ideal hit mass may be degraded by a separately bounded        *)
(* implementation/sampling error, yet inverse-polynomial capture survives   *)
(* if the ideal margin is large enough to absorb that error.                *)
(*                                                                       *)
(* Cleared-denominator form:                                                *)
(*   ideal_hit <= approx_hit + err                                          *)
(*   total + p*err <= p*ideal_hit                                           *)
(*                      ==> total <= p*approx_hit.                           *)
(*                                                                       *)
(* Hence approx_hit/total >= 1/p whenever total>0.                          *)
(* This file proves only the arithmetic transfer.  Constructing an          *)
(* efficiently samplable support/distribution for unrestricted SAT circuits *)
(* with such a margin remains OPEN.                                         *)
(* ===================================================================== *)

From Coq Require Import Arith.Arith Lia.

Module RobustDefectCapture.

Theorem robust_capture_bound :
  forall total ideal_hit approx_hit err p,
    ideal_hit <= approx_hit + err ->
    total + p * err <= p * ideal_hit ->
    total <= p * approx_hit.
Proof.
  intros total ideal_hit approx_hit err p Hideal Hmargin.
  nia.
Qed.

Theorem robust_capture_positive :
  forall total ideal_hit approx_hit err p,
    0 < total ->
    ideal_hit <= approx_hit + err ->
    total + p * err <= p * ideal_hit ->
    0 < approx_hit.
Proof.
  intros total ideal_hit approx_hit err p Htotal Hideal Hmargin.
  pose proof (robust_capture_bound total ideal_hit approx_hit err p Hideal Hmargin) as Hcap.
  destruct approx_hit.
  - simpl in Hcap. lia.
  - lia.
Qed.

(* Zero-error specialization. *)
Theorem exact_capture_bound :
  forall total hit p,
    total <= p * hit ->
    total <= p * hit.
Proof. auto. Qed.

Print Assumptions robust_capture_bound.
Print Assumptions robust_capture_positive.
Print Assumptions exact_capture_bound.

End RobustDefectCapture.
