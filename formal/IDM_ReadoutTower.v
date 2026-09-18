(*
  IDM_ReadoutTower.v -- S1 LEDGER + LICENCE of the Discrete-Continuum Readout Bridge,
  the S1-lemma `sigma_of` (contracting gaps => regularity modulus => a Bishop-readout
  real) and the S4-corollary `Pi_k` (continuum-side return = evaluation), entirely over
  Q / nat / positive.  No Reals, no classical import, no completed limit: the continuum
  object is a resolution-indexed rational readout carrying its own regularity modulus.

  Bridge lines covered (DISCRETE_CONTINUUM_BRIDGE_DESIGN_v0.1.md, section 2 / S1, the
  S1-lemma and the S4-corollary, under the 11b rulings):

    S1  tailsum(Delta g, N, M) = g(N+M) - g(N)                                  [exact, zero residue]
        rho < 1 /\ (forall k, |Delta g(k+1)| <= rho * |Delta g(k)|)
          ==> (1 - rho) * |g(N+M) - g(N)| <= |Delta g(N)|      verdict CERTIFIED(rho, N)
        otherwise no certificate (rho = 1 gives the vacuous 0 <= |Delta g N|; "HOLD" is
        the narrative reading, Dr -- this file has no verdict type; 1/(1-rho) is never
        formed in the certificate; the division form `plateau_radius` is stated ONLY
        under rho < 1).
    S1-lemma  sigma_of
        Delta g(0) = 0  ==>  rho := 0, sigma_of(g) is the constant readout g 0
        else  N(n) := least N <= Nmax(n) with |Delta g(N)| <= (1 - rho) * (1/n)
              sigma_of(g) := [ n |-> g(N(n)) ] in RR' ,
              regularity |g(N(n)) - g(N(m))| <= 1/n + 1/m discharged by S1 alone
    S4-corollary  Pi_k(x) := rseq' x k in Q ;  certificate forall m, |rseq' x m - Pi_k x| <= 1/m + 1/k
        (this IS rreg') ;  Pi_k(sigma_of g) = g(N(k)) exactly ;  re-plateau: the constant
        family of Pi_k x re-lifted by sigma_of lies within 1/k + 1/m of x at every m.

  Genesis sections instantiated (READOUT_GENESIS_CORE.md): A.1 (the retained tape: g is
  the tape, Delta g its retained differences), A.12 (a bridge carries a STATED non-zero
  recovery error: |Delta g N| / (1 - rho), never "0 in the limit"), APP-v011.10 (the
  validity gate "only when bridge error is controlled" is discharged per instance by
  `plateau_certificate`); IDM textbook A8 (declared-stability move, Def 10.5a / Th 10.10:
  plateau => readout).

  Toledo parents (registry/CANONICAL.json, read 2026-09-18 in the proposals/readout-bridge
  worktree @ b2413324; statements re-read in the LIVE IDM worktree, not the mirror):
    Z/M.08.v1  IDM-0035  PSum_delta_telescope   -> parent of `tailsum_delta_telescopes`
                                                   (window shift 0 -> N; `tailsum_delta_zero_is_Z_M08`
                                                   shows the N = 0 instance IS Z/M.08.v1)
    Z/M.06.v1  IDM-0033  FTCC_telescope         -> sibling telescope (Agg form), cited
    R/M.10.v1  IDM-0026  FTCC_eps_exact         -> the eps-explicit telescope (IDM_Bridge.v);
                                                   NOT Required here: IDM_Bridge.v and IDM_Calculus.v
                                                   both define top-level `seqf`/`Deps`, Requiring both
                                                   shadows names (inventory blocker); cited only
    R/M.32.v1  IDM-0057  refine_stable          -> `plateau_certificate` is THIS theorem at
                                                   s := Delta g + the telescoping rewrite: OCCURRENCE
    R/M.14.v1  IDM-0039  geom_majorant_tail     -> engine behind R/M.32; the windowed twin
                                                   `geom_majorant_tail_window` re-runs its induction
                                                   with the premise restricted to [N, N+M)
    R/M.31.v1            abs_tailsum_le         -> reused in `refine_stable_window`
    R/M.30.v1            Qmult_le_l_nonneg      -> reused throughout
    R/M.03.v1  IDM-0019  apriori_stable         -> a-priori licence route (supplies the `forall k`
                                                   premise from the FORM); cited, not Required
    R/M.08.v1  IDM-0024  richardson_apriori_stable -> order p => rho = 2^-p; cited, not Required
    R/M.37.v1  IDM-0062  gap_subadditive (IDM_Continuum.gap) -> `gap_is_abs_Delta` records
                                                   gap g n = |Delta g n| definitionally (renaming)
    weld/M.60.v1 CAN-1296 URCF17RComplete.RR / rseq / rreg / Req (weld__M_60_v1.v L66-70)
                                                -> the Bishop regular-Cauchy readout real. See
                                                   "Why RR' and not Require" below.
    D/M.55.v1  IDM-0114  discrete_floor          -> root no-go (no density), cited
    weld/E.05.v1         verdict alphabet         -> CERTIFIED / HOLD wording, cited

  Why a local `RR'` and not `Require` of weld__M_60_v1.v:
    The load-bearing reason is (2): IDM's own formal/verify.sh compiles with NO -Q/-R; a
    cross-repo `Require` of a Toledo canonical file would make this IDM file un-buildable
    in its own arc.
    Reason (1) as first written ("the chain is not Q-clean by the letter because
    weld__M_60_v1.v line 6 is `Require Coq.Logic.Classical.`") is NOT load-bearing and is
    struck (fixer pass 2026-09-18, independent refuter finding): IDM_BridgeRoundTrip.v
    Requires that file and every one of its 23 in-file Print Assumptions printed Closed,
    so a Require (never Imported) re-tiers nothing -- the per-theorem Print Assumptions
    readouts are the tier evidence, not the Require list.
  RENAMING (stated, byte-for-byte in the field types) -- RR', rseq', rreg', Req', mkRR' are
  a renamed twin of weld/M.60.v1 (CAN-1296), NOT new objects: they are registered as an
  OCCURRENCE under that parent (proposal PROP-BRIDGE-07), never as identifiers of a new row:
        RR'  == RR ,  rseq' == rseq ,  rreg' == rreg ,  Req' == Req   (weld__M_60_v1.v L66-70)
        mkRR' == mkRR.  The transport to_RR / of_RR (both directions, on the nose) is
        compiled in IDM_BridgeRoundTrip.v, which may Require both.

  Every identifier defined or proved in THIS file is NEW DERIVATION / PROPOSAL -- not yet in
  Toledo -- including: tailsum_delta_telescopes, tailsum_delta_zero_is_Z_M08,
  plateau_certificate (occurrence of R/M.32.v1), plateau_radius, geom_majorant_tail_window,
  refine_stable_window, plateau_certificate_window, gap_is_abs_Delta, qpow_nonneg, qpow_le_1,
  gap_geometric, inject_nat_nonneg, inject_nat_succ, qpow_bernoulli, qpow_below_eps,
  bern_transfer, Nidx_from,
  Nidx, Nidx_from_spec, Nidx_spec, Nidx_zero, Pi, Pi_certificate,
  Qfrac_pos, Qfrac_nonneg, tol, accept, Nmax, Nmax_accept, N_of, N_of_tol, N_of_least
  (Phase 2b, 2026-09-18: "least" as an exported identifier, Open ledger 19), plateau_pair,
  sigma_reg, sigma_of, sigma_readout_exact, sigma_readout_plateau, sigma_of_constant,
  const_contracts, sigma_const, sigma_const_at, Pi_replateau, Delta_geom_sum,
  geom_half_contracts, geometric_gaps_certified, harm, Delta_harm, harmonic_refutes_half.
  `plateau_certificate` is expected to be registered as an OCCURRENCE of R/M.32.v1, not a row;
  `tailsum_delta_telescopes` may itself be judged an occurrence of Z/M.08.v1 at merge.
  RR', rseq', rreg', Req' are NOT in the NEW list: renamed twin of weld/M.60.v1 (RENAMING above).

  Licence routes (S1 "Tier now", never merged): the `forall k` premise of
  `plateau_certificate` / `sigma_of` is the A-PRIORI route (R/M.03.v1 / R/M.08.v1 supply it
  from the form); the tape route can witness only finitely many gaps and uses the WINDOWED
  premise of `plateau_certificate_window` (finite_diagnostic per tape). Nothing in this
  file turns a finite tape into a `forall k` (I4 refused).

  Infinity audit: I1 untouched (every symbol in Q / nat / positive); I2 refused (no h -> 0:
  the modulus 1/n is a declared positive rational, indexed by positive); I4 refused (every
  sum is a finite `tailsum`, every search is bounded by `Nmax`, computed from Qarchimedean --
  stdlib, transparent); Z1 refused (g n is a node value at resolution n, never a point);
  Z2 / Z4 (corrected, fixer pass 2026-09-18, independent refuter finding): S1 has NO verdict
  type in this file -- "HOLD" at rho = 1 is the narrative reading (Dr) of a vacuous
  inequality; the typed gate is S5 (PROP_BRIDGE_03). The Definition `Nmax` below divides by
  (1 - rho) * (1 - rho) * (1/n), and the toledo-side `beta_S1` is |Delta g N| / (1 - rho);
  both are exported TOTAL in rho (Coq's Qdiv is total: beta_S1 g 1 N == 0 is provable and
  beta_S1 evaluates to -1 at rho = 2 -- scratch readout chk_indep3, 2026-09-18) and are
  meaningful only under the premise rho < 1, which every theorem that uses them carries
  (Nmax_accept, N_of_tol, sigma_reg, contracting_beta, contracting_radius,
  roundtrip_radius_S1, accept_certified_dQ). No ACCEPT is derivable at rho = 1; the refusal
  of Z2 rests on those premises, not on the Definitions. Threading the guard into the data
  is an open design item (cpg_research_journal PHASE2_COQ_LEDGER.md).

  Compile mapping (ruling 11b-8, live IDM worktree is the source of truth):
    cd <live IDM worktree>/formal &&
    coqc -q -R <live IDM worktree> IDM IDM_ReadoutTower.v
  (logical name IDM.formal.IDM_ReadoutTower; `Require Import IDM_Calculus` resolves under -R,
  as in every other IDM file). Memory floor: `free -g` before each compile, skip if
  available < 3 G, one coqc at a time via `ANSE_HEAVY_MAX=3G anse-heavy`.

  Tier: every theorem below is Th_coqc only after a scratch `Print Assumptions` printed
  "Closed under the global context" in front of the reader; Section hypotheses
  (Hrho0, Hrho1, Hcontr) are DISCLOSED here and become premises of the exported statements.
*)

Require Import QArith.
Require Import Qabs.
Require Import ZArith.
Require Import Lia.
Require Import Lqa.
Require Import IDM_Calculus.
Require Import IDM_Certified.
Require Import IDM_Continuum.

Open Scope Q_scope.

(* ===================================================================== *)
(*  Part A -- S1 LEDGER : the window-shifted telescope                    *)
(* ===================================================================== *)

(** tailsum (Delta g) N M == g (N+M) - g N.  The M-step readout difference is EXACTLY the
    finite sum of the M intermediate gaps.  Parent Z/M.08.v1 (PSum_delta_telescope) via
    window shift 0 -> N; the sum object is IDM_Certified.tailsum.  Not yet in Toledo. *)
Lemma tailsum_delta_telescopes : forall (g : nat -> Q) (N M : nat),
  tailsum (Delta g) N M == g (N + M)%nat - g N.
Proof.
  intros g N M. revert N. induction M as [| m IH]; intro N; simpl.
  - rewrite Nat.add_0_r. ring.
  - rewrite IH. unfold Delta. rewrite Nat.add_succ_r.
    replace (S N + m)%nat with (S (N + m))%nat by lia. ring.
Qed.

(** At N = 0 the window-shifted telescope IS Z/M.08.v1 -- the occurrence relation, in Coq. *)
Lemma tailsum_delta_zero_is_Z_M08 : forall (g : nat -> Q) (M : nat),
  tailsum (Delta g) 0 M == PSum (fun k => Delta g k) M.
Proof.
  intros g M. rewrite tailsum_delta_telescopes, PSum_delta_telescope. simpl. reflexivity.
Qed.

(* ===================================================================== *)
(*  Part B -- S1 LICENCE : the plateau certificate                        *)
(* ===================================================================== *)

(** plateau_certificate = R/M.32.v1 (refine_stable) at s := Delta g, then the telescoping
    rewrite -- an OCCURRENCE, not a new row.  rho = 1 gives 0 <= |Delta g N| (vacuous):
    verdict HOLD; the reciprocal 1/(1-rho) is never formed here. *)
Corollary plateau_certificate : forall (rho : Q) (g : nat -> Q) (N M : nat),
  rho <= 1 ->
  (forall k, Qabs (Delta g (S k)) <= rho * Qabs (Delta g k)) ->
  (1 - rho) * Qabs (g (N + M)%nat - g N) <= Qabs (Delta g N).
Proof.
  intros rho g N M Hrho Hrat.
  pose proof (refine_stable rho (Delta g) N M Hrho Hrat) as H.
  rewrite (Qabs_wd _ _ (tailsum_delta_telescopes g N M)) in H.
  exact H.
Qed.

(** The computable rational radius |Delta g N| / (1 - rho), stated ONLY under rho < 1. *)
Corollary plateau_radius : forall (rho : Q) (g : nat -> Q) (N M : nat),
  rho < 1 ->
  (forall k, Qabs (Delta g (S k)) <= rho * Qabs (Delta g k)) ->
  Qabs (g (N + M)%nat - g N) <= Qabs (Delta g N) / (1 - rho).
Proof.
  intros rho g N M Hrho Hrat.
  apply Qle_shift_div_l; [ lra | ].
  rewrite Qmult_comm. apply plateau_certificate; [ lra | exact Hrat ].
Qed.

(** Windowed twin of R/M.14.v1: the contraction premise is required only on [N, N+M).
    Same induction on M generalising N, premise restricted to the window.  This is the
    form a finite TAPE can witness (finite_diagnostic per tape).  Not yet in Toledo. *)
Lemma geom_majorant_tail_window : forall (rho : Q) (t : nat -> Q) (N M : nat),
  (forall k, 0 <= t k) ->
  (forall k, (N <= k < N + M)%nat -> t (S k) <= rho * t k) ->
  (1 - rho) * tailsum t N M <= t N.
Proof.
  intros rho t N M Hpos. revert N. induction M as [| m IHm]; intros N Hrat.
  - simpl. rewrite Qmult_0_r. apply Hpos.
  - simpl. rewrite Qmult_plus_distr_r.
    apply (Qle_trans _ ((1 - rho) * t N + rho * t N)).
    + apply Qplus_le_r.
      apply (Qle_trans _ (t (S N))).
      * apply IHm. intros k Hk. apply Hrat. lia.
      * apply Hrat. lia.
    + apply Qle_lteq. right. ring.
Qed.

(** Windowed twin of R/M.32.v1 (reuses R/M.31.v1 abs_tailsum_le and R/M.30.v1). *)
Lemma refine_stable_window : forall (rho : Q) (s : nat -> Q) (N M : nat),
  rho <= 1 ->
  (forall k, (N <= k < N + M)%nat -> Qabs (s (S k)) <= rho * Qabs (s k)) ->
  (1 - rho) * Qabs (tailsum s N M) <= Qabs (s N).
Proof.
  intros rho s N M Hrho Hrat.
  assert (Hnn : 0 <= 1 - rho) by lra.
  apply Qle_trans with (y := (1 - rho) * tailsum (fun k => Qabs (s k)) N M).
  - apply Qmult_le_l_nonneg; [ assumption | apply abs_tailsum_le ].
  - apply (geom_majorant_tail_window rho (fun k => Qabs (s k)) N M).
    + intro k. apply Qabs_nonneg.
    + intros k Hk. apply Hrat. exact Hk.
Qed.

(** The tape-route licence: contraction observed on the window [N, N+M) certifies the
    plateau on that window.  Not yet in Toledo. *)
Lemma plateau_certificate_window : forall (rho : Q) (g : nat -> Q) (N M : nat),
  rho <= 1 ->
  (forall k, (N <= k < N + M)%nat -> Qabs (Delta g (S k)) <= rho * Qabs (Delta g k)) ->
  (1 - rho) * Qabs (g (N + M)%nat - g N) <= Qabs (Delta g N).
Proof.
  intros rho g N M Hrho Hrat.
  pose proof (refine_stable_window rho (Delta g) N M Hrho Hrat) as H.
  rewrite (Qabs_wd _ _ (tailsum_delta_telescopes g N M)) in H.
  exact H.
Qed.

(* ===================================================================== *)
(*  Part C -- gap algebra link and geometric decay along the tape          *)
(* ===================================================================== *)

(** IDM_Continuum's `gap` (R/M.37.v1 family) is |Delta g| under renaming -- definitional. *)
Lemma gap_is_abs_Delta : forall (g : nat -> Q) (n : nat), gap g n = Qabs (Delta g n).
Proof. reflexivity. Qed.

Lemma qpow_nonneg : forall (r : Q) (n : nat), 0 <= r -> 0 <= qpow r n.
Proof.
  intros r n Hr. induction n as [| k IH]; cbn [qpow].
  - apply q01_le.
  - apply Qmult_le_0_compat; assumption.
Qed.

Lemma qpow_le_1 : forall (r : Q) (n : nat), 0 <= r -> r <= 1 -> qpow r n <= 1.
Proof.
  intros r n Hr0 Hr1. induction n as [| k IH]; cbn [qpow].
  - apply Qle_refl.
  - apply Qle_trans with (y := r * 1).
    + apply Qmult_le_l_nonneg; assumption.
    + rewrite Qmult_1_r. assumption.
Qed.

(** gap_geometric: under contraction the gaps decay geometrically along the tape,
    |Delta g (N + j)| <= rho^j * |Delta g N|  (0 <= rho).  Not yet in Toledo. *)
Lemma gap_geometric : forall (rho : Q) (g : nat -> Q),
  0 <= rho ->
  (forall k, Qabs (Delta g (S k)) <= rho * Qabs (Delta g k)) ->
  forall (N j : nat), Qabs (Delta g (N + j)%nat) <= qpow rho j * Qabs (Delta g N).
Proof.
  intros rho g Hrho Hrat N j. induction j as [| j IH].
  - rewrite Nat.add_0_r. cbn [qpow]. rewrite Qmult_1_l. apply Qle_refl.
  - rewrite Nat.add_succ_r. cbn [qpow].
    apply Qle_trans with (y := rho * Qabs (Delta g (N + j)%nat)).
    + apply Hrat.
    + rewrite <- Qmult_assoc. apply Qmult_le_l_nonneg; assumption.
Qed.

(* ===================================================================== *)
(*  Part D -- Bernoulli over Q (division-free), local re-proof             *)
(* ===================================================================== *)

Lemma inject_nat_nonneg : forall n : nat, 0 <= inject_Z (Z.of_nat n).
Proof.
  intro n. replace 0 with (inject_Z 0) by reflexivity.
  rewrite <- Zle_Qle. apply Nat2Z.is_nonneg.
Qed.

Lemma inject_nat_succ : forall n : nat,
  inject_Z (Z.of_nat (S n)) == inject_Z (Z.of_nat n) + 1.
Proof.
  intro n. rewrite Nat2Z.inj_succ, <- Z.add_1_r, inject_Z_plus. reflexivity.
Qed.

(** qpow_bernoulli: rho^n * (1 + n (1 - rho)) <= 1 for 0 <= rho <= 1.  This is Bernoulli's
    inequality (1 + x)^n >= 1 + n x at x := (1 - rho)/rho, written division-free so that it
    stays in Q with no side condition rho <> 0.  Not yet in Toledo. *)
Lemma qpow_bernoulli : forall (rho : Q) (n : nat),
  0 <= rho -> rho <= 1 ->
  qpow rho n * (1 + inject_Z (Z.of_nat n) * (1 - rho)) <= 1.
Proof.
  intros rho n Hr0 Hr1. induction n as [| k IH].
  - replace (inject_Z (Z.of_nat 0)) with 0 by reflexivity. cbn [qpow]. lra.
  - rewrite inject_nat_succ. cbn [qpow].
    pose proof (qpow_nonneg rho k Hr0) as Ha0.
    pose proof (qpow_le_1 rho k Hr0 Hr1) as Ha1.
    pose proof (inject_nat_nonneg k) as Hn.
    assert (H1 : rho * (qpow rho k * (1 + inject_Z (Z.of_nat k) * (1 - rho))) <= rho * 1)
      by (apply Qmult_le_l_nonneg; assumption).
    assert (H2 : (1 - rho) * (rho * qpow rho k) <= (1 - rho) * 1).
    { apply Qmult_le_l_nonneg; [ lra | ].
      apply Qle_trans with (y := rho * 1).
      - apply Qmult_le_l_nonneg; assumption.
      - rewrite Qmult_1_r. assumption. }
    lra.
Qed.

(** qpow_below_eps: the readable form of Bernoulli -- once n is large enough that
    eps * (1 + n (1 - rho)) >= 1, the n-th power is below eps.  Division-free; the
    reciprocal 1/eps is never formed.  Not yet in Toledo. *)
Lemma qpow_below_eps : forall (rho eps : Q) (n : nat),
  0 <= rho -> rho <= 1 -> 0 < eps ->
  1 <= eps * (1 + inject_Z (Z.of_nat n) * (1 - rho)) ->
  qpow rho n <= eps.
Proof.
  intros rho eps n Hr0 Hr1 He Hn.
  pose proof (qpow_bernoulli rho n Hr0 Hr1) as HB.
  pose proof (inject_nat_nonneg n) as Hnq.
  assert (Hpos : 0 < 1 + inject_Z (Z.of_nat n) * (1 - rho)).
  { assert (Hx : 0 <= inject_Z (Z.of_nat n) * (1 - rho))
      by (apply Qmult_le_0_compat; [ assumption | lra ]).
    lra. }
  apply (Qmult_le_r _ _ _ Hpos).
  apply Qle_trans with (y := 1); [ exact HB | exact Hn ].
Qed.

(** Pure algebra used by Nmax_accept: from the Bernoulli bound and a large enough NQ,
    rho^n * A <= d * e.  Not yet in Toledo. *)
Lemma bern_transfer : forall (P A NQ d e : Q),
  0 <= P -> P * (1 + NQ * d) <= 1 -> 0 <= d * e -> A <= NQ * d * d * e -> P * A <= d * e.
Proof.
  intros P A NQ d e HP HB Hde HA.
  apply Qle_trans with (y := P * (NQ * d * d * e)).
  - apply Qmult_le_l_nonneg; assumption.
  - apply Qle_trans with (y := (P * (1 + NQ * d)) * (d * e)).
    + setoid_replace (P * (NQ * d * d * e)) with ((P * (NQ * d)) * (d * e)) by ring.
      apply Qmult_le_compat_r; [ | assumption ].
      apply Qmult_le_l_nonneg; [ assumption | lra ].
    + apply Qle_trans with (y := 1 * (d * e)).
      * apply Qmult_le_compat_r; assumption.
      * rewrite Qmult_1_l. apply Qle_refl.
Qed.

(* ===================================================================== *)
(*  Part E -- Nidx : bounded search (least index below a bound)            *)
(* ===================================================================== *)

(** Nidx_from P start fuel: the least k in [start, start+fuel) with P k = true, else
    start+fuel.  Structural recursion on fuel -- no unbounded search, no I4. *)
Fixpoint Nidx_from (P : nat -> bool) (start fuel : nat) : nat :=
  match fuel with
  | O => start
  | S f => if P start then start else Nidx_from P (S start) f
  end.

Definition Nidx (P : nat -> bool) (bound : nat) : nat := Nidx_from P 0 bound.

Lemma Nidx_from_spec : forall (P : nat -> bool) (fuel start : nat),
  P (start + fuel)%nat = true ->
  P (Nidx_from P start fuel) = true
  /\ (start <= Nidx_from P start fuel <= start + fuel)%nat
  /\ (forall k, (start <= k < Nidx_from P start fuel)%nat -> P k = false).
Proof.
  intros P fuel. induction fuel as [| f IH]; intros start Hend.
  - simpl. rewrite Nat.add_0_r in Hend.
    split; [ exact Hend | split; [ lia | intros k Hk; exfalso; lia ] ].
  - simpl. destruct (P start) eqn:E.
    + split; [ exact E | split; [ lia | intros k Hk; exfalso; lia ] ].
    + assert (Hend' : P (S start + f)%nat = true)
        by (rewrite Nat.add_succ_l; rewrite Nat.add_succ_r in Hend; exact Hend).
      destruct (IH (S start) Hend') as [H1 [H2 H3]].
      split; [ exact H1 | split; [ lia | ] ].
      intros k Hk.
      destruct (Nat.eq_dec k start) as [-> | Hne].
      * exact E.
      * apply H3. lia.
Qed.

(** Nidx_spec: if P holds at the bound, Nidx returns an index <= bound where P holds and
    below which P fails everywhere -- the LEAST witness under the bound. *)
Lemma Nidx_spec : forall (P : nat -> bool) (bound : nat),
  P bound = true ->
  P (Nidx P bound) = true
  /\ (Nidx P bound <= bound)%nat
  /\ (forall k, (k < Nidx P bound)%nat -> P k = false).
Proof.
  intros P bound Hb. unfold Nidx.
  destruct (Nidx_from_spec P bound 0 Hb) as [H1 [H2 H3]].
  split; [ exact H1 | split; [ lia | intros k Hk; apply H3; lia ] ].
Qed.

Lemma Nidx_zero : forall (P : nat -> bool) (bound : nat),
  P 0%nat = true -> Nidx P bound = 0%nat.
Proof.
  intros P bound H0. unfold Nidx.
  destruct bound as [| b]; simpl; [ reflexivity | rewrite H0; reflexivity ].
Qed.

(* ===================================================================== *)
(*  Part F -- RR' : the Bishop regular-Cauchy readout real (renaming of    *)
(*  weld/M.60.v1's RR / rseq / rreg / Req) and the S4-corollary Pi_k        *)
(* ===================================================================== *)

Record RR' : Type := mkRR' {
  rseq' :> positive -> Q ;
  rreg' : forall n m, Qabs (rseq' n - rseq' m) <= (1 # n) + (1 # m)
}.

Definition Req' (x y : RR') : Prop :=
  forall n m, Qabs (rseq' x n - rseq' y m) <= (1 # n) + (1 # m).

(** Pi_k : the continuum-side return is an EVALUATION of the readout at resolution k. *)
Definition Pi (k : positive) (x : RR') : Q := rseq' x k.

(** Pi_certificate: the evaluation carries its own error certificate -- this IS rreg'. *)
Theorem Pi_certificate : forall (x : RR') (k m : positive),
  Qabs (rseq' x m - Pi k x) <= (1 # m) + (1 # k).
Proof. intros x k m. unfold Pi. apply rreg'. Qed.

Lemma Qfrac_pos : forall n : positive, 0 < 1 # n.
Proof. intro n. unfold Qlt. simpl. lia. Qed.

Lemma Qfrac_nonneg : forall n : positive, 0 <= 1 # n.
Proof. intro n. apply Qlt_le_weak. apply Qfrac_pos. Qed.

(* ===================================================================== *)
(*  Part G -- sigma_of : contracting gaps => a readout real                *)
(* ===================================================================== *)

Section SigmaOf.
  Variable g : nat -> Q.
  Variable rho : Q.
  (* DISCLOSED section hypotheses; they become premises of every exported statement. *)
  Hypothesis Hrho0 : 0 <= rho.
  Hypothesis Hrho1 : rho < 1.
  Hypothesis Hcontr : forall k, Qabs (Delta g (S k)) <= rho * Qabs (Delta g k).

  (** tolerance at resolution n: (1 - rho) / n, division-free. *)
  Definition tol (n : positive) : Q := (1 - rho) * (1 # n).

  (** the decidable acceptance test on the tape at index N. *)
  Definition accept (n : positive) (N : nat) : bool := Qle_bool (Qabs (Delta g N)) (tol n).

  (** Nmax n: a computable ceiling above which acceptance is guaranteed (Bernoulli +
      geometric decay); Qarchimedean is stdlib and transparent, so Nmax computes.
      finite_diagnostic readout 2026-09-18 (scratch Eval vm_compute, geometric tape
      g := geom_sum (1#2), rho := 1/2): Nmax 4 = 17, N_of 4 = 3, N_of 100 = 8,
      readout g (N_of 4) = 7/4 with gap 1/8 -- the least index, not the ceiling. *)
  Definition Nmax (n : positive) : nat :=
    Pos.to_nat (proj1_sig (Qarchimedean
      (Qabs (Delta g 0) / ((1 - rho) * (1 - rho) * (1 # n))))).

  Lemma Nmax_accept : forall n : positive, accept n (Nmax n) = true.
  Proof.
    intro n. unfold accept, tol, Nmax.
    apply Qle_bool_iff.
    set (A := Qabs (Delta g 0)).
    set (e := 1 # n).
    set (B := (1 - rho) * (1 - rho) * e).
    assert (He : 0 < e) by apply Qfrac_pos.
    assert (Hd : 0 < 1 - rho) by lra.
    assert (HB : 0 < B)
      by (unfold B; apply Qmult_lt_0_compat; [ apply Qmult_lt_0_compat; assumption | assumption ]).
    assert (Hne : ~ B == 0) by (intro Hc; lra).
    destruct (Qarchimedean (A / B)) as [p Hp]. cbn [proj1_sig].
    assert (HNQ : inject_Z (Z.of_nat (Pos.to_nat p)) = Z.pos p # 1)
      by (rewrite positive_nat_Z; reflexivity).
    pose proof (gap_geometric rho g Hrho0 Hcontr 0 (Pos.to_nat p)) as Hgap.
    rewrite Nat.add_0_l in Hgap.
    pose proof (qpow_bernoulli rho (Pos.to_nat p) Hrho0 (Qlt_le_weak _ _ Hrho1)) as HBern.
    rewrite HNQ in HBern.
    assert (HA : A <= (Z.pos p # 1) * (1 - rho) * (1 - rho) * e).
    { apply Qle_trans with (y := B * (A / B)).
      - rewrite (Qmult_div_r A B Hne). apply Qle_refl.
      - setoid_replace ((Z.pos p # 1) * (1 - rho) * (1 - rho) * e)
          with (B * (Z.pos p # 1)) by (unfold B; ring).
        apply Qmult_le_l_nonneg; [ lra | apply Qlt_le_weak; exact Hp ]. }
    apply Qle_trans with (y := qpow rho (Pos.to_nat p) * A).
    - exact Hgap.
    - apply (bern_transfer (qpow rho (Pos.to_nat p)) A (Z.pos p # 1) (1 - rho) e).
      + apply qpow_nonneg; assumption.
      + exact HBern.
      + apply Qmult_le_0_compat; [ lra | apply Qfrac_nonneg ].
      + exact HA.
  Qed.

  (** N(n): the LEAST index <= Nmax n at which the tape gap is within tolerance. *)
  Definition N_of (n : positive) : nat := Nidx (accept n) (Nmax n).

  Lemma N_of_tol : forall n : positive, Qabs (Delta g (N_of n)) <= (1 - rho) * (1 # n).
  Proof.
    intro n. unfold N_of.
    destruct (Nidx_spec (accept n) (Nmax n) (Nmax_accept n)) as [H1 _].
    change (Qle_bool (Qabs (Delta g (Nidx (accept n) (Nmax n)))) ((1 - rho) * (1 # n)) = true) in H1.
    apply Qle_bool_iff. exact H1.
  Qed.

  (** N_of_least: the word "least" as an exported identifier (Open ledger item 19,
      Phase 2b, 2026-09-18) -- below N_of n the tape gap is NOT within tolerance.
      From Nidx_spec's third conjunct (P k = false for every k < Nidx P bound) and the
      Bool/Prop bridge Qle_bool_iff; nothing else. *)
  Lemma N_of_least : forall (n : positive) (k : nat),
    (k < N_of n)%nat -> ~ (Qabs (Delta g k) <= tol n).
  Proof.
    intros n k Hk Hle. unfold N_of in Hk.
    destruct (Nidx_spec (accept n) (Nmax n) (Nmax_accept n)) as [_ [_ H3]].
    specialize (H3 k Hk). unfold accept in H3.
    rewrite (proj2 (Qle_bool_iff _ _) Hle) in H3. discriminate.
  Qed.

  (** S1 at a pair of tape indices a <= b (occurrence of plateau_certificate). *)
  Lemma plateau_pair : forall a b : nat, (a <= b)%nat ->
    (1 - rho) * Qabs (g b - g a) <= Qabs (Delta g a).
  Proof.
    intros a b Hab.
    pose proof (plateau_certificate rho g a (b - a) (Qlt_le_weak _ _ Hrho1) Hcontr) as H.
    replace (a + (b - a))%nat with b in H by lia.
    exact H.
  Qed.

  (** REGULARITY: |g(N n) - g(N m)| <= 1/n + 1/m, discharged by S1 alone. *)
  Lemma sigma_reg : forall n m : positive,
    Qabs (g (N_of n) - g (N_of m)) <= (1 # n) + (1 # m).
  Proof.
    intros n m.
    pose proof (N_of_tol n) as Hn. pose proof (N_of_tol m) as Hm.
    pose proof (Qfrac_nonneg n) as Hn0. pose proof (Qfrac_nonneg m) as Hm0.
    assert (Hd : 0 < 1 - rho) by lra.
    destruct (Nat.le_gt_cases (N_of n) (N_of m)) as [Hle | Hlt].
    - pose proof (plateau_pair (N_of n) (N_of m) Hle) as H.
      rewrite Qabs_Qminus.
      assert (Hx : Qabs (g (N_of m) - g (N_of n)) <= 1 # n).
      { apply (Qmult_le_l _ _ (1 - rho) Hd). lra. }
      lra.
    - pose proof (plateau_pair (N_of m) (N_of n) (Nat.lt_le_incl _ _ Hlt)) as H.
      assert (Hx : Qabs (g (N_of n) - g (N_of m)) <= 1 # m).
      { apply (Qmult_le_l _ _ (1 - rho) Hd). lra. }
      lra.
  Qed.

  (** sigma_of: the readout real  n |-> g(N n)  with its regularity modulus. *)
  Definition sigma_of : RR' := mkRR' (fun n => g (N_of n)) sigma_reg.

  (** Pi_k(sigma_of g) = g(N(k)) EXACTLY (definitional). *)
  Theorem sigma_readout_exact : forall k : positive, Pi k sigma_of = g (N_of k).
  Proof. intro k. reflexivity. Qed.

  (** Every later tape value stays within 1/k of the k-th readout: the plateau licence. *)
  Theorem sigma_readout_plateau : forall (k : positive) (M : nat),
    Qabs (g (N_of k + M)%nat - Pi k sigma_of) <= 1 # k.
  Proof.
    intros k M. change (Pi k sigma_of) with (g (N_of k)).
    pose proof (plateau_certificate rho g (N_of k) M (Qlt_le_weak _ _ Hrho1) Hcontr) as H.
    pose proof (N_of_tol k) as Hk.
    assert (Hd : 0 < 1 - rho) by lra.
    apply (Qmult_le_l _ _ (1 - rho) Hd). lra.
  Qed.

  (** Constant case, handled separately: Delta g 0 = 0 makes the search stop at index 0
      and the readout real is the constant g 0 at every resolution. *)
  Theorem sigma_of_constant : Qabs (Delta g 0) == 0 ->
    forall n : positive, rseq' sigma_of n = g 0%nat.
  Proof.
    intros H0 n.
    change (g (N_of n) = g 0%nat).
    unfold N_of. rewrite Nidx_zero; [ reflexivity | ].
    unfold accept, tol. apply Qle_bool_iff. rewrite H0.
    apply Qmult_le_0_compat; [ lra | apply Qfrac_nonneg ].
  Qed.
End SigmaOf.

(* ===================================================================== *)
(*  Part H -- the S4-corollary re-plateau : R -> Q -> R round trip          *)
(* ===================================================================== *)

(** A constant family contracts with rho = 0 (its gaps are exactly zero). *)
Lemma const_contracts : forall (q : Q) (k : nat),
  Qabs (Delta (fun _ => q) (S k)) <= 0 * Qabs (Delta (fun _ => q) k).
Proof.
  intros q k. unfold Delta.
  setoid_replace (q - q) with 0 by ring.
  rewrite Qmult_0_l. apply Qle_refl.
Qed.

(** sigma_const q: the constant readout real of q, obtained through sigma_of at rho = 0
    (the design's "Delta g(0) = 0 ==> rho := 0" branch). *)
Definition sigma_const (q : Q) : RR' :=
  sigma_of (fun _ => q) 0 (Qle_refl 0) q01 (const_contracts q).

Theorem sigma_const_at : forall (q : Q) (n : positive), rseq' (sigma_const q) n = q.
Proof. intros q n. reflexivity. Qed.

(** Pi_replateau: read x at resolution k (Pi_k x), re-enter it as a constant discrete
    family, re-lift by sigma_of -- the result is within 1/k + 1/m of x at every m.  This
    is rreg' under the renaming: the return is an evaluation, not a decision. *)
Theorem Pi_replateau : forall (x : RR') (k m : positive),
  Qabs (rseq' (sigma_const (Pi k x)) m - rseq' x m) <= (1 # k) + (1 # m).
Proof.
  intros x k m. rewrite sigma_const_at. unfold Pi. apply rreg'.
Qed.

(* ===================================================================== *)
(*  Part I -- Type-P controls (a gate that has never rejected is no gate)  *)
(* ===================================================================== *)

Lemma Delta_geom_sum : forall (r : Q) (k : nat), Delta (geom_sum r) k == qpow r k.
Proof. intros r k. unfold Delta. cbn [geom_sum]. ring. Qed.

Lemma geom_half_contracts : forall k : nat,
  Qabs (Delta (geom_sum (1 # 2)) (S k)) <= (1 # 2) * Qabs (Delta (geom_sum (1 # 2)) k).
Proof.
  intro k.
  rewrite (Qabs_wd _ _ (Delta_geom_sum (1 # 2) (S k))).
  rewrite (Qabs_wd _ _ (Delta_geom_sum (1 # 2) k)).
  cbn [qpow]. rewrite Qabs_Qmult.
  setoid_replace (Qabs (1 # 2)) with (1 # 2) by reflexivity.
  apply Qle_refl.
Qed.

(** POSITIVE control: geometric gaps, rho = 1/2 -- CERTIFIED on every window. *)
Example geometric_gaps_certified : forall N M : nat,
  (1 - (1 # 2)) * Qabs (geom_sum (1 # 2) (N + M)%nat - geom_sum (1 # 2) N)
    <= Qabs (Delta (geom_sum (1 # 2)) N).
Proof.
  intros N M. apply plateau_certificate; [ lra | apply geom_half_contracts ].
Qed.

(** harmonic tape: gaps 1/(k+1). *)
Definition harm (k : nat) : Q := PSum (fun j => 1 # Pos.of_nat (S j)) k.

Lemma Delta_harm : forall k : nat, Delta harm k == 1 # Pos.of_nat (S k).
Proof. intro k. unfold Delta, harm. cbn [PSum]. ring. Qed.

(** NEGATIVE control: harmonic gaps refute rho = 1/2 already at k = 1 -> verdict HOLD. *)
Example harmonic_refutes_half :
  ~ (Qabs (Delta harm 2) <= (1 # 2) * Qabs (Delta harm 1)).
Proof.
  apply Qlt_not_le.
  rewrite (Qabs_wd _ _ (Delta_harm 2)), (Qabs_wd _ _ (Delta_harm 1)).
  unfold Qlt. simpl. lia.
Qed.

Close Scope Q_scope.
