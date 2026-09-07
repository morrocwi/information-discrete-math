(* ShakeIrrational.v
   Th_coqc-tier claim, axiom-free over Z: the specific integer that arises as the
   SHAKE-constraint discriminant numerator (for the pivot-bob1 rigid-rod constraint of
   the double pendulum in exact_q_double_pendulum.py's initial condition, first Verlet
   step) is NOT a perfect square. Combined with the standard classical fact "a positive
   integer that is not a perfect square has an irrational square root" (cited, not
   re-derived here -- flagged Dr, not Th_coqc), this justifies the concrete claim that
   this simulation's SHAKE Lagrange multiplier lambda is irrational for this step --
   the central design reason (stated in prose in exact_q_double_pendulum.py's docstring)
   for using a penalty spring instead of SHAKE to stay closed over Q.

   delta_num was computed exactly in Python (fractions.Fraction) as the numerator of
     Delta = (r1free . d)^2 - (|r1free|^2 - 1)
   for r0=(0,0), r1=(3/5,-4/5), v1=(0,0), m1=1, g=981/100, tau=1/4000, l1^2=1,
   d = r1 - r0 (the SHAKE bond direction), r1free = r1 + v1*tau + (1/2)*(0,-g)*tau^2.
   See the journal for the full derivation.
*)
(* Toledo equation codes (https://github.com/morrocwi/toledo).
   Every theorem/lemma in this file is registered as a Toledo reading (root
   `information-discrete-math`, R2 extension, 2026-09-08). Identifier -> code:
     s_val -> R/P.01.v1
     squeeze -> R/P.02.v1
     delta_num_not_perfect_square -> R/P.03.v1
   Full table: docs/TOLEDO_CODES.md 
*)

Require Import ZArith.
Require Import Lia.
Open Scope Z_scope.

Definition delta_num : Z := 255999999999991338751.

(* The integer square root floor, and its neighbor, computed once by vm_compute. *)
Definition s : Z := Z.sqrt delta_num.

Lemma s_val : s = 15999999999.
Proof. vm_compute. reflexivity. Qed.

Lemma squeeze : s * s < delta_num < (s + 1) * (s + 1).
Proof. rewrite s_val. vm_compute. split; reflexivity. Qed.

Theorem delta_num_not_perfect_square : forall m : Z, m * m <> delta_num.
Proof.
  intro m.
  intro Hm.
  destruct squeeze as [Hlo Hhi].
  assert (Habs : Z.abs m * Z.abs m = delta_num).
  { rewrite <- Hm.
    destruct (Z.abs_spec m) as [[_ Heq] | [_ Heq]]; rewrite Heq; ring. }
  set (a := Z.abs m) in *.
  assert (Ha0 : 0 <= a) by (apply Z.abs_nonneg).
  destruct (Z.le_gt_cases a s) as [Hle | Hgt].
  - assert (a * a <= s * s) by (apply Z.mul_le_mono_nonneg; lia).
    lia.
  - assert (Hge : s + 1 <= a) by lia.
    assert ((s + 1) * (s + 1) <= a * a).
    { apply Z.mul_le_mono_nonneg; lia. }
    lia.
Qed.

Print Assumptions delta_num_not_perfect_square.
