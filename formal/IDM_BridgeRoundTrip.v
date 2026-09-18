(*
  IDM_BridgeRoundTrip.v -- S4 ROUND TRIP of the Discrete-Continuum Readout Bridge:
  the assembly file.  Three verdicts (EXACT / WITHIN RADIUS / NEVER), the level-2
  closure on the number ladder, and the +R-Open fence as header text only.

  Nothing here is proved twice: every verdict is an OCCURRENCE of a theorem that
  already compiles in IDM_SignatureFunctor.v (S2), IDM_ReadoutTower.v (S1), the Toledo
  proposal file PROP_BRIDGE_03_certified_radius.v (S3 / S5) or the Toledo canonical
  witness weld__M_60_v1.v (root R), applied at the 11b-1 typing split
  q_K : X -> R_K,  Lambda_K : R_K -> Y,  P_K := Lambda_K o q_K.

  Bridge lines covered (DISCRETE_CONTINUUM_BRIDGE_DESIGN_v0.1.md, section 2 / S4, the
  S4-corollary, and the S1-lemma's readout real, under the 11b rulings 1, 3, 5, 6, 8):

    S4  P o Lambda_K o q_K = P   <=>   P in Alg_Q                                  [EXACT]
          -> roundtrip_exact (occurrence of IDM_SignatureFunctor.roundtrip_exact_iff,
             itself the CAN-165 Factorization clause with Lambda_K as section witness);
             roundtrip_exact_fails_outside_alg is its Fail-Able-Gate control.
        Pi_k (sigma_of g) = g (N(k))  exactly                                       [EXACT, tape]
          -> roundtrip_exact_tape (occurrence of IDM_ReadoutTower.sigma_readout_exact);
             roundtrip_exact_tape_Nidx unfolds N(k) to the bounded search Nidx.
        P L_P-Lipschitz on (Y, d_Y)  ==>  d_V(P x, P x^_K) <= L_P * r_K             [WITHIN RADIUS]
          -> roundtrip_radius_record  (rho_K = 0, x^_K := Lambda_K (q_K x): the standing
             rule of ruling 11b-3; occurrence of PROP-EPSC-08 epsc08_lipschitz_tail_lift)
          -> roundtrip_radius         (x^_K within rho_K of Lambda_K (q_K x), r_K = rho_K
             + beta_K under a declared triangle inequality; occurrence of
             PROP_BRIDGE_03.bridge_radius, itself an occurrence of PROP-EPSC-08)
          -> roundtrip_radius_S1      (the whole S1 -> S3 -> S4 chain in (Q, dQ): beta_K
             := |Delta g N| / (1 - rho) from the contracting tape; occurrence of
             PROP_BRIDGE_03.contracting_radius o PROP-EPSC-08)
        q_K x = q_K x' ,  x <> x'  ==>  no total decoder D with D (q_K x) = x /\ D (q_K x') = x'
                                                                                    [NEVER]
          -> roundtrip_never, roundtrip_never_total (instances of
             no_decoder_recovers_state / true_state_exists_but_no_total_decoder,
             readout_genesis/formal/InfoTrueRecordUnreadable_attempt.v L62-114, Type-
             polymorphic, no imports; to be registered as PROP-BRIDGE-09 -- that repo has
             no -Q mapping into this arc, so the three-line proof is instantiated locally
             and the parent is cited here, never claimed as new);
             never_seen_in_alg records what Alg_Q readers make of the collapsed pair.
        level 2:  R_complete X Hreg = L ,  |X_i(k) - L(k)| <= 1/i + 4/k
                  only under the EXHIBITED modulus Hreg,
                  and definitionally  rseq L k = rseq (X (2k)) (6k)
          -> level2_bound (the exported bound, proj2_sig of weld/M.60.v1 R_complete)
          -> level2_diagonal (by reflexivity: R_complete ends with `Defined.`,
             weld__M_60_v1.v L663, READ 2026-09-18; its body is
             `let Lseq := fun n => rseq (X (2*n)) (6*n) in ...` as printed by
             `Print URCF17RComplete.R_complete` in front of the author)
          -> to_RR / of_RR: the renaming RR' == RR (IDM_ReadoutTower L397 vs weld__M_60_v1.v
             L66) written as a transport, both directions, round-tripping on the nose
          -> level2_tower, level2_tape: the S1-lemma readout reals as the approximants
             of R_complete (the tower of tapes reads its limit off the diagonal, with the
             diagonal identities level2_tower_diagonal / level2_tape_diagonal by reflexivity)

  +R-OPEN FENCE (header text only; NO theorem below states or uses it):
    the unrestricted classical statement "every Cauchy sequence has a modulus", the
    least-upper-bound principle, trichotomy / total <= on the reals, and completeness of
    any infinite-dimensional space are +R-Open BY DESIGN: never used, never called
    axiom-free, never a premise of any theorem in this file.  Every limit below is read
    off an EXHIBITED modulus (Hreg, rreg', the S1 contracting premise).  I1 named here and
    refused as a premise; I2 refused (no h -> 0 anywhere); I4 refused (1/i, 4/k are
    finite rationals; Nmax is explicit); Z1 refused (no point-object continuum value);
    Z4 refused (HOLD is a typed verdict, never the number 0).
    Falsifier of the fence (Clay-open-status-honesty ruling 2026-09-13): a genuinely
    axiom-free Q proof of tower-limit EXISTENCE without an exhibited modulus -- i.e. a
    term of type  forall X : positive -> RR, (forall i j k, |X_i(k) - X_j(k)| <= f i j k
    for SOME f not given as data) -> { L | ... }  whose scratch `Print Assumptions`
    prints "Closed under the global context".  If such a term ever appears it must be
    reported and the fence re-tiered, not suppressed.  Until then the fence stays
    +R-Open permanently: closing it would form the completed continuum as a primitive.

  Ruling 11b-5 (NO bundle row): the three-verdict law is NOT one Toledo line.  Each
  verdict is a relation / occurrence on its parent -- EXACT on EQ-002/M.01.v1 (CAN-165)
  via weld/M.64.v1 (CAN-1300); WITHIN RADIUS on PROP-EPSC-08; NEVER on PROP-BRIDGE-09
  (no_decoder_recovers_state); level 2 on weld/M.60.v1 (CAN-1296).  The "one law"
  sentence lives in the design doc at tier Dr.  Ruling 11b-6: no lineage_survives.

  Toledo parents by code (registry/CANONICAL.json + registry/proposals/*.json, worktree
  proposals/readout-bridge @ b712d0a9; statements re-read in the .v files 2026-09-18):
    EQ-002/M.01.v1  CAN-165   Factorization (ker R <= ker Phi iff Phi = g-bar o R)
                              -> roundtrip_exact is this clause at R := q_K, g-bar := P o Lambda_K
    weld/M.64.v1    CAN-1300  T5 kernel inclusion         -> Alg_Q membership (via IDM_SignatureFunctor)
    weld/M.68.v1    CAN-1305  stable_depth_exact_future   -> S2 admissibility (via IDM_SignatureFunctor)
    weld/M.63.v1    CAN-1299  T3 congruence               -> S2 admissibility (via IDM_SignatureFunctor)
    weld/M.02.v1    CAN-006   domain weld (q o F = F# o q) -> forward map (via IDM_SignatureFunctor)
    weld/M.03.v1    CAN-007   reader equivalence          -> the class [z]_Q (via IDM_SignatureFunctor)
    weld/M.60.v1    CAN-1296  URCF17RComplete.RR / rseq / rreg / Req / R_complete / inj_Q /
                              Rconv / Rlimit_unique      -> level2_bound, level2_diagonal, to_RR
                              (Rlimit_unique cited for uniqueness of the level-2 limit up to
                              Req; not applied here because R_complete exports a pointwise
                              bound, not Rconv -- an Open ledger item, see the stage result)
    R/M.32.v1       IDM-0057  refine_stable               -> S1 licence (via IDM_ReadoutTower)
    Z/M.08.v1       IDM-0035  PSum_delta_telescope        -> S1 ledger (via IDM_ReadoutTower)
    R/M.36.v1       IDM-0061  const_gap_zero              -> constant readout (cited)
    EQ-001/C.16.v1            structure != lineage sidecar (cited; no lineage theorem, 11b-6)
    root A.8 (genesis_root.json, tier Definition)  Lambda_alpha o Sigma_alpha = I_S
  Proposal-lane parents (NOT yet in Toledo):
    PROP-EPSC-08    PROP_EPSC_08_lipschitz_tail_lift.v   epsc08_lipschitz_tail_lift
                    (registry Th_coqc / verified_by_coq; compiled in this arc; Required here)
    PROP-BRIDGE-03  PROP_BRIDGE_03_certified_radius.v    bridge_radius, contracting_radius,
                    beta_S1, dQ (31 objects Closed; Required here)
    PROP-BRIDGE-09  no_decoder_recovers_state (readout_genesis, in-file Print Assumptions
                    Closed per that file's own header; NOT re-read as a transcript in this
                    stage -- the local instance below carries its own Print Assumptions)
    PROP-EPSC-03 / PROP-EPSC-17 / PROP-EPSC-23 / PROP-EPSC-39  cited through PROP-BRIDGE-03 only.

  Every identifier defined or proved in THIS file is NEW DERIVATION / PROPOSAL --
  not yet in Toledo -- namely: roundtrip_exact, roundtrip_exact_fails_outside_alg,
  roundtrip_exact_tape, roundtrip_exact_tape_Nidx, roundtrip_radius_record,
  roundtrip_radius, roundtrip_radius_S1, roundtrip_never, roundtrip_never_total,
  never_seen_in_alg, level2_bound, level2_diagonal, to_RR, of_RR, to_RR_at, of_RR_at,
  of_to_RR, to_of_RR, to_RR_Req, level2_tower, level2_tower_diagonal, level2_tape,
  level2_tape_diagonal.  Each is expected to be registered as an OCCURRENCE of the parent
  named at its definition, never as a row of its own (ruling 11b-5).  Toledo lookup
  (equivalence criterion: renaming / positive scale / constant substitution) found no
  canonical or proposal row stating a round trip (design S4 "Tier now", re-checked by
  statement 2026-09-18 for the terms decoder / round trip / diagonal / R_complete).

  Genesis sections instantiated (READOUT_GENESIS_CORE.md): A.7 (no early collapse:
  never_seen_in_alg), A.8 (Lambda o Sigma = I on Alg_Q: roundtrip_exact), A.11
  (coarsening back only under a fresh certificate: the pair (rho_K, beta_K) of
  roundtrip_radius), A.12 (a bridge carries a STATED non-zero recovery error),
  A.13 Gate 2 / Gate 5, Face 10 record law (the record is never the state:
  roundtrip_never), B.3 level L4 only (dynamically commuting quotient for x plus EXACT on
  Alg_Q; no L5 -- cross-domain levels only), X.2 ("the Coq floor closes STRUCTURE"),
  XI.1 label rule (every Th_coqc statement about RR / RR' is about Bishop-readout reals,
  never about Coq.Reals), XI.2 (no R hiding behind the odometer: level2_diagonal shows
  the limit IS a readout of the approximants).

  Reuse discipline: every parent is `Require`d and applied; nothing from IDM_SignatureFunctor,
  IDM_ReadoutTower, PROP_BRIDGE_03, PROP_EPSC_08 or weld__M_60_v1 is re-proved or copied.
  The one locally instantiated proof (roundtrip_never, three lines) is an instance of a
  readout_genesis lemma that this arc cannot `Require`; its parent is cited above.

  weld__M_60_v1.v line 6 is `Require Coq.Logic.Classical` (Require only, never Imported;
  all 43 in-file Print Assumptions of that file printed Closed at the inventory stage).
  This file keeps the same pattern: `From MRC Require weld__M_60_v1` (NOT Import) and a
  module alias `W`, so no classical name ever enters short-name scope and nothing below
  can silently re-tier.  The design may claim "no Coq.Reals"; it may NOT claim "no
  classical Require in the loaded environment" -- the per-theorem Print Assumptions
  readouts are the tier evidence, not the Require list.

  Build mapping used (recorded per ruling 11b-8 -- the LIVE IDM worktree is the source
  of truth; Toledo's coq/information-discrete-math mirror is stale and never used):
    cd <live IDM worktree>/formal &&
    coqc -q -R <live IDM worktree> IDM -Q <toledo worktree>/coq/canonical MRC IDM_BridgeRoundTrip.v
  (logical names: this file = IDM.formal.IDM_BridgeRoundTrip; IDM_* = IDM.formal.IDM_*;
  the Toledo canonical files = MRC.<basename>).  FRICTION, stated plainly: IDM's own
  formal/verify.sh compiles with no -Q/-R and an explicit FILES list; this file is not in
  that list and cannot be until the arc carries the MRC mapping -- it is an assembly
  file across two repositories by the task's design, and it is built only by the command
  above.  Memory floor: one coqc at a time, `free -g` checked (available >= 3 G) before
  it, wrapped as ANSE_HEAVY_MAX=3G anse-heavy "..."; no verify.sh, no background jobs.

  Tier: every object below is Th_coqc only where a scratch `Print Assumptions` printed
  "Closed under the global context" in front of the reader (see the stage result).
  Section Variables / Hypotheses (Hsec, d_triangle, L_P_nonneg, P_lipschitz) and the
  S1 premises (Hrho0, Hrho1, Hcontr) and the modulus Hreg are DISCLOSED here and become
  premises of the exported statements, never axioms.  No unfinished proof, no axiom
  declaration, no Coq.Reals, no classical Import.
*)

Require Import QArith.
Require Import Qabs.
Require Import IDM_Calculus.                                  (* Delta                    *)
Require Import IDM_SignatureFunctor.                          (* PK, InAlg, roundtrip_exact_iff *)
Require Import IDM_ReadoutTower.                              (* RR', rseq', rreg', Req', Pi, sigma_of, N_of, Nidx, accept, Nmax *)
From MRC Require Import PROP_BRIDGE_03_certified_radius.      (* bridge_radius, contracting_radius, beta_S1, dQ *)
From MRC Require Import PROP_EPSC_08_lipschitz_tail_lift.     (* epsc08_lipschitz_tail_lift *)
From MRC Require weld__M_60_v1.                               (* Require only, never Import *)
Module W := weld__M_60_v1.URCF17RComplete.                    (* RR, rseq, rreg, mkRR, Req, R_complete *)

Open Scope Q_scope.

(* ===================================================================== *)
(*  Part A -- EXACT : P o Lambda_K o q_K = P  <=>  P in Alg_Q              *)
(*  occurrence of IDM_SignatureFunctor.roundtrip_exact_iff (CAN-165)      *)
(* ===================================================================== *)

Section Exact.
  Context {X RK V : Type}.
  Variable q_K : X -> RK.                           (* forward map (weld/M.02 + M.03)   *)
  Variable Lambda_K : RK -> X.                      (* section: read the record back    *)
  Hypothesis Hsec : forall k, q_K (Lambda_K k) = k. (* DISCLOSED: Lambda_K is a section *)

  (** S4 EXACT, written at the 11b-1 typing (PK q lam s unfolds to lam (q s)). *)
  Theorem roundtrip_exact : forall P : X -> V,
    (forall x, P (Lambda_K (q_K x)) = P x) <-> InAlg q_K P.
  Proof.
    intro P. exact (roundtrip_exact_iff q_K Lambda_K Hsec P).
  Qed.

  (** Fail-Able-Gate control for EXACT: a reader that separates two states with the
      same record can never round-trip exactly (the contrapositive made concrete). *)
  Theorem roundtrip_exact_fails_outside_alg : forall (P : X -> V) (x x' : X),
    q_K x = q_K x' -> P x <> P x' ->
    ~ (forall y, P (Lambda_K (q_K y)) = P y).
  Proof.
    intros P x x' Heq Hneq Hfix.
    apply Hneq.
    rewrite <- (Hfix x). rewrite <- (Hfix x'). rewrite Heq. reflexivity.
  Qed.
End Exact.

(* ===================================================================== *)
(*  Part B -- EXACT on the tape : Pi_k (sigma_of g) = g (N(k))            *)
(*  occurrence of IDM_ReadoutTower.sigma_readout_exact                    *)
(* ===================================================================== *)

Theorem roundtrip_exact_tape :
  forall (g : nat -> Q) (rho : Q) (Hrho0 : 0 <= rho) (Hrho1 : rho < 1)
         (Hcontr : forall k, Qabs (Delta g (S k)) <= rho * Qabs (Delta g k))
         (k : positive),
    Pi k (sigma_of g rho Hrho0 Hrho1 Hcontr) = g (N_of g rho k).
Proof.
  intros g rho Hrho0 Hrho1 Hcontr k.
  exact (sigma_readout_exact g rho Hrho0 Hrho1 Hcontr k).
Qed.

(** The same identity with N(k) unfolded to the bounded search (definitional). *)
Theorem roundtrip_exact_tape_Nidx :
  forall (g : nat -> Q) (rho : Q) (Hrho0 : 0 <= rho) (Hrho1 : rho < 1)
         (Hcontr : forall k, Qabs (Delta g (S k)) <= rho * Qabs (Delta g k))
         (k : positive),
    Pi k (sigma_of g rho Hrho0 Hrho1 Hcontr)
      = g (Nidx (accept g rho k) (Nmax g rho k)).
Proof.
  intros. reflexivity.
Qed.

(* ===================================================================== *)
(*  Part C -- WITHIN RADIUS : d_V(P x, P x^_K) <= L_P * r_K                *)
(*  occurrences of PROP-EPSC-08 and PROP_BRIDGE_03.bridge_radius          *)
(* ===================================================================== *)

Section WithinRadius.
  Variable Y : Type.
  Variable d_Y : Y -> Y -> Q.
  Variable RK : Type.
  Variable q_K : Y -> RK.
  Variable Lambda_K : RK -> Y.
  Variable V : Type.
  Variable d_V : V -> V -> Q.
  Variable P : Y -> V.                               (* the reader                     *)
  Variable L_P : Q.
  Hypothesis L_P_nonneg : 0 <= L_P.
  Hypothesis P_lipschitz : forall a b : Y, d_V (P a) (P b) <= L_P * d_Y a b.

  (** rho_K = 0 (ruling 11b-3 standing rule, x^_K := Lambda_K (q_K x)): the reader of
      the record read back is within L_P * r_K of the reader of the object.
      Occurrence of PROP-EPSC-08 at u := x, P_K u := Lambda_K (q_K x), beta := r_K. *)
  Theorem roundtrip_radius_record : forall (x : Y) (r_K : Q),
    d_Y x (Lambda_K (q_K x)) <= r_K ->
    d_V (P x) (P (Lambda_K (q_K x))) <= L_P * r_K.
  Proof.
    intros x r_K Hr.
    exact (epsc08_lipschitz_tail_lift Y d_Y V d_V P L_P L_P_nonneg P_lipschitz
             x (Lambda_K (q_K x)) r_K Hr).
  Qed.

  (** General form: a reconstruction x^_K within rho_K of the record read back,
      r_K := rho_K + beta_K under a declared triangle inequality (S3 clause 1).
      Occurrence of PROP_BRIDGE_03.bridge_radius at Px := Lambda_K (q_K x). *)
  Hypothesis d_triangle : forall a b c : Y, d_Y a c <= d_Y a b + d_Y b c.

  Theorem roundtrip_radius : forall (x xhat : Y) (rho_K beta_K : Q),
    d_Y x (Lambda_K (q_K x)) <= beta_K ->
    d_Y (Lambda_K (q_K x)) xhat <= rho_K ->
    d_V (P x) (P xhat) <= L_P * (rho_K + beta_K).
  Proof.
    intros x xhat rho_K beta_K Hbeta Hrho.
    exact (bridge_radius Y d_Y d_triangle x xhat (Lambda_K (q_K x)) rho_K beta_K
             Hbeta Hrho V d_V P L_P L_P_nonneg P_lipschitz).
  Qed.
End WithinRadius.

(** The whole chain S1 -> S3 -> S4 in (Q, dQ): the object is the later tape value
    g (N + M), the record is g N (q_K := evaluation at N, Lambda_K := the identity on Q),
    beta_K := |Delta g N| / (1 - rho) is supplied by the contracting licence, any
    reconstruction xhat within rho_K of the record, and every L_P-Lipschitz reader P
    inherits the radius.  Occurrence of PROP_BRIDGE_03.contracting_radius composed with
    PROP-EPSC-08. *)
Theorem roundtrip_radius_S1 :
  forall (g : nat -> Q) (rho : Q),
    rho < 1 ->
    (forall k, Qabs (Delta g (S k)) <= rho * Qabs (Delta g k)) ->
    forall (V : Type) (d_V : V -> V -> Q) (P : Q -> V) (L_P : Q),
      0 <= L_P ->
      (forall a b : Q, d_V (P a) (P b) <= L_P * dQ a b) ->
      forall (N M : nat) (xhat rho_K : Q),
        dQ (g N) xhat <= rho_K ->
        d_V (P (g (N + M)%nat)) (P xhat) <= L_P * (rho_K + beta_S1 g rho N).
Proof.
  intros g rho Hrho Hcontr V d_V P L_P HL HP N M xhat rho_K Hr.
  apply (epsc08_lipschitz_tail_lift Q dQ V d_V P L_P HL HP).
  exact (contracting_radius g rho Hrho Hcontr N M xhat rho_K Hr).
Qed.

(* ===================================================================== *)
(*  Part D -- NEVER : equal records, distinct states, no decoder          *)
(*  instance of no_decoder_recovers_state (PROP-BRIDGE-09)                *)
(* ===================================================================== *)

(** If q_K identifies two distinct states, no decoder D : R_K -> X recovers both from
    the shared record.  Instance of readout_genesis
    InfoTrueRecordUnreadable_attempt.v no_decoder_recovers_state (O := q_K). *)
Theorem roundtrip_never : forall (X RK : Type) (q_K : X -> RK) (x x' : X),
  q_K x = q_K x' -> x <> x' ->
  ~ (exists D : RK -> X, D (q_K x) = x /\ D (q_K x') = x').
Proof.
  intros X RK q_K x x' Heq Hneq [D [H1 H2]].
  apply Hneq.
  rewrite <- H1. rewrite <- H2. rewrite Heq. reflexivity.
Qed.

(** The "no TOTAL decoder" form: no D correct on every state.  Instance of
    true_state_exists_but_no_total_decoder (its two existence conjuncts are trivial
    and omitted: x and x' are given). *)
Theorem roundtrip_never_total : forall (X RK : Type) (q_K : X -> RK) (x x' : X),
  q_K x = q_K x' -> x <> x' ->
  ~ (exists D : RK -> X, forall y, D (q_K y) = y).
Proof.
  intros X RK q_K x x' Heq Hneq [D HD].
  apply (roundtrip_never X RK q_K x x' Heq Hneq).
  exists D. split; apply HD.
Qed.

(** What the retained algebra makes of the collapsed pair: every P in Alg_Q returns the
    same value on x and x' -- the distinction is bounded (S3) but never seen (A.7).
    This is the definition of InAlg, recorded as the link NEVER -> EXACT. *)
Remark never_seen_in_alg : forall (X RK V : Type) (q_K : X -> RK) (P : X -> V) (x x' : X),
  InAlg q_K P -> q_K x = q_K x' -> P x = P x'.
Proof.
  intros X RK V q_K P x x' HP Heq. exact (HP x x' Heq).
Qed.

(* ===================================================================== *)
(*  Part E -- level 2 : the continuum closes under its own readout        *)
(*  occurrence of weld/M.60.v1 (CAN-1296) R_complete                      *)
(* ===================================================================== *)

(** The exported bound of R_complete: |X_i(k) - L(k)| <= 1/i + 4/k, ONLY under the
    exhibited modulus Hreg (the A8 gate).  proj2_sig, nothing more. *)
Theorem level2_bound :
  forall (X : positive -> W.RR)
         (Hreg : forall i j k, Qabs (W.rseq (X i) k - W.rseq (X j) k)
                               <= (1#i) + (1#j) + (2#1) * (1#k))
         (i k : positive),
    Qabs (W.rseq (X i) k - W.rseq (proj1_sig (W.R_complete X Hreg)) k)
      <= (1#i) + (4#1) * (1#k).
Proof.
  intros X Hreg i k. exact (proj2_sig (W.R_complete X Hreg) i k).
Qed.

(** The limit IS a readout of the approximants: its k-th value is the (2k)-th
    approximant read at resolution 6k.  Definitional, because R_complete is
    transparent (`Defined.`). *)
Theorem level2_diagonal :
  forall (X : positive -> W.RR)
         (Hreg : forall i j k, Qabs (W.rseq (X i) k - W.rseq (X j) k)
                               <= (1#i) + (1#j) + (2#1) * (1#k))
         (k : positive),
    W.rseq (proj1_sig (W.R_complete X Hreg)) k
      = W.rseq (X (2 * k)%positive) (6 * k)%positive.
Proof.
  intros X Hreg k. reflexivity.
Qed.

(* ---- the renaming RR' == RR, written as a transport in both directions ---- *)

Definition to_RR (x : RR') : W.RR := W.mkRR (rseq' x) (rreg' x).
Definition of_RR (x : W.RR) : RR' := mkRR' (W.rseq x) (W.rreg x).

Lemma to_RR_at : forall (x : RR') (k : positive), W.rseq (to_RR x) k = rseq' x k.
Proof. reflexivity. Qed.

Lemma of_RR_at : forall (x : W.RR) (k : positive), rseq' (of_RR x) k = W.rseq x k.
Proof. reflexivity. Qed.

Lemma of_to_RR : forall x : RR', of_RR (to_RR x) = x.
Proof. intro x. destruct x. reflexivity. Qed.

Lemma to_of_RR : forall x : W.RR, to_RR (of_RR x) = x.
Proof. intro x. destruct x. reflexivity. Qed.

Lemma to_RR_Req : forall x y : RR', Req' x y <-> W.Req (to_RR x) (to_RR y).
Proof. intros x y. split; intro H; exact H. Qed.

(* ---- the S1-lemma readout reals as the approximants of R_complete ---- *)

(** A tower of RR' readouts with an exhibited modulus has a level-2 limit in RR
    with the same exported bound (R_complete applied through to_RR; the modulus
    typechecks by conversion, nothing is re-proved). *)
Definition level2_tower
  (X : positive -> RR')
  (Hreg : forall i j k, Qabs (rseq' (X i) k - rseq' (X j) k)
                        <= (1#i) + (1#j) + (2#1) * (1#k))
  : { L : W.RR | forall i k, Qabs (rseq' (X i) k - W.rseq L k) <= (1#i) + (4#1) * (1#k) }
  := W.R_complete (fun i => to_RR (X i)) Hreg.

Theorem level2_tower_diagonal :
  forall (X : positive -> RR')
         (Hreg : forall i j k, Qabs (rseq' (X i) k - rseq' (X j) k)
                               <= (1#i) + (1#j) + (2#1) * (1#k))
         (k : positive),
    W.rseq (proj1_sig (level2_tower X Hreg)) k
      = rseq' (X (2 * k)%positive) (6 * k)%positive.
Proof.
  intros X Hreg k. reflexivity.
Qed.

(** A tower of contracting TAPES: the approximants are the S1-lemma readout reals
    sigma_of (g i), the modulus is stated directly on the tape values g i (N(k)), and
    the level-2 limit reads off the diagonal tape value g (2k) (N(6k)).  This is the
    tape -> readout real -> completed readout chain in one term, with every premise
    exhibited. *)
Definition level2_tape
  (g : positive -> nat -> Q) (rho : positive -> Q)
  (Hrho0 : forall i, 0 <= rho i) (Hrho1 : forall i, rho i < 1)
  (Hcontr : forall i k, Qabs (Delta (g i) (S k)) <= rho i * Qabs (Delta (g i) k))
  (Hreg : forall i j k, Qabs (g i (N_of (g i) (rho i) k) - g j (N_of (g j) (rho j) k))
                        <= (1#i) + (1#j) + (2#1) * (1#k))
  : { L : W.RR | forall i k, Qabs (g i (N_of (g i) (rho i) k) - W.rseq L k)
                             <= (1#i) + (4#1) * (1#k) }
  := level2_tower (fun i => sigma_of (g i) (rho i) (Hrho0 i) (Hrho1 i) (Hcontr i)) Hreg.

Theorem level2_tape_diagonal :
  forall (g : positive -> nat -> Q) (rho : positive -> Q)
         (Hrho0 : forall i, 0 <= rho i) (Hrho1 : forall i, rho i < 1)
         (Hcontr : forall i k, Qabs (Delta (g i) (S k)) <= rho i * Qabs (Delta (g i) k))
         (Hreg : forall i j k, Qabs (g i (N_of (g i) (rho i) k) - g j (N_of (g j) (rho j) k))
                               <= (1#i) + (1#j) + (2#1) * (1#k))
         (k : positive),
    W.rseq (proj1_sig (level2_tape g rho Hrho0 Hrho1 Hcontr Hreg)) k
      = g (2 * k)%positive (N_of (g (2 * k)%positive) (rho (2 * k)%positive) (6 * k)%positive).
Proof.
  intros. reflexivity.
Qed.

(* ===================================================================== *)
(*  In-file readout: Print Assumptions for every object above              *)
(* ===================================================================== *)
Print Assumptions roundtrip_exact.
Print Assumptions roundtrip_exact_fails_outside_alg.
Print Assumptions roundtrip_exact_tape.
Print Assumptions roundtrip_exact_tape_Nidx.
Print Assumptions roundtrip_radius_record.
Print Assumptions roundtrip_radius.
Print Assumptions roundtrip_radius_S1.
Print Assumptions roundtrip_never.
Print Assumptions roundtrip_never_total.
Print Assumptions never_seen_in_alg.
Print Assumptions level2_bound.
Print Assumptions level2_diagonal.
Print Assumptions to_RR.
Print Assumptions of_RR.
Print Assumptions to_RR_at.
Print Assumptions of_RR_at.
Print Assumptions of_to_RR.
Print Assumptions to_of_RR.
Print Assumptions to_RR_Req.
Print Assumptions level2_tower.
Print Assumptions level2_tower_diagonal.
Print Assumptions level2_tape.
Print Assumptions level2_tape_diagonal.
