(* ===================================================================== *)
(* IDM_FiniteObstructionNegativeControls.v                               *)
(* Adversarial finite controls for the shared finite-bridge programme.   *)
(*                                                                       *)
(* These theorems show why several hypotheses in the P1 safe core cannot *)
(* simply be omitted. They do not prove or disprove a Clay statement.    *)
(* ===================================================================== *)

From Coq Require Import Arith.Arith Lists.List Bool.Bool Lia.
Require Import IDM_FiniteObstructionSafeCore.
Import ListNotations.

(* --------------------------------------------------------------------- *)
(* 1. A global failure need not be visible in any finite prefix.          *)
(* --------------------------------------------------------------------- *)

Definition rising (n : nat) : nat := n.

Definition prefix_bounded (N : nat) : Prop :=
  exists B, forall n, n <= N -> rising n <= B.

Definition globally_bounded : Prop :=
  exists B, forall n, rising n <= B.

Theorem every_finite_prefix_bounded :
  forall N, prefix_bounded N.
Proof.
  intro N.
  exists N.
  intros n Hn.
  unfold rising.
  exact Hn.
Qed.

Theorem rising_not_globally_bounded :
  ~ globally_bounded.
Proof.
  intros [B HB].
  specialize (HB (S B)).
  unfold rising in HB.
  lia.
Qed.

Theorem finite_prefixes_do_not_force_global_boundedness :
  (forall N, prefix_bounded N) /\ ~ globally_bounded.
Proof.
  split.
  - exact every_finite_prefix_bounded.
  - exact rising_not_globally_bounded.
Qed.

(* --------------------------------------------------------------------- *)
(* 2. Local compatibility budgets can accumulate without a uniform tail. *)
(* --------------------------------------------------------------------- *)

Theorem unit_step_chain_sum :
  forall n, budget_sum (repeat 1 n) = n.
Proof.
  induction n as [|n IH].
  - reflexivity.
  - simpl. rewrite IH. lia.
Qed.

Theorem local_step_bounds_do_not_give_uniform_chain_bound :
  forall B, exists n, B < budget_sum (repeat 1 n).
Proof.
  intro B.
  exists (S B).
  rewrite unit_step_chain_sum.
  lia.
Qed.

(* --------------------------------------------------------------------- *)
(* 3. PASS transport can fail if verifier invariance is absent.           *)
(* --------------------------------------------------------------------- *)

Definition bool_flip (b : bool) : bool := negb b.
Definition accept_false (b : bool) : bool := negb b.

Theorem transport_can_fail_without_invariance :
  accept_false false = true /\
  accept_false (bool_flip false) = false.
Proof.
  split; reflexivity.
Qed.

(* --------------------------------------------------------------------- *)
(* 4. A checker may accept a non-defect if soundness is absent.           *)
(* --------------------------------------------------------------------- *)

Definition never_defect (_ : unit) : Prop := False.
Definition always_accept (_ : unit) (_ : unit) : bool := true.

Theorem checker_can_accept_without_soundness :
  exists x w,
    always_accept x w = true /\
    ~ never_defect x.
Proof.
  exists tt, tt.
  split.
  - reflexivity.
  - unfold never_defect. intro H. exact H.
Qed.
