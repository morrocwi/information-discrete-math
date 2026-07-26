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

Require Import ZArith Arith Lia List Bool Factorial Permutation.
Import ListNotations.

(* ============================ A2 · the one FOLD ============================ *)
(* the generic left accumulation ⊕_{k<N} f[k] over ANY carrier and operation. *)
Fixpoint fold {A : Type} (op : A -> A -> A) (e : A) (f : nat -> A) (N : nat) : A :=
  match N with
  | O => e
  | S k => op (fold op e f k) (f k)
  end.

(* ---- the DEEP semiring law: a fold over an associative-COMMUTATIVE operation is
   invariant under any REORDERING of its inputs. This is the formal justification
   that the A2 accumulation is well-defined independent of traversal order — the
   licence to reorder, chunk, and parallelise a fold (over a `list`, via Permutation). *)
Section FoldPerm.
  Context {A : Type} (op : A -> A -> A) (e : A).
  Hypothesis op_assoc : forall x y z, op x (op y z) = op (op x y) z.
  Hypothesis op_comm  : forall x y, op x y = op y x.

  Lemma op_swap : forall x y z, op x (op y z) = op y (op x z).
  Proof. intros x y z. rewrite op_assoc, (op_comm x y), <- op_assoc. reflexivity. Qed.

  Theorem fold_right_perm : forall xs ys,
    Permutation xs ys -> fold_right op e xs = fold_right op e ys.
  Proof.
    intros xs ys H. induction H; simpl.
    - reflexivity.
    - rewrite IHPermutation. reflexivity.
    - apply op_swap.
    - rewrite IHPermutation1, IHPermutation2. reflexivity.
  Qed.
End FoldPerm.

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

(* critical-/widest-path EXACTNESS (mirror of foldmin_in): the accumulated maximum
   is attained — it equals the start value or an actual element. *)
Lemma foldmax_in : forall v0 f N,
  fold Z.max v0 f N = v0 \/ exists i, (i < N)%nat /\ fold Z.max v0 f N = f i.
Proof.
  intros v0 f N. induction N as [| k IH]; simpl.
  - left. reflexivity.
  - destruct (Z.max_spec (fold Z.max v0 f k) (f k)) as [[_ Heq] | [_ Heq]]; rewrite Heq.
    + right. exists k. split; [lia | reflexivity].
    + destruct IH as [H0 | [i [Hi Hfi]]].
      * left. exact H0.
      * right. exists i. split; [lia | exact Hfi].
Qed.

(* set-aggregation is ORDER-INDEPENDENT: Σ and Π over a multiset are well-defined,
   direct corollaries of fold_right_perm (both (+) and (×) are assoc-commutative).
   This is what makes `describe`/statistics and combinatorial products unambiguous. *)
Theorem sum_list_perm : forall xs ys : list Z,
  Permutation xs ys -> fold_right Z.add 0 xs = fold_right Z.add 0 ys.
Proof. intros xs ys H. apply (fold_right_perm Z.add 0); [intros; lia | intros; lia | exact H]. Qed.

Theorem prod_list_perm : forall xs ys : list Z,
  Permutation xs ys -> fold_right Z.mul 1 xs = fold_right Z.mul 1 ys.
Proof. intros xs ys H. apply (fold_right_perm Z.mul 1); [intros; ring | intros; ring | exact H]. Qed.

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

(* ---- branch kernel 6: POLYNOMIALS — Horner's method IS a (right) fold ----
   evaluating Σ cₖ xᵏ efficiently is the nested fold  c₀ + x(c₁ + x(c₂ + …)); it
   equals the explicit polynomial. `horner` is definitionally fold_right over the
   coefficient list; horner_is_poly certifies it computes the polynomial. *)
Fixpoint horner (x : Z) (cs : list Z) : Z :=
  match cs with
  | [] => 0
  | c :: rest => c + x * horner x rest
  end.

Fixpoint poly (x : Z) (cs : list Z) (p : Z) : Z :=   (* explicit Σ cₖ·pxᵏ, p = running power *)
  match cs with
  | [] => 0
  | c :: rest => c * p + poly x rest (p * x)
  end.

Lemma horner_scaled : forall cs x p, p * horner x cs = poly x cs p.
Proof.
  induction cs as [| c rest IH]; intros x p; simpl.
  - ring.
  - rewrite <- (IH x (p * x)). ring.
Qed.

Theorem horner_is_poly : forall x cs, horner x cs = poly x cs 1.
Proof. intros x cs. rewrite <- (horner_scaled cs x 1). ring. Qed.

(* ---- the shortest-path fold is EXACT: the accumulated minimum is attained ----
   strengthens foldmin_le_* — the min is not merely a lower bound, it equals the
   start value or one actual element (so shortest_path returns the true optimum). *)
Lemma foldmin_in : forall v0 f N,
  fold Z.min v0 f N = v0 \/ exists i, (i < N)%nat /\ fold Z.min v0 f N = f i.
Proof.
  intros v0 f N. induction N as [| k IH]; simpl.
  - left. reflexivity.
  - destruct (Z.min_spec (fold Z.min v0 f k) (f k)) as [[_ Heq] | [_ Heq]]; rewrite Heq.
    + destruct IH as [H0 | [i [Hi Hfi]]].
      * left. exact H0.
      * right. exists i. split; [lia | exact Hfi].
    + right. exists k. split; [lia | reflexivity].
Qed.

(* ---- the associative-monoid CHUNKING law: a fold splits over concatenation ----
   fold over [0,m+n) = fold over [0,m) combined with fold over the shifted tail.
   This is why associative folds parallelise (MapReduce) — the reduction is not
   tied to sequential order. *)
Theorem fold_add_app : forall f m n,
  fold Z.add 0 f (m + n) = fold Z.add 0 f m + fold Z.add 0 (fun k => f (m + k)%nat) n.
Proof.
  intros f m n. induction n as [| n' IH]; simpl.
  - replace (m + 0)%nat with m by lia. ring.
  - replace (m + S n')%nat with (S (m + n')) by lia. simpl. rewrite IH. ring.
Qed.

(* ---- branch kernel 7: PRODUCT / COMBINATORICS — factorial is a fold over (×) ----
   the SAME generic fold at the multiplicative operation computes n! exactly. *)
Theorem factorial_is_fold : forall N,
  fold Z.mul 1 (fun k => Z.of_nat (S k)) N = Z.of_nat (fact N).
Proof.
  induction N as [| k IH].
  - reflexivity.
  - cbn [fold fact]. rewrite IH, <- Nat2Z.inj_mul. f_equal. lia.
Qed.

(* ---- branch kernel 8: BELLMAN–FORD / DP convergence ----
   iterative relaxation over the min-plus semiring is (i) non-increasing — a step
   never worsens the estimate — and (ii) idempotent per edge — re-relaxing the same
   candidate changes nothing. Together these are why the DP/Bellman fixpoint is
   reached in finitely many rounds. *)
Lemma relax_nonincreasing : forall d cand : Z, Z.min d cand <= d.
Proof. intros; lia. Qed.

Lemma relax_idempotent : forall d cand : Z, Z.min (Z.min d cand) cand = Z.min d cand.
Proof. intros; lia. Qed.

(* ---- A2 × A3 bridge: LP WEAK DUALITY ----
   a dual-feasible y (each c_j ≤ y·A_j, y ≥ 0) is a CERTIFICATE (A3) that bounds the
   primal objective computed by the simplex (A2): for any primal-feasible x ≥ 0 with
   Ax ≤ b, the objective c·x is ≤ y·b. Shown for two variables — the general case is
   the same argument summed over columns. *)
Theorem weak_duality_2 : forall c1 c2 x1 x2 a1 a2 b y,
  0 <= x1 -> 0 <= x2 -> 0 <= y ->
  c1 <= y * a1 -> c2 <= y * a2 ->        (* dual feasibility, per column *)
  a1 * x1 + a2 * x2 <= b ->             (* primal feasibility: A x ≤ b *)
  c1 * x1 + c2 * x2 <= y * b.           (* weak duality: c·x ≤ y·b *)
Proof. intros; nia. Qed.

(* ---- branch kernel 9: the FFT divide-and-conquer SPLIT ----
   the sum over [0,2n) decomposes into the sub-fold over the EVEN indices plus the
   sub-fold over the ODD indices — the Danielson–Lanczos reindexing at the heart of
   the fast Fourier transform. (Honest fence: the full FFT additionally combines the
   two halves with roots-of-unity twiddle factors, a complex `+ℝ` readout not claimed
   here; this certifies the recursive fold decomposition the algorithm is built on.) *)
Theorem fold_split_even_odd : forall f n,
  fold Z.add 0 f (2 * n) =
  fold Z.add 0 (fun k => f (2 * k)%nat) n + fold Z.add 0 (fun k => f (2 * k + 1)%nat) n.
Proof.
  intros f n. induction n as [| m IH].
  - reflexivity.
  - replace (2 * S m)%nat with (S (S (2 * m))) by lia.
    cbn [fold]. rewrite IH.
    replace (S (2 * m))%nat with (2 * m + 1)%nat by lia.
    ring.
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

(* ---- A3 branch instance 3: MODULAR SQUARE ROOT (the modular_sqrt kernel) ----
   a witness w with w² ≡ a (mod p) proves a is a quadratic residue mod p. *)
Definition qr_check (a p w : nat) : bool := Nat.eqb ((w * w) mod p) (a mod p).

Theorem witness_qr_sound : forall a p,
  decide (fun w => qr_check a p w) p = true -> exists w, ((w * w) mod p = a mod p)%nat.
Proof.
  intros a p H. apply witness_sound in H. destruct H as [w [_ Hc]].
  unfold qr_check in Hc. apply Nat.eqb_eq in Hc. exists w. exact Hc.
Qed.

(* ---- A3 branch instance 4: DISCRETE LOG (the discrete_log kernel) ----
   a witness w with g^w ≡ h (mod p) solves the discrete logarithm — the exact
   baby-step/giant-step verdict, now with a machine-checked soundness proof. *)
Definition dlog_check (g h p w : nat) : bool := Nat.eqb ((g ^ w) mod p) (h mod p).

Theorem witness_dlog_sound : forall g h p,
  decide (fun w => dlog_check g h p w) p = true -> exists w, ((g ^ w) mod p = h mod p)%nat.
Proof.
  intros g h p H. apply witness_sound in H. destruct H as [w [_ Hc]].
  unfold dlog_check in Hc. apply Nat.eqb_eq in Hc. exists w. exact Hc.
Qed.

(* ---- A3 flagship instance: BOOLEAN SATISFIABILITY (the `sat` kernel) ----
   the canonical decision problem. An assignment is a bit-pattern `a : nat` (bit v =
   truth of variable v); a literal is (polarity, var); a clause is satisfied if some
   literal is true; a CNF if every clause is. Searching the 2^n assignments with the
   ONE decision schema yields a satisfying model (soundness = a real model exists). *)
Definition lit : Type := (bool * nat)%type.
Definition lit_true (a : nat) (l : lit) : bool := Bool.eqb (Nat.testbit a (snd l)) (fst l).
Definition clause_sat (a : nat) (cl : list lit) : bool := existsb (lit_true a) cl.
Definition cnf_sat (a : nat) (f : list (list lit)) : bool := forallb (clause_sat a) f.

Theorem sat_reduces_to_decision : forall f n,
  decide (fun a => cnf_sat a f) (2 ^ n) = true -> exists a, cnf_sat a f = true.
Proof.
  intros f n H. apply witness_sound in H. destruct H as [a [_ Ha]]. exists a. exact Ha.
Qed.

(* a returned model is a genuine proof: every clause is satisfied by it. *)
Theorem sat_model_sound : forall a f,
  cnf_sat a f = true -> forall cl, In cl f -> clause_sat a cl = true.
Proof.
  intros a f H cl Hin. unfold cnf_sat in H. rewrite forallb_forall in H. apply H. exact Hin.
Qed.

(* ---- crypto forward map: MODULAR EXPONENTIATION is a fold over (× mod p) ----
   the RSA / elliptic-curve / discrete-log forward map g^N mod p is the SAME generic
   accumulation, now over the multiplicative operation of the ring ℤ/pℤ. *)
Fixpoint modpow_fold (g p N : nat) : nat :=
  match N with
  | O => 1 mod p
  | S k => (modpow_fold g p k * g) mod p
  end.

Theorem modpow_is_fold : forall g p N, p <> 0 -> modpow_fold g p N = (g ^ N) mod p.
Proof.
  intros g p N Hp. induction N as [| k IH]; simpl.
  - reflexivity.
  - rewrite IH, Nat.mul_mod_idemp_l by exact Hp. f_equal. lia.
Qed.

(* ---- the UNIVERSAL counterpart of the witness search: TAUTOLOGY / TRUTH TABLE ----
   where DECISION asks "does SOME witness exist?", `truth_table` asks "do ALL rows
   hold?" — a bounded forall over the 2^n assignments. A `true` verdict PROVES the
   property for every row (the tautology / valid-formula kernel). *)
Definition all_rows (check : nat -> bool) (bound : nat) : bool := forallb check (seq 0 bound).

Theorem tautology_sound : forall check bound,
  all_rows check bound = true -> forall w, (w < bound)%nat -> check w = true.
Proof.
  intros check bound H w Hw. unfold all_rows in H. rewrite forallb_forall in H.
  apply H. apply in_seq. lia.
Qed.

(* instance: a CNF checked true on every assignment is a tautology (all 2^n rows). *)
Theorem cnf_tautology_sound : forall f n,
  all_rows (fun a => cnf_sat a f) (2 ^ n) = true -> forall a, (a < 2 ^ n)%nat -> cnf_sat a f = true.
Proof. intros f n. apply tautology_sound. Qed.

(* ---- A3 branch instance 5: CHINESE REMAINDER (the `crt` kernel) ----
   a witness x meeting every congruence x ≡ rᵢ (mod mᵢ) is a solution of the
   simultaneous system — found by the one bounded search. *)
Definition crt_check (rs ms : list nat) (x : nat) : bool :=
  forallb (fun rm => Nat.eqb (x mod snd rm) (fst rm mod snd rm)) (combine rs ms).

Theorem witness_crt_sound : forall rs ms bound,
  decide (crt_check rs ms) bound = true ->
  exists x, forall r m, In (r, m) (combine rs ms) -> (x mod m = r mod m)%nat.
Proof.
  intros rs ms bound H. apply witness_sound in H. destruct H as [x [_ Hc]].
  exists x. intros r m Hin. unfold crt_check in Hc. rewrite forallb_forall in Hc.
  specialize (Hc (r, m) Hin). simpl in Hc. apply Nat.eqb_eq in Hc. exact Hc.
Qed.
