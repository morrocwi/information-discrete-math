(* ===================================================================== *)
(*  IDM_FiniteWitnesses3.v — final batch of tractable axiom-free witnesses. *)
(*  Coq 8.20, Closed under the global context. Yaoharee Lahtee.             *)
(*                                                                          *)
(*   W12 no_fibonacci_integer_dim → §4.4 Cor 4.1 (d²=1+d has NO integer      *)
(*                                   solution ⇒ φ is a fusion/history        *)
(*                                   dimension, never an ordinary rep dim)   *)
(*   W13 cauchy_schwarz_2         → §16.2 (Cauchy–Schwarz over ℚ, 2-D, via    *)
(*                                   the Lagrange identity)                  *)
(*   W14 measure_additive         → §16.1 (μ_λ finitely additive: disjoint   *)
(*                                   retained counts add)                    *)
(*   W15 ring_distrib_Z           → §12.2 (ℤ ring distributivity, + and −)   *)
(*   W16 aut_is_group             → §12.1 (readout automorphisms /            *)
(*                                   bijections form a group: closed under    *)
(*                                   ∘, id, and inverse)                     *)
(* ===================================================================== *)

Require Import List ZArith QArith Lia.
Import ListNotations.

(* ---- W12  §4.4 Cor 4.1: no integer d solves d² = 1 + d (so FPdim τ = φ is  *)
(*          not an ordinary/carrier dimension — it is a fusion dimension).    *)
Open Scope Z_scope.
Theorem no_fibonacci_integer_dim : forall d : Z, d * d <> 1 + d.
Proof.
  intros d H.
  destruct (Z_lt_le_dec d 2) as [Hlt | Hge].
  - destruct (Z_lt_le_dec d 0) as [Hn | Hp]; nia.
  - nia.
Qed.

(* ---- W15  §12.2: ℤ is a ring — distributivity over both + and −.           *)
Theorem ring_distrib_Z :
  forall a b c : Z, a * (b + c) = a * b + a * c /\ a * (b - c) = a * b - a * c.
Proof. intros; split; ring. Qed.
Close Scope Z_scope.

(* ---- W13  §16.2  Cauchy–Schwarz over ℚ (2-D), from the Lagrange identity   *)
(*          (a²+b²)(c²+d²) − (ac+bd)² = (ad−bc)² ≥ 0.                          *)
Open Scope Q_scope.
Lemma Qsq_nonneg3 : forall x : Q, 0 <= x * x.
Proof.
  intro x. destruct (Qlt_le_dec x 0) as [Hlt | Hge].
  - assert (Hnx : 0 <= - x).
    { apply Qlt_le_weak. apply Qopp_lt_compat in Hlt.
      setoid_replace (- 0) with 0 in Hlt by ring. exact Hlt. }
    setoid_replace (x * x) with ((- x) * (- x)) by ring.
    apply Qmult_le_0_compat; exact Hnx.
  - apply Qmult_le_0_compat; exact Hge.
Qed.

Theorem cauchy_schwarz_2 :
  forall a b c d : Q,
    (a*c + b*d) * (a*c + b*d) <= (a*a + b*b) * (c*c + d*d).
Proof.
  intros a b c d.
  (* RHS − LHS = (a*d − b*c)² ≥ 0 *)
  apply Qle_minus_iff.
  setoid_replace ((a*a + b*b) * (c*c + d*d) + - ((a*c + b*d) * (a*c + b*d)))
    with ((a*d - b*c) * (a*d - b*c)) by ring.
  apply Qsq_nonneg3.
Qed.
Close Scope Q_scope.

(* ---- W14  §16.1  μ_λ finitely additive: the retained count of a disjoint   *)
(*          union is the sum of the counts (concatenation length).            *)
Theorem measure_additive :
  forall (X : Type) (A B : list X), length (A ++ B) = length A + length B.
Proof. intros X A B. apply length_app. Qed.

(* ---- W16  §12.1  Readout automorphisms form a group.  Model an admissible   *)
(*          automorphism as a bijection with an explicit two-sided inverse     *)
(*          (a readout-preserving relabeling). They are closed under           *)
(*          composition and inversion, with identity — the group axioms.       *)
Section AutGroup.
  Variable A : Type.
  Record Auto := { fwd : A -> A; bwd : A -> A;
                   fb : forall x, fwd (bwd x) = x;
                   bf : forall x, bwd (fwd x) = x }.

  Definition id_auto : Auto := {| fwd := fun x => x; bwd := fun x => x;
                                  fb := fun x => eq_refl; bf := fun x => eq_refl |}.

  Definition comp_auto (g f : Auto) : Auto.
  Proof.
    refine {| fwd := fun x => fwd g (fwd f x); bwd := fun x => bwd f (bwd g x) |}.
    - intro x. rewrite fb. apply fb.
    - intro x. rewrite bf. apply bf.
  Defined.

  Definition inv_auto (f : Auto) : Auto :=
    {| fwd := bwd f; bwd := fwd f; fb := bf f; bf := fb f |}.

  (* Pointwise action equality — the group laws hold on the action of each element. *)
  Definition acts_eq (f g : Auto) : Prop := forall x, fwd f x = fwd g x.

  Theorem aut_assoc : forall f g h,
    acts_eq (comp_auto (comp_auto f g) h) (comp_auto f (comp_auto g h)).
  Proof. intros f g h x; reflexivity. Qed.

  Theorem aut_id_left  : forall f, acts_eq (comp_auto id_auto f) f.
  Proof. intros f x; reflexivity. Qed.
  Theorem aut_id_right : forall f, acts_eq (comp_auto f id_auto) f.
  Proof. intros f x; reflexivity. Qed.

  Theorem aut_inv_left : forall f, acts_eq (comp_auto (inv_auto f) f) id_auto.
  Proof. intros f x; simpl. apply bf. Qed.
  Theorem aut_inv_right : forall f, acts_eq (comp_auto f (inv_auto f)) id_auto.
  Proof. intros f x; simpl. apply fb. Qed.
End AutGroup.
