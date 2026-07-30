# Review Protocol

This repository welcomes adversarial technical review. The purpose of this protocol is not to constrain a reviewer's conclusion; it is to make every conclusion traceable to the claim actually made and the evidence actually supplied.

## 1. Restate the scope

The project's central proposal is:

> Finite source records and finite readouts are operational primitives. Continuum expressions may serve as mathematical targets or interpretations, but a computation is evaluated by its declared finite procedure and evidence.

This is not, by itself, an empirical claim about the physical world and not a theorem that continuum mathematics is dispensable in every context.

## 2. Review each axis separately

A result may succeed on one axis and fail on another. Review at least these axes independently:

1. **Definitions:** are the objects and domains specified?
2. **Mathematics:** does the conclusion follow from the hypotheses?
3. **Arithmetic:** does the implementation account for rounding and overflow?
4. **Software:** does the code implement the stated algorithm?
5. **Evidence tier:** is exact, formal, certified, stable, diagnostic, interpretive, or open evidence labelled correctly?
6. **Novelty:** what is classical, what is synthesis, and what is new?
7. **Empirics:** are benchmarks fair, reproducible, and workload-equivalent?
8. **Interpretation:** is philosophical language kept separate from theorem statements?

Acceptance of the retained-distinction interpretation is not required to audit the mathematics or code.

## 3. Do not promote evidence

Keep the following distinctions explicit:

- exact source-token arithmetic is not exact knowledge of a physical measurand;
- a truncation bound is not a target certificate unless arithmetic error is covered;
- observed refinement contraction is `STABLE`, not automatically `CERTIFIED`;
- library agreement is `finite_diagnostic`, not proof;
- a Coq theorem proves only its formal statement and mapped assumptions, not every neighboring implementation claim;
- failure of a sufficient certificate means `UNCERTIFIED`, not necessarily incorrect;
- exact algebraic singularity and numerical rank deficiency are different questions.

The normative definitions are in `docs/READOUT_CERTIFICATION_STANDARD.md`.

## 4. Classify findings precisely

Use one or more of these labels:

- **false:** contradicted under the stated definitions;
- **proof gap:** conclusion does not follow from the supplied argument;
- **implementation defect:** code does not implement the stated contract;
- **uncertified:** result may be correct but the evidence is insufficient;
- **underspecified:** key domain, arithmetic, hypothesis, or target is missing;
- **overclaim:** wording exceeds the proved scope;
- **novelty gap:** correct result is already classical or immediate;
- **reproducibility gap:** required artifact or environment is absent;
- **scope mismatch:** criticism or claim concerns a different target;
- **interpretive disagreement:** theorem remains intact but the proposed reading is disputed.

## 5. Execution and proof inspection

Run executable claims when the environment permits, and report commands, versions, exit codes, and outputs. Lack of execution does not prevent a valid proof critique, source-level bug report, or novelty assessment; state which checks were and were not performed.

For formal claims:

- inspect the exact theorem statement;
- inspect imported axioms and modules;
- verify the code-to-proof mapping;
- distinguish an abstract law from implementation verification.

For performance claims:

- compare equivalent workloads;
- disclose compilation and warm-up;
- preserve failures and non-convergence;
- inspect raw results, not only charts.

## 6. Review conclusion template

A strong review should state:

- the manuscript/repository thesis as understood;
- the strongest verified contribution;
- the strongest unresolved defect;
- which claims are exact, certified, stable, diagnostic, interpretive, or open;
- whether the main issue is correctness, novelty, implementation, evidence, or presentation;
- commands actually run; and
- a clear recommendation with required revisions.

Authority, consensus, and philosophical preference are not substitutes for evidence. Neither is repository-local terminology a substitute for established mathematical definitions.
