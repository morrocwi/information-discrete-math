# Project development plan — what's next

> The living "where this project is going" hub. Three tracks run in parallel: **A — CAS depth** (make the
> exact symbolic engine complete), **B — Developer experience** (easy for programmers), and **C — AI
> Gateway** (easy for small models). The granular CAS todolist is in [`../../BACKLOG.md`](../../BACKLOG.md);
> this folder is the higher-level "next version" view. Scope of the solver today:
> [`../../SOLVER.md`](../../SOLVER.md).

## Where we are

- **269 solver kinds** across 11 domains · **194 machine-checked axiom-free Coq theorems** · every answer
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
1. **[~]** One-command install — `pip install information-discrete-math`. Metadata publish-ready
   (readme + classifiers + URLs in `pyproject.toml`); wheel build verified (installs into a clean env,
   `import idm` solves). The `twine upload` needs a founder PyPI token — steps in
   [`docs/PUBLISHING.md`](../PUBLISHING.md).
2. **[x]** Schema discovery in Python — `idm.describe/schema/example(kind)` → `idm/discovery.py` (shared with the `python -m idm` CLI, one source of truth).
3. **[x]** Typed convenience — `idm.solve_integral(...)`, `idm.factorize(n)`, `idm.solve_matrix(A, b)` (+ `gcd`, `integrate_rational`, `eigenvalues`, `solve_roots`, `solve_ode`) → `idm/convenience.py`.
4. **[x]** `Result` object — `.status .value .bound .tier .is_hold .is_ok .raise_for_hold() .to_dict()`; a `dict` subclass so `idm.solve()` stays 100% backward-compatible → `idm/results.py`.
5. **[x]** Quick Start page — [`docs/QUICKSTART.md`](../QUICKSTART.md), copy-runnable problems (every output verified by running it).

## Track C — AI Gateway (for small models) — [task #52]

An **entrance** layer over the full 266 kinds (never a capability reduction): `idm.ai.run` →
deterministic router → the full `idm.solve` registry. Preserve: never delete the full API; pass advanced
options through; never silently downgrade exact→numeric (report the attempt); expose the route; provide an
escalation path. Phases: A (`idm.ai.run` + 8–12 high-level ops + central schema + error codes + unified
result + aliases/defaults) · B (domain router + expression classifier + plan→validate→execute + dry-run) ·
C (synthetic tool-use dataset + benchmark vs a real 0.5B). Reduces the model's decision space from 266 to
8–12 per step while the router still reaches all 266.

- **[x] Phase A** — `idm/ai.py`: `idm.ai.run(op, **params)` deterministic entrance over 11 high-level ops
  (`factor`, `gcd`, `integrate`, `integrate_exact`, `roots`, `solve_linear`, `eigenvalues`,
  `determinant`, `ode`, `limit`, `shortest_path`), `idm.ai.ops()` central schema (op → kind, fields,
  tier), unified `Result` with the route exposed, structured error codes (`UNKNOWN_OP` + `did_you_mean`
  / `MISSING_PARAM` / `SOLVER_HOLD`), tiers forwarded verbatim (no silent downgrade), and `idm.solve`
  documented as the escalation path to all 269 kinds. Never a capability reduction.
- **[x] Phase B** — `idm.ai.route(request)` maps a free-form string (via `idm.parse`) or a structured
  `{op}`/`{kind}` dict to a plan; `idm.ai.plan(op, ...)` and `run(..., dry_run=True)` return the route +
  the exact problem dict WITHOUT executing (plan→validate→execute), with an honest required/optional
  field split (from handler `p["x"]` vs `p.get("x")`); unclassifiable input HOLDs (`UNCLASSIFIED`).
- **[x] Phase C** — `idm/ai_bench.py`: a fixed synthetic tool-use dataset (`dataset()`, 17 cases over
  all 11 ops incl. free-form + unclassifiable) + a model-agnostic benchmark harness (`score(router)`
  reports op-selection & end-to-end execution accuracy). `benchmark_router()` scores the deterministic
  `idm.ai.route` as the oracle (100%/100%). To benchmark a real 0.5B, pass a router that calls the
  model — no weights are shipped or needed for the self-test.

## v1.5.0 (released 2026-07-30)

A **developer-experience & exact-CAS** release — all additive, tier-honest, 269 kinds:
- **Track A (CAS depth):** complete complex root-finding with multiplicity (`all_roots`), the exact
  rational-function integrator (repeated quadratics via the reduction formula), and a two-layer
  deterministic performance fence (HOLD, never hang, on large-coefficient/high-degree inputs).
- **Track B (DX):** the `Result` object, typed convenience wrappers, schema discovery
  (`idm.describe/schema/example`), and the Quick Start page. Gap 1 (PyPI) is *packaged and verified* —
  only the `twine upload` (a founder token) remains ([`../PUBLISHING.md`](../PUBLISHING.md)).
- **Track C (AI Gateway):** `idm.ai` — Phase A entrance (`run`/`ops`), Phase B free-form router
  (`route`/`plan`/`dry_run`), Phase C benchmark harness (`idm.ai_bench`).
- **Formal:** the published companion `zero-readout-certifies` wired into the ecosystem
  ([`../FORMAL_COMPANIONS.md`](../FORMAL_COMPANIONS.md)).

## Next (open, founder-directed)
- **PyPI upload** — needs a founder token (packaging done).
- **Track A frontier** — degree-≥3 irreducible integration (Risch), exact complex arithmetic
  (separation bounds), a *tight* `all_roots` runtime bound (the current fence is a disclosed heuristic).
- **AI Gateway** — benchmark against a real 0.5B model (harness is ready).

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
