# Project development plan — what's next

> The living "where this project is going" hub. Three tracks run in parallel: **A — CAS depth** (make the
> exact symbolic engine complete), **B — Developer experience** (easy for programmers), and **C — AI
> Gateway** (easy for small models). The granular CAS todolist is in [`../../BACKLOG.md`](../../BACKLOG.md);
> this folder is the higher-level "next version" view. Scope of the solver today:
> [`../../SOLVER.md`](../../SOLVER.md).

## Where we are

- **268 solver kinds** across 11 domains · **194 machine-checked axiom-free Coq theorems** · every answer
  is **EXACT / CONDITIONAL / HOLD** (never a fabricated number).
- The kind count is now **single-sourced**: gates read `len(idm.kinds())`, and a doc-scan gate
  (`tests/test_repo_consistency_gates.py::test_kind_count_is_single_sourced_across_docs`) fails CI if any
  doc's stated total drifts. Adding a kind: follow the permanent skill `.claude/skills/idm-add-kind/`.

## Track A — CAS depth (the math) — [`BACKLOG.md` → the 14 work packages]

Four root layers: move the public CAS onto one kernel · complete algebraic/complex exact arithmetic ·
add expression-level reasoning · connect the core to close solve/calculus/linalg **with certificates**.

- ✅ **WP2** — exact **real** algebraic-number arithmetic (`AlgReal`: construct from a ℚ-polynomial,
  `+ − × ÷`, powers, exact ordering/equality/sign, substitute-back). The #1 gap, done.
- ✅ **WP3 Increment 1** — `all_real_roots`: every **real** root exact + multiplicity, no Durand–Kerner;
  complex count reported.
- ▶ **Next in dependency order** (all unblocked by WP2/WP3): **WP6** complete univariate solving (deg-≥3
  irrational roots via `AlgReal`, symbolic quadratic coeffs, `completeness=complete`) · **WP13** exact
  eigenvalues as algebraic objects · **WP11** degree-≥3 ODE roots · **WP3 Increment 2** complex-root
  isolation (rational rectangles) · **WP8** rational-function integration (wire the existing `apart`) ·
  **WP10** wire Gosper summation.

## Track B — Developer experience (for programmers) — [task #51]

From the usability audit (~7/10 → ~9/10, **no new solver**):
1. **[ ]** One-command install — `pip install information-discrete-math` (needs a founder PyPI decision).
2. **[ ]** Schema discovery in Python — `idm.describe/schema/example(kind)` (CLI already exists).
3. **[ ]** Typed convenience — `idm.solve_integral(...)`, `idm.factorize(n)`, `idm.solve_matrix(A, b)`.
4. **[ ]** `Result` object — `.status .value .bound .tier .is_hold .raise_for_hold()` + `.to_dict()`.
5. **[ ]** Quick Start page — 10–20 copy-runnable problems from an empty environment.

## Track C — AI Gateway (for small models) — [task #52]

An **entrance** layer over the full 266 kinds (never a capability reduction): `idm.ai.run` →
deterministic router → the full `idm.solve` registry. Preserve: never delete the full API; pass advanced
options through; never silently downgrade exact→numeric (report the attempt); expose the route; provide an
escalation path. Phases: A (`idm.ai.run` + 8–12 high-level ops + central schema + error codes + unified
result + aliases/defaults) · B (domain router + expression classifier + plan→validate→execute + dry-run) ·
C (synthetic tool-use dataset + benchmark vs a real 0.5B). Reduces the model's decision space from 266 to
8–12 per step while the router still reaches all 266.

## Next version (v1.5, proposed)

A **developer-experience** release that also lands the first CAS-depth increments already shipped:
- Track B gaps 2/3/4/5 (pure DX, no behavior change) + Track A WP6 (complete univariate solving).
- Gap 1 (PyPI publish) and the AI-Gateway Phase A are founder calls on scope/priority.

**Not in scope / not CAS blockers:** P1 general-group cardinality, P7/P8 approximate-counting bounds,
Sylvester/Haynsworth analytic extensions, adaptive numerical grids (theory-open or numeric-engineering).

## Recently done (this cycle)

ℚ-computability law + two-tier Hilbert frontier · the continuum as a ℚ-primitive (`idm.continuum`) + a CI
anti-ℝ-slide guard · textbook local-fence consistency · `SOLVER.md` + the audited CAS checklist + the
14-work-package plan · **WP2 + WP3 Increment 1** (exact algebraic numbers & real roots) · the kind count
single-sourced + the `idm-add-kind` skill. Formal core → 194 axiom-free theorems; registry → 266 kinds.

---
*A plan, not a promise of dates. Items move as evidence changes; `BACKLOG.md` holds the granular CAS list
and git history holds what actually shipped.*
