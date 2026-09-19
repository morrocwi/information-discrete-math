(* ===================================================================== *)
(* IDM_EssentialInputDAGBound.v                                           *)
(* Input-slot lower bound for shared fan-in-2 straight-line circuit DAGs.   *)
(*                                                                       *)
(* A gate has at most two references.  Each reference is either an input    *)
(* variable or an earlier gate.  Across s gates plus an optional direct      *)
(* input output reference there are at most 2s+1 input-reference slots.      *)
(* Hence any NoDup family of essential inputs that an exact circuit must     *)
(* syntactically mention has cardinality at most 2s+1.                       *)
(*                                                                       *)
(* This is deliberately sharing-aware: gates are a list of DAG instructions,*)
(* not an unfolded formula tree.  The semantic premise that every essential *)
(* target input must occur is kept explicit.  The SAT clause-encoding lane   *)
(* supplies constructive essentiality witnesses separately.                 *)
(*                                                                       *)
(* Result: m essential inputs -> m <= 2s+1.  This is only a linear lower      *)
(* bound in the encoded input length, not SAT notin P/poly.                  *)
(* ===================================================================== *)

From Coq Require Import Lists.List Arith.Arith Lia.
Import ListNotations.

Module EssentialInputDAGBound.

Inductive Ref : Type :=
| RInput : nat -> Ref
| RGate : nat -> Ref.

Inductive Gate : Type :=
| GAnd : Ref -> Ref -> Gate
| GOr : Ref -> Ref -> Gate.

Definition ref_inputs (r : Ref) : list nat :=
  match r with
  | RInput v => [v]
  | RGate _ => []
  end.

Definition gate_inputs (g : Gate) : list nat :=
  match g with
  | GAnd a b => ref_inputs a ++ ref_inputs b
  | GOr a b => ref_inputs a ++ ref_inputs b
  end.

Fixpoint program_inputs (gs : list Gate) : list nat :=
  match gs with
  | [] => []
  | g :: t => gate_inputs g ++ program_inputs t
  end.

Definition input_slots (gs : list Gate) (out : Ref) : list nat :=
  program_inputs gs ++ ref_inputs out.

Lemma ref_inputs_length :
  forall r,
    length (ref_inputs r) <= 1.
Proof.
  intros [v|g]; simpl; lia.
Qed.

Lemma gate_inputs_length :
  forall g,
    length (gate_inputs g) <= 2.
Proof.
  intros [a b|a b]; unfold gate_inputs;
    rewrite length_app;
    pose proof (ref_inputs_length a);
    pose proof (ref_inputs_length b);
    lia.
Qed.

Lemma program_inputs_length :
  forall gs,
    length (program_inputs gs) <= 2 * length gs.
Proof.
  induction gs as [|g t IH].
  - simpl. lia.
  - simpl. rewrite length_app.
    pose proof (gate_inputs_length g).
    lia.
Qed.

Theorem input_slots_bound :
  forall gs out,
    length (input_slots gs out) <= 2 * length gs + 1.
Proof.
  intros gs out.
  unfold input_slots.
  rewrite length_app.
  pose proof (program_inputs_length gs).
  pose proof (ref_inputs_length out).
  lia.
Qed.

(* Semantic interface: for an exact target computation, every declared
   essential input must occur in the circuit's syntactic input slots. *)
Theorem essential_inputs_force_gate_bound :
  forall essentials gs out,
    NoDup essentials ->
    (forall v, In v essentials -> In v (input_slots gs out)) ->
    length essentials <= 2 * length gs + 1.
Proof.
  intros essentials gs out Hnd Hincl.
  eapply Nat.le_trans.
  - apply NoDup_incl_length with (l' := input_slots gs out).
    + exact Hnd.
    + unfold incl. exact Hincl.
  - apply input_slots_bound.
Qed.

Theorem essential_inputs_even_bound :
  forall essentials gs out m,
    NoDup essentials ->
    (forall v, In v essentials -> In v (input_slots gs out)) ->
    length essentials = S m ->
    m <= 2 * length gs.
Proof.
  intros essentials gs out m Hnd Hincl Hlen.
  pose proof (essential_inputs_force_gate_bound essentials gs out Hnd Hincl) as H.
  rewrite Hlen in H.
  lia.
Qed.

Print Assumptions ref_inputs_length.
Print Assumptions gate_inputs_length.
Print Assumptions program_inputs_length.
Print Assumptions input_slots_bound.
Print Assumptions essential_inputs_force_gate_bound.
Print Assumptions essential_inputs_even_bound.

End EssentialInputDAGBound.
