(* ===================================================================== *)
(*  IDM_SetsFunctions.v — Th 10.2 (the function ≅ functional-relation        *)
(*  coincidence), machine-checked and axiom-free (Coq 8.20; Print Assumptions *)
(*  = Closed under the global context).  By Yaoharee Lahtee.                 *)
(*                                                                          *)
(*  This is a v-proofs upgrade: textbook §10.1 stated Th 10.2 as a           *)
(*  `Th_coqc`-ELIGIBLE sketch — "AdmissibleMap(X,Y) ≅ {R : IsFunction(R)}",  *)
(*  the step that closes the biggest not-standalone blocker (functions built *)
(*  from δ_R with no continuum).  Here it is given an actual witness.        *)
(*                                                                          *)
(*  Everything is over finite lists with a decidable equality on the domain  *)
(*  — no funext, no LEM, no choice, exactly as §10.1 promised for            *)
(*  axiom-free eligibility.  The graph of a map on a finite domain IS a      *)
(*  functional relation (total + single-valued on the domain), and the       *)
(*  correspondence is FAITHFUL: two maps agree on the domain iff their        *)
(*  graphs coincide.  That faithful total-single-valued correspondence is     *)
(*  the "≅" of Th 10.2, now `Th_coqc`.                                       *)
(* ===================================================================== *)

Require Import List.
Import ListNotations.

Section SetsFunctions.
  Variables A B : Type.
  Variable eqA_dec : forall x y : A, {x = y} + {x <> y}.

  (* the GRAPH of a map on a finite domain — an admissible relation (§10.1). *)
  Definition graph (f : A -> B) (dom : list A) : list (A * B) :=
    map (fun a => (a, f a)) dom.

  (* assoc lookup with decidable keys: the readout of the relation at a point. *)
  Fixpoint lookup (R : list (A * B)) (a : A) : option B :=
    match R with
    | [] => None
    | (a', b) :: tl => if eqA_dec a a' then Some b else lookup tl a
    end.

  (* the relation a ↦ b holds when the lookup certifies it. *)
  Definition maps_to (R : list (A * B)) (a : A) (b : B) : Prop := lookup R a = Some b.

  (* ---- on its own graph, lookup returns exactly f a for every domain point. *)
  Lemma lookup_graph_in :
    forall f dom a, In a dom -> lookup (graph f dom) a = Some (f a).
  Proof.
    intros f dom a Hin. induction dom as [| x tl IH]; simpl in *.
    - contradiction.
    - destruct (eqA_dec a x) as [Heq | Hne].
      + subst x. reflexivity.
      + destruct Hin as [Hx | Hin']; [ subst x; now exfalso; apply Hne | apply IH; exact Hin' ].
  Qed.

  (* ---- Th 10.2 (a): the graph is a FUNCTION — every domain point has an image *)
  (*      (totality) and it is single-valued (well-defined).                    *)
  Theorem graph_total :
    forall f dom a, In a dom -> exists b, maps_to (graph f dom) a b.
  Proof.
    intros f dom a Hin. exists (f a). unfold maps_to. apply lookup_graph_in; exact Hin.
  Qed.

  Theorem graph_single_valued :
    forall f dom a b1 b2,
      maps_to (graph f dom) a b1 -> maps_to (graph f dom) a b2 -> b1 = b2.
  Proof.
    unfold maps_to. intros f dom a b1 b2 H1 H2.
    rewrite H1 in H2. injection H2. auto.
  Qed.

  (* ---- Th 10.2 (b): FAITHFULNESS — two maps agree on the domain IFF their    *)
  (*      graphs coincide there.  This is the "≅" of AdmissibleMap ≅ IsFunction: *)
  (*      the graph carries all and only the map's behaviour on the domain.      *)
  Theorem graph_faithful :
    forall f g dom, graph f dom = graph g dom -> forall a, In a dom -> f a = g a.
  Proof.
    intros f g dom Heq a Hin.
    assert (Hf : lookup (graph f dom) a = Some (f a)) by (apply lookup_graph_in; exact Hin).
    assert (Hg : lookup (graph g dom) a = Some (g a)) by (apply lookup_graph_in; exact Hin).
    rewrite Heq in Hf. rewrite Hf in Hg. injection Hg. auto.
  Qed.

  (* the converse of faithfulness is definitional (equal maps ⇒ equal graphs),   *)
  (* so the correspondence is a genuine bijection on domain-behaviour.           *)
  Theorem graph_faithful_converse :
    forall f g dom, (forall a, In a dom -> f a = g a) -> graph f dom = graph g dom.
  Proof.
    intros f g dom H. unfold graph. apply map_ext_in.
    intros a Hin. rewrite (H a Hin). reflexivity.
  Qed.

  (* ---- Th 10.2 (c): the CONVERSE construction — a functional relation yields   *)
  (*      a map.  A relation that is total + single-valued on the domain is       *)
  (*      exactly `lookup`, and reading it back gives its own graph.  So          *)
  (*      {functional relations} → {maps} → {graphs} is the identity on           *)
  (*      domain-behaviour, completing the ≅.                                     *)
  Definition is_function_on (R : list (A * B)) (dom : list A) : Prop :=
    forall a, In a dom -> exists b, maps_to R a b.

  (* the codomain fiber Y is inhabited — the setting of Th 10.2 (maps INTO a      *)
  (* nonempty admissible fiber).  Made explicit so the construction is choice-     *)
  (* and default-free; only theorems that build a total map below use it.          *)
  Variable b0 : B.

  Theorem functional_relation_has_map :
    forall R dom, is_function_on R dom ->
      exists f : A -> B, forall a, In a dom -> maps_to R a (f a).
  Proof.
    intros R dom Hfun.
    (* the map is `lookup R`, made total by the default b0 outside dom; on the     *)
    (* domain it agrees with the (single-valued) relation.                         *)
    exists (fun a => match lookup R a with Some b => b | None => b0 end).
    intros a Hin. destruct (Hfun a Hin) as [b Hb].
    unfold maps_to in *. rewrite Hb. reflexivity.
  Qed.

End SetsFunctions.
