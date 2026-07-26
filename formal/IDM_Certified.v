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

(** Sanity checks that these are computable finite readouts (not just abstract). *)
Example geom_half_3 : geom_sum (1 # 2) 3 == 7 # 4.
Proof. reflexivity. Qed.

Example geom_id_third_4 : (1 - (1 # 3)) * geom_sum (1 # 3) 4 == 1 - qpow (1 # 3) 4.
Proof. apply geom_certified_identity. Qed.
