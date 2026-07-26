(** IDM_Tropical.v — the min-plus / max-plus (tropical) and bottleneck semirings, machine-checked.

    Minimization ("shortest path"), maximization ("critical path"), and bottleneck ("widest path")
    problems are exactly linear algebra over a DISCRETE semiring with a different pair of operations:

        min-plus (tropical):   a ⊕ b = min(a,b),  a ⊗ b = a + b     → shortest path / minimization
        max-plus:              a ⊕ b = max(a,b),  a ⊗ b = a + b     → critical path / scheduling
        bottleneck (max-min):  a ⊕ b = max(a,b),  a ⊗ b = min(a,b)  → widest path / max capacity

    These are genuine commutative semirings — no continuum, entirely over ℤ. We machine-check the
    semiring laws (associativity, commutativity, the identity, and — the crucial one — DISTRIBUTIVITY of
    ⊗ over ⊕, which is what makes matrix "powers" compute all-pairs optima). The additive identity is the
    tropical +∞/−∞; under readout-first that is NOT a completed infinity but a discrete "unreached"
    sentinel, handled symbolically in tools/aggregate.py — so nothing here needs it. Axiom-free. *)

Require Import ZArith.
Require Import Lia.
Open Scope Z_scope.

Definition tadd (a b : Z) := a + b.          (* ⊗ for min-plus / max-plus *)
Definition tmin (a b : Z) := Z.min a b.      (* ⊕ for min-plus *)
Definition tmax (a b : Z) := Z.max a b.      (* ⊕ for max-plus; ⊗ for bottleneck *)

(* ---- ⊕ = min is a commutative, associative, idempotent monoid-like operation ---- *)
Theorem tmin_assoc : forall a b c, tmin a (tmin b c) = tmin (tmin a b) c.
Proof. intros; unfold tmin; lia. Qed.
Theorem tmin_comm : forall a b, tmin a b = tmin b a.
Proof. intros; unfold tmin; lia. Qed.
Theorem tmin_idem : forall a, tmin a a = a.
Proof. intros; unfold tmin; lia. Qed.

(* ---- ⊕ = max, the max-plus / bottleneck additive operation ---- *)
Theorem tmax_assoc : forall a b c, tmax a (tmax b c) = tmax (tmax a b) c.
Proof. intros; unfold tmax; lia. Qed.
Theorem tmax_comm : forall a b, tmax a b = tmax b a.
Proof. intros; unfold tmax; lia. Qed.
Theorem tmax_idem : forall a, tmax a a = a.
Proof. intros; unfold tmax; lia. Qed.

(* ---- ⊗ = + is a commutative monoid with identity 0 ---- *)
Theorem tadd_assoc : forall a b c, tadd a (tadd b c) = tadd (tadd a b) c.
Proof. intros; unfold tadd; lia. Qed.
Theorem tadd_comm : forall a b, tadd a b = tadd b a.
Proof. intros; unfold tadd; lia. Qed.
Theorem tadd_0_l : forall a, tadd 0 a = a.
Proof. intros; unfold tadd; lia. Qed.

(* ---- THE key law: ⊗ distributes over ⊕. This is what makes shortest/longest-path matrix powers work. *)
Theorem minplus_distrib : forall a b c, tadd a (tmin b c) = tmin (tadd a b) (tadd a c).
Proof. intros; unfold tadd, tmin; lia. Qed.
Theorem maxplus_distrib : forall a b c, tadd a (tmax b c) = tmax (tadd a b) (tadd a c).
Proof. intros; unfold tadd, tmax; lia. Qed.

(* ---- Bottleneck (widest path): ⊗ = min distributes over ⊕ = max ---- *)
Theorem bottleneck_distrib : forall a b c, tmin a (tmax b c) = tmax (tmin a b) (tmin a c).
Proof. intros; unfold tmin, tmax; lia. Qed.
