(* ===================================================================== *)
(* IDM_FiniteObstructionSafeCore.v                                       *)
(* Safe finite logic for the shared Clay finite-obstruction programme.   *)
(*                                                                       *)
(* Scope:                                                               *)
(* - strict certified margin / fail-closed HOLD                          *)
(* - finite error-budget monotonicity and composition                    *)
(* - finite-chain compatibility-budget composition                       *)
(* - certificate transport under declared symmetry invariance            *)
(* - local finite-defect checker soundness                               *)
(*                                                                       *)
(* Deliberately NOT proved here:                                         *)
(* - global failure -> finite witness                                    *)
(* - unrestricted constructive witness capture                           *)
(* - Navier--Stokes singularity bridge                                   *)
(* - SAT circuit lower bounds or P != NP                                 *)
(*                                                                       *)
(* Theorems in this file are generic finite kernels only. Domain          *)
(* adapters and separate load-bearing bridge theorems remain necessary.   *)
(* ===================================================================== *)

From Coq Require Import Arith.Arith Lists.List Bool.Bool Lia.
Import ListNotations.

(* --------------------------------------------------------------------- *)
(* 1. Fail-closed strict-margin gate.                                    *)
(* --------------------------------------------------------------------- *)

Inductive CertVerdict : Type :=
| PASS
| HOLD.

Definition strict_margin_verdict (margin error : nat) : CertVerdict :=
  if Nat.ltb error margin then PASS else HOLD.

Theorem strict_margin_pass_sound :
  forall margin error,
    strict_margin_verdict margin error = PASS ->
    error < margin.
Proof.
  intros margin error H.
  unfold strict_margin_verdict in H.
  destruct (Nat.ltb error margin) eqn:Hlt.
  - apply Nat.ltb_lt. exact Hlt.
  - discriminate H.
Qed.

Theorem strict_margin_pass_complete :
  forall margin error,
    error < margin ->
    strict_margin_verdict margin error = PASS.
Proof.
  intros margin error Hlt.
  unfold strict_margin_verdict.
  apply Nat.ltb_lt in Hlt.
  rewrite Hlt. reflexivity.
Qed.

Theorem strict_margin_hold_when_not_strict :
  forall margin error,
    margin <= error ->
    strict_margin_verdict margin error = HOLD.
Proof.
  intros margin error Hge.
  unfold strict_margin_verdict.
  destruct (Nat.ltb error margin) eqn:Hlt.
  - apply Nat.ltb_lt in Hlt. lia.
  - reflexivity.
Qed.

Definition gated_margin_verdict
  (certificate_present : bool) (margin error : nat) : CertVerdict :=
  match certificate_present with
  | true => strict_margin_verdict margin error
  | false => HOLD
  end.

Theorem missing_certificate_holds :
  forall margin error,
    gated_margin_verdict false margin error = HOLD.
Proof.
  intros margin error. reflexivity.
Qed.

Theorem gated_pass_requires_certificate_and_margin :
  forall certificate_present margin error,
    gated_margin_verdict certificate_present margin error = PASS ->
    certificate_present = true /\ error < margin.
Proof.
  intros certificate_present margin error H.
  destruct certificate_present eqn:Hpresent.
  - split.
    + reflexivity.
    + simpl in H. apply strict_margin_pass_sound. exact H.
  - simpl in H. discriminate H.
Qed.

(* --------------------------------------------------------------------- *)
(* 2. Finite error-budget monotonicity and additive composition.          *)
(* --------------------------------------------------------------------- *)

Theorem error_budget_monotone :
  forall error small_budget large_budget,
    error <= small_budget ->
    small_budget <= large_budget ->
    error <= large_budget.
Proof.
  intros. lia.
Qed.

Theorem error_budget_additive :
  forall e1 e2 b1 b2,
    e1 <= b1 ->
    e2 <= b2 ->
    e1 + e2 <= b1 + b2.
Proof.
  intros. lia.
Qed.

Fixpoint budget_sum (xs : list nat) : nat :=
  match xs with
  | [] => 0
  | x :: rest => x + budget_sum rest
  end.

Theorem finite_chain_budget_composition :
  forall (actual certified : list nat),
    Forall2 le actual certified ->
    budget_sum actual <= budget_sum certified.
Proof.
  intros actual certified H.
  induction H.
  - simpl. lia.
  - simpl. lia.
Qed.

(* A three-resolution specialization: if the direct n->k discrepancy is no
   larger than the sum of the n->m and m->k discrepancies, certified bounds
   on the two legs compose into a certified n->k bound. *)
Theorem compatibility_two_step :
  forall d_nm d_mk d_nk eta_nm eta_mk,
    d_nm <= eta_nm ->
    d_mk <= eta_mk ->
    d_nk <= d_nm + d_mk ->
    d_nk <= eta_nm + eta_mk.
Proof.
  intros. lia.
Qed.

(* --------------------------------------------------------------------- *)
(* 3. Symmetry-respecting certificate transport.                         *)
(* --------------------------------------------------------------------- *)

Section SymmetryTransport.
  Variables G X Cert : Type.
  Variable act : G -> X -> X.
  Variable verify : X -> Cert -> bool.

  Hypothesis verify_invariant :
    forall g x c, verify (act g x) c = verify x c.

  Theorem symmetry_transport_pass :
    forall g x c,
      verify x c = true ->
      verify (act g x) c = true.
  Proof.
    intros g x c Hpass.
    rewrite (verify_invariant g x c).
    exact Hpass.
  Qed.
End SymmetryTransport.

(* --------------------------------------------------------------------- *)
(* 4. Local finite-defect checker soundness.                              *)
(* --------------------------------------------------------------------- *)

Section LocalDefectChecker.
  Variables Obj Witness : Type.
  Variable defect : Obj -> Prop.
  Variable verify_defect : Obj -> Witness -> bool.

  Hypothesis verifier_sound :
    forall x w, verify_defect x w = true -> defect x.

  Theorem verified_local_defect_sound :
    forall x w,
      verify_defect x w = true -> defect x.
  Proof.
    exact verifier_sound.
  Qed.
End LocalDefectChecker.
