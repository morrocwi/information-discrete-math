(* ===================================================================== *)
(* IDM_FreeRereadGuard.v                                                  *)
(* Readout-Universe model guard for unrestricted Boolean circuits.        *)
(*                                                                       *)
(* Scope: pure finite/extensional structure.  These lemmas record that an  *)
(* identity-accessible source is sufficient for any target decoder, and    *)
(* that repeated readers may reuse the same source without requiring new   *)
(* retained distinctions in this abstract model.                           *)
(*                                                                       *)
(* This is a NO-GO guard: a circuit-size lower bound may not charge         *)
(* ordinary fanout/rereading as if it were a new Boolean gate.             *)
(* ===================================================================== *)

From Coq Require Import Lists.List Bool.Bool.
Import ListNotations.

Module FreeRereadGuard.

Section IdentityAccessible.

  Variable X : Type.
  Variable target : X -> bool.

  Definition accessible_identity (x : X) : X := x.
  Definition target_decoder (x : X) : bool := target x.

  Theorem identity_accessible_exact :
    forall x,
      target_decoder (accessible_identity x) = target x.
  Proof.
    intro x. reflexivity.
  Qed.

End IdentityAccessible.

Section Reuse.

  Variables X Y : Type.
  Variable reader : X -> Y.

  Fixpoint repeat_read (k : nat) (x : X) : list Y :=
    match k with
    | O => []
    | S k' => reader x :: repeat_read k' x
    end.

  Theorem repeat_read_length :
    forall k x,
      length (repeat_read k x) = k.
  Proof.
    induction k as [|k IH]; intro x; simpl; auto.
  Qed.

  Theorem repeat_read_head_same_source :
    forall k x,
      repeat_read (S k) x = reader x :: repeat_read k x.
  Proof.
    reflexivity.
  Qed.

End Reuse.

Print Assumptions identity_accessible_exact.
Print Assumptions repeat_read_length.
Print Assumptions repeat_read_head_same_source.

End FreeRereadGuard.
