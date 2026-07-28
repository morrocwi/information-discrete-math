(* ===================================================================== *)
(*  IDM_ApproxCount.v — the r-coarsened deferred-counting pigeonhole,       *)
(*  finite combinatorial core, axiom-free.  Coq 8.20, Closed under the      *)
(*  global context.  Developed by Yaoharee Lahtee.                          *)
(*                                                                          *)
(*  Task #45 asks about two OPEN questions on top of the exact Declaration  *)
(*  Bound (IDM_DeclarationBound.v):                                         *)
(*                                                                          *)
(*   P7 (approximate counting, CONJECTURE, NOT proved here): the retained-   *)
(*      state cost of a DEFERRED weight readout nu(sigma), correct only to   *)
(*      within an additive +-r, is conjectured Theta(n/r) retained BITS.     *)
(*      Proving Theta(n/r) needs a genuine r-tolerant FOOLING FAMILY of      *)
(*      size exponential in n/r (an adversary/communication-complexity       *)
(*      argument), which is NOT constructed here and remains +R-Open.        *)
(*   P8 (randomized, two-sided error, CONJECTURE, NOT touched here): does    *)
(*      the Omega(n) exact deferred bound survive a reduction from INDEX     *)
(*      under two-sided-error randomization?  Entirely open; nothing in     *)
(*      this file bears on it, and no randomized/probabilistic claim is      *)
(*      stated anywhere below.                                              *)
(*                                                                          *)
(*  What IS proved here — a strictly WEAKER, genuinely tractable honest      *)
(*  kernel that is the finite engine an r-tolerant argument would need,      *)
(*  without claiming the sharp Theta(n/r) rate:                             *)
(*                                                                          *)
(*   AC1 pigeonhole_bits_needed   a direct generalisation of                *)
(*       IDM_DeclarationBound.deferred_record_bits from the full n-cube to   *)
(*       ANY NoDup list of size >= 2^L: an injective-on-the-list record      *)
(*       scheme must retain >= L bits for some list element.                *)
(*   AC2 fam_nodup / fam_elem_weight   a concrete "weight-ladder" family of  *)
(*       S(n/(2r+1)) n-bit strings with pairwise Hamming weights spaced      *)
(*       exactly (2r+1) apart — a genuine, finite, fooling-family-AT-        *)
(*       RESOLUTION-r fact (weights, not full fooling of an adversary).      *)
(*   AC3 r_correct_far_apart_False   any r-correct approximate answer        *)
(*       function CANNOT agree on two strings whose true weights differ by   *)
(*       more than 2r (their +-r answer-intervals are disjoint) — a plain    *)
(*       arithmetic fact about interval separation.                          *)
(*   AC4 approx_count_deferred_lower_bound   composing AC1-AC3: any deferred  *)
(*       scheme whose retained record determines an r-correct weight answer  *)
(*       must, for SOME string in the ladder, retain >= L bits, whenever      *)
(*       2^L <= S(n/(2r+1)).  This is an honest Omega(log(n/r)) retained-bit *)
(*       LOWER BOUND for r-approximate deferred counting — logarithmic, not   *)
(*       linear, and STRICTLY WEAKER than the conjectured Theta(n/r) of P7.   *)
(*       P7 itself (the sharp linear rate) is NOT proved and stays Open;     *)
(*       P8 is untouched.                                                    *)
(*                                                                          *)
(*  Tier: Th_coqc for AC1-AC4 (machine-checked, axiom-free, below).  P7 and  *)
(*  P8 remain +R-Open / Open by design — see verify.sh's THMS list, which    *)
(*  lists only AC1-AC4, never P7/P8.                                        *)
(* ===================================================================== *)

Require Import List.
Require Import PeanoNat.
Require Import Lia.
Require Import Arith.
Import ListNotations.

Require Import IDM_DeclarationBound.
  (* reuses: b2n, short_records, short_records_length, short_records_complete,
     NoDup_map_inj_on, two_pow_pos, NoDup_incl_length (stdlib) *)

(* ===================================================================== *)
(*  AC1 — generalised pigeonhole: ANY NoDup list of size >= 2^L, injective  *)
(*  under rec, forces some element's record to be >= L bits.  Instantiating  *)
(*  l := bcube n, L := n recovers deferred_record_bits exactly (2^n <= 2^n). *)
(* ===================================================================== *)
Theorem pigeonhole_bits_needed :
  forall (l : list (list bool)) (rec : list bool -> list bool) (L : nat),
    NoDup l ->
    2 ^ L <= length l ->
    (forall x y, In x l -> In y l -> rec x = rec y -> x = y) ->
    exists x, In x l /\ L <= length (rec x).
Proof.
  intros l rec L Hnd Hlen Hinj.
  destruct (Exists_dec (fun x => L <= length (rec x)) l
                       (fun x => le_dec L (length (rec x)))) as [HE | HNE].
  - apply Exists_exists in HE as [x [Hin HP]]. exists x. split; assumption.
  - exfalso.
    assert (Hall : Forall (fun x => ~ (L <= length (rec x))) l).
    { apply Forall_forall. intros x Hx HP.
      apply HNE. apply Exists_exists. exists x. split; assumption. }
    assert (Hndrec : NoDup (map rec l)).
    { apply NoDup_map_inj_on; [exact Hnd | exact Hinj]. }
    assert (Hincl : incl (map rec l) (short_records L)).
    { intros y Hy. apply in_map_iff in Hy as [x [<- Hx]].
      rewrite Forall_forall in Hall. specialize (Hall x Hx).
      apply short_records_complete. lia. }
    pose proof (NoDup_incl_length Hndrec Hincl) as Hle.
    rewrite length_map in Hle.
    rewrite short_records_length in Hle.
    pose proof (two_pow_pos L). lia.
Qed.

(* ===================================================================== *)
(*  Hamming weight, and its additivity under append / repeat.               *)
(* ===================================================================== *)
Definition weight (bs : list bool) : nat :=
  fold_right (fun x acc => b2n x + acc) 0 bs.

Lemma weight_cons : forall x t, weight (x :: t) = b2n x + weight t.
Proof. intros; reflexivity. Qed.

Lemma weight_app : forall a b, weight (a ++ b) = weight a + weight b.
Proof.
  induction a as [| x a IH]; intros b; simpl.
  - reflexivity.
  - rewrite IH. lia.
Qed.

Lemma weight_repeat_true : forall k, weight (repeat true k) = k.
Proof.
  induction k as [| k IH]; simpl.
  - reflexivity.
  - rewrite IH. reflexivity.
Qed.

Lemma weight_repeat_false : forall k, weight (repeat false k) = 0.
Proof.
  induction k as [| k IH]; simpl.
  - reflexivity.
  - rewrite IH. reflexivity.
Qed.

(* ===================================================================== *)
(*  AC2 — the weight-ladder family: n-bit strings whose Hamming weights are  *)
(*  the multiples of (2r+1) up to n, so distinct family members are always   *)
(*  more than 2r apart in true weight.                                      *)
(* ===================================================================== *)
Definition fam_elem (n r k : nat) : list bool :=
  repeat true (k * (2 * r + 1)) ++ repeat false (n - k * (2 * r + 1)).

Lemma fam_elem_weight : forall n r k, weight (fam_elem n r k) = k * (2 * r + 1).
Proof.
  intros. unfold fam_elem.
  rewrite weight_app, weight_repeat_true, weight_repeat_false. lia.
Qed.

Lemma k_bound : forall n r k, k <= n / (2 * r + 1) -> k * (2 * r + 1) <= n.
Proof.
  intros n r k Hk.
  pose proof (Nat.div_mod n (2 * r + 1) ltac:(lia)) as Hdm.
  assert (Hmul : k * (2 * r + 1) <= (n / (2 * r + 1)) * (2 * r + 1)) by nia.
  nia.
Qed.

Lemma fam_elem_length : forall n r k, k <= n / (2 * r + 1) -> length (fam_elem n r k) = n.
Proof.
  intros n r k Hk. unfold fam_elem.
  rewrite length_app, !repeat_length.
  pose proof (k_bound n r k Hk). lia.
Qed.

Definition fam (n r : nat) : list (list bool) :=
  map (fam_elem n r) (seq 0 (S (n / (2 * r + 1)))).

Lemma fam_length : forall n r, length (fam n r) = S (n / (2 * r + 1)).
Proof. intros. unfold fam. rewrite length_map, length_seq. reflexivity. Qed.

Lemma fam_in : forall n r x,
  In x (fam n r) -> exists k, k <= n / (2 * r + 1) /\ x = fam_elem n r k.
Proof.
  intros n r x Hin. unfold fam in Hin.
  apply in_map_iff in Hin as [k [<- Hk]].
  apply in_seq in Hk as [_ Hkb].
  exists k. split; [lia | reflexivity].
Qed.

Lemma fam_nodup : forall n r, NoDup (fam n r).
Proof.
  intros n r. unfold fam.
  apply NoDup_map_inj_on.
  - apply seq_NoDup.
  - intros k1 k2 Hk1 Hk2 Heq.
    apply in_seq in Hk1 as [_ Hk1b]. apply in_seq in Hk2 as [_ Hk2b].
    assert (Hb1 : k1 <= n / (2 * r + 1)) by lia.
    assert (Hb2 : k2 <= n / (2 * r + 1)) by lia.
    assert (Hw : weight (fam_elem n r k1) = weight (fam_elem n r k2))
      by (rewrite Heq; reflexivity).
    rewrite !fam_elem_weight in Hw.
    nia.
Qed.

(* ===================================================================== *)
(*  AC3 — an r-correct answer function cannot agree on two strings whose     *)
(*  true weights differ by more than 2r: their +-r answer-intervals are      *)
(*  disjoint.  This is the plain arithmetic fact that makes the ladder a     *)
(*  genuine (weight-)fooling family at resolution r.                        *)
(* ===================================================================== *)
Definition r_correct (val : list bool -> nat) (r : nat) : Prop :=
  forall bs, weight bs <= val bs + r /\ val bs <= weight bs + r.

Lemma r_correct_far_apart_False :
  forall (val : list bool -> nat) (r : nat) (bs cs : list bool),
    r_correct val r ->
    weight bs + 2 * r < weight cs ->
    val bs = val cs ->
    False.
Proof.
  intros val r bs cs Hcorr Hfar Heq.
  destruct (Hcorr bs) as [Hb1 Hb2].
  destruct (Hcorr cs) as [Hc1 Hc2].
  lia.
Qed.

(* ===================================================================== *)
(*  AC4 — the composed honest lower bound: an Omega(log(n/r)) retained-bit   *)
(*  bound for r-approximate deferred counting.  STRICTLY WEAKER than P7's    *)
(*  conjectured Theta(n/r); P7 and P8 are NOT proved and stay Open (header). *)
(* ===================================================================== *)
Theorem approx_count_deferred_lower_bound :
  forall (n r L : nat) (rec : list bool -> list bool) (val : list bool -> nat),
    2 ^ L <= S (n / (2 * r + 1)) ->
    (forall bs cs, rec bs = rec cs -> val bs = val cs) ->
    r_correct val r ->
    exists bs, In bs (fam n r) /\ L <= length (rec bs).
Proof.
  intros n r L rec val HL Hdet Hcorr.
  apply pigeonhole_bits_needed with (l := fam n r).
  - apply fam_nodup.
  - rewrite fam_length. exact HL.
  - intros x y Hx Hy Heq.
    apply fam_in in Hx as [k1 [Hk1 ->]].
    apply fam_in in Hy as [k2 [Hk2 ->]].
    assert (Hdetv : val (fam_elem n r k1) = val (fam_elem n r k2))
      by (apply Hdet; exact Heq).
    destruct (Nat.lt_trichotomy k1 k2) as [Hlt | [Heqk | Hgt]].
    + exfalso.
      apply (r_correct_far_apart_False val r (fam_elem n r k1) (fam_elem n r k2) Hcorr).
      * rewrite !fam_elem_weight. nia.
      * exact Hdetv.
    + rewrite Heqk. reflexivity.
    + exfalso.
      apply (r_correct_far_apart_False val r (fam_elem n r k2) (fam_elem n r k1) Hcorr).
      * rewrite !fam_elem_weight. nia.
      * symmetry. exact Hdetv.
Qed.

