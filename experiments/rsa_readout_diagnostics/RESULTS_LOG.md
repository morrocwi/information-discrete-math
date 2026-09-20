# IDM-RSA experiment results log (append-only — never edit or delete an entry)

Status banner: every object below is **PROPOSAL — NOT CANONICAL**, intended Toledo slot
only, per `TG-RFG-01`. Nothing here is a registered Toledo equation or a proved theorem.
This file lives in the session scratchpad (Milestone 0 — freezing formal statements and
registering intended slots in the real Toledo proposals registry — has not happened yet);
it is not part of the `information-discrete-math` repo.

---

## Entry 001 — PROP-IDM-RSA-08 (Exact Safe-Drop Criterion), intended slot A3/M.20.v1

**Verdict: DRIFT**

**Claim tested:** DropSafe_N(c|s) formalized as "residual cofactor is a probable prime
strictly greater than the largest factor-base prime ⇒ certified non-smooth, safe to drop
without further trial division" — hypothesized to reduce total smooth-relation-acquisition
work relative to a classical numeric-threshold early-abort heuristic.

**Method:** `smoke_dropsafe_vs_sieve_threshold.py`. Three/four arms sharing one relation
generator and factor base: FULL (ground truth, no early exit), HEURISTIC (classical
numeric-threshold early abort), DROPSAFE-exact (Miller-Rabin, 8 rounds), DROPSAFE-bounded
(Miller-Rabin, 1/2/4 rounds, quantified worst-case error bound 4^-k). Cost measured as
division ops + certificate (modular-exponentiation) ops, counted separately, never
aggregated in a way that hides which channel paid.

**Result (3 trials, N ≈ 10^8, 10^10, 10^12; 3000–6000 candidates each):**
- DROPSAFE-exact: 0/0/0 false rejects (provably safe, as designed) — but total ops
  (div+cert) were **178,883 / 79,699 / 355,189**, all *higher* than HEURISTIC's
  **63,800 / 17,064 / 262,462** on the same inputs. DROPSAFE-exact never won.
- HEURISTIC itself false-rejected 5 genuinely-smooth candidates in the N≈10^10 trial
  (uncalibrated numeric threshold — a real correctness bug in the classical baseline,
  logged for completeness, not defended).
- DROPSAFE-bounded (traded safety down to 1 Miller-Rabin round, worst-case error bound
  25% per event): total ops **172,171 / 69,953 / 338,337** — still higher than HEURISTIC
  in all three trials (2.7×–5.4×), with 0 empirical false rejects observed over the
  tested sample (an observation, not a proof — the theoretical bound is far looser than
  what was seen).
- Reducing Miller-Rabin rounds from 8→1 shaved only 20–40% off the certificate-cost
  component; it never closed the gap to HEURISTIC, because the cost asymmetry is
  mechanism-level (one modular exponentiation vs. one bit-length comparison), not
  round-count-level.

**Conclusion:** PROP-IDM-RSA-08, in every tested formalization (exact and
safety-traded), costs more total work than the classical heuristic it was meant to beat,
even though it is provably safer. It does not deliver the claimed computational
advantage in this test. Consistent with the earlier structural finding that RSA-08
reduces to a known classical implementation trick ("early abort with a primality
check"). **Reported as DRIFT, not re-tuned to hide the result.**

**Artifacts:** `smoke_dropsafe_vs_sieve_threshold.py` (scratchpad). Raw run output not
separately saved; script is deterministic (seeded) and reproducible on demand.

---

## Entry 002 — PROP-IDM-RSA-04 (Retain-Recompute-Resolve Gate), intended slot A3/M.18.v1

**Verdict: DRIFT (falsified under the natural operational reading; not confirmed vacuous)**

**Claim tested:** the contrapositive form `F_N(T_u(s))!=F_N(T_u(t)) => R_N(s)!=R_N(t) or
Q_N(s)!=Q_N(t) or C_N(s)!=C_N(t)`, equivalently the forward direction actually load-bearing
for engineering use: if two computation states agree on (R_N,Q_N,C_N), their eventual
factor-certificate outcome must agree. Flagged in the prior session review as carrying an
unresolved **vacuity risk** (possibly true only because R/Q/C are defined to already
encode the answer).

**Method:** `smoke_rsa04_rrr_gate_vacuity.py`. Built REAL mid-pipeline states (not
hand-faked) from the same trial-division code path used elsewhere in this log, under two
independent readings of (R_N,Q_N,C_N):
- **Reading 1 (coarse scalar counters)** — R_N = count of distinct factor-base primes
  that divided the candidate so far, Q_N = division ops spent so far, C_N = 0 (resolve
  channel not yet invoked). This is the operational reading actually used by RSA-05's
  cost fold elsewhere in this research line.
- **Reading 2 (full local content)** — R_N = the actual exponent-parity vector (mod 2)
  over the tested prefix, per RSA-07's rho_B encoding — richer than a scalar count.

For each reading, grouped real candidates by identical (R_N,Q_N,C_N) key and checked
whether any group contained candidates with DIFFERENT eventual smoothness outcomes
(F_N ACCEPT vs. not) — a direct counterexample to the claimed implication.

**Result (3 trials, N ≈ 10^8, 10^10, 10^12):** the gate was **falsified under both
readings, in all three trials** — every trial produced multiple groups with identical
(R_N,Q_N,C_N) but divergent eventual outcomes (e.g. the all-zero parity-vector group —
"none of the tested prefix primes divided the candidate" — split into both smooth and
non-smooth outcomes in every trial, since the untested suffix of the factor base still
determines the result independently).

**Conclusion:** RSA-04, under the definitions of R_N/Q_N/C_N actually used elsewhere in
this line (scalar cost counters, or even a richer local parity vector), is a **false
claim**, not a tautology — it is genuinely informative that cost/local-content summaries
do not determine the eventual outcome, because information about factor-base primes
outside the tested prefix is independently load-bearing and is not captured by either
reading. The theoretical concern that a "genuinely sufficient" R_N would have to encode
as much as finishing the computation (making the gate vacuous rather than useful) remains
an open question this test did not close — it only shows two natural, cheap-to-compute
readings both fail. **Reported as DRIFT.**

**Artifacts:** `smoke_rsa04_rrr_gate_vacuity.py` (scratchpad), deterministic/reproducible.

---

## Entry 003 — PROP-IDM-RSA-05 (Total Computational Cost Fold), intended slot A2/M.29.v1

**Verdict: NO ADVANTAGE SHOWN IN THIS INSTANCE (not falsified — scope-limited negative result)**

**Claim tested:** does explicitly accounting for the recompute channel (argmin C_N(q))
ever pick a DIFFERENT, better representation than the naive baseline of minimizing
stored bits alone (argmin |q|)? Concrete instance: retaining only the mod-2 parity
vector per relation (q_PARITY, small storage, needs recompute if later selected) vs.
retaining the full integer exponent vector (q_FULL, larger storage, zero recompute).

**Method:** `smoke_rsa05_cost_fold.py`. Real Dixon-style relation acquisition against a
real factor base, real GF(2) nullspace search for the combining subset, real recompute
(re-trial-division) cost measured only on the subset actually selected. Exchange-rate
sweep (alpha = cost per recompute-op in retained-bit units), not a hidden constant.

**Result (2 of 3 trials completed; 1 trial hit a 200k-candidate search cap and is
reported INCONCLUSIVE, not silently dropped):**
- Selected combining subset size was consistently **tiny (1 relation)** relative to the
  total relations retained (49 and 65 in the two completed trials).
- Because q_PARITY's storage saving is paid across ALL retained relations while its
  recompute cost is paid only on the tiny selected subset, argmin C_N(q) agreed with
  naive argmin |q| (q_PARITY won) across every tested exchange rate from alpha=0.001 to
  alpha=10 — the crossover point where q_FULL would win was alpha* ≈ 130–195, many
  orders of magnitude above any realistic bit-vs-division-op cost ratio.

**Conclusion:** in this concrete instance, RSA-05's cost-fold accounting does **not**
change the decision a naive storage-minimizing heuristic already makes — it does not
demonstrate the "semantic minimality != computational minimality" divergence the
framework was meant to expose. This is a scope-limited negative result, not a
falsification of the framework itself: **the retain/recompute tradeoff tested here is
too lopsided (selected-later fraction ≈ 1/50–1/65) to ever make the two criteria
disagree.** Per the reuse-pipeline discipline (a hypothesis-set failure is not evidence
against the whole programme), this narrows the search: the next test needs a decision
point where the "selected later" fraction is large, not small — not yet identified.

**Artifacts:** `smoke_rsa05_cost_fold.py` (scratchpad), deterministic/reproducible
(one trial capped at 200k candidates and reported INCONCLUSIVE rather than hung).

---

## Entry 004 — PROP-IDM-RSA-08 family, Generation-2 (STAGED gate) + cost-model audit + closure

**Hypothesis H2:** a gate-conditional certificate (only pay for Miller-Rabin when a
cheap size-check flags the residual cofactor as implausibly large) reduces total cost
relative to unconditional DropSafe-exact, potentially beating classical HEURISTIC.

**Derived from failure F1 (Entry 001):** exact/bounded certificate paid unconditionally
on every candidate past the prefix, most of which didn't need it.

**Mechanism:** `smoke_rsa08_gen2_staged.py` — STAGED arm, same primality-certificate
mechanism as Entry 001's DROPSAFE-exact, gated by the classical heuristic's own
bit-length threshold (never used as a rejection rule itself — only as a "is it worth
buying the certificate" trigger). Zero false rejects preserved by construction (falls
through to safe full division whenever the certificate doesn't confirm primality).

**COST-MODEL AUDIT (raised by project review, applied before any further
interpretation):** the prior report summed `div_ops + cert_ops` as commensurable
units. This is invalid — measured via `calibrate_costs.py` (`timeit`, 200k reps,
operand sizes matching this test's own N/cofactor scale): **one modular-exponentiation
round costs ≈32.85× one division/modulo operation** (1195.9ns vs 36.4ns, this
machine). Recomputing Entry 001/002's raw counts with this calibrated weight:

| N | HEURISTIC (=1.00×) | DROPSAFE-exact | STAGED |
|---|---|---|---|
| ≈10^12 | 1.00× | 8.82× | 7.47× |
| ≈10^8  | 1.00× | 32.70× | 32.33× |
| ≈10^10 | 1.00× | 4.82× | 2.81× |

**Corrected result: the true cost gap is LARGER than the uncorrected scalar-sum
report suggested (previously understated as 2.8–5.4×; calibrated reality is
2.8–32.7×).** STAGED's ~1–60% cut in certificate *call count* (Entry 004's own
Generation-2 run) is real and directionally correct (cutting the now-properly-weighted
expensive operation matters more than the naive sum implied), but insufficient to
approach HEURISTIC's cost in any trial.

**Mechanism-space closure reasoning (why no further local variant was attempted):**
the constraint-refinement analysis requested by review — formalizing `BuyCert(x)=1 iff
E[S(x)|φ(x)] > C_cert(x)` — was checked against the one remaining lever proposed
(amortized/batched certificate cost across candidates): **no valid batching mechanism
exists for primality certification across distinct moduli** in the tested scheme.
Miller-Rabin's dominant cost (`pow(a,d,n)`) is intrinsically per-modulus; unlike batch
trial-division (Bernstein product trees, which amortize *divisibility* testing across
many candidates against a shared prime set), there is no analogous shared computation
for *primality* certificates of different, unrelated cofactors. A cheap Fermat
pre-screen was analyzed (not implemented, since the reasoning already rules it out):
a Fermat-composite verdict does **not** license a safe drop (compositeness ≠ absence of
a factor-base-prime factor — the reviewer's warning in point 5 is directly confirmed by
this analysis), so it cannot replace or precede the primality certificate the mechanism
actually depends on. The existing Miller-Rabin implementation already early-exits on
the cheap case (composite cofactors, usually 1 round); the expensive, unavoidable case
(genuinely-prime cofactors, which is exactly the case DropSafe needs to certify) has no
shortcut in this scheme.

**Classical overlap:** STAGED-gate = a version of documented "early abort with a
primality fallback" implementation practice; no component identified as IDM-specific
novelty beyond a restatement of this practice under the readout/DropSafe vocabulary.

**Pareto-frontier statement (safety vs. calibrated cost, both completed generations):**
HEURISTIC — cheapest, but NOT safe (5 real false rejects observed in Entry 001's
N≈10^10 trial). DROPSAFE-exact / STAGED — safe (0 false rejects across all trials,
both generations) but 2.8×–32.7× more expensive than HEURISTIC in calibrated cost. No
tested variant is safe AND cost-competitive.

**Verdict: BLOCK — PROP-IDM-RSA-08 family (primality-certificate-based DropSafe) is
blocked under the tested mechanism model.** This is a family-scoped closure, not a
closure of readout-conditioned pruning in general, and not a claim about IDM as a
whole (per the reuse-pipeline discipline — a hypothesis-family failure is not evidence
against the programme). Claim ceiling: `empirical` (measured on 3 instances, this
machine, this implementation) — not `finite_diagnostic` or `Th_coqc`, and not claimed
to generalize beyond the tested regime without further evidence.

**Artifacts:** `calibrate_costs.py`, `smoke_rsa08_gen2_staged.py` (scratchpad).

---

## Entry 005 — Track B, Entry 1: relation-acquisition boundary A (candidate generation /
## factor-base construction) — QR-restricted factor base

**Hypothesis H_B1:** primes where N is a quadratic non-residue can never appear in any
relation's factorization; trial-dividing candidates by them is provably wasted work.

**Mechanism:** classical QR (Legendre-symbol) factor-base restriction — the standard
practitioner technique (textbook Dixon/QS), explicitly labeled **CLASSICAL**, not an
IDM claim. Tested here to (a) quantify its real magnitude and (b) audit whether prior
entries in this log used a representative classical baseline.

**Result (2 of 3 trials completed; 1 hit the candidate cap, reported INCONCLUSIVE):**
QR-primes were ≈45–56% of all odd primes below the bound (matches ~50% theory). Using
the QR-filtered factor base to reach its OWN (smaller) target relation count needed
**3.64×–5.23× fewer total division operations** and 2.06×–2.92× fewer candidates
examined than the unfiltered factor base needed to reach its own (larger) target.

**Methodological finding (not itself a research result, but load-bearing):** every
prior entry in this log (001–004) used an **unfiltered** factor base on both arms of
each internal comparison — those internal comparisons remain valid (both arms shared
the same, consistently weaker, factor base), but the absolute "HEURISTIC is the
classical baseline to beat" framing was against a weaker-than-practice control. Since
QR-filtering only reduces cost further (making the classical baseline cheaper still),
this **strengthens** Entry 004's BLOCK verdict rather than undermining it — DropSafe/
STAGED's gap to real classical practice is at least as large as reported, likely
larger.

**Classical overlap:** fully classical, no IDM content claimed at this boundary.

**Claim ceiling:** `empirical`, 2 of 3 planned instances (1 inconclusive, reported not
hidden).

**Next Track B entries (not yet run):** Entry 2 — real practitioner acquisition uses a
SIEVE (O(1) amortized array increments per candidate per prime) rather than per-
candidate trial division; this log's own `full_trial_divide`-based acquisition cost
model is itself a weaker classical control than a real sieve implementation — needs
the same disclosure/correction pass Entry 005 just gave the factor base. Entries for
boundaries B (evidence reuse across candidates), C (batch/shared structure), D
(relation utility beyond bare smoothness), E (deferred reconstruction, already
partially covered by Entry 003/RSA-05) remain open, per the reviewer's mandated
decomposition — not yet attacked.

**Artifacts:** `track_b_entry1_qr_filter.py` (scratchpad).

---

## Entry 006 — Track B, Entry 2: baseline hierarchy B0/B1/B2 + bottleneck location

**Hypothesis:** a real sieve-based acquisition baseline (B2) will beat candidate-by-
candidate trial division (B0/B1), and the resulting bottleneck decomposition will show
where a genuine next-generation mechanism should aim (per review mandate: measure,
locate bottleneck, THEN search prior art, THEN generate a mechanism — not the reverse).

**Mechanism (B2): SIMPLIFIED QS-LIKE SIEVE**, explicitly labeled simplified, not
standard — real components present: QR-filtered factor base (reused from Entry 005),
brute-force modular square roots, array-based log2(p)-weighted sieve over an interval,
thresholded flagging, verification via full trial division ONLY on flagged positions.
Disclosed omissions: single polynomial only (no MPQS), no prime-power (p^2, p^3, ...)
sieve contributions, one global threshold (not per-position tuned), no large-prime
variation, no duplicate/singleton handling. Labeled `SIMPLIFIED QS-LIKE BASELINE`,
not `STANDARD QS BASELINE`, per the reviewer's mandated honesty distinction.

**Cost model:** kept as a vector (N_div, N_sieve_updates, N_relations,
N_candidates_covered); calibrated via `timeit` on this machine: 1 division op ≈ 40.7ns,
1 sieve-array update ≈ 51.2ns — stated as **machine-specific empirical calibration**,
not a universal constant, per review point 11.

**Result (3 trials; 1 of 3 completed its relation-count target, 2 of 3 did not —
disclosed, not hidden):**

| N | Status | B2/B1 calibrated-time ratio | B2/B0 ratio | Bottleneck decomposition (B2) |
|---|---|---|---|---|
| ≈10^10 | **complete** (38/38 relations) | **0.157×** (sieve 6.4× cheaper than QR trial-division) | **0.043×** (23× cheaper than naive) | sieve-phase 93.3% / verify-phase 6.7% |
| ≈10^12 | incomplete (12/28) — hit interval cap | not computed (target unmet) | — | sieve-phase 99.8% / verify-phase 0.2% |
| ≈10^8  | incomplete (4/15) — hit interval cap; B0 also hit its own cap | not computed | — | sieve-phase 99.9% / verify-phase 0.1% |

**Known limitation (disclosed, not swept under):** the sieve interval cap (200k) was
too small for 2 of 3 trials to reach their relation targets — this needs a fix (larger
interval, or investigate whether the fixed global threshold under-flags candidates for
larger N) before those two instances count as completed evidence.

**KEY FINDING — answers the review's required question ("after moving to a sieve,
where did the bottleneck move?") consistently across all 3 trials, complete or not:**

$$
\boxed{\text{Bottleneck moved overwhelmingly to the SIEVE-UPDATE phase itself: 93.3\%–99.9\% of total cost, vs. 0.1\%–6.7\% for verification.}}
$$

**Implication for prior RSA-08/DropSafe family (Entries 001, 004):** that entire
mechanism family targeted **verification/certificate cost** — which this measurement
now shows is only 0.1–6.7% of total acquisition cost once a real sieve baseline is
used, not the dominant term it appeared to be against the weaker trial-division
baseline. This does not retroactively change the BLOCK verdict (which was already
correct on its own terms — DropSafe lost even against the weaker baseline), but it
explains WHY that family could never have delivered a large practical gain even if its
internal cost problems had been solved: it was aimed at a cost component that a
correctly-built classical baseline makes nearly irrelevant.

**Claim ceiling:** `empirical`, 1 of 3 instances complete, 2 of 3 partial but
directionally consistent. Explicitly NOT claimed to "scale" — no bit-size ladder run
yet (review point 13, still open).

**Next required step per the review's mandated order (Measure → Locate bottleneck →
Check prior art → Generate mechanism):** prior-art search on sieve-update-phase
reduction BEFORE any mechanism is proposed — this territory (large-prime variation,
self-initializing/SIQS sieving, lattice sieving, log-bucket sieving, wheel
optimization) is exactly where the review flagged the highest risk of
"IDM-reinterpretation-only" / confirmation bias (review point 9). Not yet done.

**Artifacts:** `track_b_entry2_baseline_hierarchy.py` (scratchpad).

---

## Entry 007 — Prior-art check on sieve-phase reduction (mandatory before any mechanism)

**Method:** WebSearch (live, cited below — not from training-memory recall alone,
per the readout-not-truth verification discipline).

**Finding, directly on point:** independent literature confirms our own empirical
measurement is the textbook-known state of the field, not a discovery: *"The
collection of smooth values is overwhelmingly the most time-consuming stage of both
MPQS and the Number Field Sieve"* — i.e. sieving IS the known bottleneck, exactly
matching Entry 006's 93.3–99.9% figure. This is reassuring methodologically (our
measurement is sane) and simultaneously a strong warning: **this exact bottleneck has
30+ years of dense, specific classical attack already published:**
- **Self-Initializing QS (SIQS)** — amortizes the per-polynomial root-computation
  setup cost across `2^r` sieving intervals via fast polynomial switching (Contini).
  About 2× faster than plain MPQS.
- **Large-prime variation** — allows a relation to have one or two prime factors
  between the factor-base bound and a larger "large prime bound," instead of requiring
  full smoothness — directly reduces wasted rejection of "almost-smooth" candidates.
- **Lattice sieving / special-q** (NFS) — reframes the candidate space as lattice
  points via Gauss-reduced bases per special-q ideal, a structurally different (not
  merely faster) way to generate candidates worth sieving.
- **Polynomial root optimization / selection** — chooses sieving polynomials with
  many roots mod small prime powers specifically to raise sieve yield.

**Conclusion: the sieve-update-phase bottleneck is not an open target — it is the
single most heavily optimized component in the entire classical factoring literature.**
Any mechanism proposed here must be checked against ALL FOUR of the above before any
novelty claim, per review point 9's explicit warning that this exact area is the
highest-risk zone for "IDM-reinterpretation-only."

**Verdict: HOLD — sieve-efficiency mechanism space, prior art dense and specific, not
yet exhausted-by-us but likely already exhausted-by-the-field.** Not blocked (we have
not tested anything here yet), but flagged as low-expected-value for a "first
principles IDM" attack without deep engagement with the SIQS/NFS literature itself —
proposing a naive variant here risks reinventing one of the four techniques above under
new vocabulary.

**Redirect (per reviewer's own Family list, point 8):** Family B5 (utility-conditioned
retention: "smooth ≠ useful," relation marginal contribution to downstream rank) is a
different axis from sieve efficiency — worth checking next — but ALSO has dense prior
art flagged explicitly by the reviewer (singleton removal, structured Gaussian
elimination, relation filtering) and must get the same prior-art-first treatment before
any mechanism is generated there.

**Sources:**
- [Self-initializing quadratic sieve - Prime-Wiki](https://www.rieselprime.de/ziki/Self-initializing_quadratic_sieve)
- [Factoring Integers with the Self-Initializing Quadratic Sieve (Contini)](https://www.researchgate.net/publication/2331506_Factoring_Integers_with_the_Self-Initializing_Quadratic_Sieve)
- [A New Angle on Lattice Sieving for the Number Field Sieve](https://arxiv.org/pdf/2001.10860)
- [Root optimization of polynomials in the number field sieve](https://arxiv.org/pdf/1212.1958)
- [The Quadratic Sieve Factoring Algorithm (Landquist)](https://www.cs.virginia.edu/crab/QFS_Simple.pdf)

**Provenance correction (Phase 3 audit, per review point 31):** the quoted phrase
above ("the collection of smooth values is overwhelmingly the most time-consuming
stage...") was a WebSearch-tool synthesized summary, not a verbatim quote confirmed
from a specific named paper's text — it should have been flagged as paraphrase, not
quotation. It is now independently, more directly corroborated in Phase 3 (see
`PRIOR_ART_MAP.md`/`SOURCES.md`) by a practitioner-adjacent source (CADO-NFS material)
stating plainly "NFS computation time is mostly spent on sieving" — closer to a
primary/implementer-level claim. The underlying finding stands; the citation
discipline for the first version did not meet this project's own bar and is corrected
here rather than left uncorrected.

---

## Entry 008 — Track C, Entry 1: Layer A Oracle Headroom for readout-conditioned routing

**main.hub-inspired experimental framing** (explicitly not claimed as prior art or a
Toledo object): `s_t -> Pi(s_t, Q) -> a_t -> T(s_t,a_t) -> s_{t+1}`, tested for its
narrowest, most tractable instantiation before any policy is built, per the review's
mandated order (Lens Note -> ... -> Oracle headroom -> ... -> policy).

**Lens Note (required before hypothesis):** terminal readout Q = enough relations for
a GF(2) nullspace; retained state s_t = relations found so far + regions sieved;
candidate actions = which of K contiguous sieve regions to process next; no action
changes Q itself, only the path-cost to reach it; full exponent vectors remain
bookkeeping until selected (per Entry 003).

**Hypothesis (Layer A only):** does an omniscient retrospective oracle (choosing
which of K pre-sieved regions to consume, best-yield-first) save meaningfully more
total cost than the naive fixed (index-order) schedule, on the SAME finite window?

**Harness (SIMPLIFIED, disclosed):** single polynomial `x^2-N` (NOT true MPQS/multiple
polynomials — a materially larger engineering lift, not attempted here). K contiguous
candidate regions of fixed width, each fully sieved+verified (reusing Entry 006's B2
sieve mechanics) to compute a retrospective (relations_found, cost) pair per region.
This tests only "which region to search first," not real polynomial-switching
headroom — an explicitly weak, disclosed proxy for the real question.

**Result — INCLUDES A METHODOLOGICAL SELF-CORRECTION, not hidden:**
- First pass (`slack_bits=3`, matching Entry 006's threshold): 1 of 3 instances valid
  (2 inconclusive — insufficient relations in the tested window, reported not
  papered-over). The valid instance (N≈10^10) showed **27.8% headroom**.
- On inspection this appeared driven by uneven relation-detection sensitivity across
  regions from an overly strict verification threshold, not real yield variance — so
  the threshold was loosened (`slack_bits=6`) and the SAME instance was rerun before
  any interpretation was finalized.
- With the corrected threshold, the same instance's headroom **dropped to 0.8%**.
  Inspecting per-region yields explains why: the region closest to sqrt(N) (smallest
  cofactor magnitude, highest smoothness probability — classical, well-known) already
  has the best yield, and the naive index-order schedule already searches it FIRST.
  There is no ordering mistake for an oracle to fix.

**Verdict (CORRECTED per review audit — see amendment below): LOW HEADROOM SIGNAL,
region-choice-within-a-single-polynomial routing.** The original wording of this entry
claimed "headroom ≈ 0%" as if structurally settled. That overstates what one completed
instance can support. Corrected status: this is a **DROP CANDIDATE, not yet a
universally confirmed BLOCK** — the classical reason given (search near sqrt(N) first
already captures most yield structure) is a plausible explanation for the single
observed instance, not an empirical replacement for a proper distribution study
(n≥20–50 held-out instances, frozen parameters, no post-hoc tuning). That study has not
been run yet (flagged as Phase 1 in the follow-up plan, not yet executed as of this
entry). This is not evidence that "readout-conditioned routing" in general has no
content — real MPQS/SIQS-style polynomial-switching (Entry 007's prior-art find) is a
structurally different action family (switching the actual polynomial/lattice, not
just which contiguous region of one polynomial to search) and its headroom remains
untested; building that testbed is a materially larger engineering task than this
scratch harness, and per review discipline should not be started before the cheap
distribution study is done and a genuine "classical-adaptive" baseline (P1, not just
naive P0) is defined and subtracted out (residual headroom, not naive headroom).

**Reflexive note (explicitly flagged, since this is exactly the audit's watch-list
item "using a weak baseline / measurement artifact without noticing"):** the initial
27.8% figure would have been a false positive for "IDM/routing content" had it been
reported without the follow-up correction. This is logged as a positive example of
catching a spurious headroom result before it propagated into a mechanism claim.

**Claim ceiling:** `empirical`, n=1 valid instance (2 of 3 inconclusive — window sizing
issue, not evidence either way for those instances).

**Artifacts:** `track_c_entry1_oracle_headroom.py` (scratchpad).

**Amendment (epistemic-tier audit, applied before publication):** this entry's Lens
Note, when relayed in chat, described RSA-05 (Entry 003) as having "proved"
(`พิสูจน์แล้ว`) that full exponent vectors are unnecessary until nullspace selection.
That overclaims Entry 003's actual tier — it was one empirical representation
comparison on 2 completed instances, not a proof. Corrected framing: **"observed
sufficient in the tested construction"** (empirical tier), not "proved." Logged here
as a caught overclaim, not silently corrected.

---

## Entry 009 — Phase 1: Oracle Headroom DISTRIBUTION (n=20 held-out instances, closing Entry 008's n=1 gap)

**Why:** Entry 008's "≈0%" verdict from a single instance was flagged (correctly) as
overreaching — a distribution study was required before treating region-choice routing
as closed.

**Frozen parameters (declared before running, never adjusted after seeing output):**
`PRIME_LIMIT=300, MARGIN=4, K_REGIONS=10, REGION_WIDTH=4000, SLACK_BITS=6` (the
already-corrected value from Entry 008, not a new tune), semiprimes = product of two
random ~17-bit primes, `N_INSTANCES=20`, `SEED=20260920` (fixed, reproducible).

**Result:** 13/20 instances completed (65% completion rate — disclosed, not hidden;
7 instances were INCONCLUSIVE under the frozen window, not retried with a wider one).
Headroom distribution over the 13 complete instances: **min=0.0%, Q1=0.0%,
median=0.0%, Q3=0.4%, mean=3.9%, max=32.6%.** 7 of 13 instances showed exactly 0.0%
headroom.

**Outlier audit (per review point 4 — every outlier is a suspect before it's a
discovery), on the two instances >15% (32.6% and 16.2%):** per-region breakdown of the
32.6% instance shows region 0 (closest to √N) yielding 27 relations vs. 4–11 for other
regions (confirms the same classical explanation as Entry 008 — proximity to √N
dominates). The oracle's actual saving over naive came from a SECOND-ORDER effect: the
naive schedule (index order 0,1,2,...) collected slightly more relations than strictly
needed by continuing past the target inside region 2, while the oracle picked the
next-best-yielding region (region 4, yield 11) instead of the next-index region
(region 1/2, yield 9–10) and stopped exactly at target. This is **real, not a
threshold/measurement bug** (verified against the same corrected `SLACK_BITS=6`), but
it is **small-sample Poisson-like noise in per-region smoothness counts**, not a
structural, predictable pattern — which region gets lucky varies instance to instance
and is only knowable after paying the sieve+verify cost the mechanism would need to
avoid paying. This is exactly the "oracle confusion" failure mode flagged in the
review (retrospective knowledge ≠ online-observable signal).

**Verdict: Layer A/B closure for this action family, now on a real distribution, not
n=1.** Median headroom 0%, mean pulled up by noise-driven outliers that are not
online-predictable without incurring the cost they'd save. Per the review's own stop
rule (`median(H) < 5%` and no online-predictable tail pattern → HOLD/BLOCK without
building a policy): **region-choice-within-a-single-polynomial routing is BLOCKED
under the tested model, on distributional evidence.** Constraint for any next
candidate action family (per review point 19): it must offer alternatives with
genuinely distinct STRUCTURAL yield profiles (e.g. real polynomial-switching, where
different polynomials have different, in-principle-computable discriminant/root
properties) — not regions whose yield differs only by sampling noise around the same
underlying process.

**Claim ceiling:** `empirical`, n=13 complete of 20 attempted, one fixed bit-size
regime (~34-bit N), one machine. Not claimed to generalize to other bit sizes or to
real multi-polynomial action spaces.

**Artifacts:** `phase1_headroom_distribution.py` (scratchpad → repo).

---

## Entry 010 — Phase 2A: B5a cheap analytical ceiling (no oracle hierarchy built)

**Lens Note:** terminal readout is `1<g<N, g|N` (a valid factor certificate), NOT
"reached nullspace" or "matrix rank threshold" — those are necessary machinery, not
terminal success (per review point 9). B5a's action family: a retrospective oracle
that may keep/drop/reorder ALREADY-ACQUIRED relations only — it may NOT touch
acquisition, factor-base, or polynomial choice (per review point 11, oracle power must
match the tested family, or the result is inflated).

**Question (the only load-bearing one):** if this oracle made downstream cost
(filter + linear algebra + reconstruction + terminal gcd) exactly ZERO, how much of
END-TO-END pipeline cost would that save? `H_B5a^max = 1 - C_acquire / (C_acquire +
C_downstream)`.

**Method:** `phase2a_b5a_ceiling.py`. `C_acquire` measured identically to Entries
003/005 (real QR-filtered trial-division acquisition to target relations).
`C_downstream` = REAL timed wall-clock cost of (a) `gf2_nullspace_subset` (the same
unmodified, classical, no-novelty-claimed GF(2) elimination from Entry 003) on the
actual collected relations, 30-rep average, plus (b) real recompute cost on the found
subset, plus (c) a timed `gcd` call. Not estimated — measured.

**Result (3/3 instances complete):**

| N | C_acquire | C_downstream (LA+recon) | H_B5a^max |
|---|---|---|---|
| ≈10^12 | 48,912 μs | 7.8 μs | 0.016% |
| ≈10^8  | 60,696 μs | 3.6 μs | 0.006% |
| ≈10^10 | 14,683 μs | 10.0 μs | 0.068% |

Downstream cost is 3–4 orders of magnitude smaller than acquisition cost in every
tested instance. Even a PERFECT downstream oracle could not save a practically
meaningful fraction of total pipeline cost.

**Verdict: BLOCK B5a.** Max observed ceiling (0.068%) is far below the pre-declared
5% stop-rule threshold — decisively enough that building the full O0/O1/O2/O3 oracle
hierarchy (rank/nullity/factor oracles) the review specified was judged unnecessary;
the analytical ceiling already answers the question (per review point 4's own
allowance: "this may kill B5-posthoc without building anything"). No claim of "IDM
advantage" is made anywhere in this entry, per review point 25 — this is a
retrospective upper-bound calculation, nothing more.

**Constraint derived for the next hypothesis (per review point 18):** since
acquisition dominates cost by 3–4 orders of magnitude in every instance tested so far
(Entries 006, 009, 010 all agree), **any next mechanism must intervene UPSTREAM, in
the acquisition process itself, before the dominant cost is paid** — post-hoc
relation filtering/reordering (B5a) cannot matter regardless of how clever the
selection rule is. This motivates B5b (feedback-conditioned acquisition) as the
logical next candidate, not because "we still want to try something," but because the
cost map forces it.

**B5b status: HOLD, not started.** Per review points 19–20: B5b requires genuinely
structurally distinct acquisition-time action choices — and Entries 008/009 already
established that the current single-polynomial harness's only available choice
(which region to sieve next) has near-zero exploitable structure (it's sampling
noise, not a real branch point). Fabricating an artificial choice to give B5b
"something to route between" is explicitly forbidden (review point 8/failure mode
"choice fabrication"). A genuine B5b action space (e.g. real polynomial switching)
requires the Phase 3 (deep prior-art mapping) and Phase 4 (residual-headroom-vs-
classical-adaptive-baseline) work first — not yet done — before any engineering
investment in a larger harness is justified.

**Claim ceiling:** `empirical`, n=3/3 complete, same fixed bit-size regime as prior
entries. Not claimed to generalize to larger N or to pipelines with non-trivial
filtering (large-prime variants, singleton removal) that this harness never
implemented.

**Artifacts:** `phase2a_b5a_ceiling.py` (scratchpad → repo).

---
