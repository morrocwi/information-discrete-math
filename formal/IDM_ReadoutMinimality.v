(* ===================================================================== *)
(*  IDM_ReadoutMinimality.v — the minimal value-set of a signed readout,   *)
(*  machine-checked locally and axiom-free (Coq 8.20; Print Assumptions =   *)
(*  Closed under the global context).  By Yaoharee Lahtee.                  *)
(*                                                                          *)
(*  This certifies exactly the TWO results in the readout-mathematics brief *)
(*  that are PROVED there (not the P1..P10 conjectures, which stay open):   *)
(*                                                                          *)
(*   T1  (Theorem 1, minimal cardinality).  A total, involution-equivariant *)
(*       signed readout that separates at least one object from its negative *)
(*       needs at least THREE distinct values — and the third is forced to be *)
(*       a fixed point of the sign-involution (the neutral).  Two values      *)
(*       cannot report a self-negative object without lying.                  *)
(*                                                                          *)
(*   D0  (the 0 / bottom separation).  The neutral 0 (determinately balanced *)
(*       — a fact about the OBJECT) and the unresolved bottom (the declared   *)
(*       resolution does not decide — a fact about the INSTRUMENT) are two    *)
(*       DISTINCT fixed points of the involution, on two different axes: 0 is *)
(*       incomparable in the information order, bottom is its least element.  *)
(*       A readout that maps both to one symbol destroys a real distinction. *)
(*       This is why the value algebra is four-valued, not three.            *)
(*                                                                          *)
(*  Everything below is finite and decidable, so it is Th_coqc (machine-     *)
(*  checked, axiom-free) — the strongest tier this repository certifies.     *)
(* ===================================================================== *)

(* ---------------------------------------------------------------------- *)
(*  The four-element value algebra  S4 = { Sp (+), Sm (-), Sz (0), Sbot }. *)
(* ---------------------------------------------------------------------- *)
Inductive S4 : Type := Sp | Sm | Sz | Sbot.

(* the sign-involution ¬ : + <-> -, and it FIXES both neutral 0 and bottom. *)
Definition neg (v : S4) : S4 :=
  match v with
  | Sp   => Sm
  | Sm   => Sp
  | Sz   => Sz
  | Sbot => Sbot
  end.

(* neg is an involution.                                                    *)
Theorem neg_involution : forall v, neg (neg v) = v.
Proof. intro v; destruct v; reflexivity. Qed.

(* the fixed points of neg are EXACTLY the two neutral values.              *)
Theorem neg_fixed_iff : forall v, neg v = v <-> (v = Sz \/ v = Sbot).
Proof.
  intro v; split.
  - destruct v; simpl; intro H;
      [ discriminate H | discriminate H | now left | now right ].
  - intros [H | H]; subst; reflexivity.
Qed.

(* the moving points are EXACTLY the two signs.                             *)
Theorem neg_moves_iff : forall v, neg v <> v <-> (v = Sp \/ v = Sm).
Proof.
  intro v; split.
  - destruct v; simpl; intro H;
      [ now left | now right | now exfalso; apply H | now exfalso; apply H ].
  - intros [H | H]; subst; discriminate.
Qed.

(* ---------------------------------------------------------------------- *)
(*  T1 · Theorem 1 — a signed readout needs at least THREE distinct values. *)
(*                                                                          *)
(*  We model the source generally: a set A with a sign-flip involution `op` *)
(*  (op(op a) = a) that has at least one fixed point x0 (the self-negative  *)
(*  object). A readout r : A -> S4 is EQUIVARIANT (r(op a) = neg (r a)) and *)
(*  NON-DEGENERATE (it separates some a from op a). The theorem forces      *)
(*  three pairwise-distinct readout values — no continuum, no ambient reals, *)
(*  just the counting of what an equivariant map must hit.                  *)
(* ---------------------------------------------------------------------- *)
Section MinimalReadout.
  Variable A : Type.
  Variable op : A -> A.                       (* the object-level sign flip x |-> -x *)
  Hypothesis op_involution : forall a, op (op a) = a.
  Variable x0 : A.                            (* a self-negative object: -x0 = x0     *)
  Hypothesis x0_selfneg : op x0 = x0.

  Variable r : A -> S4.                        (* the readout *)
  Hypothesis equivariant : forall a, r (op a) = neg (r a).
  Hypothesis nondegenerate : exists a, r a <> r (op a).

  (* the self-negative object is read as a fixed point of neg (a neutral).    *)
  Lemma readout_of_selfneg_is_neutral : neg (r x0) = r x0.
  Proof.
    (* neg (r x0) = r (op x0) = r x0 *)
    rewrite <- equivariant. rewrite x0_selfneg. reflexivity.
  Qed.

  (* THEOREM 1.  Three readout values are forced, and they are pairwise       *)
  (* distinct: the separated object, its negative, and the self-negative one. *)
  Theorem minimal_three_values :
    exists a b c : A,
      r a <> r b /\ r a <> r c /\ r b <> r c.
  Proof.
    destruct nondegenerate as [a Ha].       (* r a <> r (op a) *)
    exists a, (op a), x0.
    (* r (op a) = neg (r a); r a is a moving point; r x0 is a fixed point. *)
    assert (Hmov : neg (r a) <> r a).
    { rewrite equivariant in Ha. intro Hc. apply Ha. symmetry. exact Hc. }
    assert (Hfix : neg (r x0) = r x0) by exact readout_of_selfneg_is_neutral.
    split; [| split].
    - (* r a <> r (op a) *) exact Ha.
    - (* r a <> r x0 : a moving point can't equal a fixed point *)
      intro Hc. apply Hmov. rewrite Hc. exact Hfix.
    - (* r (op a) <> r x0 : neg(r a) moves, r x0 is fixed *)
      rewrite equivariant. intro Hc.
      (* if neg (r a) = r x0 then neg (r a) is fixed, but it moves *)
      assert (Hmov2 : neg (neg (r a)) <> neg (r a)).
      { rewrite neg_involution. intro Hd. apply Hmov. symmetry. exact Hd. }
      apply Hmov2. rewrite Hc. exact Hfix.
  Qed.

  (* the forced third value is a fixed point of the sign-involution — i.e. a  *)
  (* NEUTRAL (Sz or Sbot), never a strict sign.  This is the content that a    *)
  (* two-valued signed readout cannot honour.                                  *)
  Theorem third_value_is_neutral : r x0 = Sz \/ r x0 = Sbot.
  Proof. apply neg_fixed_iff. exact readout_of_selfneg_is_neutral. Qed.

End MinimalReadout.

(* ---------------------------------------------------------------------- *)
(*  D0 · the neutral 0 and the unresolved bottom are DISTINCT — and live on *)
(*  different axes.  Sign-involution and information-order together separate *)
(*  them; either one alone would let a three-valued reading hide the gap.    *)
(* ---------------------------------------------------------------------- *)

(* Axis 1 (the involution): both are fixed, yet they are not equal.          *)
Theorem neutral_distinct_from_bottom : Sz <> Sbot.
Proof. discriminate. Qed.

Theorem two_distinct_neutrals :
  neg Sz = Sz /\ neg Sbot = Sbot /\ Sz <> Sbot.
Proof. repeat split; discriminate. Qed.

(* Axis 2 (the information order):  x ⊑ y  iff  x is bottom or x = y.        *)
Definition sqle (x y : S4) : Prop := x = Sbot \/ x = y.

(* ⊥ is a least element: it sits below every value.                          *)
Theorem bottom_is_least : forall v, sqle Sbot v.
Proof. intro v. left. reflexivity. Qed.

(* ⊥ is the UNIQUE least element: anything below everything IS ⊥.            *)
Theorem bottom_unique : forall x, (forall v, sqle x v) -> x = Sbot.
Proof.
  intros x H.
  destruct (H Sp) as [Hb | He1].
  - exact Hb.
  - (* x = Sp; but x must also be <= Sm, impossible unless x = Sbot *)
    subst x. destruct (H Sm) as [Hb | He2]; [ exact Hb | discriminate He2 ].
Qed.

(* the determinate neutral 0 is NOT a bottom: it is INCOMPARABLE to a sign,   *)
(* so it carries information (it is a genuine reading, not "no information"). *)
Theorem neutral_is_not_below_sign : ~ sqle Sz Sp.
Proof. intros [H | H]; discriminate. Qed.

(* hence 0 and ⊥ are separated on the order axis too: 0 is not the bottom.    *)
Theorem neutral_is_not_bottom : Sz <> Sbot /\ ~ (forall v, sqle Sz v).
Proof.
  split; [ discriminate |].
  intro H. exact (neutral_is_not_below_sign (H Sp)).
Qed.
