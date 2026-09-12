(* ===================================================================== *)
(* IDM_CircuitGenesisBridge.v                                             *)
(* Exact finite structural bridge: shared DeMorgan DAG -> Genesis ledger. *)
(*                                                                        *)
(* Scope: syntax/semantics preservation only. This file does NOT prove a  *)
(* circuit lower bound for SAT or P <> NP. It closes the elementary bridge *)
(* obligation that a fan-in-two DAG can be copied into a one-entry-per-gate *)
(* semantic ledger without unfolding sharing or importing a target answer. *)
(* ===================================================================== *)

Require Import List Bool Arith.
Import ListNotations.

Module CircuitGenesisBridge.

Inductive gate_desc : Type :=
| GInput : nat -> gate_desc
| GNot   : nat -> gate_desc
| GAnd   : nat -> nat -> gate_desc
| GOr    : nat -> nat -> gate_desc.

Definition parents (g : gate_desc) : list nat :=
  match g with
  | GInput _ => []
  | GNot a => [a]
  | GAnd a b => [a; b]
  | GOr a b => [a; b]
  end.

Definition eval_gate
  (inputs env : list bool) (g : gate_desc) : bool :=
  match g with
  | GInput i => nth i inputs false
  | GNot a => negb (nth a env false)
  | GAnd a b => andb (nth a env false) (nth b env false)
  | GOr a b => orb (nth a env false) (nth b env false)
  end.

Fixpoint eval_gates_acc
  (inputs : list bool) (gs : list gate_desc) (env : list bool) : list bool :=
  match gs with
  | [] => env
  | g :: rest =>
      let v := eval_gate inputs env g in
      eval_gates_acc inputs rest (env ++ [v])
  end.

Definition eval_circuit (inputs : list bool) (gs : list gate_desc) : list bool :=
  eval_gates_acc inputs gs [].

Definition circuit_readout
  (inputs : list bool) (gs : list gate_desc) (out : nat) : bool :=
  nth out (eval_circuit inputs gs) false.

Record ledger_entry : Type := mkLedgerEntry {
  le_index : nat;
  le_gate : gate_desc
}.

Fixpoint compile_from (k : nat) (gs : list gate_desc) : list ledger_entry :=
  match gs with
  | [] => []
  | g :: rest => mkLedgerEntry k g :: compile_from (S k) rest
  end.

Definition compile_ledger (gs : list gate_desc) : list ledger_entry :=
  compile_from 0 gs.

Definition erase_ledger (ls : list ledger_entry) : list gate_desc :=
  map le_gate ls.

Fixpoint ledger_indices (ls : list ledger_entry) : list nat :=
  match ls with
  | [] => []
  | e :: rest => le_index e :: ledger_indices rest
  end.

Lemma erase_compile_from :
  forall k gs, erase_ledger (compile_from k gs) = gs.
Proof.
  intros k gs. revert k.
  induction gs as [|g rest IH]; intro k; simpl.
  - reflexivity.
  - rewrite IH. reflexivity.
Qed.

Theorem cgsl_erases_to_original :
  forall gs, erase_ledger (compile_ledger gs) = gs.
Proof.
  intro gs. unfold compile_ledger. apply erase_compile_from.
Qed.

Lemma compile_from_length :
  forall k gs, length (compile_from k gs) = length gs.
Proof.
  intros k gs. revert k.
  induction gs as [|g rest IH]; intro k; simpl.
  - reflexivity.
  - rewrite IH. reflexivity.
Qed.

Theorem cgsl_one_entry_per_gate :
  forall gs, length (compile_ledger gs) = length gs.
Proof.
  intro gs. unfold compile_ledger. apply compile_from_length.
Qed.

Lemma compile_from_indices :
  forall k gs, ledger_indices (compile_from k gs) = seq k (length gs).
Proof.
  intros k gs. revert k.
  induction gs as [|g rest IH]; intro k; simpl.
  - reflexivity.
  - rewrite IH. reflexivity.
Qed.

Theorem cgsl_topological_indices_preserved :
  forall gs,
    ledger_indices (compile_ledger gs) = seq 0 (length gs).
Proof.
  intro gs. unfold compile_ledger. apply compile_from_indices.
Qed.

Definition eval_ledger (inputs : list bool) (ls : list ledger_entry) : list bool :=
  eval_circuit inputs (erase_ledger ls).

Definition ledger_readout
  (inputs : list bool) (ls : list ledger_entry) (out : nat) : bool :=
  nth out (eval_ledger inputs ls) false.

Theorem cgsl_semantics_preserved :
  forall inputs gs,
    eval_ledger inputs (compile_ledger gs) = eval_circuit inputs gs.
Proof.
  intros inputs gs. unfold eval_ledger.
  rewrite cgsl_erases_to_original. reflexivity.
Qed.

Theorem cgsl_terminal_reader_preserved :
  forall inputs gs out,
    ledger_readout inputs (compile_ledger gs) out =
    circuit_readout inputs gs out.
Proof.
  intros inputs gs out.
  unfold ledger_readout, circuit_readout.
  rewrite cgsl_semantics_preserved. reflexivity.
Qed.

Theorem cgsl_parent_descriptors_preserved :
  forall gs,
    map parents (erase_ledger (compile_ledger gs)) = map parents gs.
Proof.
  intro gs. rewrite cgsl_erases_to_original. reflexivity.
Qed.

Print Assumptions cgsl_erases_to_original.
Print Assumptions cgsl_one_entry_per_gate.
Print Assumptions cgsl_topological_indices_preserved.
Print Assumptions cgsl_semantics_preserved.
Print Assumptions cgsl_terminal_reader_preserved.
Print Assumptions cgsl_parent_descriptors_preserved.

End CircuitGenesisBridge.
