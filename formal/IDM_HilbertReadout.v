(* IDM_HilbertReadout.v — the ℚ-computable core of the +ℝ-Open Hilbert frontier.

   The infinite-dimensional Hilbert readouts (ℓ², L², completeness) leave the COMPLETED object
   (the ℓ²/L² element, the total norm ‖x‖², the limit) +ℝ-Open — those are non-readouts (I1). But the
   FINITE partial energy Σ_{k≤N} |x_k|² that idm.hilbert_open actually COMPUTES is an exact ℚ readout.
   This file machine-checks exactly that computable core, over ℚ, axiom-free:

     - partial_energy_nonneg      : Σ x_k² ≥ 0                    (a genuine seminorm value)
     - partial_energy_app         : Σ_{xs++ys} = Σ_xs + Σ_ys     (EXACT over ℚ — no rounding)
     - partial_energy_monotone    : Σ_xs ≤ Σ_{xs++[x]}           (adding a coordinate never decreases;
                                                                   the finite readout is a monotone
                                                                   lower approximant of the open total)

   Principle (founder, 2026-07-29): if an ℝ-rung quantity is actually COMPUTED, it is computed on ℚ —
   so its computed core must carry a ℚ tier (here Th_coqc), not a blanket +ℝ-Open. Only the completed
   tail Σ_{k>N} (a limit / a non-readout) stays open. This is the two-tier (continuum-maya, Part XX)
   split made machine-checked: the readout is closed on ℚ; only the non-readout remains open. *)

Require Import QArith.
Require Import List.
Import ListNotations.

Open Scope Q_scope.

(* The exact finite partial energy Σ_{k} x_k² over a list of rational coordinates — precisely the
   quantity idm.hilbert_open.l2_readout / L2_readout return in their `computed_core`. *)
Definition partial_energy (xs : list Q) : Q :=
  fold_right (fun x acc => x * x + acc) 0 xs.

(* Reused, self-contained arithmetic facts (mirrors IDM_Keystone; kept local so this file is standalone). *)
Lemma Qsq_nonneg : forall x : Q, 0 <= x * x.
Proof.
  intro x. destruct (Qlt_le_dec x 0) as [Hlt | Hge].
  - assert (Hnx : 0 <= - x).
    { apply Qlt_le_weak. apply Qopp_lt_compat in Hlt.
      setoid_replace (- 0) with 0 in Hlt by ring. exact Hlt. }
    setoid_replace (x * x) with ((- x) * (- x)) by ring.
    apply Qmult_le_0_compat; exact Hnx.
  - apply Qmult_le_0_compat; exact Hge.
Qed.

Lemma Qadd_nonneg : forall a b : Q, 0 <= a -> 0 <= b -> 0 <= a + b.
Proof.
  intros a b Ha Hb.
  setoid_replace 0 with (0 + 0) by ring.
  apply Qplus_le_compat; assumption.
Qed.

(* (1) The computed partial energy is nonnegative — a real seminorm readout. *)
Theorem partial_energy_nonneg : forall xs : list Q, 0 <= partial_energy xs.
Proof.
  induction xs as [| x xs' IH]; simpl.
  - apply Qle_refl.
  - apply Qadd_nonneg; [ apply Qsq_nonneg | exact IH ].
Qed.

(* (2) Exactness over ℚ: the partial energy is additive across concatenation — no rounding, the
   readout composes exactly (this is why it is `exact`/Th_coqc, not a floating approximation). *)
Theorem partial_energy_app :
  forall xs ys : list Q,
    partial_energy (xs ++ ys) == partial_energy xs + partial_energy ys.
Proof.
  induction xs as [| x xs' IH]; intro ys; simpl.
  - rewrite Qplus_0_l. reflexivity.
  - rewrite IH. ring.
Qed.

(* (3) Monotone in N: extending the computed window by one coordinate never decreases the readout, so
   the finite Σ_{k≤N} is a monotone lower approximant climbing toward the +ℝ-Open total Σ_{k}. *)
Theorem partial_energy_monotone :
  forall (xs : list Q) (x : Q),
    partial_energy xs <= partial_energy (xs ++ [x]).
Proof.
  intros xs x.
  rewrite partial_energy_app. simpl.
  rewrite Qplus_0_r.
  setoid_replace (partial_energy xs) with (partial_energy xs + 0) at 1 by ring.
  apply Qplus_le_compat; [ apply Qle_refl | apply Qsq_nonneg ].
Qed.
