(* ===================================================================== *)
(* IDM_RetainRecomputeResolve.v                                           *)
(* Genesis-native finite Retain--Recompute--Resolve (RRR) skeleton.       *)
(*                                                                        *)
(* Scope: exact finite/logical content. This file does NOT prove P <> NP. *)
(* It formalizes the NoEarlyCollapse consequence for an explicitly typed  *)
(* three-channel decoder, a finite aggregation bound for obligations, and *)
(* the full-seed degeneracy showing why recomputation COST must be charged. *)
(* ===================================================================== *)

Require Import List.
Require Import Lia.
Import ListNotations.

Module RetainRecomputeResolve.

Section SemanticNoEarlyCollapse.

  Variables History Future Retained RecomputeSeed Resolved Output : Type.

  Variable retain : History -> Retained.
  Variable seed : History -> RecomputeSeed.
  Variable resolve : History -> Resolved.
  Variable readout : History -> Future -> Output.
  Variable decode : Retained -> RecomputeSeed -> Resolved -> Future -> Output.

  Hypothesis decode_correct :
    forall (h : History) (u : Future),
      decode (retain h) (seed h) (resolve h) u = readout h u.

  (* If a future reader distinguishes two histories, an exact downstream
     decoder cannot see identical values in all three legal channels. *)
  Theorem no_free_collapse_three_channels :
    forall (h h' : History) (u : Future),
      readout h u <> readout h' u ->
      ~ (retain h = retain h' /\
         seed h = seed h' /\
         resolve h = resolve h').
  Proof.
    intros h h' u Hdiff [Hr [Hs Hc]].
    apply Hdiff.
    rewrite <- (decode_correct h u).
    rewrite <- (decode_correct h' u).
    rewrite Hr, Hs, Hc.
    reflexivity.
  Qed.

  (* Constructive disjunctive form, parameterized by explicit equality
     deciders rather than importing classical logic. *)
  Variables retained_eq_dec :
    forall x y : Retained, {x = y} + {x <> y}.
  Variables seed_eq_dec :
    forall x y : RecomputeSeed, {x = y} + {x <> y}.
  Variables resolved_eq_dec :
    forall x y : Resolved, {x = y} + {x <> y}.

  Theorem retain_recompute_resolve_trichotomy :
    forall (h h' : History) (u : Future),
      readout h u <> readout h' u ->
      retain h <> retain h' \/
      seed h <> seed h' \/
      resolve h <> resolve h'.
  Proof.
    intros h h' u Hdiff.
    destruct (retained_eq_dec (retain h) (retain h')) as [Hr | Hr].
    - destruct (seed_eq_dec (seed h) (seed h')) as [Hs | Hs].
      + destruct (resolved_eq_dec (resolve h) (resolve h')) as [Hc | Hc].
        * exfalso.
          eapply no_free_collapse_three_channels.
          -- exact Hdiff.
          -- repeat split; assumption.
        * right. right. exact Hc.
      + right. left. exact Hs.
    - left. exact Hr.
  Qed.

End SemanticNoEarlyCollapse.

(* --------------------------------------------------------------------- *)
(* No-go / calibration theorem.  If recomputation is allowed to keep the   *)
(* complete source history and the decoder has uncharged access to the     *)
(* target readout function, every future-readout problem is trivially exact. *)
(* Thus RRR becomes complexity-relevant only after the construction/decoder *)
(* work of the recompute channel is resource-bounded.                       *)
(* --------------------------------------------------------------------- *)
Section FullSeedDegeneracy.

  Variables History Future Output : Type.
  Variable target_readout : History -> Future -> Output.

  Definition seed_identity (h : History) : History := h.

  Definition decode_from_full_seed
    (_ : unit) (h : History) (_ : unit) (u : Future) : Output :=
    target_readout h u.

  Theorem full_history_recompute_seed_is_exact :
    forall (h : History) (u : Future),
      decode_from_full_seed tt (seed_identity h) tt u = target_readout h u.
  Proof.
    intros h u. reflexivity.
  Qed.

End FullSeedDegeneracy.

Section FiniteObligationLedger.

  Variable Obligation : Type.

  (* If every distinct semantic obligation is assigned to at least one of the
     three legal channels, its count cannot exceed the total channel entries.
     Duplicates on the channel side only weaken the bound. *)
  Theorem rrr_cover_count :
    forall (obligations retained recomputed resolved : list Obligation),
      NoDup obligations ->
      incl obligations (retained ++ recomputed ++ resolved) ->
      length obligations <=
      length retained + length recomputed + length resolved.
  Proof.
    intros obligations retained recomputed resolved Hnd Hinc.
    pose proof (NoDup_incl_length Hnd Hinc) as Hlen.
    rewrite !app_length in Hlen.
    lia.
  Qed.

  Theorem rrr_budget_bound :
    forall (obligations retained recomputed resolved : list Obligation)
           (bR bQ bC : nat),
      NoDup obligations ->
      incl obligations (retained ++ recomputed ++ resolved) ->
      length retained <= bR ->
      length recomputed <= bQ ->
      length resolved <= bC ->
      length obligations <= bR + bQ + bC.
  Proof.
    intros obligations retained recomputed resolved bR bQ bC
           Hnd Hinc HR HQ HC.
    pose proof (rrr_cover_count obligations retained recomputed resolved Hnd Hinc)
      as Hcover.
    lia.
  Qed.

  (* A strict budget gap refutes the claim that the three declared channels
     cover all distinct obligations within those budgets. *)
  Theorem rrr_gap_blocks_complete_cover :
    forall (obligations retained recomputed resolved : list Obligation)
           (bR bQ bC : nat),
      NoDup obligations ->
      length retained <= bR ->
      length recomputed <= bQ ->
      length resolved <= bC ->
      bR + bQ + bC < length obligations ->
      ~ incl obligations (retained ++ recomputed ++ resolved).
  Proof.
    intros obligations retained recomputed resolved bR bQ bC
           Hnd HR HQ HC Hgap Hinc.
    pose proof
      (rrr_budget_bound obligations retained recomputed resolved bR bQ bC
        Hnd Hinc HR HQ HC) as Hbound.
    lia.
  Qed.

End FiniteObligationLedger.

Print Assumptions no_free_collapse_three_channels.
Print Assumptions retain_recompute_resolve_trichotomy.
Print Assumptions full_history_recompute_seed_is_exact.
Print Assumptions rrr_cover_count.
Print Assumptions rrr_budget_bound.
Print Assumptions rrr_gap_blocks_complete_cover.

End RetainRecomputeResolve.
