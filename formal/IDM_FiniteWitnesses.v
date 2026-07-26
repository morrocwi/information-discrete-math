(* ===================================================================== *)
(*  IDM_FiniteWitnesses.v — machine-checked, axiom-free witnesses for the  *)
(*  finite (Th_coqc-elig) claims of Information Discrete Mathematics.       *)
(*  Developed by Yaoharee Lahtee. Coq 8.20. No Reals, no classical axioms:  *)
(*  every result is Closed under the global context (Print Assumptions).    *)
(*                                                                          *)
(*  Witnesses (→ textbook claim):                                           *)
(*   W1 handshake_lemma        → §15.2  (Σ deg = 2·|E|)                      *)
(*   W2 finite_yoneda          → §17.2  (an object is determined by its      *)
(*                                       admissible readouts on a finite dom)*)
(*   W3 kuratowski_pair_inj    → §10.1 Th 10.1 (ordered-pair injectivity)    *)
(*   W4 pigeonhole             → §15.3  (more distinctions than classes ⇒     *)
(*                                       a collision)                         *)
(*   W5 semiring_distrib       → §12.2  (ring/field distributive identity)    *)
(* ===================================================================== *)

Require Import List.
Require Import PeanoNat.
Require Import Lia.
Import ListNotations.

(* ---- W1  Handshake lemma (§15.2): the endpoint multiset of an edge list  *)
(*         has length 2·|E|; i.e. summing degrees double-counts each edge.   *)
Definition endpoints (edges : list (nat * nat)) : list nat :=
  flat_map (fun e => [fst e; snd e]) edges.

Theorem handshake_lemma :
  forall edges : list (nat * nat),
    length (endpoints edges) = 2 * length edges.
Proof.
  induction edges as [| e es IH]; simpl.
  - reflexivity.
  - rewrite IH. lia.
Qed.

(* ---- W2  Finite Yoneda / determination by readouts (§17.2): two objects  *)
(*         (here maps) with equal readouts on every point of a finite domain *)
(*         are indistinguishable as readout-vectors over that domain.         *)
Theorem finite_yoneda :
  forall (A B : Type) (f g : A -> B) (dom : list A),
    (forall x, In x dom -> f x = g x) ->
    map f dom = map g dom.
Proof.
  intros A B f g dom H.
  apply map_ext_in. exact H.
Qed.

(* ---- W3  Kuratowski ordered-pair injectivity (§10.1, Th 10.1).            *)
(*   Model a finite set of naturals by membership (nat -> bool up to ext).    *)
(*   Kuratowski pair (a,b) := { {a}, {a,b} }. We prove the classical          *)
(*   injectivity biconditional over nat with decidable equality.             *)
Definition sing (a : nat) : nat -> bool := fun x => Nat.eqb x a.
Definition upair (a b : nat) : nat -> bool := fun x => orb (Nat.eqb x a) (Nat.eqb x b).
(* a Kuratowski pair, as the pair of characteristic functions *)
Definition kpair (a b : nat) : (nat -> bool) * (nat -> bool) := (sing a, upair a b).

(* set extensional equality *)
Definition seteq (s t : nat -> bool) : Prop := forall x, s x = t x.

Lemma sing_eq_iff : forall a c, seteq (sing a) (sing c) <-> a = c.
Proof.
  intros a c; split.
  - intro H. specialize (H a). unfold sing in H.
    rewrite Nat.eqb_refl in H. symmetry in H.
    apply Nat.eqb_eq in H. lia.
  - intro H; subst; intro x; reflexivity.
Qed.

Theorem kuratowski_pair_inj :
  forall a b c d : nat,
    seteq (fst (kpair a b)) (fst (kpair c d)) ->
    seteq (snd (kpair a b)) (snd (kpair c d)) ->
    a = c /\ b = d.
Proof.
  intros a b c d Hfst Hsnd.
  (* first components are the singletons {a},{c} ⇒ a=c *)
  assert (Hac : a = c) by (apply sing_eq_iff; exact Hfst).
  subst c. split; [reflexivity|].
  (* second components {a,b},{a,d} agree everywhere; test at x=b and x=d *)
  unfold kpair, upair, seteq in Hsnd; simpl in Hsnd.
  destruct (Nat.eq_dec b d) as [ | Hbd]; [assumption|].
  (* evaluate at x = b : left side true ⇒ right side true ⇒ b=a or b=d *)
  specialize (Hsnd b) as Hb.
  rewrite Nat.eqb_refl in Hb.
  rewrite Bool.orb_true_r in Hb. symmetry in Hb.
  apply Bool.orb_true_iff in Hb. destruct Hb as [Hba | Hbd'].
  - (* b = a : then test at x = d, right side true ⇒ left true ⇒ d=a=b, contra *)
    apply Nat.eqb_eq in Hba. subst b.
    specialize (Hsnd d) as Hd.
    rewrite Nat.eqb_refl in Hd. rewrite Bool.orb_true_r in Hd.
    apply Bool.orb_true_iff in Hd. destruct Hd as [Hda | Hdd].
    + apply Nat.eqb_eq in Hda. lia.
    + apply Nat.eqb_eq in Hdd. lia.
  - apply Nat.eqb_eq in Hbd'. lia.
Qed.

(* ---- W4  Pigeonhole (§15.3): a list of classes, each < n, longer than n,  *)
(*         must repeat a class. Stated via NoDup: no duplicate-free list of   *)
(*         values < n can exceed length n.                                    *)
Theorem pigeonhole :
  forall (l : list nat) (n : nat),
    (forall x, In x l -> x < n) ->
    NoDup l ->
    length l <= n.
Proof.
  intros l n Hbound Hnodup.
  (* l is a NoDup list all of whose elements are in seq 0 n; hence
     length l <= length (seq 0 n) = n. *)
  assert (Hincl : incl l (seq 0 n)).
  { intros x Hx. apply in_seq. split; [lia|]. simpl. specialize (Hbound x Hx). lia. }
  apply NoDup_incl_length in Hincl; [| exact Hnodup].
  rewrite length_seq in Hincl. exact Hincl.
Qed.

(* ---- W5  Semiring distributive identity (§12.2): D≅nat carries ⊗ over ⊕.  *)
Theorem semiring_distrib :
  forall a b c : nat, a * (b + c) = a * b + a * c.
Proof. intros; lia. Qed.

(* Sanity: the five results are independent of any axiom (checked in the
   companion Print Assumptions run). *)
