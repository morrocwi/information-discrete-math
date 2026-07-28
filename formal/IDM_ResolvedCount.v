(* ===================================================================== *)
(*  IDM_ResolvedCount.v — the resolved (four-valued) pivot readout, and the *)
(*  discrete core of P4: separating the determinate neutral 0 from the      *)
(*  unresolved bottom ⊥ inside an inertia count, machine-checked over ℚ and  *)
(*  axiom-free (Coq 8.20; Print Assumptions = Closed under the global        *)
(*  context).  By Yaoharee Lahtee.                                          *)
(*                                                                          *)
(*  The readout-mathematics brief's P4 asks: define a resolved count that    *)
(*  returns an S₄ value per pivot, characterise the floors under which it is *)
(*  well-behaved, and prove the ⊥-set is exactly the coordinates the declared *)
(*  resolution does not decide.  The full analytic statements (monotonicity   *)
(*  in the shift σ; ν_ε = the exact count of some Ã within ε‖A‖) are          *)
(*  real-matrix backward-error results, kept at their honest tier (measured   *)
(*  + classical Sturm backward-stability, in retained_spectral/inertia.py and *)
(*  tests/test_resolved_inertia.py) — NOT claimed here.  What IS finite and   *)
(*  decidable is proved here, axiom-free, and it is the operational heart:    *)
(*                                                                          *)
(*   • the ⊥-set is EXACTLY the undecided band  |v| ≤ floor  (classify_bot_iff)*)
(*   • a resolved strict sign NEVER lies: a reported + is truly > 0, a         *)
(*     reported − is truly < 0                (classify_plus/minus_sound)      *)
(*   • shrinking the declared resolution can only SHRINK the ⊥-set            *)
(*                                            (bot_monotone_in_floor)          *)
(*   • the certain-below count under-approximates the classic signed-floor     *)
(*     count, so the true count lives in a bracket the readout reports         *)
(*                                            (certain_le_signedfloor)         *)
(* ===================================================================== *)

Require Import QArith.
Require Import Setoid.                   (* setoid rewriting under Qeq (adds no axioms) *)
Require Import Lia.
Require Import IDM_ReadoutMinimality.   (* the S4 = {Sp,Sm,Sz,Sbot} value algebra *)

Local Open Scope Q_scope.

(* ---------------------------------------------------------------------- *)
(*  What `0` MEANS here (information semantics — read before the code).      *)
(*                                                                          *)
(*  In this framework every reading is a readout of a retained difference    *)
(*  δ_R (information = retained distinction).  The neutral value `0` (Sz) is  *)
(*  NOT 'nothing', NOT the void, and NOT the continuum's point of zero        *)
(*  extent (a non-readout).  It is a POSITIVE, determinate reading: a δ_R     *)
(*  that is genuinely present and whose signed content cancels EXACTLY — a    *)
(*  null direction, an exact balance, the invariant rank-deficiency `n₀` of   *)
(*  Sylvester's law.  It is a fact ABOUT THE OBJECT and it carries            *)
(*  information (which is why, in IDM_ReadoutMinimality, `0` is order-        *)
(*  incomparable to ±, never the order-bottom).                              *)
(*                                                                          *)
(*  The bottom `⊥` (Sbot) is the opposite kind of thing: a fact ABOUT THE     *)
(*  INSTRUMENT — the declared resolution does not retain enough distinction   *)
(*  to decide the sign.  It is the least element of the information order.    *)
(*                                                                          *)
(*  So `classify` must let `0` be REACHED — but only where it is truly        *)
(*  earned: at EXACT resolution (floor = 0) an exact null reads `0` (a        *)
(*  determinate balance in the object); at any POSITIVE declared resolution   *)
(*  the whole band is honestly `⊥` (the instrument cannot certify exactness). *)
(*  The theorem `bot_needs_positive_resolution` below makes this precise:     *)
(*  ⊥ NEVER arises intrinsically — it is always the instrument's finiteness.  *)
(* ---------------------------------------------------------------------- *)
Definition classify (floor v : Q) : S4 :=
  if Qlt_le_dec floor v then Sp                 (* floor < v             -> + (certain)    *)
  else if Qlt_le_dec v (- floor) then Sm        (* v < -floor            -> - (certain)    *)
  else if Qeq_dec floor 0 then Sz               (* band is {0}, exact    -> 0 (determinate)*)
  else Sbot.                                     (* band, positive floor  -> ⊥ (unresolved) *)

(* ---- ⊥-characterisation: the unresolved set is EXACTLY the band at a       *)
(*      POSITIVE declared resolution.  (At exact resolution the band is {0}    *)
(*      and the reading is the determinate neutral 0, not ⊥.)                 *)
Theorem classify_bot_iff :
  forall floor v,
    classify floor v = Sbot <-> (~ floor == 0 /\ - floor <= v /\ v <= floor).
Proof.
  intros floor v. unfold classify.
  destruct (Qlt_le_dec floor v) as [Hgt | Hle1].
  - split; [ discriminate | intros [_ [_ Hvf]]; exfalso; exact (Qlt_not_le _ _ Hgt Hvf) ].
  - destruct (Qlt_le_dec v (- floor)) as [Hlt | Hge2].
    + split; [ discriminate | intros [_ [Hnf _]]; exfalso; exact (Qlt_not_le _ _ Hlt Hnf) ].
    + destruct (Qeq_dec floor 0) as [Hz | Hnz].
      * split; [ discriminate | intros [Hne _]; exfalso; apply Hne; exact Hz ].
      * split; [ intros _; repeat split; assumption | reflexivity ].
Qed.

(* ---- THE philosophical theorem.  ⊥ is ALWAYS a fact about the instrument:   *)
(*      it can only arise from a strictly POSITIVE declared resolution, never  *)
(*      intrinsically from the object.  A reading of ⊥ is never `the value is  *)
(*      indeterminate` -- it is `MY resolution is too coarse to say`.           *)
Theorem bot_needs_positive_resolution :
  forall floor v, 0 <= floor -> classify floor v = Sbot -> 0 < floor.
Proof.
  intros floor v Hf H. apply classify_bot_iff in H. destruct H as [Hne _].
  (* 0 <= floor and floor <> 0 give 0 < floor *)
  destruct (Qlt_le_dec 0 floor) as [Hlt | Hle]; [ exact Hlt |].
  exfalso. apply Hne. apply Qle_antisym; assumption.
Qed.

(* ---- the determinate neutral 0 is INTRINSIC and EXACT: it is emitted only    *)
(*      at exact resolution, and exactly when the value is a true balance.      *)
(*      This is `0` as a fact about the OBJECT — the mirror image of ⊥ above.   *)
Theorem classify_zero_iff :
  forall floor v, classify floor v = Sz <-> (floor == 0 /\ v == 0).
Proof.
  intros floor v. unfold classify. split.
  - (* forward: only the third branch yields Sz, forcing floor==0 and v==0 *)
    destruct (Qlt_le_dec floor v) as [Hgt | Hle1]; [ discriminate |].
    destruct (Qlt_le_dec v (- floor)) as [Hlt | Hge2]; [ discriminate |].
    destruct (Qeq_dec floor 0) as [Hz | Hnz]; [| discriminate ].
    intros _. split; [ exact Hz |].
    assert (Hnf0 : - floor == 0) by (rewrite Hz; reflexivity).
    apply Qle_antisym.
    + (* v <= 0 *) rewrite <- Hz. exact Hle1.
    + (* 0 <= v *) apply Qle_trans with (y := - floor); [ rewrite Hnf0; apply Qle_refl | exact Hge2 ].
  - (* backward: floor==0 and v==0 route the deciders to the Sz branch *)
    intros [Hz Hv].
    destruct (Qlt_le_dec floor v) as [Hgt | Hle1].
    { exfalso. rewrite Hz, Hv in Hgt. exact (Qlt_irrefl _ Hgt). }
    destruct (Qlt_le_dec v (- floor)) as [Hlt | Hge2].
    { exfalso. rewrite Hv, Hz in Hlt. exact (Qlt_irrefl _ Hlt). }
    destruct (Qeq_dec floor 0) as [Hz2 | Hnz]; [ reflexivity | exfalso; apply Hnz; exact Hz ].
Qed.

(* ---- a resolved strict sign never lies (backward-honesty, per pivot). ----- *)
(*      With a nonnegative floor, a reported + is a genuine positive value.    *)
Theorem classify_plus_sound :
  forall floor v, 0 <= floor -> classify floor v = Sp -> 0 < v.
Proof.
  intros floor v Hf H. unfold classify in H.
  destruct (Qlt_le_dec floor v) as [Hgt | Hle1].
  - apply Qle_lt_trans with (y := floor); assumption.
  - destruct (Qlt_le_dec v (- floor)); [ discriminate | destruct (Qeq_dec floor 0); discriminate ].
Qed.

(*      and a reported − is a genuine negative value.                          *)
Theorem classify_minus_sound :
  forall floor v, 0 <= floor -> classify floor v = Sm -> v < 0.
Proof.
  intros floor v Hf H. unfold classify in H.
  destruct (Qlt_le_dec floor v) as [Hgt | Hle1]; [ discriminate |].
  destruct (Qlt_le_dec v (- floor)) as [Hlt | Hge2];
    [| destruct (Qeq_dec floor 0); discriminate ].
  apply Qlt_le_trans with (y := - floor); [ assumption |].
  (* -floor <= 0  since 0 <= floor *)
  rewrite <- (Qopp_involutive 0). simpl. apply Qopp_le_compat. assumption.
Qed.

(*      'not-bot' means a DETERMINATE reading — a definite + , a definite − , or  *)
(*      the determinate neutral 0.  The point of the four-valued algebra: a     *)
(*      non-⊥ reading is never silent, and 0 is one of the determinate three,   *)
(*      NOT lumped with the instrument's ⊥.                                     *)
Theorem classify_not_bot_is_determinate :
  forall floor v, classify floor v <> Sbot ->
    classify floor v = Sp \/ classify floor v = Sm \/ classify floor v = Sz.
Proof.
  intros floor v H. unfold classify in *.
  destruct (Qlt_le_dec floor v); [ now left |].
  destruct (Qlt_le_dec v (- floor)); [ right; now left |].
  destruct (Qeq_dec floor 0); [ right; right; reflexivity | now exfalso; apply H ].
Qed.

(* ---- monotonicity in the declared resolution: a LARGER floor (coarser      *)
(*      resolution) can only ENLARGE the ⊥-set; equivalently, refining the    *)
(*      resolution (smaller floor) only ever resolves more pivots.            *)
Theorem bot_monotone_in_floor :
  forall f1 f2 v, 0 <= f1 -> f1 <= f2 ->
    classify f1 v = Sbot -> classify f2 v = Sbot.
Proof.
  intros f1 f2 v Hf1 Hle Hbot.
  apply classify_bot_iff in Hbot. destruct Hbot as [Hne1 [Hlo Hhi]].
  (* 0 < f1 (bot needs positive resolution) <= f2, so ~ f2 == 0 too *)
  assert (Hpos1 : 0 < f1)
    by (destruct (Qlt_le_dec 0 f1) as [Hlt | Hle0];
        [ exact Hlt | exfalso; apply Hne1; apply Qle_antisym; assumption ]).
  apply classify_bot_iff. repeat split.
  - (* ~ f2 == 0 *) intro Hz2. rewrite Hz2 in Hle.
    exact (Qlt_not_le _ _ Hpos1 Hle).
  - (* -f2 <= -f1 <= v *)
    apply Qle_trans with (y := - f1); [ apply Qopp_le_compat; assumption | assumption ].
  - (* v <= f1 <= f2 *)
    apply Qle_trans with (y := f1); assumption.
Qed.

(* ---------------------------------------------------------------------- *)
(*  The count bracket.  Over a list of pivots, the resolved reading splits   *)
(*  the classic signed-floor count into a CERTAIN part and an UNRESOLVED     *)
(*  part.  `signed_floor_below` models the legacy integer count (every band  *)
(*  pivot forced to -floor, hence counted below); `certain_below` counts     *)
(*  only the definite negatives.  The true count lies in                     *)
(*  [certain_below, certain_below + unresolved], and the classic count is     *)
(*  its upper end — so the single integer was hiding `unresolved` bits of     *)
(*  uncertainty the resolved reading now returns.                            *)
(* ---------------------------------------------------------------------- *)
Require Import List.
Import ListNotations.

(* is a pivot value a CERTAIN negative at this resolution? (a definite −)      *)
Definition is_below (floor v : Q) : bool :=
  match classify floor v with Sm => true | _ => false end.

(* the classic signed-floor rule: every band pivot is forced to -floor, so it  *)
(* counts as below — i.e. below OR unresolved.  This models the single integer *)
(* count_below_banded returns.                                                 *)
Definition is_below_or_bot (floor v : Q) : bool :=
  match classify floor v with Sm => true | Sbot => true | _ => false end.

Fixpoint count_if (p : Q -> bool) (vs : list Q) : nat :=
  match vs with
  | [] => 0
  | v :: tl => (if p v then 1 else 0) + count_if p tl
  end.

(* the unresolved (⊥) pivots — a fact about the instrument's declared resolution *)
Definition is_bot (floor v : Q) : bool :=
  match classify floor v with Sbot => true | _ => false end.

Definition certain_below (floor : Q) (vs : list Q) : nat := count_if (is_below floor) vs.
Definition unresolved   (floor : Q) (vs : list Q) : nat := count_if (is_bot floor) vs.
Definition signed_floor_below (floor : Q) (vs : list Q) : nat := count_if (is_below_or_bot floor) vs.

(* a pointwise 0/1 split lifts to the counts over any list (no atom desync).    *)
Lemma count_if_split :
  forall (p q r : Q -> bool) vs,
    (forall v, ((if p v then 1 else 0) = (if q v then 1 else 0) + (if r v then 1 else 0))%nat) ->
    count_if p vs = (count_if q vs + count_if r vs)%nat.
Proof.
  intros p q r vs Hpt. induction vs as [| v tl IH]; simpl; [ reflexivity |].
  rewrite Hpt, IH. lia.
Qed.

(* the signed-floor count splits EXACTLY into the certain-below and the         *)
(* unresolved (⊥) counts: the legacy single integer hid precisely `unresolved`  *)
(* pivots of uncertainty by charging every ⊥ as a −.                            *)
Theorem signedfloor_is_certain_plus_unresolved :
  forall floor vs,
    signed_floor_below floor vs = (certain_below floor vs + unresolved floor vs)%nat.
Proof.
  intros floor vs. unfold signed_floor_below, certain_below, unresolved.
  apply count_if_split. intro v.
  unfold is_below_or_bot, is_below, is_bot. destruct (classify floor v); reflexivity.
Qed.

(* hence the certain-below count under-approximates the classic signed-floor     *)
(* count — the true #below is bracketed in [certain_below, signed_floor_below],  *)
(* the legacy single integer being the UPPER end.                               *)
Theorem certain_le_signedfloor :
  forall floor vs, (certain_below floor vs <= signed_floor_below floor vs)%nat.
Proof.
  intros floor vs. rewrite signedfloor_is_certain_plus_unresolved. apply Nat.le_add_r.
Qed.
