(* ===================================================================== *)
(*  IDM_Bridge.v — the exact formal core of the CONTINUUM-MAYA BRIDGE       *)
(*  (Part XX): the discrete Fundamental Theorem of the Causal Calculus      *)
(*  (FTCC).  I_ε ∘ D_ε = f[N] − f[0]  EXACTLY (zero residue), so the        *)
(*  continuum's Fundamental Theorem of Calculus is recovered as a readout   *)
(*  of a finite discrete telescoping sum — no limit is taken.               *)
(*                                                                          *)
(*  Developed by Yaoharee Lahtee. Coq 8.20, over ℚ, axiom-free              *)
(*  (Print Assumptions = "Closed under the global context").               *)
(* ===================================================================== *)

Require Import List.
Require Import QArith.
Import ListNotations.
Open Scope Q_scope.

Definition seqf := nat -> Q.

(* Backward causal difference scaled by ε: (D_ε f)[n]·ε = f[n] − f[n−1].
   We work with the ε-cleared increment Δf[n] = f(S n) − f(n), since I_ε
   multiplies each D_ε by ε and the ε cancels exactly (shown below). *)
Definition delta (f : seqf) (n : nat) : Q := f (S n) - f n.

(* Aggregation I_ε of the increments over the first N steps = telescoping sum. *)
Fixpoint agg (f : seqf) (N : nat) : Q :=
  match N with
  | O => 0
  | S k => agg f k + delta f k
  end.

(* FTCC (exact, zero residue): I_ε(D_ε f) over [0,N] = f[N] − f[0]. *)
Theorem FTCC_exact :
  forall (f : seqf) (N : nat), agg f N == f N - f 0%nat.
Proof.
  intros f N. induction N as [| k IH]; simpl.
  - ring.
  - unfold delta. rewrite IH. ring.
Qed.

(* The ε-form, honest about the cancellation: with a declared nonzero
   resolution ε, D_ε f[n] = (f n − f (n−1))/ε and I_ε g[N] = ε·Σ g, so the
   ε cancels and the exact result stands for every ε ≠ 0. *)
Definition Deps (f : seqf) (eps : Q) (n : nat) : Q := (f (S n) - f n) / eps.
Fixpoint Ieps (g : nat -> Q) (eps : Q) (N : nat) : Q :=
  match N with O => 0 | S k => Ieps g eps k + eps * g k end.

Theorem FTCC_eps_exact :
  forall (f : seqf) (eps : Q) (N : nat),
    ~ eps == 0 -> Ieps (Deps f eps) eps N == f N - f 0%nat.
Proof.
  intros f eps N Hne. induction N as [| k IH]; simpl.
  - ring.
  - rewrite IH. unfold Deps.
    (* eps * ((f(Sk)-f k)/eps) = f(Sk) - f k *)
    field_simplify_eq; [ ring | exact Hne ].
Qed.

(* Faithfulness, exact rung: on a telescoping (exact) discrete input the
   bridge value Λ = agg equals the classical net change f[N]−f[0] with NO
   approximation — the continuum FTC as a readout of the discrete.  The
   general Λ (limits/integrals via A8-stable acceleration) is validated
   numerically at 100/100 in Appendix E; this is its exact, machine-checked
   core. *)
Corollary bridge_faithful_exact_core :
  forall f N, agg f N == f N - f 0%nat.
Proof. exact FTCC_exact. Qed.
