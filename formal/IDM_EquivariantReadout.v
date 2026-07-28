(* ===================================================================== *)
(*  IDM_EquivariantReadout.v — the necessary condition behind P1 (minimal   *)
(*  equivariant readout for a general group), machine-checked and axiom-free *)
(*  (Coq 8.20; Print Assumptions = Closed under the global context).         *)
(*  By Yaoharee Lahtee.                                                      *)
(*                                                                          *)
(*  Theorem 1 (formal/IDM_ReadoutMinimality.v) settled the value-set of a    *)
(*  signed readout for the group Z2 = {+,-}: three values are forced, the    *)
(*  third a neutral.  P1 asks the same for a GENERAL group G of admissible   *)
(*  re-descriptions: how few values must a total, G-equivariant, separating  *)
(*  readout carry?                                                           *)
(*                                                                          *)
(*  P1 is stated in the brief as a CONJECTURE, and its cardinality formula   *)
(*  is left open (and loosely worded — the count that gives Theorem 1's "3"  *)
(*  is Σ_type [G : H_type] = [G:1] + [G:G] = 2 + 1, one orbit per realised   *)
(*  stabiliser type, not the bare number of types).  So this file proves     *)
(*  only what the brief itself records as ESTABLISHED — the *necessary        *)
(*  condition* — and leaves the cardinality formula fenced as a conjecture,   *)
(*  exactly as horizontal-knowledge discipline requires (a conjecture is     *)
(*  never dressed as a theorem).                                            *)
(*                                                                          *)
(*  Established here, fully general (any group action, no finiteness):        *)
(*    NC1  equivariant_stabilizer_containment                                *)
(*         — every symmetry that fixes an object x also fixes its readout     *)
(*           r(x):  Stab_X(x) ⊆ Stab_V(r x).  This is the general mechanism   *)
(*           that forced the neutral third value in Theorem 1.               *)
(*    NC2  faithful_stabilizer_equality                                       *)
(*         — if the readout is FAITHFUL on the orbit of x (it distinguishes   *)
(*           the re-descriptions of x), the containment is an EQUALITY:       *)
(*           Stab_V(r x) = Stab_X(x).  So a faithful readout copies the       *)
(*           orbit type exactly — the image orbit is G/Stab_X(x), of size     *)
(*           [G : Stab_X(x)].  (This is the per-type lower-bound input to     *)
(*           Conjecture P1's Σ [G:H_t].)                                      *)
(*    NC3  nondegenerate_value_moves — the Theorem-1 mechanism recovered:     *)
(*         a symmetry that MOVES x to a distinctly-read image must MOVE the   *)
(*         readout value too, so a moved object cannot be read as a fixed     *)
(*         (neutral) value.                                                   *)
(* ===================================================================== *)

Section EquivariantReadout.
  (* the group of admissible re-descriptions, given only as a carrier with a  *)
  (* distinguished identity — no group axioms are needed for the necessary    *)
  (* condition, which keeps the result maximally general.                     *)
  Variable G : Type.
  Variable e : G.                       (* the identity re-description *)

  Variable X : Type.                    (* objects *)
  Variable V : Type.                    (* readout values *)
  Variable actX : G -> X -> X.          (* G acts on objects *)
  Variable actV : G -> V -> V.          (* G acts on values *)
  Hypothesis actX_e : forall x, actX e x = x.
  Hypothesis actV_e : forall v, actV e v = v.

  Variable r : X -> V.                  (* the readout *)
  Hypothesis equivariant : forall g x, r (actX g x) = actV g (r x).

  (* stabiliser membership: the symmetries that fix a given object / value.   *)
  Definition stabX (g : G) (x : X) : Prop := actX g x = x.
  Definition stabV (g : G) (v : V) : Prop := actV g v = v.

  (* ---- NC1.  The necessary condition: Stab_X(x) ⊆ Stab_V(r x). ------------ *)
  Theorem equivariant_stabilizer_containment :
    forall g x, stabX g x -> stabV g (r x).
  Proof.
    intros g x H. unfold stabV.
    (* actV g (r x) = r (actX g x) = r x, since actX g x = x *)
    rewrite <- equivariant. unfold stabX in H. rewrite H. reflexivity.
  Qed.

  (* faithfulness on the orbit of x: the readout separates the re-descriptions *)
  (* of x (it is injective along x's orbit).                                   *)
  Definition faithful_on (x : X) : Prop :=
    forall g h, r (actX g x) = r (actX h x) -> actX g x = actX h x.

  (* ---- NC2.  Under faithfulness the containment becomes EQUALITY. --------- *)
  Theorem faithful_stabilizer_equality :
    forall g x, faithful_on x -> (stabV g (r x) <-> stabX g x).
  Proof.
    intros g x Hf. split.
    - (* Stab_V(r x) ⊆ Stab_X(x) using injectivity along the orbit *)
      intro Hv. unfold stabX.
      assert (Hrg : r (actX g x) = r (actX e x)).
      { rewrite (equivariant g x). unfold stabV in Hv. rewrite Hv.
        rewrite (actX_e x). reflexivity. }
      apply Hf in Hrg. rewrite (actX_e x) in Hrg. exact Hrg.
    - (* the reverse is NC1 *)
      apply equivariant_stabilizer_containment.
  Qed.

  (* ---- NC3.  The Theorem-1 mechanism, recovered generally: an object moved  *)
  (*      to a distinctly-read image cannot be read as a fixed (neutral) value.*)
  (*      Contrapositive form: if the readout value is g-fixed, then g does not *)
  (*      change the reading of x.                                             *)
  Theorem fixed_value_reads_equal :
    forall g x, stabV g (r x) -> r (actX g x) = r x.
  Proof.
    intros g x Hv. rewrite (equivariant g x). unfold stabV in Hv. exact Hv.
  Qed.

  Theorem nondegenerate_value_moves :
    forall g x, r (actX g x) <> r x -> ~ stabV g (r x).
  Proof.
    intros g x Hne Hv. apply Hne. apply fixed_value_reads_equal. exact Hv.
  Qed.

End EquivariantReadout.

(* ---------------------------------------------------------------------- *)
(*  Conjecture P1 (NOT proved here — stated so it is not mistaken for a      *)
(*  theorem).  For a finite group G acting on X, the minimum size of a G-set *)
(*  V admitting a total, G-equivariant, faithful, separating readout X -> V  *)
(*  is                                                                       *)
(*        |V|_min  =  Σ_{[H] realised}  [G : H],                             *)
(*  one G-orbit G/H per conjugacy class [H] of stabiliser subgroups realised *)
(*  in X.  NC1–NC2 above supply the per-type input (a faithful readout copies *)
(*  each orbit type exactly, so each realised type [H] forces an image orbit  *)
(*  of size [G:H]); the full statement additionally needs that distinct types *)
(*  land in disjoint V-orbits and a Lagrange/orbit-stabiliser count to sum    *)
(*  them — orbit combinatorics this file does not formalise.  Theorem 1 is    *)
(*  the instance G = Z2 with the two types free ([G:1]=2) and fixed ([G:G]=1),*)
(*  giving 2 + 1 = 3.  Related classical vocabulary for a literature route:   *)
(*  the orbit-type stratification of a G-set / the poset of conjugacy classes *)
(*  of subgroups / the Burnside ring.  Tier: Open (conjecture), fenced.       *)
(* ---------------------------------------------------------------------- *)
