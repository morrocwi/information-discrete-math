# Clay P1 Safe Core — Formal Boundary

**Date:** 2026-09-11  
**Status:** **PASS / `Th_coqc` safe finite core** at PR #125 head `0da424aec8b06a49bcd01c8a5c75f4149c2e0df3`; dedicated GitHub Actions run `34563300185` compiled `formal/IDM_FiniteObstructionSafeCore.v` under Coq 8.20 and every listed theorem reported `Closed under the global context`.  
**Issue:** `morrocwi/information-discrete-math#124`.

This file records the exact boundary of the first P1 formal pass. It is intentionally smaller than the Clay-bearing programme.

## Formalized finite kernels

| Identifier | Tier | Statement role |
|---|---|---|
| `strict_margin_pass_sound` | `Th_coqc` | `PASS` from a strict finite margin implies certified error is below the margin |
| `strict_margin_pass_complete` | `Th_coqc` | finite error below the margin makes the strict gate return `PASS` |
| `strict_margin_hold_when_not_strict` | `Th_coqc` | failure of the strict inequality returns `HOLD` |
| `missing_certificate_holds` | `Th_coqc` | absent certificate fails closed to `HOLD` |
| `gated_pass_requires_certificate_and_margin` | `Th_coqc` | `PASS` requires both certificate presence and strict margin |
| `error_budget_monotone` | `Th_coqc` | enlarging a certified budget preserves an existing error bound |
| `error_budget_additive` | `Th_coqc` | two certified finite error bounds compose additively |
| `finite_chain_budget_composition` | `Th_coqc` | pointwise certified budgets along any finite chain imply a bound on the summed chain error |
| `compatibility_two_step` | `Th_coqc` | two finite comparison legs plus a triangle-style direct discrepancy bound yield a composed comparison bound |
| `symmetry_transport_pass` | `Th_coqc` | a passing certificate transports across a declared action when verifier invariance is explicitly assumed |
| `verified_local_defect_sound` | `Th_coqc` | a verified local witness implies the declared local defect when verifier soundness is explicitly assumed |

## CI evidence

Dedicated verifier: `formal/verify_clay_safe_core.sh`.

Recorded run: `clay-safe-core` GitHub Actions run `34563300185`.

The run reported:

```text
axiom-free  strict_margin_pass_sound
axiom-free  strict_margin_pass_complete
axiom-free  strict_margin_hold_when_not_strict
axiom-free  missing_certificate_holds
axiom-free  gated_pass_requires_certificate_and_margin
axiom-free  error_budget_monotone
axiom-free  error_budget_additive
axiom-free  finite_chain_budget_composition
axiom-free  compatibility_two_step
axiom-free  symmetry_transport_pass
axiom-free  verified_local_defect_sound
CLAY SAFE CORE PASS
```

This is formal evidence for the finite kernels only. It is not evidence for any open Clay-bearing bridge.

## What this closes

It closes the first **safe finite logic/composition** layer requested by IDM issue #124. In particular it provides machine-checked versions of:

1. strict-margin soundness and fail-closed HOLD semantics;
2. finite error-budget monotonicity/composition;
3. finite-chain compatibility-budget composition;
4. symmetry-respecting certificate transport under declared invariance;
5. local finite-defect checker soundness under a declared checker-soundness hypothesis.

The hypotheses are explicit. No theorem manufactures a witness, global object, continuum limit, circuit lower bound, or PDE regularity statement.

## NS stress test

A Navier--Stokes finite-resolution adapter may interpret:

```text
finite error          -> retained-state / residual / comparison discrepancy
certified budget      -> eta_NM or another finite enclosure
finite chain          -> N0 < N1 < ... < Nk resolution comparisons
symmetry action       -> declared translation or other proved reader symmetry
local defect checker  -> checker for a finite PDE-relevant obstruction
```

The safe core can compose certified finite budgets or transport an invariant certificate. It does **not** prove:

```text
FiniteTimeSingularity -> exists finite PDE-relevant witness
```

nor its converse. `NS-FUB-A1/A2` therefore remain OPEN.

## P-vs-NP stress test

A P-vs-NP adapter may interpret:

```text
finite error/budget   -> certified support/sampling loss budget
symmetry action       -> explicitly proved representation equivalence
local defect checker  -> restriction/boundary defect verifier
strict margin         -> positive capture margin after certified finite loss
```

The safe core proves that a locally verified defect is sound under the declared checker-soundness hypothesis and that a strict certified margin survives declared finite error accounting. It does **not** construct a polynomial-size hitting support or establish inverse-polynomial capture against every polynomial-size unrestricted SAT circuit.

Therefore `PNP-FUB-A1` remains OPEN.

## Non-vacuity boundary

The formal file contains no theorem corresponding to the following open proposals:

- `PROP-FUB-03` global failure -> finite witness;
- `PROP-FUB-04` unrestricted constructive uniform capture;
- the Clay-strength part of `PROP-FUB-05` turning finite compatibility into a global semantic conclusion;
- `NS-FUB-A1/A2`;
- `PNP-FUB-A1`.

Those statements require separate domain mathematics and remain subject to `PROP-FUB-06` non-vacuity auditing.

## Promotion rule

The theorem rows above are promoted only at the exact CI-verified source state. Any later statement or proof change must rerun `clay-safe-core` and the Clay governance gate before a new status is asserted.
