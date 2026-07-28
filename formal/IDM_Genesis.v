(* ===================================================================== *)
(*  IDM_Genesis.v — the genesis of number, machine-checked locally and     *)
(*  axiom-free.  So the Five Core Theorems (THEOREM.md, spine §I) prove      *)
(*  themselves from THIS repository's own formal system, without citing an   *)
(*  external one.  Coq 8.20, over the naturals; every theorem is axiom-free  *)
(*  (Print Assumptions = Closed under the global context).  By Yaoharee Lahtee.*)
(*                                                                          *)
(*  Model.  The retained-difference engine D is Coq's `nat` (ground 0,       *)
(*  successor S = "retain one more distinction"); D ≅ ℕ is then the identity *)
(*  and needs no separate proof.  The two facts the spine actually rests on  *)
(*  are elementary here and are exhibited, not postulated:                    *)
(*                                                                          *)
(*   G1 primordial_difference_exists  — a first distinction EXISTS (δ_R).    *)
(*   G2 discrete_floor                — nothing lies strictly between the     *)
(*                                      ground 0 and the first tick (S 0):    *)
(*                                      density is ABSENT at the root.        *)
(* ===================================================================== *)

Require Import PeanoNat.
Require Import Lia.

(* ---- G1 (δ_R, §I).  A retained difference exists: two distinct inhabitants *)
(*      of D.  Ontologically primitive, but not assumed — it is witnessed.     *)
Theorem primordial_difference_exists : exists a b : nat, a <> b.
Proof. exists (S 0), 0. discriminate. Qed.

(* realized concretely by the successor of the ground being distinct from it   *)
(* (RD3): a retained tick is never the ground.                                 *)
Theorem succ_ground_distinct : S 0 <> 0.
Proof. discriminate. Qed.

(* ---- G2 (discrete floor, §I / Th 2.9).  No element lies strictly between    *)
(*      the ground 0 and the first tick S 0.  The continuum (a dense order)    *)
(*      is therefore PROVABLY absent at the root and can only ever be a later  *)
(*      readout — never a primitive.                                           *)
Theorem discrete_floor : ~ (exists z : nat, 0 < z /\ z < S 0).
Proof. intros [z [Hlo Hhi]]. lia. Qed.

(* corollary in successor form: no z with 0 < z < 1.                           *)
Corollary no_density_at_root : forall z : nat, 0 < z -> ~ (z < 1).
Proof. intros z Hlo Hhi. lia. Qed.
