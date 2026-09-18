(*
  Leaf_HeatPath.v -- the HEAT / DIFFUSION LEAF of the Discrete-Continuum Readout Bridge:
  a domain leaf that runs S1 -> S5 end to end with quantitative certificate content (the
  programme's Phase 3 leaf), instantiated on the exact rationals of ONE executed run (2026-09-18) of the
  frozen heat-leaf protocol (explicit stepper phi <- phi - dt * L_R phi on the unit path,
  nested grids N_K = 8 * 2^K, K = 0..4, six tapes, seven readers).  Phase 3, 2026-09-18.

  LEAF DECLARATION.  This file is a LEAF: it adds no line to the bridge.  It instantiates
  the compiled objects of the five bridge files on concrete numbers and on one small
  concrete grid.  Everything is over Q / nat / finite tuples and finite lists; no
  statement forms h -> 0, a limit, a tail or a supremum; the continuum heat equation is
  never an object here (it is a readout, tier Dr, named only in this sentence).

  TIER SPLIT (binding for every reader of this file).
    * The NUMBERS (every g_K, khat, s below) are tier finite_diagnostic: they were produced
      by one dated executed run (standard library, exact rational arithmetic, script committed
      before its first execution, certificates committed before the held-out levels were
      computed) and are COPIED here by a generator from the run's leaf_numbers.json
      (sha256 42f85fbfa5eaa3a5d41302f8871eb84a248b7d6411bb5c92eda5bbf4bb430986).
      The run, its freeze file and the generator live in the programme's private research
      journal.
    * The THEOREMS are tier Th_coqc, and they are theorems ABOUT THOSE NUMBERS: "this
      rational tape satisfies the window premise", "the compiled gate' returns ACCEPT at
      this cell", "hence |g_4 - g_{K+1}| <= eps".  A Th_coqc line here certifies the
      arithmetic and the instantiation -- never the run, the stepper's fidelity beyond
      level 0 (see SEAM TIE), the physical model, the choice of reader, or anything beyond
      level 4 of the tape.  Every certificate below is a WINDOW certificate on witnessed
      levels; none is a tail certificate or a continuum-limit certificate.  HOLD is not FALSE.
    * Th_coqc is claimed for a statement only through its own in-file Print Assumptions
      readout at the end of this file ("Closed under the global context").

  NOTATION.  kappa / khat = the contraction ratio of the ledger (the argument named `rho`
  in IDM_ReadoutTower.v and PROP_BRIDGE_03_certified_radius.v).  rho_K = the inner
  reconstruction radius of S3.  This file never writes a bare rho.

  PARENTS BY CODE (reused through THEIR OWN Coq objects; no private twin of any of them).
  Dotted codes (R/M.32.v1, weld/S.22.v1, ...) are canonical Toledo codes; PROP-BRIDGE-nn are
  rows of the bridge's PROPOSAL lane, themselves not yet in Toledo (codes pending):
    R/M.32.v1, R/M.14.v1   refine_stable / geom_majorant_tail -- through their windowed
                           forms plateau_certificate_window (PROP-BRIDGE-13), IDM_ReadoutTower
    Z/M.08.v1              the telescope behind tailsum_delta_telescopes (PROP-BRIDGE-01)
    PROP-BRIDGE-04         beta_S1, dQ, dQ_triangle, dQ_sym, triangle_composition
    PROP-BRIDGE-06         Certificate', gate', fail_closed' (occurrence of PROP-EPSC-03:
                           Verdict / ACCEPT / HOLD are PROP_EPSC_03's own)
    PROP-BRIDGE-16         gate_accept_certified, accept_certified_dQ (the ACCEPT theorem)
    PROP-BRIDGE-15         roundtrip_radius_record (occurrence of PROP-EPSC-08)
    PROP-BRIDGE-18         InAlg, exact_on_alg, roundtrip_exact,
                           roundtrip_exact_fails_outside_alg (occurrence of EQ-002/M.01.v1
                           and weld/M.64.v1)
    PROP-BRIDGE-03         PK, PK_idempotent, PK_fixes_image (typing split)
    PROP-BRIDGE-09         roundtrip_never, roundtrip_never_total (no-decoder theorem of
                           Readout Genesis, cited at its source tier)
    PROP-BRIDGE-02         Nidx, accept (the bounded search; N_of / sigma_of are NOT used)
    PROP-BRIDGE-08         seam_grid, Lvec, path_w (Bridge_Seam.v; parents weld/M.01.v1,
                           L_R/M.20-22.v1, weld/M.41.v1)
    weld/S.22.v1           s[n+1] = s[n] + dt (-A s[n] + J), A := L_R + Gamma: heat_step
                           below is that statement at Gamma := 0, J := 0 (occurrence)
    weld/M.02.v1 + weld/M.03.v1   the reader-domain quotient: q53 is an occurrence

  NEW IN THIS FILE -- every item is NEW DERIVATION / PROPOSAL, not yet in Toledo, and must
  not be cited as an equation until the registrar assigns a code:
    N4  plateau_radius_window        the DIVISION-form radius on a WINDOW (the compiled
                                     plateau_radius needs the premise at every k; the
                                     compiled window lemma is multiplicative): parents
                                     plateau_certificate_window + Qle_shift_div_l.
        heldout_miss_refutes_persistence   its contrapositive (a held-out MISS forces the
                                     contraction premise to fail on the window).
    N1  q53 / Lam35 / res32 / q52 / Lam23 on TUPLE carriers (5 fine / 3 coarse / 2 nodes),
        the section law, the coherence q52 = res32 o q53; dinf5 (finite max of dQ) with
        its triangle inequality and symmetry.
    leaf suppliers (scoring machinery, not equations): tape_of, window_ok / licence_ok
        (boolean readers of the window premise, with soundness), cert_dec (the decision
        procedure that BUILDS the input of the compiled gate'), leaf_gate := gate' applied
        to that input, hold_downward / leaf_hold_sound (HOLD cells are closed under smaller
        tolerances), leaf_gate_threshold (under a licence the gate IS the threshold
        delta_K + r_K <= eps), no_licence_if_gap_grows / leaf_gate_holds_if_gap_grows,
        eps_abs / eps_rel (the protocol's two frozen grids), heat_step / heat_step_pinned.
  Reuse pipeline, recorded: the freeze of the protocol carries its own lookup (heat, diffusion,
  stepper, Richardson, held-out, restrict, nested, coarse, prolong, interpol, piecewise,
  checkerboard, window, plateau, tolerance grid ...).  For the objects added by THIS file a
  second Toledo lookup by statement was run on 2026-09-18 over registry/CANONICAL.json (1,333
  rows) and registry/proposals/*.json -- keywords decid, boolean, Qle_bool, certificate
  builder, cert_of, prolong, restrict, padd, finite list, nth, max / sup norm, d_inf, infinity
  norm, chebyshev, window; every hit's statement was read: the only window rows are the multiplicative ones of the bridge lane
  (PROP-BRIDGE-13 / -17); A3/M.01-03.v1 `decide` is a bounded WITNESS search, not a
  certificate builder; the one infinity-norm hit is a Vandermonde conditioning number; no
  grid restriction / prolongation pair and no d_inf on tuples is registered.  Genesis
  compatibility (READOUT_GENESIS_CORE.md, through the bridge's declared sections): q53
  instantiates the reader-domain quotient of the Exact Domain Gate (A.4); Lam35 is a
  DISCLOSED section (A.8, section reading, Dr, founder ruling pending); NEVER is A.8's
  "merging must not erase history" read as "merged fine states are not recovered"; HOLD is
  the gate-level image of the third value of A.13 Gate 2; the FAIL rows implement the
  Fail-Able Gate Law (V.14 / VI.7).

  WHAT THE PROTOCOL DECLARES AND THIS FILE FOLLOWS.
    * Reader layer (S1 -> S3 -> S5): Y := Q, d_Y := dQ (Qabs of the difference); the ACCEPT
      theorem is used as a three-point statement with the explicit witnesses RK := RK1 := Q,
      Lambda_K := id, res_K := id, q_K := the CONSTANT map to g_K, x_{K+1} := g_{K+1},
      object x := g_4 (the finest readout ON THE TAPE).  No structural law is claimed at this
      layer.  Triangle = dQ_triangle, symmetry = dQ_sym (to orient the defect), 0 <= r_K from
      kappa < 1 (beta_S1_nonneg): all three discharged in leaf_accept_certified.
    * rho_K is NOT instantiated: the leaf has no inner reconstruction stage, r_K := beta_K
      = beta_S1 g khat_5 K, fed directly as the radius premise, licensed on the WINDOW [K,4)
      by N4 -- never by contracting_beta, whose every-k premise would hold here only by the
      padding.  No every-k lemma (plateau_radius, contracting_beta, N_of, sigma_of, ...) is
      instantiated on any padded tape in this file.
    * delta_K := dQ g_{K+1} g_K; cell ACCEPT iff delta_K <= eps and (eps - delta_K)^2 >= r_K^2.
    * State layer (S2, S4): the 5-fine / 3-coarse grid with tuple carriers; shared-node
      values are COPIED by Lam35, so the section law is Leibniz and closes by reflexivity.

  ROWS INSTANTIATED (7 of the run's 40; the other 33 are left out, see LEFT OUT):
    TC_near   T-C x O_near   PASS candidate, in state S, matched pair of TD_near
    TD_near   T-D x O_near   FAIL, unstable dt: no licence at any window, HOLD everywhere
    TA_mid    T-A x O_mid    closed-form class ("same reader, two regimes" with TB_mid)
    TB_mid    T-B x O_mid    the TRAP: the C3 window licence EXISTS (kappa_0 = 1/4 exactly),
                             its extrapolated ball MISSES both held-out values, C4 / C5 HOLD
    TC_ssq    T-C x O_ssq    FAIL, non-refining reader: HOLD everywhere (forced by arithmetic)
    TR_near   T-R x O_near   FAIL control that the gate ACCEPTS -- compiled on purpose, so that
                             this file does not look better than the run: an ACCEPT certifies
                             the ledger it is given, not the model; the run reported this first
    TR_state  T-R x O_state  TOLERANCE-ONLY: licensed (khat_5 ~ 0.9989) and HOLD from the
                             largest tolerance of either grid downwards
  Also compiled, against the PASS reading: the C3 extrapolated ball MISSES the held-out g_3
  and g_4 on the PASS row TC_near (the one-ratio window certificate is not a regime
  classifier), and hold_is_not_false_* cells where the gate HOLDs although the inequality is
  true on the tape.

  SEAM TIE (level 0 only).  For six rows the level-0 readout g_0 is RECOMPUTED in this file
  from the compiled seam operator (one heat_step on 9 nodes through Bridge_Seam.Lvec 9 path_w)
  and proved == to the run's number: an independent implementation agrees with the run at
  level 0.  Levels 1..4 are NOT recomputed here (see LEFT OUT).

  LEFT OUT (each with stance + falsifier in the programme's Coq ledger, private research
  journal; none is written here as an unfinished proof):
    - recomputation of levels 1..4 inside Coq (needs a list-state stepper with reduction of
      fractions; the nested-function stepper multiplies unreduced denominators);
    - the state-layer ledger O_state as a Coq object (delta N3, path-length ledger) and the
      S1 -> S3 -> S4(b) chain through it; TR_state's numbers are consumed as a scalar tape only;
    - the 129-node instances of S2 / S4 and the triangle_composition DIAGNOSTIC with
      rho_K^diag > 0 (the small grid carries the typed instance; the diagnostic enters no
      certificate);
    - the truncation device (pad beyond a held-out level m) that would turn a held-out HIT
      with a persisting premise into a window-lemma instance; held-out containments below are
      decided by computation and labelled as observations;
    - route P (kappa_P = 1/2), the sharp form, K = 3 cells, the other 33 rows, and every
      scoring convention of the freeze (labels, tallies, power criterion).

  Compile mapping (the live IDM worktree is the source of truth):
    cd <live IDM worktree>/formal &&
    coqc -q -R <live IDM worktree> IDM -Q <toledo worktree>/coq/canonical MRC Leaf_HeatPath.v
  Prerequisites (compiled .vo, same mappings): IDM_Calculus, IDM_ReadoutTower,
  IDM_SignatureFunctor, IDM_BridgeRoundTrip, Bridge_Seam (IDM worktree);
  PROP_EPSC_03_fail_closed_gate, PROP_BRIDGE_03_certified_radius (toledo worktree).  Logical
  name: IDM.formal.Leaf_HeatPath.  `formal/verify.sh` cannot build it (it needs the MRC
  mapping), exactly as for IDM_BridgeRoundTrip.v and Bridge_Seam.v.
  Memory note (binding): `free -g` before the coqc, skip if available < 3 G; ONE coqc, in the
  foreground, under a memory cap; never a full-arc verify script in the loop.  Proof methods:
  vm_compute on closed rational terms, lra, lia, direct instantiation -- no search of any kind.

  No AI is an author of this file.
*)

Require Import Coq.Lists.List.
Require Import Coq.Bool.Bool.
Require Import Coq.Arith.PeanoNat.
Require Import Coq.ZArith.ZArith.
Require Import Coq.micromega.Lia.
Require Import Coq.QArith.QArith.
Require Import Coq.QArith.Qabs.
Require Import Coq.QArith.Qminmax.
Require Import Coq.micromega.Lqa.

From IDM.formal Require Import IDM_Matrix.              (* Sum, Lap *)
From IDM.formal Require Import IDM_Calculus.            (* Delta *)
From IDM.formal Require Import IDM_ReadoutTower.        (* plateau_certificate_window, Nidx, accept *)
From IDM.formal Require Import IDM_SignatureFunctor.    (* PK, InAlg, exact_on_alg, PK_idempotent *)
From IDM.formal Require Import IDM_BridgeRoundTrip.     (* roundtrip_exact, roundtrip_never, roundtrip_radius_record *)
From IDM.formal Require Import Bridge_Seam.             (* Lvec, path_w, seam_grid *)
From MRC Require Import PROP_EPSC_03_fail_closed_gate.  (* Verdict, ACCEPT, HOLD *)
From MRC Require Import PROP_BRIDGE_03_certified_radius. (* beta_S1, dQ, Certificate', gate', gate_accept_certified *)

Import ListNotations.
Open Scope Q_scope.

(* ===================================================================== *)
(*  Part 0 -- leaf suppliers (NEW DERIVATION / PROPOSAL, not yet in Toledo) *)
(* ===================================================================== *)

(* closed rational facts are decided by computation, never by search *)
Ltac qdec :=
  match goal with
  | |- ~ (_ <= _) =>
      let HH := fresh "HH" in
      intro HH; apply (proj2 (Qle_bool_iff _ _)) in HH; vm_compute in HH; discriminate HH
  | |- _ == _ => apply Qeq_bool_eq; vm_compute; reflexivity
  | |- _ <= _ => apply (proj1 (Qle_bool_iff _ _)); vm_compute; reflexivity
  | |- _ < _ => vm_compute; reflexivity
  end.

(** The tape as a function nat -> Q: a finite list of witnessed readouts, padded CONSTANT
    (stdlib nth with a default).  The padding is bookkeeping and carries no content. *)
Definition tape_of (l : list Q) (pad : Q) : nat -> Q := fun k => nth k l pad.

(** N4 -- the DIVISION-form radius on a WINDOW.  Parents: plateau_certificate_window
    (PROP-BRIDGE-13) and Qle_shift_div_l.  The value is the compiled beta_S1 g kappa N.
    NEW DERIVATION / PROPOSAL -- not yet in Toledo. *)
Lemma plateau_radius_window : forall (kappa : Q) (g : nat -> Q) (N M : nat),
  kappa < 1 ->
  (forall k, (N <= k < N + M)%nat -> Qabs (Delta g (S k)) <= kappa * Qabs (Delta g k)) ->
  Qabs (g (N + M)%nat - g N) <= beta_S1 g kappa N.
Proof.
  intros kappa g N M Hk Hw. unfold beta_S1.
  apply Qle_shift_div_l; [ lra | ].
  rewrite Qmult_comm. apply plateau_certificate_window; [ lra | exact Hw ].
Qed.

(** Contrapositive: a held-out value OUTSIDE the ball refutes the persistence of the
    contraction on the window (the script's MISS ==> not-PP assertion, as a theorem). *)
Corollary heldout_miss_refutes_persistence : forall (kappa : Q) (g : nat -> Q) (N M : nat),
  kappa < 1 ->
  ~ (Qabs (g (N + M)%nat - g N) <= beta_S1 g kappa N) ->
  ~ (forall k, (N <= k < N + M)%nat -> Qabs (Delta g (S k)) <= kappa * Qabs (Delta g k)).
Proof.
  intros kappa g N M Hk Hmiss Hw. apply Hmiss.
  exact (plateau_radius_window kappa g N M Hk Hw).
Qed.

(** 0 <= r_K: the radius is nonnegative as soon as kappa < 1 (no 0 <= kappa needed). *)
Lemma beta_S1_nonneg : forall (g : nat -> Q) (kappa : Q) (N : nat),
  kappa < 1 -> 0 <= beta_S1 g kappa N.
Proof.
  intros g kappa N Hk. unfold beta_S1.
  apply Qle_shift_div_l; [ lra | ].
  rewrite Qmult_0_l. apply Qabs_nonneg.
Qed.

(** The window premise of plateau_certificate_window, read by a boolean on [N, N+M). *)
Fixpoint window_ok (g : nat -> Q) (kappa : Q) (N M : nat) : bool :=
  match M with
  | O => true
  | S m => Qle_bool (Qabs (Delta g (S N))) (kappa * Qabs (Delta g N)) && window_ok g kappa (S N) m
  end.

Lemma window_ok_sound : forall (g : nat -> Q) (kappa : Q) (M N : nat),
  window_ok g kappa N M = true ->
  forall k, (N <= k < N + M)%nat -> Qabs (Delta g (S k)) <= kappa * Qabs (Delta g k).
Proof.
  intros g kappa M. induction M as [| m IH]; intros N H k Hk.
  - exfalso. lia.
  - cbn [window_ok] in H. apply andb_true_iff in H. destruct H as [H1 H2].
    destruct (Nat.eq_dec k N) as [Heq | Hne].
    + subst k. apply (proj1 (Qle_bool_iff _ _)). exact H1.
    + apply (IH (S N) H2). lia.
Qed.

(** The licence: kappa < 1 AND the window premise, both read by computation. *)
Definition licence_ok (g : nat -> Q) (kappa : Q) (N M : nat) : bool :=
  negb (Qle_bool 1 kappa) && window_ok g kappa N M.

Lemma licence_ok_sound : forall (g : nat -> Q) (kappa : Q) (N M : nat),
  licence_ok g kappa N M = true ->
  kappa < 1 /\
  (forall k, (N <= k < N + M)%nat -> Qabs (Delta g (S k)) <= kappa * Qabs (Delta g k)).
Proof.
  intros g kappa N M H. unfold licence_ok in H.
  apply andb_true_iff in H. destruct H as [H1 H2]. split.
  - apply Qnot_le_lt. intro Hle.
    apply (proj2 (Qle_bool_iff _ _)) in Hle. rewrite Hle in H1. discriminate H1.
  - exact (window_ok_sound g kappa M N H2).
Qed.

(** The decision procedure that BUILDS the input of the compiled gate': a certificate
    carrying r2 when both clauses of Certificate' are decided true, None otherwise. *)
Definition cert_dec (delta eps r2 : Q) : option (Certificate' delta eps) :=
  match Qlt_le_dec eps delta with
  | left _ => None
  | right Hle =>
      match Qlt_le_dec ((eps - delta) * (eps - delta)) r2 with
      | left _ => None
      | right Hsq => Some (exist _ r2 (conj Hle Hsq))
      end
  end.

Lemma cert_dec_complete : forall delta eps r2 : Q,
  delta <= eps -> r2 <= (eps - delta) * (eps - delta) ->
  gate' delta eps (cert_dec delta eps r2) = ACCEPT r2.
Proof.
  intros delta eps r2 Hle Hsq. unfold cert_dec.
  destruct (Qlt_le_dec eps delta) as [Hlt | Hle'].
  - exfalso. exact (Qlt_not_le _ _ Hlt Hle).
  - destruct (Qlt_le_dec ((eps - delta) * (eps - delta)) r2) as [Hlt2 | Hsq'].
    + exfalso. exact (Qlt_not_le _ _ Hlt2 Hsq).
    + reflexivity.
Qed.

(** A computed HOLD is not a choice of the leaf: NO certificate carrying r2 exists. *)
Lemma cert_dec_hold_sound : forall delta eps r2 : Q,
  gate' delta eps (cert_dec delta eps r2) = HOLD ->
  forall c : option (Certificate' delta eps), gate' delta eps c <> ACCEPT r2.
Proof.
  intros delta eps r2 Hhold c Hacc.
  destruct (fail_closed' delta eps c r2 Hacc) as [Hle Hsq].
  rewrite (cert_dec_complete delta eps r2 Hle Hsq) in Hhold. discriminate Hhold.
Qed.

(** HOLD cells are closed under SMALLER tolerances (ACCEPT cells are a down-set in j). *)
Lemma hold_downward : forall delta eps eps' r2 : Q,
  eps' <= eps ->
  (forall c : option (Certificate' delta eps), gate' delta eps c <> ACCEPT r2) ->
  forall c' : option (Certificate' delta eps'), gate' delta eps' c' <> ACCEPT r2.
Proof.
  intros delta eps eps' r2 Hee Hno c' Hacc.
  destruct (fail_closed' delta eps' c' r2 Hacc) as [Hle Hsq].
  assert (Hle2 : delta <= eps) by lra.
  assert (Hsq2 : r2 <= (eps - delta) * (eps - delta)).
  { apply Qle_trans with (y := (eps' - delta) * (eps' - delta)); [ exact Hsq | ].
    apply sq_monotone; lra. }
  apply (Hno (Some (exist _ r2 (conj Hle2 Hsq2)))). reflexivity.
Qed.

(** The leaf's gate: delta_K := dQ g_{K+1} g_K, r_K := beta_S1 g kappa K (rho_K NOT
    instantiated), licence on the window [K, top); the verdict is the COMPILED gate'
    applied to the computed certificate. *)
Definition leaf_delta (g : nat -> Q) (K : nat) : Q := dQ (g (S K)) (g K).
Definition leaf_r (g : nat -> Q) (kappa : Q) (K : nat) : Q := beta_S1 g kappa K.

Definition leaf_cert (g : nat -> Q) (kappa : Q) (top K : nat) (eps : Q)
  : option (Certificate' (leaf_delta g K) eps) :=
  if licence_ok g kappa K (top - K)
  then cert_dec (leaf_delta g K) eps (leaf_r g kappa K * leaf_r g kappa K)
  else None.

Definition leaf_gate (g : nat -> Q) (kappa : Q) (top K : nat) (eps : Q) : Verdict :=
  gate' (leaf_delta g K) eps (leaf_cert g kappa top K eps).

Lemma leaf_gate_licensed : forall (g : nat -> Q) (kappa : Q) (top K : nat) (eps r2 : Q),
  leaf_gate g kappa top K eps = ACCEPT r2 -> licence_ok g kappa K (top - K) = true.
Proof.
  intros g kappa top K eps r2 H. unfold leaf_gate, leaf_cert in H.
  destruct (licence_ok g kappa K (top - K)); [ reflexivity | ].
  change (HOLD = ACCEPT r2) in H. discriminate H.
Qed.

(** S1 -> S3 -> S5 in one statement.  gate_accept_certified at Y := Q, d_Y := dQ:
    triangle = dQ_triangle; symmetry = dQ_sym (orients the defect); 0 <= r_K from
    kappa < 1; radius premise from N4 on the WINDOW [K, top).  Witnesses as the protocol
    declares: q_K := the constant map to g K, Lambda_K := id, res_K := id,
    x := g top, x_{K+1} := g (S K). *)
Theorem leaf_accept_certified : forall (g : nat -> Q) (kappa : Q) (top K : nat) (eps : Q),
  (K <= top)%nat ->
  leaf_gate g kappa top K eps = ACCEPT (leaf_r g kappa K * leaf_r g kappa K) ->
  dQ (g top) (g (S K)) <= eps.
Proof.
  intros g kappa top K eps HK Hacc.
  pose proof (leaf_gate_licensed g kappa top K eps _ Hacc) as Hlic.
  destruct (licence_ok_sound g kappa K (top - K) Hlic) as [Hk Hw].
  assert (Hr : 0 <= leaf_r g kappa K) by (apply beta_S1_nonneg; exact Hk).
  assert (Hrad : dQ (g top) (g K) <= leaf_r g kappa K).
  { pose proof (plateau_radius_window kappa g K (top - K) Hk Hw) as H.
    replace (K + (top - K))%nat with top in H by lia.
    unfold dQ, leaf_r. exact H. }
  assert (Hdef : dQ (g K) (g (S K)) <= leaf_delta g K).
  { unfold leaf_delta. apply Qle_lteq. right. apply dQ_sym. }
  exact (gate_accept_certified Q dQ dQ_triangle Q Q
           (fun _ : Q => g K) (fun y : Q => y) (fun y : Q => y)
           (g top) (g (S K)) (leaf_delta g K) eps (leaf_r g kappa K)
           Hr Hrad Hdef (leaf_cert g kappa top K eps) Hacc).
Qed.

(** The same conclusion from the literal premises, through accept_certified_dQ (no gate). *)
Corollary leaf_accept_premises : forall (g : nat -> Q) (kappa : Q) (top K : nat) (eps : Q),
  (K <= top)%nat -> kappa < 1 ->
  (forall k, (K <= k < K + (top - K))%nat -> Qabs (Delta g (S k)) <= kappa * Qabs (Delta g k)) ->
  leaf_delta g K <= eps ->
  leaf_r g kappa K * leaf_r g kappa K <= (eps - leaf_delta g K) * (eps - leaf_delta g K) ->
  dQ (g top) (g (S K)) <= eps.
Proof.
  intros g kappa top K eps HK Hk Hw Hle Hsq.
  assert (Hrad : dQ (g top) (g K) <= leaf_r g kappa K).
  { pose proof (plateau_radius_window kappa g K (top - K) Hk Hw) as H.
    replace (K + (top - K))%nat with top in H by lia.
    unfold dQ, leaf_r. exact H. }
  exact (accept_certified_dQ Q Q (fun _ : Q => g K) (fun y : Q => y) (fun y : Q => y)
           (g top) (g (S K)) (leaf_delta g K) eps (leaf_r g kappa K)
           (beta_S1_nonneg g kappa K Hk) Hrad (Qle_refl _) Hle Hsq).
Qed.

(** Under a licence the gate IS the threshold eps*_K = delta_K + r_K (equiv_to_sum with the
    rational root r_K as witness; no square root). *)
Theorem leaf_gate_threshold : forall (g : nat -> Q) (kappa : Q) (top K : nat) (eps : Q),
  licence_ok g kappa K (top - K) = true ->
  (leaf_gate g kappa top K eps = ACCEPT (leaf_r g kappa K * leaf_r g kappa K)
   <-> leaf_delta g K + leaf_r g kappa K <= eps).
Proof.
  intros g kappa top K eps Hlic.
  destruct (licence_ok_sound g kappa K (top - K) Hlic) as [Hk _].
  assert (Hr : 0 <= leaf_r g kappa K) by (apply beta_S1_nonneg; exact Hk).
  unfold leaf_gate, leaf_cert. rewrite Hlic. split.
  - intro Hacc.
    apply (proj1 (equiv_to_sum (leaf_delta g K) eps (leaf_r g kappa K)
                    (leaf_r g kappa K * leaf_r g kappa K) Hr (Qeq_refl _))).
    exact (fail_closed' _ _ _ _ Hacc).
  - intro Hsum.
    destruct (proj2 (equiv_to_sum (leaf_delta g K) eps (leaf_r g kappa K)
                       (leaf_r g kappa K * leaf_r g kappa K) Hr (Qeq_refl _)) Hsum) as [Hle Hsq].
    apply cert_dec_complete; assumption.
Qed.

(** Under a licence a computed HOLD at eps means: no certificate carrying r_K^2 exists at
    eps NOR at any smaller tolerance ("too tight for the level"). *)
Lemma leaf_hold_sound : forall (g : nat -> Q) (kappa : Q) (top K : nat) (eps : Q),
  licence_ok g kappa K (top - K) = true ->
  leaf_gate g kappa top K eps = HOLD ->
  forall eps', eps' <= eps ->
  forall c : option (Certificate' (leaf_delta g K) eps'),
    gate' (leaf_delta g K) eps' c <> ACCEPT (leaf_r g kappa K * leaf_r g kappa K).
Proof.
  intros g kappa top K eps Hlic Hhold eps' He.
  apply (hold_downward (leaf_delta g K) eps eps' _ He).
  apply cert_dec_hold_sound.
  unfold leaf_gate, leaf_cert in Hhold. rewrite Hlic in Hhold. exact Hhold.
Qed.

(** A gap that GROWS inside the window refutes the premise for every kappa <= 1. *)
Lemma no_licence_if_gap_grows : forall (g : nat -> Q) (N M k0 : nat),
  (N <= k0 < N + M)%nat ->
  Qabs (Delta g k0) < Qabs (Delta g (S k0)) ->
  forall kappa : Q, kappa <= 1 ->
  ~ (forall k, (N <= k < N + M)%nat -> Qabs (Delta g (S k)) <= kappa * Qabs (Delta g k)).
Proof.
  intros g N M k0 Hk0 Hgrow kappa Hk Hw.
  pose proof (Hw k0 Hk0) as H.
  pose proof (Qabs_nonneg (Delta g k0)) as Ha.
  assert (H0 : 0 <= (1 - kappa) * Qabs (Delta g k0)) by (apply Qmult_le_0_compat; lra).
  lra.
Qed.

(** ... hence the leaf's gate HOLDs for EVERY kappa and EVERY tolerance at every cell whose
    window [K, top) contains the growing gap. *)
Lemma leaf_gate_holds_if_gap_grows : forall (g : nat -> Q) (top k0 : nat),
  (k0 < top)%nat ->
  Qabs (Delta g k0) < Qabs (Delta g (S k0)) ->
  forall (kappa : Q) (K : nat) (eps : Q), (K <= k0)%nat -> leaf_gate g kappa top K eps = HOLD.
Proof.
  intros g top k0 Hk0 Hgrow kappa K eps HK.
  unfold leaf_gate, leaf_cert.
  destruct (licence_ok g kappa K (top - K)) eqn:E; [ exfalso | reflexivity ].
  destruct (licence_ok_sound g kappa K (top - K) E) as [Hk Hw].
  assert (Hin : (K <= k0 < K + (top - K))%nat) by lia.
  exact (no_licence_if_gap_grows g K (top - K) k0 Hin Hgrow kappa (Qlt_le_weak _ _ Hk) Hw).
Qed.

(** The protocol's two frozen tolerance grids, j = 2, 4, .., 24. *)
Definition eps_abs (j : positive) : Q := 1 # (2 ^ j)%positive.
Definition eps_rel (s : Q) (j : positive) : Q := (1 # (2 ^ j)%positive) * s.

(* ===================================================================== *)
(*  Part 1 -- the stepper through the compiled seam (occurrence of weld/S.22.v1 *)
(*  at Gamma := 0, J := 0) and the level-0 data                            *)
(* ===================================================================== *)

(* free: the literal stepper on all n nodes, L_R = IDM_Matrix.Lap n path_w through Lvec *)
Definition heat_step (n : nat) (dt : Q) (phi : nat -> Q) : nat -> Q :=
  fun i => phi i - dt * Lvec n path_w phi i.

(* pinned: the same rows on interior nodes, the two end nodes held *)
Definition heat_step_pinned (n : nat) (dt : Q) (phi : nat -> Q) : nat -> Q :=
  fun i => if (Nat.eqb i 0 || Nat.eqb (S i) n)%bool then phi i else heat_step n dt phi i.

(** On interior nodes the step IS the [1,-2,1] update -- seam_grid, used as compiled. *)
Theorem heat_step_interior : forall (n i : nat) (dt : Q) (phi : nat -> Q),
  (S (S i) < n)%nat ->
  heat_step n dt phi (S i) == phi (S i) + dt * (phi i - 2 * phi (S i) + phi (S (S i))).
Proof.
  intros n i dt phi Hi. unfold heat_step.
  rewrite (seam_grid n i phi Hi). ring.
Qed.

(* level-0 data (N_0 = 8, nodes 0..8): quartic 16 (i (8 - i))^2 / 8^4, and the rough datum
   quartic + a * (-1)^i with a = 1/8 *)
Definition quartic8 (i : nat) : Q :=
  (16 * Z.of_nat (i * (8 - i)) * Z.of_nat (i * (8 - i)))%Z # 4096.
Definition rough8 (i : nat) : Q :=
  quartic8 i + (if Nat.even i then 1 # 8 else - (1 # 8)).

(* ===================================================================== *)
(*  Part 2 -- the rows: exact rationals of the run (finite_diagnostic),    *)
(*  theorems about them (Th_coqc by the readouts at the end of the file)   *)
(* ===================================================================== *)

(* --------------------------------------------------------------------- *)
(*  T-C x O_near  (P09)  --  PASS candidate
    tape: pinned boundary, dt = 1/4, profile quartic; role: PASS candidate (seam_grid rows only) *)
(*  PASS candidate IN STATE S (C4 certified, informative held-out HIT, ACCEPT cells at K <= 2 on the *)
(*  relative grid); its matched FAIL row is TD_near.  DISCLOSED against the PASS reading: the one-ratio *)
(*  C3 ball MISSES both held-out values on this PASS row (C3_heldout_g3_MISS / _g4_MISS), so a C3 *)
(*  CERTIFICATE-MISS is not a regime classifier. *)
(* --------------------------------------------------------------------- *)
Module TC_near.
  Definition g0 : Q := (Qmake (121)%Z (512)%positive).
  Definition g1 : Q := (Qmake (15149)%Z (65536)%positive).
  Definition g2 : Q := (Qmake (253275869225)%Z (1099511627776)%positive).
  Definition g3 : Q := (Qmake (10025762293627835646641134960843137632839)%Z (43556142965880123323311949751266331066368)%positive).
  Definition g4 : Q := (Qmake (98740952122324366551186367748850683692824964384651879587728039155066342623755707929909502769726292099928551200223631925066910236311673984258048203410418543)%Z (429049853758163107186368799942587076079339706258956588087153966199096448962353503257659977541340909686081019461967553627320124249982290238285876768194691072)%positive).
  (* the tape as nat -> Q: the five witnessed levels, padded CONSTANT beyond level 4
     (bookkeeping only; Delta g k = 0 for k >= 4 carries no content) *)
  Definition g : nat -> Q := tape_of [g0; g1; g2; g3; g4] g4.

  (* C3 (coarse levels 0,1,2): khat_3 = kappa_0, copied from leaf_numbers.json *)
  Definition khat3 : Q := (Qmake (294058653)%Z (1895825408)%positive).
  Example khat3_lt_1 :
    khat3 < 1.
  Proof. vm_compute. reflexivity. Qed.
  (* khat_3 IS the witnessed ratio |Dg 1| / |Dg 0| (equality at the maximiser) *)
  Example khat3_attained :
    Qabs (Delta g 1) == khat3 * Qabs (Delta g 0).
  Proof. qdec. Qed.
  (* WINDOW [0,1): reads g_0, g_1, g_2 only *)
  Example C3_window_0_1 :
    forall k, (0 <= k < 0 + 1)%nat -> Qabs (Delta g (S k)) <= khat3 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* instance of the compiled plateau_certificate_window; on this window the bound is an identity: CERTIFIED carries one bit, |Dg 1| < |Dg 0| *)
  Example C3_bound_0_1 :
    (1 - khat3) * Qabs (g 1%nat - g 0%nat) <= Qabs (Delta g 0).
  Proof. exact (plateau_certificate_window khat3 g 0 1 (Qlt_le_weak _ _ khat3_lt_1) C3_window_0_1). Qed.
  (* the extrapolated C3 radius, base g_1 (same expression as the run's beta_3) *)
  Example C3_beta_value :
    beta_S1 g khat3 1 == (Qmake (99685883367)%Z (104973386055680)%positive).
  Proof. qdec. Qed.
  (* CERTIFICATE-MISS: held-out g_3 lies OUTSIDE the extrapolated C3 ball (the Dr hypothesis H3 is refuted on this row) *)
  Example C3_heldout_g3_MISS :
    ~ (Qabs (g 3%nat - g 1%nat) <= beta_S1 g khat3 1).
  Proof. qdec. Qed.
  (* the contrapositive of N4: the MISS forces the contraction premise to FAIL on [1,3) *)
  Corollary C3_persistence_refuted_g3 :
    ~ (forall k, (1 <= k < 1 + 2)%nat -> Qabs (Delta g (S k)) <= khat3 * Qabs (Delta g k)).
  Proof. exact (heldout_miss_refutes_persistence khat3 g 1 2 khat3_lt_1 C3_heldout_g3_MISS). Qed.
  (* CERTIFICATE-MISS: held-out g_4 lies OUTSIDE the extrapolated C3 ball (the Dr hypothesis H3 is refuted on this row) *)
  Example C3_heldout_g4_MISS :
    ~ (Qabs (g 4%nat - g 1%nat) <= beta_S1 g khat3 1).
  Proof. qdec. Qed.
  (* the contrapositive of N4: the MISS forces the contraction premise to FAIL on [1,4) (at m = 4 the last index is the padded one and is true by padding, so the failure is at a witnessed index) *)
  Corollary C3_persistence_refuted_g4 :
    ~ (forall k, (1 <= k < 1 + 3)%nat -> Qabs (Delta g (S k)) <= khat3 * Qabs (Delta g k)).
  Proof. exact (heldout_miss_refutes_persistence khat3 g 1 3 khat3_lt_1 C3_heldout_g4_MISS). Qed.

  (* C4 (coarse levels 0..3): khat_4 = max(kappa_0, kappa_1), copied *)
  Definition khat4 : Q := (Qmake (2509523440698378690236474650725923987)%Z (11648863374304832199347397766051528704)%positive).
  Example khat4_lt_1 :
    khat4 < 1.
  Proof. vm_compute. reflexivity. Qed.
  Example khat4_attained :
    Qabs (Delta g 2) == khat4 * Qabs (Delta g 1).
  Proof. qdec. Qed.
  (* WINDOW [0,2): reads g_0 .. g_3 only *)
  Example C4_window_0_2 :
    forall k, (0 <= k < 0 + 2)%nat -> Qabs (Delta g (S k)) <= khat4 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* instance of the compiled plateau_certificate_window -- a statement about witnessed values *)
  Example C4_bound_0_2 :
    (1 - khat4) * Qabs (g 2%nat - g 0%nat) <= Qabs (Delta g 0).
  Proof. exact (plateau_certificate_window khat4 g 0 2 (Qlt_le_weak _ _ khat4_lt_1) C4_window_0_2). Qed.
  Example C4_beta_value :
    beta_S1 g khat4 2 == (Qmake (2213841247931071850804525961783332039392828533)%Z (10048810527197831463981018321073640614640213819392)%positive).
  Proof. qdec. Qed.
  (* held-out g_4 lies INSIDE the extrapolated C4 ball (class INFORMATIVE; persistence premise at k = 2 FAILS: contained with slack although H4 is false) -- decided by computation, an observation about this tape *)
  Example C4_heldout_g4_inside :
    Qabs (g 4%nat - g 2%nat) <= beta_S1 g khat4 2.
  Proof. qdec. Qed.

  (* C5 (full tape): khat_5 = max(kappa_0, kappa_1, kappa_2); s = the level-0 reader scale of the
     relative tolerance grid; both copied from leaf_numbers.json *)
  Definition khat5 : Q := (Qmake (5944960650386672863783855149439623456451665559679723494672331392506957104327026438241613736937062191359569196458118075590501197882336928677988827121371)%Z (24720064540098677637483605430176772829323077418490671987713971078056231365679207206160684957564086137198254909767341006954934028993013748240930305998848)%positive).
  Definition s : Q := (Qmake (121)%Z (512)%positive).
  Example khat5_lt_1 :
    khat5 < 1.
  Proof. vm_compute. reflexivity. Qed.
  (* khat_5 is the LEAST kappa satisfying the window premise: equality at k = 2 *)
  Example khat5_attained :
    Qabs (Delta g 3) == khat5 * Qabs (Delta g 2).
  Proof. qdec. Qed.

  (* S1 -- witnessed window [0,3): k = 0,1,2 read g_0 .. g_4 only; NO padded index *)
  Example window_0_3 :
    forall k, (0 <= k < 0 + 3)%nat -> Qabs (Delta g (S k)) <= khat5 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* instance of the compiled plateau_certificate_window (multiplicative form) *)
  Example S1_bound_0_3 :
    (1 - khat5) * Qabs (g 3%nat - g 0%nat) <= Qabs (Delta g 0).
  Proof. exact (plateau_certificate_window khat5 g 0 3 (Qlt_le_weak _ _ khat5_lt_1) window_0_3). Qed.
  (* the same window in division form (N4) *)
  Example S1_radius_0_3 :
    Qabs (g 3%nat - g 0%nat) <= beta_S1 g khat5 0.
  Proof. exact (plateau_radius_window khat5 g 0 3 khat5_lt_1 window_0_3). Qed.

  (* S1 / S3 -- WINDOW [K,4), padded index carries no content: the premise at k = 3 is
     0 <= khat5 * |Dg 3| (true by padding); the conclusion needs g_K .. g_4 only.
     r_K := beta_K = beta_S1 g khat5 K; rho_K is NOT instantiated (no inner stage). *)
  Example licence_K0 :
    licence_ok g khat5 0 (4 - 0) = true.
  Proof. vm_compute. reflexivity. Qed.
  Example window_0_4 :
    forall k, (0 <= k < 0 + 4)%nat -> Qabs (Delta g (S k)) <= khat5 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* S3 radius premise of the gate: |g_4 - g_0| <= r_0 *)
  Example radius_K0 :
    dQ (g 4%nat) (g 0%nat) <= leaf_r g khat5 0.
  Proof. exact (plateau_radius_window khat5 g 0 4 khat5_lt_1 window_0_4). Qed.
  Example r_K0_value :
    leaf_r g khat5 0 == (Qmake (127870206895346858506880832532194915605781909864324002133713320853592871596759815107551150522067645271457037573411996480678140805490595407923513393152)%Z (18775103889712004773699750280737149372871411858810948493041639685549274261352180767919071220627023945838685713309222931364432831110676819562941478877477)%positive).
  Proof. qdec. Qed.
  Example r_K0_nonneg :
    0 <= leaf_r g khat5 0.
  Proof. exact (beta_S1_nonneg g khat5 0 khat5_lt_1). Qed.
  Example delta_K0_value :
    leaf_delta g 0 == (Qmake (339)%Z (65536)%positive).
  Proof. qdec. Qed.
  (* the threshold eps*_K = delta_K + r_K of leaf_gate_threshold *)
  Example eps_star_K0_value :
    leaf_delta g 0 + leaf_r g khat5 0 == (Qmake (14744862097705821337391157585999819626543931865005249342976152048862266407563640523213037344406786318149522871222955175090265365575151102485512535073074175)%Z (1230445208516165944849186834398389821300500847579034320439976898432157237991976518806344251515012641314484106907433234029899470019669316046876932759714332672)%positive).
  Proof. qdec. Qed.
  Example licence_K1 :
    licence_ok g khat5 1 (4 - 1) = true.
  Proof. vm_compute. reflexivity. Qed.
  Example window_1_4 :
    forall k, (1 <= k < 1 + 3)%nat -> Qabs (Delta g (S k)) <= khat5 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* S3 radius premise of the gate: |g_4 - g_1| <= r_1 *)
  Example radius_K1 :
    dQ (g 4%nat) (g 1%nat) <= leaf_r g khat5 1.
  Proof. exact (plateau_radius_window khat5 g 1 3 khat5_lt_1 window_1_4). Qed.
  Example r_K1_value :
    leaf_r g khat5 1 == (Qmake (19833757180279867406606130286621739387767983446327209906772630941743518415882075990752594371348070119021464141178933022902578701913303764426588946432)%Z (18775103889712004773699750280737149372871411858810948493041639685549274261352180767919071220627023945838685713309222931364432831110676819562941478877477)%positive).
  Proof. qdec. Qed.
  Example r_K1_nonneg :
    0 <= leaf_r g khat5 1.
  Proof. exact (beta_S1_nonneg g khat5 1 khat5_lt_1). Qed.
  Example delta_K1_value :
    leaf_delta g 1 == (Qmake (882175959)%Z (1099511627776)%positive).
  Proof. qdec. Qed.
  (* the threshold eps*_K = delta_K + r_K of leaf_gate_threshold *)
  Example eps_star_K1_value :
    leaf_delta g 1 + leaf_r g khat5 1 == (Qmake (38370391921434762944530109149113616085172315482718773979864621970014409224206311009134876048981917422777682726588625322711704308084792066091635115736313703270675)%Z (20643445039440755548578894945058016084159903628016535865434707460006363327754796322942099678025694326063623790153099372898173866805516363890720426327203457534001152)%positive).
  Proof. qdec. Qed.
  Example licence_K2 :
    licence_ok g khat5 2 (4 - 2) = true.
  Proof. vm_compute. reflexivity. Qed.
  Example window_2_4 :
    forall k, (2 <= k < 2 + 2)%nat -> Qabs (Delta g (S k)) <= khat5 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* S3 radius premise of the gate: |g_4 - g_2| <= r_2 *)
  Example radius_K2 :
    dQ (g 4%nat) (g 2%nat) <= leaf_r g khat5 2.
  Proof. exact (plateau_radius_window khat5 g 2 2 khat5_lt_1 window_2_4). Qed.
  Example r_K2_value :
    leaf_r g khat5 2 == (Qmake (4272801299294354567091680816157089773677387491954271573434512643610758679860935450782214207423831550745345604732535378796573016359513453131565367296)%Z (18775103889712004773699750280737149372871411858810948493041639685549274261352180767919071220627023945838685713309222931364432831110676819562941478877477)%positive).
  Proof. qdec. Qed.
  Example r_K2_nonneg :
    0 <= leaf_r g khat5 2.
  Proof. exact (beta_S1_nonneg g khat5 2 khat5_lt_1). Qed.
  Example delta_K2_value :
    leaf_delta g 2 == (Qmake (7528570322095136070709423952177771961)%Z (43556142965880123323311949751266331066368)%positive).
  Proof. qdec. Qed.
  (* the threshold eps*_K = delta_K + r_K of leaf_gate_threshold *)
  Example eps_star_K2_value :
    leaf_delta g 2 + leaf_r g khat5 2 == (Qmake (327456434195202003098659186162288025013558042987685334975214754414845259177652802495275652900710648335069027366640644748043493154043065777106154849919505911219261414646704063326434437723325)%Z (817771109219548079430969239355401835683683301623993715383292340104243352685841667786350320375744424812893899104359686889805107700424162559698291518489652348984831693443888637422444397027393536)%positive).
  Proof. qdec. Qed.

  (* S5 -- gate' on the protocol's frozen grids: relative eps_j = 2^-j * s (scoring grid) and
     absolute eps_j = 2^-j, j = 2,4,..,24; cells K = 0,1,2 (K = 3 is unscored by the protocol
     and is not instantiated).  ACCEPT / HOLD by computation through the compiled gate'. *)
  Example gate_K0_rel_j4_ACCEPT :
    leaf_gate g khat5 4 0 (eps_rel s 4) = ACCEPT (leaf_r g khat5 0 * leaf_r g khat5 0).
  Proof. vm_compute. reflexivity. Qed.
  (* ACCEPT ==> the finest readout ON THIS TAPE, g_4, lies within eps of g_1 (nothing about a finer level, a limit, or the model) *)
  Theorem heldout_K0_rel_j4 :
    dQ (g 4%nat) (g 1%nat) <= eps_rel s 4.
  Proof. exact (leaf_accept_certified g khat5 4 0 (eps_rel s 4) ltac:(lia) gate_K0_rel_j4_ACCEPT). Qed.
  Example gate_K0_rel_j6_HOLD :
    leaf_gate g khat5 4 0 (eps_rel s 6) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* too tight for the level: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K0_rel_below_j6 :
    forall eps', eps' <= eps_rel s 6 -> forall c : option (Certificate' (leaf_delta g 0) eps'), gate' (leaf_delta g 0) eps' c <> ACCEPT (leaf_r g khat5 0 * leaf_r g khat5 0).
  Proof. exact (leaf_hold_sound g khat5 4 0 (eps_rel s 6) licence_K0 gate_K0_rel_j6_HOLD). Qed.
  (* HOLD is not FALSE: the gate HOLDs at this cell although the inequality it would have certified is TRUE on the tape (the cost of the certificate's slack) *)
  Example hold_is_not_false_K0_rel_j6 :
    leaf_gate g khat5 4 0 (eps_rel s 6) = HOLD /\ dQ (g 4%nat) (g 1%nat) <= eps_rel s 6.
  Proof. split; [ vm_compute; reflexivity | qdec ]. Qed.
  Example gate_K1_rel_j6_ACCEPT :
    leaf_gate g khat5 4 1 (eps_rel s 6) = ACCEPT (leaf_r g khat5 1 * leaf_r g khat5 1).
  Proof. vm_compute. reflexivity. Qed.
  (* ACCEPT ==> the finest readout ON THIS TAPE, g_4, lies within eps of g_2 (nothing about a finer level, a limit, or the model) *)
  Theorem heldout_K1_rel_j6 :
    dQ (g 4%nat) (g 2%nat) <= eps_rel s 6.
  Proof. exact (leaf_accept_certified g khat5 4 1 (eps_rel s 6) ltac:(lia) gate_K1_rel_j6_ACCEPT). Qed.
  Example gate_K1_rel_j8_HOLD :
    leaf_gate g khat5 4 1 (eps_rel s 8) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* too tight for the level: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K1_rel_below_j8 :
    forall eps', eps' <= eps_rel s 8 -> forall c : option (Certificate' (leaf_delta g 1) eps'), gate' (leaf_delta g 1) eps' c <> ACCEPT (leaf_r g khat5 1 * leaf_r g khat5 1).
  Proof. exact (leaf_hold_sound g khat5 4 1 (eps_rel s 8) licence_K1 gate_K1_rel_j8_HOLD). Qed.
  (* HOLD is not FALSE: the gate HOLDs at this cell although the inequality it would have certified is TRUE on the tape (the cost of the certificate's slack) *)
  Example hold_is_not_false_K1_rel_j8 :
    leaf_gate g khat5 4 1 (eps_rel s 8) = HOLD /\ dQ (g 4%nat) (g 2%nat) <= eps_rel s 8.
  Proof. split; [ vm_compute; reflexivity | qdec ]. Qed.
  Example gate_K2_rel_j8_ACCEPT :
    leaf_gate g khat5 4 2 (eps_rel s 8) = ACCEPT (leaf_r g khat5 2 * leaf_r g khat5 2).
  Proof. vm_compute. reflexivity. Qed.
  (* ACCEPT ==> the finest readout ON THIS TAPE, g_4, lies within eps of g_3 (nothing about a finer level, a limit, or the model) *)
  Theorem heldout_K2_rel_j8 :
    dQ (g 4%nat) (g 3%nat) <= eps_rel s 8.
  Proof. exact (leaf_accept_certified g khat5 4 2 (eps_rel s 8) ltac:(lia) gate_K2_rel_j8_ACCEPT). Qed.
  Example gate_K2_rel_j10_HOLD :
    leaf_gate g khat5 4 2 (eps_rel s 10) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* too tight for the level: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K2_rel_below_j10 :
    forall eps', eps' <= eps_rel s 10 -> forall c : option (Certificate' (leaf_delta g 2) eps'), gate' (leaf_delta g 2) eps' c <> ACCEPT (leaf_r g khat5 2 * leaf_r g khat5 2).
  Proof. exact (leaf_hold_sound g khat5 4 2 (eps_rel s 10) licence_K2 gate_K2_rel_j10_HOLD). Qed.
  (* HOLD is not FALSE: the gate HOLDs at this cell although the inequality it would have certified is TRUE on the tape (the cost of the certificate's slack) *)
  Example hold_is_not_false_K2_rel_j10 :
    leaf_gate g khat5 4 2 (eps_rel s 10) = HOLD /\ dQ (g 4%nat) (g 3%nat) <= eps_rel s 10.
  Proof. split; [ vm_compute; reflexivity | qdec ]. Qed.
  Example gate_K0_abs_j6_ACCEPT :
    leaf_gate g khat5 4 0 (eps_abs 6) = ACCEPT (leaf_r g khat5 0 * leaf_r g khat5 0).
  Proof. vm_compute. reflexivity. Qed.
  (* ACCEPT ==> the finest readout ON THIS TAPE, g_4, lies within eps of g_1 (nothing about a finer level, a limit, or the model) *)
  Theorem heldout_K0_abs_j6 :
    dQ (g 4%nat) (g 1%nat) <= eps_abs 6.
  Proof. exact (leaf_accept_certified g khat5 4 0 (eps_abs 6) ltac:(lia) gate_K0_abs_j6_ACCEPT). Qed.
  Example gate_K0_abs_j8_HOLD :
    leaf_gate g khat5 4 0 (eps_abs 8) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* too tight for the level: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K0_abs_below_j8 :
    forall eps', eps' <= eps_abs 8 -> forall c : option (Certificate' (leaf_delta g 0) eps'), gate' (leaf_delta g 0) eps' c <> ACCEPT (leaf_r g khat5 0 * leaf_r g khat5 0).
  Proof. exact (leaf_hold_sound g khat5 4 0 (eps_abs 8) licence_K0 gate_K0_abs_j8_HOLD). Qed.
  Example gate_K1_abs_j8_ACCEPT :
    leaf_gate g khat5 4 1 (eps_abs 8) = ACCEPT (leaf_r g khat5 1 * leaf_r g khat5 1).
  Proof. vm_compute. reflexivity. Qed.
  (* ACCEPT ==> the finest readout ON THIS TAPE, g_4, lies within eps of g_2 (nothing about a finer level, a limit, or the model) *)
  Theorem heldout_K1_abs_j8 :
    dQ (g 4%nat) (g 2%nat) <= eps_abs 8.
  Proof. exact (leaf_accept_certified g khat5 4 1 (eps_abs 8) ltac:(lia) gate_K1_abs_j8_ACCEPT). Qed.
  Example gate_K1_abs_j10_HOLD :
    leaf_gate g khat5 4 1 (eps_abs 10) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* too tight for the level: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K1_abs_below_j10 :
    forall eps', eps' <= eps_abs 10 -> forall c : option (Certificate' (leaf_delta g 1) eps'), gate' (leaf_delta g 1) eps' c <> ACCEPT (leaf_r g khat5 1 * leaf_r g khat5 1).
  Proof. exact (leaf_hold_sound g khat5 4 1 (eps_abs 10) licence_K1 gate_K1_abs_j10_HOLD). Qed.
  Example gate_K2_abs_j10_ACCEPT :
    leaf_gate g khat5 4 2 (eps_abs 10) = ACCEPT (leaf_r g khat5 2 * leaf_r g khat5 2).
  Proof. vm_compute. reflexivity. Qed.
  (* ACCEPT ==> the finest readout ON THIS TAPE, g_4, lies within eps of g_3 (nothing about a finer level, a limit, or the model) *)
  Theorem heldout_K2_abs_j10 :
    dQ (g 4%nat) (g 3%nat) <= eps_abs 10.
  Proof. exact (leaf_accept_certified g khat5 4 2 (eps_abs 10) ltac:(lia) gate_K2_abs_j10_ACCEPT). Qed.
  Example gate_K2_abs_j12_HOLD :
    leaf_gate g khat5 4 2 (eps_abs 12) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* too tight for the level: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K2_abs_below_j12 :
    forall eps', eps' <= eps_abs 12 -> forall c : option (Certificate' (leaf_delta g 2) eps'), gate' (leaf_delta g 2) eps' c <> ACCEPT (leaf_r g khat5 2 * leaf_r g khat5 2).
  Proof. exact (leaf_hold_sound g khat5 4 2 (eps_abs 12) licence_K2 gate_K2_abs_j12_HOLD). Qed.

  (* S1-lemma readout (reported, not scored): the compiled bounded search Nidx on the compiled
     accept, bound 4.  The value 4 means NO WITNESSED INDEX (accept at 4 is a padding artifact). *)
  Example nidx_n10 :
    Nidx (accept g khat5 10) 4 = 0%nat.
  Proof. vm_compute. reflexivity. Qed.
  Example nidx_n1000 :
    Nidx (accept g khat5 1000) 4 = 2%nat.
  Proof. vm_compute. reflexivity. Qed.
  Example nidx_n100000 :
    Nidx (accept g khat5 100000) 4 = 4%nat.
  Proof. vm_compute. reflexivity. Qed.

  (* SEAM TIE: the level-0 readout g_0 of the run is recomputed HERE from the compiled seam operator Lvec 9 path_w (ONE pinned step of the declared datum, 9 nodes) *)
  Example seam_tie_level0 :
    heat_step_pinned 9 (1 # 4) quartic8 1 == g 0%nat.
  Proof. qdec. Qed.
End TC_near.

(* --------------------------------------------------------------------- *)
(*  T-D x O_near  (P18)  --  FAIL unstable dt
    tape: pinned boundary, dt = 1, profile quartic; role: FAIL control (unstable dt) *)
(*  FAIL control, unstable dt: the gap GROWS at every witnessed index, so no kappa <= 1 licences any *)
(*  window; the leaf's gate HOLDs for every kappa, every scored cell and every tolerance. *)
(* --------------------------------------------------------------------- *)
Module TD_near.
  Definition g0 : Q := (Qmake (95)%Z (256)%positive).
  Definition g1 : Q := (Qmake (101)%Z (256)%positive).
  Definition g2 : Q := (Qmake (7729357)%Z (2048)%positive).
  Definition g3 : Q := (Qmake (149945015726043356390435627101)%Z (8192)%positive).
  Definition g4 : Q := (Qmake (1507297175777117769846267476049251320765303835276149795482432128699182252195521496666637590072886630935965467040102888169)%Z (32768)%positive).
  (* the tape as nat -> Q: the five witnessed levels, padded CONSTANT beyond level 4
     (bookkeeping only; Delta g k = 0 for k >= 4 carries no content) *)
  Definition g : nat -> Q := tape_of [g0; g1; g2; g3; g4] g4.

  (* C3 verdict HOLD: the gap GROWS at k = 0 (kappa_0 ~ 161011) *)
  Example C3_gap_grows_k0 :
    Qabs (Delta g 0) < Qabs (Delta g 1).
  Proof. vm_compute. reflexivity. Qed.
  (* NO kappa <= 1 satisfies the window premise on [0,1): no licence exists, the verdict is HOLD (HOLD is not FALSE) *)
  Theorem C3_no_licence :
    forall kappa, kappa <= 1 -> ~ (forall k, (0 <= k < 0 + 1)%nat -> Qabs (Delta g (S k)) <= kappa * Qabs (Delta g k)).
  Proof. exact (no_licence_if_gap_grows g 0 1 0 ltac:(lia) C3_gap_grows_k0). Qed.

  (* C4 verdict HOLD: the gap GROWS at k = 0 (kappa_0 ~ 161011) *)
  Example C4_gap_grows_k0 :
    Qabs (Delta g 0) < Qabs (Delta g 1).
  Proof. vm_compute. reflexivity. Qed.
  (* no kappa <= 1 licences the window [0,2): HOLD *)
  Theorem C4_no_licence :
    forall kappa, kappa <= 1 -> ~ (forall k, (0 <= k < 0 + 2)%nat -> Qabs (Delta g (S k)) <= kappa * Qabs (Delta g k)).
  Proof. exact (no_licence_if_gap_grows g 0 2 0 ltac:(lia) C4_gap_grows_k0). Qed.

  (* kappa_1 ~ 4.85036e+21 *)
  Example gap_grows_k1 :
    Qabs (Delta g 1) < Qabs (Delta g 2).
  Proof. vm_compute. reflexivity. Qed.
  (* kappa_2 ~ 2.51308e+90 *)
  Example gap_grows_k2 :
    Qabs (Delta g 2) < Qabs (Delta g 3).
  Proof. vm_compute. reflexivity. Qed.
  (* NO LICENCE: for EVERY kappa, every scored cell K <= 2 and EVERY tolerance the leaf's gate (the compiled gate' applied to the leaf's certificate) returns HOLD -- every window [K,4) contains k = 2, where the gap grows, so no kappa <= 1 satisfies the premise.  HOLD is not FALSE. *)
  Theorem C5_HOLD_everywhere :
    forall (kappa : Q) (K : nat) (eps : Q), (K <= 2)%nat -> leaf_gate g kappa 4 K eps = HOLD.
  Proof. exact (leaf_gate_holds_if_gap_grows g 4 2 ltac:(lia) gap_grows_k2). Qed.

  (* SEAM TIE: the level-0 readout g_0 of the run is recomputed HERE from the compiled seam operator Lvec 9 path_w (ONE pinned step of the declared datum, 9 nodes) *)
  Example seam_tie_level0 :
    heat_step_pinned 9 (1 # 1) quartic8 1 == g 0%nat.
  Proof. qdec. Qed.
End TD_near.

(* --------------------------------------------------------------------- *)
(*  T-A x O_mid  (P01)  --  CLOSED-FORM on levels 0-2 (same reader, two regimes)
    tape: free boundary, dt = 1/4, profile quartic; role: PASS candidate (literal stepper) *)
(*  CLOSED-FORM class: on levels 0-2 this ledger is a closed form for EVERY dt, so this row is never *)
(*  evidence of regime sensitivity by itself; it is the stable half of 'same reader, two regimes' *)
(*  (the unstable half is TB_mid, with the SAME khat_3 = 1/4, see trap_same_C3_ratio below). *)
(* --------------------------------------------------------------------- *)
Module TA_mid.
  Definition g0 : Q := (Qmake (481)%Z (512)%positive).
  Definition g1 : Q := (Qmake (3851)%Z (4096)%positive).
  Definition g2 : Q := (Qmake (15407)%Z (16384)%positive).
  Definition g3 : Q := (Qmake (167775540439415717701508570770306229371398713)%Z (178405961588244985132285746181186892047843328)%positive).
  Definition g4 : Q := (Qmake (26443093323013822415884161226022290365623969547993975297268436670202149405956281172654226660871572710736377121125797263056076409671850149868895900888985275068633)%Z (28118211215894977392565865673037386617935606989386978956879722328823984879196799189494004288149317857187005691459505594520051662846839373056303219880407274094592)%positive).
  (* the tape as nat -> Q: the five witnessed levels, padded CONSTANT beyond level 4
     (bookkeeping only; Delta g k = 0 for k >= 4 carries no content) *)
  Definition g : nat -> Q := tape_of [g0; g1; g2; g3; g4] g4.

  (* C3 (coarse levels 0,1,2): khat_3 = kappa_0, copied from leaf_numbers.json *)
  Definition khat3 : Q := (Qmake (1)%Z (4)%positive).
  Example khat3_lt_1 :
    khat3 < 1.
  Proof. vm_compute. reflexivity. Qed.
  (* khat_3 IS the witnessed ratio |Dg 1| / |Dg 0| (equality at the maximiser) *)
  Example khat3_attained :
    Qabs (Delta g 1) == khat3 * Qabs (Delta g 0).
  Proof. qdec. Qed.
  (* WINDOW [0,1): reads g_0, g_1, g_2 only *)
  Example C3_window_0_1 :
    forall k, (0 <= k < 0 + 1)%nat -> Qabs (Delta g (S k)) <= khat3 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* instance of the compiled plateau_certificate_window; on this window the bound is an identity: CERTIFIED carries one bit, |Dg 1| < |Dg 0| *)
  Example C3_bound_0_1 :
    (1 - khat3) * Qabs (g 1%nat - g 0%nat) <= Qabs (Delta g 0).
  Proof. exact (plateau_certificate_window khat3 g 0 1 (Qlt_le_weak _ _ khat3_lt_1) C3_window_0_1). Qed.
  (* the extrapolated C3 radius, base g_1 (same expression as the run's beta_3) *)
  Example C3_beta_value :
    beta_S1 g khat3 1 == (Qmake (1)%Z (4096)%positive).
  Proof. qdec. Qed.
  (* held-out g_3 lies INSIDE the extrapolated C3 ball -- decided by computation on the run's numbers; an observation about this tape, not an instance of the window lemma *)
  Example C3_heldout_g3_inside :
    Qabs (g 3%nat - g 1%nat) <= beta_S1 g khat3 1.
  Proof. qdec. Qed.
  (* held-out g_4 lies INSIDE the extrapolated C3 ball -- decided by computation on the run's numbers; an observation about this tape, not an instance of the window lemma *)
  Example C3_heldout_g4_inside :
    Qabs (g 4%nat - g 1%nat) <= beta_S1 g khat3 1.
  Proof. qdec. Qed.

  (* C4 (coarse levels 0..3): khat_4 = max(kappa_0, kappa_1), copied *)
  Definition khat4 : Q := (Qmake (1)%Z (4)%positive).
  Example khat4_lt_1 :
    khat4 < 1.
  Proof. vm_compute. reflexivity. Qed.
  Example khat4_attained :
    Qabs (Delta g 1) == khat4 * Qabs (Delta g 0).
  Proof. qdec. Qed.
  (* WINDOW [0,2): reads g_0 .. g_3 only *)
  Example C4_window_0_2 :
    forall k, (0 <= k < 0 + 2)%nat -> Qabs (Delta g (S k)) <= khat4 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* instance of the compiled plateau_certificate_window -- a statement about witnessed values *)
  Example C4_bound_0_2 :
    (1 - khat4) * Qabs (g 2%nat - g 0%nat) <= Qabs (Delta g 0).
  Proof. exact (plateau_certificate_window khat4 g 0 2 (Qlt_le_weak _ _ khat4_lt_1) C4_window_0_2). Qed.
  Example C4_beta_value :
    beta_S1 g khat4 2 == (Qmake (8166770586952690941768315866138686515769)%Z (133804471191183738849214309635890169035882496)%positive).
  Proof. qdec. Qed.
  (* held-out g_4 lies INSIDE the extrapolated C4 ball (class INFORMATIVE; persistence premise at k = 2 HOLDS) -- decided by computation, an observation about this tape *)
  Example C4_heldout_g4_inside :
    Qabs (g 4%nat - g 2%nat) <= beta_S1 g khat4 2.
  Proof. qdec. Qed.

  (* C5 (full tape): khat_5 = max(kappa_0, kappa_1, kappa_2); s = the level-0 reader scale of the
     relative tolerance grid; both copied from leaf_numbers.json *)
  Definition khat5 : Q := (Qmake (1)%Z (4)%positive).
  Definition s : Q := (Qmake (481)%Z (512)%positive).
  Example khat5_lt_1 :
    khat5 < 1.
  Proof. vm_compute. reflexivity. Qed.
  (* khat_5 is the LEAST kappa satisfying the window premise: equality at k = 0 *)
  Example khat5_attained :
    Qabs (Delta g 1) == khat5 * Qabs (Delta g 0).
  Proof. qdec. Qed.

  (* S1 -- witnessed window [0,3): k = 0,1,2 read g_0 .. g_4 only; NO padded index *)
  Example window_0_3 :
    forall k, (0 <= k < 0 + 3)%nat -> Qabs (Delta g (S k)) <= khat5 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* instance of the compiled plateau_certificate_window (multiplicative form) *)
  Example S1_bound_0_3 :
    (1 - khat5) * Qabs (g 3%nat - g 0%nat) <= Qabs (Delta g 0).
  Proof. exact (plateau_certificate_window khat5 g 0 3 (Qlt_le_weak _ _ khat5_lt_1) window_0_3). Qed.
  (* the same window in division form (N4) *)
  Example S1_radius_0_3 :
    Qabs (g 3%nat - g 0%nat) <= beta_S1 g khat5 0.
  Proof. exact (plateau_radius_window khat5 g 0 3 khat5_lt_1 window_0_3). Qed.

  (* S1 / S3 -- WINDOW [K,4), padded index carries no content: the premise at k = 3 is
     0 <= khat5 * |Dg 3| (true by padding); the conclusion needs g_K .. g_4 only.
     r_K := beta_K = beta_S1 g khat5 K; rho_K is NOT instantiated (no inner stage). *)
  Example licence_K0 :
    licence_ok g khat5 0 (4 - 0) = true.
  Proof. vm_compute. reflexivity. Qed.
  Example window_0_4 :
    forall k, (0 <= k < 0 + 4)%nat -> Qabs (Delta g (S k)) <= khat5 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* S3 radius premise of the gate: |g_4 - g_0| <= r_0 *)
  Example radius_K0 :
    dQ (g 4%nat) (g 0%nat) <= leaf_r g khat5 0.
  Proof. exact (plateau_radius_window khat5 g 0 4 khat5_lt_1 window_0_4). Qed.
  Example r_K0_value :
    leaf_r g khat5 0 == (Qmake (1)%Z (1024)%positive).
  Proof. qdec. Qed.
  Example r_K0_nonneg :
    0 <= leaf_r g khat5 0.
  Proof. exact (beta_S1_nonneg g khat5 0 khat5_lt_1). Qed.
  Example delta_K0_value :
    leaf_delta g 0 == (Qmake (3)%Z (4096)%positive).
  Proof. qdec. Qed.
  (* the threshold eps*_K = delta_K + r_K of leaf_gate_threshold *)
  Example eps_star_K0_value :
    leaf_delta g 0 + leaf_r g khat5 0 == (Qmake (7)%Z (4096)%positive).
  Proof. qdec. Qed.
  Example licence_K1 :
    licence_ok g khat5 1 (4 - 1) = true.
  Proof. vm_compute. reflexivity. Qed.
  Example window_1_4 :
    forall k, (1 <= k < 1 + 3)%nat -> Qabs (Delta g (S k)) <= khat5 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* S3 radius premise of the gate: |g_4 - g_1| <= r_1 *)
  Example radius_K1 :
    dQ (g 4%nat) (g 1%nat) <= leaf_r g khat5 1.
  Proof. exact (plateau_radius_window khat5 g 1 3 khat5_lt_1 window_1_4). Qed.
  Example r_K1_value :
    leaf_r g khat5 1 == (Qmake (1)%Z (4096)%positive).
  Proof. qdec. Qed.
  Example r_K1_nonneg :
    0 <= leaf_r g khat5 1.
  Proof. exact (beta_S1_nonneg g khat5 1 khat5_lt_1). Qed.
  Example delta_K1_value :
    leaf_delta g 1 == (Qmake (3)%Z (16384)%positive).
  Proof. qdec. Qed.
  (* the threshold eps*_K = delta_K + r_K of leaf_gate_threshold *)
  Example eps_star_K1_value :
    leaf_delta g 1 + leaf_r g khat5 1 == (Qmake (7)%Z (16384)%positive).
  Proof. qdec. Qed.
  Example licence_K2 :
    licence_ok g khat5 2 (4 - 2) = true.
  Proof. vm_compute. reflexivity. Qed.
  Example window_2_4 :
    forall k, (2 <= k < 2 + 2)%nat -> Qabs (Delta g (S k)) <= khat5 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* S3 radius premise of the gate: |g_4 - g_2| <= r_2 *)
  Example radius_K2 :
    dQ (g 4%nat) (g 2%nat) <= leaf_r g khat5 2.
  Proof. exact (plateau_radius_window khat5 g 2 2 khat5_lt_1 window_2_4). Qed.
  Example r_K2_value :
    leaf_r g khat5 2 == (Qmake (8166770586952690941768315866138686515769)%Z (133804471191183738849214309635890169035882496)%positive).
  Proof. qdec. Qed.
  Example r_K2_nonneg :
    0 <= leaf_r g khat5 2.
  Proof. exact (beta_S1_nonneg g khat5 2 khat5_lt_1). Qed.
  Example delta_K2_value :
    leaf_delta g 2 == (Qmake (8166770586952690941768315866138686515769)%Z (178405961588244985132285746181186892047843328)%positive).
  Proof. qdec. Qed.
  (* the threshold eps*_K = delta_K + r_K of leaf_gate_threshold *)
  Example eps_star_K2_value :
    leaf_delta g 2 + leaf_r g khat5 2 == (Qmake (57167394108668836592378211062970805610383)%Z (535217884764734955396857238543560676143529984)%positive).
  Proof. qdec. Qed.

  (* S5 -- gate' on the protocol's frozen grids: relative eps_j = 2^-j * s (scoring grid) and
     absolute eps_j = 2^-j, j = 2,4,..,24; cells K = 0,1,2 (K = 3 is unscored by the protocol
     and is not instantiated).  ACCEPT / HOLD by computation through the compiled gate'. *)
  Example gate_K0_rel_j8_ACCEPT :
    leaf_gate g khat5 4 0 (eps_rel s 8) = ACCEPT (leaf_r g khat5 0 * leaf_r g khat5 0).
  Proof. vm_compute. reflexivity. Qed.
  (* ACCEPT ==> the finest readout ON THIS TAPE, g_4, lies within eps of g_1 (nothing about a finer level, a limit, or the model) *)
  Theorem heldout_K0_rel_j8 :
    dQ (g 4%nat) (g 1%nat) <= eps_rel s 8.
  Proof. exact (leaf_accept_certified g khat5 4 0 (eps_rel s 8) ltac:(lia) gate_K0_rel_j8_ACCEPT). Qed.
  Example gate_K0_rel_j10_HOLD :
    leaf_gate g khat5 4 0 (eps_rel s 10) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* too tight for the level: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K0_rel_below_j10 :
    forall eps', eps' <= eps_rel s 10 -> forall c : option (Certificate' (leaf_delta g 0) eps'), gate' (leaf_delta g 0) eps' c <> ACCEPT (leaf_r g khat5 0 * leaf_r g khat5 0).
  Proof. exact (leaf_hold_sound g khat5 4 0 (eps_rel s 10) licence_K0 gate_K0_rel_j10_HOLD). Qed.
  (* HOLD is not FALSE: the gate HOLDs at this cell although the inequality it would have certified is TRUE on the tape (the cost of the certificate's slack) *)
  Example hold_is_not_false_K0_rel_j10 :
    leaf_gate g khat5 4 0 (eps_rel s 10) = HOLD /\ dQ (g 4%nat) (g 1%nat) <= eps_rel s 10.
  Proof. split; [ vm_compute; reflexivity | qdec ]. Qed.
  Example gate_K1_rel_j10_ACCEPT :
    leaf_gate g khat5 4 1 (eps_rel s 10) = ACCEPT (leaf_r g khat5 1 * leaf_r g khat5 1).
  Proof. vm_compute. reflexivity. Qed.
  (* ACCEPT ==> the finest readout ON THIS TAPE, g_4, lies within eps of g_2 (nothing about a finer level, a limit, or the model) *)
  Theorem heldout_K1_rel_j10 :
    dQ (g 4%nat) (g 2%nat) <= eps_rel s 10.
  Proof. exact (leaf_accept_certified g khat5 4 1 (eps_rel s 10) ltac:(lia) gate_K1_rel_j10_ACCEPT). Qed.
  Example gate_K1_rel_j12_HOLD :
    leaf_gate g khat5 4 1 (eps_rel s 12) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* too tight for the level: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K1_rel_below_j12 :
    forall eps', eps' <= eps_rel s 12 -> forall c : option (Certificate' (leaf_delta g 1) eps'), gate' (leaf_delta g 1) eps' c <> ACCEPT (leaf_r g khat5 1 * leaf_r g khat5 1).
  Proof. exact (leaf_hold_sound g khat5 4 1 (eps_rel s 12) licence_K1 gate_K1_rel_j12_HOLD). Qed.
  (* HOLD is not FALSE: the gate HOLDs at this cell although the inequality it would have certified is TRUE on the tape (the cost of the certificate's slack) *)
  Example hold_is_not_false_K1_rel_j12 :
    leaf_gate g khat5 4 1 (eps_rel s 12) = HOLD /\ dQ (g 4%nat) (g 2%nat) <= eps_rel s 12.
  Proof. split; [ vm_compute; reflexivity | qdec ]. Qed.
  Example gate_K2_rel_j12_ACCEPT :
    leaf_gate g khat5 4 2 (eps_rel s 12) = ACCEPT (leaf_r g khat5 2 * leaf_r g khat5 2).
  Proof. vm_compute. reflexivity. Qed.
  (* ACCEPT ==> the finest readout ON THIS TAPE, g_4, lies within eps of g_3 (nothing about a finer level, a limit, or the model) *)
  Theorem heldout_K2_rel_j12 :
    dQ (g 4%nat) (g 3%nat) <= eps_rel s 12.
  Proof. exact (leaf_accept_certified g khat5 4 2 (eps_rel s 12) ltac:(lia) gate_K2_rel_j12_ACCEPT). Qed.
  Example gate_K2_rel_j14_HOLD :
    leaf_gate g khat5 4 2 (eps_rel s 14) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* too tight for the level: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K2_rel_below_j14 :
    forall eps', eps' <= eps_rel s 14 -> forall c : option (Certificate' (leaf_delta g 2) eps'), gate' (leaf_delta g 2) eps' c <> ACCEPT (leaf_r g khat5 2 * leaf_r g khat5 2).
  Proof. exact (leaf_hold_sound g khat5 4 2 (eps_rel s 14) licence_K2 gate_K2_rel_j14_HOLD). Qed.
  (* HOLD is not FALSE: the gate HOLDs at this cell although the inequality it would have certified is TRUE on the tape (the cost of the certificate's slack) *)
  Example hold_is_not_false_K2_rel_j14 :
    leaf_gate g khat5 4 2 (eps_rel s 14) = HOLD /\ dQ (g 4%nat) (g 3%nat) <= eps_rel s 14.
  Proof. split; [ vm_compute; reflexivity | qdec ]. Qed.
  Example gate_K0_abs_j8_ACCEPT :
    leaf_gate g khat5 4 0 (eps_abs 8) = ACCEPT (leaf_r g khat5 0 * leaf_r g khat5 0).
  Proof. vm_compute. reflexivity. Qed.
  (* ACCEPT ==> the finest readout ON THIS TAPE, g_4, lies within eps of g_1 (nothing about a finer level, a limit, or the model) *)
  Theorem heldout_K0_abs_j8 :
    dQ (g 4%nat) (g 1%nat) <= eps_abs 8.
  Proof. exact (leaf_accept_certified g khat5 4 0 (eps_abs 8) ltac:(lia) gate_K0_abs_j8_ACCEPT). Qed.
  Example gate_K0_abs_j10_HOLD :
    leaf_gate g khat5 4 0 (eps_abs 10) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* too tight for the level: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K0_abs_below_j10 :
    forall eps', eps' <= eps_abs 10 -> forall c : option (Certificate' (leaf_delta g 0) eps'), gate' (leaf_delta g 0) eps' c <> ACCEPT (leaf_r g khat5 0 * leaf_r g khat5 0).
  Proof. exact (leaf_hold_sound g khat5 4 0 (eps_abs 10) licence_K0 gate_K0_abs_j10_HOLD). Qed.
  Example gate_K1_abs_j10_ACCEPT :
    leaf_gate g khat5 4 1 (eps_abs 10) = ACCEPT (leaf_r g khat5 1 * leaf_r g khat5 1).
  Proof. vm_compute. reflexivity. Qed.
  (* ACCEPT ==> the finest readout ON THIS TAPE, g_4, lies within eps of g_2 (nothing about a finer level, a limit, or the model) *)
  Theorem heldout_K1_abs_j10 :
    dQ (g 4%nat) (g 2%nat) <= eps_abs 10.
  Proof. exact (leaf_accept_certified g khat5 4 1 (eps_abs 10) ltac:(lia) gate_K1_abs_j10_ACCEPT). Qed.
  Example gate_K1_abs_j12_HOLD :
    leaf_gate g khat5 4 1 (eps_abs 12) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* too tight for the level: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K1_abs_below_j12 :
    forall eps', eps' <= eps_abs 12 -> forall c : option (Certificate' (leaf_delta g 1) eps'), gate' (leaf_delta g 1) eps' c <> ACCEPT (leaf_r g khat5 1 * leaf_r g khat5 1).
  Proof. exact (leaf_hold_sound g khat5 4 1 (eps_abs 12) licence_K1 gate_K1_abs_j12_HOLD). Qed.
  Example gate_K2_abs_j12_ACCEPT :
    leaf_gate g khat5 4 2 (eps_abs 12) = ACCEPT (leaf_r g khat5 2 * leaf_r g khat5 2).
  Proof. vm_compute. reflexivity. Qed.
  (* ACCEPT ==> the finest readout ON THIS TAPE, g_4, lies within eps of g_3 (nothing about a finer level, a limit, or the model) *)
  Theorem heldout_K2_abs_j12 :
    dQ (g 4%nat) (g 3%nat) <= eps_abs 12.
  Proof. exact (leaf_accept_certified g khat5 4 2 (eps_abs 12) ltac:(lia) gate_K2_abs_j12_ACCEPT). Qed.
  Example gate_K2_abs_j14_HOLD :
    leaf_gate g khat5 4 2 (eps_abs 14) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* too tight for the level: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K2_abs_below_j14 :
    forall eps', eps' <= eps_abs 14 -> forall c : option (Certificate' (leaf_delta g 2) eps'), gate' (leaf_delta g 2) eps' c <> ACCEPT (leaf_r g khat5 2 * leaf_r g khat5 2).
  Proof. exact (leaf_hold_sound g khat5 4 2 (eps_abs 14) licence_K2 gate_K2_abs_j14_HOLD). Qed.

  (* S1-lemma readout (reported, not scored): the compiled bounded search Nidx on the compiled
     accept, bound 4.  The value 4 means NO WITNESSED INDEX (accept at 4 is a padding artifact). *)
  Example nidx_n10 :
    Nidx (accept g khat5 10) 4 = 0%nat.
  Proof. vm_compute. reflexivity. Qed.
  Example nidx_n1000 :
    Nidx (accept g khat5 1000) 4 = 0%nat.
  Proof. vm_compute. reflexivity. Qed.
  Example nidx_n100000 :
    Nidx (accept g khat5 100000) 4 = 4%nat.
  Proof. vm_compute. reflexivity. Qed.

  (* SEAM TIE: the level-0 readout g_0 of the run is recomputed HERE from the compiled seam operator Lvec 9 path_w (ONE free step of the declared datum, 9 nodes) *)
  Example seam_tie_level0 :
    heat_step 9 (1 # 4) quartic8 4 == g 0%nat.
  Proof. qdec. Qed.
End TA_mid.

(* --------------------------------------------------------------------- *)
(*  T-B x O_mid  (P14)  --  TRAP (FAIL, regime-blind coarse window)
    tape: free boundary, dt = 1, profile quartic; role: FAIL control (dt above the Dr bound 1/2) *)
(*  THE TRAP (FAIL control behind a regime-blind coarse window).  The C3 window licence EXISTS and is *)
(*  a compiled fact (khat_3 = 1/4 exactly); what catches the row is the held-out test (both values *)
(*  OUTSIDE the extrapolated ball, by more than 10^22) and then C4 / C5: no licence, HOLD everywhere. *)
(* --------------------------------------------------------------------- *)
Module TB_mid.
  Definition g0 : Q := (Qmake (97)%Z (128)%positive).
  Definition g1 : Q := (Qmake (403)%Z (512)%positive).
  Definition g2 : Q := (Qmake (1627)%Z (2048)%positive).
  Definition g3 : Q := (Qmake (397243482153602189261125037)%Z (524288)%positive).
  Definition g4 : Q := (Qmake (14746276246568139131577987022908300315666844146937455642756939971590116904126736036979880939549780326933464671789743323)%Z (4194304)%positive).
  (* the tape as nat -> Q: the five witnessed levels, padded CONSTANT beyond level 4
     (bookkeeping only; Delta g k = 0 for k >= 4 carries no content) *)
  Definition g : nat -> Q := tape_of [g0; g1; g2; g3; g4] g4.

  (* C3 (coarse levels 0,1,2): khat_3 = kappa_0, copied from leaf_numbers.json *)
  Definition khat3 : Q := (Qmake (1)%Z (4)%positive).
  Example khat3_lt_1 :
    khat3 < 1.
  Proof. vm_compute. reflexivity. Qed.
  (* khat_3 IS the witnessed ratio |Dg 1| / |Dg 0| (equality at the maximiser) *)
  Example khat3_attained :
    Qabs (Delta g 1) == khat3 * Qabs (Delta g 0).
  Proof. qdec. Qed.
  (* WINDOW [0,1): reads g_0, g_1, g_2 only *)
  Example C3_window_0_1 :
    forall k, (0 <= k < 0 + 1)%nat -> Qabs (Delta g (S k)) <= khat3 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* instance of the compiled plateau_certificate_window; on this window the bound is an identity: CERTIFIED carries one bit, |Dg 1| < |Dg 0| *)
  Example C3_bound_0_1 :
    (1 - khat3) * Qabs (g 1%nat - g 0%nat) <= Qabs (Delta g 0).
  Proof. exact (plateau_certificate_window khat3 g 0 1 (Qlt_le_weak _ _ khat3_lt_1) C3_window_0_1). Qed.
  (* the extrapolated C3 radius, base g_1 (same expression as the run's beta_3) *)
  Example C3_beta_value :
    beta_S1 g khat3 1 == (Qmake (5)%Z (512)%positive).
  Proof. qdec. Qed.
  (* CERTIFICATE-MISS: held-out g_3 lies OUTSIDE the extrapolated C3 ball (the Dr hypothesis H3 is refuted on this row) *)
  Example C3_heldout_g3_MISS :
    ~ (Qabs (g 3%nat - g 1%nat) <= beta_S1 g khat3 1).
  Proof. qdec. Qed.
  (* the contrapositive of N4: the MISS forces the contraction premise to FAIL on [1,3) *)
  Corollary C3_persistence_refuted_g3 :
    ~ (forall k, (1 <= k < 1 + 2)%nat -> Qabs (Delta g (S k)) <= khat3 * Qabs (Delta g k)).
  Proof. exact (heldout_miss_refutes_persistence khat3 g 1 2 khat3_lt_1 C3_heldout_g3_MISS). Qed.
  (* CERTIFICATE-MISS: held-out g_4 lies OUTSIDE the extrapolated C3 ball (the Dr hypothesis H3 is refuted on this row) *)
  Example C3_heldout_g4_MISS :
    ~ (Qabs (g 4%nat - g 1%nat) <= beta_S1 g khat3 1).
  Proof. qdec. Qed.
  (* the contrapositive of N4: the MISS forces the contraction premise to FAIL on [1,4) (at m = 4 the last index is the padded one and is true by padding, so the failure is at a witnessed index) *)
  Corollary C3_persistence_refuted_g4 :
    ~ (forall k, (1 <= k < 1 + 3)%nat -> Qabs (Delta g (S k)) <= khat3 * Qabs (Delta g k)).
  Proof. exact (heldout_miss_refutes_persistence khat3 g 1 3 khat3_lt_1 C3_heldout_g4_MISS). Qed.

  (* C4 verdict HOLD: the gap GROWS at k = 1 (kappa_1 ~ 1.03449e+23) *)
  Example C4_gap_grows_k1 :
    Qabs (Delta g 1) < Qabs (Delta g 2).
  Proof. vm_compute. reflexivity. Qed.
  (* no kappa <= 1 licences the window [0,2): HOLD *)
  Theorem C4_no_licence :
    forall kappa, kappa <= 1 -> ~ (forall k, (0 <= k < 0 + 2)%nat -> Qabs (Delta g (S k)) <= kappa * Qabs (Delta g k)).
  Proof. exact (no_licence_if_gap_grows g 0 2 1 ltac:(lia) C4_gap_grows_k1). Qed.

  (* kappa_2 ~ 4.64019e+90 *)
  Example gap_grows_k2 :
    Qabs (Delta g 2) < Qabs (Delta g 3).
  Proof. vm_compute. reflexivity. Qed.
  (* NO LICENCE: for EVERY kappa, every scored cell K <= 2 and EVERY tolerance the leaf's gate (the compiled gate' applied to the leaf's certificate) returns HOLD -- every window [K,4) contains k = 2, where the gap grows, so no kappa <= 1 satisfies the premise.  HOLD is not FALSE. *)
  Theorem C5_HOLD_everywhere :
    forall (kappa : Q) (K : nat) (eps : Q), (K <= 2)%nat -> leaf_gate g kappa 4 K eps = HOLD.
  Proof. exact (leaf_gate_holds_if_gap_grows g 4 2 ltac:(lia) gap_grows_k2). Qed.

  (* SEAM TIE: the level-0 readout g_0 of the run is recomputed HERE from the compiled seam operator Lvec 9 path_w (ONE free step of the declared datum, 9 nodes) *)
  Example seam_tie_level0 :
    heat_step 9 (1 # 1) quartic8 4 == g 0%nat.
  Proof. qdec. Qed.
End TB_mid.

(* --------------------------------------------------------------------- *)
(*  T-C x O_ssq  (P13)  --  FAIL non-refining reader (instrument check, class d)
    tape: pinned boundary, dt = 1/4, profile quartic; role: PASS candidate (seam_grid rows only) *)
(*  FAIL control, NON-REFINING reader on a stable tape (kappa_k ~ 2): HOLD everywhere.  Forced by *)
(*  arithmetic (class d of the protocol) -- an instrument check, never evidence of certificate power. *)
(* --------------------------------------------------------------------- *)
Module TC_ssq.
  Definition g0 : Q := (Qmake (779815)%Z (262144)%positive).
  Definition g1 : Q := (Qmake (408927984853)%Z (68719476736)%positive).
  Definition g2 : Q := (Qmake (14735487098548524072578921549)%Z (1237940039285380274899124224)%positive).
  Definition g3 : Q := (Qmake (5920025021221530754893083422210361138079586935041286754541399994127060747964803987733033)%Z (248661618204893321077691124073410420050228075398673858720231988446579748506266687766528)%positive).
  Definition g4 : Q := (Qmake (147056882385105720303174172180684981588333362091278667212903776708269183866113250466677653902608538701699808057554448102623380881476293358063976082934666163097150010366062966487682365563006493058293890945896343317204168477034422958989923569444874985389414076196765056779437999088239591567831609504320784357105190871997377)%Z (3088413288990945714607167766096760666649729152895234960279866913260350640380788374205938472006792060778611417607373228628384532735989280347702230834056678923362997806954442769843550227998248540363155634742320939156524772391123850992097524347673943425610505012700786888921103128284156837954503288400970554554866145951744)%positive).
  (* the tape as nat -> Q: the five witnessed levels, padded CONSTANT beyond level 4
     (bookkeeping only; Delta g k = 0 for k >= 4 carries no content) *)
  Definition g : nat -> Q := tape_of [g0; g1; g2; g3; g4] g4.

  (* C3 verdict HOLD: the gap GROWS at k = 0 (kappa_0 ~ 2.00023) *)
  Example C3_gap_grows_k0 :
    Qabs (Delta g 0) < Qabs (Delta g 1).
  Proof. vm_compute. reflexivity. Qed.
  (* NO kappa <= 1 satisfies the window premise on [0,1): no licence exists, the verdict is HOLD (HOLD is not FALSE) *)
  Theorem C3_no_licence :
    forall kappa, kappa <= 1 -> ~ (forall k, (0 <= k < 0 + 1)%nat -> Qabs (Delta g (S k)) <= kappa * Qabs (Delta g k)).
  Proof. exact (no_licence_if_gap_grows g 0 1 0 ltac:(lia) C3_gap_grows_k0). Qed.

  (* C4 verdict HOLD: the gap GROWS at k = 0 (kappa_0 ~ 2.00023) *)
  Example C4_gap_grows_k0 :
    Qabs (Delta g 0) < Qabs (Delta g 1).
  Proof. vm_compute. reflexivity. Qed.
  (* no kappa <= 1 licences the window [0,2): HOLD *)
  Theorem C4_no_licence :
    forall kappa, kappa <= 1 -> ~ (forall k, (0 <= k < 0 + 2)%nat -> Qabs (Delta g (S k)) <= kappa * Qabs (Delta g k)).
  Proof. exact (no_licence_if_gap_grows g 0 2 0 ltac:(lia) C4_gap_grows_k0). Qed.

  (* kappa_1 ~ 1.99987 *)
  Example gap_grows_k1 :
    Qabs (Delta g 1) < Qabs (Delta g 2).
  Proof. vm_compute. reflexivity. Qed.
  (* kappa_2 ~ 1.99996 *)
  Example gap_grows_k2 :
    Qabs (Delta g 2) < Qabs (Delta g 3).
  Proof. vm_compute. reflexivity. Qed.
  (* NO LICENCE: for EVERY kappa, every scored cell K <= 2 and EVERY tolerance the leaf's gate (the compiled gate' applied to the leaf's certificate) returns HOLD -- every window [K,4) contains k = 2, where the gap grows, so no kappa <= 1 satisfies the premise.  HOLD is not FALSE. *)
  Theorem C5_HOLD_everywhere :
    forall (kappa : Q) (K : nat) (eps : Q), (K <= 2)%nat -> leaf_gate g kappa 4 K eps = HOLD.
  Proof. exact (leaf_gate_holds_if_gap_grows g 4 2 ltac:(lia) gap_grows_k2). Qed.

  (* SEAM TIE: the level-0 readout g_0 of the run is recomputed HERE from the compiled seam operator Lvec 9 path_w (ONE pinned step of the declared datum, 9 nodes) *)
  Example seam_tie_level0 :
    Sum 9 (fun i => heat_step_pinned 9 (1 # 4) quartic8 i * heat_step_pinned 9 (1 # 4) quartic8 i) == g 0%nat.
  Proof. qdec. Qed.
End TC_ssq.

(* --------------------------------------------------------------------- *)
(*  T-R x O_near  (P24)  --  FAIL rough datum (pair datum, dt)
    tape: free boundary, dt = 1/2, profile quartic+checkerboard; role: FAIL control (rough, non-restriction-coherent datum) *)
(*  DECLARED FAIL CONTROL THAT THE GATE ACCEPTS -- compiled on purpose.  Rough, non-restriction-coherent *)
(*  datum at the marginal step; the row is licensed under C5 and has ACCEPT cells at K <= 2 on both *)
(*  grids.  Every ACCEPT below is a TRUE statement about this tape (g_4 within eps of g_{K+1}); what it *)
(*  shows is that an ACCEPT certifies the LEDGER it is given, not the model or the datum.  The run *)
(*  reported this first, as a finding about the gate's power; the matched smooth tape shows the same *)
(*  narrow C3 MISS, so this file does NOT claim that the gate detects the rough datum. *)
(* --------------------------------------------------------------------- *)
Module TR_near.
  Definition g0 : Q := (Qmake (13)%Z (32)%positive).
  Definition g1 : Q := (Qmake (24913)%Z (65536)%positive).
  Definition g2 : Q := (Qmake (1593639701)%Z (4294967296)%positive).
  Definition g3 : Q := (Qmake (3549089164766021709412647)%Z (9671406556917033397649408)%positive).
  Definition g4 : Q := (Qmake (88626533130389846929108278684632804885714161388380891943612317990140030798652003331)%Z (242833611528216133864932738352939863330300854881517440156476551217363035650651062272)%positive).
  (* the tape as nat -> Q: the five witnessed levels, padded CONSTANT beyond level 4
     (bookkeeping only; Delta g k = 0 for k >= 4 carries no content) *)
  Definition g : nat -> Q := tape_of [g0; g1; g2; g3; g4] g4.

  (* C3 (coarse levels 0,1,2): khat_3 = kappa_0, copied from leaf_numbers.json *)
  Definition khat3 : Q := (Qmake (39058667)%Z (112132096)%positive).
  Example khat3_lt_1 :
    khat3 < 1.
  Proof. vm_compute. reflexivity. Qed.
  (* khat_3 IS the witnessed ratio |Dg 1| / |Dg 0| (equality at the maximiser) *)
  Example khat3_attained :
    Qabs (Delta g 1) == khat3 * Qabs (Delta g 0).
  Proof. qdec. Qed.
  (* WINDOW [0,1): reads g_0, g_1, g_2 only *)
  Example C3_window_0_1 :
    forall k, (0 <= k < 0 + 1)%nat -> Qabs (Delta g (S k)) <= khat3 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* instance of the compiled plateau_certificate_window; on this window the bound is an identity: CERTIFIED carries one bit, |Dg 1| < |Dg 0| *)
  Example C3_bound_0_1 :
    (1 - khat3) * Qabs (g 1%nat - g 0%nat) <= Qabs (Delta g 0).
  Proof. exact (plateau_certificate_window khat3 g 0 1 (Qlt_le_weak _ _ khat3_lt_1) C3_window_0_1). Qed.
  (* the extrapolated C3 radius, base g_1 (same expression as the run's beta_3) *)
  Example C3_beta_value :
    beta_S1 g khat3 1 == (Qmake (66829379237)%Z (4788940242944)%positive).
  Proof. qdec. Qed.
  (* held-out g_3 lies INSIDE the extrapolated C3 ball -- decided by computation on the run's numbers; an observation about this tape, not an instance of the window lemma *)
  Example C3_heldout_g3_inside :
    Qabs (g 3%nat - g 1%nat) <= beta_S1 g khat3 1.
  Proof. qdec. Qed.
  (* CERTIFICATE-MISS: held-out g_4 lies OUTSIDE the extrapolated C3 ball (the Dr hypothesis H3 is refuted on this row) *)
  Example C3_heldout_g4_MISS :
    ~ (Qabs (g 4%nat - g 1%nat) <= beta_S1 g khat3 1).
  Proof. qdec. Qed.
  (* the contrapositive of N4: the MISS forces the contraction premise to FAIL on [1,4) (at m = 4 the last index is the padded one and is true by padding, so the failure is at a witnessed index) *)
  Corollary C3_persistence_refuted_g4 :
    ~ (forall k, (1 <= k < 1 + 3)%nat -> Qabs (Delta g (S k)) <= khat3 * Qabs (Delta g k)).
  Proof. exact (heldout_miss_refutes_persistence khat3 g 1 3 khat3_lt_1 C3_heldout_g4_MISS). Qed.

  (* C4 (coarse levels 0..3): khat_4 = max(kappa_0, kappa_1), copied *)
  Definition khat4 : Q := (Qmake (39468417027192621418201)%Z (87952299073394144444416)%positive).
  Example khat4_lt_1 :
    khat4 < 1.
  Proof. vm_compute. reflexivity. Qed.
  Example khat4_attained :
    Qabs (Delta g 2) == khat4 * Qabs (Delta g 1).
  Proof. qdec. Qed.
  (* WINDOW [0,2): reads g_0 .. g_3 only *)
  Example C4_window_0_2 :
    forall k, (0 <= k < 0 + 2)%nat -> Qabs (Delta g (S k)) <= khat4 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* instance of the compiled plateau_certificate_window -- a statement about witnessed values *)
  Example C4_bound_0_2 :
    (1 - khat4) * Qabs (g 2%nat - g 0%nat) <= Qabs (Delta g 0).
  Proof. exact (plateau_certificate_window khat4 g 0 2 (Qlt_le_weak _ _ khat4_lt_1) C4_window_0_2). Qed.
  Example C4_beta_value :
    beta_S1 g khat4 2 == (Qmake (1541583757682246544830580598067)%Z (208236687771557102422984375664640)%positive).
  Proof. qdec. Qed.
  (* held-out g_4 lies INSIDE the extrapolated C4 ball (class INFORMATIVE; persistence premise at k = 2 FAILS: contained with slack although H4 is false) -- decided by computation, an observation about this tape *)
  Example C4_heldout_g4_inside :
    Qabs (g 4%nat - g 2%nat) <= beta_S1 g khat4 2.
  Proof. qdec. Qed.

  (* C5 (full tape): khat_5 = max(kappa_0, kappa_1, kappa_2); s = the level-0 reader scale of the
     relative tolerance grid; both copied from leaf_numbers.json *)
  Definition khat5 : Q := (Qmake (485441890389594072311087281947848976685009455245964206549261340417276836975979517)%Z (990989076057424094907407911115088263382435716346783229385557574009616950974480384)%positive).
  Definition s : Q := (Qmake (13)%Z (32)%positive).
  Example khat5_lt_1 :
    khat5 < 1.
  Proof. vm_compute. reflexivity. Qed.
  (* khat_5 is the LEAST kappa satisfying the window premise: equality at k = 2 *)
  Example khat5_attained :
    Qabs (Delta g 3) == khat5 * Qabs (Delta g 2).
  Proof. qdec. Qed.

  (* S1 -- witnessed window [0,3): k = 0,1,2 read g_0 .. g_4 only; NO padded index *)
  Example window_0_3 :
    forall k, (0 <= k < 0 + 3)%nat -> Qabs (Delta g (S k)) <= khat5 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* instance of the compiled plateau_certificate_window (multiplicative form) *)
  Example S1_bound_0_3 :
    (1 - khat5) * Qabs (g 3%nat - g 0%nat) <= Qabs (Delta g 0).
  Proof. exact (plateau_certificate_window khat5 g 0 3 (Qlt_le_weak _ _ khat5_lt_1) window_0_3). Qed.
  (* the same window in division form (N4) *)
  Example S1_radius_0_3 :
    Qabs (g 3%nat - g 0%nat) <= beta_S1 g khat5 0.
  Proof. exact (plateau_radius_window khat5 g 0 3 khat5_lt_1 window_0_3). Qed.

  (* S1 / S3 -- WINDOW [K,4), padded index carries no content: the premise at k = 3 is
     0 <= khat5 * |Dg 3| (true by padding); the conclusion needs g_K .. g_4 only.
     r_K := beta_K = beta_S1 g khat5 K; rho_K is NOT instantiated (no inner stage). *)
  Example licence_K0 :
    licence_ok g khat5 0 (4 - 0) = true.
  Proof. vm_compute. reflexivity. Qed.
  Example window_0_4 :
    forall k, (0 <= k < 0 + 4)%nat -> Qabs (Delta g (S k)) <= khat5 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* S3 radius premise of the gate: |g_4 - g_0| <= r_0 *)
  Example radius_K0 :
    dQ (g 4%nat) (g 0%nat) <= leaf_r g khat5 0.
  Proof. exact (plateau_radius_window khat5 g 0 4 khat5_lt_1 window_0_4). Qed.
  Example r_K0_value :
    leaf_r g khat5 0 == (Qmake (25872532793186227819619368529020935343129692240438020408305191179358743333699584)%Z (505547185667830022596320629167239286697426261100819022836296233592340113998500867)%positive).
  Proof. qdec. Qed.
  Example r_K0_nonneg :
    0 <= leaf_r g khat5 0.
  Proof. exact (beta_S1_nonneg g khat5 0 khat5_lt_1). Qed.
  Example delta_K0_value :
    leaf_delta g 0 == (Qmake (1711)%Z (65536)%positive).
  Proof. qdec. Qed.
  (* the threshold eps*_K = delta_K + r_K of leaf_gate_threshold *)
  Example eps_star_K0_value :
    leaf_delta g 0 + leaf_r g khat5 0 == (Qmake (2560573543811909795048879532423062438186643843412847453551591864806948538168770920461)%Z (33131540359926908360872468753104193893002527447503275480599509964707601711005752819712)%positive).
  Proof. qdec. Qed.
  Example licence_K1 :
    licence_ok g khat5 1 (4 - 1) = true.
  Proof. vm_compute. reflexivity. Qed.
  Example window_1_4 :
    forall k, (1 <= k < 1 + 3)%nat -> Qabs (Delta g (S k)) <= khat5 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* S3 radius premise of the gate: |g_4 - g_1| <= r_1 *)
  Example radius_K1 :
    dQ (g 4%nat) (g 1%nat) <= leaf_r g khat5 1.
  Proof. exact (plateau_radius_window khat5 g 1 3 khat5_lt_1 window_1_4). Qed.
  Example r_K1_value :
    leaf_r g khat5 1 == (Qmake (9012108743741316860719779840067455348340526757225269143878274572214457040109568)%Z (505547185667830022596320629167239286697426261100819022836296233592340113998500867)%positive).
  Proof. qdec. Qed.
  Example r_K1_nonneg :
    0 <= leaf_r g khat5 1.
  Proof. exact (beta_S1_nonneg g khat5 1 khat5_lt_1). Qed.
  Example delta_K1_value :
    leaf_delta g 1 == (Qmake (39058667)%Z (4294967296)%positive).
  Proof. qdec. Qed.
  (* the threshold eps*_K = delta_K + r_K of leaf_gate_threshold *)
  Example eps_star_K1_value :
    leaf_delta g 1 + leaf_r g khat5 1 == (Qmake (58452711500151546065957004313283517763495152383087406317983397993806909549077038680052417)%Z (2171308629028169866338138112203436450971813638799574661896569485047077385732473016792645632)%positive).
  Proof. qdec. Qed.
  Example licence_K2 :
    licence_ok g khat5 2 (4 - 2) = true.
  Proof. vm_compute. reflexivity. Qed.
  Example window_2_4 :
    forall k, (2 <= k < 2 + 2)%nat -> Qabs (Delta g (S k)) <= khat5 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* S3 radius premise of the gate: |g_4 - g_2| <= r_2 *)
  Example radius_K2 :
    dQ (g 4%nat) (g 2%nat) <= leaf_r g khat5 2.
  Proof. exact (plateau_radius_window khat5 g 2 2 khat5_lt_1 window_2_4). Qed.
  Example r_K2_value :
    leaf_r g khat5 2 == (Qmake (4044165643647054840820696275394234594444575896210177949057404716147462004277248)%Z (505547185667830022596320629167239286697426261100819022836296233592340113998500867)%positive).
  Proof. qdec. Qed.
  Example r_K2_nonneg :
    0 <= leaf_r g khat5 2.
  Proof. exact (beta_S1_nonneg g khat5 2 khat5_lt_1). Qed.
  Example delta_K2_value :
    leaf_delta g 2 == (Qmake (39468417027192621418201)%Z (9671406556917033397649408)%positive).
  Proof. qdec. Qed.
  (* the threshold eps*_K = delta_K + r_K of leaf_gate_threshold *)
  Example eps_star_K2_value :
    leaf_delta g 2 + leaf_r g khat5 2 == (Qmake (59065917274088212944308759618395554954097721170136431596822856825451799445408139266678367927314603149451)%Z (4889352366298804172176749740396347683366894041275265120498364329685815599878451291659630963723993650036736)%positive).
  Proof. qdec. Qed.

  (* S5 -- gate' on the protocol's frozen grids: relative eps_j = 2^-j * s (scoring grid) and
     absolute eps_j = 2^-j, j = 2,4,..,24; cells K = 0,1,2 (K = 3 is unscored by the protocol
     and is not instantiated).  ACCEPT / HOLD by computation through the compiled gate'. *)
  Example gate_K0_rel_j2_ACCEPT :
    leaf_gate g khat5 4 0 (eps_rel s 2) = ACCEPT (leaf_r g khat5 0 * leaf_r g khat5 0).
  Proof. vm_compute. reflexivity. Qed.
  (* ACCEPT ==> the finest readout ON THIS TAPE, g_4, lies within eps of g_1 (nothing about a finer level, a limit, or the model) *)
  Theorem heldout_K0_rel_j2 :
    dQ (g 4%nat) (g 1%nat) <= eps_rel s 2.
  Proof. exact (leaf_accept_certified g khat5 4 0 (eps_rel s 2) ltac:(lia) gate_K0_rel_j2_ACCEPT). Qed.
  Example gate_K0_rel_j4_HOLD :
    leaf_gate g khat5 4 0 (eps_rel s 4) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* too tight for the level: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K0_rel_below_j4 :
    forall eps', eps' <= eps_rel s 4 -> forall c : option (Certificate' (leaf_delta g 0) eps'), gate' (leaf_delta g 0) eps' c <> ACCEPT (leaf_r g khat5 0 * leaf_r g khat5 0).
  Proof. exact (leaf_hold_sound g khat5 4 0 (eps_rel s 4) licence_K0 gate_K0_rel_j4_HOLD). Qed.
  Example gate_K1_rel_j2_ACCEPT :
    leaf_gate g khat5 4 1 (eps_rel s 2) = ACCEPT (leaf_r g khat5 1 * leaf_r g khat5 1).
  Proof. vm_compute. reflexivity. Qed.
  (* ACCEPT ==> the finest readout ON THIS TAPE, g_4, lies within eps of g_2 (nothing about a finer level, a limit, or the model) *)
  Theorem heldout_K1_rel_j2 :
    dQ (g 4%nat) (g 2%nat) <= eps_rel s 2.
  Proof. exact (leaf_accept_certified g khat5 4 1 (eps_rel s 2) ltac:(lia) gate_K1_rel_j2_ACCEPT). Qed.
  Example gate_K1_rel_j4_HOLD :
    leaf_gate g khat5 4 1 (eps_rel s 4) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* too tight for the level: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K1_rel_below_j4 :
    forall eps', eps' <= eps_rel s 4 -> forall c : option (Certificate' (leaf_delta g 1) eps'), gate' (leaf_delta g 1) eps' c <> ACCEPT (leaf_r g khat5 1 * leaf_r g khat5 1).
  Proof. exact (leaf_hold_sound g khat5 4 1 (eps_rel s 4) licence_K1 gate_K1_rel_j4_HOLD). Qed.
  Example gate_K2_rel_j4_ACCEPT :
    leaf_gate g khat5 4 2 (eps_rel s 4) = ACCEPT (leaf_r g khat5 2 * leaf_r g khat5 2).
  Proof. vm_compute. reflexivity. Qed.
  (* ACCEPT ==> the finest readout ON THIS TAPE, g_4, lies within eps of g_3 (nothing about a finer level, a limit, or the model) *)
  Theorem heldout_K2_rel_j4 :
    dQ (g 4%nat) (g 3%nat) <= eps_rel s 4.
  Proof. exact (leaf_accept_certified g khat5 4 2 (eps_rel s 4) ltac:(lia) gate_K2_rel_j4_ACCEPT). Qed.
  Example gate_K2_rel_j6_HOLD :
    leaf_gate g khat5 4 2 (eps_rel s 6) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* too tight for the level: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K2_rel_below_j6 :
    forall eps', eps' <= eps_rel s 6 -> forall c : option (Certificate' (leaf_delta g 2) eps'), gate' (leaf_delta g 2) eps' c <> ACCEPT (leaf_r g khat5 2 * leaf_r g khat5 2).
  Proof. exact (leaf_hold_sound g khat5 4 2 (eps_rel s 6) licence_K2 gate_K2_rel_j6_HOLD). Qed.
  Example gate_K0_abs_j2_ACCEPT :
    leaf_gate g khat5 4 0 (eps_abs 2) = ACCEPT (leaf_r g khat5 0 * leaf_r g khat5 0).
  Proof. vm_compute. reflexivity. Qed.
  (* ACCEPT ==> the finest readout ON THIS TAPE, g_4, lies within eps of g_1 (nothing about a finer level, a limit, or the model) *)
  Theorem heldout_K0_abs_j2 :
    dQ (g 4%nat) (g 1%nat) <= eps_abs 2.
  Proof. exact (leaf_accept_certified g khat5 4 0 (eps_abs 2) ltac:(lia) gate_K0_abs_j2_ACCEPT). Qed.
  Example gate_K0_abs_j4_HOLD :
    leaf_gate g khat5 4 0 (eps_abs 4) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* too tight for the level: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K0_abs_below_j4 :
    forall eps', eps' <= eps_abs 4 -> forall c : option (Certificate' (leaf_delta g 0) eps'), gate' (leaf_delta g 0) eps' c <> ACCEPT (leaf_r g khat5 0 * leaf_r g khat5 0).
  Proof. exact (leaf_hold_sound g khat5 4 0 (eps_abs 4) licence_K0 gate_K0_abs_j4_HOLD). Qed.
  Example gate_K1_abs_j4_ACCEPT :
    leaf_gate g khat5 4 1 (eps_abs 4) = ACCEPT (leaf_r g khat5 1 * leaf_r g khat5 1).
  Proof. vm_compute. reflexivity. Qed.
  (* ACCEPT ==> the finest readout ON THIS TAPE, g_4, lies within eps of g_2 (nothing about a finer level, a limit, or the model) *)
  Theorem heldout_K1_abs_j4 :
    dQ (g 4%nat) (g 2%nat) <= eps_abs 4.
  Proof. exact (leaf_accept_certified g khat5 4 1 (eps_abs 4) ltac:(lia) gate_K1_abs_j4_ACCEPT). Qed.
  Example gate_K1_abs_j6_HOLD :
    leaf_gate g khat5 4 1 (eps_abs 6) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* too tight for the level: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K1_abs_below_j6 :
    forall eps', eps' <= eps_abs 6 -> forall c : option (Certificate' (leaf_delta g 1) eps'), gate' (leaf_delta g 1) eps' c <> ACCEPT (leaf_r g khat5 1 * leaf_r g khat5 1).
  Proof. exact (leaf_hold_sound g khat5 4 1 (eps_abs 6) licence_K1 gate_K1_abs_j6_HOLD). Qed.
  Example gate_K2_abs_j6_ACCEPT :
    leaf_gate g khat5 4 2 (eps_abs 6) = ACCEPT (leaf_r g khat5 2 * leaf_r g khat5 2).
  Proof. vm_compute. reflexivity. Qed.
  (* ACCEPT ==> the finest readout ON THIS TAPE, g_4, lies within eps of g_3 (nothing about a finer level, a limit, or the model) *)
  Theorem heldout_K2_abs_j6 :
    dQ (g 4%nat) (g 3%nat) <= eps_abs 6.
  Proof. exact (leaf_accept_certified g khat5 4 2 (eps_abs 6) ltac:(lia) gate_K2_abs_j6_ACCEPT). Qed.
  Example gate_K2_abs_j8_HOLD :
    leaf_gate g khat5 4 2 (eps_abs 8) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* too tight for the level: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K2_abs_below_j8 :
    forall eps', eps' <= eps_abs 8 -> forall c : option (Certificate' (leaf_delta g 2) eps'), gate' (leaf_delta g 2) eps' c <> ACCEPT (leaf_r g khat5 2 * leaf_r g khat5 2).
  Proof. exact (leaf_hold_sound g khat5 4 2 (eps_abs 8) licence_K2 gate_K2_abs_j8_HOLD). Qed.

  (* S1-lemma readout (reported, not scored): the compiled bounded search Nidx on the compiled
     accept, bound 4.  The value 4 means NO WITNESSED INDEX (accept at 4 is a padding artifact). *)
  Example nidx_n10 :
    Nidx (accept g khat5 10) 4 = 0%nat.
  Proof. vm_compute. reflexivity. Qed.
  Example nidx_n1000 :
    Nidx (accept g khat5 1000) 4 = 4%nat.
  Proof. vm_compute. reflexivity. Qed.
  Example nidx_n100000 :
    Nidx (accept g khat5 100000) 4 = 4%nat.
  Proof. vm_compute. reflexivity. Qed.

  (* SEAM TIE: the level-0 readout g_0 of the run is recomputed HERE from the compiled seam operator Lvec 9 path_w (ONE free step of the declared datum, 9 nodes) *)
  Example seam_tie_level0 :
    heat_step 9 (1 # 2) rough8 1 == g 0%nat.
  Proof. qdec. Qed.
End TR_near.

(* --------------------------------------------------------------------- *)
(*  T-R x O_state  (P21)  --  FAIL rough datum (pair datum, dt)
    tape: free boundary, dt = 1/2, profile quartic+checkerboard; role: FAIL control (rough, non-restriction-coherent datum) *)
(*  TOLERANCE-ONLY FAIL control: licensed (khat_5 ~ 0.9989, a useless contraction), and the gate HOLDs *)
(*  from the LARGEST tolerance of either grid downwards -- true-but-useless is a HOLD at the gate; never *)
(*  evidence of certificate power.  The numbers are the run's path-length ledger of the state tape *)
(*  (g_0 = 0 by construction; s = D_0); the ledger's construction (delta N3) is NOT a Coq object here: *)
(*  the tape is consumed as a scalar tape only. *)
(* --------------------------------------------------------------------- *)
Module TR_state.
  Definition g0 : Q := (Qmake (0)%Z (1)%positive).
  Definition g1 : Q := (Qmake (131)%Z (512)%positive).
  Definition g2 : Q := (Qmake (2178920881)%Z (4294967296)%positive).
  Definition g3 : Q := (Qmake (7327739197831415157108831)%Z (9671406556917033397649408)%positive).
  Definition g4 : Q := (Qmake (244712309557794446999278341208248362767159426177949815210395629966286473544380200883)%Z (242833611528216133864932738352939863330300854881517440156476551217363035650651062272)%positive).
  (* the tape as nat -> Q: the five witnessed levels, padded CONSTANT beyond level 4
     (bookkeeping only; Delta g k = 0 for k >= 4 carries no content) *)
  Definition g : nat -> Q := tape_of [g0; g1; g2; g3; g4] g4.

  (* C3 (coarse levels 0,1,2): khat_3 = kappa_0, copied from leaf_numbers.json *)
  Definition khat3 : Q := (Qmake (1080013233)%Z (1098907648)%positive).
  Example khat3_lt_1 :
    khat3 < 1.
  Proof. vm_compute. reflexivity. Qed.
  (* khat_3 IS the witnessed ratio |Dg 1| / |Dg 0| (equality at the maximiser) *)
  Example khat3_attained :
    Qabs (Delta g 1) == khat3 * Qabs (Delta g 0).
  Proof. qdec. Qed.
  (* WINDOW [0,1): reads g_0, g_1, g_2 only *)
  Example C3_window_0_1 :
    forall k, (0 <= k < 0 + 1)%nat -> Qabs (Delta g (S k)) <= khat3 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* instance of the compiled plateau_certificate_window; on this window the bound is an identity: CERTIFIED carries one bit, |Dg 1| < |Dg 0| *)
  Example C3_bound_0_1 :
    (1 - khat3) * Qabs (g 1%nat - g 0%nat) <= Qabs (Delta g 0).
  Proof. exact (plateau_certificate_window khat3 g 0 1 (Qlt_le_weak _ _ khat3_lt_1) C3_window_0_1). Qed.
  (* the extrapolated C3 radius, base g_1 (same expression as the run's beta_3) *)
  Example C3_beta_value :
    beta_S1 g khat3 1 == (Qmake (141481733523)%Z (9673940480)%positive).
  Proof. qdec. Qed.
  (* held-out g_3 lies INSIDE the extrapolated C3 ball -- decided by computation on the run's numbers; an observation about this tape, not an instance of the window lemma *)
  Example C3_heldout_g3_inside :
    Qabs (g 3%nat - g 1%nat) <= beta_S1 g khat3 1.
  Proof. qdec. Qed.
  (* held-out g_4 lies INSIDE the extrapolated C3 ball -- decided by computation on the run's numbers; an observation about this tape, not an instance of the window lemma *)
  Example C3_heldout_g4_inside :
    Qabs (g 4%nat - g 1%nat) <= beta_S1 g khat3 1.
  Proof. qdec. Qed.

  (* C4 (coarse levels 0..3): khat_4 = max(kappa_0, kappa_1), copied *)
  Definition khat4 : Q := (Qmake (2421245563960718728245343)%Z (2431973596847002336886784)%positive).
  Example khat4_lt_1 :
    khat4 < 1.
  Proof. vm_compute. reflexivity. Qed.
  Example khat4_attained :
    Qabs (Delta g 2) == khat4 * Qabs (Delta g 1).
  Proof. qdec. Qed.
  (* WINDOW [0,2): reads g_0 .. g_3 only *)
  Example C4_window_0_2 :
    forall k, (0 <= k < 0 + 2)%nat -> Qabs (Delta g (S k)) <= khat4 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* instance of the compiled plateau_certificate_window -- a statement about witnessed values *)
  Example C4_bound_0_2 :
    (1 - khat4) * Qabs (g 2%nat - g 0%nat) <= Qabs (Delta g 0).
  Proof. exact (plateau_certificate_window khat4 g 0 2 (Qlt_le_weak _ _ khat4_lt_1) C4_window_0_2). Qed.
  Example C4_beta_value :
    beta_S1 g khat4 2 == (Qmake (2614977249420124118695901310623919)%Z (46076550397000586095852085313536)%positive).
  Proof. qdec. Qed.
  (* held-out g_4 lies INSIDE the extrapolated C4 ball (class TRIVIAL; persistence premise at k = 2 FAILS: contained with slack although H4 is false) -- decided by computation, an observation about this tape *)
  Example C4_heldout_g4_inside :
    Qabs (g 4%nat - g 2%nat) <= beta_S1 g khat4 2.
  Proof. qdec. Qed.

  (* C5 (full tape): khat_5 = max(kappa_0, kappa_1, kappa_2); s = the level-0 reader scale of the
     relative tolerance grid; both copied from leaf_numbers.json *)
  Definition khat5 : Q := (Qmake (60724451817120126557678152688991885535567841497590042888121523305161226725400262579)%Z (60793618925340520340088734016733015887014507669366594477453873404946737343141773312)%positive).
  Definition s : Q := (Qmake (131)%Z (512)%positive).
  Example khat5_lt_1 :
    khat5 < 1.
  Proof. vm_compute. reflexivity. Qed.
  (* khat_5 is the LEAST kappa satisfying the window premise: equality at k = 2 *)
  Example khat5_attained :
    Qabs (Delta g 3) == khat5 * Qabs (Delta g 2).
  Proof. qdec. Qed.

  (* S1 -- witnessed window [0,3): k = 0,1,2 read g_0 .. g_4 only; NO padded index *)
  Example window_0_3 :
    forall k, (0 <= k < 0 + 3)%nat -> Qabs (Delta g (S k)) <= khat5 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* instance of the compiled plateau_certificate_window (multiplicative form) *)
  Example S1_bound_0_3 :
    (1 - khat5) * Qabs (g 3%nat - g 0%nat) <= Qabs (Delta g 0).
  Proof. exact (plateau_certificate_window khat5 g 0 3 (Qlt_le_weak _ _ khat5_lt_1) window_0_3). Qed.
  (* the same window in division form (N4) *)
  Example S1_radius_0_3 :
    Qabs (g 3%nat - g 0%nat) <= beta_S1 g khat5 0.
  Proof. exact (plateau_radius_window khat5 g 0 3 khat5_lt_1 window_0_3). Qed.

  (* S1 / S3 -- WINDOW [K,4), padded index carries no content: the premise at k = 3 is
     0 <= khat5 * |Dg 3| (true by padding); the conclusion needs g_K .. g_4 only.
     r_K := beta_K = beta_S1 g khat5 K; rho_K is NOT instantiated (no inner stage). *)
  Example licence_K0 :
    licence_ok g khat5 0 (4 - 0) = true.
  Proof. vm_compute. reflexivity. Qed.
  Example window_0_4 :
    forall k, (0 <= k < 0 + 4)%nat -> Qabs (Delta g (S k)) <= khat5 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* S3 radius premise of the gate: |g_4 - g_0| <= r_0 *)
  Example radius_K0 :
    dQ (g 4%nat) (g 0%nat) <= leaf_r g khat5 0.
  Proof. exact (plateau_radius_window khat5 g 0 4 khat5_lt_1 window_0_4). Qed.
  Example r_K0_value :
    leaf_r g khat5 0 == (Qmake (15554617342225797196389890930062548986716602548216843508879799640718794124905414656)%Z (69167108220393782410581327741130351446666171776551589332350099785510617741510733)%positive).
  Proof. qdec. Qed.
  Example r_K0_nonneg :
    0 <= leaf_r g khat5 0.
  Proof. exact (beta_S1_nonneg g khat5 0 khat5_lt_1). Qed.
  Example delta_K0_value :
    leaf_delta g 0 == (Qmake (131)%Z (512)%positive).
  Proof. qdec. Qed.
  (* the threshold eps*_K = delta_K + r_K of leaf_gate_threshold *)
  Example eps_star_K0_value :
    leaf_delta g 0 + leaf_r g khat5 0 == (Qmake (7973024970396479750047410310126113157238413773189752134748995279119924482875710209895)%Z (35413559408841616594217639803458739940693079949594413738163251090181436283653495296)%positive).
  Proof. qdec. Qed.
  Example licence_K1 :
    licence_ok g khat5 1 (4 - 1) = true.
  Proof. vm_compute. reflexivity. Qed.
  Example window_1_4 :
    forall k, (1 <= k < 1 + 3)%nat -> Qabs (Delta g (S k)) <= khat5 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* S3 radius premise of the gate: |g_4 - g_1| <= r_1 *)
  Example radius_K1 :
    dQ (g 4%nat) (g 1%nat) <= leaf_r g khat5 1.
  Proof. exact (plateau_radius_window khat5 g 1 3 khat5_lt_1 window_1_4). Qed.
  Example r_K1_value :
    leaf_r g khat5 1 == (Qmake (15287174126442289212346424612283916349051264381477588499848475545749357899364171776)%Z (69167108220393782410581327741130351446666171776551589332350099785510617741510733)%positive).
  Proof. qdec. Qed.
  Example r_K1_nonneg :
    0 <= leaf_r g khat5 1.
  Proof. exact (beta_S1_nonneg g khat5 1 khat5_lt_1). Qed.
  Example delta_K1_value :
    leaf_delta g 1 == (Qmake (1080013233)%Z (4294967296)%positive).
  Proof. qdec. Qed.
  (* the threshold eps*_K = delta_K + r_K of leaf_gate_threshold *)
  Example eps_star_K1_value :
    leaf_delta g 1 + leaf_r g khat5 1 == (Qmake (65732614313493369363875843605472031363915241305148037599381023167206465919591213137097767485)%Z (297070467765484055695186846996412413536417496009807295839266153401104717860545979867987968)%positive).
  Proof. qdec. Qed.
  Example licence_K2 :
    licence_ok g khat5 2 (4 - 2) = true.
  Proof. vm_compute. reflexivity. Qed.
  Example window_2_4 :
    forall k, (2 <= k < 2 + 2)%nat -> Qabs (Delta g (S k)) <= khat5 * Qabs (Delta g k).
  Proof. apply window_ok_sound. vm_compute. reflexivity. Qed.
  (* S3 radius premise of the gate: |g_4 - g_2| <= r_2 *)
  Example radius_K2 :
    dQ (g 4%nat) (g 2%nat) <= leaf_r g khat5 2.
  Proof. exact (plateau_radius_window khat5 g 2 2 khat5_lt_1 window_2_4). Qed.
  Example r_K2_value :
    leaf_r g khat5 2 == (Qmake (15219738646476782725648210522898287481158033748358513270499481534495217175758897152)%Z (69167108220393782410581327741130351446666171776551589332350099785510617741510733)%positive).
  Proof. qdec. Qed.
  Example r_K2_nonneg :
    0 <= leaf_r g khat5 2.
  Proof. exact (beta_S1_nonneg g khat5 2 khat5_lt_1). Qed.
  Example delta_K2_value :
    leaf_delta g 2 == (Qmake (2421245563960718728245343)%Z (9671406556917033397649408)%positive).
  Proof. qdec. Qed.
  (* the threshold eps*_K = delta_K + r_K of leaf_gate_threshold *)
  Example eps_star_K2_value :
    leaf_delta g 2 + leaf_r g khat5 2 == (Qmake (147363750694049750804956570988462556920257690238299233332699742459267911457158048729706848650642082317452435)%Z (668943223965706468364265745263596481002781199755815331242623632145102370757595403249140482641229003096064)%positive).
  Proof. qdec. Qed.

  (* S5 -- gate' on the protocol's frozen grids: relative eps_j = 2^-j * s (scoring grid) and
     absolute eps_j = 2^-j, j = 2,4,..,24; cells K = 0,1,2 (K = 3 is unscored by the protocol
     and is not instantiated).  ACCEPT / HOLD by computation through the compiled gate'. *)
  Example gate_K0_rel_j2_HOLD :
    leaf_gate g khat5 4 0 (eps_rel s 2) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* TOLERANCE-ONLY cell: licensed, yet HOLD from the LARGEST tolerance of the grid downwards: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K0_rel_below_j2 :
    forall eps', eps' <= eps_rel s 2 -> forall c : option (Certificate' (leaf_delta g 0) eps'), gate' (leaf_delta g 0) eps' c <> ACCEPT (leaf_r g khat5 0 * leaf_r g khat5 0).
  Proof. exact (leaf_hold_sound g khat5 4 0 (eps_rel s 2) licence_K0 gate_K0_rel_j2_HOLD). Qed.
  Example gate_K1_rel_j2_HOLD :
    leaf_gate g khat5 4 1 (eps_rel s 2) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* TOLERANCE-ONLY cell: licensed, yet HOLD from the LARGEST tolerance of the grid downwards: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K1_rel_below_j2 :
    forall eps', eps' <= eps_rel s 2 -> forall c : option (Certificate' (leaf_delta g 1) eps'), gate' (leaf_delta g 1) eps' c <> ACCEPT (leaf_r g khat5 1 * leaf_r g khat5 1).
  Proof. exact (leaf_hold_sound g khat5 4 1 (eps_rel s 2) licence_K1 gate_K1_rel_j2_HOLD). Qed.
  Example gate_K2_rel_j2_HOLD :
    leaf_gate g khat5 4 2 (eps_rel s 2) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* TOLERANCE-ONLY cell: licensed, yet HOLD from the LARGEST tolerance of the grid downwards: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K2_rel_below_j2 :
    forall eps', eps' <= eps_rel s 2 -> forall c : option (Certificate' (leaf_delta g 2) eps'), gate' (leaf_delta g 2) eps' c <> ACCEPT (leaf_r g khat5 2 * leaf_r g khat5 2).
  Proof. exact (leaf_hold_sound g khat5 4 2 (eps_rel s 2) licence_K2 gate_K2_rel_j2_HOLD). Qed.
  Example gate_K0_abs_j2_HOLD :
    leaf_gate g khat5 4 0 (eps_abs 2) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* TOLERANCE-ONLY cell: licensed, yet HOLD from the LARGEST tolerance of the grid downwards: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K0_abs_below_j2 :
    forall eps', eps' <= eps_abs 2 -> forall c : option (Certificate' (leaf_delta g 0) eps'), gate' (leaf_delta g 0) eps' c <> ACCEPT (leaf_r g khat5 0 * leaf_r g khat5 0).
  Proof. exact (leaf_hold_sound g khat5 4 0 (eps_abs 2) licence_K0 gate_K0_abs_j2_HOLD). Qed.
  Example gate_K1_abs_j2_HOLD :
    leaf_gate g khat5 4 1 (eps_abs 2) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* TOLERANCE-ONLY cell: licensed, yet HOLD from the LARGEST tolerance of the grid downwards: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K1_abs_below_j2 :
    forall eps', eps' <= eps_abs 2 -> forall c : option (Certificate' (leaf_delta g 1) eps'), gate' (leaf_delta g 1) eps' c <> ACCEPT (leaf_r g khat5 1 * leaf_r g khat5 1).
  Proof. exact (leaf_hold_sound g khat5 4 1 (eps_abs 2) licence_K1 gate_K1_abs_j2_HOLD). Qed.
  Example gate_K2_abs_j2_HOLD :
    leaf_gate g khat5 4 2 (eps_abs 2) = HOLD.
  Proof. vm_compute. reflexivity. Qed.
  (* TOLERANCE-ONLY cell: licensed, yet HOLD from the LARGEST tolerance of the grid downwards: NO certificate carrying r_K^2 exists at ANY tolerance <= this one (HOLD is not FALSE) *)
  Theorem too_tight_K2_abs_below_j2 :
    forall eps', eps' <= eps_abs 2 -> forall c : option (Certificate' (leaf_delta g 2) eps'), gate' (leaf_delta g 2) eps' c <> ACCEPT (leaf_r g khat5 2 * leaf_r g khat5 2).
  Proof. exact (leaf_hold_sound g khat5 4 2 (eps_abs 2) licence_K2 gate_K2_abs_j2_HOLD). Qed.

  (* S1-lemma readout (reported, not scored): the compiled bounded search Nidx on the compiled
     accept, bound 4.  The value 4 means NO WITNESSED INDEX (accept at 4 is a padding artifact). *)
  Example nidx_n10 :
    Nidx (accept g khat5 10) 4 = 4%nat.
  Proof. vm_compute. reflexivity. Qed.
  Example nidx_n1000 :
    Nidx (accept g khat5 1000) 4 = 4%nat.
  Proof. vm_compute. reflexivity. Qed.
  Example nidx_n100000 :
    Nidx (accept g khat5 100000) 4 = 4%nat.
  Proof. vm_compute. reflexivity. Qed.
End TR_state.

(* ---- across rows ---- *)
(** the TRAP made literal: the stable tape T-A and the unstable tape T-B carry the SAME C3
    certificate ratio for O_mid -- the one-ratio coarse window is regime-blind by construction *)
Example trap_same_C3_ratio : TA_mid.khat3 = TB_mid.khat3.
Proof. reflexivity. Qed.

(** same reader, two regimes (the matched pair of the run): ACCEPT at the protocol's cell on the
    stable pinned tape, HOLD at the same cell -- and at every other -- on the unstable one *)
Example matched_pair_near :
  leaf_gate TC_near.g TC_near.khat5 4 0 (eps_rel TC_near.s 4)
    = ACCEPT (leaf_r TC_near.g TC_near.khat5 0 * leaf_r TC_near.g TC_near.khat5 0)
  /\ (forall kappa eps, leaf_gate TD_near.g kappa 4 0 eps = HOLD).
Proof.
  split; [ exact TC_near.gate_K0_rel_j4_ACCEPT | ].
  intros kappa eps. exact (TD_near.C5_HOLD_everywhere kappa 0%nat eps ltac:(lia)).
Qed.

(* ===================================================================== *)
(*  Part 3 -- state layer on the small concrete grid: S2 section law,      *)
(*  S4 EXACT / NEVER / WITHIN RADIUS.  5 fine nodes, 3 coarse nodes (the    *)
(*  even ones), 2 coarsest nodes; TUPLE carriers (nat -> Q is never the     *)
(*  carrier of a record: Leibniz equality of functions is not available).   *)
(* ===================================================================== *)

Definition X5 : Type := (Q * Q * Q * Q * Q)%type.
Definition R3 : Type := (Q * Q * Q)%type.
Definition R2 : Type := (Q * Q)%type.

(* q_K : read the fine state at the shared nodes *)
Definition q53 (x : X5) : R3 := let '(x0, x1, x2, x3, x4) := x in (x0, x2, x4).
(* Lambda_K : piecewise-linear prolongation; shared-node values are COPIED, midpoints computed *)
Definition Lam35 (r : R3) : X5 := let '(a, b, c) := r in (a, (a + b) / 2, b, (b + c) / 2, c).
(* one level coarser, and the restriction between the two record levels *)
Definition q52 (x : X5) : R2 := let '(x0, x1, x2, x3, x4) := x in (x0, x4).
Definition res32 (r : R3) : R2 := let '(a, b, c) := r in (a, c).
Definition Lam23 (r : R2) : R3 := let '(a, c) := r in (a, (a + c) / 2, c).

(* node accessor: reaches Lvec / seam_grid, which take nat -> Q *)
Definition to_fun5 (x : X5) : nat -> Q :=
  let '(x0, x1, x2, x3, x4) := x in
  fun i => match i with
           | 0%nat => x0 | 1%nat => x1 | 2%nat => x2 | 3%nat => x3 | 4%nat => x4
           | _ => 0
           end.

(** S2: q o Lambda = id on the record type -- LEIBNIZ, for every record (not one example). *)
Theorem S2_section_law : forall r : R3, q53 (Lam35 r) = r.
Proof. intros [[a b] c]. reflexivity. Qed.

Theorem S2_section_law_coarse : forall r : R2, res32 (Lam23 r) = r.
Proof. intros [a c]. reflexivity. Qed.

(** coherence of the nested restrictions: q_K = res_K o q_{K+1} *)
Theorem S2_restriction_coherence : forall x : X5, q52 x = res32 (q53 x).
Proof. intros [[[[x0 x1] x2] x3] x4]. reflexivity. Qed.

(** consequences REUSED from IDM_SignatureFunctor (not re-proved): P_K idempotent, fixes the image *)
Theorem S2_PK_idempotent : forall x : X5, PK q53 Lam35 (PK q53 Lam35 x) = PK q53 Lam35 x.
Proof. exact (PK_idempotent q53 Lam35 S2_section_law). Qed.

Theorem S2_PK_fixes_image : forall r : R3, PK q53 Lam35 (Lam35 r) = Lam35 r.
Proof. exact (PK_fixes_image q53 Lam35 S2_section_law). Qed.

(** the run's section example r = (1/2, 1/3, 1/5): Lambda r as rationals, q (Lambda r) = r *)
Example S2_section_example_values :
  to_fun5 (Lam35 (1 # 2, 1 # 3, 1 # 5)) 0%nat == 1 # 2 /\
  to_fun5 (Lam35 (1 # 2, 1 # 3, 1 # 5)) 1%nat == 5 # 12 /\
  to_fun5 (Lam35 (1 # 2, 1 # 3, 1 # 5)) 2%nat == 1 # 3 /\
  to_fun5 (Lam35 (1 # 2, 1 # 3, 1 # 5)) 3%nat == 4 # 15 /\
  to_fun5 (Lam35 (1 # 2, 1 # 3, 1 # 5)) 4%nat == 1 # 5.
Proof. repeat split; qdec. Qed.

Example S2_section_example : q53 (Lam35 (1 # 2, 1 # 3, 1 # 5)) = (1 # 2, 1 # 3, 1 # 5).
Proof. exact (S2_section_law (1 # 2, 1 # 3, 1 # 5)). Qed.

(** the fine-grid operator on the tuple carrier IS the seam operator (seam_grid, n = 5) *)
Theorem small_grid_seam : forall (x : X5) (i : nat), (i < 3)%nat ->
  Lvec 5 path_w (to_fun5 x) (S i)
  == - (to_fun5 x i - 2 * to_fun5 x (S i) + to_fun5 x (S (S i))).
Proof. intros x i Hi. apply seam_grid. lia. Qed.

(* ---- S4 EXACT: the shared-node reader is in Alg_Q ---- *)
Definition P_sh (x : X5) : Q := to_fun5 x 2.     (* fine node 2 = coarse node 1: shared *)
Definition P_sh0 (x : X5) : Q := to_fun5 x 0.    (* fine node 0 = coarse node 0: shared *)
Definition P_odd (x : X5) : Q := to_fun5 x 1.    (* fine node 1: NOT shared *)

Theorem S4_P_sh_in_alg : InAlg q53 P_sh.
Proof.
  unfold InAlg. intros [[[[s0 s1] s2] s3] s4] [[[[t0 t1] t2] t3] t4] H.
  cbn in H. injection H as H0 H2 H4. cbn. exact H2.
Qed.

Theorem S4_P_sh0_in_alg : InAlg q53 P_sh0.
Proof.
  unfold InAlg. intros [[[[s0 s1] s2] s3] s4] [[[[t0 t1] t2] t3] t4] H.
  cbn in H. injection H as H0 H2 H4. cbn. exact H0.
Qed.

(** EXACT, through exact_on_alg: the round trip returns the shared-node reader exactly *)
Theorem S4_exact_P_sh : forall x : X5, P_sh (PK q53 Lam35 x) = P_sh x.
Proof. exact (exact_on_alg q53 Lam35 S2_section_law P_sh S4_P_sh_in_alg). Qed.

Theorem S4_exact_P_sh0 : forall x : X5, P_sh0 (Lam35 (q53 x)) = P_sh0 x.
Proof. exact (exact_on_alg q53 Lam35 S2_section_law P_sh0 S4_P_sh0_in_alg). Qed.

(** the same through the iff of IDM_BridgeRoundTrip *)
Theorem S4_exact_iff_P_sh : (forall x : X5, P_sh (Lam35 (q53 x)) = P_sh x) <-> InAlg q53 P_sh.
Proof. exact (roundtrip_exact q53 Lam35 S2_section_law P_sh). Qed.

(* ---- S4 NEVER: two fine states with the same record ---- *)
Definition x_nv : X5 := (0, 0, 0, 0, 0).
Definition x_nv' : X5 := (0, 1, 0, 1, 0).

Lemma never_same_record : q53 x_nv = q53 x_nv'.
Proof. reflexivity. Qed.

Lemma never_distinct : x_nv <> x_nv'.
Proof. unfold x_nv, x_nv'. intro H. discriminate H. Qed.

(** the pair is RATIONALLY distinct (Leibniz distinctness of Q-tuples alone would be weaker) *)
Lemma never_rationally_distinct : ~ (to_fun5 x_nv 1%nat == to_fun5 x_nv' 1%nat).
Proof. intro H. vm_compute in H. discriminate H. Qed.

Theorem S4_never :
  ~ (exists D : R3 -> X5, D (q53 x_nv) = x_nv /\ D (q53 x_nv') = x_nv').
Proof. exact (roundtrip_never X5 R3 q53 x_nv x_nv' never_same_record never_distinct). Qed.

Theorem S4_never_total : ~ (exists D : R3 -> X5, forall y : X5, D (q53 y) = y).
Proof. exact (roundtrip_never_total X5 R3 q53 x_nv x_nv' never_same_record never_distinct). Qed.

(** in particular the prolongation is not a left inverse: P_K merges the pair *)
Example S4_PK_merges : PK q53 Lam35 x_nv' = PK q53 Lam35 x_nv.
Proof. reflexivity. Qed.

(* ---- fail-able control for EXACT: the non-shared reader is NOT in Alg_Q ---- *)
Lemma P_odd_separates : P_odd x_nv <> P_odd x_nv'.
Proof. intro H. vm_compute in H. discriminate H. Qed.

Theorem S4_P_odd_not_in_alg : ~ InAlg q53 P_odd.
Proof. intro HP. exact (P_odd_separates (HP x_nv x_nv' never_same_record)). Qed.

Theorem S4_exact_fails_outside_alg : ~ (forall y : X5, P_odd (Lam35 (q53 y)) = P_odd y).
Proof.
  exact (roundtrip_exact_fails_outside_alg q53 Lam35 P_odd x_nv x_nv'
           never_same_record P_odd_separates).
Qed.

(** the separating fact with Qeq: P_odd (P_K x') == 0 (it computes to 0 # 2), P_odd x' = 1 *)
Example S4_exact_fails_Qeq :
  P_odd (Lam35 (q53 x_nv')) == 0 /\ P_odd x_nv' == 1 /\
  ~ (P_odd (Lam35 (q53 x_nv')) == P_odd x_nv').
Proof.
  split; [ qdec | split; [ qdec | ] ].
  intro H. vm_compute in H. discriminate H.
Qed.

(* ---- d_inf on the small grid: a finite max of dQ; triangle and symmetry PROVED ---- *)
Definition max5 (v0 v1 v2 v3 v4 : Q) : Q := Qmax v0 (Qmax v1 (Qmax v2 (Qmax v3 v4))).

Ltac max_r := eapply Qle_trans; [ | apply Q.le_max_r ].

Lemma max5_ub : forall v0 v1 v2 v3 v4 : Q,
  v0 <= max5 v0 v1 v2 v3 v4 /\ v1 <= max5 v0 v1 v2 v3 v4 /\ v2 <= max5 v0 v1 v2 v3 v4 /\
  v3 <= max5 v0 v1 v2 v3 v4 /\ v4 <= max5 v0 v1 v2 v3 v4.
Proof.
  intros v0 v1 v2 v3 v4. unfold max5. repeat split.
  - apply Q.le_max_l.
  - max_r. apply Q.le_max_l.
  - max_r. max_r. apply Q.le_max_l.
  - max_r. max_r. max_r. apply Q.le_max_l.
  - max_r. max_r. max_r. apply Q.le_max_r.
Qed.

Lemma max5_lub : forall v0 v1 v2 v3 v4 z : Q,
  v0 <= z -> v1 <= z -> v2 <= z -> v3 <= z -> v4 <= z -> max5 v0 v1 v2 v3 v4 <= z.
Proof.
  intros v0 v1 v2 v3 v4 z H0 H1 H2 H3 H4. unfold max5.
  repeat apply Q.max_lub; assumption.
Qed.

Definition dinf5 (a b : X5) : Q :=
  max5 (dQ (to_fun5 a 0) (to_fun5 b 0)) (dQ (to_fun5 a 1) (to_fun5 b 1))
       (dQ (to_fun5 a 2) (to_fun5 b 2)) (dQ (to_fun5 a 3) (to_fun5 b 3))
       (dQ (to_fun5 a 4) (to_fun5 b 4)).

Lemma dinf5_triangle : forall a b c : X5, dinf5 a c <= dinf5 a b + dinf5 b c.
Proof.
  intros a b c. unfold dinf5.
  destruct (max5_ub (dQ (to_fun5 a 0) (to_fun5 b 0)) (dQ (to_fun5 a 1) (to_fun5 b 1))
                    (dQ (to_fun5 a 2) (to_fun5 b 2)) (dQ (to_fun5 a 3) (to_fun5 b 3))
                    (dQ (to_fun5 a 4) (to_fun5 b 4))) as [A0 [A1 [A2 [A3 A4]]]].
  destruct (max5_ub (dQ (to_fun5 b 0) (to_fun5 c 0)) (dQ (to_fun5 b 1) (to_fun5 c 1))
                    (dQ (to_fun5 b 2) (to_fun5 c 2)) (dQ (to_fun5 b 3) (to_fun5 c 3))
                    (dQ (to_fun5 b 4) (to_fun5 c 4))) as [B0 [B1 [B2 [B3 B4]]]].
  apply max5_lub.
  - pose proof (dQ_triangle (to_fun5 a 0) (to_fun5 b 0) (to_fun5 c 0)). lra.
  - pose proof (dQ_triangle (to_fun5 a 1) (to_fun5 b 1) (to_fun5 c 1)). lra.
  - pose proof (dQ_triangle (to_fun5 a 2) (to_fun5 b 2) (to_fun5 c 2)). lra.
  - pose proof (dQ_triangle (to_fun5 a 3) (to_fun5 b 3) (to_fun5 c 3)). lra.
  - pose proof (dQ_triangle (to_fun5 a 4) (to_fun5 b 4) (to_fun5 c 4)). lra.
Qed.

Lemma dinf5_sym : forall a b : X5, dinf5 a b == dinf5 b a.
Proof.
  intros a b.
  assert (Hle : forall u v : X5, dinf5 u v <= dinf5 v u).
  { intros u v. unfold dinf5.
    destruct (max5_ub (dQ (to_fun5 v 0) (to_fun5 u 0)) (dQ (to_fun5 v 1) (to_fun5 u 1))
                      (dQ (to_fun5 v 2) (to_fun5 u 2)) (dQ (to_fun5 v 3) (to_fun5 u 3))
                      (dQ (to_fun5 v 4) (to_fun5 u 4))) as [A0 [A1 [A2 [A3 A4]]]].
    apply max5_lub.
    - pose proof (dQ_sym (to_fun5 u 0) (to_fun5 v 0)). lra.
    - pose proof (dQ_sym (to_fun5 u 1) (to_fun5 v 1)). lra.
    - pose proof (dQ_sym (to_fun5 u 2) (to_fun5 v 2)). lra.
    - pose proof (dQ_sym (to_fun5 u 3) (to_fun5 v 3)). lra.
    - pose proof (dQ_sym (to_fun5 u 4) (to_fun5 v 4)). lra. }
  apply Qle_antisym; apply Hle.
Qed.

(** S3 clause 1 and the S5 ACCEPT theorem are TYPED at the state layer of the small grid:
    the triangle inequality of d_inf is discharged, nothing else is claimed. *)
Theorem small_grid_triangle_composition : forall (x xhat : X5) (rho_K beta_K : Q),
  dinf5 x (Lam35 (q53 x)) <= beta_K ->
  dinf5 (Lam35 (q53 x)) xhat <= rho_K ->
  dinf5 x xhat <= rho_K + beta_K.
Proof.
  intros x xhat rho_K beta_K Hb Hr.
  exact (triangle_composition X5 dinf5 dinf5_triangle x xhat (Lam35 (q53 x)) rho_K beta_K Hb Hr).
Qed.

Theorem small_grid_accept_certified :
  forall (x : X5) (xK1 : X5) (delta_K eps r_K : Q),
    0 <= r_K ->
    dinf5 x (Lam35 (q53 x)) <= r_K ->
    dinf5 (Lam35 (q53 x)) (Lam35 (q53 xK1)) <= delta_K ->
    delta_K <= eps -> r_K * r_K <= (eps - delta_K) * (eps - delta_K) ->
    dinf5 x (Lam35 (q53 xK1)) <= eps.
Proof.
  intros x xK1 delta_K eps r_K Hr Hrad Hdef Hle Hsq.
  exact (accept_certified X5 dinf5 dinf5_triangle R3 X5 q53 Lam35 q53 x xK1
           delta_K eps r_K Hr Hrad Hdef Hle Hsq).
Qed.

(* ---- S4 WITHIN RADIUS on the small grid: P_odd is 1-Lipschitz for d_inf ---- *)
Lemma P_odd_lipschitz : forall a b : X5, dQ (P_odd a) (P_odd b) <= 1 * dinf5 a b.
Proof.
  intros a b. unfold P_odd, dinf5.
  destruct (max5_ub (dQ (to_fun5 a 0) (to_fun5 b 0)) (dQ (to_fun5 a 1) (to_fun5 b 1))
                    (dQ (to_fun5 a 2) (to_fun5 b 2)) (dQ (to_fun5 a 3) (to_fun5 b 3))
                    (dQ (to_fun5 a 4) (to_fun5 b 4))) as [_ [A1 _]].
  lra.
Qed.

Theorem S4_within_radius_P_odd : forall (x : X5) (r_K : Q),
  dinf5 x (Lam35 (q53 x)) <= r_K ->
  dQ (P_odd x) (P_odd (Lam35 (q53 x))) <= 1 * r_K.
Proof.
  intros x r_K Hr.
  assert (H01 : 0 <= 1) by lra.
  exact (roundtrip_radius_record X5 dinf5 R3 q53 Lam35 Q dQ P_odd 1 H01 P_odd_lipschitz x r_K Hr).
Qed.

(** on the NEVER pair: the exact distance d_inf (x', P_K x') is 1, and the non-shared reader
    moves by exactly 1 = L_P * r_K: the within-radius bound is attained *)
Example S4_within_radius_attained :
  dinf5 x_nv' (Lam35 (q53 x_nv')) == 1 /\
  dQ (P_odd x_nv') (P_odd (Lam35 (q53 x_nv'))) == 1.
Proof. split; qdec. Qed.

(* ===================================================================== *)
(*  In-file readout: Print Assumptions for every theorem-like statement   *)
(*  (and the two computing definitions cert_dec, leaf_gate).  Expected for *)
(*  each line: "Closed under the global context".                          *)
(* ===================================================================== *)
Print Assumptions plateau_radius_window.
Print Assumptions heldout_miss_refutes_persistence.
Print Assumptions beta_S1_nonneg.
Print Assumptions window_ok_sound.
Print Assumptions licence_ok_sound.
Print Assumptions cert_dec.
Print Assumptions cert_dec_complete.
Print Assumptions cert_dec_hold_sound.
Print Assumptions hold_downward.
Print Assumptions leaf_gate.
Print Assumptions leaf_gate_licensed.
Print Assumptions leaf_accept_certified.
Print Assumptions leaf_accept_premises.
Print Assumptions leaf_gate_threshold.
Print Assumptions leaf_hold_sound.
Print Assumptions no_licence_if_gap_grows.
Print Assumptions leaf_gate_holds_if_gap_grows.
Print Assumptions heat_step_interior.
Print Assumptions TC_near.khat3_lt_1.
Print Assumptions TC_near.khat3_attained.
Print Assumptions TC_near.C3_window_0_1.
Print Assumptions TC_near.C3_bound_0_1.
Print Assumptions TC_near.C3_beta_value.
Print Assumptions TC_near.C3_heldout_g3_MISS.
Print Assumptions TC_near.C3_persistence_refuted_g3.
Print Assumptions TC_near.C3_heldout_g4_MISS.
Print Assumptions TC_near.C3_persistence_refuted_g4.
Print Assumptions TC_near.khat4_lt_1.
Print Assumptions TC_near.khat4_attained.
Print Assumptions TC_near.C4_window_0_2.
Print Assumptions TC_near.C4_bound_0_2.
Print Assumptions TC_near.C4_beta_value.
Print Assumptions TC_near.C4_heldout_g4_inside.
Print Assumptions TC_near.khat5_lt_1.
Print Assumptions TC_near.khat5_attained.
Print Assumptions TC_near.window_0_3.
Print Assumptions TC_near.S1_bound_0_3.
Print Assumptions TC_near.S1_radius_0_3.
Print Assumptions TC_near.licence_K0.
Print Assumptions TC_near.window_0_4.
Print Assumptions TC_near.radius_K0.
Print Assumptions TC_near.r_K0_value.
Print Assumptions TC_near.r_K0_nonneg.
Print Assumptions TC_near.delta_K0_value.
Print Assumptions TC_near.eps_star_K0_value.
Print Assumptions TC_near.licence_K1.
Print Assumptions TC_near.window_1_4.
Print Assumptions TC_near.radius_K1.
Print Assumptions TC_near.r_K1_value.
Print Assumptions TC_near.r_K1_nonneg.
Print Assumptions TC_near.delta_K1_value.
Print Assumptions TC_near.eps_star_K1_value.
Print Assumptions TC_near.licence_K2.
Print Assumptions TC_near.window_2_4.
Print Assumptions TC_near.radius_K2.
Print Assumptions TC_near.r_K2_value.
Print Assumptions TC_near.r_K2_nonneg.
Print Assumptions TC_near.delta_K2_value.
Print Assumptions TC_near.eps_star_K2_value.
Print Assumptions TC_near.gate_K0_rel_j4_ACCEPT.
Print Assumptions TC_near.heldout_K0_rel_j4.
Print Assumptions TC_near.gate_K0_rel_j6_HOLD.
Print Assumptions TC_near.too_tight_K0_rel_below_j6.
Print Assumptions TC_near.hold_is_not_false_K0_rel_j6.
Print Assumptions TC_near.gate_K1_rel_j6_ACCEPT.
Print Assumptions TC_near.heldout_K1_rel_j6.
Print Assumptions TC_near.gate_K1_rel_j8_HOLD.
Print Assumptions TC_near.too_tight_K1_rel_below_j8.
Print Assumptions TC_near.hold_is_not_false_K1_rel_j8.
Print Assumptions TC_near.gate_K2_rel_j8_ACCEPT.
Print Assumptions TC_near.heldout_K2_rel_j8.
Print Assumptions TC_near.gate_K2_rel_j10_HOLD.
Print Assumptions TC_near.too_tight_K2_rel_below_j10.
Print Assumptions TC_near.hold_is_not_false_K2_rel_j10.
Print Assumptions TC_near.gate_K0_abs_j6_ACCEPT.
Print Assumptions TC_near.heldout_K0_abs_j6.
Print Assumptions TC_near.gate_K0_abs_j8_HOLD.
Print Assumptions TC_near.too_tight_K0_abs_below_j8.
Print Assumptions TC_near.gate_K1_abs_j8_ACCEPT.
Print Assumptions TC_near.heldout_K1_abs_j8.
Print Assumptions TC_near.gate_K1_abs_j10_HOLD.
Print Assumptions TC_near.too_tight_K1_abs_below_j10.
Print Assumptions TC_near.gate_K2_abs_j10_ACCEPT.
Print Assumptions TC_near.heldout_K2_abs_j10.
Print Assumptions TC_near.gate_K2_abs_j12_HOLD.
Print Assumptions TC_near.too_tight_K2_abs_below_j12.
Print Assumptions TC_near.nidx_n10.
Print Assumptions TC_near.nidx_n1000.
Print Assumptions TC_near.nidx_n100000.
Print Assumptions TC_near.seam_tie_level0.
Print Assumptions TD_near.C3_gap_grows_k0.
Print Assumptions TD_near.C3_no_licence.
Print Assumptions TD_near.C4_gap_grows_k0.
Print Assumptions TD_near.C4_no_licence.
Print Assumptions TD_near.gap_grows_k1.
Print Assumptions TD_near.gap_grows_k2.
Print Assumptions TD_near.C5_HOLD_everywhere.
Print Assumptions TD_near.seam_tie_level0.
Print Assumptions TA_mid.khat3_lt_1.
Print Assumptions TA_mid.khat3_attained.
Print Assumptions TA_mid.C3_window_0_1.
Print Assumptions TA_mid.C3_bound_0_1.
Print Assumptions TA_mid.C3_beta_value.
Print Assumptions TA_mid.C3_heldout_g3_inside.
Print Assumptions TA_mid.C3_heldout_g4_inside.
Print Assumptions TA_mid.khat4_lt_1.
Print Assumptions TA_mid.khat4_attained.
Print Assumptions TA_mid.C4_window_0_2.
Print Assumptions TA_mid.C4_bound_0_2.
Print Assumptions TA_mid.C4_beta_value.
Print Assumptions TA_mid.C4_heldout_g4_inside.
Print Assumptions TA_mid.khat5_lt_1.
Print Assumptions TA_mid.khat5_attained.
Print Assumptions TA_mid.window_0_3.
Print Assumptions TA_mid.S1_bound_0_3.
Print Assumptions TA_mid.S1_radius_0_3.
Print Assumptions TA_mid.licence_K0.
Print Assumptions TA_mid.window_0_4.
Print Assumptions TA_mid.radius_K0.
Print Assumptions TA_mid.r_K0_value.
Print Assumptions TA_mid.r_K0_nonneg.
Print Assumptions TA_mid.delta_K0_value.
Print Assumptions TA_mid.eps_star_K0_value.
Print Assumptions TA_mid.licence_K1.
Print Assumptions TA_mid.window_1_4.
Print Assumptions TA_mid.radius_K1.
Print Assumptions TA_mid.r_K1_value.
Print Assumptions TA_mid.r_K1_nonneg.
Print Assumptions TA_mid.delta_K1_value.
Print Assumptions TA_mid.eps_star_K1_value.
Print Assumptions TA_mid.licence_K2.
Print Assumptions TA_mid.window_2_4.
Print Assumptions TA_mid.radius_K2.
Print Assumptions TA_mid.r_K2_value.
Print Assumptions TA_mid.r_K2_nonneg.
Print Assumptions TA_mid.delta_K2_value.
Print Assumptions TA_mid.eps_star_K2_value.
Print Assumptions TA_mid.gate_K0_rel_j8_ACCEPT.
Print Assumptions TA_mid.heldout_K0_rel_j8.
Print Assumptions TA_mid.gate_K0_rel_j10_HOLD.
Print Assumptions TA_mid.too_tight_K0_rel_below_j10.
Print Assumptions TA_mid.hold_is_not_false_K0_rel_j10.
Print Assumptions TA_mid.gate_K1_rel_j10_ACCEPT.
Print Assumptions TA_mid.heldout_K1_rel_j10.
Print Assumptions TA_mid.gate_K1_rel_j12_HOLD.
Print Assumptions TA_mid.too_tight_K1_rel_below_j12.
Print Assumptions TA_mid.hold_is_not_false_K1_rel_j12.
Print Assumptions TA_mid.gate_K2_rel_j12_ACCEPT.
Print Assumptions TA_mid.heldout_K2_rel_j12.
Print Assumptions TA_mid.gate_K2_rel_j14_HOLD.
Print Assumptions TA_mid.too_tight_K2_rel_below_j14.
Print Assumptions TA_mid.hold_is_not_false_K2_rel_j14.
Print Assumptions TA_mid.gate_K0_abs_j8_ACCEPT.
Print Assumptions TA_mid.heldout_K0_abs_j8.
Print Assumptions TA_mid.gate_K0_abs_j10_HOLD.
Print Assumptions TA_mid.too_tight_K0_abs_below_j10.
Print Assumptions TA_mid.gate_K1_abs_j10_ACCEPT.
Print Assumptions TA_mid.heldout_K1_abs_j10.
Print Assumptions TA_mid.gate_K1_abs_j12_HOLD.
Print Assumptions TA_mid.too_tight_K1_abs_below_j12.
Print Assumptions TA_mid.gate_K2_abs_j12_ACCEPT.
Print Assumptions TA_mid.heldout_K2_abs_j12.
Print Assumptions TA_mid.gate_K2_abs_j14_HOLD.
Print Assumptions TA_mid.too_tight_K2_abs_below_j14.
Print Assumptions TA_mid.nidx_n10.
Print Assumptions TA_mid.nidx_n1000.
Print Assumptions TA_mid.nidx_n100000.
Print Assumptions TA_mid.seam_tie_level0.
Print Assumptions TB_mid.khat3_lt_1.
Print Assumptions TB_mid.khat3_attained.
Print Assumptions TB_mid.C3_window_0_1.
Print Assumptions TB_mid.C3_bound_0_1.
Print Assumptions TB_mid.C3_beta_value.
Print Assumptions TB_mid.C3_heldout_g3_MISS.
Print Assumptions TB_mid.C3_persistence_refuted_g3.
Print Assumptions TB_mid.C3_heldout_g4_MISS.
Print Assumptions TB_mid.C3_persistence_refuted_g4.
Print Assumptions TB_mid.C4_gap_grows_k1.
Print Assumptions TB_mid.C4_no_licence.
Print Assumptions TB_mid.gap_grows_k2.
Print Assumptions TB_mid.C5_HOLD_everywhere.
Print Assumptions TB_mid.seam_tie_level0.
Print Assumptions TC_ssq.C3_gap_grows_k0.
Print Assumptions TC_ssq.C3_no_licence.
Print Assumptions TC_ssq.C4_gap_grows_k0.
Print Assumptions TC_ssq.C4_no_licence.
Print Assumptions TC_ssq.gap_grows_k1.
Print Assumptions TC_ssq.gap_grows_k2.
Print Assumptions TC_ssq.C5_HOLD_everywhere.
Print Assumptions TC_ssq.seam_tie_level0.
Print Assumptions TR_near.khat3_lt_1.
Print Assumptions TR_near.khat3_attained.
Print Assumptions TR_near.C3_window_0_1.
Print Assumptions TR_near.C3_bound_0_1.
Print Assumptions TR_near.C3_beta_value.
Print Assumptions TR_near.C3_heldout_g3_inside.
Print Assumptions TR_near.C3_heldout_g4_MISS.
Print Assumptions TR_near.C3_persistence_refuted_g4.
Print Assumptions TR_near.khat4_lt_1.
Print Assumptions TR_near.khat4_attained.
Print Assumptions TR_near.C4_window_0_2.
Print Assumptions TR_near.C4_bound_0_2.
Print Assumptions TR_near.C4_beta_value.
Print Assumptions TR_near.C4_heldout_g4_inside.
Print Assumptions TR_near.khat5_lt_1.
Print Assumptions TR_near.khat5_attained.
Print Assumptions TR_near.window_0_3.
Print Assumptions TR_near.S1_bound_0_3.
Print Assumptions TR_near.S1_radius_0_3.
Print Assumptions TR_near.licence_K0.
Print Assumptions TR_near.window_0_4.
Print Assumptions TR_near.radius_K0.
Print Assumptions TR_near.r_K0_value.
Print Assumptions TR_near.r_K0_nonneg.
Print Assumptions TR_near.delta_K0_value.
Print Assumptions TR_near.eps_star_K0_value.
Print Assumptions TR_near.licence_K1.
Print Assumptions TR_near.window_1_4.
Print Assumptions TR_near.radius_K1.
Print Assumptions TR_near.r_K1_value.
Print Assumptions TR_near.r_K1_nonneg.
Print Assumptions TR_near.delta_K1_value.
Print Assumptions TR_near.eps_star_K1_value.
Print Assumptions TR_near.licence_K2.
Print Assumptions TR_near.window_2_4.
Print Assumptions TR_near.radius_K2.
Print Assumptions TR_near.r_K2_value.
Print Assumptions TR_near.r_K2_nonneg.
Print Assumptions TR_near.delta_K2_value.
Print Assumptions TR_near.eps_star_K2_value.
Print Assumptions TR_near.gate_K0_rel_j2_ACCEPT.
Print Assumptions TR_near.heldout_K0_rel_j2.
Print Assumptions TR_near.gate_K0_rel_j4_HOLD.
Print Assumptions TR_near.too_tight_K0_rel_below_j4.
Print Assumptions TR_near.gate_K1_rel_j2_ACCEPT.
Print Assumptions TR_near.heldout_K1_rel_j2.
Print Assumptions TR_near.gate_K1_rel_j4_HOLD.
Print Assumptions TR_near.too_tight_K1_rel_below_j4.
Print Assumptions TR_near.gate_K2_rel_j4_ACCEPT.
Print Assumptions TR_near.heldout_K2_rel_j4.
Print Assumptions TR_near.gate_K2_rel_j6_HOLD.
Print Assumptions TR_near.too_tight_K2_rel_below_j6.
Print Assumptions TR_near.gate_K0_abs_j2_ACCEPT.
Print Assumptions TR_near.heldout_K0_abs_j2.
Print Assumptions TR_near.gate_K0_abs_j4_HOLD.
Print Assumptions TR_near.too_tight_K0_abs_below_j4.
Print Assumptions TR_near.gate_K1_abs_j4_ACCEPT.
Print Assumptions TR_near.heldout_K1_abs_j4.
Print Assumptions TR_near.gate_K1_abs_j6_HOLD.
Print Assumptions TR_near.too_tight_K1_abs_below_j6.
Print Assumptions TR_near.gate_K2_abs_j6_ACCEPT.
Print Assumptions TR_near.heldout_K2_abs_j6.
Print Assumptions TR_near.gate_K2_abs_j8_HOLD.
Print Assumptions TR_near.too_tight_K2_abs_below_j8.
Print Assumptions TR_near.nidx_n10.
Print Assumptions TR_near.nidx_n1000.
Print Assumptions TR_near.nidx_n100000.
Print Assumptions TR_near.seam_tie_level0.
Print Assumptions TR_state.khat3_lt_1.
Print Assumptions TR_state.khat3_attained.
Print Assumptions TR_state.C3_window_0_1.
Print Assumptions TR_state.C3_bound_0_1.
Print Assumptions TR_state.C3_beta_value.
Print Assumptions TR_state.C3_heldout_g3_inside.
Print Assumptions TR_state.C3_heldout_g4_inside.
Print Assumptions TR_state.khat4_lt_1.
Print Assumptions TR_state.khat4_attained.
Print Assumptions TR_state.C4_window_0_2.
Print Assumptions TR_state.C4_bound_0_2.
Print Assumptions TR_state.C4_beta_value.
Print Assumptions TR_state.C4_heldout_g4_inside.
Print Assumptions TR_state.khat5_lt_1.
Print Assumptions TR_state.khat5_attained.
Print Assumptions TR_state.window_0_3.
Print Assumptions TR_state.S1_bound_0_3.
Print Assumptions TR_state.S1_radius_0_3.
Print Assumptions TR_state.licence_K0.
Print Assumptions TR_state.window_0_4.
Print Assumptions TR_state.radius_K0.
Print Assumptions TR_state.r_K0_value.
Print Assumptions TR_state.r_K0_nonneg.
Print Assumptions TR_state.delta_K0_value.
Print Assumptions TR_state.eps_star_K0_value.
Print Assumptions TR_state.licence_K1.
Print Assumptions TR_state.window_1_4.
Print Assumptions TR_state.radius_K1.
Print Assumptions TR_state.r_K1_value.
Print Assumptions TR_state.r_K1_nonneg.
Print Assumptions TR_state.delta_K1_value.
Print Assumptions TR_state.eps_star_K1_value.
Print Assumptions TR_state.licence_K2.
Print Assumptions TR_state.window_2_4.
Print Assumptions TR_state.radius_K2.
Print Assumptions TR_state.r_K2_value.
Print Assumptions TR_state.r_K2_nonneg.
Print Assumptions TR_state.delta_K2_value.
Print Assumptions TR_state.eps_star_K2_value.
Print Assumptions TR_state.gate_K0_rel_j2_HOLD.
Print Assumptions TR_state.too_tight_K0_rel_below_j2.
Print Assumptions TR_state.gate_K1_rel_j2_HOLD.
Print Assumptions TR_state.too_tight_K1_rel_below_j2.
Print Assumptions TR_state.gate_K2_rel_j2_HOLD.
Print Assumptions TR_state.too_tight_K2_rel_below_j2.
Print Assumptions TR_state.gate_K0_abs_j2_HOLD.
Print Assumptions TR_state.too_tight_K0_abs_below_j2.
Print Assumptions TR_state.gate_K1_abs_j2_HOLD.
Print Assumptions TR_state.too_tight_K1_abs_below_j2.
Print Assumptions TR_state.gate_K2_abs_j2_HOLD.
Print Assumptions TR_state.too_tight_K2_abs_below_j2.
Print Assumptions TR_state.nidx_n10.
Print Assumptions TR_state.nidx_n1000.
Print Assumptions TR_state.nidx_n100000.
Print Assumptions trap_same_C3_ratio.
Print Assumptions matched_pair_near.
Print Assumptions S2_section_law.
Print Assumptions S2_section_law_coarse.
Print Assumptions S2_restriction_coherence.
Print Assumptions S2_PK_idempotent.
Print Assumptions S2_PK_fixes_image.
Print Assumptions S2_section_example_values.
Print Assumptions S2_section_example.
Print Assumptions small_grid_seam.
Print Assumptions S4_P_sh_in_alg.
Print Assumptions S4_P_sh0_in_alg.
Print Assumptions S4_exact_P_sh.
Print Assumptions S4_exact_P_sh0.
Print Assumptions S4_exact_iff_P_sh.
Print Assumptions never_same_record.
Print Assumptions never_distinct.
Print Assumptions never_rationally_distinct.
Print Assumptions S4_never.
Print Assumptions S4_never_total.
Print Assumptions S4_PK_merges.
Print Assumptions P_odd_separates.
Print Assumptions S4_P_odd_not_in_alg.
Print Assumptions S4_exact_fails_outside_alg.
Print Assumptions S4_exact_fails_Qeq.
Print Assumptions max5_ub.
Print Assumptions max5_lub.
Print Assumptions dinf5_triangle.
Print Assumptions dinf5_sym.
Print Assumptions small_grid_triangle_composition.
Print Assumptions small_grid_accept_certified.
Print Assumptions P_odd_lipschitz.
Print Assumptions S4_within_radius_P_odd.
Print Assumptions S4_within_radius_attained.
