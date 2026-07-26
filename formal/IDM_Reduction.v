(* ===================================================================== *)
(*  IDM_Reduction.v — the root design, machine-checked: A2 (FOLD) and A3     *)
(*  (DECISION) generate the solver's branches. Coq 8.20, axiom-free          *)
(*  (Closed under the global context). Yaoharee Lahtee.                      *)
(*                                                                          *)
(*  Root design (see the 3+1 axiom note):                                    *)
(*    A1 READOUT   δ_R : everything is a finite discrete rational readout.   *)
(*    A2 FOLD      I_⊕[f](N) = ⊕_{k<N} f[k]  — ONE generic accumulation;     *)
(*                 changing the operation changes the branch.                *)
(*    A3 DECISION  P(X) ⟺ ∃ finite checkable witness w.                      *)
(*                                                                          *)
(*  This file proves the STRUCTURAL reductions — that each branch's CORE     *)
(*  operation is literally an instance of the one generic `fold` (A2) or of  *)
(*  the one generic bounded-witness `decide` (A3). HONEST FENCE: it does     *)
(*  NOT claim every one of the 230 Python handlers is verified; it certifies *)
(*  that the branch KERNELS reduce to A2/A3, lifting that structural claim   *)
(*  from Dr (design) to Th_coqc.                                             *)
(*                                                                          *)
(*  A2 — one `fold`, four branch kernels:                                    *)
(*    ftcc_Z              (+,·) telescoping  → analysis/summation branch      *)
(*    foldmin_le_init/elem (min,+) relaxation → shortest-path/DP branch       *)
(*    sum_is_fold, path_is_fold  both ARE `fold`, only the operation differs  *)
(*    pivot_preserves     elimination atom   → linear-algebra/LP/geometry     *)
(*  A3 — one `decide`, its soundness + a branch instance:                    *)
(*    witness_sound/complete   bounded checkable search = a decision          *)
(*    witness_composite_sound  a found divisor PROVES compositeness           *)
(* ===================================================================== *)

Require Import ZArith Arith Lia List Bool.
Import ListNotations.

(* ============================ A2 · the one FOLD ============================ *)
(* the generic left accumulation ⊕_{k<N} f[k] over ANY carrier and operation. *)
Fixpoint fold {A : Type} (op : A -> A -> A) (e : A) (f : nat -> A) (N : nat) : A :=
  match N with
  | O => e
  | S k => op (fold op e f k) (f k)
  end.

(* ---- branch kernel 1: the ANALYSIS / SUMMATION branch = fold over (+) ---- *)
Open Scope Z_scope.

Definition sum_readout (f : nat -> Z) : nat -> Z := fold Z.add 0 f.
Definition zdelta (f : nat -> Z) (n : nat) : Z := f (S n) - f n.

(* FTCC (integer/counting readout): the accumulation of increments telescopes
   EXACTLY — this is the analysis-branch engine, over the additive operation. *)
Theorem ftcc_Z : forall (f : nat -> Z) (N : nat),
  fold Z.add 0 (zdelta f) N = f N - f 0%nat.
Proof.
  intros f N. induction N as [| k IH]; simpl.
  - lia.
  - rewrite IH. unfold zdelta. lia.
Qed.

(* ---- branch kernel 2: the PATH / DP branch = the SAME fold over (min) ---- *)
Definition path_accum (v0 : Z) (f : nat -> Z) : nat -> Z := fold Z.min v0 f.

(* the shortest-path/DP relaxation invariant: the accumulation is a lower bound
   on the start value and on every accumulated element — "best so far". *)
Lemma foldmin_le_init : forall v0 f N, fold Z.min v0 f N <= v0.
Proof.
  intros v0 f N. induction N as [| k IH]; simpl.
  - lia.
  - lia.
Qed.

Lemma foldmin_le_elem : forall v0 f N i,
  (i < N)%nat -> fold Z.min v0 f N <= f i.
Proof.
  intros v0 f N. induction N as [| k IH]; intros i Hi; simpl.
  - lia.
  - assert (i = k \/ i < k)%nat as [->|Hlt] by lia.
    + lia.
    + specialize (IH i Hlt). lia.
Qed.

(* the two branch kernels are literally the SAME generic `fold`, differing only
   in the semiring operation — this IS the reduction: one engine, many branches. *)
Theorem sum_is_fold  : forall f N, sum_readout f N = fold Z.add 0 f N.
Proof. reflexivity. Qed.
Theorem path_is_fold : forall v0 f N, path_accum v0 f N = fold Z.min v0 f N.
Proof. reflexivity. Qed.

(* ---- branch kernel 3: the LINEAR-ALGEBRA / LP / GEOMETRY atom ----
   Gaussian elimination, the simplex, and the sign-of-determinant geometry
   predicates are schedules of ONE retained-difference row operation. Its atom:
   combining equation i with a multiple of equation j preserves every solution
   (so the whole elimination preserves the solution set). Shown for a 2-variable
   row, which is the general pivot step restricted to the pivot columns. *)
Theorem pivot_preserves : forall a b c d k x y v w,
  a * x + b * y = v ->
  c * x + d * y = w ->
  (a - k * c) * x + (b - k * d) * y = v - k * w.
Proof.
  intros a b c d k x y v w H1 H2.
  rewrite <- H1, <- H2. ring.
Qed.

Close Scope Z_scope.

(* ---- the semiring LAWS that make the fold-reduction valid ----
   linearity and additivity of the additive fold are exactly why "the branch is a
   fold" is a legitimate reduction: expectation, integration, summation, and the
   matrix product all inherit these from the one `fold`. *)
Open Scope Z_scope.

Lemma fold_ext : forall {A} (op : A -> A -> A) (e : A) (f g : nat -> A) N,
  (forall k, f k = g k) -> fold op e f N = fold op e g N.
Proof.
  intros A op e f g N H. induction N as [| k IH]; simpl.
  - reflexivity.
  - rewrite IH, H. reflexivity.
Qed.

Theorem fold_linear : forall (c : Z) (f : nat -> Z) N,
  fold Z.add 0 (fun k => c * f k) N = c * fold Z.add 0 f N.
Proof.
  intros c f N. induction N as [| k IH]; simpl.
  - ring.
  - rewrite IH. ring.
Qed.

Theorem fold_add_split : forall (f g : nat -> Z) N,
  fold Z.add 0 (fun k => f k + g k) N = fold Z.add 0 f N + fold Z.add 0 g N.
Proof.
  intros f g N. induction N as [| k IH]; simpl.
  - ring.
  - rewrite IH. ring.
Qed.

(* ---- branch kernel 4: max-plus / bottleneck (CRITICAL & WIDEST path) ----
   the same fold over Z.max: the accumulation is an upper bound on the start and
   on every element — the "longest / widest so far" invariant. *)
Lemma foldmax_ge_init : forall v0 f N, v0 <= fold Z.max v0 f N.
Proof. intros v0 f N. induction N as [| k IH]; simpl; lia. Qed.

Lemma foldmax_ge_elem : forall v0 f N i,
  (i < N)%nat -> f i <= fold Z.max v0 f N.
Proof.
  intros v0 f N. induction N as [| k IH]; intros i Hi; simpl.
  - lia.
  - assert (i = k \/ i < k)%nat as [->|Hlt] by lia; [lia | specialize (IH i Hlt); lia].
Qed.

(* ---- branch kernel 5: the INNER PRODUCT (matrix-multiply / convolution / dot) ----
   every entry of a matrix product, every convolution tap, and dot/cross are the
   SAME fold over (+) of pointwise products; scaling a factor scales the result
   (bilinearity), inherited from fold_linear via fold_ext. *)
Definition dotf (u v : nat -> Z) : nat -> Z := fold Z.add 0 (fun k => u k * v k).

Theorem dot_is_fold : forall u v N,
  dotf u v N = fold Z.add 0 (fun k => u k * v k) N.
Proof. reflexivity. Qed.

Theorem dot_scale : forall a u v N, dotf (fun k => a * u k) v N = a * dotf u v N.
Proof.
  intros a u v N. unfold dotf.
  rewrite (fold_ext Z.add 0 (fun k => (a * u k) * v k) (fun k => a * (u k * v k)) N)
    by (intro k; ring).
  apply fold_linear.
Qed.

Close Scope Z_scope.

(* ============================ A3 · the one DECISION ============================ *)
(* a predicate decided by a BOUNDED search for a checkable witness. This is the
   kernel of every decision/enumeration branch member (primality, SAT, discrete
   log, Diophantine solvability): ACCEPT carries a witness; no witness ⇒ HOLD. *)
Definition decide (check : nat -> bool) (bound : nat) : bool :=
  existsb check (seq 0 bound).

(* soundness: an ACCEPT is a PROOF — it exhibits an actual witness in range. *)
Theorem witness_sound : forall check bound,
  decide check bound = true -> exists w, (w < bound)%nat /\ check w = true.
Proof.
  intros check bound H. unfold decide in H.
  apply existsb_exists in H. destruct H as [w [Hin Hc]].
  apply in_seq in Hin. exists w. split; [lia | exact Hc].
Qed.

(* completeness: any genuine in-range witness is found by the search. *)
Theorem witness_complete : forall check bound w,
  (w < bound)%nat -> check w = true -> decide check bound = true.
Proof.
  intros check bound w Hlt Hc. unfold decide.
  apply existsb_exists. exists w. split; [apply in_seq; lia | exact Hc].
Qed.

(* the decision is, itself, decidable (the search terminates with a verdict). *)
Theorem decide_dec : forall check bound,
  {decide check bound = true} + {decide check bound = false}.
Proof. intros check bound. destruct (decide check bound); [left | right]; reflexivity. Qed.

(* ---- A3 branch instance: COMPOSITENESS by a found divisor ----
   the exact backbone of is_prime / primality_certificate: a witness d with
   1 < d < n and d | n is a PROOF that n is composite (for any n). *)
Definition divides_check (n d : nat) : bool :=
  (1 <? d) && (d <? n) && (Nat.eqb (n mod d) 0).

Definition composite (n : nat) : Prop :=
  exists d, (1 < d < n)%nat /\ Nat.divide d n.

Theorem witness_composite_sound : forall n,
  decide (divides_check n) n = true -> composite n.
Proof.
  intros n H. apply witness_sound in H. destruct H as [d [_ Hc]].
  unfold divides_check in Hc.
  apply andb_true_iff in Hc as [Hc1 Hmod].
  apply andb_true_iff in Hc1 as [H1 H2].
  apply Nat.ltb_lt in H1. apply Nat.ltb_lt in H2. apply Nat.eqb_eq in Hmod.
  exists d. split.
  - lia.
  - (* n mod d = 0 ⇒ d | n *)
    apply Nat.Lcm0.mod_divide. exact Hmod.
Qed.

(* and compositeness is exactly the existence of a nontrivial divisor — so the
   decision kernel captures the whole notion, no continuum, fully decidable. *)
Theorem composite_has_factor : forall n,
  composite n -> exists d, Nat.divide d n /\ d <> 1%nat /\ d <> n.
Proof.
  intros n [d [Hlt Hdiv]]. exists d. split; [exact Hdiv | split; lia].
Qed.

(* soundness AND completeness together: the bounded search is a faithful reflection
   of "a witness exists" — the exact ACCEPT/HOLD contract of the solver. *)
Theorem decide_reflect : forall check bound,
  decide check bound = true <-> exists w, (w < bound)%nat /\ check w = true.
Proof.
  intros check bound. split.
  - apply witness_sound.
  - intros [w [Hlt Hc]]. eapply witness_complete; eauto.
Qed.

(* ---- A3 branch instance 2: INTEGER ROOT / PERFECT POWER ----
   the integer_root / is_perfect_square backbone: a witness w with w^k = n proves
   n is a perfect k-th power (found by the bounded search, else HOLD). *)
Definition power_check (n k w : nat) : bool := Nat.eqb (w ^ k) n.

Theorem witness_power_sound : forall n k,
  decide (fun w => power_check n k w) (S n) = true -> exists w, (w ^ k = n)%nat.
Proof.
  intros n k H. apply witness_sound in H. destruct H as [w [_ Hc]].
  unfold power_check in Hc. apply Nat.eqb_eq in Hc. exists w. exact Hc.
Qed.
