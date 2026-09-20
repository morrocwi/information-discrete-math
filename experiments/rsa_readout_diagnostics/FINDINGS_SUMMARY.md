# IDM–RSA readout-conditioned factoring diagnostics — findings summary

**Status banner:** everything referenced here (`PROP-IDM-RSA-01`..`08` and the
routing-architecture sketch) is **PROPOSAL / SKETCH — NOT CANONICAL**, per Toledo's
`EQUATION_SOURCE_POLICY.md` gate `TG-RFG-01`. Nothing here is registered in Toledo, no
intended slot (`A3/M.15–20.v1`, `A2/M.29–30.v1`) has been assigned. This directory is a
disposable diagnostic log, not a Toledo submission, not a paper, not a claim of a new
factoring algorithm.

**Scope:** these are smoke-test-scale numerical experiments (single machine, pure
Python, seconds-to-minutes runtime per trial), not a production cryptanalysis effort.
Sample sizes are small (2–3 instances per test, semiprimes of 27–40 bits). Nothing here
should be read as evidence about real-world RSA key sizes.

Full entry-by-entry log: [`RESULTS_LOG.md`](./RESULTS_LOG.md) (8 entries). This file is
the condensed positive/negative summary requested for quick review.

---

## Positive findings

1. **Methodology cross-check passed.** Our own empirical measurement — that
   smooth-relation acquisition (sieving) dominates total factoring cost (93.3–99.9% in
   our harness) — independently matches the published literature ("the collection of
   smooth values is overwhelmingly the most time-consuming stage of both MPQS and the
   Number Field Sieve"). This gives confidence the measurement approach itself is sound
   (Entry 006, 007).
2. **Two self-caught measurement errors, corrected before being reported as findings**
   (the process working as intended, not a clean result but a positive sign about the
   discipline used):
   - A cost model that summed division-ops and certificate-ops as equal units was
     wrong by ≈33× (measured via `timeit`); correcting it made an existing negative
     result (RSA-08) *more* negative, not less — i.e. the correction was applied
     honestly, not in whichever direction was convenient (Entry 004).
   - An apparent 27.8% "routing headroom" signal was traced to an under-sensitive
     verification threshold before being reported as a finding, and vanished (0.8%) once
     fixed — an explicit example of catching a spurious signal before it propagated
     into an "IDM has content" claim (Entry 008).
3. **Reusable calibration data produced:** empirical, machine-specific cost ratios (1
   modular-exponentiation round ≈ 33× one division op; 1 sieve-array update ≈ 0.8× one
   division op) that any follow-up work on this line can reuse instead of re-deriving.
4. **A concrete, well-known classical optimization was quantified rather than assumed:**
   QR (quadratic-residue) factor-base restriction cuts division work 3.6×–5.2× in our
   harness — useful as a calibrated floor for any future comparison, even though it is
   fully classical (Entry 005).
5. **Every negative result below is falsifiable and reproducible**, not just asserted:
   each has a named script, a stated method, and (where relevant) a stated reason *why*
   it failed, not just *that* it failed — satisfying the project's "failure must
   generate a constraint for the next hypothesis" discipline.

## Negative findings (no computational advantage found)

1. **`PROP-IDM-RSA-08` (DropSafe / Safe-Drop Criterion) — BLOCKED.** In every tested
   form (exact certificate, safety-traded/bounded certificate, and a gate-conditional
   "Generation-2" variant), the mechanism cost 2.8×–32.7× more (calibrated) than the
   classical numeric-threshold heuristic it was meant to beat. No valid batching
   mechanism exists for primality certification across distinct moduli in the tested
   scheme, closing off the most promising remaining lever (Entries 001, 004).
2. **`PROP-IDM-RSA-04` (Retain-Recompute-Resolve Gate) — FALSIFIED (DRIFT), not merely
   vacuous.** Built from real pipeline states (not hand-constructed counterexamples),
   the claimed implication failed under both a coarse cost-counter reading and a richer
   local-parity-vector reading, in all tested instances (Entry 002).
3. **`PROP-IDM-RSA-05` (Total Computational Cost Fold) — no advantage shown in the
   tested instance.** The specific retain/recompute tradeoff tested (parity vs. full
   exponent storage in Dixon's method) was too lopsided (the combining subset was ~1/50
   the size of the full relation set) for cost-aware selection to ever disagree with
   naive storage-minimization (Entry 003).
4. **Region-choice routing ("readout-conditioned computational routing," narrowest
   testable form) — BLOCKED, now on distributional evidence (n=13 of 20 held-out
   instances, frozen parameters, not tuned post-hoc).** Median headroom **0.0%**, mean
   3.9% (pulled up by 2 noise-driven outliers up to 32.6%). The outliers were audited
   per-region (not assumed genuine): they come from small-sample Poisson-like variance
   in which nearby region happens to yield a few more relations — real, not a
   measurement bug, but **not observable online without paying the exact cost the
   mechanism would need to save** (classic oracle-vs-online confusion). Constraint
   derived for the next candidate action family: it must offer alternatives with
   genuinely distinct STRUCTURAL yield profiles (e.g. real polynomial-switching), not
   regions differing only by sampling noise (Entry 008 + Entry 009).
5. **Sieve-efficiency mechanism space — HOLD, not attempted, flagged high-risk.** The
   dominant cost component (sieving) is exactly the target of 30+ years of dense,
   specific classical technique (SIQS polynomial-switching, large-prime variation,
   lattice/special-q sieving, polynomial root optimization). No mechanism was proposed
   here because the risk of reinventing one of these under new vocabulary was judged too
   high without deeper literature engagement first (Entry 007).

## Explicitly open / not yet tested (neither confirmed nor closed)

- **Family B5 — utility-conditioned relation retention/feedback** ("smooth ≠ useful";
  does the current retained-relation/dependency state usefully inform what to search
  for next?). Flagged as a genuinely different axis from everything tested above, but
  not yet attacked — also has dense classical prior art (singleton removal, structured
  Gaussian elimination, relation filtering) that must be checked first.
- **Real MPQS/SIQS-style polynomial-switching headroom.** The routing test above only
  measured headroom for choosing a region within ONE polynomial — a deliberately weak
  proxy. Testing genuine polynomial-switching headroom needs a materially larger
  implementation (true multiple-polynomial sieving) than this session's smoke-test
  scale supports.
- **`PROP-IDM-RSA-01` (Factor Certificate Readout) and `PROP-IDM-RSA-06`/`07`**
  (classical congruence-of-squares / Dixon parity-vector steps, used here only as
  infrastructure) were not independently attacked as hypotheses — `01`'s parent-lineage
  to Toledo was flagged as weak/unresolved and never revisited; `06`/`07` were always
  treated as disclosed classical baseline machinery, not IDM claims.

## Corrected overclaims (caught before publication, logged not hidden)

- **Entry 008's original verdict** stated region-routing headroom as "≈0%, structurally
  settled" from a single completed instance. Corrected to "low headroom signal, drop
  candidate — not yet a confirmed block" pending a real distribution study.
- **A chat-relayed Lens Note** described RSA-05 (Entry 003) as having "proved" that
  full exponent vectors are unnecessary until nullspace selection. Corrected to
  "observed sufficient in the tested construction" — Entry 003 is one empirical
  comparison on 2 instances, not a proof, and should never have been described as one.

## Phase 2A result (Entry 010) — B5a analytical ceiling, BLOCKED

A retrospective oracle allowed to make post-acquisition relation filtering/linear-
algebra/reconstruction cost exactly zero (a strict upper bound under the "B5a" action
family — it may not touch acquisition itself) could save at most **0.006%–0.068%** of
end-to-end pipeline cost, measured across 3/3 instances with real timed downstream
cost (GF(2) elimination + reconstruction), not an estimate. This is because
downstream cost is 3–4 orders of magnitude smaller than acquisition cost in every
instance. **BLOCK B5a** — no oracle hierarchy (O0–O3) needed to confirm further; the
analytical ceiling alone answers the question decisively, below the pre-declared 5%
stop-rule threshold. Derived constraint: any further mechanism must intervene
upstream in acquisition itself (motivating "B5b," feedback-conditioned acquisition),
but B5b is HOLD, not started — it needs genuinely structurally distinct acquisition-
time choices that the current single-polynomial harness does not have, and
fabricating one to give a policy "something to route between" is explicitly out of
bounds.

## Phase 3 result — Classical Adaptive Map, Engineering Verdict: HOLD

Deep literature mapping (see `PRIOR_ART_MAP.md`, `SOURCES.md`, `PHASE3_DECISION.md`),
using field vocabulary only (never "IDM"), found that classical adaptive factoring
practice already implements near-identical mechanisms for most of what this project's
routing hypothesis was reaching for:
- **Murphy's E-score polynomial ranking** (NFS/GNFS, Murphy 1999) — a cheap,
  pre-computed structural score that routes sieve effort to promising candidates
  before paying the expensive cost. **Near-identical overlap** with the core routing
  hypothesis.
- **Single/double large-prime variation** — a state-dependent partial-relation
  acceptance rule closely related to the RSA-08 family (retrospective attribution
  correction logged).
- **Singleton/clique removal + structured Gaussian elimination** — mature classical
  downstream filtering, independently confirmed cost-irrelevant by this project's own
  Entry 010 (0.006%–0.068% ceiling).

One narrow, specific question survived 3 rounds of negative search: whether classical
practice uses **live, within-run yield feedback** to re-rank/abandon a polynomial
mid-sieve, as distinct from Murphy's E's pre-computed score — not confirmed present or
absent in the sources reviewed (a practitioner-adjacent source admits yield
prediction "is hard," which keeps this question open rather than closed).
**Engineering verdict: HOLD** (not YES, not NO) — the cheap-enough next step is
reading CADO-NFS/msieve implementation source directly, not building a new harness;
if a deeper literature/source read still finds nothing, THEN a MEDIUM-cost
2-polynomial synthetic test would be the justified next experiment.

## Documented next steps (proposed, NOT yet executed under this commit)

An external review of this log proposed a more disciplined follow-up program before
any further mechanism is generated, summarized here for continuity but not run in this
commit (running it is a substantially larger compute/time investment than a
smoke-test-scale session, needs explicit go-ahead):
1. **Phase 1 — DONE (Entry 009).** Froze all region-routing parameters, ran 20
   held-out semiprime instances (13 completed, 65% completion rate, disclosed).
   Result: median headroom 0.0%, mean 3.9%, 2 audited outliers traced to sampling
   noise, not online-predictable. Verdict: region-choice-within-a-single-polynomial
   routing is BLOCKED on distributional evidence, per the review's own stop rule
   (median < 5%, no predictable tail).
2. **Phase 2 — B5 oracle-first test:** define relation-utility oracles (Δrank,
   dependency membership, contribution to required nullity — explicitly retrospective,
   never usable online) and measure END-TO-END pipeline headroom (acquisition + filter
   + linear algebra + reconstruct), not just relation-count reduction.
3. **Phase 3 — deeper prior-art mapping** of real adaptive classical mechanisms
   (SIQS polynomial switching, special-q scheduling, large-prime variants, adaptive
   interval strategies) as (state → decision → cost/yield objective) tables, not just
   named citations.
4. **Phase 4 — residual headroom**, `H_residual = C_classical_adaptive - C_oracle`,
   distinct from naive headroom `H_naive = C_fixed - C_oracle` — since a classical
   adaptive baseline may already capture most of the naive-vs-oracle gap.
5. **Phase 5 — engineering decision gate:** only build a true multi-polynomial
   MPQS/SIQS instrumentation harness if `H_residual` is large enough, on the held-out
   distribution, to justify the engineering cost — explicitly NOT before that.

## Bottom line

Across every mechanism family actually tested at this session's scale, **no
computational advantage for the IDM framing over classical factoring practice was
observed** — several formulations reduce to classical technique (sometimes
undisclosed in the original proposal text), and one (RSA-04) is an outright false
claim under its natural reading. Two threads remain genuinely open but require
substantially more engineering than a smoke test to evaluate honestly. This is
reported as the current, falsifiable state of the evidence, not as a final closure of
the IDM research programme as a whole (per the reuse-pipeline discipline: a tested
hypothesis family failing is not evidence against untested families).
