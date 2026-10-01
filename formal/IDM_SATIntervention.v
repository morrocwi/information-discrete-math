(* ===================================================================== *)
(* IDM_SATIntervention.v                                                  *)
(* Generic intervention-query lower bound for the P-vs-NP readout lane.  *)
(*                                                                        *)
(* This file reuses the axiom-free finite pigeonhole core of               *)
(* IDM_DeclarationBound.  It does NOT prove P <> NP.  It proves a         *)
(* restricted retained-state statement: if a family of future Boolean     *)
(* queries separates every pair of n-bit-indexed source objects, and an   *)
(* exact decoder must answer every query from one retained binary record, *)
(* then some source requires a record of length at least n.                *)
(* ===================================================================== *)

Require Import List.
Require Import Bool.
Require Import IDM_DeclarationBound.
Import ListNotations.

Module SATIntervention.

Section GenericInterventionBound.

  Variables Source Query : Type.

  (* An n-bit word indexes a source object.  For SAT the source can be a CNF
     F_b and Query can be a partial assignment / intervention. *)
  Variable source_of_bits : list bool -> Source.

  (* Exact query-response relation on the source. *)
  Variable answer : Source -> Query -> bool.

  (* Compiled retained record and its query decoder. *)
  Variable record : Source -> list bool.
  Variable decode : list bool -> Query -> bool.

  Hypothesis decode_correct :
    forall (bs : list bool) (q : Query),
      decode (record (source_of_bits bs)) q = answer (source_of_bits bs) q.

  (* The future query family separates distinct source indices. *)
  Hypothesis queries_separate_bits :
    forall bs cs : list bool,
      bs <> cs ->
      exists q : Query,
        answer (source_of_bits bs) q <> answer (source_of_bits cs) q.

  Lemma exact_intervention_decoder_forces_record_injective :
    forall bs cs : list bool,
      record (source_of_bits bs) = record (source_of_bits cs) ->
      bs = cs.
  Proof.
    intros bs cs Hrec.
    destruct (list_eq_dec Bool.bool_dec bs cs) as [Heq | Hneq].
    - exact Heq.
    - destruct (queries_separate_bits bs cs Hneq) as [q Hdiff].
      exfalso.
      apply Hdiff.
      rewrite <- (decode_correct bs q).
      rewrite <- (decode_correct cs q).
      rewrite Hrec.
      reflexivity.
  Qed.

  (* Declaration-Bound lift: exact support for all separating interventions
     forces an n-bit record on at least one n-bit-indexed source. *)
  Theorem intervention_record_bits :
    forall n : nat,
      exists bs : list bool,
        In bs (bcube n) /\
        n <= length (record (source_of_bits bs)).
  Proof.
    intro n.
    apply deferred_record_bits.
    intros bs cs Hbs Hcs Hrec.
    apply exact_intervention_decoder_forces_record_injective.
    exact Hrec.
  Qed.

End GenericInterventionBound.

Print Assumptions exact_intervention_decoder_forces_record_injective.
Print Assumptions intervention_record_bits.

End SATIntervention.
