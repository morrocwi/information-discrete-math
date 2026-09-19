(* ===================================================================== *)
(* IDM_ProjectionCollapseGuard.v                                          *)
(* Finite guard: witness-side distinction can disappear under exists.     *)
(*                                                                       *)
(* This is a no-go theorem for complexity measures that charge witness     *)
(* diversity before existential projection.  If every source point has a  *)
(* matching witness and equality is recognized by [eqb], the existential  *)
(* projection is identically true, regardless of how many distinct        *)
(* witness slices the relation may have.                                  *)
(*                                                                       *)
(* No complexity lower bound and no P <> NP claim is made here.           *)
(* ===================================================================== *)

From Coq Require Import Lists.List Bool.Bool.
Import ListNotations.

Module ProjectionCollapseGuard.

Section Guard.

  Variable X : Type.
  Variable eqb : X -> X -> bool.
  Hypothesis eqb_refl : forall x, eqb x x = true.
  Variable witnesses : list X.
  Hypothesis complete : forall x, In x witnesses.

  Definition equality_relation (x w : X) : bool := eqb x w.

  Definition projected (x : X) : bool :=
    existsb (fun w => equality_relation x w) witnesses.

  Theorem equality_projection_constant_true :
    forall x, projected x = true.
  Proof.
    intros x.
    unfold projected, equality_relation.
    apply existsb_exists.
    exists x.
    split.
    - apply complete.
    - apply eqb_refl.
  Qed.

  Theorem projection_erases_witness_identity :
    forall x y, projected x = projected y.
  Proof.
    intros x y.
    rewrite equality_projection_constant_true.
    rewrite equality_projection_constant_true.
    reflexivity.
  Qed.

End Guard.

Print Assumptions equality_projection_constant_true.
Print Assumptions projection_erases_witness_identity.

End ProjectionCollapseGuard.
