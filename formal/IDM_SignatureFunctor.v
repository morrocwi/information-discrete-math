(*
  IDM_SignatureFunctor.v -- S2 RETAIN of the Discrete-Continuum Readout Bridge,
  as pure CIC (no QArith, no Reals, no classical import, no List beyond the
  `list Action` words already carried by IDM_ReaderDomainFoundation).

  Bridge lines covered (DISCRETE_CONTINUUM_BRIDGE_DESIGN_v0.1.md, section 2 / S2
  and the EXACT clause of S4, under the 11b rulings):

    S2  x_K := P_K x in R_K ,  P_K o P_K = P_K
        Sigma_Q(z) := ( O(z), [z]_Q ),  [z]_Q := { z' : O(F^k z') = O(F^k z), k <= L }
        admissible iff DepthStable(L) /\ P_K o F = F#_K o P_K /\ O = O# o P_K
        Alg_Q := { P : ker P_K subseteq ker P }
    S4  P o Lambda_K o P_K = P  <=>  P in Alg_Q                        [EXACT]

  Typing (ruling 11b-1, the q_K / Lambda_K / res_K split): in this file
    q_K      = `DepthClass` (Part I, Prop-valued class, no funext) and the
               abstract record map `q : S -> K` / `rk : State -> K` (Parts II, III);
    Lambda_K = the Section Variable `lam : K -> S` with the DISCLOSED hypothesis
               `Hsec : forall k, q (lam k) = k` (a section of q, i.e. a representative
               chooser -- said, not hidden);
    P_K      := `PK := lam o q : S -> S`  (Y = X = S: the endomap reading, the one
               under which `P_K o P_K = P_K` is even typable; the metric reading
               Y <> X is S3's and is not in this file);
    res_K    is not used by this file.

  Genesis sections instantiated (READOUT_GENESIS_CORE.md): A.8 (formation of the
  signature `Sigma_alpha = (O_alpha, Q_alpha)` and `Lambda_alpha o Sigma_alpha = I`;
  here `Sigma` and `PK_fixes_image` / `PK_idempotent` -- the identity holds on the
  RETAINED states lam(K), which is all A.8 can mean once q merges two states, cf.
  the S4 NEVER clause), A.2 (domain quotient), A.7 (what P_K collapses is gone from
  the record: `InAlg` is exactly the set of readouts that never see the collapsed
  difference), A.5/CAN-008 (the record is a class, not a point:
  `sigma_class_well_defined`), IV.5 / V.20 commuting-square criterion (readout half
  only: `future_readers_in_alg`; the state half is T4b in the Foundation file).

  Toledo parents (registry/CANONICAL.json, read 2026-09-18 in the proposals/
  readout-bridge worktree @ b2413324):
    weld/M.03.v1  CAN-007  reader equivalence        -> `DepthClass` at horizon L is an
                                                       OCCURRENCE (finite-horizon form)
    weld/M.68.v1  CAN-1305 DepthStable(n) => depth-n = all-future (stable_depth_exact_future)
    weld/M.63.v1  CAN-1299 congruence under F_u (T3_future_equivalence_dynamic_stability)
                                                    -> `sigma_respects_step` is an OCCURRENCE
                                                       of M.68 + M.63 (proof reuses both)
    weld/M.64.v1  CAN-1300 ker rho subseteq R (T5)   -> `inalg_is_sufficiency`,
                                                       `inalg_kernel_inclusion`: OCCURRENCE
    EQ-002/M.01.v1 CAN-165 Factorization Theorem     -> `alg_iff_factors`: OCCURRENCE with
      (coq/canonical/MRC_Prelude.v, mr_factorization_thm)  `lam` as the section witness:
      CAN-165's `Rinv_dec y` is specialised to `inl (exist _ (lam y) (Hsec y))`, so the
      total section replaces the per-y decidable preimage search; no new row (ruling in
      S2 "Tier now": Alg_Q is CAN-165 at R := q_K, g-bar := P o Lambda_K)
    weld/M.02.v1  CAN-006  domain weld, readout half `O = O# o q`
                                                    -> `future_readers_in_alg`: OCCURRENCE
    root A.8 (genesis_root.json, tier Definition)   -> `Sigma`, `PK_fixes_image`

  Every identifier defined or proved in THIS file is NEW DERIVATION / PROPOSAL --
  not yet in Toledo -- including: Obs, DepthClass, Sigma, sigma_class_refl,
  sigma_respects_step, sigma_readout_factor, sigma_readout_factor_sig,
  sigma_class_well_defined, PK, q_PK, PK_idempotent, PK_fixes_image, InAlg,
  exact_on_alg, alg_is_fixed_points, roundtrip_exact_iff, gbar, alg_factors,
  factors_in_alg, alg_iff_factors, inalg_is_sufficiency, inalg_kernel_inclusion,
  readers_in_alg, future_readers_in_alg. Toledo lookup (equivalence criterion:
  renaming / positive scale / constant substitution) found no existing idempotent-
  section / retained-readout-algebra row; the nearest hits (Keystone/P.14.v1
  projection_idempotent, Q/M.18.v1 twirl_idempotent, weld/M.62.v1 closure
  idempotent) are matrix or closure-operator objects, not this one.

  Ruling 11b-6: `lineage_survives` is DELETED from this file -- a lineage tag on the
  section (parent EQ-001/C.16.v1) adds no proof obligation that `Hsec` does not already
  carry, so writing it would be a renamed twin, not a theorem.

  What is NOT here (Open ledger of the build report): the identification of the
  Part-I Prop-valued class `DepthClass s` with a Part-II/III record `rk s : K` under
  Leibniz equality needs a representative chooser and an extensional record
  equality; this file only takes the sound half (`record_sufficient`: equal record
  => same class) as a disclosed hypothesis.

  Reuse discipline: every theorem below `Require`s the LIVE
  IDM_ReaderDomainFoundation.v (ruling 11b-8; worktree formal/readout-bridge @
  84cdd7b, 1345 lines, Section FiniteBottleneckRDLB present) and cites its
  identifiers; nothing from it is re-proved or copied.

  Build mapping used (recorded per ruling 11b-8):
    cd <idm worktree>/formal && coqc -q -R <idm worktree> IDM IDM_SignatureFunctor.v
  so this file's logical name is IDM.formal.IDM_SignatureFunctor and the plain
  `Require Import IDM_ReaderDomainFoundation` below resolves to
  IDM.formal.IDM_ReaderDomainFoundation (the live .vo compiled under the same -R).
  Memory floor: one coqc at a time, `free -g` checked (available >= 3 G) before it,
  wrapped as ANSE_HEAVY_MAX=3G anse-heavy "...".

  Tier: every theorem is Th_coqc only where a scratch `Print Assumptions` printed
  "Closed under the global context" (see the build report); Section Variables /
  Hypotheses (lam, Hsec, rk, record_sufficient, and the DepthStable premise) are
  premises of the exported statements, never axioms.

  Claim boundary: generic finite/discrete mathematics over abstract types only.
  No continuum premise, no completeness, no decidability assumed, no numeral
  literal anywhere; the horizon L is a declared nat (I4 refused), the class is
  never a point (Z1 refused), an empty class is a Prop, never a state (Z4 refused).
*)

Require Import IDM_ReaderDomainFoundation.

(* ------------------------------------------------------------------ *)
(* Part I.  Sigma_Q at a finite horizon L over the reader-domain quotient *)
(* ------------------------------------------------------------------ *)

Section SignatureAtHorizon.

Context {State Value Action Reader : Type}.
Variable step : Action -> State -> State.
Variable read : Reader -> State -> Value.
Variable L : nat.

(* O(z): the immediate readout of a state by every declared reader. *)
Definition Obs (s : State) : Reader -> Value := fun r => read r s.

(* [z]_Q at horizon L: the CAN-007 class, as a predicate (membership), so that
   no functional-extensionality or propositional-extensionality axiom is needed. *)
Definition DepthClass (s : State) : State -> Prop :=
  fun t => DepthEq step read L s t.

(* Sigma_Q(z) := ( O(z), [z]_Q )  -- Genesis A.8 formation, S2 line 2. *)
Definition Sigma (s : State) : (Reader -> Value) * (State -> Prop) :=
  (Obs s, DepthClass s).

(* Every state is in its own class (reuse: future_eq_implies_depth, future_eq_refl). *)
Lemma sigma_class_refl : forall s, DepthClass s s.
Proof.
  intro s. unfold DepthClass.
  apply (future_eq_implies_depth L).
  apply future_eq_refl.
Qed.

(* S2 admissibility clause 1, at the FIXED horizon L: under DepthStable(L) the
   class component of Sigma is a congruence for every declared action.
   Proof route = weld/M.68 (stable_depth_exact_future) both ways around
   weld/M.63 (T3); the Foundation's depth_stable_successor_closed gives the same
   statement in one step -- cited, not duplicated. *)
Theorem sigma_respects_step :
  DepthStable step read L ->
  forall (u : Action) (s t : State),
    DepthClass s t -> DepthClass (step u s) (step u t).
Proof.
  intros Hst u s t Hd.
  unfold DepthClass in *.
  apply (proj2 (stable_depth_exact_future Hst (step u s) (step u t))).
  apply (T3_future_equivalence_dynamic_stability u).
  exact (proj1 (stable_depth_exact_future Hst s t) Hd).
Qed.

(* S2 admissibility clause 3 (O = O# o q_K), immediate form: the readout
   component of Sigma is constant on the class component. Reuse: depth_immediate. *)
Theorem sigma_readout_factor :
  forall s t, DepthClass s t -> forall r, read r s = read r t.
Proof.
  intros s t Hd r.
  exact (depth_immediate step read L s t Hd r).
Qed.

(* The same statement written on Sigma itself (pointwise on readers). *)
Theorem sigma_readout_factor_sig :
  forall s t, snd (Sigma s) t -> forall r, fst (Sigma s) r = fst (Sigma t) r.
Proof.
  intros s t Hd r.
  unfold Sigma in *. simpl in *. unfold Obs.
  apply sigma_readout_factor. exact Hd.
Qed.

(* The record is a class, not a point (A.5 / CAN-008): under DepthStable(L) two
   states in one class have the same class, pointwise. Reuse: weld/M.68 and the
   FutureEq equivalence lemmas future_eq_sym / future_eq_trans. *)
Theorem sigma_class_well_defined :
  DepthStable step read L ->
  forall s t, DepthClass s t -> forall z, DepthClass s z <-> DepthClass t z.
Proof.
  intros Hst s t Hd z.
  unfold DepthClass in *.
  pose proof (proj1 (stable_depth_exact_future Hst s t) Hd) as Hf.
  split; intro Hz.
  - apply (proj2 (stable_depth_exact_future Hst t z)).
    apply (future_eq_trans (future_eq_sym Hf)).
    exact (proj1 (stable_depth_exact_future Hst s z) Hz).
  - apply (proj2 (stable_depth_exact_future Hst s z)).
    apply (future_eq_trans Hf).
    exact (proj1 (stable_depth_exact_future Hst t z) Hz).
Qed.

End SignatureAtHorizon.

(* ------------------------------------------------------------------ *)
(* Part II.  The retained algebra Alg_Q and the EXACT clause of S4      *)
(* ------------------------------------------------------------------ *)

Section RetainedAlgebra.

Context {S K V : Type}.
Variable q : S -> K.                       (* q_K : X -> R_K, the forward map *)
Variable lam : K -> S.                     (* Lambda_K : R_K -> Y with Y = X = S *)
Hypothesis Hsec : forall k, q (lam k) = k. (* DISCLOSED: lam is a section of q *)

(* P_K := Lambda_K o q_K. *)
Definition PK (s : S) : S := lam (q s).

(* The record of the retained state is the record. *)
Theorem q_PK : forall s, q (PK s) = q s.
Proof. intro s. unfold PK. apply Hsec. Qed.

(* S2 line 1: P_K o P_K = P_K, from q o Lambda = id. *)
Theorem PK_idempotent : forall s, PK (PK s) = PK s.
Proof. intro s. unfold PK. rewrite Hsec. reflexivity. Qed.

(* Genesis A.8 `Lambda o Sigma = I` in the only form compatible with a merging q:
   the identity on the retained states lam(K). *)
Theorem PK_fixes_image : forall k, PK (lam k) = lam k.
Proof. intro k. unfold PK. rewrite Hsec. reflexivity. Qed.

(* Alg_Q := { P : ker q_K subseteq ker P }. *)
Definition InAlg (P : S -> V) : Prop :=
  forall s t, q s = q t -> P s = P t.

(* EXACT, direction 1: on Alg_Q the round trip through Lambda_K is exact. *)
Theorem exact_on_alg :
  forall P, InAlg P -> forall s, P (PK s) = P s.
Proof.
  intros P HP s. apply HP. apply q_PK.
Qed.

(* EXACT, direction 2: pointwise fixed points of the round trip lie in Alg_Q. *)
Theorem alg_is_fixed_points :
  forall P, (forall s, P (PK s) = P s) -> InAlg P.
Proof.
  intros P Hfix s t Hq.
  rewrite <- (Hfix s). rewrite <- (Hfix t).
  unfold PK. rewrite Hq. reflexivity.
Qed.

(* S4 EXACT clause:  P o Lambda_K o q_K = P  <=>  P in Alg_Q  (pointwise, no funext). *)
Theorem roundtrip_exact_iff :
  forall P, (forall s, P (PK s) = P s) <-> InAlg P.
Proof.
  intro P. split.
  - exact (@alg_is_fixed_points P).
  - exact (@exact_on_alg P).
Qed.

(* CAN-165 (EQ-002/M.01.v1) Factorization Theorem, OCCURRENCE with lam as the
   section witness: g-bar := P o Lambda_K. *)
Definition gbar (P : S -> V) : K -> V := fun k => P (lam k).

Theorem alg_factors :
  forall P, InAlg P -> forall s, P s = gbar P (q s).
Proof.
  intros P HP s. symmetry. exact (exact_on_alg P HP s).
Qed.

Theorem factors_in_alg :
  forall (P : S -> V) (g : K -> V), (forall s, P s = g (q s)) -> InAlg P.
Proof.
  intros P g Hg s t Hq.
  rewrite (Hg s). rewrite (Hg t). rewrite Hq. reflexivity.
Qed.

Theorem alg_iff_factors :
  forall P, InAlg P <-> exists g : K -> V, forall s, P s = g (q s).
Proof.
  intro P. split.
  - intro HP. exists (gbar P). exact (alg_factors P HP).
  - intros [g Hg]. exact (factors_in_alg P g Hg).
Qed.

(* weld/M.64.v1 (CAN-1300, T5) OCCURRENCE: membership in Alg_Q IS sufficiency of
   the record for the kernel of P, and hence the kernel inclusion ker q <= ker P. *)
Theorem inalg_is_sufficiency :
  forall P, InAlg P <-> SufficientFor q (@kernel S V P).
Proof.
  intro P. split; intro H; exact H.
Qed.

Theorem inalg_kernel_inclusion :
  forall P, InAlg P -> forall s t, KernelR q s t -> @kernel S V P s t.
Proof.
  intros P HP s t Hk.
  exact (T5_sufficiency_kernel_inclusion (proj1 (inalg_is_sufficiency P) HP) Hk).
Qed.

End RetainedAlgebra.

(* ------------------------------------------------------------------ *)
(* Part III.  Readouts of the future lie in Alg_Q  (O = O# o q_K)        *)
(* ------------------------------------------------------------------ *)

Section RecordedReadouts.

Context {State Value Action Reader K : Type}.
Variable step : Action -> State -> State.
Variable read : Reader -> State -> Value.
Variable L : nat.
Variable rk : State -> K.                  (* the record map q_K into a record type *)
(* DISCLOSED (weld/E.06 sufficiency, sound half only): equal records never merge
   two states the readers separate within horizon L. *)
Hypothesis record_sufficient :
  forall s t, rk s = rk t -> DepthEq step read L s t.

(* Every declared reader factors through the record. *)
Theorem readers_in_alg : forall r, InAlg rk (read r).
Proof.
  intro r. unfold InAlg. intros s t Hq.
  exact (depth_immediate step read L s t (record_sufficient s t Hq) r).
Qed.

(* weld/M.02.v1 (CAN-006) readout half, all futures: under DepthStable(L) every
   reader after every finite word of actions factors through the record.
   Reuse: weld/M.68 (stable_depth_exact_future) and the definition of FutureEq. *)
Theorem future_readers_in_alg :
  DepthStable step read L ->
  forall (r : Reader) (w : list Action),
    InAlg rk (fun s => read r (run_word step w s)).
Proof.
  intros Hst r w. unfold InAlg. intros s t Hq.
  exact (proj1 (stable_depth_exact_future Hst s t) (record_sufficient s t Hq) r w).
Qed.

End RecordedReadouts.
