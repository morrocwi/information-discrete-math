# formal/ — local machine-checked witnesses (Coq 8.20)

Axiom-free Coq proofs of the finite (`Th_coqc`) claims that live natively in this repository (the rest
of the `Th_coqc` corpus is external: `research_universal_solver`, `readout_genesis`, `readout_universe`).

## Reproduce

```
cd formal
coqc -q IDM_Keystone.v
coqc -q IDM_Bridge.v
coqc -q IDM_FiniteWitnesses.v
coqc -q IDM_FiniteWitnesses2.v
printf 'Require Import IDM_FiniteWitnesses.\nPrint Assumptions kuratowski_pair_inj.\nPrint Assumptions handshake_lemma.\nPrint Assumptions pigeonhole.\nPrint Assumptions finite_yoneda.\nPrint Assumptions semiring_distrib.\n' > _chk.v
coqc -q _chk.v   # every result prints "Closed under the global context" = axiom-free
rm -f _chk.v *.vo *.glob *.vos *.vok
```

## Witnesses → textbook claim

| lemma | textbook | statement |
|---|---|---|
| `keystone_B_eq_I` (`IDM_Keystone.v`) | §5.1 Th 5.1 | **keystone** `B(Φ,Φ)=I(Φ)`: `ΦᵀL_RΦ = Σ_edges w·(Φi−Φj)²` |
| `keystone_nonneg` (`IDM_Keystone.v`) | §5.1 | `L_R` positive semidefinite (retained metric is a seminorm) |
| `kuratowski_pair_inj` | §10.1 Th 10.1 | Kuratowski ordered-pair injectivity `(a,b)=(c,d) ⟺ a=c ∧ b=d` |
| `handshake_lemma` | §15.2 | endpoint multiset of an edge list has length `2·|E|` (Σ deg = 2|E|) |
| `pigeonhole` | §15.3 | a `NoDup` list of values `< n` has length `≤ n` |
| `finite_yoneda` | §17.2 | maps agreeing on every point of a finite domain have equal readout-vectors |
| `semiring_distrib` | §12.2 | `a·(b+c) = a·b + a·c` on `D≅ℕ` |
| `no_infinite_readout` (`IDM_FiniteWitnesses2.v`) | §10.2 Th 10.5 | every readout list is finite (no infinite inhabitant) |
| `tape_count_succ` (`IDM_FiniteWitnesses2.v`) | §10.2 Th 10.4 | a σ-generated tape strictly grows ⇒ no terminal stage |
| `same_set_same_size` (`IDM_FiniteWitnesses2.v`) | §10.2 Th 10.3 | NoDup + same members ⇒ equal count (equinumerosity) |
| `lagrange_order_div` (`IDM_FiniteWitnesses2.v`) | §12.3 | order `n/gcd(g,n)` divides `|ℤ_n|=n` |
| `FTCC_exact` / `FTCC_eps_exact` (`IDM_Bridge.v`) | §20.2 | continuum-maya exact core: `I_ε(D_ε f)=f[N]−f[0]` (zero residue) |

All checked axiom-free under Coq 8.20 (`Print Assumptions` = *Closed under the global context*).
