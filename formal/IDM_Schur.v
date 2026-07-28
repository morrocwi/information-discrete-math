(* ===================================================================== *)
(*  IDM_Schur.v — the Schur/boundary congruence, the algebraic atom of      *)
(*  Haynsworth inertia-additivity, machine-checked over ℚ and axiom-free     *)
(*  (Coq 8.20; Print Assumptions = Closed under the global context).         *)
(*  By Yaoharee Lahtee.                                                      *)
(*                                                                          *)
(*  THEOREM.md §"inertia is the spectral readout" reads inertia as a         *)
(*  BOUNDARY readout: by Haynsworth additivity the sign-count is additive    *)
(*  across a separator, so the object retained is the boundary, not the      *)
(*  volume.  Haynsworth is cited there as classical.  The ALGEBRAIC atom     *)
(*  that makes it true — eliminating the boundary node produces EXACTLY the   *)
(*  Schur complement, as an exact congruence — is finite and rational, and   *)
(*  is machine-checked here for the one-node boundary (2×2 block).           *)
(*                                                                          *)
(*  For a symmetric 2×2 block  A = [[a, b],[b, c]]  with pivot a ≠ 0, the     *)
(*  boundary elimination                                                     *)
(*        M = [[1, b/a],[0, 1]]     (unit upper-triangular)                   *)
(*        D = [[a, 0 ],[0, s]]      s = c − b²/a   (the Schur complement)     *)
(*  gives the exact congruence  A = Mᵀ · D · M  over ℚ (schur_congruence).    *)
(*  The pivot list of D is [a ; s], so the readout inertia (the LDLᵀ pivot-   *)
(*  sign count, §A) of D is additive across the boundary: neg-count(D) =      *)
(*  (a<0?1:0) + (s<0?1:0)  (diag_inertia_additive).                          *)
(*                                                                          *)
(*  HONEST FENCE.  This machine-checks the exact Schur *congruence* over ℚ   *)
(*  and the additivity of the pivot-count readout on the resulting diagonal. *)
(*  The step it does NOT close — that congruence PRESERVES the sign-count     *)
(*  (Sylvester's law of inertia, so that inertia(A) = inertia(D)) — is a      *)
(*  real-spectral statement, `+ℝ-Open`, cited not proved.  Within this        *)
(*  framework's own semantics inertia IS the pivot-count readout (§A), so     *)
(*  the atom below is Haynsworth-across-one-node in that readout; the         *)
(*  order-invariance and the general n-block boundary are the declared next   *)
(*  steps (see docs/P46_P5_lower_bound_analysis.md §6).                      *)
(* ===================================================================== *)

Require Import QArith.

Local Open Scope Q_scope.

Section SchurAtom.
  Variables a b c : Q.
  Hypothesis Ha : ~ a == 0.

  (* the Schur complement of the boundary node *)
  Definition schur : Q := c - b * b / a.

  (* the boundary elimination M = [[1, b/a],[0,1]] and D = diag(a, schur);
     the four entries of Mᵀ · D · M, written out. *)
  Definition MtDM (i j : nat) : Q :=
    match i, j with
    | O, O => 1 * (a * 1)                               (* (Mᵀ D M)[0,0] *)
    | O, S O => 1 * (a * (b / a))                       (* [0,1] *)
    | S O, O => (b / a) * (a * 1)                       (* [1,0] *)
    | _, _ => (b / a) * (a * (b / a)) + 1 * (schur * 1) (* [1,1] *)
    end.

  (* ---- the exact Schur congruence over ℚ: A = Mᵀ · D · M, entry by entry.  *)
  (*      The content is the b²/a cancellation in the (1,1) entry.            *)
  Theorem schur_congruence_00 : MtDM O O == a.
  Proof. unfold MtDM. ring. Qed.

  Theorem schur_congruence_01 : MtDM O (S O) == b.
  Proof. unfold MtDM. field. exact Ha. Qed.

  Theorem schur_congruence_10 : MtDM (S O) O == b.
  Proof. unfold MtDM. field. exact Ha. Qed.

  Theorem schur_congruence_11 : MtDM (S O) (S O) == c.
  Proof. unfold MtDM, schur. field. exact Ha. Qed.

End SchurAtom.

(* ---------------------------------------------------------------------- *)
(*  The readout inertia (LDLᵀ pivot-sign count, §A) is additive across the   *)
(*  boundary on the diagonal D = diag(p, q): neg-count(D) = neg(p) + neg(q). *)
(*  Trivial for a diagonal, but it is the additivity half of the atom.       *)
(* ---------------------------------------------------------------------- *)
Definition negb_pivot (p : Q) : nat := if Qlt_le_dec p 0 then 1 else 0.

Definition diag_neg_count (p q : Q) : nat := (negb_pivot p + negb_pivot q)%nat.

Theorem diag_inertia_additive :
  forall p q, diag_neg_count p q = (negb_pivot p + negb_pivot q)%nat.
Proof. reflexivity. Qed.

(* the pivot list of the boundary elimination is [a ; schur], so the readout
   inertia of the congruent diagonal is exactly this boundary sum. *)
Theorem schur_pivots_are_boundary_and_complement :
  forall a b c : Q, ~ a == 0 ->
    diag_neg_count a (schur a b c) = (negb_pivot a + negb_pivot (schur a b c))%nat.
Proof. intros a b c _. reflexivity. Qed.
