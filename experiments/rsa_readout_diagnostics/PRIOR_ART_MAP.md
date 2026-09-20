# Classical Adaptive Routing Map — Phase 3

**Method note:** searches used field vocabulary only (no "IDM"/"readout"/"routing"
framing terms), per the discipline that vocabulary bias must not contaminate the
search. Sources are cited per finding; secondary web-search summaries are marked as
such and not treated as verbatim quotes from the underlying papers unless the paper
itself was read directly (none were opened in full text this pass — flagged as a
depth limitation, not hidden).

---

## A. Classical Adaptive Map (state → decision → action → objective)

### Layer A — Candidate/polynomial generation

| Technique | State observed | Decision | Action | Objective |
|---|---|---|---|---|
| **Murphy's E-score polynomial selection** (NFS/GNFS) | Candidate polynomial's coefficients, root properties mod small primes, size properties — computed WITHOUT sieving | Rank candidate polynomials by E(F) score, descending | Select/commit sieving effort only to top-ranked polynomials | Maximize expected relation yield per unit sieve cost, minimize matrix dimension |

**Overlap severity: HIGH architectural overlap; different information source (predictive structural score, not observed-execution feedback)** — corrected per Phase 3B code audit (`PHASE3B_CODE_AUDIT.md`), which found CADO-NFS's own `adjust_with_estimated_yield` is the SAME category (predictive, pre-sieve estimate), reinforcing that this layer's classical norm is predictive routing, distinct from the observed-execution-feedback question this project actually cares about most. This is a cheap, pre-computed proxy signal
that predicts downstream yield BEFORE paying the expensive sieve cost, then routes
computational effort accordingly — structurally the same shape as the
main.hub-inspired routing sketch (`s_t -> cheap signal -> a_t -> avoid paying full
cost on bad candidates`). Same information-type input (structural properties
computable cheaply), same decision variable (a score), same objective (yield per
cost), same action consequence (commit or skip expensive work). **Classical, decades
old (Murphy 1999).**

Sources: [Polynomial selection in NFS for integer factorization](https://www.sciencedirect.com/science/article/pii/S2213020916300210), [Murphy's PhD thesis, ANU](https://maths-people.anu.edu.au/~brent/pd/Murphy-thesis.pdf), [Root optimization of polynomials in NFS](https://arxiv.org/pdf/1212.1958).

**Caveat (depth limitation, disclosed):** Murphy's E-score is computed and applied
*before* sieving starts (an offline/precomputed ranking), not necessarily updated
using *live, within-run* observed yield from sieving already-in-progress candidates.
Whether classical practice also does live-feedback re-ranking mid-run was not
confirmed either way in this search pass — flagged as an open question, not a gap
claim (see Residual Candidates below).

### Layer B — Sieve-allocation adaptation

| Technique | State observed | Decision | Action | Objective |
|---|---|---|---|---|
| **Special-q / lattice sieving** (NFS) | A chosen special-q ideal defines a lattice of (a,b) pairs | Partition the search space by special-q, process each independently | Sieve each special-q's lattice region | Enable "almost infinite" parallelism, cover the candidate space systematically |

**Overlap severity: MEDIUM.** This IS a form of routing (choosing where to spend
compute), but the search evidence found describes special-q processing as
embarrassingly parallel and independent ("each special q is handled completely
separately... with no overhead") — i.e. a systematic partition/schedule, not an
online yield-feedback-driven choice of *which* special-q to prioritize based on
observed results from other special-q's. No evidence found (this search pass) of
special-q selection being reordered mid-run based on live yield.

Sources: [Relation collection using Pollard special-q sieving](https://link.springer.com/article/10.1007/s11227-020-03351-6), [A New Angle on Lattice Sieving for NFS](https://arxiv.org/pdf/2001.10860), [cuda-sieve implementation](https://github.com/kyleaskine/cuda-sieve).

**Smoothness-bound (B) tuning:** "a very small bound may fail to yield enough
relations and a large bound results in an unwieldy matrix" — this is parameter
selection, generally done from N's size via known formulas ahead of the run, not
demonstrated as a live within-run adaptive loop in the sources reviewed.

### Layer C — Verification adaptation

| Technique | State observed | Decision | Action | Objective |
|---|---|---|---|---|
| **Single/double large-prime variation** | Residual cofactor size after trial-division against the factor base | If residual ≤ 1 or 2 factors in (B, B²], accept as a PARTIAL relation instead of discarding | Retain partial relation; later combine matching partials (cycle-finding) into full relations | Increase usable relation yield "at no extra cost" beyond what full trial division already produced |

**Overlap severity: adjacent classical design space / HIGH conceptual overlap** (corrected per Phase 3B audit point 9 — the two mechanisms share a state-dependent framing but differ in semantics: RSA-08 certifies a safe DROP, large-prime variation RETAINS partial information for later combination) to any state-dependent
accept/certify/retain-partial-information hypothesis (directly adjacent to our
BLOCKED RSA-08 DropSafe family and to the general "retain vs. discard based on
current state" framing). Documented: "It is always better to use the single
large-prime variation than not to use large primes at all... partial relations found
at no extra cost." Double large-prime gives ≈2.5× speedup for sufficiently large n,
and beats single-large-prime past ~80 digits.

**Retrospective attribution correction (per review point 7):** RSA-08's DropSafe
family and this large-prime variation both make a state-dependent
accept/reject/retain decision on a partial-factorization residual. They differ in
what they certify (DropSafe = an EXACT proof the residual is unfactorable further
via primality; large-prime variation = a SIZE-BOUNDED acceptance that stores the
partial information for later combination rather than requiring full smoothness at
all). This is disclosed as a closely related classical mechanism family, not
identical, but close enough that RSA-08 should be read as sitting in a crowded,
decades-old design space, not an unexplored one.

Sources: [Factoring with Two Large Primes](https://www.researchgate.net/publication/266349860_Factoring_with_Two_Large_Primes), [Factoring Integers with Large-Prime Variations of the QS](https://projecteuclid.org/download/pdf_1/euclid.em/1047565445).

### Layer D — Relation-retention adaptation

Same mechanism as Layer C (large-prime variation) — the retention decision and the
verification decision are the same act in this literature (accept-as-partial IS the
retention decision). No separate distinct retention-layer technique was found beyond
this in this search pass.

### Layer E — Matrix/filtering adaptation

| Technique | State observed | Decision | Action | Objective |
|---|---|---|---|---|
| **Singleton removal / clique removal / structured Gaussian elimination / merge** | A prime/ideal's occurrence count across all collected relations; matrix sparsity structure | Remove a relation whose unique prime can never cancel (singleton); remove excess rows via the clique/union-find rule; merge light columns under a fill-in bound | Delete/merge relations and columns before the expensive linear-algebra step | Reduce matrix dimension and reduce fill-in, minimizing linear-algebra cost |

**Overlap severity: HIGH**, structurally similar to any "B5a-style" post-acquisition
relation-utility hypothesis — but per our OWN Entry 010 finding, this entire layer
operates on a cost component (downstream: filter+LA+reconstruction) that is 3–4
orders of magnitude smaller than acquisition cost in every instance we measured. So
even though this classical technique is mature and effective, it is optimizing a
budget that (in our own measurements) barely matters to end-to-end cost — consistent
with, and independently reinforcing, Entry 010's BLOCK verdict for B5a.

Sources: [Parallel Structured Gaussian Elimination for NFS](https://hal-lirmm.ccsd.cnrs.fr/LORIA-ALGO/hal-02098114v2), [CADO-NFS documentation](https://github.com/doublegate/cado-nfs-modern/blob/main/docs/number-field-sieve.md).

---

## B. Overlap Audit

| IDM/main.hub-inspired hypothesis | Classical analogue found | Same info input? | Same decision variable? | Same objective? | Same action consequence? | Verdict |
|---|---|---|---|---|---|---|
| "Score a candidate cheaply, route effort before paying full cost" (Layer A routing sketch) | Murphy's E-score polynomial ranking | Yes | Yes (a score) | Yes (yield/cost) | Yes (commit/skip expensive work) | **REINVENTION RISK: HIGH — classical, near-identical mechanism, decades old** |
| "Accept/retain partial state-dependent information instead of requiring full completion" (RSA-08 DropSafe family, general shape) | Single/double large-prime variation | Partially (both look at residual state) | Different (primality certificate vs. size-bounded acceptance) | Similar (avoid wasted/duplicated work) | Similar (retain instead of discard) | **REINVENTION RISK: HIGH — closely related classical family, not identical mechanism** |
| "Retrospective relation-utility oracle changes downstream cost" (B5a) | Singleton/clique/structured-Gaussian filtering | Yes | Similar | Yes | Similar | **HIGH overlap, AND independently shown cost-irrelevant by our own Entry 010** |
| "Live within-run yield feedback reorders which region/candidate to process next" (Track C region-choice, and the open Layer B question above) | Special-q partitioning (parallel, not feedback-reordered per evidence found); no live-feedback mid-run polynomial reordering confirmed in sources reviewed | Not confirmed either way | Not confirmed either way | Similar in spirit | Not confirmed either way | **PRIOR-ART GAP CANDIDATE — not identified in sources reviewed so far (see below)** |

---

## C. Residual Information / Decision Space

Two questions, per review point 16, before any mechanism is proposed:

1. **What state variables does classical adaptive practice already observe?**
   Polynomial structural/root properties (pre-sieve, via Murphy's E); partial-
   factorization residual size (large-prime variation); prime/ideal occurrence
   counts across the collected relation pool (filtering). All three are used to make
   an accept/route/retain decision.
2. **What state remains apparently unobserved in the sources reviewed?**
   **Live, within-run, observed sieve-yield data used to re-rank or abandon a
   polynomial/candidate mid-run**, as opposed to (a) a pre-computed structural score
   (Murphy's E, computed once, before any sieving) or (b) an embarrassingly-parallel
   partition (special-q, no cross-region feedback). No source reviewed this pass
   described using "this polynomial/region is already underperforming its predicted
   score, abandon it early" as a live decision rule.

This is stated per review point 21's required wording: **not identified in sources
reviewed so far** — not "novel," not "unexplored," given the limited search depth
(9 targeted queries, no full-text papers read end-to-end).

---

## D. Residual Questions (max 3, per review point 24 cap)

### Residual Question 1 — Live within-run yield-feedback polynomial re-ranking

- **Gap:** using observed relation yield *during* sieving of polynomial P₁ to decide
  whether to abandon P₁ early (even though Murphy's E ranked it well) in favor of a
  lower-E-scored but empirically-hotter alternative, or vice versa.
- **Evidence:** absence in the 9 searches run this pass (Layer A/B rows above);
  Murphy's E is described as a pre-sieve screen, special-q as independently
  parallel — neither source describes live cross-candidate feedback.
- **Why potentially useful:** if Murphy's E has meaningful residual prediction
  error (real yield ≠ predicted E-rank order), live data could in principle correct
  for it before wasting sieve effort on a mis-ranked candidate.
- **Why not already classical (tentative):** E-score is cheap and apparently
  effective enough that practitioners may not have needed within-run correction —
  this is a plausible, not proven, explanation for the absence.
- **Additional evidence (negative search, per review point 20):** practitioner-level
  documentation around CADO-NFS/msieve states plainly that "predicting in advance the
  yield for a range of (a,b) pairs is hard" — a direct admission from
  implementation-adjacent sources that Murphy's E-style pre-screening is imperfect,
  not a solved problem. This strengthens (does not confirm) Residual Question 1's
  plausibility: if yield prediction were already easy/solved, there would be little
  room for a live-feedback correction to add value. Source: [CADO-NFS/msieve README/talk material](https://magix.lix.polytechnique.fr/magix/magixalix/slides/magix_thome.pdf).
  No source reviewed (this pass) describes a live within-run feedback mechanism that
  closes this admitted prediction gap — consistent with "not identified in sources
  reviewed so far," not "does not exist."
- **Cheap falsifier:** our own Track C evidence (Entries 008/009) already provides
  a *partial* falsifier for the SAME underlying question at the region-noise level:
  median headroom for "which sub-region to search first" was 0%, and outliers were
  traced to un-predictable sampling noise. The remaining open question is whether
  this holds at the POLYNOMIAL level (where Murphy's E gives real structural
  signal, unlike same-polynomial regions which don't differ structurally) — a cheap
  test would be a 2-polynomial (not full MPQS) synthetic harness: generate two
  polynomials with different Murphy's-E-like root-count scores, sieve both a small
  amount, and check whether early partial yield reliably predicts final yield well
  enough to justify early abandonment decisions net of the decision's own cost.
- **Engineering cost: MEDIUM.** Needs correct multi-polynomial generation (not a
  single `x²-N`), which is more than a region split but far short of a production
  SIQS/MPQS implementation.

### Residual Question 2 — None identified with an engineering cost below MEDIUM

No other candidate gap survived the overlap audit above with a plausible headroom
story: Layer C/D (large-prime variation) is near-identical classical machinery;
Layer E (filtering) is classical AND cost-irrelevant per our own Entry 010; Layer B's
smoothness-bound tuning is a static pre-run parameter choice in the sources
reviewed, with no clear "live feedback" story or plausible large headroom given it's
a single scalar tuned once per run, not a per-candidate decision.

*(Fewer than 3–5 gaps reported, per review point 24's own allowance — a shorter,
honest list, not padded to hit a count.)*

---

## E. Engineering Verdict

$$
\boxed{\textbf{HOLD}}
$$

**Reasoning:** Classical adaptive factoring practice already implements
near-identical mechanisms for 3 of the 4 layers we hypothesized about (candidate
scoring, state-dependent partial-information retention, downstream filtering) —
this is NOT a "dense literature therefore stop thinking" closure (review point 22
explicitly forbids that); a specific residual question (Residual Question 1) survives
the overlap audit with a stated cheap-ish falsifier and a real, not fabricated,
structural difference (Murphy's E gives genuine polynomial-level structural signal,
unlike the noise-dominated single-polynomial region choice we already tested and
blocked). But: (a) the falsifier itself needs a 2-polynomial harness — a real,
non-trivial engineering step beyond anything built so far in this project, not "free
to check"; (b) our own strongest piece of adjacent evidence (Track C) suggests this
class of live-feedback-based routing tends to run into a chicken-and-egg problem
(you must pay much of the cost to observe the signal that would justify not paying
it) even where structural variance genuinely exists; (c) search depth this pass was
shallow (9 queries, summaries not full papers) — before building anything, the
specific unresolved question ("does classical MPQS/SIQS/GNFS practice use live
intra-run yield feedback for polynomial switching, in implementation practice
beyond what indexed papers describe") deserves a deeper, primary-source check
(implementation docs/code of CADO-NFS, msieve, or similar established software) —
this is a reading task, not a build task, and should happen before the Candidate
Gap 1 falsifier is built.

**This is not a "yes, build it" and not a "no, fully closed" — it is a specific,
narrow, honestly-scoped open question with a defined but not-yet-executed next
step.**
