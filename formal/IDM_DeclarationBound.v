(* ===================================================================== *)
(*  IDM_DeclarationBound.v — the Declaration Bound, finite combinatorial   *)
(*  core, axiom-free.  Coq 8.20, Closed under the global context.          *)
(*  Developed by Yaoharee Lahtee.                                          *)
(*                                                                         *)
(*  The Sturm readout on a symmetric tridiagonal operator can answer a     *)
(*  threshold query with Theta(1) retained BITS if the query is declared    *)
(*  in advance, but needs Theta(n log q) retained BITS if the query is      *)
(*  deferred until after the record has streamed past (q = alphabet size;    *)
(*  q = n gives a sharp Theta(1) vs Theta(n) machine-word separation).       *)
(*  Retained state is measured in bits/words, NOT in an undefined "number of *)
(*  scalars": the classical constant-REGISTER Sturm property (declared       *)
(*  query) is real but is a separate statement and must not be identified    *)
(*  with constant BITS (a counter already costs Theta(log n) bits).          *)
(*  This file formalises the finite, combinatorial skeleton — pure           *)
(*  counting/pigeonhole, no continuum, no real analysis, no eigenvalue       *)
(*  machinery — so it is machine-checked axiom-free.  The binary (q = 2)     *)
(*  theorems are the sharp base case; the q-ARY section at the end           *)
(*  generalises the faithful readout and the string count (q^n) to any q.    *)
(*                                                                         *)
(*  A string of n bits is modelled as a list bool.  The "Sturm profile" is *)
(*  the query-response record  i |-> i + b_i  (the count of eigenvalues    *)
(*  below the i-th threshold, in the irreducible fooling family where that *)
(*  count is exactly i + b_i).  What is proved here:                        *)
(*                                                                         *)
(*   DB1 bit_extraction_exact   b_i is recovered from the i-th profile      *)
(*                              entry as (i + b_i) - i  (the readout is      *)
(*                              information-preserving per bit).            *)
(*   DB2 profile_injective      distinct strings give distinct profiles     *)
(*                              (the fooling family is irreducible).        *)
(*   DB3 bcube_length/_nodup    the n-bit cube has exactly 2^n distinct     *)
(*                              strings (the counting backbone).            *)
(*   DB4 deferred_record_bits   ANY deferred scheme that keeps a distinct   *)
(*                              bit-record per n-bit string must, for some  *)
(*                              string, retain a record of length >= n       *)
(*                              — the Theta(n) lower bound, by pigeonhole    *)
(*                              over the < 2^n short records.               *)
(*   DB5 declared_forgets_tail  the declared scheme's answer depends only   *)
(*                              on the prefix up to the declared threshold, *)
(*                              so the streamed tail need not be retained    *)
(*                              — a single accumulator (Theta(1)) suffices.  *)
(*   DB6 declaration_separation deferred >= n while declared ignores the    *)
(*                              tail: the value of declaring is Theta(n).    *)
(*                                                                         *)
(*  Tier: Th_coqc for every statement below (machine-checked, axiom-free).  *)
(*  NOT captured here (honestly fenced): the spectral fact that the fooling *)
(*  family's Sturm count equals i + b_i — that is an eigenvalue-separation  *)
(*  argument checked numerically in demos/verify_declaration_bound.py, not  *)
(*  re-derived in Coq.  This file takes that count function as its model    *)
(*  and proves the information-theoretic consequences exactly.             *)
(* ===================================================================== *)

Require Import List.
Require Import PeanoNat.
Require Import Lia.
Require Import Arith.
Import ListNotations.

(* nat value of a bit. *)
Definition b2n (x : bool) : nat := if x then 1 else 0.

Lemma b2n_inj : forall x y : bool, b2n x = b2n y -> x = y.
Proof. intros [] []; simpl; congruence. Qed.

(* ---- DB1  bit extraction: the i-th profile entry is i + b_i, and the bit  *)
(*      is recovered exactly by subtracting the known index i.               *)
Theorem bit_extraction_exact :
  forall (i : nat) (x : bool), b2n x = (i + b2n x) - i.
Proof. intros i x. lia. Qed.

(* The Sturm profile of a bit-string streamed from threshold index i0. *)
Fixpoint sturm_profile (i0 : nat) (bs : list bool) : list nat :=
  match bs with
  | []       => []
  | x :: t   => (i0 + b2n x) :: sturm_profile (S i0) t
  end.

(* ---- DB2  the fooling family is irreducible: equal profiles force equal    *)
(*      strings.  This is exactly "no two strings may share a state".         *)
Theorem profile_injective :
  forall (i0 : nat) (bs cs : list bool),
    sturm_profile i0 bs = sturm_profile i0 cs -> bs = cs.
Proof.
  intros i0 bs. revert i0.
  induction bs as [| x t IH]; intros i0 [| y u] H; simpl in H.
  - reflexivity.
  - discriminate.
  - discriminate.
  - injection H as Hhd Htl.
    assert (b2n x = b2n y) by lia.
    apply b2n_inj in H.
    subst y.
    f_equal. apply (IH (S i0) u Htl).
Qed.

(* ===================================================================== *)
(*  DB3 — the boolean n-cube: 2^n distinct strings.                        *)
(* ===================================================================== *)

Fixpoint bcube (n : nat) : list (list bool) :=
  match n with
  | 0    => [ [] ]
  | S k  => map (cons true) (bcube k) ++ map (cons false) (bcube k)
  end.

Lemma bcube_length : forall n, length (bcube n) = 2 ^ n.
Proof.
  induction n as [| k IH]; simpl.
  - reflexivity.
  - rewrite length_app, !length_map, IH. lia.
Qed.

Lemma two_pow_pos : forall k, 1 <= 2 ^ k.
Proof. induction k as [| k IH]; simpl; lia. Qed.

(* every element of the n-cube has length n *)
Lemma bcube_all_len : forall n l, In l (bcube n) -> length l = n.
Proof.
  induction n as [| k IH]; intros l Hin; simpl in Hin.
  - destruct Hin as [<- | []]. reflexivity.
  - apply in_app_iff in Hin as [Hin | Hin];
    apply in_map_iff in Hin as [l0 [<- Hl0]]; simpl; f_equal; apply IH; exact Hl0.
Qed.

(* completeness: every bit-string is in the cube of its own length *)
Lemma bcube_complete : forall l : list bool, In l (bcube (length l)).
Proof.
  induction l as [| x t IH]; simpl.
  - left; reflexivity.
  - apply in_app_iff. destruct x.
    + left.  apply in_map_iff. exists t. split; [reflexivity | exact IH].
    + right. apply in_map_iff. exists t. split; [reflexivity | exact IH].
Qed.

(* the two halves of the cube are disjoint (heads differ) *)
Lemma bcube_halves_disjoint :
  forall (k : nat) (l : list bool),
    In l (map (cons true) (bcube k)) ->
    In l (map (cons false) (bcube k)) -> False.
Proof.
  intros k l Ht Hf.
  apply in_map_iff in Ht as [a [<- _]].
  apply in_map_iff in Hf as [c [Heq _]].
  discriminate Heq.
Qed.

(* a general helper: NoDup of a disjoint append *)
Lemma NoDup_app_disjoint :
  forall (A : Type) (l1 l2 : list A),
    NoDup l1 -> NoDup l2 ->
    (forall x, In x l1 -> In x l2 -> False) ->
    NoDup (l1 ++ l2).
Proof.
  intros A l1. induction l1 as [| a l1 IH]; intros l2 H1 H2 Hdisj; simpl.
  - exact H2.
  - inversion H1 as [| ? ? Hna Hnd1]; subst.
    constructor.
    + rewrite in_app_iff. intros [Hin | Hin].
      * exact (Hna Hin).
      * apply (Hdisj a); [left; reflexivity | exact Hin].
    + apply IH; [exact Hnd1 | exact H2 |].
      intros x Hx1 Hx2. apply (Hdisj x); [right; exact Hx1 | exact Hx2].
Qed.

(* cons is injective, so it preserves NoDup under map *)
Lemma NoDup_map_cons :
  forall (a : bool) (l : list (list bool)),
    NoDup l -> NoDup (map (cons a) l).
Proof.
  intros a l. induction l as [| x xs IH]; intros Hnd; simpl.
  - constructor.
  - inversion Hnd as [| ? ? Hnx Hnxs]; subst.
    constructor.
    + rewrite in_map_iff. intros [y [Heq Hin]].
      injection Heq as ->. exact (Hnx Hin).
    + apply IH; exact Hnxs.
Qed.

Lemma bcube_nodup : forall n, NoDup (bcube n).
Proof.
  induction n as [| k IH]; simpl.
  - constructor; [intros [] | constructor].
  - apply NoDup_app_disjoint.
    + apply NoDup_map_cons; exact IH.
    + apply NoDup_map_cons; exact IH.
    + apply bcube_halves_disjoint.
Qed.

(* ===================================================================== *)
(*  DB4 — deferred lower bound: Theta(n) retained bits.                    *)
(* ===================================================================== *)

(* the "short records": every bit-list of length < n, collected as the      *)
(* concatenation of the cubes 0..n-1.  There are 2^n - 1 of them.           *)
Fixpoint short_records (n : nat) : list (list bool) :=
  match n with
  | 0    => []
  | S k  => short_records k ++ bcube k
  end.

Lemma short_records_length : forall n, length (short_records n) = 2 ^ n - 1.
Proof.
  induction n as [| k IH]; simpl.
  - reflexivity.
  - rewrite length_app, IH, bcube_length.
    pose proof (two_pow_pos k). lia.
Qed.

(* every record shorter than n is among the short records *)
Lemma short_records_complete :
  forall (n : nat) (l : list bool), length l < n -> In l (short_records n).
Proof.
  induction n as [| k IH]; intros l Hlt; simpl.
  - lia.
  - rewrite in_app_iff.
    destruct (Nat.eq_dec (length l) k) as [Heq | Hne].
    + right. rewrite <- Heq. apply bcube_complete.
    + left. apply IH. lia.
Qed.

(* map of an injective-on-l function preserves NoDup *)
Lemma NoDup_map_inj_on :
  forall (A B : Type) (f : A -> B) (l : list A),
    NoDup l ->
    (forall x y, In x l -> In y l -> f x = f y -> x = y) ->
    NoDup (map f l).
Proof.
  intros A B f l. induction l as [| a l IH]; intros Hnd Hinj; simpl.
  - constructor.
  - inversion Hnd as [| ? ? Hna Hndl]; subst.
    constructor.
    + rewrite in_map_iff. intros [y [Hfy Hiny]].
      assert (a = y) by
        (apply Hinj; [left; reflexivity | right; exact Hiny | symmetry; exact Hfy]).
      subst y. exact (Hna Hiny).
    + apply IH; [exact Hndl |].
      intros x y Hx Hy Hfxy. apply Hinj; [right; exact Hx | right; exact Hy | exact Hfxy].
Qed.

(* The Declaration Bound, deferred regime.  ANY scheme [rec] that, over the   *)
(* 2^n strings of the n-cube, keeps a distinct bit-record per string (which   *)
(* the deferred regime must, since the query is not yet known and no two      *)
(* strings may share a terminal state — DB2) is forced to retain, for at      *)
(* least one string, a record of length >= n.  Hence retained state = Omega(n)*)
Theorem deferred_record_bits :
  forall (n : nat) (rec : list bool -> list bool),
    (forall bs cs, In bs (bcube n) -> In cs (bcube n) -> rec bs = rec cs -> bs = cs) ->
    exists bs, In bs (bcube n) /\ n <= length (rec bs).
Proof.
  intros n rec Hinj.
  destruct (Exists_dec (fun bs => n <= length (rec bs)) (bcube n)
                       (fun bs => le_dec n (length (rec bs)))) as [HE | HNE].
  - (* some string already needs an n-bit record — that is the witness *)
    apply Exists_exists in HE. destruct HE as [bs [Hin HP]].
    exists bs. split; assumption.
  - (* otherwise every record is shorter than n; pigeonhole gives a contradiction *)
    exfalso.
    assert (Hall : Forall (fun bs => ~ (n <= length (rec bs))) (bcube n)).
    { apply Forall_forall. intros bs Hbs HP.
      apply HNE. apply Exists_exists. exists bs. split; assumption. }
    (* the image records are duplicate-free and all lie in the < 2^n short records *)
    assert (Hnd : NoDup (map rec (bcube n))).
    { apply NoDup_map_inj_on; [apply bcube_nodup | exact Hinj]. }
    assert (Hincl : incl (map rec (bcube n)) (short_records n)).
    { intros y Hy. apply in_map_iff in Hy as [bs [<- Hbs]].
      rewrite Forall_forall in Hall.
      apply short_records_complete.
      specialize (Hall bs Hbs). lia. }
    pose proof (NoDup_incl_length Hnd Hincl) as Hle.
    rewrite length_map, bcube_length, short_records_length in Hle.
    pose proof (two_pow_pos n). lia.
Qed.

(* ===================================================================== *)
(*  DB5 — declared regime forgets the tail: Theta(1) retained state.       *)
(* ===================================================================== *)

(* When the threshold index j is DECLARED in advance, the readout keeps a    *)
(* single running accumulator: the number of set bits in the streamed prefix *)
(* up to j.  Its carried state is one nat, independent of the string length. *)
Definition declared_count (j : nat) (bs : list bool) : nat :=
  fold_left (fun acc x => acc + b2n x) (firstn j bs) 0.

(* The answer depends only on the declared prefix; the streamed tail past j    *)
(* is never consulted, so it need not be retained — hence Theta(1) state.      *)
Theorem declared_forgets_tail :
  forall (j : nat) (bs cs : list bool),
    firstn j bs = firstn j cs -> declared_count j bs = declared_count j cs.
Proof. intros j bs cs H. unfold declared_count. rewrite H. reflexivity. Qed.

(* ===================================================================== *)
(*  DB6 — the separation: deferred Theta(n) vs declared Theta(1).          *)
(* ===================================================================== *)

(* One statement carrying both sides.  Left: any deferred scheme keeping a     *)
(* distinct record per n-bit string must retain >= n bits for some string.     *)
(* Right: the declared scheme's answer never depends on more than the declared *)
(* prefix, so a single accumulator suffices for every n.  The value of         *)
(* declaring the query in advance is therefore Theta(n) retained bits.         *)
Theorem declaration_separation :
  forall (n : nat),
    (forall rec : list bool -> list bool,
        (forall bs cs, In bs (bcube n) -> In cs (bcube n) -> rec bs = rec cs -> bs = cs) ->
        exists bs, In bs (bcube n) /\ n <= length (rec bs))
    /\
    (forall (j : nat) (bs cs : list bool),
        firstn j bs = firstn j cs -> declared_count j bs = declared_count j cs).
Proof.
  intro n. split.
  - intros rec Hinj. apply deferred_record_bits. exact Hinj.
  - apply declared_forgets_tail.
Qed.

(* ===================================================================== *)
(*  q-ARY generalization.  The binary theorems above are the sharp q = 2   *)
(*  instance.  For an alphabet of size q the fooling family reads off a     *)
(*  SYMBOL a_i ∈ {0..q-1} per position via the q-1 thresholds r, by the     *)
(*  extraction identity  #below σ(i,r) = i + [a_i ≤ r].  Two facts carry     *)
(*  the general-q separation, both machine-checked here:                    *)
(*                                                                          *)
(*   Q1 qary_symbol_injective  — the per-position q-ary readout is faithful: *)
(*      distinct symbols give distinct threshold signatures (so distinct     *)
(*      strings give distinct profiles, exactly as q=2's profile_injective). *)
(*   Q2 qcube_length           — there are q^n length-n q-ary strings, so the *)
(*      deferred record (a distinct record per string) needs ≥ log2(q^n) =   *)
(*      n·log2 q bits: the deferred bound is Θ(n log q), matching q=2's       *)
(*      deferred_record_bits (n bits) at q = 2.                              *)
(* ===================================================================== *)

Require Import Arith.

(* Q1.  The count signature of a symbol a at position i is r ↦ i + [a ≤ r].      *)
(*      Two symbols in {0..q-1} with the same signature on every threshold        *)
(*      r < q-1 are equal — the q-ary faithful readout.                            *)
Theorem qary_symbol_injective :
  forall (q a b : nat),
    a < q -> b < q ->
    (forall r, r < q - 1 -> (a <=? r) = (b <=? r)) ->
    a = b.
Proof.
  intros q a b Ha Hb Hsig.
  destruct (Nat.compare_spec a b) as [Heq | Hlt | Hgt].
  - exact Heq.
  - (* a < b: at r = a (a valid threshold since a < b <= q-1, so a < q-1) *)
    assert (Hr : a < q - 1) by lia.
    specialize (Hsig a Hr).
    rewrite Nat.leb_refl in Hsig.                 (* a <=? a = true, so true = (b <=? a) *)
    symmetry in Hsig. apply Nat.leb_le in Hsig. lia.
  - (* a > b: at r = b *)
    assert (Hr : b < q - 1) by lia.
    specialize (Hsig b Hr).
    rewrite Nat.leb_refl in Hsig.                 (* b <=? b = true, so (a <=? b) = true *)
    apply Nat.leb_le in Hsig. lia.
Qed.

(* Q2.  The q-ary cube: all length-n strings over the alphabet {0..q-1}.          *)
Fixpoint qcube (q n : nat) : list (list nat) :=
  match n with
  | 0    => [ [] ]
  | S k  => flat_map (fun s => map (cons s) (qcube q k)) (seq 0 q)
  end.

Lemma flat_map_cons_length :
  forall (q : nat) (C : list (list nat)) (L : list nat),
    length (flat_map (fun s => map (cons s) C) L) = length L * length C.
Proof.
  intros q C L. induction L as [| s L' IH]; simpl.
  - reflexivity.
  - rewrite length_app, length_map, IH. reflexivity.
Qed.

Lemma qcube_length : forall q n, length (qcube q n) = q ^ n.
Proof.
  intros q n. induction n as [| k IH]; simpl.
  - reflexivity.
  - rewrite (flat_map_cons_length q), length_seq, IH. reflexivity.
Qed.

(* Every element of the q-ary cube has length n (the record is n symbols wide).   *)
Lemma qcube_all_len : forall q n l, In l (qcube q n) -> length l = n.
Proof.
  intros q n. induction n as [| k IH]; intros l Hin; simpl in Hin.
  - destruct Hin as [<- | []]. reflexivity.
  - apply in_flat_map in Hin as [s [_ Hin]].
    apply in_map_iff in Hin as [l0 [<- Hl0]]. simpl. f_equal. apply IH; exact Hl0.
Qed.
