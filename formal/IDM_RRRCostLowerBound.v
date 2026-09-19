(* ===================================================================== *)
(* IDM_RRRCostLowerBound.v                                                *)
(* Resource-aware Retain--Recompute--Resolve lower-bound arithmetic.      *)
(*                                                                        *)
(* This isolates the exact finite implication needed by the P-vs-NP lane: *)
(* if semantic demand must be covered by R/R/R resources and one circuit  *)
(* gate can contribute only bounded capacity to those resources, demand   *)
(* forces a gate lower bound.                                             *)
(*                                                                        *)
(* HONEST FENCE: this file does NOT prove that SAT has superpolynomial     *)
(* semantic demand or that a Boolean gate has any particular capacity.    *)
(* Those are the load-bearing open semantic premises.                     *)
(* ===================================================================== *)

Require Import Arith.
Require Import Lia.

Module RRRCostLowerBound.

(* Aggregate capacity form. *)
Theorem demand_bounded_by_gate_capacity :
  forall demand retain_cost recompute_cost resolve_cost
         cap_retain cap_recompute cap_resolve gates : nat,
    demand <= retain_cost + recompute_cost + resolve_cost ->
    retain_cost <= gates * cap_retain ->
    recompute_cost <= gates * cap_recompute ->
    resolve_cost <= gates * cap_resolve ->
    demand <= gates * (cap_retain + cap_recompute + cap_resolve).
Proof.
  intros demand retain_cost recompute_cost resolve_cost
         cap_retain cap_recompute cap_resolve gates
         Hcover HR HQ HC.
  nia.
Qed.

(* Strict lower-bound form: a target demand larger than B times total per-gate
   capacity excludes every B-gate implementation satisfying the premises. *)
Theorem demand_gap_excludes_gate_budget :
  forall demand retain_cost recompute_cost resolve_cost
         cap_retain cap_recompute cap_resolve gates B : nat,
    demand <= retain_cost + recompute_cost + resolve_cost ->
    retain_cost <= gates * cap_retain ->
    recompute_cost <= gates * cap_recompute ->
    resolve_cost <= gates * cap_resolve ->
    gates <= B ->
    B * (cap_retain + cap_recompute + cap_resolve) < demand ->
    False.
Proof.
  intros demand retain_cost recompute_cost resolve_cost
         cap_retain cap_recompute cap_resolve gates B
         Hcover HR HQ HC Hg Hgap.
  pose proof
    (demand_bounded_by_gate_capacity
      demand retain_cost recompute_cost resolve_cost
      cap_retain cap_recompute cap_resolve gates
      Hcover HR HQ HC) as Hbound.
  nia.
Qed.

(* Rearranged certificate: any correct realization must have enough gates to
   cover demand. This avoids integer division and is the form used by exact
   certificate checkers. *)
Theorem certified_gate_lower_bound :
  forall demand capacity gates : nat,
    demand <= gates * capacity ->
    forall lower : nat,
      gates < lower ->
      (lower - 1) * capacity < demand ->
      False.
Proof.
  intros demand capacity gates Hcover lower Hsmall Hgap.
  destruct lower as [|k].
  - lia.
  - simpl in Hgap. nia.
Qed.

(* If an asymptotic target family supplies a demand D(n) and capacity K(n),
   all later class-separation work reduces to proving D(n) outgrows every
   polynomial gate budget times K(n). This theorem deliberately does not
   encode asymptotics; it is the finite kernel each n must instantiate. *)

Print Assumptions demand_bounded_by_gate_capacity.
Print Assumptions demand_gap_excludes_gate_budget.
Print Assumptions certified_gate_lower_bound.

End RRRCostLowerBound.
