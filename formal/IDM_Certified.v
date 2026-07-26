(** IDM_Certified.v — an END-TO-END certified finite readout, machine-checked, axiom-free.

    The geometric series is the cleanest continuum "limit" that a finite algorithm can read out with a
    *proven* error term, entirely inside Q (no reals, no completed limit, no axioms):

      algorithm : geom_sum r N = sum_{k<N} r^k        (a finite, structurally-terminating fixpoint)
      target    : 1/(1-r)                             (the classical geometric-series "limit")
      certificate: 1/(1-r) - geom_sum r N = r^N/(1-r) (EXACT error, a finite expression in r,N)

    This is the Certified Finite-Readout Theorem for one concrete class: given r and N the readout comes
    with an exact, computable error, so for any rational tolerance one picks the least N with the error
    below it (done in tools/certified_readout.py). Coq checks the mathematics; `Print Assumptions` shows
    it rests on nothing. *)

Require Import QArith.
Open Scope Q_scope.

Fixpoint qpow (r : Q) (n : nat) : Q :=
  match n with
  | O => 1
  | S k => r * qpow r k
  end.

Fixpoint geom_sum (r : Q) (n : nat) : Q :=
  match n with
  | O => 0
  | S k => geom_sum r k + qpow r k
  end.

(** Core exact identity — the algorithm's output telescopes: (1 - r) * S_N = 1 - r^N. Axiom-free. *)
Theorem geom_certified_identity : forall (r : Q) (n : nat),
  (1 - r) * geom_sum r n == 1 - qpow r n.
Proof.
  intros r n. induction n as [| n IH]; simpl.
  - ring.
  - rewrite Qmult_plus_distr_r. rewrite IH. ring.
Qed.

(** The certified DEFECT in division-free form: 1 - (1 - r) * S_N = r^N, for every r and N (no r<>1
    needed). Multiplying the target identity 1 = (1-r)*(1/(1-r)) through, this is exactly the statement
    that the finite readout's error, scaled by (1-r), equals r^N — i.e. on paper (and numerically in
    tools/certified_readout.py) 1/(1-r) - S_N = r^N/(1-r). We keep the Coq statement division-free so it
    stays fully within Q and trivially axiom-free; the r^N term is the shipped, exact error certificate. *)
Corollary geom_certified_defect : forall (r : Q) (n : nat),
  1 - (1 - r) * geom_sum r n == qpow r n.
Proof.
  intros r n. rewrite geom_certified_identity. ring.
Qed.

(** ---------------------------------------------------------------------------------------------
    GENERAL GEOMETRIC-MAJORANT TAIL BOUND — the certificate mechanism behind exp/Simpson/Richardson.

    If a run of nonnegative terms contracts by a ratio ρ (t_{k+1} ≤ ρ·t_k), then ANY finite tail of M
    terms starting at N is bounded: (1 − ρ)·Σ_{j<M} t_{N+j} ≤ t_N, i.e. the tail ≤ t_N/(1−ρ). This is
    the exact, finite, division-free stability certificate the readout ships (the finite exponential's
    Taylor tail is the instance t_k = x^k/k!, ρ = x ≤ ½). Proved by a clean induction — no completed
    sum, no reals, axiom-free. *)
Fixpoint tailsum (t : nat -> Q) (N M : nat) : Q :=
  match M with
  | O => 0
  | S m => t N + tailsum t (S N) m
  end.

Theorem geom_majorant_tail : forall (rho : Q) (t : nat -> Q),
  (forall k, 0 <= t k) ->
  (forall k, t (S k) <= rho * t k) ->
  forall (M N : nat), (1 - rho) * tailsum t N M <= t N.
Proof.
  intros rho t Hpos Hrat.
  induction M as [| m IHm]; intro N.
  - simpl. rewrite Qmult_0_r. apply Hpos.
  - simpl. rewrite Qmult_plus_distr_r.
    apply (Qle_trans _ ((1 - rho) * t N + rho * t N)).
    + apply Qplus_le_r.
      apply (Qle_trans _ (t (S N))).
      * apply IHm.
      * apply Hrat.
    + apply Qle_lteq. right. ring.
Qed.

(** ---------------------------------------------------------------------------------------------
    EXP INSTANCE — the finite exponential's Taylor tail is a certified readout.

    Terms t_k = x^k/k! built by the standard recurrence t_{k+1} = t_k·x/(k+1). For 0≤x they are
    nonnegative and contract with ratio x (since x/(k+1) ≤ x), so geom_majorant_tail applies and the
    M-term tail from index N is bounded by t_N/(1−x). Machine-checked, axiom-free. *)
Require Import Coq.ZArith.ZArith.
Require Import Coq.micromega.Lia.

Fixpoint exp_term (x : Q) (k : nat) : Q :=
  match k with
  | O => 1
  | S j => exp_term x j * x / inject_Z (Z.of_nat (S j))
  end.

Lemma one_le_Sk : forall k, 1 <= inject_Z (Z.of_nat (S k)).
Proof.
  intro k.
  replace 1 with (inject_Z 1) by reflexivity.
  rewrite <- Zle_Qle.
  rewrite Nat2Z.inj_succ.
  assert (H := Nat2Z.is_nonneg k). lia.
Qed.

Lemma q01 : (0 < 1)%Q.    Proof. unfold Qlt; simpl; lia. Qed.
Lemma q01_le : (0 <= 1)%Q. Proof. unfold Qle; simpl; lia. Qed.

Lemma pos_Sk : forall k, 0 < inject_Z (Z.of_nat (S k)).
Proof.
  intro k. apply Qlt_le_trans with (y := 1); [ apply q01 | apply one_le_Sk ].
Qed.

Lemma div_le_self : forall a d, 0 <= a -> 1 <= d -> a / d <= a.
Proof.
  intros a d Ha Hd.
  assert (Hd0 : 0 < d) by (apply Qlt_le_trans with (y := 1); [ apply q01 | assumption ]).
  apply Qle_shift_div_r; [ assumption | ].
  setoid_replace (a * d) with (d * a) by ring.
  setoid_replace a with (1 * a) at 1 by ring.
  apply Qmult_le_compat_r; [ assumption | assumption ].
Qed.

Lemma exp_term_nonneg : forall x k, 0 <= x -> 0 <= exp_term x k.
Proof.
  intros x k Hx. induction k as [| j IH]; simpl.
  - apply q01_le.
  - apply Qle_shift_div_l; [ apply pos_Sk | ].
    rewrite Qmult_0_l. apply Qmult_le_0_compat; assumption.
Qed.

Lemma exp_term_ratio : forall x k, 0 <= x -> exp_term x (S k) <= x * exp_term x k.
Proof.
  intros x k Hx.
  assert (HA : 0 <= exp_term x k * x) by (apply Qmult_le_0_compat; [ apply exp_term_nonneg | ]; assumption).
  simpl.
  apply (Qle_trans _ (exp_term x k * x)).
  - apply div_le_self; [ assumption | apply one_le_Sk ].
  - rewrite Qmult_comm. apply Qle_refl.
Qed.

Theorem exp_tail_certified : forall (x : Q) (N M : nat),
  0 <= x ->
  (1 - x) * tailsum (exp_term x) N M <= exp_term x N.
Proof.
  intros x N M Hx.
  apply (geom_majorant_tail x (exp_term x)).
  - intro k. apply exp_term_nonneg; assumption.
  - intro k. apply exp_term_ratio; assumption.
Qed.

(** Sanity checks that these are computable finite readouts (not just abstract). *)
Example geom_half_3 : geom_sum (1 # 2) 3 == 7 # 4.
Proof. reflexivity. Qed.

Example geom_id_third_4 : (1 - (1 # 3)) * geom_sum (1 # 3) 4 == 1 - qpow (1 # 3) 4.
Proof. apply geom_certified_identity. Qed.
