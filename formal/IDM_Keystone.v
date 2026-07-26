(* ===================================================================== *)
(*  IDM_Keystone.v — machine-checked, axiom-free proof of the operator     *)
(*  keystone  B(Φ,Φ) = I(Φ)  (§5.1 Th 5.1): the Laplacian quadratic form    *)
(*  (Dirichlet energy of the retained-information operator L_R = D_W − W)   *)
(*  EQUALS the retained information — the total weighted squared retained   *)
(*  difference across the graph.                                            *)
(*                                                                          *)
(*  Developed by Yaoharee Lahtee. Coq 8.20, over ℚ, no Reals / no classical *)
(*  axioms: Print Assumptions = "Closed under the global context".          *)
(*                                                                          *)
(*  Model. A weighted graph is a list of edges (i,j,w). For an edge with    *)
(*  incidence vector b = e_i − e_j, the Laplacian is L = Σ_edges w·b·bᵀ,    *)
(*  so ΦᵀLΦ = Σ_edges w·(bᵀΦ)² = Σ_edges w·(Φ_i − Φ_j)². We define the      *)
(*  quadratic form by its assembled bilinear expansion (degree terms        *)
(*  w·Φ_i² + w·Φ_j² on the diagonal of D_W, and the off-diagonal −2w·Φ_iΦ_j *)
(*  from −W), and prove it equals the retained-information sum edge by edge. *)
(* ===================================================================== *)

Require Import List.
Require Import QArith.
Import ListNotations.
Open Scope Q_scope.

Definition edge := (nat * nat * Q)%type.        (* (i, j, weight) *)
Definition Phi := nat -> Q.

(* B(Φ,Φ) per edge: the assembled Laplacian bilinear form Φᵀ(w·b bᵀ)Φ,
   written as the degree diagonal (w·Φi² + w·Φj²) minus the 2·off-diagonal
   (2·w·ΦiΦj) — exactly the entries L_R contributes for this edge. *)
Definition B_edge (phi : Phi) (e : edge) : Q :=
  let '(i, j, w) := e in
  w * (phi i) * (phi i) + w * (phi j) * (phi j) - (2 # 1) * w * (phi i) * (phi j).

(* I(Φ) per edge: the retained information = weighted squared retained difference. *)
Definition I_edge (phi : Phi) (e : edge) : Q :=
  let '(i, j, w) := e in  w * ((phi i - phi j) * (phi i - phi j)).

(* The keystone, per edge: Dirichlet form = retained information. *)
Lemma keystone_edge : forall phi e, B_edge phi e == I_edge phi e.
Proof.
  intros phi [[i j] w]. unfold B_edge, I_edge. ring.
Qed.

(* Assemble over the whole graph. *)
Definition B_form (phi : Phi) (g : list edge) : Q :=
  fold_right (fun e acc => B_edge phi e + acc) 0 g.
Definition I_form (phi : Phi) (g : list edge) : Q :=
  fold_right (fun e acc => I_edge phi e + acc) 0 g.

(* KEYSTONE (Th 5.1):  B(Φ,Φ) = I(Φ)  for every graph and every field Φ. *)
Theorem keystone_B_eq_I :
  forall (phi : Phi) (g : list edge), B_form phi g == I_form phi g.
Proof.
  intros phi g. induction g as [| e es IH]; simpl.
  - reflexivity.
  - rewrite keystone_edge, IH. reflexivity.
Qed.

(* Corollary: retained information is nonnegative when all weights are —
   B(Φ,Φ) = Σ w·(Φi−Φj)² ≥ 0, so L_R is positive semidefinite (the retained
   metric is a genuine seminorm). *)
Lemma Qsq_nonneg : forall x : Q, 0 <= x * x.
Proof.
  intro x. destruct (Qlt_le_dec x 0) as [Hlt | Hge].
  - assert (Hnx : 0 <= - x).
    { apply Qlt_le_weak. apply Qopp_lt_compat in Hlt.
      setoid_replace (- 0) with 0 in Hlt by ring. exact Hlt. }
    setoid_replace (x * x) with ((- x) * (- x)) by ring.
    apply Qmult_le_0_compat; exact Hnx.
  - apply Qmult_le_0_compat; exact Hge.
Qed.

Lemma Qadd_nonneg : forall a b : Q, 0 <= a -> 0 <= b -> 0 <= a + b.
Proof.
  intros a b Ha Hb.
  setoid_replace 0 with (0 + 0) by ring.
  apply Qplus_le_compat; assumption.
Qed.

Lemma I_edge_nonneg :
  forall phi e, (let '(_,_,w) := e in 0 <= w) -> 0 <= I_edge phi e.
Proof.
  intros phi [[i j] w] Hw. unfold I_edge.
  apply Qmult_le_0_compat; [exact Hw | apply Qsq_nonneg].
Qed.

Theorem keystone_nonneg :
  forall (phi : Phi) (g : list edge),
    (forall e, In e g -> let '(_,_,w) := e in 0 <= w) ->
    0 <= B_form phi g.
Proof.
  intros phi g Hw. rewrite keystone_B_eq_I.
  induction g as [| e es IH]; simpl.
  - apply Qle_refl.
  - apply Qadd_nonneg.
    + apply I_edge_nonneg. apply Hw. left; reflexivity.
    + apply IH. intros e' Hin. apply Hw. right; exact Hin.
Qed.
