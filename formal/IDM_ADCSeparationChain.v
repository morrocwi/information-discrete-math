(* ===================================================================== *)
(* IDM_ADCSeparationChain.v                                               *)
(* Candidate-adaptive defect hitting -> SAT notin P/poly transfer.         *)
(*                                                                       *)
(* Correct quantifier pattern for nonuniform separation:                    *)
(*   for every declared polynomial bound p,                                *)
(*   there exists an input length n such that                               *)
(*   every candidate of size <= p(n) has a verified local defect.           *)
(*                                                                       *)
(* This rules out an exact polynomial-size candidate family.                *)
(* The theorem is a transfer kernel only.  The load-bearing OPEN premise is  *)
(* constructing/proving the outer hit for unrestricted SAT circuits without *)
(* a SAT/equivalence oracle.                                                *)
(* ===================================================================== *)

From Coq Require Import Bool.Bool Arith.Arith.

Module ADCSeparationChain.

Section Chain.

  Variable Candidate Cert : nat -> Type.
  Variable csize : forall n, Candidate n -> nat.
  Variable exact_sat : forall n, Candidate n -> Prop.
  Variable verify : forall n, Candidate n -> Cert n -> bool.
  Variable PolyBound : (nat -> nat) -> Prop.

  Definition CandidateFamily : Type := forall n, Candidate n.

  Definition SAT_in_Ppoly : Prop :=
    exists (fam : CandidateFamily) (p : nat -> nat),
      PolyBound p /\
      (forall n, csize n (fam n) <= p n) /\
      (forall n, exact_sat n (fam n)).

  Hypothesis verified_defect_sound :
    forall n (c : Candidate n) (z : Cert n),
      verify n c z = true ->
      ~ exact_sat n c.

  Hypothesis outer_hit_for_every_polynomial_budget :
    forall p,
      PolyBound p ->
      exists n,
        forall c : Candidate n,
          csize n c <= p n ->
          exists z : Cert n,
            verify n c z = true.

  Theorem outer_hit_implies_SAT_notin_Ppoly :
    ~ SAT_in_Ppoly.
  Proof.
    intros [fam [p [Hp [Hsize Hexact]]]].
    destruct (outer_hit_for_every_polynomial_budget p Hp) as [n Hhit].
    destruct (Hhit (fam n) (Hsize n)) as [z Hv].
    pose proof (verified_defect_sound n (fam n) z Hv) as Hnotexact.
    exact (Hnotexact (Hexact n)).
  Qed.

  Variable P_eq_NP : Prop.

  (* Standard external complexity-class implication, isolated as a premise:
       P=NP -> SAT in P -> SAT in P/poly. *)
  Hypothesis P_eq_NP_implies_SAT_in_Ppoly :
    P_eq_NP -> SAT_in_Ppoly.

  Theorem outer_hit_implies_P_neq_NP :
    ~ P_eq_NP.
  Proof.
    intro Hpeq.
    apply outer_hit_implies_SAT_notin_Ppoly.
    now apply P_eq_NP_implies_SAT_in_Ppoly.
  Qed.

End Chain.

Print Assumptions outer_hit_implies_SAT_notin_Ppoly.
Print Assumptions outer_hit_implies_P_neq_NP.

End ADCSeparationChain.
