(*
  Bridge_Seam.v -- the OPERATOR SEAM of the Discrete-Continuum Readout Bridge
  (DISCRETE_CONTINUUM_BRIDGE_DESIGN_v0.1.md section 2 item 6 / section 4 item 2 /
  section 9 item 5; proposal row PROP-BRIDGE-08), written as RING IDENTITIES over Q
  on the path graph with unit weights.  Phase 2b, 2026-09-18.

  BRIDGE LINE (an operator INSTANTIATION of the reader O -- not a core line, never
  S1-S5): when the reader O is a Dirichlet / spectral reader, the declared graph
  (V, E, w) at spacing h carries L_R = D_W - W, and the continuum second-order
  operator is READ OUT from L_R by the seam

        -h^2 Delta_h  :=  L_R^(h)          (h^2 multiplied through, no division)

  so that "d^2 / dx^2", the [1,-2,1] stencil and the retained-difference Laplacian
  are ONE object at every finite h.  Nothing below takes h -> 0 (I2 refused); every
  symbol is in Q / nat / a finite list; the continuum PDE is the readout, the graph
  is the state.  The spectral ceiling below is the reason a "UV divergence" is an
  h -> 0 artefact and never a readout: at every h, every EXACT RATIONAL Rayleigh
  value lam of h^2 * (-Delta_h) on the path satisfies lam <= 4 (seam_ceiling,
  compiled below); the lower bound 0 <= lam is weld/M.42's rayleigh_nonneg, cited
  here and not instantiated (fixer pass 2026-09-18: the earlier wording "the
  spectrum sits in [0, 4]" overstated what this file compiles -- the statements
  quantify over exact rational Rayleigh pairs, not a spectrum).

  Every object defined or proved in THIS file is NEW DERIVATION / PROPOSAL --
  not yet in Toledo -- until the registrar assigns PROP-BRIDGE-08 its code, with
  ONE exception found in the fixer pass (2026-09-18, EPIS-REUSE-PIPELINE step 1
  extended to registry/proposals/*.json): seam_energy_qform is an OCCURRENCE under
  constant substitution w := path_w (path_w_sym, path_w_diag0) of the proposals-lane
  row PROP-P3-LRS-LAPLACIAN-PSD-CLOSURE-01 (endogenous_laplacian_quadratic_form:
  x^T L x == sum_{i<j} w_ij (x_i - x_j)^2 for the same `Lap` at general N, w
  symmetric with zero diagonal; tier Th_coqc as its source states; its Coq file
  lives in a private repository and was matched by statement only).  The
  parents are used by THEIR OWN Coq objects (no private twin of any of them):

    L_R/M.20.v1   IDM_Matrix.laplacian_symmetric      (used in seam_box: L = L^T)
    L_R/M.21.v1   IDM_Matrix.laplacian_rowsum_zero    (Lap / deg / Sum are the objects
    L_R/M.22.v1   IDM_Matrix.laplacian_ones_in_kernel  of that section; the two row-sum
                                                        theorems are cited, not re-proved)
    Keystone/M.03.v1  IDM_Keystone.keystone_B_eq_I    (B_form = I_form; seam_energy_names)
    weld/M.41.v1  weld__M_41_v1.energy / energy_nonneg / D2 / laplacian_stencil
                  (the Dirichlet energy as a fold over (i, j, w) edges; the D2 stencil)
    weld/M.42.v1  weld__M_42_v1.SpectralCeiling.rayleigh_ceiling / form / deg / norm2
                  (the degree-only Rayleigh ceiling lambda <= 2 d_max; instantiated here
                  at d_max = 2, the registered statement has no h)
    weld/M.01.v1  L_R = D_W - W (root reading; Lap i j = if i = j then deg i else - w i j
                  IS D_W - W entrywise, IDM_Matrix L128)

  What is proved (all ring identities over Q; no Reals, no classical axiom, no
  unfinished proof, no Section variable):

    (a) seam_grid          (L_R phi)(i) = -(phi(i-1) - 2 phi(i) + phi(i+1))  at every
                           interior node of the path with unit weights, with L_R the
                           IDM_Matrix Laplacian `Lap n path_w` applied through `Sum`
                           (Lvec_is_mmul: this IS IDM_Matrix.mmul on a column vector);
        seam_grid_D2       the same with phi the tape of f : Q -> Q read at spacing h:
                           (L_R phi)(i) = - D2 f x_i h  -- weld/M.41's D2 IS h^2 Delta_h,
                           so this line is  -h^2 Delta_h f = L_R phi  exactly, h^2
                           multiplied through (premise: f respects Qeq -- Q is a setoid);
        seam_grid_stencil  the [1,-2,1] order of weld/M.41.laplacian_stencil.
    (b) seam_energy        <phi, L_R phi> = I_form phi (path edges) = Sum of (phi(i+1) -
                           phi(i))^2 over the m edges, for EVERY m (by induction on m,
                           general n -- no fixed small n was needed: IDM_Matrix exports
                           Sum_plus / Sum_ext_lt / Sum_delta, which suffice);
        seam_energy_names  the same number under its five registered names:
                           qform (IDM_Matrix Lap) = I_form = B_form (Keystone/M.03.v1)
                           = weld/M.41 energy = weld/M.42 form = edge_sq.
    (c) seam_box           I(phi + e_i) - I(phi) = 2 (L_R phi)_i + L_ii  for ANY weighted
                           graph with symmetric w (L_R/M.20.v1 is the step), i < n: the
                           finite-difference gradient of the retained information in the
                           direction of IDM_Matrix's identity column `mid i`, exact, with
                           the second-order term L_ii kept (no Jacobian, no "+ o(1)");
        seam_box_path      the same on the path with I = I_form (Keystone/M.03.v1).
    (d) seam_ceiling       every exact Rayleigh pair of the path graph on S m nodes has
                           lam <= 4 = 2 d_max (weld/M.42.v1 rayleigh_ceiling at d_max = 2:
                           deg_path_E_le2 is the degree bound, path_nodes_ok the range);
        seam_ceiling_Lap   the same for an exact eigenpair of the IDM_Matrix Laplacian
                           `Lap (S m) path_w` (through seam_energy and Sum_is_qsum);
        seam_ceiling_scaled  h*h*mu == lam  ==>  h*h*mu <= 4: the design's
                           "lambda(Delta_h) <= 2 d_max / h^2" as a POSITIVE-SCALE rewrite
                           with h^2 multiplied through (NEW DERIVATION / PROPOSAL; the
                           registered weld/M.42 statement has no h).

  NOT written (Open, stance + falsifier in the programme's Coq ledger, private research journal):
  the tick-path x space PRODUCT-graph form (the (+1,-1) d'Alembertian) named in the
  PROP-BRIDGE-08 note_ascii -- this file fixes seam_box as the pullback identity the
  task states; the product graph is a second instantiation of the same seam.
  NAME NOTE (fixer pass 2026-09-18): the registry row's note_ascii used the name
  `seam_box` for that product-graph form; in THIS file `seam_box` denotes the
  pullback identity (c) below and nothing else.  Whether the compiled theorem is
  renamed (e.g. seam_pullback) or the product-graph form gets its own name is a
  founder / registrar decision, not made here; the row now states the compiled
  meaning.

  Reuse pipeline (EPIS-REUSE-PIPELINE steps 1-2, recorded): Toledo lookup by statement
  2026-09-18 over registry/CANONICAL.json -- the [1,-2,1] = L_R identity exists only
  as weld/M.41 laplacian_stencil (on Q -> Q, no graph), the energy identity only as
  Keystone/M.03 (edge list, no operator), the ceiling only as weld/M.42 (no h); no
  canonical object states the operator/energy/box identities for `Lap` against those
  parents.  Fixer pass, same day, lookup extended to registry/proposals/*.json: the
  Lap-vs-edge-sum identity IS stated there at general N (PROP-P3-LRS-LAPLACIAN-PSD-
  CLOSURE-01, see above) -> seam_energy_qform is its occurrence, not a new object;
  no proposals-lane match was found for the stencil identity (seam_grid,
  seam_grid_D2, seam_grid_stencil), the I_form link (seam_energy, seam_energy_names),
  the pullback identity (seam_box, seam_box_path) or the h^2-scaled ceiling
  (seam_ceiling_scaled) -> those are the delta.  Two local twins, disclosed:
  Sum_scale (three lines; = weld__M_42_v1.SpectralCeiling.qsum_scale, since Sum and
  qsum are convertible by Sum_is_qsum) and edge_sq (the induction-friendly Sum form
  of the edge ledger; = SpectralCeiling.form (path_E m) = weld__M_41_v1.energy
  (path_edges m) = I_form by seam_energy_names) -- neither carries theorem content
  of its own.  Genesis: instantiates the Face-8 operator reader (design section 4
  item 2), root SignBridge made exact (the sign is a theorem here, not a convention).

  Compile mapping (ruling 11b-8: the live IDM worktree is the source of truth):
    cd <live IDM worktree>/formal &&
    coqc -q -R <live IDM worktree> IDM -Q <toledo worktree>/coq/canonical MRC Bridge_Seam.v
  Prerequisites (each once, same mapping): IDM_Matrix.vo, IDM_Keystone.vo (coqc -q -R
  <live IDM worktree> IDM), weld__M_41_v1.vo and weld__M_42_v1.vo (cd <toledo
  worktree>/coq/canonical && coqc -q -Q . MRC <file>).  Logical name of this file:
  IDM.formal.Bridge_Seam.  `formal/verify.sh` cannot build it (it needs the MRC mapping),
  exactly as for IDM_BridgeRoundTrip.v.
  Memory floor (binding): `free -g` before every coqc, skip if available < 3 G, one coqc
  at a time under a memory cap, never in the background, never a
  full-arc verify script in the loop.

  Tier: every theorem below is Th_coqc only after a scratch `Print Assumptions` printed
  "Closed under the global context" in front of the reader (the in-file readouts at the
  end print the same during the compile).  No AI is an author of this file.
*)

Require Import Coq.Lists.List.
Import ListNotations.
Require Import Coq.Arith.PeanoNat.
Require Import Coq.ZArith.ZArith.
Require Import Coq.micromega.Lia.
Require Import Coq.QArith.QArith.
Require Import Coq.micromega.Lqa.

From IDM.formal Require Import IDM_Matrix.     (* Sum, Mat, mmul, mid, deg, Lap; L_R/M.20-22.v1 *)
From IDM.formal Require Import IDM_Keystone.   (* edge, Phi, B_form, I_form; Keystone/M.03.v1 *)
From MRC Require weld__M_41_v1.                (* energy, D2, laplacian_stencil; weld/M.41.v1 *)
From MRC Require Import weld__M_42_v1.         (* SpectralCeiling.*; weld/M.42.v1 *)

Open Scope Q_scope.

(* --------------------------------------------------------------------- *)
(*  0. Bookkeeping lemmas on IDM_Matrix's Sum (one-step unfoldings and a  *)
(*     scalar pull-out; the parents export Sum_plus / Sum_ext / Sum_ext_lt *)
(*     / Sum_delta / Sum_zero, used below by name).                       *)
(* --------------------------------------------------------------------- *)

Lemma Sum_0 : forall f, Sum 0 f = 0.
Proof. reflexivity. Qed.

Lemma Sum_S : forall n f, Sum (S n) f = Sum n f + f n.
Proof. reflexivity. Qed.

(* local twin of weld__M_42_v1.SpectralCeiling.qsum_scale (Sum and qsum are the same
   fixpoint, Sum_is_qsum below); kept local so section 0 needs no MRC object *)
Lemma Sum_scale : forall n (c : Q) (f : nat -> Q),
  Sum n (fun k => c * f k) == c * Sum n f.
Proof.
  induction n as [| k IH]; intros c f.
  - rewrite !Sum_0. ring.
  - rewrite !Sum_S, IH. cbv beta. ring.
Qed.

(* boolean case splits on Nat.eqb / Nat.ltb / Nat.leb, each turned into a nat fact *)
Ltac split_cmp :=
  repeat match goal with
  | [ |- context [Nat.eqb ?a ?b] ] =>
      let E := fresh "E" in
      destruct (Nat.eqb a b) eqn:E; [ apply Nat.eqb_eq in E | apply Nat.eqb_neq in E ]
  | [ |- context [Nat.ltb ?a ?b] ] =>
      let E := fresh "E" in
      destruct (Nat.ltb a b) eqn:E; [ apply Nat.ltb_lt in E | apply Nat.ltb_ge in E ]
  | [ |- context [Nat.leb ?a ?b] ] =>
      let E := fresh "E" in
      destruct (Nat.leb a b) eqn:E; [ apply Nat.leb_le in E | apply Nat.leb_gt in E ]
  end.

(* --------------------------------------------------------------------- *)
(*  1. The operator L_R applied to a node field, in IDM_Matrix's objects   *)
(* --------------------------------------------------------------------- *)

(* (L_R phi)(i) = Sum_j Lap[i,j] * phi j -- IDM_Matrix.mmul on the column vector phi *)
Definition Lvec (n : nat) (w : nat -> nat -> Q) (phi : nat -> Q) (i : nat) : Q :=
  Sum n (fun j => Lap n w i j * phi j).

Lemma Lvec_is_mmul : forall n w phi i,
  Lvec n w phi i = mmul n (Lap n w) (fun j _ => phi j) i 0%nat.
Proof. reflexivity. Qed.

(* the quadratic form <phi, L_R phi> *)
Definition qform (n : nat) (w : nat -> nat -> Q) (phi : nat -> Q) : Q :=
  Sum n (fun i => phi i * Lvec n w phi i).

(* one more node: the diagonal picks up the new weight w i n, nothing else *)
Lemma Lap_succ : forall n w i j,
  Lap (S n) w i j == Lap n w i j + (if Nat.eqb i j then w i n else 0).
Proof.
  intros n w i j. unfold Lap, deg.
  destruct (Nat.eqb i j); cbv iota; [ rewrite Sum_S; cbv beta; ring | ring ].
Qed.

Lemma Lvec_succ_lt : forall n w phi i, (i < n)%nat ->
  Lvec (S n) w phi i == Lvec n w phi i + w i n * phi i + Lap (S n) w i n * phi n.
Proof.
  intros n w phi i Hi. unfold Lvec. rewrite Sum_S. cbv beta.
  rewrite (Sum_ext n (fun j => Lap (S n) w i j * phi j)
                     (fun j => Lap n w i j * phi j
                               + (if Nat.eqb i j then w i n * phi j else 0))).
  2:{ intro j. rewrite (Lap_succ n w i j). destruct (Nat.eqb i j); cbv iota; ring. }
  rewrite Sum_plus. rewrite (Sum_delta n i (fun j => w i n * phi j) Hi). cbv beta. ring.
Qed.

(* --------------------------------------------------------------------- *)
(*  2. The path graph with unit weights: w i j = 1 iff |i - j| = 1         *)
(* --------------------------------------------------------------------- *)

Definition path_w (i j : nat) : Q :=
  if Nat.eqb (S i) j then 1 else if Nat.eqb (S j) i then 1 else 0.

Lemma path_w_sym : forall i j, path_w i j == path_w j i.
Proof. intros i j. unfold path_w. split_cmp; cbv iota; try (exfalso; lia); reflexivity. Qed.

Lemma path_w_diag0 : forall i, path_w i i == 0.
Proof. intro i. unfold path_w. split_cmp; cbv iota; try (exfalso; lia); reflexivity. Qed.

(* the two neighbours of node S i, as delta indicators *)
Lemma path_w_S : forall i j,
  path_w (S i) j == (if Nat.eqb i j then 1 else 0) + (if Nat.eqb (S (S i)) j then 1 else 0).
Proof. intros i j. unfold path_w. split_cmp; cbv iota; try (exfalso; lia); ring. Qed.

(* below the last node S k only the left neighbour k is seen *)
Lemma path_w_below : forall k j, (j < S k)%nat ->
  path_w (S k) j == (if Nat.eqb k j then 1 else 0).
Proof. intros k j Hj. unfold path_w. split_cmp; cbv iota; try (exfalso; lia); reflexivity. Qed.

Lemma path_w_below' : forall k j, (j < S k)%nat ->
  path_w j (S k) == (if Nat.eqb k j then 1 else 0).
Proof. intros k j Hj. rewrite path_w_sym. apply path_w_below. exact Hj. Qed.

(* interior degree is 2 (the d_max of the path) *)
Lemma deg_path_interior : forall n i, (S (S i) < n)%nat -> deg n path_w (S i) == 2.
Proof.
  intros n i Hi. unfold deg.
  rewrite (Sum_ext n (fun k => path_w (S i) k)
                     (fun k => (if Nat.eqb i k then 1 else 0)
                               + (if Nat.eqb (S (S i)) k then 1 else 0)))
    by (intro k; apply path_w_S).
  rewrite Sum_plus.
  rewrite (Sum_delta n i (fun _ => 1)) by lia.
  rewrite (Sum_delta n (S (S i)) (fun _ => 1)) by lia.
  cbv beta. ring.
Qed.

(* the last node S m of the path on S (S m) nodes has degree 1 *)
Lemma deg_path_last : forall m, deg (S (S m)) path_w (S m) == 1.
Proof.
  intro m. unfold deg. rewrite Sum_S. cbv beta. rewrite path_w_diag0.
  rewrite (Sum_ext_lt (S m) (fun k => path_w (S m) k) (fun k => if Nat.eqb m k then 1 else 0))
    by (intros k Hk; apply path_w_below; exact Hk).
  rewrite (Sum_delta (S m) m (fun _ => 1)) by lia.
  cbv beta. ring.
Qed.

(* --------------------------------------------------------------------- *)
(*  (a) seam_grid : the [1,-2,1] stencil IS L_R at every interior node     *)
(* --------------------------------------------------------------------- *)

Lemma Lap_path_interior_pointwise : forall n i j (phi : nat -> Q), (S (S i) < n)%nat ->
  Lap n path_w (S i) j * phi j
  == (if Nat.eqb (S i) j then 2 * phi j else 0)
     + (if Nat.eqb i j then - phi j else 0)
     + (if Nat.eqb (S (S i)) j then - phi j else 0).
Proof.
  intros n i j phi Hi.
  pose proof (deg_path_interior n i Hi) as Hd.
  unfold Lap. revert Hd. generalize (deg n path_w (S i)). intros d Hd.
  unfold path_w. split_cmp; cbv iota; try (exfalso; lia); try rewrite Hd; ring.
Qed.

Theorem seam_grid : forall (n i : nat) (phi : nat -> Q),
  (S (S i) < n)%nat ->
  Lvec n path_w phi (S i) == - (phi i - 2 * phi (S i) + phi (S (S i))).
Proof.
  intros n i phi Hi. unfold Lvec.
  rewrite (Sum_ext n (fun j => Lap n path_w (S i) j * phi j)
                     (fun j => (if Nat.eqb (S i) j then 2 * phi j else 0)
                               + (if Nat.eqb i j then - phi j else 0)
                               + (if Nat.eqb (S (S i)) j then - phi j else 0)))
    by (intro j; apply Lap_path_interior_pointwise; exact Hi).
  rewrite Sum_plus, Sum_plus.
  rewrite (Sum_delta n (S i) (fun j => 2 * phi j)) by lia.
  rewrite (Sum_delta n i (fun j => - phi j)) by lia.
  rewrite (Sum_delta n (S (S i)) (fun j => - phi j)) by lia.
  cbv beta. ring.
Qed.

(* the tape of f : Q -> Q read at spacing h from x0 : phi j = f (x0 + j h) *)
Definition sample (f : Q -> Q) (x0 h : Q) (j : nat) : Q :=
  f (x0 + inject_Z (Z.of_nat j) * h).

Lemma inject_nat_S : forall j, inject_Z (Z.of_nat (S j)) == inject_Z (Z.of_nat j) + 1.
Proof.
  intro j. rewrite Nat2Z.inj_succ. unfold Z.succ. rewrite inject_Z_plus.
  replace (inject_Z 1) with 1 by reflexivity. reflexivity.
Qed.

(* -h^2 Delta_h f = L_R phi, h^2 multiplied through: weld/M.41's D2 f x h IS
   f(x+h) - 2 f(x) + f(x-h) = h^2 * Delta_h f (x), and L_R phi at the node reading x
   is exactly its negative.  Premise: f respects Qeq (Q is a setoid; a function on
   rationals that distinguishes 2#4 from 1#2 is not a function on Q). *)
Theorem seam_grid_D2 : forall (f : Q -> Q) (x0 h : Q) (n i : nat),
  (forall a b, a == b -> f a == f b) ->
  (S (S i) < n)%nat ->
  Lvec n path_w (sample f x0 h) (S i)
    == - weld__M_41_v1.D2 f (x0 + inject_Z (Z.of_nat (S i)) * h) h.
Proof.
  intros f x0 h n i Hf Hi.
  rewrite (seam_grid n i (sample f x0 h) Hi).
  unfold weld__M_41_v1.D2, sample.
  rewrite (Hf (x0 + inject_Z (Z.of_nat (S (S i))) * h)
              (x0 + inject_Z (Z.of_nat (S i)) * h + h)).
  2:{ rewrite (inject_nat_S (S i)). ring. }
  rewrite (Hf (x0 + inject_Z (Z.of_nat i) * h)
              (x0 + inject_Z (Z.of_nat (S i)) * h - h)).
  2:{ rewrite (inject_nat_S i). ring. }
  ring.
Qed.

(* the same line in the [1,-2,1] order of weld/M.41.laplacian_stencil *)
Theorem seam_grid_stencil : forall (f : Q -> Q) (x0 h : Q) (n i : nat),
  (forall a b, a == b -> f a == f b) ->
  (S (S i) < n)%nat ->
  let x := x0 + inject_Z (Z.of_nat (S i)) * h in
  Lvec n path_w (sample f x0 h) (S i) == - (f (x - h) - (2#1) * f x + f (x + h)).
Proof.
  intros f x0 h n i Hf Hi x.
  rewrite <- (weld__M_41_v1.laplacian_stencil f x h).
  apply seam_grid_D2; assumption.
Qed.

(* finite positive control: phi = j^2 on 4 nodes, interior node 1: L phi = -(0 - 2 + 4) = -2 *)
Example seam_grid_control :
  Lvec 4 path_w (fun j => inject_Z (Z.of_nat (j * j))) 1 == - (2#1).
Proof. vm_compute. reflexivity. Qed.

(* --------------------------------------------------------------------- *)
(*  (b) seam_energy : <phi, L_R phi> = the edge ledger of squared retained  *)
(*      differences = I_form (Keystone) = B_form = energy (M.41) = form (M.42) *)
(* --------------------------------------------------------------------- *)

(* the m unit edges (k, S k, 1) of the path on S m nodes, in IDM_Keystone's edge type
   (nat * nat * Q) -- which is also weld/M.41's Edge type, definitionally *)
Fixpoint path_edges (m : nat) : list edge :=
  match m with
  | O => []
  | S k => (k, S k, 1) :: path_edges k
  end.

(* the same m edges in weld/M.42's unweighted (nat * nat) type *)
Fixpoint path_E (m : nat) : list (nat * nat) :=
  match m with
  | O => []
  | S k => (k, S k) :: path_E k
  end.

(* the edge ledger: Sum over the m edges of the squared retained difference
   (a local twin in Sum form -- equal to SpectralCeiling.form (path_E m) phi,
   weld__M_41_v1.energy (path_edges m) phi and I_form phi (path_edges m) by
   seam_energy_names; no theorem content of its own) *)
Definition edge_sq (phi : nat -> Q) (m : nat) : Q :=
  Sum m (fun i => (phi (S i) - phi i) * (phi (S i) - phi i)).

Lemma edge_sq_S : forall phi k,
  edge_sq phi (S k) = edge_sq phi k + (phi (S k) - phi k) * (phi (S k) - phi k).
Proof. reflexivity. Qed.

(* the quadratic form on one node is 0 (a single node has no edge and degree 0) *)
Lemma qform_path_one : forall phi, qform 1 path_w phi == 0.
Proof.
  intro phi. unfold qform. rewrite Sum_S, Sum_0. cbv beta.
  unfold Lvec. rewrite Sum_S, Sum_0. cbv beta.
  unfold Lap. rewrite Nat.eqb_refl. cbv iota.
  unfold deg. rewrite Sum_S, Sum_0. cbv beta. rewrite path_w_diag0. ring.
Qed.

(* (L_R phi) at the last node S m of the path on S (S m) nodes *)
Lemma Lvec_path_last : forall m phi,
  Lvec (S (S m)) path_w phi (S m) == phi (S m) - phi m.
Proof.
  intros m phi. unfold Lvec. rewrite Sum_S. cbv beta.
  rewrite (Sum_ext_lt (S m) (fun j => Lap (S (S m)) path_w (S m) j * phi j)
                            (fun j => if Nat.eqb m j then - phi j else 0)).
  2:{ intros j Hj. unfold Lap.
      assert (E : Nat.eqb (S m) j = false) by (apply Nat.eqb_neq; lia).
      rewrite E. cbv iota. rewrite (path_w_below m j Hj).
      destruct (Nat.eqb m j); cbv iota; ring. }
  rewrite (Sum_delta (S m) m (fun j => - phi j)) by lia. cbv beta.
  unfold Lap. rewrite Nat.eqb_refl. cbv iota. rewrite deg_path_last. ring.
Qed.

(* (L_R phi) at an old node i < S m when the node S m is appended *)
Lemma Lvec_path_step : forall m phi i, (i < S m)%nat ->
  Lvec (S (S m)) path_w phi i
  == Lvec (S m) path_w phi i + (if Nat.eqb m i then 1 else 0) * (phi i - phi (S m)).
Proof.
  intros m phi i Hi.
  rewrite (Lvec_succ_lt (S m) path_w phi i Hi).
  unfold Lap.
  assert (E : Nat.eqb i (S m) = false) by (apply Nat.eqb_neq; lia).
  rewrite E. cbv iota. rewrite (path_w_below' m i Hi). ring.
Qed.

(* appending one edge adds exactly one squared retained difference *)
Lemma qform_path_step : forall m phi,
  qform (S (S m)) path_w phi
  == qform (S m) path_w phi + (phi (S m) - phi m) * (phi (S m) - phi m).
Proof.
  intros m phi. unfold qform. rewrite Sum_S. cbv beta.
  rewrite (Sum_ext_lt (S m) (fun i => phi i * Lvec (S (S m)) path_w phi i)
                            (fun i => phi i * Lvec (S m) path_w phi i
                                      + (if Nat.eqb m i then phi i * (phi i - phi (S m)) else 0))).
  2:{ intros i Hi. rewrite (Lvec_path_step m phi i Hi).
      destruct (Nat.eqb m i); cbv iota; ring. }
  rewrite Sum_plus.
  rewrite (Sum_delta (S m) m (fun i => phi i * (phi i - phi (S m)))) by lia.
  rewrite Lvec_path_last. cbv beta. ring.
Qed.

(* <phi, L_R phi> on the path with m edges = the edge ledger, every m.
   OCCURRENCE (fixer pass 2026-09-18), not a new object: the proposals-lane row
   PROP-P3-LRS-LAPLACIAN-PSD-CLOSURE-01 states x^T L x == sum_{i<j} w_ij (x_i - x_j)^2
   for the same Lap at general N (w symmetric, zero diagonal); this is that statement
   under w := path_w.  Own readout kept (independent proof by induction on m). *)
Theorem seam_energy_qform : forall m phi, qform (S m) path_w phi == edge_sq phi m.
Proof.
  intros m phi. induction m as [| k IH].
  - unfold edge_sq. rewrite Sum_0. apply qform_path_one.
  - rewrite qform_path_step, IH, edge_sq_S. reflexivity.
Qed.

(* the edge ledger under its registered names *)
Lemma I_edge_unit : forall phi i j, I_edge phi (i, j, 1) == (phi i - phi j) * (phi i - phi j).
Proof. intros phi i j. unfold I_edge. cbv iota. ring. Qed.

Lemma I_form_path : forall phi m, I_form phi (path_edges m) == edge_sq phi m.
Proof.
  intros phi m. induction m as [| k IH].
  - reflexivity.
  - change (I_form phi (path_edges (S k)))
      with (I_edge phi (k, S k, 1) + I_form phi (path_edges k)).
    rewrite I_edge_unit, IH, edge_sq_S. ring.
Qed.

Lemma term41_unit : forall (x : nat -> Q) i j,
  weld__M_41_v1.term x (i, j, 1) == (x i - x j) * (x i - x j).
Proof.
  intros x i j.
  change (weld__M_41_v1.term x (i, j, 1)) with (1 * ((x i - x j) * (x i - x j))).
  ring.
Qed.

Lemma energy41_path : forall (x : nat -> Q) m,
  weld__M_41_v1.energy (path_edges m) x == edge_sq x m.
Proof.
  intros x m. induction m as [| k IH].
  - reflexivity.
  - change (weld__M_41_v1.energy (path_edges (S k)) x)
      with (weld__M_41_v1.term x (k, S k, 1) + weld__M_41_v1.energy (path_edges k) x).
    rewrite term41_unit, IH, edge_sq_S. ring.
Qed.

Lemma ediff42_pair : forall (x : nat -> Q) a b,
  SpectralCeiling.ediff x (a, b) = x a - x b.
Proof. reflexivity. Qed.

Lemma form42_path : forall (x : nat -> Q) m,
  SpectralCeiling.form (path_E m) x == edge_sq x m.
Proof.
  intros x m. induction m as [| k IH].
  - reflexivity.
  - change (SpectralCeiling.form (path_E (S k)) x)
      with (SpectralCeiling.ediff x (k, S k) * SpectralCeiling.ediff x (k, S k)
            + SpectralCeiling.form (path_E k) x).
    rewrite ediff42_pair, IH, edge_sq_S. ring.
Qed.

(* (b) as stated: <phi, L_R phi> = I_form phi (path edges), the retained information *)
Theorem seam_energy : forall m phi,
  qform (S m) path_w phi == I_form phi (path_edges m).
Proof. intros m phi. rewrite seam_energy_qform, I_form_path. reflexivity. Qed.

(* one number, five registered names *)
Theorem seam_energy_names : forall m phi,
  qform (S m) path_w phi == I_form phi (path_edges m)
  /\ I_form phi (path_edges m) == B_form phi (path_edges m)
  /\ B_form phi (path_edges m) == weld__M_41_v1.energy (path_edges m) phi
  /\ weld__M_41_v1.energy (path_edges m) phi == SpectralCeiling.form (path_E m) phi
  /\ SpectralCeiling.form (path_E m) phi == edge_sq phi m.
Proof.
  intros m phi.
  pose proof (seam_energy m phi) as H1.
  pose proof (keystone_B_eq_I phi (path_edges m)) as H2.
  pose proof (I_form_path phi m) as H3.
  pose proof (energy41_path phi m) as H4.
  pose proof (form42_path phi m) as H5.
  repeat split.
  - exact H1.
  - symmetry. exact H2.
  - rewrite H2, H3, H4. reflexivity.
  - rewrite H4, H5. reflexivity.
  - exact H5.
Qed.

(* --------------------------------------------------------------------- *)
(*  (c) seam_box : I(phi + e_i) - I(phi) = 2 (L_R phi)_i + L_ii            *)
(* --------------------------------------------------------------------- *)

(* the unit bump at node i is IDM_Matrix's identity column mid i *)
Definition bump (phi : nat -> Q) (i : nat) : nat -> Q := fun j => phi j + mid i j.

Lemma Lvec_bump : forall n w phi i a, (i < n)%nat ->
  Lvec n w (bump phi i) a == Lvec n w phi a + Lap n w a i.
Proof.
  intros n w phi i a Hi. unfold Lvec, bump, mid.
  rewrite (Sum_ext n (fun j => Lap n w a j * (phi j + (if Nat.eqb i j then 1 else 0)))
                     (fun j => Lap n w a j * phi j + (if Nat.eqb i j then Lap n w a j else 0)))
    by (intro j; destruct (Nat.eqb i j); cbv iota; ring).
  rewrite Sum_plus. rewrite (Sum_delta n i (fun j => Lap n w a j) Hi). cbv beta. ring.
Qed.

(* the finite-difference gradient of the retained information, exact, for ANY
   symmetric weighted graph (L_R/M.20.v1 laplacian_symmetric is the one step) *)
Theorem seam_box : forall n (w : nat -> nat -> Q) (phi : nat -> Q) (i : nat),
  (forall a b, w a b == w b a) ->
  (i < n)%nat ->
  qform n w (bump phi i) - qform n w phi == 2 * Lvec n w phi i + Lap n w i i.
Proof.
  intros n w phi i Hsym Hi. unfold qform.
  rewrite (Sum_ext n (fun a => bump phi i a * Lvec n w (bump phi i) a)
                     (fun a => phi a * Lvec n w phi a
                               + Lap n w i a * phi a
                               + (if Nat.eqb i a then Lvec n w phi a else 0)
                               + (if Nat.eqb i a then Lap n w i a else 0))).
  2:{ intro a. rewrite (Lvec_bump n w phi i a Hi). unfold bump, mid.
      rewrite (laplacian_symmetric n w Hsym a i). unfold transpose.
      destruct (Nat.eqb i a); cbv iota; ring. }
  rewrite Sum_plus, Sum_plus, Sum_plus.
  rewrite (Sum_delta n i (fun a => Lvec n w phi a) Hi).
  rewrite (Sum_delta n i (fun a => Lap n w i a) Hi).
  cbv beta. unfold Lvec. ring.
Qed.

(* the same on the path, with I the retained information of Keystone/M.03.v1 *)
Corollary seam_box_path : forall m (phi : nat -> Q) (i : nat), (i < S m)%nat ->
  I_form (bump phi i) (path_edges m) - I_form phi (path_edges m)
  == 2 * Lvec (S m) path_w phi i + Lap (S m) path_w i i.
Proof.
  intros m phi i Hi.
  rewrite <- (seam_energy m (bump phi i)), <- (seam_energy m phi).
  apply seam_box; [ apply path_w_sym | exact Hi ].
Qed.

(* --------------------------------------------------------------------- *)
(*  (d) seam_ceiling : no exact Rayleigh pair of the path exceeds 2 d_max = 4 *)
(* --------------------------------------------------------------------- *)

Lemma path_E_nodes : forall m e, In e (path_E m) -> (fst e < m)%nat /\ (snd e <= m)%nat.
Proof.
  induction m as [| k IH]; intros e H.
  - destruct H.
  - destruct H as [<- | H].
    + simpl. lia.
    + destruct (IH e H). lia.
Qed.

Lemma path_nodes_ok : forall m, SpectralCeiling.nodes_ok (S m) (path_E m).
Proof. intros m e He. destruct (path_E_nodes m e He). lia. Qed.

Lemma deg42_cons : forall e E i,
  SpectralCeiling.deg (e :: E) i = SpectralCeiling.share e i + SpectralCeiling.deg E i.
Proof. reflexivity. Qed.

Lemma share42_pair : forall a b i,
  SpectralCeiling.share (a, b) i = SpectralCeiling.ind a i + SpectralCeiling.ind b i.
Proof. reflexivity. Qed.

(* the exact degree of node i in the path with m edges: [i < m] + [0 < i <= m] *)
Lemma deg_path_E : forall m i,
  SpectralCeiling.deg (path_E m) i
  == (if Nat.ltb i m then 1 else 0)
     + (if Nat.ltb 0 i then (if Nat.leb i m then 1 else 0) else 0).
Proof.
  induction m as [| k IH]; intro i.
  - change (SpectralCeiling.deg (path_E 0) i) with 0.
    split_cmp; cbv iota; try (exfalso; lia); ring.
  - change (path_E (S k)) with ((k, S k) :: path_E k).
    rewrite deg42_cons, share42_pair, IH. unfold SpectralCeiling.ind.
    split_cmp; cbv iota; try (exfalso; lia); ring.
Qed.

Lemma deg_path_E_le2 : forall m i, SpectralCeiling.deg (path_E m) i <= 2.
Proof. intros m i. rewrite deg_path_E. split_cmp; cbv iota; lra. Qed.

(* weld/M.42.v1 rayleigh_ceiling instantiated on the path: d_max = 2, so lam <= 4 *)
Theorem seam_ceiling : forall m (x : nat -> Q) (lam : Q),
  SpectralCeiling.form (path_E m) x == lam * SpectralCeiling.norm2 (S m) x ->
  0 < SpectralCeiling.norm2 (S m) x ->
  lam <= 4.
Proof.
  intros m x lam Heig Hpos.
  pose proof (SpectralCeiling.rayleigh_ceiling (path_E m) (S m) x lam 2
                (path_nodes_ok m) (fun i _ => deg_path_E_le2 m i) Heig Hpos) as H.
  lra.
Qed.

(* IDM_Matrix's Sum and weld/M.42's qsum are the same recursion *)
Lemma Sum_is_qsum : forall n f, Sum n f = SpectralCeiling.qsum n f.
Proof.
  induction n as [| k IH]; intro f.
  - reflexivity.
  - change (Sum k f + f k = SpectralCeiling.qsum k f + f k). rewrite IH. reflexivity.
Qed.

(* the same ceiling for an exact eigenpair of the IDM_Matrix Laplacian on the path *)
Theorem seam_ceiling_Lap : forall m (x : nat -> Q) (lam : Q),
  (forall i, (i < S m)%nat -> Lvec (S m) path_w x i == lam * x i) ->
  0 < Sum (S m) (fun i => x i * x i) ->
  lam <= 4.
Proof.
  intros m x lam Heig Hpos.
  apply (seam_ceiling m x lam).
  - rewrite form42_path. rewrite <- seam_energy_qform. unfold qform.
    rewrite (Sum_ext_lt (S m) (fun i => x i * Lvec (S m) path_w x i)
                              (fun i => lam * (x i * x i)))
      by (intros i Hi; rewrite (Heig i Hi); ring).
    rewrite Sum_scale. unfold SpectralCeiling.norm2.
    (* Sum and qsum are the same fixpoint (Sum_is_qsum): convertible, so reflexivity *)
    reflexivity.
  - unfold SpectralCeiling.norm2. exact Hpos.
Qed.

(* the design's lambda(Delta_h) <= 2 d_max / h^2, as a positive-scale rewrite with h^2
   multiplied through: if h^2 mu is an exact Rayleigh value of the path then h^2 mu <= 4.
   NEW DERIVATION / PROPOSAL -- not yet in Toledo (weld/M.42's registered statement has
   no h; this is its occurrence under the seam -h^2 Delta_h := L_R^(h)). *)
Corollary seam_ceiling_scaled : forall m (x : nat -> Q) (lam h mu : Q),
  SpectralCeiling.form (path_E m) x == lam * SpectralCeiling.norm2 (S m) x ->
  0 < SpectralCeiling.norm2 (S m) x ->
  h * h * mu == lam ->
  h * h * mu <= 4.
Proof.
  intros m x lam h mu Heig Hpos Hh. rewrite Hh. apply (seam_ceiling m x lam); assumption.
Qed.

(* --------------------------------------------------------------------- *)
(*  In-file readouts (the scratch file repeats every line from the .vo)   *)
(* --------------------------------------------------------------------- *)
Print Assumptions seam_grid.
Print Assumptions seam_grid_D2.
Print Assumptions seam_grid_stencil.
Print Assumptions seam_grid_control.
Print Assumptions seam_energy_qform.
Print Assumptions seam_energy.
Print Assumptions seam_energy_names.
Print Assumptions seam_box.
Print Assumptions seam_box_path.
Print Assumptions seam_ceiling.
Print Assumptions seam_ceiling_Lap.
Print Assumptions seam_ceiling_scaled.
Print Assumptions Lvec_is_mmul.
Print Assumptions deg_path_interior.
Print Assumptions deg_path_last.
Print Assumptions deg_path_E.
Print Assumptions deg_path_E_le2.
Print Assumptions path_nodes_ok.
Print Assumptions Sum_is_qsum.

(* In-file axiom-freedom readouts for every theorem-like statement of this file
   (added 2026-09-18 after an independent pre-merge review found the readouts
   had been taken in scratch files only). Expected output for each line:
   "Closed under the global context". *)
Print Assumptions Sum_0.
Print Assumptions Sum_S.
Print Assumptions Sum_scale.
Print Assumptions Lap_succ.
Print Assumptions Lvec_succ_lt.
Print Assumptions path_w_sym.
Print Assumptions path_w_diag0.
Print Assumptions path_w_S.
Print Assumptions path_w_below.
Print Assumptions path_w_below'.
Print Assumptions Lap_path_interior_pointwise.
Print Assumptions inject_nat_S.
Print Assumptions edge_sq_S.
Print Assumptions qform_path_one.
Print Assumptions Lvec_path_last.
Print Assumptions Lvec_path_step.
Print Assumptions qform_path_step.
Print Assumptions I_edge_unit.
Print Assumptions I_form_path.
Print Assumptions term41_unit.
Print Assumptions energy41_path.
Print Assumptions ediff42_pair.
Print Assumptions form42_path.
Print Assumptions Lvec_bump.
Print Assumptions path_E_nodes.
Print Assumptions deg42_cons.
Print Assumptions share42_pair.
