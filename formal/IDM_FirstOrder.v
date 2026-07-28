(* ===================================================================== *)
(*  IDM_FirstOrder.v — finite first-order satisfaction ⊨_λ is DECIDABLE via   *)
(*  forallb/existsb, machine-checked and axiom-free (Coq 8.20; Print          *)
(*  Assumptions = Closed under the global context).  By Yaoharee Lahtee.      *)
(*                                                                          *)
(*  v-proofs upgrade for textbook §10.3, Th 10.6.  The PROPOSITIONAL fragment *)
(*  of ⊨_λ was already machine-checked (formal/IDM_Logic.v: finite_satisfaction_dec).*)
(*  The remaining piece was the FIRST-ORDER quantifier-over-finite-domain      *)
(*  recursion — stated `Th_coqc`-eligible (decidable by finite forallb/existsb,  *)
(*  not yet formalized there).  Here it is formalized.                         *)
(*                                                                          *)
(*  A quantifier ranges over a FINITE domain `dom : list D` (the readout      *)
(*  discipline: no completed infinite domain).  `eval` is a total boolean      *)
(*  Tarski recursion — ∀ becomes `forallb`, ∃ becomes `existsb` — and         *)
(*  `eval_correct` proves it sound and complete for the Prop-level relation    *)
(*  `Sat`.  Decidability of ⊨_λ (`sat_fo_decidable`) is then immediate: a      *)
(*  finite first-order sentence over a finite domain is decided by computation, *)
(*  with NO appeal to a completed model — the honest content of "⊨_λ decidable".*)
(* ===================================================================== *)

Require Import List.
Require Import Bool.
Import ListNotations.

Section FirstOrder.
  Variable D : Type.                      (* the finite domain of individuals *)

  (* First-order formulas.  Atoms read the current environment (the stack of   *)
  (* bound individuals, innermost first); a quantifier pushes one individual.   *)
  Inductive form : Type :=
  | Atom : (list D -> bool) -> form       (* a decidable atomic predicate on the env *)
  | Neg  : form -> form
  | Conj : form -> form -> form
  | Disj : form -> form -> form
  | All  : form -> form                   (* ∀ x ∈ dom, ... (x pushed onto env) *)
  | Ex   : form -> form.                  (* ∃ x ∈ dom, ... *)

  (* the boolean Tarski recursion: ∀ ↦ forallb, ∃ ↦ existsb over the finite dom. *)
  Fixpoint eval (dom : list D) (f : form) (env : list D) : bool :=
    match f with
    | Atom p   => p env
    | Neg g    => negb (eval dom g env)
    | Conj g h => eval dom g env && eval dom h env
    | Disj g h => eval dom g env || eval dom h env
    | All g    => forallb (fun d => eval dom g (d :: env)) dom
    | Ex  g    => existsb (fun d => eval dom g (d :: env)) dom
    end.

  (* the Prop-level satisfaction relation it is meant to decide. *)
  Fixpoint Sat (dom : list D) (f : form) (env : list D) : Prop :=
    match f with
    | Atom p   => p env = true
    | Neg g    => ~ Sat dom g env
    | Conj g h => Sat dom g env /\ Sat dom h env
    | Disj g h => Sat dom g env \/ Sat dom h env
    | All g    => forall d, In d dom -> Sat dom g (d :: env)
    | Ex  g    => exists d, In d dom /\ Sat dom g (d :: env)
    end.

  (* ---- eval is SOUND and COMPLETE for Sat: the boolean recursion decides the *)
  (*      finite first-order satisfaction, quantifiers included. --------------- *)
  Theorem eval_correct :
    forall f dom env, eval dom f env = true <-> Sat dom f env.
  Proof.
    induction f; intros dom env; simpl.
    - (* Atom *) reflexivity.
    - (* Neg *) rewrite negb_true_iff. split.
      + intros Hf Hs. apply IHf in Hs. rewrite Hs in Hf. discriminate.
      + intro Hns. destruct (eval dom f env) eqn:E; [ exfalso; apply Hns; apply IHf; exact E | reflexivity ].
    - (* Conj *) rewrite andb_true_iff, IHf1, IHf2. reflexivity.
    - (* Disj *) rewrite orb_true_iff, IHf1, IHf2. reflexivity.
    - (* All *) rewrite forallb_forall. split.
      + intros H d Hd. apply IHf. apply H. exact Hd.
      + intros H d Hd. apply IHf. apply H. exact Hd.
    - (* Ex *) rewrite existsb_exists. split.
      + intros [d [Hd He]]. exists d. split; [ exact Hd | apply IHf; exact He ].
      + intros [d [Hd Hs]]. exists d. split; [ exact Hd | apply IHf; exact Hs ].
  Qed.

  (* ---- Th 10.6 (first-order): ⊨_λ over a finite domain is DECIDABLE — a       *)
  (*      finite first-order sentence is decided by computation, no completed    *)
  (*      model invoked. ------------------------------------------------------- *)
  Theorem sat_fo_decidable :
    forall f dom env, {Sat dom f env} + {~ Sat dom f env}.
  Proof.
    intros f dom env. destruct (eval dom f env) eqn:E.
    - left. apply eval_correct. exact E.
    - right. intro Hs. apply eval_correct in Hs. rewrite Hs in E. discriminate.
  Qed.

  (* a sentence is evaluated in the empty environment; its truth is decidable.   *)
  Definition Models (dom : list D) (f : form) : Prop := Sat dom f [].

  Corollary models_decidable :
    forall dom f, {Models dom f} + {~ Models dom f}.
  Proof. intros dom f. apply sat_fo_decidable. Qed.

End FirstOrder.
