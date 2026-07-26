(* ===================================================================== *)
(*  IDM_Hilbert.v — the finite-dimensional Hilbert-space laws, machine-checked. *)
(*  Coq 8.20, axiom-free (Closed under the global context). Yaoharee Lahtee. *)
(*                                                                          *)
(*  The exact/decidable core of idm.hilbert, over a FIXED FINITE n, entries  *)
(*  in ℚ (the real case; the ℚ[i] case is the same proof shape on ℚ×ℚ      *)
(*  pairs). NO completeness, NO ℓ²/L², NO algebraic closure of ℂ / FTA, NO   *)
(*  infinite-dimensional object is quantified anywhere — those are +ℝ-Open   *)
(*  (idm.hilbert_open) and are deliberately absent here (the +ℝ fence).      *)
(*                                                                          *)
(*   inner_sym / inner_linear_l / inner_pos     inner product = sesquilinear, PSD *)
(*   parallelogram_law / pythagoras_orthogonal  the two identities            *)
(*   cauchy_schwarz_2                            |⟨u,v⟩|² ≤ ⟨u,u⟩⟨v,v⟩ (n=2)    *)
(*   adjoint_involutive / adjoint_of_product     adjoint: involution + antihomomorphism *)
(*   hermitian_2x2_discriminant_nonneg           a symmetric 2×2 has real spectrum *)
(*   hermitian_2x2_gap_is_discriminant           (λ₁−λ₂)² = discriminant (Vieta) *)
(*   projection_idempotent / projection_self_adjoint                          *)
(* ===================================================================== *)

Require Import QArith Lqa.
Require Import IDM_Matrix.
Open Scope Q_scope.

Definition Vec := nat -> Q.
Definition inner (n : nat) (u v : Vec) : Q := Sum n (fun k => u k * v k).

(* ---- a robust square-nonneg fact (no nonlinear-arith witness search) ---- *)
Lemma Qsq_nonneg : forall x : Q, 0 <= x * x.
Proof.
  intro x. destruct (Qlt_le_dec x 0) as [H | H].
  - setoid_replace (x * x) with ((- x) * (- x)) by ring.
    apply Qmult_le_0_compat; lra.
  - apply Qmult_le_0_compat; lra.
Qed.

(* ---- finite-sum helpers ---- *)
Lemma Sum_scale : forall n c f, Sum n (fun k => c * f k) == c * Sum n f.
Proof. induction n; intros; simpl; [ ring | rewrite IHn; ring ]. Qed.

Lemma Sum_nonneg : forall n f, (forall k, 0 <= f k) -> 0 <= Sum n f.
Proof.
  induction n; intros f H; simpl.
  - lra.
  - specialize (IHn f H). specialize (H n). lra.
Qed.

(* ---- inner product: sesquilinear (real: symmetric + linear) and positive ---- *)
Theorem inner_sym : forall n u v, inner n u v == inner n v u.
Proof. intros; unfold inner; apply Sum_ext; intro k; ring. Qed.

Theorem inner_linear_l : forall n c u1 u2 v,
  inner n (fun k => c * u1 k + u2 k) v == c * inner n u1 v + inner n u2 v.
Proof.
  intros n c u1 u2 v. unfold inner.
  rewrite (Sum_ext n (fun k => (c * u1 k + u2 k) * v k)
                     (fun k => c * (u1 k * v k) + u2 k * v k)) by (intro; ring).
  rewrite Sum_plus, Sum_scale. reflexivity.
Qed.

Theorem inner_pos : forall n v, 0 <= inner n v v.
Proof. intros n v. unfold inner. apply Sum_nonneg. intro k. apply Qsq_nonneg. Qed.

(* ---- the two Hilbert identities ---- *)
Theorem parallelogram_law : forall n u v,
  inner n (fun k => u k + v k) (fun k => u k + v k)
  + inner n (fun k => u k - v k) (fun k => u k - v k)
  == 2 * inner n u u + 2 * inner n v v.
Proof.
  intros n u v. unfold inner.
  rewrite <- Sum_plus.
  rewrite (Sum_ext n (fun k => (u k + v k) * (u k + v k) + (u k - v k) * (u k - v k))
                     (fun k => 2 * (u k * u k) + 2 * (v k * v k))) by (intro; ring).
  rewrite Sum_plus, Sum_scale, Sum_scale. reflexivity.
Qed.

Theorem pythagoras_orthogonal : forall n u v,
  inner n u v == 0 ->
  inner n (fun k => u k + v k) (fun k => u k + v k) == inner n u u + inner n v v.
Proof.
  intros n u v Horth. unfold inner in *.
  rewrite (Sum_ext n (fun k => (u k + v k) * (u k + v k))
                     (fun k => (u k * u k + v k * v k) + 2 * (u k * v k))) by (intro; ring).
  rewrite Sum_plus, Sum_plus, Sum_scale, Horth. ring.
Qed.

(* ---- Cauchy–Schwarz, n=2 (the Lagrange-identity square witness, entirely ℚ) ---- *)
Theorem cauchy_schwarz_2 : forall u1 u2 v1 v2 : Q,
  (u1 * v1 + u2 * v2) * (u1 * v1 + u2 * v2)
  <= (u1 * u1 + u2 * u2) * (v1 * v1 + v2 * v2).
Proof.
  intros u1 u2 v1 v2.
  assert (E : (u1 * u1 + u2 * u2) * (v1 * v1 + v2 * v2)
              == (u1 * v1 + u2 * v2) * (u1 * v1 + u2 * v2)
                 + (u1 * v2 - u2 * v1) * (u1 * v2 - u2 * v1)) by ring.
  rewrite E. pose proof (Qsq_nonneg (u1 * v2 - u2 * v1)) as Hsq. lra.
Qed.

(* ---- adjoint (real case = transpose): reuse the proven matrix facts ---- *)
Definition adjoint (A : Mat) : Mat := transpose A.

Theorem adjoint_involutive : forall n A, meq n (adjoint (adjoint A)) A.
Proof. intros; apply transpose_involutive. Qed.

Theorem adjoint_of_product : forall n A B,
  meq n (adjoint (mmul n A B)) (mmul n (adjoint B) (adjoint A)).
Proof. intros; apply transpose_mmul. Qed.

(* ---- Hermitian 2×2: real spectrum (nonneg discriminant) + the Vieta gap identity ---- *)
Theorem hermitian_2x2_discriminant_nonneg : forall a b c : Q,
  0 <= (a - c) * (a - c) + 4 * (b * b).
Proof.
  intros a b c. pose proof (Qsq_nonneg (a - c)) as H1. pose proof (Qsq_nonneg b) as H2. lra.
Qed.

Theorem hermitian_2x2_gap_is_discriminant : forall a b c lam1 lam2 : Q,
  lam1 + lam2 == a + c ->
  lam1 * lam2 == a * c - b * b ->
  (lam1 - lam2) * (lam1 - lam2) == (a - c) * (a - c) + 4 * (b * b).
Proof.
  intros a b c lam1 lam2 Hs Hp.
  setoid_replace ((lam1 - lam2) * (lam1 - lam2))
    with ((lam1 + lam2) * (lam1 + lam2) - 4 * (lam1 * lam2)) by ring.
  rewrite Hs, Hp. ring.
Qed.

(* ---- projection: idempotent and self-adjoint, straight from the definition ---- *)
Definition is_projection (n : nat) (P : Mat) : Prop :=
  meq n (mmul n P P) P /\ meq n (transpose P) P.

Theorem projection_idempotent : forall n P, is_projection n P -> meq n (mmul n P P) P.
Proof. intros n P [H1 _]; exact H1. Qed.

Theorem projection_self_adjoint : forall n P, is_projection n P -> meq n (adjoint P) P.
Proof. intros n P [_ H2]; exact H2. Qed.
