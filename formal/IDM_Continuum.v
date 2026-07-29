(* IDM_Continuum.v — the ℚ-algebra laws behind idm.continuum: the continuum as a first-class ℚ PRIMITIVE.

   A continuum value is carried as a resolution-indexed exact-ℚ readout g : nat -> Q (never an ℝ object).
   idm/continuum.py combines such readouts pointwise (a+b at N = a.at N + b.at N, etc.). This file
   machine-checks, axiom-free over ℚ, that this makes the readouts a sound algebra you can compute with —
   in particular that combining two PLATEAUING readouts still plateaus, so `.readout(ε)` stays honest
   under the algebra:

     - radd_at / rmul_at    : the combinators are the pointwise ℚ operations (homomorphism into ℚ at each N)
     - radd_comm            : the readout sum is commutative (representative ring law)
     - const_gap_zero       : a constant readout has zero successive gap (it trivially plateaus)
     - gap_subadditive      : |Δ(g+h)(N)| ≤ |Δg(N)| + |Δh(N)|  — THE soundness law: the A8 gap of a sum is
                              bounded by the sum of gaps, so adding two plateauing continua yields a
                              plateauing continuum (its `.readout(ε)` cannot silently diverge).

   Founder principle (2026-07-29): if the ℝ-rung is computable, it is computable on ℚ — here the whole
   continuum-LIKE object is a ℚ primitive, and its algebra is a machine-checked ℚ theorem, not a stance. *)

Require Import QArith.
Require Import Qabs.

Open Scope Q_scope.

(* A readout is just a resolution-indexed rational. The combinators are pointwise. *)
Definition readout := nat -> Q.

Definition radd (g h : readout) : readout := fun n => g n + h n.
Definition rmul (g h : readout) : readout := fun n => g n * h n.
Definition rconst (q : Q) : readout := fun _ => q.

(* successive gap at resolution n: |g(n+1) - g(n)| — the quantity .readout(ε) drives below ε. *)
Definition gap (g : readout) (n : nat) : Q := Qabs (g (S n) - g n).

(* (1) The combinators ARE the pointwise ℚ operations — homomorphism into ℚ at each resolution. *)
Theorem radd_at : forall g h n, radd g h n = g n + h n.
Proof. reflexivity. Qed.

Theorem rmul_at : forall g h n, rmul g h n = g n * h n.
Proof. reflexivity. Qed.

(* (2) A representative ring law: the readout sum is commutative (pointwise over ℚ). *)
Theorem radd_comm : forall g h n, radd g h n == radd h g n.
Proof. intros g h n. unfold radd. ring. Qed.

(* (3) A constant readout never changes — zero gap — so it trivially plateaus to any ε > 0. *)
Theorem const_gap_zero : forall q n, gap (rconst q) n == 0.
Proof.
  intros q n. unfold gap, rconst.
  setoid_replace (q - q) with 0 by ring.
  reflexivity.
Qed.

(* (4) THE soundness law of the algebra: the gap of a sum is sub-additive. Hence combining two
   plateauing continua (each gap eventually ≤ ε/2) yields a continuum that also plateaus (gap ≤ ε):
   the ℚ-algebra cannot turn two honest readouts into a silently divergent one. *)
Theorem gap_subadditive :
  forall g h n, gap (radd g h) n <= gap g n + gap h n.
Proof.
  intros g h n. unfold gap, radd.
  setoid_replace (g (S n) + h (S n) - (g n + h n))
    with ((g (S n) - g n) + (h (S n) - h n)) by ring.
  apply Qabs_triangle.
Qed.
