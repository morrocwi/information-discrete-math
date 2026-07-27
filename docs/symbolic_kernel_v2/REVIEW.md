# Adversarial Review — IDM Symbolic Kernel v2 Merged Architecture

## Ranked Findings

### 1. [CRITICAL] Domain-correctness gap masquerading as "the fix" — 2 of 3 named live bugs are left confidently wrong, and silently so

§1 asserts, as the motivating problem, that today **none** of the six `symbolic_*` kinds gate three specific unsafe identities: `(x^a)^b → x^(ab)`, `sqrt(x²)→|x|`, `log(ab)→log a+log b`. But wave 2 (item 11) ships `RS_CORE_NORMALIZE` with **exactly one rule**: `pow_pow_collapse`. Nothing in the design gates `sqrt(x²)→|x|` or `log(ab)` splitting.

Worse: §7's "Explicitly deferred to Phase 2 (named, not silently dropped)" list — which the document itself holds up as its transparency mechanism — does **not** mention the sqrt/log identities at all. They are simply absent, which is precisely the "silently dropped" failure the section header claims to avoid.

**Failure scenario:** After Phase 1 ships and `symbolic_simplify`/`symbolic_integrate` are re-pointed to the kernel, a caller runs `simplify(sqrt(x**2))` for a symbol `x` with no assumption declared. Nothing in Phase 1 stops the legacy code path from still returning `x` (dropping the `|x|`), and nothing in the migration marks this as HOLD — because the fix machinery (Guard/domain_gate) was only wired to the pow-case. The document's own headline claim ("domain-unsafe rewrites become structurally impossible to add ungated") is false for two of the three bugs it named as the reason this pillar exists.

**Fix:** Either (a) add `sqrt_even_root` and `log_product` to the Phase-1 gated ruleset (they're small, single-rule additions using the same `domain_gate` machinery already built for pow), or (b) explicitly list them in §7's deferred section with the same honesty given to Gröbner/Risch/nonlinear-systems, and strike or soften the §1 claim that this design "closes" the domain-unsafe-identity problem.

---

### 2. [HIGH] Migration-safety narrative self-contradicts on its own regression test

§5 states as a hard invariant: "steps 1–7 touch zero existing files" and item 21 (step 8) is "the ONE edit to an existing file in all of Phase 1." But item 12 (wave 2) explicitly edits `idm/symbolic.py`'s `simplify()` pow-case internally to call `rewrite_safe`. That's a second edit to an existing file, contradicting §5's own accounting.

More seriously, item 12's stated test is: *"`symbolic.simplify(e)` (no kwarg) is byte-identical to today's output on the existing `symbolic.py` test fixtures."* But the entire point of wiring `rewrite_safe` into the pow-case is to stop the **unconditional** collapse that §1 names as the live bug. If `rewrite_safe` is called with `assumptions=EMPTY` (the default) and correctly refuses to fire absent a proof of safety, then for any existing fixture that exercised the unconditional collapse, output changes — it can't be simultaneously "the fix" and "byte-identical to today."

**Failure scenario:** CI either (a) passes item 12's stated test, meaning the fix is a no-op for the default (no-kwarg) path and the named live bug is still live for every caller who doesn't explicitly opt in with `assumptions=`, or (b) the fix actually changes default behavior and item 12's own acceptance test as written fails, undermining trust in every other "byte-identical" claim in §5/§7 (including item 21's, which is load-bearing for the whole "registry keeps working during migration" argument).

**Fix:** State explicitly which of the two is intended. If it's "no-kwarg path is unchanged, fix is opt-in only," say so plainly and stop describing this as closing the `symbolic.py:117` defect. If it's "default behavior changes for the unsafe case," rewrite the acceptance test to assert byte-identity only on the *safe* subset of fixtures and explicit HOLD on the unsafe ones.

---

### 3. [HIGH] "One-kernel thesis" is a Phase-1 *aspiration*, not a Phase-1 *result* — real risk of becoming the 259th subsystem

The design is honest in the small print (§5, §7) that only 6 of 258 kinds move, and that migrating the other 252 is "explicitly deferred" with no plan, timeline, or even rough sizing. But the framing in §1 ("collapse the substrate underneath all 258 kinds onto one shared kernel") and the document's title/thesis language read as if this is what's being delivered. At the close of Phase 1, the codebase has **seven** substrates, not one: the original six (`symbolic.py`, `exact.py`, `interval.py`, `functions.py`, `crypto.py`, `analysis.py` — all explicitly "UNCHANGED") plus the new `idm/kernel/` package, used by exactly 6 of 258 kinds.

**Failure scenario:** Phase 1 ships, gets adopted, and — as with most "Phase 2 later" plans — the other 252 kinds never migrate because there's no forcing function, no owner, no budget named anywhere in this document for that work. `idm/kernel/` becomes a permanent, additional, parallel subsystem alongside the six it was meant to replace — the exact "259th kind" failure mode the design claims to avoid, just one level down (a 7th substrate instead of a 259th kind).

**Fix:** Either commit to a Phase-2 migration plan (even a rough wave order and kind-count target) in this document, or reframe §1's thesis honestly as "Phase 1 proves the pattern on 6 kinds; the unification claim is conditional on a committed Phase 2/3/… migrating the rest," and stop using unconditional language ("collapse... onto one shared kernel") for what is currently a 2.3%-of-kinds pilot.

---

### 4. [MEDIUM-HIGH] "Structurally impossible to add ungated" is not backed by any structural mechanism shown

Nothing in `kernel/engine.py`'s `Rule`/`RuleSet`/`Pattern` design (as specified) prevents a future author from registering a `Rule` with no `Guard` at all. `Guard.check()`'s fail-closed `UNKNOWN→HOLD` behavior only fires if a `Guard` is attached in the first place; there is no shown mechanism (a required field, a linter, a classifier of "domain-sensitive pattern shapes") that forces one. The one gated rule shipped (`pow_pow_collapse`) demonstrates the *mechanism* works, not that it's *mandatory*.

**Failure scenario:** A Phase-2 contributor adds `RS_TRIG_SIMPLIFY` with a rule for `arcsin(sin(x))→x` and forgets a Guard (an easy mistake — this identity is false outside `[-π/2,π/2]`, in whatever discretized sense IDM represents that range). Nothing in the type system or registration path catches this; it ships as confidently wrong, and the document's own claim that this can't happen is the reason nobody double-checks.

**Fix:** Downgrade the claim from "structurally impossible" to "mechanism exists, convention-enforced, not yet statically enforced," or actually build the enforcement (e.g., `RuleSet.register` requires an explicit `guard=None` opt-out with a lint/review flag, or a maintained allowlist of pattern-shapes known to be domain-safe unconditionally).

---

### 5. [MEDIUM] `AmbientDomain` reuses raw continuum labels (`C`, `R`, `Q_`, `Z`) without redefining them in readout terms

§3/§8(R8) renames three of the four colliding `Domain` concepts carefully, but `AmbientDomain{C,R,Q_,Z}` keeps symbols that read exactly like "the complex numbers," "the reals" — the very I1/non-readout vocabulary §4's table is built to police everywhere else in the document. Nothing in §3 or §6 states what `AmbientDomain.R` cashes out to operationally (an `AlgebraicNumber`/`RealBall` result tower? a search restricted to real leaves? something else).

**Failure scenario:** `solve(eq, "x", domain=AmbientDomain.R)` is called; a caller (or a future implementer under deadline pressure) reads "R" as license to reach for `mpmath`/float machinery "because it's real numbers," reintroducing exactly the silent-float-contamination path R6 was written to close — because the enum's *name* invites continuum thinking even though the rest of the kernel forbids it.

**Fix:** Rename to something that names the readout behavior, not the classical set (e.g. `AmbientDomain.REAL_READOUT`), or at minimum add one sentence pinning each enum value to which `Number` rungs a `Solution` may report under it.

---

### 6. [MEDIUM] Layout/todolist mismatch: two poly files are declared but never scheduled

§2's module tree lists `kernel/poly/algebraic.py` and `kernel/poly/multivariate.py` as part of the Phase-1 package. §7 wave 5 (items 18–20) only builds `coeffring.py`, `univariate.py`, and `GFRing`. There is no item anywhere for `algebraic.py` or `multivariate.py` bodies, and they aren't in the "explicitly deferred" list either.

**Failure scenario:** Someone treats §2 as the source of truth for "what Phase 1 delivers," imports `kernel.poly.algebraic`, and finds an empty or stub module with no corresponding test — a small instance of the same "claimed but not built, not disclosed as deferred" pattern as finding #1, just in the poly tower instead of the rewrite rules.

**Fix:** Either add build items for these two files to wave 5, or move them into §7's explicit-defer list, or drop them from §2's Phase-1 tree entirely (create them empty/`NotImplementedError`-stub only when Phase 2 needs them).

---

### 7. [MEDIUM] Feasibility/ROI: large net-new surface for a 6/258-kind payoff, no sizing given

Phase 1 as scoped is ~14 new modules including several genuinely nontrivial subsystems for a from-scratch build in one phase: a hashcons/interning layer, a ball-based `AlgebraicNumber` with a precision-re-isolation contract, a monotone-closure assumption/predicate engine with its own termination argument, and a cost-based multi-strategy rewrite search engine (`search_paths`). Individually each is reasonably scoped (§7's items are small and testable), but the aggregate is a serious undertaking, delivered for a functional delta of exactly 6 kinds out of 258, with no engineer-week estimate, staffing, or calendar anywhere in the document.

**Failure scenario:** Phase 1, taken as literally scoped, quietly becomes a multi-month effort with no way to tell from this document whether that's proportionate — and finding #3 (no Phase 2 plan) means there's no visibility into when the other 252 kinds start seeing any return on this investment.

**Fix:** Attach even a rough size/time estimate per wave, or explicitly flag in the document that sizing is out of scope for an architecture doc and belongs in a separate planning artifact — right now the document's confident, fully-detailed todolist format implicitly suggests "this is ready to schedule," which the doc's Chief-architect framing doesn't actually support without a size estimate.

---

### 8. [LOW-MEDIUM] `InternTable` memory bound is asserted, not specified

Item 2/§6 claims the `InternTable` is "bounded by the same LoopGuardConfig-style caps," but no concrete cap (max entries, eviction policy) is given anywhere. "Request-scoped, discarded after" bounds lifetime, not peak size within one request.

**Failure scenario:** A single `expand()` call on a moderately large polynomial-in-several-variables produces enough structurally-distinct intermediate subtrees to blow request memory before any `LoopGuardConfig.max_steps` check fires (step count and distinct-subtree count aren't the same quantity) — the design has a named guard for *iteration count*, not for *interned-object count*.

**Fix:** Give `InternTable` its own explicit cap (e.g., `max_entries`) with a defined behavior on overflow (HOLD with `ResourceBudgetExceeded`, per the R9 internal-exception pattern already established).

---

### 9. [LOW] R9's "never raise across the public boundary" has one unexamined exception

`closure()` is specified to raise `DomainContradiction` as a "caller error." But a contradiction can arise not just from a single obviously-malformed call, but from the *composition* of caller-declared facts with `domain_of_expr()`-inferred implicit facts (e.g., caller says `x: negative` for unrelated reasons, kernel infers `x: nonneg` from a `sqrt(x)` subterm elsewhere in the same expression). That's a legitimate "this system has no solution under these constraints" finding, not obviously a programming mistake — yet it's the one place in the whole spine that raises instead of returning a HOLD/CERTIFIED-contradiction result.

**Fix:** Reconsider whether externally-triggerable contradictions (inferred-vs-declared, not just declared-vs-declared) should return a `status=HOLD, reason="contradictory assumptions"` result instead of raising, to keep the "safe to call directly" property R9 claims for the rest of the spine.

---

### 10. [LOW] R6's "removes the silent-float-contamination door structurally" is asserted ahead of the code that would deliver it

§6's `ExactRational`/`ExactInteger` dataclasses show no arithmetic operators (`__add__`, etc.) in the skeleton — understandable for a stub, but the Reconciliation Ledger's present-tense claim ("P1.6's typed wrapper... removes that door structurally") describes a guarantee that doesn't exist in any code shown yet; it exists only if every future arithmetic method on these types is written to route through `coerce_up`/`coerce_down` and never falls through to bare `Fraction`/`float` ops, which is a discipline claim, not (yet) a structural one.

**Fix:** Either show the operator stubs with their coercion discipline in §6 (even as `NotImplementedError` bodies with the contract in the docstring), or soften "structurally" to "by convention, enforced at the operator-implementation layer described in Phase 1 item 4."

---

## VERDICT: **SOUND-WITH-FIXES**

The reconciliation discipline (§3's Ledger), the tier/status orthogonality (R2/R5), the mandatory `LoopGuardConfig`, the request-scoped interning, and the return-not-raise public contract (R9) are unusually rigorous for a merged six-pillar design — this is not a shallow document. But it has one real correctness bug in its migration story (#2), one honesty gap that directly contradicts its own stated principles (#1), and one load-bearing claim (#3, the one-kernel thesis) that is true only as a long-term intention with no committed path, not as a Phase-1 deliverable. None of these require re-architecting the kernel itself — they require narrowing claims to match what's actually being built, or extending Phase 1's scope by a small, well-understood amount (two more gated rules).

### Top 5 must-fix before this goes to implementation sign-off:

1. Gate `sqrt(x²)→|x|` and `log(ab)` splitting in Phase 1 (or explicitly move them to the deferred list) — closing the gap between §1's stated problem and §7's actual delivery.
2. Resolve the item-12 contradiction: decide and state whether the pow-case fix changes default (no-kwarg) behavior, and fix the "byte-identical" test claim accordingly.
3. Reframe the one-kernel thesis as conditional on an actual Phase-2+ plan, or add a minimal one — stop implying Phase 1 delivers unification when it delivers a 6-kind pilot.
4. Either enforce (statically or via required review gate) that every domain-sensitive `Rule` carries a `Guard`, or downgrade "structurally impossible to add ungated" to an accurate description of a convention-enforced mechanism.
5. Fix the §2/§7 mismatch on `poly/algebraic.py` and `poly/multivariate.py` (schedule them or defer them explicitly) to keep the document's "everything deferred is named" promise intact.