(* ===================================================================== *)
(* IDM_FixedSamplerSparsePatchGuard.v                                      *)
(* Averaging guard for candidate-independent local samplers.               *)
(*                                                                         *)
(* Suppose there are N possible sparse-patch locations.  After clearing     *)
(* denominators, [hits] records the sampler hit mass for each location.     *)
(* If local incidence gives                                                  *)
(*                                                                         *)
(*     sum hits <= d * total,                                               *)
(*                                                                         *)
(* then some location has                                                    *)
(*                                                                         *)
(*     N * hit <= d * total.                                                *)
(*                                                                         *)
(* Consequently, when N > p*d and total>0, some patch has                   *)
(*                                                                         *)
(*     hit / total < 1/p                                                    *)
(*                                                                         *)
(* in cleared-denominator form p*hit < total.                               *)
(*                                                                         *)
(* This is an arithmetic/no-go kernel only.  A concrete application must    *)
(* separately prove the incidence budget and that the sparse patch is       *)
(* realizable inside the candidate circuit class.  It proves no SAT lower   *)
(* bound and makes no P<>NP claim.                                          *)
(* ===================================================================== *)

From Coq Require Import Lists.List Arith.Arith Lia.
Import ListNotations.

Module FixedSamplerSparsePatchGuard.

Fixpoint nsum (xs : list nat) : nat :=
  match xs with
  | [] => 0
  | x :: t => x + nsum t
  end.

Lemma small_member_or_all_large :
  forall xs N B,
    (exists h, In h xs /\ N * h <= B) \/
    Forall (fun h => B < N * h) xs.
Proof.
  induction xs as [|a t IH]; intros N B.
  - right. constructor.
  - destruct (le_gt_dec (N * a) B) as [Hle | Hgt].
    + left. exists a. split.
      * left. reflexivity.
      * exact Hle.
    + destruct (IH N B) as [[h [Hin Hsmall]] | Hall].
      * left. exists h. split.
        -- right. exact Hin.
        -- exact Hsmall.
      * right. constructor.
        -- exact Hgt.
        -- exact Hall.
Qed.

Lemma all_large_forces_sum_large :
  forall xs N B,
    xs <> [] ->
    Forall (fun h => B < N * h) xs ->
    length xs * B < N * nsum xs.
Proof.
  induction xs as [|x t IH]; intros N B Hne Hall.
  - contradiction.
  - inversion Hall as [|x' t' Hx Ht]; subst.
    destruct t as [|y u].
    + simpl in *. nia.
    + assert (Htail : y :: u <> []) by discriminate.
      specialize (IH N B Htail Ht).
      simpl in *. nia.
Qed.

Theorem fixed_sampler_sparse_patch_guard :
  forall hits N total d,
    0 < N ->
    length hits = N ->
    nsum hits <= d * total ->
    exists h,
      In h hits /\
      N * h <= d * total.
Proof.
  intros hits N total d HN Hlen Hsum.
  destruct (small_member_or_all_large hits N (d * total))
    as [Hsmall | Hall].
  - exact Hsmall.
  - exfalso.
    assert (Hne : hits <> []).
    { intro Heq. subst hits. simpl in Hlen. lia. }
    pose proof (all_large_forces_sum_large
      hits N (d * total) Hne Hall) as Hlarge.
    rewrite Hlen in Hlarge.
    nia.
Qed.

Theorem fixed_sampler_fails_inverse_p_when_locations_dominate :
  forall hits N total d p,
    0 < N ->
    0 < total ->
    length hits = N ->
    nsum hits <= d * total ->
    p * d < N ->
    exists h,
      In h hits /\
      p * h < total.
Proof.
  intros hits N total d p HN Htotal Hlen Hsum Hgap.
  destruct (fixed_sampler_sparse_patch_guard
    hits N total d HN Hlen Hsum) as [h [Hin Havg]].
  exists h. split.
  - exact Hin.
  - nia.
Qed.

Print Assumptions small_member_or_all_large.
Print Assumptions all_large_forces_sum_large.
Print Assumptions fixed_sampler_sparse_patch_guard.
Print Assumptions fixed_sampler_fails_inverse_p_when_locations_dominate.

End FixedSamplerSparsePatchGuard.
