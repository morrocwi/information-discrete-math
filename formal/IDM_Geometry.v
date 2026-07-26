(* ===================================================================== *)
(*  IDM_Geometry.v — the exact orientation predicate, machine-checked.      *)
(*  Coq 8.20, axiom-free (Closed under the global context). Yaoharee Lahtee. *)
(*                                                                          *)
(*  This is the Coq end-to-end backing for a *solver method*: idm.geometry  *)
(*  decides which-side / inside / do-they-cross by the SIGN of the exact    *)
(*  rational orientation determinant                                        *)
(*     Orient a b c = (bx-ax)(cy-ay) - (by-ay)(cx-ax).                       *)
(*  The combinatorial guarantees the geometry solver relies on are exactly  *)
(*  the algebraic laws of this determinant — proven here over ℚ, so the     *)
(*  sign the code branches on is provably well-defined and provably 0 on    *)
(*  the boundary (which is why point_in_polygon can report on_boundary       *)
(*  exactly, with no epsilon). Only the exact/discrete predicate is claimed  *)
(*  here; the numeric readouts (quadrature, ODE) remain finite_diagnostic    *)
(*  and are deliberately NOT asserted machine-checked.                       *)
(*                                                                          *)
(*   orient_swap_bc        swapping the last two vertices negates it         *)
(*   orient_swap_ab        swapping the first two vertices negates it        *)
(*   orient_cyclic         invariant under cyclic rotation of vertices       *)
(*   orient_coincident_*   coincident vertices ⇒ exactly 0 (degenerate)      *)
(*   orient_translation    coordinate-frame independent (translation)        *)
(*   orient_scale          positive scaling preserves the sign               *)
(*   orient_collinear_mid  the midpoint of a,b is collinear ⇒ exactly 0      *)
(*   orient_collinear_aff  any affine combination on line a,b ⇒ exactly 0    *)
(* ===================================================================== *)

Require Import QArith.
Open Scope Q_scope.

(* twice the signed area of triangle (a,b,c) — the exact orientation determinant *)
Definition Orient (ax ay bx by_ cx cy : Q) : Q :=
  (bx - ax) * (cy - ay) - (by_ - ay) * (cx - ax).

(* swapping the last two vertices flips orientation (CCW ↔ CW) *)
Lemma orient_swap_bc : forall ax ay bx by_ cx cy,
  Orient ax ay cx cy bx by_ == - Orient ax ay bx by_ cx cy.
Proof. intros; unfold Orient; ring. Qed.

(* swapping the first two vertices also flips orientation *)
Lemma orient_swap_ab : forall ax ay bx by_ cx cy,
  Orient bx by_ ax ay cx cy == - Orient ax ay bx by_ cx cy.
Proof. intros; unfold Orient; ring. Qed.

(* cyclic rotation of the three vertices leaves orientation unchanged (hull winding) *)
Lemma orient_cyclic : forall ax ay bx by_ cx cy,
  Orient ax ay bx by_ cx cy == Orient bx by_ cx cy ax ay.
Proof. intros; unfold Orient; ring. Qed.

(* coincident first/second vertex ⇒ degenerate, exactly zero *)
Lemma orient_coincident_ab : forall ax ay cx cy,
  Orient ax ay ax ay cx cy == 0.
Proof. intros; unfold Orient; ring. Qed.

(* coincident first/third vertex ⇒ exactly zero *)
Lemma orient_coincident_ac : forall ax ay bx by_,
  Orient ax ay bx by_ ax ay == 0.
Proof. intros; unfold Orient; ring. Qed.

(* coincident second/third vertex ⇒ exactly zero *)
Lemma orient_coincident_bc : forall ax ay bx by_,
  Orient ax ay bx by_ bx by_ == 0.
Proof. intros; unfold Orient; ring. Qed.

(* translating all three points by the same vector does not change orientation:
   the predicate is coordinate-frame independent *)
Lemma orient_translation : forall ax ay bx by_ cx cy tx ty,
  Orient (ax + tx) (ay + ty) (bx + tx) (by_ + ty) (cx + tx) (cy + ty)
    == Orient ax ay bx by_ cx cy.
Proof. intros; unfold Orient; ring. Qed.

(* uniform scaling by s multiplies the determinant by s²; a strictly positive scale
   therefore preserves the SIGN the solver branches on *)
Lemma orient_scale : forall s ax ay bx by_ cx cy,
  Orient (s*ax) (s*ay) (s*bx) (s*by_) (s*cx) (s*cy)
    == (s * s) * Orient ax ay bx by_ cx cy.
Proof. intros; unfold Orient; ring. Qed.

(* the midpoint of a and b lies on line ab: the predicate returns EXACTLY 0 there —
   this is the boundary case point_in_polygon detects with no tolerance *)
Lemma orient_collinear_mid : forall ax ay bx by_,
  Orient ax ay bx by_ ((ax + bx) / (2#1)) ((ay + by_) / (2#1)) == 0.
Proof. intros; unfold Orient; field. Qed.

(* general collinearity: any affine combination c = a + t·(b - a) lies on line ab,
   so orientation is exactly 0 for every rational parameter t *)
Lemma orient_collinear_aff : forall ax ay bx by_ t,
  Orient ax ay bx by_ (ax + t*(bx - ax)) (ay + t*(by_ - ay)) == 0.
Proof. intros; unfold Orient; ring. Qed.
