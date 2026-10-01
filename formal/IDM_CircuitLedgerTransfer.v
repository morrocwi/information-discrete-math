(* ===================================================================== *)
(* IDM_CircuitLedgerTransfer.v                                            *)
(* Exact finite transfer: semantic-ledger lower bounds -> circuit bounds. *)
(*                                                                        *)
(* Scope: abstract finite arithmetic. This does NOT prove a SAT lower      *)
(* bound. It closes the bookkeeping bridge: if every correct semantic      *)
(* ledger for a target exceeds B and every correct circuit compiles to a   *)
(* correct ledger with no size expansion, every correct circuit exceeds B. *)
(* ===================================================================== *)

Require Import Arith.
Require Import Lia.

Module CircuitLedgerTransfer.

Section Transfer.

  Variables Circuit Ledger : Type.
  Variable circuit_size : Circuit -> nat.
  Variable ledger_size : Ledger -> nat.
  Variable compile : Circuit -> Ledger.
  Variable circuit_correct : Circuit -> Prop.
  Variable ledger_correct : Ledger -> Prop.

  Hypothesis compile_preserves_correctness :
    forall c : Circuit, circuit_correct c -> ledger_correct (compile c).

  Hypothesis compile_nonexpanding :
    forall c : Circuit, ledger_size (compile c) <= circuit_size c.

  Theorem ledger_lower_bound_transfers_to_circuits :
    forall B : nat,
      (forall l : Ledger, ledger_correct l -> B < ledger_size l) ->
      forall c : Circuit, circuit_correct c -> B < circuit_size c.
  Proof.
    intros B Hledger c Hcorrect.
    pose proof (Hledger (compile c) (compile_preserves_correctness c Hcorrect)) as Hlb.
    pose proof (compile_nonexpanding c) as Hsize.
    lia.
  Qed.

  Theorem bounded_correct_circuit_yields_bounded_correct_ledger :
    forall (B : nat) (c : Circuit),
      circuit_correct c ->
      circuit_size c <= B ->
      exists l : Ledger, ledger_correct l /\ ledger_size l <= B.
  Proof.
    intros B c Hcorrect Hbound.
    exists (compile c). split.
    - apply compile_preserves_correctness. exact Hcorrect.
    - pose proof (compile_nonexpanding c). lia.
  Qed.

  (* Contrapositive presentation convenient for a refuter: if no correct
     semantic ledger exists at size <= B, then no correct circuit exists at
     size <= B. *)
  Theorem no_small_ledger_implies_no_small_circuit :
    forall B : nat,
      (forall l : Ledger, ledger_correct l -> B < ledger_size l) ->
      forall c : Circuit, circuit_size c <= B -> ~ circuit_correct c.
  Proof.
    intros B Hledger c Hsize Hcorrect.
    pose proof (ledger_lower_bound_transfers_to_circuits B Hledger c Hcorrect) as Hlarge.
    lia.
  Qed.

End Transfer.

Print Assumptions ledger_lower_bound_transfers_to_circuits.
Print Assumptions bounded_correct_circuit_yields_bounded_correct_ledger.
Print Assumptions no_small_ledger_implies_no_small_circuit.

End CircuitLedgerTransfer.
