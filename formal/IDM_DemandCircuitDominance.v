(* ===================================================================== *)
(* IDM_DemandCircuitDominance.v                                           *)
(* Route-closure kernel for semantic demand / gate-capacity arguments.    *)
(*                                                                        *)
(* HONEST FENCE: this file does NOT prove a SAT circuit lower bound or     *)
(* P <> NP. It proves a meta-fact about the proposed accounting schema:    *)
(* once universal accounting gives demand <= circuit_size * capacity, any  *)
(* demand/capacity gap beyond a gate budget is already a circuit-size      *)
(* lower-bound certificate. The hard step therefore remains the universal *)
(* SAT-specific demand/capacity theorem itself.                            *)
(* ===================================================================== *)

Require Import Arith.
Require Import Lia.

Module DemandCircuitDominance.

(* If H is universally chargeable to a correct circuit at K units per gate,
   then any certified H > B*K immediately excludes circuit size <= B. *)
Theorem demand_gap_is_circuit_lower_bound :
  forall H K circuit_size B : nat,
    H <= circuit_size * K ->
    B * K < H ->
    B < circuit_size.
Proof.
  intros H K circuit_size B Haccount Hgap.
  nia.
Qed.

(* Equivalent contradiction form, useful when the candidate circuit already
   comes with a declared gate budget. No asymptotics are hidden here. *)
Theorem universal_accounting_excludes_budget :
  forall H K circuit_size B : nat,
    H <= circuit_size * K ->
    circuit_size <= B ->
    B * K < H ->
    False.
Proof.
  intros H K circuit_size B Haccount Hsize Hgap.
  nia.
Qed.

(* Positive capacity makes the normalization H/K conceptually legitimate,
   but the finite proof should stay multiplication-only to avoid rounding.
   This lemma records the exact integer consequence: a nonzero demand gap
   requires at least one more gate than B. *)
Theorem positive_capacity_strict_gate_step :
  forall H K circuit_size B : nat,
    0 < K ->
    H <= circuit_size * K ->
    B * K < H ->
    S B <= circuit_size.
Proof.
  intros H K circuit_size B HK Haccount Hgap.
  nia.
Qed.

Print Assumptions demand_gap_is_circuit_lower_bound.
Print Assumptions universal_accounting_excludes_budget.
Print Assumptions positive_capacity_strict_gate_step.

End DemandCircuitDominance.
