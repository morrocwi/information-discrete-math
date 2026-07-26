(* ===================================================================== *)
(*  IDM_Logic.v — axiom-free witnesses for the logic layer:                *)
(*    W10 finite_satisfaction_dec → §10.3 (⊨_λ is a decidable, computable   *)
(*                                   Tarski recursion; finite model-checking *)
(*                                   over a finite environment set decides)  *)
(*    W11 rdl_non_explosion       → §10.4 / Part I (RDL non-explosion:       *)
(*                                   from p ∧ ¬p one may NOT derive an        *)
(*                                   arbitrary q — a 4-valued Belnap–Dunn     *)
(*                                   countermodel, the load-bearing rung)     *)
(*  Coq 8.20, Closed under the global context. Developed by Yaoharee Lahtee. *)
(* ===================================================================== *)

Require Import List Bool.
Import ListNotations.

(* ---- §10.3  Finite satisfaction ⊨_λ is decidable / computable ---- *)
Inductive form : Type :=
  | Atom : nat -> form
  | Neg  : form -> form
  | Conj : form -> form -> form
  | Disj : form -> form -> form.

Fixpoint sat (env : nat -> bool) (f : form) : bool :=
  match f with
  | Atom n   => env n
  | Neg a    => negb (sat env a)
  | Conj a b => andb (sat env a) (sat env b)
  | Disj a b => orb  (sat env a) (sat env b)
  end.

(* Satisfaction under a given environment is a decidable readout. *)
Theorem sat_dec : forall env f, {sat env f = true} + {sat env f = false}.
Proof. intros env f. destruct (sat env f); [left|right]; reflexivity. Qed.

(* Finite model-checking: validity over a FINITE environment set is decidable —
   the honest content of "⊨_λ on a finite domain + finite formula computes". *)
Theorem finite_satisfaction_dec :
  forall (f : form) (envs : list (nat -> bool)),
    {forall e, In e envs -> sat e f = true} +
    {exists e, In e envs /\ sat e f = false}.
Proof.
  intros f envs. induction envs as [| e es IH]; simpl.
  - left. intros e [].
  - destruct (sat_dec e f) as [Ht | Hf].
    + destruct IH as [Hall | Hex].
      * left. intros e' [He | He']; [subst; exact Ht | apply Hall; exact He'].
      * right. destruct Hex as [w [Hin Hw]]. exists w. split; [right; exact Hin | exact Hw].
    + right. exists e. split; [left; reflexivity | exact Hf].
Qed.

(* ---- §10.4 / Part I  RDL non-explosion (Belnap–Dunn FDE, 4-valued) ---- *)
(* Values as truth-content sets: has_t / has_f over {t,f}. T={t} F={f} B={t,f} N={}. *)
Inductive V4 : Type := VT | VF | VB | VN.
Definition hast (x : V4) : bool := match x with VT | VB => true | _ => false end.
Definition hasf (x : V4) : bool := match x with VF | VB => true | _ => false end.
Definition mk (t f : bool) : V4 :=
  match t, f with
  | true , true  => VB
  | true , false => VT
  | false, true  => VF
  | false, false => VN
  end.
Definition neg4  (x : V4)   : V4 := mk (hasf x) (hast x).
Definition conj4 (x y : V4) : V4 := mk (andb (hast x) (hast y)) (orb (hasf x) (hasf y)).
(* Designated (asserted-as-true) values: those containing t, i.e. {VT, VB}. *)
Definition designated (x : V4) : bool := hast x.

(* NON-EXPLOSION: there is a valuation where the contradiction p ∧ ¬p is designated
   yet an arbitrary q is NOT — so p ∧ ¬p does not semantically entail q. Ex falso
   is refused; this is the rung that makes RDL load-bearing (Ax-RDL3). *)
Theorem rdl_non_explosion :
  exists vp vq : V4,
    designated (conj4 vp (neg4 vp)) = true /\ designated vq = false.
Proof.
  exists VB, VN. split; reflexivity.
Qed.

(* Sanity: classical logic WOULD explode — with only {VT,VF} a contradiction is never
   designated, so the countermodel genuinely needs the extra (paraconsistent) value VB. *)
Theorem classical_would_explode :
  forall x : V4, x = VT \/ x = VF ->
    designated (conj4 x (neg4 x)) = false.
Proof. intros x [H | H]; subst; reflexivity. Qed.
