(* ===================================================================== *)
(*  IDM_Calculus.v — the EXACT discrete-calculus rules (Part VIII / §10.5    *)
(*  Th 10.8), machine-checked axiom-free over ℚ.  These are the genuinely    *)
(*  new results: in the causal / secant form the D_ε rules are EXACT finite  *)
(*  identities with ZERO O(ε) residue — no Reals, no limit.                  *)
(*  Coq 8.20, Closed under the global context. Yaoharee Lahtee.             *)
(*                                                                          *)
(*   delta_sum      D_ε(f+g)   = D_εf + D_εg                                 *)
(*   delta_scalar   D_ε(c·f)   = c·D_εf                                      *)
(*   delta_product  D_ε(f·g)[n] = f[n+1]·D_εg[n] + g[n]·D_εf[n]  (causal)     *)
(*   Deps_*         the same with an explicit nonzero resolution ε           *)
(*   FTCC_telescope I_ε(D_ε f) = f[N] − f[0]  (exact accumulation)           *)
(* ===================================================================== *)

Require Import QArith.
Open Scope Q_scope.

Definition seqf := nat -> Q.

(* ε-cleared increment Δf[n] = f[n+1] − f[n] (the secant numerator) *)
Definition Delta (f : seqf) (n : nat) : Q := f (S n) - f n.

(* sum rule — exact *)
Theorem delta_sum : forall f g n, Delta (fun k => f k + g k) n == Delta f n + Delta g n.
Proof. intros f g n. unfold Delta. ring. Qed.

(* scalar rule — exact *)
Theorem delta_scalar : forall (c : Q) f n, Delta (fun k => c * f k) n == c * Delta f n.
Proof. intros c f n. unfold Delta. ring. Qed.

(* causal PRODUCT rule — exact, zero residue (the secant across the actual jump) *)
Theorem delta_product :
  forall f g n, Delta (fun k => f k * g k) n == f (S n) * Delta g n + g n * Delta f n.
Proof. intros f g n. unfold Delta. ring. Qed.

(* ---- with an explicit declared resolution ε ≠ 0 (the ε cancels exactly) ---- *)
Definition Deps (f : seqf) (eps : Q) (n : nat) : Q := (f (S n) - f n) / eps.

Theorem Deps_sum :
  forall f g eps n, ~ eps == 0 ->
    Deps (fun k => f k + g k) eps n == Deps f eps n + Deps g eps n.
Proof. intros f g eps n Hne. unfold Deps. field. exact Hne. Qed.

Theorem Deps_product :
  forall f g eps n, ~ eps == 0 ->
    Deps (fun k => f k * g k) eps n == f (S n) * Deps g eps n + g n * Deps f eps n.
Proof. intros f g eps n Hne. unfold Deps. field. exact Hne. Qed.

(* ---- FTCC: aggregation of the increments telescopes EXACTLY ---- *)
Fixpoint Agg (f : seqf) (N : nat) : Q :=
  match N with O => 0 | S k => Agg f k + Delta f k end.

Theorem FTCC_telescope : forall f N, Agg f N == f N - f 0%nat.
Proof.
  intros f N. induction N as [| k IH]; simpl.
  - ring.
  - unfold Delta. rewrite IH. ring.
Qed.

(* plain prefix sum  Σ_{k<N} f k, and its telescoping *)
Fixpoint PSum (f : seqf) (N : nat) : Q :=
  match N with O => 0 | S k => PSum f k + f k end.

Lemma PSum_ext : forall f g N, (forall n, f n == g n) -> PSum f N == PSum g N.
Proof. intros f g N H. induction N; simpl; [ reflexivity | rewrite IHN, H; reflexivity ]. Qed.

(* Σ_{k<N} Δh[k] = h[N] − h[0] (telescoping — Agg is exactly this prefix sum of Δ) *)
Lemma PSum_delta_telescope : forall h N, PSum (fun k => Delta h k) N == h N - h 0%nat.
Proof.
  intros h N. induction N as [| k IH]; simpl.
  - ring.
  - unfold Delta. rewrite IH. ring.
Qed.

(* SUMMATION BY PARTS, exact: Σ (f[k+1]Δg[k] + g[k]Δf[k]) = f[N]g[N] − f[0]g[0]. *)
Theorem summation_by_parts :
  forall f g N,
    PSum (fun n => f (S n) * Delta g n + g n * Delta f n) N
      == f N * g N - f 0%nat * g 0%nat.
Proof.
  intros f g N.
  rewrite (PSum_ext _ (fun k => Delta (fun m => f m * g m) k))
    by (intro n; symmetry; apply delta_product).
  apply (PSum_delta_telescope (fun m => f m * g m)).
Qed.
Close Scope Q_scope.
