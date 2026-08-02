# Finding: is "proof-theoretic/ordinal strength" a 5th injected infinity? (issue #104)

**Tier discipline used throughout**: `Th_coqc` (machine-checked here) / `finite_diagnostic`
(measured/searched, reproducible) / `Dr` (stance, narrative judgment) / `+ℝ-Open` (needs the
continuum to settle). Nothing below is `Th_coqc` — this is a philosophy-of-foundations question,
not a theorem.

## Provenance

Surfaced 2026-08-02 while reviewing a user-authored essay surveying three historical traditions
for naming unimaginably-large-finite-numbers (Greek/Archimedes-Kasner, Jain/asaṃkhyāta, Chinese
`數術記遺`), which closed by arguing that BB(n)-independence-from-ZFC (n=643, reduced from 745;
BB(5)=47,176,870 proved 2024 via Coq-BB5/bbchallenge) and Harvey Friedman's finite combinatorial
independence results are the strongest available candidates for "a fully finite mathematical
statement that cannot be settled without accepting actual infinity." All historical/numeric
claims in that essay were independently re-verified via web search against bbchallenge.org,
Wikipedia, and Googology Wiki and checked out (see chat transcript 2026-08-02); no factual errors
found there.

The question this finding addresses is narrower: **does that closing argument actually implicate
the same "infinity" this repo's `SKILL.md` already tracks (I1 ℝ-completeness, I2 infinite
divisibility, I3 infinite scale separation, I4 actual `+∞` — all continuum-flavored), or a
different one the framework has no name for yet?**

## Hypothesis (Dr)

I1–I4 are about the **continuum**. BB(n)-ZFC-independence and Goodstein/Kirby–Paris/
Paris–Harrington unprovability-in-PA live entirely in `ℕ`/`D` (finite Turing machines, finite
integer sequences) — nothing about them requires `ℝ`-completeness. What they require instead is
**proof-theoretic/ordinal strength**: induction beyond what a given system's axioms license
(transfinite induction to `ε₀` for PA; consistency-strength assumptions for ZFC-independent
BB(n)). Proposal: name this axis **I5**, keep it explicitly decoupled from I1–I4, so the
pre-write checklist's "diagnose which infinity" step has a correct answer for this class instead
of silently forcing it into I1–I4 or leaving it unclassified.

## Experiments run (before writing anything into SKILL.md/textbook)

**Exp. A — does an I5-without-(I1–I4) example exist?**
Web-search-verified: Gentzen (1936) proved PA's consistency over **primitive recursive
arithmetic** (no continuum, no reals, finitist base) **plus quantifier-free transfinite
induction to `ε₀`**; Ackermann's independent 1940s proof does the same via an ordinal notation
system. This is a real, textbook (Stanford Encyclopedia of Philosophy-adjacent) example of strong
ordinal/proof strength with **zero continuum apparatus**. — **CONFIRMED, strong.**

**Exp. B — does an (I1–I4)-without-I5 example exist?**
Web-search-verified: `RCA0` (reverse mathematics base system) has proof-theoretic ordinal `ω^ω`
— far weaker than even PA — yet, extended only to `WKL0`, already proves the Intermediate Value
Theorem and Heine–Borel on `[0,1]^n`, i.e. real-number-flavored statements, at low ordinal
strength. — **CONFIRMED, but weaker than Exp. A**: `RCA0`/`WKL0`'s "reals" are Cauchy sequences
with a computable modulus, i.e. already close to the *readout-style* ℝ this repo already accepts
(§ discrete number ladder), not the full classical LUB-completeness a realist means by I1. A
cleaner example (e.g. full second-order arithmetic `Z2`, which does prove classical
LUB-completeness, at an ordinal strength well below any large-cardinal-flavored theory) is a
sharper candidate but was not independently re-verified this pass — flagged as open, not claimed.

**Exp. C — self-audit: does IDM's own axiom-free-over-ℚ core already smuggle I5?**
`grep -rniE "ordinal|transfinite|epsilon_0|well.?founded|Acc |wf_ind" formal/*.v` → **0 real
hits** (the raw grep's apparent hits were all false positives on the accumulator variable name
`acc` in `fold_right`/`fold_left`, not the Coq `Acc`/well-founded-recursion machinery). The 194
machine-checked theorems use ordinary structural/primitive recursion only. — **CONFIRMED clean**:
no retrofit needed; I5 is a genuinely new axis for this repo, not a correction to existing proofs.

**Exp. D — falsifier search: does mainstream philosophy of math already treat these as one axis?**
Search returned an explicit statement that proof-theoretic ordinal strength and "actual infinity
in the continuum" address different questions (system strength vs. ontological status of infinite
collections) and that accepting one without the other is coherent. — **No falsifier found**, but
this was a single shallow search pass, not a literature review; tier this as `finite_diagnostic`,
not `Th_coqc`.

## Positive findings

1. The I1–I4/I5 split is not an invention of this conversation — it tracks a real, independently
   documented distinction in proof theory (ordinal analysis) vs. philosophy of the continuum.
2. Gentzen/Ackermann give a clean, citable, historically important example of I5-without-I1-I4
   (Exp. A) — strong enough to use in the textbook if this gets written up.
3. IDM's existing 194-theorem core is I5-clean (Exp. C) — adding I5 to the checklist is additive,
   not a retroactive admission of a gap in already-shipped proofs.

## Negative findings / caveats (do not silently drop these)

1. Exp. B's counterexample is soft — `RCA0`/`WKL0`'s reals are already readout-flavored, so it
   doesn't cleanly show "full classical I1 with weak I5." A sharper example is still open.
2. **Deeper open question (Dr, unresolved — flag, don't paper over)**: is I5 actually a *new*
   infinity, or just "which induction principles a system licenses over an already-accepted
   completed `ℕ`"? IDM already treats `D≅ℕ` as machine-checked and complete (§ discrete number
   ladder). A strict ultrafinitist could argue that accepting *any* induction principle stronger
   than what's needed for feasible computation — even ordinary PA induction, let alone `ε₀` — is
   already smuggling a completed-infinite-totality commitment, and that I5 is not a sibling of
   I1–I4 but a restatement of the same D-vs-completed-ℕ question IDM already settled by adopting
   `D≅ℕ`. This finding does **not** resolve that tension; it should be stated as an open dispute
   if I5 is added, not decided in the textbook's voice.
3. Exp. D is shallow (one search pass) — do not cite it as if a literature review was done.

## What's actually usable right now

- **Usable, low-risk**: record I5 as a named, explicitly-open axis (tier `Dr`) in the pre-write
  checklist and contaminated-concept table's surrounding text, *with* the Exp. B caveat and the
  ultrafinitist objection stated inline — not as a fifth settled row equivalent in confidence to
  I1–I4 (those are `Th_coqc`-adjacent via the discrete ladder; I5 is not).
- **Usable**: Gentzen/Ackermann (Exp. A) as the textbook's worked example when a BB(n)-style or
  Gödel-style independence result comes up — gives a correct, non-continuum diagnosis instead of
  defaulting to "this needs infinity" undifferentiated.
- **Not yet usable / still open**: a clean Exp. B counterexample; a real literature review for
  Exp. D; and the ultrafinitist objection in caveat 2, which is a live philosophical fork, not a
  closed matter.

## Recommendation

Merge this finding as a **doc-only, non-binding record** (this file). Do **not** edit
`SKILL.md`/textbook in the same PR — that edit, if made, should explicitly carry the caveats
above (especially caveat 2) rather than presenting I5 as I1–I4's equal. Founder call on whether
to promote I5 into the skill at all, given caveat 2 is unresolved.
