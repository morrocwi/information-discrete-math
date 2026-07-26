(* ===================================================================== *)
(*  IDM_Matrix.v — a small discrete matrix library over ℚ, from scratch,    *)
(*  closing the finite-ℚ matrix facts of Parts XIII / XV / XVI.            *)
(*  Coq 8.20, axiom-free (Closed under the global context). Yaoharee Lahtee. *)
(*                                                                          *)
(*  Matrices are entry functions `nat -> nat -> Q` with an explicit         *)
(*  dimension `n`; equality is pointwise on [0,n). Finite sums `Sum n f`.    *)
(*                                                                          *)
(*   madd_comm / madd_assoc     matrix addition is a commutative monoid     *)
(*   transpose_involutive        (Aᵀ)ᵀ = A                                  *)
(*   transpose_mmul              (A·B)ᵀ = Bᵀ·Aᵀ                              *)
(*   mid_left                    I·A = A                                     *)
(*   laplacian_symmetric         L_R = L_Rᵀ  (self-adjoint)                 *)
(*   laplacian_rowsum_zero       Σ_j L_R[i,j] = 0                           *)
(*   laplacian_ones_in_kernel    (L_R · 1)[i] = 0  (constants ∈ ker L_R —    *)
(*                                 the connectivity kernel of §15.2)         *)
(* ===================================================================== *)

Require Import QArith Lia.
Open Scope Q_scope.

(* ---- finite sum  Σ_{k=0}^{n-1} f k  and its algebra ---- *)
Fixpoint Sum (n : nat) (f : nat -> Q) : Q :=
  match n with O => 0 | S k => Sum k f + f k end.

Lemma Sum_plus : forall n f g, Sum n (fun k => f k + g k) == Sum n f + Sum n g.
Proof. induction n; intros; simpl; [ ring | rewrite IHn; ring ]. Qed.

Lemma Sum_opp : forall n f, Sum n (fun k => - f k) == - Sum n f.
Proof. induction n; intros; simpl; [ ring | rewrite IHn; ring ]. Qed.

Lemma Sum_zero : forall n, Sum n (fun _ => 0) == 0.
Proof. induction n; simpl; [ reflexivity | rewrite IHn; ring ]. Qed.

Lemma Sum_ext : forall n f g, (forall k, f k == g k) -> Sum n f == Sum n g.
Proof. induction n; intros f g H; simpl; [ reflexivity | rewrite (IHn f g H), H; reflexivity ]. Qed.

(* bounded extensionality: agreement on [0,n) suffices *)
Lemma Sum_ext_lt : forall n f g, (forall k, (k < n)%nat -> f k == g k) -> Sum n f == Sum n g.
Proof.
  induction n as [| m IH]; intros f g H; simpl.
  - reflexivity.
  - rewrite (IH f g); [ rewrite (H m) by lia; reflexivity | intros k Hk; apply H; lia ].
Qed.

(* delta lemma: a sum that keeps only the k=i term (i in range) reads f i *)
Lemma Sum_delta : forall n i f,
  (i < n)%nat -> Sum n (fun k => if Nat.eqb i k then f k else 0) == f i.
Proof.
  induction n as [| m IH]; intros i f Hi; simpl.
  - inversion Hi.
  - destruct (Nat.eq_dec i m) as [He | Hne].
    + subst m. rewrite Nat.eqb_refl.
      rewrite (Sum_ext_lt _ _ (fun _ => 0)); [ rewrite Sum_zero; ring | ].
      intros k Hk. assert (Nat.eqb i k = false) as E by (apply Nat.eqb_neq; lia).
      rewrite E. reflexivity.
    + rewrite (proj2 (Nat.eqb_neq i m) Hne).
      rewrite IH by lia. ring.
Qed.

(* ---- matrices ---- *)
Definition Mat := nat -> nat -> Q.
Definition meq (n : nat) (A B : Mat) : Prop := forall i j, (i < n)%nat -> (j < n)%nat -> A i j == B i j.
Definition madd (A B : Mat) : Mat := fun i j => A i j + B i j.
Definition transpose (A : Mat) : Mat := fun i j => A j i.
Definition mmul (n : nat) (A B : Mat) : Mat := fun i j => Sum n (fun k => A i k * B k j).
Definition mid : Mat := fun i j => if Nat.eqb i j then 1 else 0.

Theorem madd_comm : forall n A B, meq n (madd A B) (madd B A).
Proof. intros n A B i j _ _. unfold madd. ring. Qed.
Theorem madd_assoc : forall n A B C, meq n (madd (madd A B) C) (madd A (madd B C)).
Proof. intros n A B C i j _ _. unfold madd. ring. Qed.

Theorem transpose_involutive : forall n A, meq n (transpose (transpose A)) A.
Proof. intros n A i j _ _. unfold transpose. reflexivity. Qed.

Theorem transpose_mmul : forall n A B, meq n (transpose (mmul n A B)) (mmul n (transpose B) (transpose A)).
Proof.
  intros n A B i j _ _. unfold transpose, mmul.
  apply Sum_ext. intro k. unfold transpose. ring.
Qed.

Theorem mid_left : forall n A i j, (i < n)%nat -> mmul n mid A i j == A i j.
Proof.
  intros n A i j Hi. unfold mmul, mid.
  rewrite (Sum_ext n (fun k => (if Nat.eqb i k then 1 else 0) * A k j)
                     (fun k => if Nat.eqb i k then A k j else 0)).
  - apply Sum_delta with (f := fun k => A k j); exact Hi.
  - intro k. destruct (Nat.eqb i k); ring.
Qed.

(* ---- Graph Laplacian over ℚ:  L[i][j] = if i=j then deg i else -w i j ---- *)
Section Laplacian.
  Variable n : nat.
  Variable w : nat -> nat -> Q.
  Hypothesis w_sym  : forall i j, w i j == w j i.
  Hypothesis w_diag0 : forall i, w i i == 0.

  Definition deg (i : nat) : Q := Sum n (fun k => w i k).
  Definition Lap : Mat := fun i j => if Nat.eqb i j then deg i else - (w i j).

  Theorem laplacian_symmetric : forall i j, Lap i j == transpose Lap i j.
  Proof.
    intros i j. unfold Lap, transpose.
    destruct (Nat.eqb i j) eqn:E.
    - apply Nat.eqb_eq in E. subst j. rewrite Nat.eqb_refl. reflexivity.
    - rewrite (Nat.eqb_sym j i), E. rewrite w_sym. reflexivity.
  Qed.

  (* row-sum zero, hence the all-ones vector is in ker L_R (connectivity kernel,
     §15.2): Σ_j Lap[i,j] = deg i − Σ_{j≠i} w i j = deg i − deg i = 0.  Proved via
     the delta lemma on both the diagonal degree term and the off-diagonal weights. *)
  Theorem laplacian_rowsum_zero : forall i, (i < n)%nat -> Sum n (fun j => Lap i j) == 0.
  Proof.
    intros i Hi.
    (* off-diagonal weights sum to deg i (using w i i = 0), so their negatives sum to -deg i *)
    assert (Hoff : Sum n (fun j => if Nat.eqb i j then 0 else - w i j) == - deg i).
    { transitivity (Sum n (fun j => - w i j)).
      - apply Sum_ext_lt. intros j Hj. destruct (Nat.eqb i j) eqn:E.
        + apply Nat.eqb_eq in E; subst j. rewrite w_diag0. ring.
        + reflexivity.
      - unfold deg. rewrite Sum_opp. reflexivity. }
    unfold Lap.
    rewrite (Sum_ext_lt n (fun j => if Nat.eqb i j then deg i else - w i j)
                          (fun j => (if Nat.eqb i j then deg i else 0)
                                  + (if Nat.eqb i j then 0 else - w i j))).
    - rewrite Sum_plus, (Sum_delta n i (fun _ => deg i) Hi), Hoff. ring.
    - intros j Hj. destruct (Nat.eqb i j); ring.
  Qed.

  (* constants are in the kernel: (Lap · 1)[i] = Σ_j Lap[i,j]·1 = 0 *)
  Theorem laplacian_ones_in_kernel :
    forall i, (i < n)%nat -> Sum n (fun j => Lap i j * 1) == 0.
  Proof.
    intros i Hi. rewrite (Sum_ext n (fun j => Lap i j * 1) (fun j => Lap i j)).
    - apply laplacian_rowsum_zero; exact Hi.
    - intro j. ring.
  Qed.
End Laplacian.

(* ===================================================================== *)
(*  The parameter-reducing twirl (Reynolds operator).  This is the        *)
(*  mathematics behind the Standard-Model parameter economy: a full       *)
(*  metric on an n-dim space has n(n+1)/2 free components, but averaging   *)
(*  it over a symmetry group whose only invariant is the trace collapses   *)
(*  it to a SINGLE scalar.  The isotropy twirl Π(X) = (tr X / n)·I is      *)
(*  that averaging map; here we machine-check it is an idempotent          *)
(*  projector whose image is the 1-dimensional scalar line ℚ·I.           *)
(* ===================================================================== *)
Definition trace (n : nat) (A : Mat) : Q := Sum n (fun k => A k k).
Definition scalarM (c : Q) : Mat := fun i j => if Nat.eqb i j then c else 0.
Definition twirl (n : nat) (A : Mat) : Mat := scalarM (trace n A / inject_Z (Z.of_nat n)).

(* PARAMETER REDUCTION (the heart of the SM parameter economy, as mathematics):
   the twirl's image is the 1-dimensional scalar line ℚ·I — EVERY output is a scalar
   matrix.  So an arbitrary n×n metric (n(n+1)/2 free symmetric components) averaged by
   the twirl retains exactly ONE free scalar.  (The twirl is also the standard idempotent
   Reynolds projector Π(Π(A))=Π(A); the scalar-image fact below is the parameter count.) *)
Theorem twirl_image_scalar :
  forall n A, exists c, forall i j, twirl n A i j = scalarM c i j.
Proof. intros n A. exists (trace n A / inject_Z (Z.of_nat n)). intros; reflexivity. Qed.

(* sum of a constant: Σ_{k<n} c = n·c *)
Lemma Sum_const : forall n c, Sum n (fun _ => c) == inject_Z (Z.of_nat n) * c.
Proof.
  induction n as [| m IH]; intro c; simpl Sum.
  - replace (inject_Z (Z.of_nat 0)) with 0 by reflexivity. ring.
  - rewrite IH. replace (Z.of_nat (S m)) with (Z.of_nat m + 1)%Z by lia.
    rewrite inject_Z_plus. replace (inject_Z 1) with 1 by reflexivity. ring.
Qed.

(* trace of a scalar matrix c·I over n indices is n·c *)
Lemma trace_scalarM : forall n c, trace n (scalarM c) == inject_Z (Z.of_nat n) * c.
Proof.
  intros n c. unfold trace, scalarM.
  rewrite (Sum_ext n (fun k => if Nat.eqb k k then c else 0) (fun _ => c)).
  - apply Sum_const.
  - intro k. rewrite Nat.eqb_refl. reflexivity.
Qed.

(* The twirl is a GENUINE (non-trivial) idempotent projector: Π(Π(A)) = Π(A), n ≥ 1.
   This is the substantive Reynolds/parameter-reduction fact — not merely that the image
   happens to be scalar by definition, but that re-averaging changes nothing. *)
Lemma inject_nat_nonzero : forall n, (n <> 0)%nat -> ~ inject_Z (Z.of_nat n) == 0.
Proof.
  intros n Hn Hc.
  assert (Hz : Z.of_nat n = 0%Z).
  { apply inject_Z_injective. rewrite Hc. reflexivity. }
  apply Hn. lia.
Qed.

(* re-averaging a scalar matrix returns the same trace scale (n ≠ 0) *)
Lemma trace_twirl : forall n A, (n <> 0)%nat -> trace n (twirl n A) == trace n A.
Proof.
  intros n A Hn. unfold twirl. rewrite trace_scalarM. field.
  apply inject_nat_nonzero; exact Hn.
Qed.

Theorem twirl_idempotent :
  forall n A i j, (n <> 0)%nat -> twirl n (twirl n A) i j == twirl n A i j.
Proof.
  intros n A i j Hn. unfold twirl at 1. unfold scalarM at 1.
  destruct (Nat.eqb i j) eqn:E.
  - rewrite (trace_twirl n A Hn). unfold twirl, scalarM. rewrite E. reflexivity.
  - unfold twirl, scalarM. rewrite E. reflexivity.
Qed.

(* the scalar line is 1-dimensional: any two scalar matrices agreeing at (0,0) agree everywhere *)
Theorem scalar_line_one_dim :
  forall c d, scalarM c 0%nat 0%nat = scalarM d 0%nat 0%nat -> forall i j, scalarM c i j = scalarM d i j.
Proof.
  intros c d H i j. unfold scalarM in *. simpl in H.
  destruct (Nat.eqb i j); [ exact H | reflexivity ].
Qed.
