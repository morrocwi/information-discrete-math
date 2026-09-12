(* ===================================================================== *)
(* IDM_SATNotInPpolyImpliesPneqNP.v                                      *)
(* Logical separation kernel: SAT notin P/poly -> P <> NP.                *)
(*                                                                       *)
(* The complexity-theoretic content is supplied as two standard premises: *)
(*   1. P = NP  -> SAT in P,                                               *)
(*      because SAT is in NP (indeed NP-complete);                         *)
(*   2. SAT in P -> SAT in P/poly, because uniform polynomial time gives  *)
(*      polynomial-size circuit families.                                 *)
(*                                                                       *)
(* The theorem below machine-checks only the final logical transfer.       *)
(* It does NOT prove SAT notin P/poly; that remains the load-bearing OPEN  *)
(* circuit-lower-bound statement in this research lane.                   *)
(* ===================================================================== *)

Module SATNotInPpolyImpliesPneqNP.

Section Separation.

  Variables P_eq_NP SAT_in_P SAT_in_Ppoly : Prop.

  Hypothesis P_eq_NP_implies_SAT_in_P :
    P_eq_NP -> SAT_in_P.

  Hypothesis SAT_in_P_implies_SAT_in_Ppoly :
    SAT_in_P -> SAT_in_Ppoly.

  Theorem SAT_notin_Ppoly_implies_P_neq_NP :
    ~ SAT_in_Ppoly ->
    ~ P_eq_NP.
  Proof.
    intros Hnot Hpeq.
    apply Hnot.
    apply SAT_in_P_implies_SAT_in_Ppoly.
    apply P_eq_NP_implies_SAT_in_P.
    exact Hpeq.
  Qed.

  Theorem contrapositive_P_eq_NP_implies_SAT_in_Ppoly :
    P_eq_NP -> SAT_in_Ppoly.
  Proof.
    intro Hpeq.
    apply SAT_in_P_implies_SAT_in_Ppoly.
    now apply P_eq_NP_implies_SAT_in_P.
  Qed.

End Separation.

Print Assumptions SAT_notin_Ppoly_implies_P_neq_NP.
Print Assumptions contrapositive_P_eq_NP_implies_SAT_in_Ppoly.

End SATNotInPpolyImpliesPneqNP.
