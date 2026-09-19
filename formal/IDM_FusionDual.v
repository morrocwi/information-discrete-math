(* ===================================================================== *)
(* IDM_FusionDual.v                                                       *)
(* Scaled finite aggregation theorem for Fusion/Horn lower-bound duals.  *)
(*                                                                        *)
(* Scope: finite natural-number ledger only.  A concrete cover verifier   *)
(* must separately establish that each selected fusion pair is charged no *)
(* more than [budget] units and that all adversarial weight is assigned to *)
(* selected pairs.  This file proves the final local-to-global arithmetic. *)
(* It does NOT prove a SAT circuit lower bound.                            *)
(* ===================================================================== *)

Require Import List.
Require Import Lia.
Import ListNotations.

Module FusionDual.

Fixpoint nsum (xs : list nat) : nat :=
  match xs with
  | [] => 0
  | x :: t => x + nsum t
  end.

(* If every selected rule is charged at most [budget] weight units, the
   aggregate charge of k selected rules is at most k*budget. *)
Theorem bounded_loads_sum :
  forall (loads : list nat) (budget : nat),
    Forall (fun z => z <= budget) loads ->
    nsum loads <= length loads * budget.
Proof.
  intros loads budget H.
  induction H as [|x xs Hx Hxs IH].
  - simpl. lia.
  - simpl. nia.
Qed.

(* Scaled dual certificate aggregation.  [total] is the total integer weight
   of all adversarial states.  [loads] contains, for each selected fusion
   pair, the weight assigned to that pair.  A concrete incidence checker is
   responsible for proving total <= nsum loads and each load <= budget. *)
Theorem scaled_dual_cover_bound :
  forall (total budget : nat) (loads : list nat),
    total <= nsum loads ->
    Forall (fun z => z <= budget) loads ->
    total <= length loads * budget.
Proof.
  intros total budget loads Hcover Hloads.
  pose proof (bounded_loads_sum loads budget Hloads) as Hsum.
  lia.
Qed.

(* If k is the number of selected rules, the same certificate reads
   total <= k*budget.  Clearing denominators of a rational dual uses exactly
   this form with [budget] equal to the common denominator. *)
Theorem scaled_dual_k_rules :
  forall (total budget k : nat) (loads : list nat),
    length loads = k ->
    total <= nsum loads ->
    Forall (fun z => z <= budget) loads ->
    total <= k * budget.
Proof.
  intros total budget k loads Hlen Hcover Hloads.
  subst k.
  exact (scaled_dual_cover_bound total budget loads Hcover Hloads).
Qed.

(* Strict corollary convenient for refuting an alleged too-small cover. *)
Theorem dual_gap_refutes_k_cover :
  forall (total budget k : nat),
    k * budget < total ->
    ~ (total <= k * budget).
Proof.
  intros total budget k Hgap Hle.
  lia.
Qed.

Print Assumptions bounded_loads_sum.
Print Assumptions scaled_dual_cover_bound.
Print Assumptions scaled_dual_k_rules.
Print Assumptions dual_gap_refutes_k_cover.

End FusionDual.
