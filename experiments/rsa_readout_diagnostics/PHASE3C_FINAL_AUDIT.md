# Phase 3C — Final Primary-Source Audit (Phase 3 terminal round)

**Residual Question 1 (FROZEN, per review point 4 — not reworded after this point):**

> Given actual relation yield already observed from one specific acquisition unit,
> does a production factoring implementation abandon, deprioritize, resize, reorder,
> or switch future work for that unit or its alternatives before the originally
> allocated work is exhausted, for cost/yield reasons?

---

## A. Corrections to Phase 3B (per review points 1–2)

1. `PHASE3B_CODE_AUDIT.md`'s Section F ("Verdict") was written before its own
   Section A4a (the `las.cpp` special-q-abandonment trace) was added, and
   contradicted it by listing `las.cpp` as unread. Corrected in place — Section F
   now points to this document as the actual final verdict for Phase 3, and no
   longer claims `las.cpp` is unread (it was traced, and found to abandon only on
   memory-budget/geometric grounds, never yield).
2. `FINDINGS_SUMMARY.md`'s roadmap section is corrected below (see the paired edit)
   to stop describing Phase 2/2A as "proposed, not yet executed" — Phase 2A/B5a
   was DONE and BLOCKED in Entry 010, before Phase 3 even started.

## B. CADO Polysel result (independently re-verified this pass, not just re-quoted)

Read `Polysel1Task`/`Polysel2Task` in `scripts/cadofactor/cadotask.py` directly:
- `Polysel1Task.submit_one_wu`: advances a search-range pointer (`adnext`)
  deterministically across a fixed `[admin, admax)` range — a systematic scan, not
  yield-conditioned.
- Polynomial scoring: `MurphyE`, `exp_E` are parsed from polyselect output and used
  to maintain a ranked heap (`poly_heap`, sorted by `exp_E`) of best-found
  candidates — this is the SAME predictive-ranking mechanism already documented
  (Layer A / Category A), operating on candidates found by systematic search, not
  on observed sieve yield from having actually sieved any of them.
- **Confirmed:** `candidate polynomial -> exp_E/MurphyE -> rank/retain -> select
  best`, exactly as characterized. **Not identified:** any path where observed
  relation yield from having started sieving with a selected polynomial feeds back
  to re-rank or abandon it.
- Wording used per review point 2: **not identified in the CADO-NFS Polysel control
  paths inspected** (not "does not exist anywhere in CADO").

## C. msieve code-path audit (new this pass — first independent second implementation)

- **Repository:** `github.com/radii/msieve` (Jason Papadopoulos's original, the
  most-referenced canonical repo).
- **Files traced directly** (definition → caller → condition → state mutation, not
  keyword-only): `mpqs/mpqs.c` (top-level driver), `mpqs/poly.c` (polynomial/`a`
  value construction), `mpqs/sieve.c` (the actual acquisition control loop).
- **Finding, `mpqs/sieve.c`, function `collect_relations` (~line 697):**
  ```
  num_poly = 1 << (conf->num_poly_factors - 1)   // fixed, derived from factor-base size
  while (relations_found < target_relations) {
      build_base_poly(conf);                      // generate next scheduled batch
      i = 0;
      while (i < num_poly) {                      // process the batch IN INDEX ORDER
          relations_found += core_sieve_fcn(conf, i, curr_num_poly);
          i += curr_num_poly;
          if (external STOP flag set) return;      // user-triggered (Ctrl-C), not yield-triggered
      }
  }
  ```
  Every polynomial in a batch is sieved to completion via `core_sieve_fcn` in a
  fixed, predetermined index order; its individual contribution is simply added to
  `relations_found`; the ONLY loop-continuation check is the GLOBAL running total
  against `target_relations`. **No code path inspects an individual polynomial's
  own yield to skip, deprioritize, or reorder remaining polynomials in the batch.**
- **This independently reproduces the exact same structural pattern found in
  CADO-NFS** (predictive polynomial construction + GLOBAL observed-feedback
  stopping condition, no fine-grained own-unit corrective routing) in a completely
  separate, independently-written implementation (msieve vs. CADO-NFS share no
  code). Two independent implementations converging on the same architecture is
  stronger evidence than either alone.
- **Provenance:** `github.com/radii/msieve`, files `mpqs/sieve.c` (function
  `collect_relations`, `mpqs_core.c` caller chain), `mpqs/poly.c`,
  fetched 2026-09-20 via raw GitHub content at the `master` branch tip.
  NFS-side msieve code (`gnfs/poly/*`, `gnfs/sieve/*`) was NOT traced this pass
  (time-boxed; MPQS was prioritized as msieve's more actively-used sieving path)
  — disclosed as an open item, not treated as a completed negative for msieve's
  GNFS mode specifically.

## D. Category D found or not found

$$
\boxed{\textbf{NOT FOUND}}
$$

across five independently-traced production/near-production code regions spanning
two separately-implemented established factoring codebases (CADO-NFS: geometry
adjustment, global relation-request feedback, special-q abandonment, Polysel
ranking; msieve: MPQS relation-collection loop).

**Required wording (per review point 2/13):** *"Fine-grained observed-yield
corrective routing was not identified in the two established implementations
(CADO-NFS, msieve) reviewed."* This is not a claim that it does not exist anywhere
(msieve's GNFS sieve path and any other established implementation, e.g. GGNFS,
were not traced) — it is the honestly-scoped result of this specific audit.

## E. Final Phase 3 verdict

Restructured by mechanism category, per review point 21, not by algorithm name:

| Category | Status |
|---|---|
| **Predictive routing** (score a candidate cheaply before paying full cost — Murphy's E/exp_E in both CADO and msieth's polynomial selection; `adjust_with_estimated_yield`'s per-special-q geometry estimate) | **CLASSICAL** |
| **Coarse observed-feedback routing** (global/batch relation-count or duplicate-ratio feedback sizing how much more acquisition work to schedule — confirmed in both CADO's `cadotask.py` and msieve's `collect_relations`) | **CLASSICAL** |
| **Downstream relation filtering** (singleton/clique/structured Gaussian elimination) | **CLASSICAL**, and independently shown **cost-small** in this project's own harness (Entry 010: 0.006–0.068% of total cost) |
| **Fine-grained, own-unit observed-yield corrective routing** (Residual Question 1) | **NOT IDENTIFIED** in the two implementations reviewed → **RESIDUAL HEADROOM CANDIDATE** |

$$
\boxed{\textbf{PHASE 3 VERDICT: RESIDUAL HEADROOM CANDIDATE}}
$$

Not "novelty." Not "IDM advantage." Not "invention." A specific, narrow, frozen
question that survived source-code audits of two independent established
factoring codebases without being confirmed present OR fully ruled out everywhere.

## F. Next gate

Per review points 14–16 (hard stop — Phase 3 ends here, no Phase 3D, and prior-art
survival must precede residual-headroom estimation, which must precede any
engineering decision):

$$
\boxed{\text{PROCEED TO PHASE 4 — Residual Headroom Estimation (NOT engineering, NOT a new mechanism)}}
$$

Phase 4's question, unchanged from when it was originally specified: **even though
fine-grained corrective routing was not found in established implementations, is
there plausible, measurable headroom large enough to justify building anything at
all?** This requires a cheap-as-possible estimate (analytical or small-scale
empirical, in the spirit of Entry 010's ceiling calculation), not a 2-polynomial
harness, as the first move.

Programme status is otherwise unchanged from before Phase 3 (per review point 22 —
no family's verdict is altered by this phase): RSA-08 BLOCK, RSA-04 DRIFT, RSA-05 no
advantage shown, region routing BLOCK, B5a BLOCK, B5b HOLD.
