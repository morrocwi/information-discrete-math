# Phase 3 literature search log (reproducibility record)

Method: WebSearch tool, field vocabulary only (no "IDM"/"readout"/"routing" terms).
Date accessed: 2026-09-20. Search-tool summaries were used to identify and orient to
sources; no full-text paper was read end-to-end this pass (a depth limitation,
disclosed in PRIOR_ART_MAP.md, not hidden).

| # | Search query | Purpose | Key finding | Relevance |
|---|---|---|---|---|
| 1 | MPQS SIQS polynomial selection switching adaptive yield feedback state decision | Layer A/B mapping | Query too specific/compound for direct hits; redirected to targeted follow-ups (#5, #8) | Low direct value, informed later queries |
| 2 | large prime variation single double large prime relation acquisition factoring | Layer C/D mapping | Single/double large-prime variation is a state-dependent partial-relation acceptance rule, ~2.5x speedup for double vs single at scale | HIGH — near-identical to RSA-08/retention hypotheses |
| 3 | special-q lattice sieving NFS relation collection load balancing adaptive scheduling | Layer B mapping | Special-q is embarrassingly parallel, independently processed per-q, no evidence of cross-q live feedback found | MEDIUM — rules out one candidate overlap, doesn't confirm a gap |
| 4 | polynomial scoring Murphy's E quadratic sieve number field sieve choose best polynomial before sieving | Layer A mapping | Murphy's E-score ranks candidate polynomials by root/size properties before sieving, decades-old (Murphy 1999) | HIGH — near-identical to the core routing hypothesis |
| 5 | "adaptive sieving" OR "yield feedback" OR "online relation yield" quadratic sieve number field sieve dynamic | Negative search for Candidate Gap 1 | No source described a named "adaptive sieving"/"online relation yield" live-feedback technique; found smoothness-bound (B) tuning is a static pre-run parameter choice | Supports Candidate Gap 1 as not-yet-identified (not proven absent) |
| 6 | singleton removal structured Gaussian elimination filtering matrix step NFS quadratic sieve relation reduction | Layer E mapping | Singleton/clique removal + structured Gaussian elimination is mature, well-documented downstream filtering | HIGH overlap, but independently shown cost-irrelevant by Entry 010 |
| 7 | "adaptive polynomial selection" OR "dynamic sieve allocation" OR "feedback controlled sieving" quadratic sieve implementation | Negative search, round 2 | Confirmed these exact terms are not established literature terminology; SIQS "automates parameter selection" per-interval (not per observed yield) | Supports Candidate Gap 1 as not-yet-identified |
| 8 | msieve CADO-NFS implementation abandon poor polynomial early sieving yield monitor | Negative search, round 3, practitioner/implementation level | Practitioner-adjacent source states "predicting in advance the yield for a range of (a,b) pairs is hard" — an explicit admission of imperfect prediction; "NFS computation time is mostly spent on sieving" (corroborates Entry 007's bottleneck finding from a source closer to primary/implementer level) | Strengthens plausibility of Candidate Gap 1; independently corroborates Entry 007 |

**Exclusion note:** Wikipedia/blog/Medium-style summaries surfaced in several queries
were used only to orient (per review point 9's priority order), never as the sole
support for a technical claim above — every claim in `PRIOR_ART_MAP.md` cites a paper,
thesis, practitioner documentation, or established open-source implementation
(CADO-NFS, msieve) as its primary evidence.

**What was NOT done this pass (disclosed limitation):** no full paper was read
end-to-end; no source code of CADO-NFS/msieve was read directly (only README/docs
summaries via search); no additional search rounds beyond the 8 above were run. If a
deeper confirmation of Residual Question 1 is wanted, the next step is reading
CADO-NFS/msieve source (polynomial-selection and sieving modules) directly, not
further web search.

**UPDATE — Phase 3B did exactly that.** See `PHASE3B_CODE_AUDIT.md` for the full
write-up; provenance record for the code-level claims below.

| # | Repository | Commit | Path | Function/class | Behavior (from reading the body, not the name) | Production or test? |
|---|---|---|---|---|---|---|
| 9 | github.com/cado-nfs/cado-nfs | `6bcda7ce141afe4d9c409ec4ad8b6358162f21fc` | `sieve/las-norms.cpp`, `sieve/las-choose-sieve-area.cpp` | `sieve_range_adjust::adjust_with_estimated_yield()` | Numerically integrates an analytic norm-size estimate over ~24 candidate sieve-rectangle geometries per special-q, before sieving it; picks best-estimated shape. Predictive, not observed-execution feedback. | Production code path, but gated behind non-default `adjust_strategy>=2` (default is 0, per `sieve/las-siever-config.hpp` line 39; shown commented in example configs) |
| 10 | github.com/cado-nfs/cado-nfs | `6bcda7ce...` | `scripts/opal-test/las_run.py` | `LasRunner`, `last_report` | Uses just-observed relation yield from a completed benchmark sieve run to size the next test batch's special-q range (`q_inc`) | **TEST/TUNING infrastructure (OPAL parameter-optimization harness), NOT production** |
| 11 | github.com/cado-nfs/cado-nfs | `6bcda7ce...` | `scripts/cadofactor/cadotask.py` | `Duplicates2Task.update_ratio()`, `SievingTask.request_more_relations()` | Computes observed unique/total relation ratio from just-completed deduplication; uses it to size how many MORE raw relations to request via a `WANT_MORE_RELATIONS` notification | **Production** (this file is the real end-user orchestration driver) |
| 12 | github.com/cado-nfs/cado-nfs | `6bcda7ce...` | `scripts/cadofactor/cadotask.py` | `SievingTask` main loop (`enough_work_received`, `qnext` advancement) | Issues work units advancing one special-q pointer; accumulates relations unconditionally per unit; checks only the GLOBAL running total against target. No per-unit yield inspection found. | Production |
| 13 | github.com/cado-nfs/cado-nfs | `6bcda7ce...` | `sieve/las.cpp` | special-q abandonment logic | Abandons a special-q only on memory-budget overflow or geometric/skew validity failure — never on observed yield underperformance | Production |

**Method for #9–13:** `gh search code` (GitHub code search across the real
repository) to locate the claimed function, followed by `curl` of the raw file
content at the pinned commit and direct reading of the function body and its
call sites — not keyword-matching alone, per the review's explicit warning against
inferring purpose from a function's name.
