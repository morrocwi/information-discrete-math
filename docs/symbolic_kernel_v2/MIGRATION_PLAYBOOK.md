# P1.7 Migration Playbook (ground map + review)

Produced by the migration-planning ultracode run (wf_ad2c356b-ed0). NOTE: 13 of the per-family
plan agents were rate-limited by the API server (not a usage limit) and did not return; the
GROUND family map below (which is the load-bearing artifact) completed in full, and the scope
conclusion is unambiguous from it.

## Scope conclusion

Per ARCHITECTURE.md §5, Phase-1 migration scope is ONLY the ~6 symbolic_* handlers; every other
family maps to kernel_target "none/keep" with migratability=defer because its source module
(exact.py / functions.py / integrate.py / analysis.py / special.py / series.py / diffeq.py /
discrete.py / algebra.py) is explicitly listed UNCHANGED in the design. So a byte-identical
migration today is intentionally narrow.

## Family map (all 259 kinds accounted for)

| family | #kinds | current module | kernel target | migratability |
|---|---|---|---|---|
| constants & core expression eval | 3 | idm/functions.py | none/keep | defer |
| certified series/limits core | 3 | idm/certified.py | none/keep | defer |
| numerical integration (DE quadrature) | 7 | idm/integrate.py | none/keep | defer |
| discrete calculus / root-finding | 10 | idm/functions.py (derivative, limit, ode) + idm/analysis.py (the rest) | none/keep | defer |
| number theory core | 18 | idm/exact.py | none/keep | defer |
| exact linear algebra core | 6 | idm/exact.py (matrix_multiply/determinant/inverse/solve_linear) + idm/analysis.py (char_poly, eigenvalues) | none/keep | defer |
| polynomial evaluation/roots | 3 | idm/exact.py (poly_eval, rational_roots) + idm/analysis.py (poly_roots) | idm/kernel/poly/ (orthogonal wave, not wired to these kinds in Phase 1) | defer |
| graph path semirings | 6 | idm/algebra.py | none/keep | defer |
| readouts aggregator | 1 | idm/readouts.py | none/keep | defer |
| number theory extended | 20 | idm/exact.py | none/keep | defer |
| polynomial algebra (ring ops) | 8 | idm/exact.py (poly_add..poly_from_roots) + idm/positivity.py (polynomial_positivity) | idm/kernel/poly/ (orthogonal, not wired in Phase 1) | defer |
| matrix extended (exact ℚ) | 6 | idm/exact.py | none/keep | defer |
| geometry exact (ℚ + √) | 6 | idm/exact.py | none/keep | defer |
| analysis extended | 5 | idm/analysis.py | none/keep | defer |
| discrete structures / graph theory | 8 | idm/discrete.py | none/keep | defer |
| differential equations (ODE/PDE) | 7 | idm/diffeq.py | none/keep | defer |
| limits & series (numeric, finite-difference) | 9 | idm/series.py | none/keep | defer |
| special functions | 29 | idm/special.py | none/keep | defer |
| transforms & complex analysis | 9 | idm/transforms.py | none/keep | defer |
| continuous optimization | 5 | idm/optimize.py | none/keep | defer |
| symbolic exact CAS (Phase-1 migration target) | 6 | idm/symbolic.py | idm/kernel/rewrite.py (diff/simplify/expand/integrate/taylor spine) + idm/kernel/solution.py (solve, for symbolic_solve) + idm/kernel/eval.py and idm/kernel/assumptions.py as supporting dependencies | clean |
| P1 number theory advanced | 7 | idm/exact.py | none/keep | defer |
| P1 linear algebra advanced | 4 | idm/exact.py | none/keep | defer |
| P1 DP / combinatorial optimization | 5 | idm/combopt.py | none/keep | defer |
| P1 graph advanced | 6 | idm/combopt.py | none/keep | defer |
| P1 LP / logic | 2 | idm/combopt.py | none/keep | defer |
| P1 rigorous interval certification | 5 | idm/interval.py | none/keep | defer |
| P2 statistics & probability | 14 | idm/stats.py | none/keep | defer |
| P2 computational geometry (exact predicates) | 6 | idm/geometry.py | none/keep | defer |
| P2 cryptographic number theory | 7 | idm/crypto.py | none/keep | defer |
| H1 Hilbert-space core (finite-dim) | 23 | idm/hilbert.py | none/keep | defer |
| +R-Open frontier readouts (fenced, non-certified) | 5 | idm/hilbert_open.py | none/keep | defer |

## Notable findings

- **number theory core**: exact.py is explicitly UNCHANGED per §2. FACTUAL FINDING (independent of migration): exact.py also defines @kind("binomial","Th_coqc") at solve.py:144-145 (X.binomial, C(n,k)), but _REG is a plain dict and the later @kind("binomial") at solve.py:659-660 (stats.py pmf/cdf) silently overwrites it, so idm.kinds() lists 'binomial' only once and solve({'kind':'binomial',...}) always dispatches to the stats handler (verified by running it; matches tests/test_idm_api.py:343 which asserts the pmf-shaped result). The exact.py combinatorics binomial handler is dead/unreachable code today — not caused by
- **symbolic exact CAS (Phase-1 migration target)**: THE ONLY family ARCHITECTURE.md §5 scopes for Phase-1 migration: 'every one of the six pillars independently converged on this exact scope boundary'. Binding invariant: zero new kinds, zero new _COQ_BACKED entries, @kind/_REG/_norm/_ok mechanism in solve.py NOT edited — only these 6 handler BODIES are repointed, as the single last step (§5 item 8), after building kernel/tiers+hashcons+nodes+numbers -> kernel/legacy -> kernel/assumptions -> kernel/engine+rewrite -> kernel/eval -> kernel/solution -> kernel/poly (parallel-buildable), each new/additive with zero existing-file edits, verified modul
- **P2 statistics & probability**: 'binomial' here is the LIVE handler (solve.py:659-660, ST.binomial pmf/cdf) that wins the registry collision described in the number-theory-core family above; stats.py not named in ARCHITECTURE.md.

## Adversarial review (separate team)

# Adversarial Review — P1.7 Migration Playbook

## Finding 1 [HIGH] — Headline claim overclaims completeness that §3b itself disproves

**Claim:** Overview says *"every kind was routed to its true verdict (DEFER, all 259 surveyed so far)"* and *"Net finding: zero kinds are migratable today"* — stated with full confidence, in bold, as the document's thesis.

**Contradiction:** §3b admits **13 of the 21 surveyed families have no kind-level list at all** — not even a per-family count (only "differential equations" gets a count: 7). By the document's own arithmetic (157 named in §3a + 7 named in ODE/PDE = 164), that leaves **~95 of 259 kinds (≈37%)** with zero visibility — no names, no counts, nothing to check against a fixture. §3b even says this ledger "can[not] be called complete at the kind level" until someone runs a follow-up `grep` and appends the missing rows.

**Failure scenario:** A maintainer reads only the Overview (as most will), takes "all 259 surveyed" and "zero migratable" at face value, and closes P1.7 as a fully-audited defer-everything phase. Six months later someone discovers one of the 95 unnamed kinds in, say, "exact linear algebra core" or "polynomial algebra (ring ops)" actually *does* have a viable kernel target (these are exactly the families most likely to overlap with the kernel's existing `poly/` and scalar-number tower) — and it was never individually checked, only assumed-DEFER by pattern-matching from unrelated families.

**Fix:** Overview must state coverage honestly up front, e.g. *"164/259 (63%) kinds individually verified DEFER with a named blocking gap; the remaining 95 across 13 families are DEFER-by-family-report only, not yet kind-level confirmed — see §3b action item."* Do not let the "zero migratable" framing imply exhaustive kind-level coverage it doesn't have.

## Finding 2 [HIGH] — Self-contradiction on whether `simplify` already has a live kernel route

**§4** states flatly: *"the 6 symbolic_* kinds... have **no** kernel route today (confirmed: `idm/kernel/rewrite.py` doesn't exist...)"* and lists `simplify` among the group whose byte-identical guarantee is "trivial... because nothing changed."

**§2, readiness queue item #4** states the opposite for the same kind: *"this one is already partially wired: `idm/symbolic.py`'s `(bᵃ)ᶜ→b^(ac)` collapse already calls `idm.kernel.engine.pow_pow_collapse_safe(...)`, gated dormant..."* — i.e. `simplify` **does** have an existing kernel call site today, just conditionally inert.

These can't both be true. This isn't pedantic: the whole point of criterion (1) — "could a batch change observed output without the byte-identical gate catching it" — depends on knowing precisely what code paths already touch the kernel. If the gate condition (`assumptions is not None`) is ever flipped by *unrelated* work (a different PR touching the registry handler, not this playbook), `simplify`'s output could silently change and this playbook's "nothing to diff" reasoning gives false comfort, because it asserted the wrong premise for this one kind.

**Fix:** Carve `simplify` out of the "no kernel route" group in §4 exactly as `symbolic_solve` already is; state explicitly that it has a *pre-existing dormant* kernel dependency, and that its byte-identical guarantee rests on that gate condition staying `False` — which this playbook does not control and should flag as a standing watch-item, not a solved fact.

## Finding 3 [MEDIUM] — Dormancy claim is asserted, not independently re-verified in this synthesis

The claim that `pow_pow_collapse_safe` is "never triggered by the current registry handler" comes from a sub-team survey with no line citation, no grep output, no test evidence quoted in this merge document — a single unverified assertion being used to justify "no further action needed." This is precisely the trap this org's own diagnosis discipline warns about (single observation ⇒ trusted conclusion, no re-check). **Fix:** before treating item #4 as closed, independently grep the call site and confirm the guard condition is actually unreachable from the live registry path, and cite it (file:line) in the playbook.

## Finding 4 [MEDIUM] — A real tier-honesty flag surfaced in §2 is missing from §5's dedicated flag roundup

Readiness-queue item #2 (`interval_enclose`) surfaces a genuine pre-existing issue: *today's* production tier for `interval_enclose` reads `exact`, while the kernel's `evaluate_certified` bridge — evaluating the same underlying `mpmath.iv` engine — always tags results `finite_diagnostic`. That's a real signal the current (unmigrated) tier label may already be too generous. But §5's "pre-existing tier-honesty quirks... flagged for visibility only" list names `closest_pair`/`in_circle`/`least_squares`/`sat`/"several P1 kinds" and **omits `interval_enclose`**. A reviewer scanning §5 specifically for tier concerns (its stated purpose) will miss this one. **Fix:** add `interval_enclose` (with cross-reference to readiness-queue #2) to §5's list.

## Finding 5 [MEDIUM] — Future-queue "disjoint file, parallel-safe" claim rests on unverified line numbers

`symbolic_solve` (idm/solve.py:552-556), `interval_enclose` (640-642), `characteristic_poly` ("H1 block") are cited to justify running items 1-3 in parallel once unblocked. These numbers come from the 21 source surveys, not a fresh read at merge time, and the queue explicitly won't be acted on until an unspecified future date after prerequisite kernel work lands (which will itself edit files, plausibly including `idm/solve.py`). Line ranges drift. **Fix:** state explicitly that these ranges are point-in-time and MUST be re-derived (`grep -n '@kind("symbolic_solve"'` etc.) at the moment the queue is actually opened, not trusted from this document — otherwise two future contributors could genuinely collide on `idm/solve.py`.

## Finding 6 [LOW] — "≈250+" is imprecise and compounds Finding 1

259 − 4 (flagged-close items) = 255, but of those, only ~161 are actually *named* (157 + ODE/PDE's implied but unlisted 7 ≈ 164 minus overlaps); the rest are the same ~91-95 unnamed kinds from Finding 1. "≈250+" reads as confident but is really "some known, some unknown, lumped together." Minor on its own, but makes the coverage gap in Finding 1 harder to audit by inspection.

## Finding 7 [LOW] — Unconfirmed possible near-duplicate kind names

`gershgorin` (P1 rigorous interval certification) vs. `gershgorin_bound` (H1 Hilbert-space core) are listed as two distinct kinds in two different families, with no one-line confirmation they're actually different operations (vs. a naming collision/typo). Given the review's explicit "no kind in two batches or none" check, this should get an explicit one-line disambiguation rather than being left implicit.

## What checked out fine

- **Scope/RAM realism (5):** Batch 0 is genuinely trivial (one markdown file, no code touched); the full-suite-once cadence is explicitly and correctly deferred to "once, optional, before merge," matching the standing no-repeated-full-arc-audit rule.
- **File-ownership for the *executing* batch (4):** Batch 0 owns only its own doc; no contention possible since it's the only batch that runs. (The future-queue parallelism claim is where the real risk sits — Finding 5.)
- **No forced/premature migration, no tier inflation, no new kinds invented** — §5's core disclaimers are consistent with the rest of the document (modulo Findings 2 and 4 above).
- The 157-kind tally in §3a is internally arithmetically consistent with the document's own stated "157 kinds named" header.

---

## VERDICT: SOUND-WITH-FIXES

The engineering decision itself — defer everything, touch zero implementation files, keep legacy paths intact — is safe and appropriately conservative; there is no real code-regression risk in what this phase *executes*. The problems are entirely in what the document *claims about its own coverage and internal consistency*, which matters a lot given this org's explicit horizontal-honesty standard (no silent overclaim, name every deferral with a real reason). Do not merge as a "complete honesty record" until fixed.

**Top 5 must-fix items:**
1. Fix the Overview's "all 259 surveyed" claim to disclose the ~95-kind (13-family) coverage gap named in §3b (Finding 1).
2. Reconcile §4 vs. §2 on whether `simplify` has an existing kernel route — it does; stop grouping it with the "no route" siblings (Finding 2).
3. Independently re-verify (don't just repeat) the claim that `pow_pow_collapse_safe`'s gate is unreachable from the live `simplify` handler (Finding 3).
4. Add `interval_enclose` to §5's pre-existing tier-honesty flag list (Finding 4).
5. Mark the future-queue line-number citations as point-in-time-only, to be re-derived fresh whenever that queue is actually opened (Finding 5).