(* ===================================================================== *)
(* IDM_BackdoorSupportBudget.v                                            *)
(* Exact finite node budget for a declared binary backdoor tree.           *)
(*                                                                       *)
(* A backdoor of k binary variables has at most                           *)
(*   1 + 2 + ... + 2^k = 2^(k+1)-1                                      *)
(* visited states when fully expanded.  This file proves the recurrence     *)
(* in the subtraction-free form                                           *)
(*   S(tree_nodes k) = 2^(S k).                                           *)
(*                                                                       *)
(* Combined with an independently certified tractable frontier and the     *)
(* SAT restriction-defect kernel, this gives a parameterized support       *)
(* budget.  It does NOT prove that arbitrary SAT instances or circuits      *)
(* admit logarithmic backdoors.                                            *)
(* ===================================================================== *)

From Coq Require Import Arith.Arith Lia.

Module BackdoorSupportBudget.

Fixpoint tree_nodes (k : nat) : nat :=
  match k with
  | 0 => 1
  | S t => 1 + 2 * tree_nodes t
  end.

Theorem tree_nodes_plus_one_power :
  forall k,
    S (tree_nodes k) = 2 ^ (S k).
Proof.
  induction k as [|k IH].
  - reflexivity.
  - simpl.
    simpl in IH.
    lia.
Qed.

Theorem one_backdoor_three_nodes : tree_nodes 1 = 3.
Proof. reflexivity. Qed.

Theorem two_backdoor_seven_nodes : tree_nodes 2 = 7.
Proof. reflexivity. Qed.

Theorem three_backdoor_fifteen_nodes : tree_nodes 3 = 15.
Proof. reflexivity. Qed.

Print Assumptions tree_nodes_plus_one_power.
Print Assumptions one_backdoor_three_nodes.
Print Assumptions two_backdoor_seven_nodes.
Print Assumptions three_backdoor_fifteen_nodes.

End BackdoorSupportBudget.
