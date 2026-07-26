(* ===================================================================== *)
(*  IDM_Harvest.v — pure-mathematics results harvested from readout_genesis *)
(*  and re-proved locally, axiom-free (Closed under the global context).    *)
(*  Coq 8.20. Yaoharee Lahtee.  Told in the information language:            *)
(*                                                                          *)
(*   H1 repeated_event_zero     a self-cancelling readout is null           *)
(*                              (C = −C ⇒ C = 0 over ℚ)                     *)
(*   H2 odd_from_cyclic_closure  cyclic start-independence forces k odd:     *)
(*                              (−1)^(k−1) = 1 ⇒ Nat.Odd k  (⇒ least k = 3)  *)
(*   H3 sym_skew_reconstruct     every retained operator splits into a       *)
(*                              self-adjoint (metric) part + a skew part      *)
(*                              M = ½(M+Mᵀ) + ½(M−Mᵀ)                        *)
(*   H4 skew_diag_zero           a skew operator has zero diagonal (its       *)
(*                              pointwise self-pairing carries no load)       *)
(* ===================================================================== *)

Require Import QArith ZArith Lia.
Require Import Coq.micromega.Lqa.

(* ---- H1  a self-cancelling readout is null (over ℚ) ---- *)
Open Scope Q_scope.
Theorem repeated_event_zero : forall C : Q, C == - C -> C == 0.
Proof. intros C H. lra. Qed.
Close Scope Q_scope.

(* ---- H2  cyclic start-independence forces an odd length ---- *)
(* The ordered-tape closed loop is start-independent iff the cyclic-shift sign
   (−1)^(k−1) = +1 — which is exactly the statement that k−1 is EVEN, hence k is ODD.
   The least nontrivial length k>1 is therefore 3 (⇒ the color number 3 / SU(3)). *)
Theorem odd_from_cyclic_closure :
  forall k : nat, (k >= 1)%nat -> Nat.Even (k - 1) -> Nat.Odd k.
Proof. intros k Hk [m Hm]. exists m. lia. Qed.

Theorem least_nontrivial_odd_is_three :
  forall k : nat, (k > 1)%nat -> Nat.Odd k -> (k >= 3)%nat.
Proof. intros k Hk [m Hm]. lia. Qed.

(* ---- H3/H4  the symmetric/skew split of a retained operator over ℚ ---- *)
Open Scope Q_scope.
Definition M := nat -> nat -> Q.
Definition sympart  (A : M) : M := fun i j => (1#2) * (A i j + A j i).
Definition skewpart (A : M) : M := fun i j => (1#2) * (A i j - A j i).

(* every operator reconstructs from its self-adjoint + skew parts *)
Theorem sym_skew_reconstruct :
  forall (A : M) i j, A i j == sympart A i j + skewpart A i j.
Proof. intros A i j. unfold sympart, skewpart. ring. Qed.

(* the self-adjoint part is genuinely self-adjoint (the retained metric) *)
Theorem sympart_self_adjoint :
  forall (A : M) i j, sympart A i j == sympart A j i.
Proof. intros A i j. unfold sympart. ring. Qed.

(* the skew part is antisymmetric, hence carries zero load on its diagonal:
   its pointwise self-pairing S i i vanishes — a skew operator holds no
   retained metric on any single node. *)
Theorem skew_antisym :
  forall (A : M) i j, skewpart A i j == - skewpart A j i.
Proof. intros A i j. unfold skewpart. ring. Qed.

Theorem skew_diag_zero :
  forall (A : M) i, skewpart A i i == 0.
Proof. intros A i. unfold skewpart. ring. Qed.
Close Scope Q_scope.
