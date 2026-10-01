From Coq Require Import Lists.List Bool.Bool.
Import ListNotations.

(**
  Readout-Universe / Readout-Genesis finite kernels for the P-vs-NP lane.

  Scope:
  - root/global injective retention does not imply visible working-memory
    injectivity; if the visible component collides, an injective joint record
    must carry the distinction in the complementary tape;
  - a decoder that sees only the visible record cannot distinguish a visible
    collision;
  - a finite cover by independently sound rejection cells yields a sound
    global rejection on the declared finite witness list.

  These are structural finite theorems.  They do NOT prove a SAT lower bound,
  a circuit lower bound, or P <> NP.
*)

Section RD4Relocation.

  Variables X Visible Tape Out : Type.
  Variables visible : X -> Visible.
  Variables tape : X -> Tape.
  Variable decoder : Visible -> Out.

  Hypothesis joint_injective :
    forall x y,
      visible x = visible y ->
      tape x = tape y ->
      x = y.

  Lemma visible_collision_forces_tape_distinction :
    forall x y,
      x <> y ->
      visible x = visible y ->
      tape x <> tape y.
  Proof.
    intros x y Hneq Hvisible Htape.
    apply Hneq.
    eapply joint_injective; eauto.
  Qed.

  Lemma visible_collision_blocks_decoder_distinction :
    forall x y,
      visible x = visible y ->
      decoder (visible x) = decoder (visible y).
  Proof.
    intros x y Hvisible.
    now rewrite Hvisible.
  Qed.

End RD4Relocation.

Section FiniteAccessibleCompletion.

  Variables Witness Cell : Type.

  (** [rejects w = true] means the declared terminal predicate has an
      independently verified rejection/obstruction on witness [w]. *)
  Variable rejects : Witness -> bool.

  (** [covers c w] means witness [w] lies in certificate cell [c]. *)
  Variable covers : Cell -> Witness -> Prop.

  Variables witness_list : list Witness.
  Variables certificate : list Cell.

  Definition cell_sound (c : Cell) : Prop :=
    forall w, covers c w -> rejects w = true.

  Hypothesis all_certificate_cells_sound :
    forall c,
      In c certificate ->
      cell_sound c.

  Hypothesis certificate_covers_declared_witnesses :
    forall w,
      In w witness_list ->
      exists c,
        In c certificate /\ covers c w.

  Theorem finite_completion_sound :
    forall w,
      In w witness_list ->
      rejects w = true.
  Proof.
    intros w Hw.
    destruct (certificate_covers_declared_witnesses w Hw)
      as [c [Hc Hcw]].
    apply (all_certificate_cells_sound c Hc w Hcw).
  Qed.

  (** If the declared finite witness list is itself complete, the local-cover
      certificate proves rejection for every witness in the finite source. *)
  Hypothesis witness_list_complete :
    forall w, In w witness_list.

  Corollary global_completion_sound :
    forall w, rejects w = true.
  Proof.
    intro w.
    apply finite_completion_sound.
    apply witness_list_complete.
  Qed.

End FiniteAccessibleCompletion.

Print Assumptions visible_collision_forces_tape_distinction.
Print Assumptions visible_collision_blocks_decoder_distinction.
Print Assumptions finite_completion_sound.
Print Assumptions global_completion_sound.
