# Phase 3B — Primary-Source Code Audit (CADO-NFS)

**Method:** direct source inspection via `gh search code` (GitHub code search) and
`curl` of raw files from `github.com/cado-nfs/cado-nfs` at commit
`6bcda7ce141afe4d9c409ec4ad8b6358162f21fc` (master, fetched 2026-09-20). Not web-search
summaries — actual function bodies and call sites read and traced. msieve was not
reached this pass (time-boxed; disclosed, not hidden — see open items).

---

## A. Code-Path Map

### A1. `sieve_range_adjust::adjust_with_estimated_yield()`
- **Definition:** `sieve/las-norms.cpp`, `sieve/las-norms.hpp`.
- **Caller:** `choose_sieve_area_impl()` in `sieve/las-choose-sieve-area.cpp`, itself
  called from the production sieving executable's main loop (`sieve/las.cpp`) — this
  IS a production code path, not a test file.
- **Condition:** only executes `if (adjust_strategy >= 2)` (`las-choose-sieve-area.cpp`
  line ~102-103).
- **What it does (read the actual body, not inferred from the name):** for the
  CURRENT special-q, before any sieving of it happens, numerically integrates an
  analytic norm-size distribution (`estimate_yield_in_sieve_area`, `N=5` sample
  points) over ~24 candidate sieve-rectangle "shuffle matrices" (geometric
  transforms of the (I,J) sieve area), and picks the shape with the best ESTIMATED
  yield. This never touches actually-observed relation counts from completed
  sieving — it is a pre-sieve, model-based estimate.
- **Default status (verified, not assumed):** `sieve/las-siever-config.hpp` line 39:
  `int adjust_strategy = 0;` (class default). Example parameter files
  (`parameters/factor/params.c115`, `.c120`, `.c148`) show
  `#tasks.sieve.adjust_strategy = 2` **commented out**. `scripts/cadofactor/cadotask.py`
  (the production orchestration driver end users actually run) does not set
  `adjust_strategy` to 2 in its own default config path found this pass.
  **Conclusion: production-path CAPABLE, but NOT the default/normal-practice
  behavior** — this is a real distinction per review point 25/26 (capability ≠
  default practice; capability alone still forecloses a *novelty* claim on the
  mechanism, but does not license calling it "what CADO does").
- **Taxonomy: A (Predicted-yield adaptation).** **Granularity: SPECIAL-Q /
  SIEVE-AREA-GEOMETRY** (per-special-q, before its own sieving; not cross-special-q).

### A2. `scripts/opal-test/las_run.py` — `LasRunner`, `last_report`
- **Context (verified by reading the file, not guessed from the name):** this lives
  under `scripts/opal-test/` — CADO's own OPAL-based parameter-optimization/
  benchmarking harness, used by developers to tune sieve parameters (`lim0/1`,
  `lpb0/1`, etc.) for different problem sizes. **This is TEST/TUNING infrastructure,
  not the production end-user factoring driver** (per review point 5's required
  test-vs-production distinction).
- **What it does:** after each benchmark sieving run, `runner.last_report =
  stats.relations_int.lastvalue[0]` records the just-observed relation yield; this
  value sizes `q_inc` (how large the NEXT special-q range batch should be) via
  `q_inc = int(self.rels_wanted / (10.0 * v))`.
- **Taxonomy: C (Observed-yield parameter tuning).** **Granularity: BATCH.**
  **Classification: TEST-ONLY**, per the explicit warning against test-to-production
  leakage — this does NOT establish that production factoring does this.

### A3. `Duplicates2Task.update_ratio()` + `SievingTask.request_more_relations()`
- **Definition:** `scripts/cadofactor/cadotask.py` — **this IS the real production
  orchestration driver** end users run to factor a number (confirmed: this file
  drives `Polysel*Task`, `SievingTask`, `PurgeTask`, `Duplicates2Task`, etc. as a
  real task-dependency pipeline).
- **Call chain traced:** after deduplication of a batch of relations,
  `update_ratio(input_nrel, output_nrel)` computes `ratio = new_out / new_in` (the
  fraction of newly-added relations that survive dedup) and stores it in
  `self.state["unique_ratio"]`. When downstream filtering later calls
  `request_more_relations(target)` (because more relations are still needed),
  it uses this **stored, OBSERVED ratio from the actual just-completed run** —
  not a predictive model — to compute `additional_in = additional_out / ratio`, the
  number of MORE raw relations to request, then sends a `WANT_MORE_RELATIONS`
  notification back to `SievingTask` with the new target.
- **This is a genuine, confirmed, PRODUCTION, observed-execution-feedback
  mechanism** that changes a future acquisition action (how much more sieving work
  to schedule) based on actually-measured results from completed work, not a
  prediction.
- **Taxonomy: C/D boundary (observed-yield feedback that resizes future
  acquisition).** **Granularity: GLOBAL/BATCH** (total unique-relation yield rate
  across the whole run so far, not per-polynomial or per-special-q).

### A4a. `sieve/las.cpp` special-q iteration loop — abandonment logic (added after initial write-up, per own recommended next step)
- **Traced directly.** The only "special-q is abandoned" logic found in the main
  sieving executable's loop is triggered by a **memory-budget check** (projected
  bucket-sort memory would exceed the machine's configured budget → abandon this
  special-q, log a suggestion to restart with different memory settings) — a
  resource-safety guard, not a cost/yield optimization decision. Other discard paths
  found earlier (A1's context: q-lattice basis too skewed, `J` below minimum) are
  geometric/structural validity checks, also not yield-triggered. **Per review point
  17 ("is its objective computational-cost/yield optimization?"), none of these
  count toward Category D** — they answer "can we safely proceed at all," not "is
  this unit's yield low enough to abandon in favor of something better."
- **Conclusion:** this specific, additional trace (one more code region read, per
  the project's own "reading is cheaper than building" principle) finds NO
  yield-triggered fine-grained abandonment in the production special-q loop either.
  Residual Question 1's "not identified" status is now supported by three
  independently-traced code regions (A1, A3/A4, A4a), not just one.

### A4b. `SievingTask` main loop (`enough_work_received`, `qnext` advancement)
- **Traced directly** (`cadotask.py`, `SievingTask` class): the sieving loop issues
  work units advancing a single `qnext` special-q pointer, accumulates
  `rels_found` from each completed work unit unconditionally, and checks only
  `get_nrels() >= rels_wanted` (a GLOBAL threshold) to decide whether to keep
  issuing more work units. **No code was found in this class that inspects an
  individual work unit's own yield to cancel, deprioritize, or reallocate away from
  it before it completes.** Every work unit runs to completion regardless of its
  individual yield; the only feedback loop is the global running total vs. target.

---

## B. Adaptation Taxonomy (applied to all findings above)

| Category | Definition | Found? | Where |
|---|---|---|---|
| A — Predicted-yield | Model/score used before execution | YES | `adjust_with_estimated_yield` (A1) |
| B — Observed-yield diagnostics only | Logged/reported, doesn't change action | YES (implicit) | general stats/logging (`utils/stats.c`, not action-changing) |
| C — Observed-yield parameter tuning | Measured result resizes NEXT task | YES, production | `update_ratio`/`request_more_relations` (A3, GLOBAL); also YES, test-only (A2, BATCH) |
| D — Observed-yield production ROUTING (abandon/reprioritize a specific in-progress unit before completion, based on ITS OWN yield) | **NOT FOUND** in code paths traced (A1, A3, A4) | NOT CONFIRMED either way | — |

---

## C. Granularity Map

| Granularity | Observed-feedback mechanism found? |
|---|---|
| GLOBAL | YES, production, confirmed (`update_ratio`/`request_more_relations`) |
| BATCH | YES, but TEST-ONLY (opal-test `q_inc` sizing) |
| POLYNOMIAL | NOT FOUND (Murphy's E is predictive, pre-sieve, not observed-feedback) |
| SPECIAL-Q | NOT FOUND as observed-feedback (adjust_with_estimated_yield is predictive, per-special-q, not fed by other special-q's observed results); no per-special-q abandon-based-on-own-yield found in `SievingTask`'s work-unit loop |
| REGION / CANDIDATE | Not applicable in the code paths reviewed at this granularity |

---

## D. Corrected Prior-Art Map wording (per review points 8–10)

- **Murphy's E-score:** overlap corrected from "NEAR-IDENTICAL" to **"HIGH
  architectural overlap; different information source"** — it is predictive
  (structural properties, computed before sieving), not observed-execution
  feedback. Confirmed by A1's same-category finding: CADO's OWN
  `adjust_with_estimated_yield` is the same category (A, predictive), reinforcing
  that predictive routing is the classical norm at this layer, while observed
  feedback (category C) exists only at coarser (GLOBAL) granularity in production.
- **Large-prime variation:** overlap corrected from implicit near-identical framing
  to **"adjacent classical design space / HIGH conceptual overlap,"** preserving the
  distinction already logged in Phase 3 (certify-safe-drop vs. retain-partial-for-
  later-combination).
- **"Candidate Gap 1" renamed to "Residual Question 1"** throughout, per review
  point 10, since it had not yet survived a production-code audit when first
  written.

---

## E. Residual Question (re-narrowed, operational form)

The BROAD framing from Phase 3 — "does production use observed execution results to
alter future acquisition actions for cost/yield reasons?" — is now **CLOSED AS
CLASSICAL, confirmed in production code (A3), at GLOBAL/BATCH granularity.** Do not
re-open that framing.

**Residual Question 1 (re-narrowed):**

> Given partial observed sieve yield from ONE specific in-progress polynomial or
> special-q range (not the pipeline's aggregate global total), does a production
> implementation abandon, deprioritize, or reallocate effort away from that specific
> unit — before its allocated work is finished — based on ITS OWN observed
> underperformance, for cost/yield reasons?

**Status: not identified in the primary-source implementations reviewed this
pass** — three independently-traced production code regions checked directly
(`las-choose-sieve-area.cpp`/`las-norms.cpp`'s per-special-q geometry code,
`las.cpp`'s special-q abandonment logic, and `cadotask.py`'s
`SievingTask`/`Duplicates2Task` classes), all showing either predictive
(non-observed) routing, resource-safety abandonment (non-yield-triggered), or
GLOBAL-granularity (not per-unit) observed feedback. **Remaining unread:** the
`Polysel1Task`/`Polysel2Task` polynomial-selection scheduling classes in
`cadotask.py`, and msieve's equivalent code entirely — disclosed as open items, not
treated as a completed negative. This is now a **RESIDUAL HEADROOM CANDIDATE**, not a
novelty claim, and not yet a fully "destroyed" question — the search was narrowed by
real evidence across three separate code paths, not preserved by narrowing
definitions to dodge falsification (per review point 31's rule).

---

## F. Verdict

$$
\boxed{\textbf{HOLD}}
$$

**Not NO:** the fine-grained (polynomial/special-q-level, own-yield-triggered
abandon-and-reallocate) mechanism was not found in the specific code paths traced,
but the search was not exhaustive (the actual C++ special-q iteration/scheduling
loop in `las.cpp` and the polynomial-selection task classes remain unread this
pass) — closing this as NO would be a search-depth-driven false closure, exactly
what review point 31 forbids.

**Not YES-TO-PHASE-4:** the specific residual question has a real, narrow,
operational definition now (huge progress from Phase 3's vaguer framing), but (a)
the broad version of the question this project actually cared about (does classical
practice ALREADY do state→estimate→route computational effort before paying cost?)
is now answered YES at multiple layers (Murphy's E predictive routing, GLOBAL
observed-feedback resizing) — the remaining sliver is specifically about
FINE-GRAINED, mid-execution, own-unit-triggered abandonment, a narrower question
than the project started with; (b) reading two more specific code regions
(`las.cpp`'s scheduling loop, `Polysel*Task`) is strictly cheaper than building a
2-polynomial harness and has not been done yet.

**Next step (reading, not building):** trace `sieve/las.cpp`'s special-q iteration
loop and the `Polysel1Task`/`Polysel2Task` classes in `cadotask.py` for any
per-polynomial or per-special-q yield-triggered reallocation before concluding
Residual Question 1 either way. If that also comes up empty, Residual Question 1
graduates to a genuine residual-headroom candidate worth a cheap 2-polynomial
falsifier (Phase 4). If found, close as CLASSICAL and redirect the research question
to "does any additional observable state improve an already-adaptive classical
controller" (per review point 28), a categorically different and harder hypothesis.
