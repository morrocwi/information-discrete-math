# Clay P1 Safe Core — Formal Boundary

**Date:** 2026-09-11  
**Status:** formal candidate until the PR CI compiles `formal/IDM_FiniteObstructionSafeCore.v` under Coq 8.20 and every listed theorem reports `Closed under the global context`.  
**Issue:** `morrocwi/information-discrete-math#124`.

This file records the exact boundary of the first P1 formal pass. It is intentionally smaller than the Clay-bearing programme.

## Formalized finite kernels

| Identifier | Statement role |
|---|---|
| `strict_margin_pass_sound` | `PASS` from a strict finite margin implies certified error is below the margin |
| `strict_margin_pass_complete` | finite error below the margin makes the strict gate return `PASS` |
| `strict_margin_hold_when_not_strict` | failure of the strict inequality returns `HOLD` |
| `missing_certificate_holds` | absent certificate fails closed to `HOLD` |
| `gated_pass_requires_certificate_and_margin` | `PASS` requires both certificate presence and strict margin |
| `error_budget_monotone` | enlarging a certified budget preserves an existing error bound |
| `error_budget_additive` | two certified finite error bounds compose additively |
| `finite_chain_budget_composition` | pointwise certified budgets along any finite chain imply a bound on the summed chain error |
| `compatibility_two_step` | two finite comparison legs plus a triangle-style direct discrepancy bound yield a composed comparison bound |
| `symmetry_transport_pass` | a passing certificate transports across a declared action when verifier invariance is explicitly assumed |
| `verified_local_defect_sound` | a verified local witness implies the declared local defect when verifier soundness is explicitly assumed |

## What this closes if CI is green

It closes the first **safe finite logic/composition** layer requested by IDM issue #124. In particular it provides machine-checkable versions of:

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

The safe core can prove that a locally verified defect is sound and that a strict certified margin survives declared finite error accounting. It does **not** construct a polynomial-size hitting support or establish inverse-polynomial capture against every polynomial-size unrestricted SAT circuit.

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

Only after the dedicated `clay-safe-core` CI job passes may the theorem rows above be described as `Th_coqc` / machine-checked axiom-free results. Before that, this document is a statement-level specification of the intended formal artifact.
