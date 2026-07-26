(* ===================================================================== *)
(*  IDM_FiniteWitnesses2.v — second batch of axiom-free witnesses          *)
(*  (cardinality §10.2, Lagrange §12.3). Coq 8.20, Closed under the global  *)
(*  context. Developed by Yaoharee Lahtee.                                  *)
(*                                                                          *)
(*   W6 no_infinite_readout   → §10.2 Th 10.5 (every readout list is finite)*)
(*   W7 tape_count_succ       → §10.2 Th 10.4 (a σ-generated tape strictly   *)
(*                                     grows ⇒ no terminal stage)            *)
(*   W8 same_set_same_size    → §10.2 Th 10.3 (equinumerosity = admissible   *)
(*                                     bijection: NoDup + same members ⇒     *)
(*                                     equal count)                          *)
(*   W9 lagrange_order_div    → §12.3   (element order n/gcd divides the      *)
(*                                     group order n in ℤ_n)                  *)
(* ===================================================================== *)

Require Import List.
Require Import PeanoNat.
Require Import Lia.
Import ListNotations.

(* ---- W6  Th 10.5: every readout inhabits list A, which has no infinite    *)
(*         inhabitant — the actual infinite is excluded by the type, not fiat.*)
Theorem no_infinite_readout :
  forall (A : Type) (l : list A), exists n : nat, length l = n.
Proof. intros A l. exists (length l). reflexivity. Qed.

(* ---- W7  Th 10.4: a distinction-generated tape Tape(n) with count n+1     *)
(*         strictly grows, so no stage is terminal (unbounded process, no    *)
(*         completed object).                                                 *)
Definition tape_count (n : nat) : nat := S n.
Theorem tape_count_succ :
  forall n : nat, tape_count n < tape_count (S n).
Proof. intro n. unfold tape_count. lia. Qed.
Corollary tape_no_terminal :
  forall n : nat, exists m, tape_count n < tape_count m.
Proof. intro n. exists (S n). apply tape_count_succ. Qed.

(* ---- W8  Th 10.3: "same size" = an admissible bijection. For duplicate-   *)
(*         free readouts, having the same members forces equal counts.        *)
Theorem same_set_same_size :
  forall (A : Type) (eqA : forall x y : A, {x = y} + {x <> y}) (l l' : list A),
    NoDup l -> NoDup l' ->
    (forall x, In x l <-> In x l') ->
    length l = length l'.
Proof.
  intros A eqA l l' Hnd Hnd' Hiff.
  assert (Hincl  : incl l l')  by (intros x Hx; apply Hiff; exact Hx).
  assert (Hincl' : incl l' l)  by (intros x Hx; apply Hiff; exact Hx).
  apply NoDup_incl_length in Hincl;  [| exact Hnd].
  apply NoDup_incl_length in Hincl'; [| exact Hnd'].
  lia.
Qed.

(* ---- W9  §12.3 Lagrange (cyclic case): in ℤ_n the order of g is           *)
(*         n / gcd(g,n), and it divides the group order n.                    *)
Theorem lagrange_order_div :
  forall g n : nat, 0 < n -> Nat.divide (n / Nat.gcd g n) n.
Proof.
  intros g n Hn.
  set (d := Nat.gcd g n).
  assert (Hd : Nat.divide d n) by apply Nat.gcd_divide_r.
  assert (Hdpos : 0 < d).
  { destruct (Nat.eq_dec d 0) as [H0|]; [| lia].
    apply Nat.gcd_eq_0 in H0. destruct H0. lia. }
  destruct Hd as [k Hk].                 (* n = k * d *)
  assert (Hnd : n / d = k).
  { rewrite Hk. apply Nat.div_mul. lia. }
  rewrite Hnd. exists d. lia.            (* goal n = d * k, from Hk : n = k * d *)
Qed.
