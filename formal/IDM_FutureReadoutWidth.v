(* ===================================================================== *)
(* IDM_FutureReadoutWidth.v                                               *)
(* Future-readout equivalence as a restricted branching-state lower bound. *)
(*                                                                        *)
(* Exact finite content only. This file does NOT prove P <> NP.           *)
(* It formalizes the block-ordered equality witness: after an m-bit prefix *)
(* has been read, an exact state from which every m-bit suffix query can be *)
(* answered must distinguish all 2^m prefixes.                             *)
(* ===================================================================== *)

Require Import List.
Require Import Bool.
Require Import PeanoNat.
Require Import IDM_DeclarationBound.
Import ListNotations.

Module FutureReadoutWidth.

Definition bits_eqb (x y : list bool) : bool :=
  if list_eq_dec Bool.bool_dec x y then true else false.

Lemma bits_eqb_refl : forall x : list bool, bits_eqb x x = true.
Proof.
  intro x. unfold bits_eqb.
  destruct (list_eq_dec Bool.bool_dec x x) as [_ | H]; [reflexivity | contradiction].
Qed.

Lemma bits_eqb_neq :
  forall x y : list bool, x <> y -> bits_eqb x y = false.
Proof.
  intros x y Hneq. unfold bits_eqb.
  destruct (list_eq_dec Bool.bool_dec x y) as [Heq | _].
  - contradiction.
  - reflexivity.
Qed.

Section GenericState.

  Variable State : Type.
  Variable state : list bool -> State.
  Variable decode : State -> list bool -> bool.

  (* Under block order, prefix x is the already-read x-block and suffix y is
     the unread y-block.  Correctness means the retained state answers every
     possible future y query exactly. *)
  Hypothesis decode_equality_correct :
    forall prefix suffix : list bool,
      decode (state prefix) suffix = bits_eqb prefix suffix.

  Theorem equality_future_readout_forces_state_injective :
    forall x y : list bool,
      state x = state y -> x = y.
  Proof.
    intros x y Hstate.
    destruct (list_eq_dec Bool.bool_dec x y) as [Heq | Hneq].
    - exact Heq.
    - exfalso.
      assert (Hyx : y <> x).
      { intro Hyx. apply Hneq. symmetry. exact Hyx. }
      pose proof (decode_equality_correct x x) as Hxx.
      pose proof (decode_equality_correct y x) as Hyxans.
      rewrite bits_eqb_refl in Hxx.
      rewrite (bits_eqb_neq y x Hyx) in Hyxans.
      rewrite Hstate in Hxx.
      congruence.
  Qed.

  Theorem equality_block_middle_states_nodup :
    forall m : nat,
      NoDup (map state (bcube m)).
  Proof.
    intro m.
    apply NoDup_map_inj_on.
    - apply bcube_nodup.
    - intros x y Hx Hy Hstate.
      apply equality_future_readout_forces_state_injective.
      exact Hstate.
  Qed.

  Theorem equality_block_middle_state_count :
    forall m : nat,
      length (map state (bcube m)) = 2 ^ m.
  Proof.
    intro m. rewrite length_map. apply bcube_length.
  Qed.

End GenericState.

Section BinaryRecord.

  Variable record : list bool -> list bool.
  Variable decode_record : list bool -> list bool -> bool.
  Hypothesis decode_record_correct :
    forall prefix suffix : list bool,
      decode_record (record prefix) suffix = bits_eqb prefix suffix.

  Lemma equality_record_injective :
    forall x y : list bool,
      record x = record y -> x = y.
  Proof.
    intros x y Hrecord.
    eapply equality_future_readout_forces_state_injective
      with (State := list bool) (state := record) (decode := decode_record).
    - exact decode_record_correct.
    - exact Hrecord.
  Qed.

  Theorem equality_block_record_bits :
    forall m : nat,
      exists prefix : list bool,
        In prefix (bcube m) /\
        m <= length (record prefix).
  Proof.
    intro m.
    apply deferred_record_bits.
    intros x y Hx Hy Hrecord.
    apply equality_record_injective.
    exact Hrecord.
  Qed.

End BinaryRecord.

Print Assumptions bits_eqb_refl.
Print Assumptions bits_eqb_neq.
Print Assumptions equality_future_readout_forces_state_injective.
Print Assumptions equality_block_middle_states_nodup.
Print Assumptions equality_block_middle_state_count.
Print Assumptions equality_record_injective.
Print Assumptions equality_block_record_bits.

End FutureReadoutWidth.
