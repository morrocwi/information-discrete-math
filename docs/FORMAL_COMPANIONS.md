# Formal companions — the machine-checked ecosystem this repo sits in

`information-discrete-math` (IDM) is the CAS + textbook + local Coq arc. Its `Th_coqc` corpus is
deliberately *partial by design* (`formal/README.md`): most of the framework's machine-checked
claims live in **sibling repositories**, each a self-contained Coq artifact. This document is the
single map of that ecosystem — which sibling proves what, and, for the one that backs a discipline
the IDM kernel *runs on*, exactly how the code and the proof line up.

> **Horizontal, not hierarchical.** These siblings are *witnesses we cite*, authored inside the same
> program (same author, `Yaoharee Lahtee`) — never an outside authority conferring legitimacy. A
> citation here means "a machine checked this statement", nothing more and nothing less. Evaluate
> each on its own tier; never promote a companion's result into an IDM claim it does not license.

## The sibling map

| Sibling repo | Machine-checks | Relation to IDM |
|---|---|---|
| **`research_universal_solver`** (`anse-spine`) | the spine PDE theorems, the retained-difference root `δ_R` arc | the universal solver backbone IDM's philosophy floor is stated against |
| **`readout_genesis`** | the English Genesis core (number ladder `D→ℤ→ℚ→ℝ`, readout-not-truth) | the genesis of number IDM chapters II–III restate |
| **`readout_universe`** | the Philosophy & Logic textbook (C1–C7 verified) | the RDL / logic floor IDM chapter I restates |
| **`zero-readout-certifies`** | the **zero-fibre** of the retained-difference operator + the **typed reader-state** separation | see below — the published companion to IDM's own keystone (§IV) and the machine-checked floor under IDM's **HOLD discipline** |

`zero-readout-certifies` — v1.0.0, Coq 8.20 / Rocq 9.2, 38 audited results all *Closed under the
global context*, published with DOI [`10.5281/zenodo.21665100`](https://doi.org/10.5281/zenodo.21665100)
(code MIT, text CC BY 4.0). Verified locally here: `make verify` in that repo reports
`verified 38 audited results with no additional global assumptions`.

## Why `zero-readout-certifies` is the one that matters most for IDM

IDM already proves the **keystone identity** locally — `formal/IDM_Keystone.v`:
`keystone_B_eq_I` (`ΦᵀL_RΦ = Σ w(Φ_i−Φ_j)²`) and `keystone_nonneg` (`L_R` PSD). The companion
extends that same operator in two directions IDM's local arc does **not** cover, and publishes them:

### 1. The zero fibre (extends §IV of `THEOREM.md`)

For strictly positive weights,

```
I_g(Φ) = 0  ⟺  Φ_i = Φ_j on every edge  ⟺  Φ constant on every connected component.
```

Companion witnesses: `keystone_zero_iff_edge` (the edgewise biconditional), `keystone_zero_iff_component`
(the connected-component form), plus the zero-locus structure `kernel_zero` / `kernel_add` /
`kernel_scale` (it is a ℚ-subspace) and `indist_refl` / `indist_sym` / `indist_trans` (indistinguishability
is an equivalence relation). The hypotheses are shown to be load-bearing by executable boundary
witnesses — a zero-weight edge or a disconnected declaration makes zero *not* imply constancy
(`zero_weight_edge_*`, `disconnected_*`). **Interpretive reading (Dr):** a legitimate zero readout of
`L_R` certifies exactly that the declared comparison structure *cannot distinguish* the compared
states — zero is the failure locus of retained distinction, not an absence of value.

#### Third arrival — the same indistinguishability kernel, reached again (Dr: coherence, not new depth)

A third machine-checked sibling arrives at the *same* structure from a different framing. In
`readout_genesis`, **`InfoTrueRecordUnreadable`** (`formal/InfoTrueRecordUnreadable_attempt.v`,
`Th_coqc` — `coqc` here reports *Closed under the global context* for all three lemmas) proves, for
**any** readout `O`,

```coq
no_decoder_recovers_state : forall X R (O : X -> R) x1 x2,
  x1 <> x2 -> O x1 = O x2 -> forall D : R -> X, D (O x1) = x1 -> D (O x2) = x2 -> False.
```

with a gauge-redundancy specialization `gauge_redundancy_forces_undecodability` (`O (h x) = O x`). This
is the abstract twin of the companion's **zero-fibre indistinguishability equivalence**: `indist Φ Ψ :=
I(Φ−Ψ)=0` is proved reflexive/symmetric/transitive (`indist_refl/sym/trans`), and
`keystone_zero_iff_component` supplies its concrete content (constant on each connected component).
Instantiating `O := Φ ↦ [Φ]_indist` makes `no_decoder_recovers_state` apply directly to the zero fibre.

**Honest fence (Dr).** The shared core — the equivalence-kernel (kernel-pair) of a non-injective readout
partitions distinct true states into classes no decoder can separate — is *generic*: it holds for any
non-injective map, and the abstract lemma's proof is a one-line consequence of non-injectivity. So the
several independent arrivals (an abstract collapse map here, a concrete Dirichlet-form zero fibre in the
companion, and a pigeonhole route) are **coherence across the program, not three independent pieces of
deep evidence**. What is worth keeping is the opposite of a boast: a foundation's central move here is
*elementary and universal* — exactly what a foundational move should be. (Provenance note: the sibling
results `minimal_three_values` and `discrete_floor` live in **this** repo's
`formal/IDM_ReadoutMinimality.v` and `formal/IDM_Genesis.v`, not in `readout_genesis`.)

### 2. The typed reader states — the machine-checked floor under IDM's HOLD discipline

Every exact kernel in IDM refuses to fake a result: on a genuinely unresolved case it raises a
**distinct typed HOLD**, never a numeric `0`. `AlgebraicHOLD`, `ComplexRootsHOLD`,
`RationalIntegralHOLD`, and `FactorizationBudgetExceeded` are exactly a *sum type* separating
"resolved value (including a resolved zero)" from "unresolved / failed / budget-exceeded". The
companion's `ReaderTwoLevels.v` machine-checks that this separation is **sound and necessary** over ℚ:

| IDM kernel behaviour (convention, evidenced by the typed HOLD) | Companion theorem (machine-checked over ℚ) |
|---|---|
| a resolved `0` is a *different object* from a HOLD — the two never collapse | `recorded_zero_differs_from_boundary`, `accumulator_states_are_distinct`, `resolved_zero_is_not_unresolved` |
| a HOLD is **fail-closed**: it absorbs, it never silently becomes a value downstream | `accumulator_failure_left/right_absorbing`, `pipeline_unresolved_left/right_absorbing`, `boundary_blocks_next_stage` |
| a resolved zero *does* flow to the next stage; a HOLD does not | `recorded_zero_allows_next_stage` vs `boundary_blocks_next_stage` |
| the empty/degenerate case's verdict depends on the declared contract (e.g. `∫0 dx → "0"` resolved, vs a budget-exceeded factorization → HOLD) | `total_contract_empty_is_zero`, `strict_contract_empty_is_unresolved`, `empty_case_depends_on_contract` |
| reusing ONE untagged value as both unit *and* absorber for the **same** operation forces the whole carrier to collapse — why "just use `0` for everything" is unsound | `rr_identity_and_absorbing_collapses` |
| the typed escape hatch: across **two distinct** operations (accumulation vs sequencing) one boundary state is a unit for one and absorbing for the other with **no** collapse — so keeping resolved-zero and HOLD as distinct states is not just safe but the only sound design | `boundary_two_roles_no_collapse` (= `boundary_acc_left_unit` ∧ `boundary_seq_left_absorbing` ∧ carrier has ≥2 distinct elements) |

**Honest fence.** The companion proves the *discipline* is sound over ℚ — that a typed reader **can**
and **must** keep these states apart. It does **not** prove that IDM's Python kernel implements the
discipline faithfully; that is a code convention held by review (every exact kind returns a typed
HOLD, never a bare `0`, on an unresolved case), evidenced by the HOLD exception types, not itself
machine-checked. Read the two together: the convention is the code's, the soundness proof is the
companion's. This is also the formal backing for the workspace-wide **zero/∞ non-readout guard** —
injected zeros `Z1–Z4` (`INDEX.md §0`) are non-readouts; a *resolved* zero from `L_R` is a readout,
and the two are now provably distinct objects, not the same `0`.

## Reproduce

```bash
git clone https://github.com/morrocwi/zero-readout-certifies.git
cd zero-readout-certifies && make verify      # → verified 38 audited results, no extra assumptions
```

Both arcs share the same metatheory fence: `Closed under the global context` means an audited
constant reports no *additional* global assumptions; it does not claim the Coq/Rocq kernel or CIC
itself is assumption-free. That fence is declared, not hidden — in `formal/README.md` here and in
`docs/SCOPE.md` there.
