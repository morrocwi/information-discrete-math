# formal/ — local machine-checked witnesses (Coq 8.20)

Axiom-free Coq proofs of the finite (`Th_coqc`) claims that live natively in this repository (the rest
of the `Th_coqc` corpus is external: `research_universal_solver`, `readout_genesis`, `readout_universe`).

## Reproduce

**One command:** `bash formal/verify.sh` — compiles every witness and confirms all 127 theorems are axiom-free (*Closed under the global context*); exits 0 iff all pass.

### Manual

```
cd formal
coqc -q IDM_Keystone.v
coqc -q IDM_Bridge.v
coqc -q IDM_FiniteWitnesses.v
coqc -q IDM_FiniteWitnesses2.v
coqc -q IDM_Logic.v
coqc -q IDM_FiniteWitnesses3.v
coqc -q IDM_Matrix.v
coqc -q IDM_Harvest.v
coqc -q IDM_Calculus.v
printf 'Require Import IDM_FiniteWitnesses.\nPrint Assumptions kuratowski_pair_inj.\nPrint Assumptions handshake_lemma.\nPrint Assumptions pigeonhole.\nPrint Assumptions finite_yoneda.\nPrint Assumptions semiring_distrib.\n' > _chk.v
coqc -q _chk.v   # every result prints "Closed under the global context" = axiom-free
rm -f _chk.v *.vo *.glob *.vos *.vok
```

## Witnesses → textbook claim

| lemma | textbook | statement |
|---|---|---|
| `keystone_B_eq_I` (`IDM_Keystone.v`) | §5.1 Th 5.1 | **keystone** `B(Φ,Φ)=I(Φ)`: `ΦᵀL_RΦ = Σ_edges w·(Φi−Φj)²` |
| `keystone_nonneg` (`IDM_Keystone.v`) | §5.1 | `L_R` positive semidefinite (retained metric is a seminorm) |
| `relaxation_dissipation` (`IDM_Keystone.v`) | §21.3 | no-blow-up: `d/dt‖I‖²=−(2/τ)B(I,I)≤0` for `τ dI/dt+L_R I=S` |
| `kuratowski_pair_inj` | §10.1 Th 10.1 | Kuratowski ordered-pair injectivity `(a,b)=(c,d) ⟺ a=c ∧ b=d` |
| `handshake_lemma` | §15.2 | endpoint multiset of an edge list has length `2·|E|` (Σ deg = 2|E|) |
| `pigeonhole` | §15.3 | a `NoDup` list of values `< n` has length `≤ n` |
| `finite_yoneda` | §17.2 | maps agreeing on every point of a finite domain have equal readout-vectors |
| `semiring_distrib` | §12.2 | `a·(b+c) = a·b + a·c` on `D≅ℕ` |
| `no_infinite_readout` (`IDM_FiniteWitnesses2.v`) | §10.2 Th 10.5 | every readout list is finite (no infinite inhabitant) |
| `tape_count_succ` (`IDM_FiniteWitnesses2.v`) | §10.2 Th 10.4 | a σ-generated tape strictly grows ⇒ no terminal stage |
| `same_set_same_size` (`IDM_FiniteWitnesses2.v`) | §10.2 Th 10.3 | NoDup + same members ⇒ equal count (equinumerosity) |
| `lagrange_order_div` (`IDM_FiniteWitnesses2.v`) | §12.3 | order `n/gcd(g,n)` divides `|ℤ_n|=n` |
| `finite_satisfaction_dec` (`IDM_Logic.v`) | §10.3 Th 10.6 | finite Tarski satisfaction / model-checking is decidable |
| `rdl_non_explosion` (`IDM_Logic.v`) | §10.4 / Part I | Belnap–Dunn countermodel: `p∧¬p` designated, `q` not (non-explosion) |
| `no_fibonacci_integer_dim` (`IDM_FiniteWitnesses3.v`) | §4.4 Cor 4.1 | `d²=1+d` has no integer solution (φ not an ordinary dim) |
| `cauchy_schwarz_2` (`IDM_FiniteWitnesses3.v`) | §16.2 | Cauchy–Schwarz over ℚ (2-D, Lagrange identity) |
| `measure_additive` (`IDM_FiniteWitnesses3.v`) | §16.1 | μ_λ finitely additive (disjoint counts add) |
| `ring_distrib_Z` (`IDM_FiniteWitnesses3.v`) | §12.2 | ℤ ring distributivity (+ and −) |
| `aut_assoc`/`aut_id_*`/`aut_inv_*` (`IDM_FiniteWitnesses3.v`) | §12.1 | readout automorphisms form a group |
| `mid_left`/`transpose_mmul`/… (`IDM_Matrix.v`) | §13 | discrete matrix algebra over ℚ (from scratch) |
| `laplacian_symmetric`/`_rowsum_zero`/`_ones_in_kernel` (`IDM_Matrix.v`) | §15.2 | L_R symmetric; row-sums 0; constants ∈ ker L_R (connectivity) |
| `twirl_image_scalar`/`twirl_idempotent` (`IDM_Matrix.v`) | §13.4 | the averaging/Reynolds projector: idempotent, image = 1-D scalar line (parameter reduction) |
| `sym_skew_reconstruct`/`skew_diag_zero` (`IDM_Harvest.v`) | §13 | every operator = self-adjoint (metric) + skew part; skew diagonal = 0 |
| `odd_from_cyclic_closure`/`least_nontrivial_odd_is_three` (`IDM_Harvest.v`) | §4.4/§II | cyclic start-independence ⇒ k odd ⇒ least 3 |
| `repeated_event_zero` (`IDM_Harvest.v`) | — | a self-cancelling readout is null (C=−C⇒C=0) |
| `delta_sum`/`delta_scalar`/`delta_product` (`IDM_Calculus.v`) | §8.2/§10.5 Th 10.8 | exact D_ε rules, zero O(ε) residue |
| `Deps_sum`/`Deps_product` (`IDM_Calculus.v`) | §10.5 | the ε-form (ε cancels exactly) |
| `FTCC_telescope`/`summation_by_parts` (`IDM_Calculus.v`) | §8.2 | exact discrete FTC + integration by parts |
| `FTCC_exact` / `FTCC_eps_exact` (`IDM_Bridge.v`) | §20.2 | continuum-maya exact core: `I_ε(D_ε f)=f[N]−f[0]` (zero residue) |
| `bit_extraction_exact` / `profile_injective` (`IDM_DeclarationBound.v`) | Declaration Bound | Sturm profile `i↦i+b_i` recovers every bit; distinct strings ⇒ distinct profiles (irreducible fooling family) |
| `bcube_length` / `bcube_nodup` (`IDM_DeclarationBound.v`) | Declaration Bound | the n-bit cube has exactly `2ⁿ` distinct strings (counting backbone) |
| `deferred_record_bits` (`IDM_DeclarationBound.v`) | Declaration Bound | **deferred lower bound**: any scheme keeping a distinct record per n-bit string must retain `≥ n` bits for some string (pigeonhole over the `<2ⁿ` short records) — Θ(n) |
| `declared_forgets_tail` / `declaration_separation` (`IDM_DeclarationBound.v`) | Declaration Bound | declared regime depends only on the prefix up to the threshold ⇒ single accumulator, Θ(1); the separation deferred-Θ(n) vs declared-Θ(1) |

All checked axiom-free under Coq 8.20 (`Print Assumptions` = *Closed under the global context*).

The **Declaration Bound** row-set formalises the finite combinatorial core of the retained-state
separation (a Sturm threshold query costs Θ(1) retained state when *declared in advance* but Θ(n)
when *deferred*). The one spectral ingredient (the fooling family's Sturm count equals `i+b_i`) is
verified numerically in [`demos/verify_declaration_bound.py`](../demos/verify_declaration_bound.py),
not re-derived in Coq — an honest fence, stated in the file header.
