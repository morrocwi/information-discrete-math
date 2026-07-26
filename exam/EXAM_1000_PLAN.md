# EXAM-1000 — plan to measure Information Discrete Mathematics on 1000 external benchmark problems

**Goal.** Measure the efficacy of *our equations* (the discrete, readout-first framework) against **1000
external, independently-authoritative math problems**, under three separated roles (setter / solver /
grader), with a hard requirement: the solver must **translate each problem into our information language
FIRST, then solve with mathematics locked to that info-semantics** — no importing standard continuum
math or another framework (the grader enforces this). The exam is not just a scoreboard: it is the
driver for building the **interpret → translate → analyze → solve → verify** pipeline.

---

## 1. Data sources (แหล่งข้อมูล) — real, verifiable, machine-checkable answers

Use existing, canonical benchmark corpora that already ship **verified answers** (so the "benchmark is
wrong" risk is near-zero and grading can be automated). Prioritised by definite-answer verifiability:

| source | ~size | answer form | why | access |
|---|---|---|---|---|
| **MATH** (Hendrycks et al.) | 12,500 | `\boxed{}` closed form | competition problems, 5 difficulty levels, 7 subjects (algebra, number theory, counting/probability, geometry, precalc, intermediate algebra, prealgebra) | HuggingFace `hendrycks/competition_math` |
| **AIME** (1983–present) | ~1,000 | integer 0–999 | exact-match trivial to grade; genuinely hard | AoPS archive / HF `AI-MO/aimo-validation-aime` |
| **AMC 10/12** | thousands | multiple choice / integer | graded exactly; scales difficulty down | AoPS / HF datasets |
| **GSM8K** | 8,500 | integer | grade-school arithmetic floor (sanity band) | HF `gsm8k` |
| **OlympiadBench** | 8,476 | numeric/expression + some proof | olympiad-level, typed | HF `Hothan/OlympiadBench` |
| **Omni-MATH** | 4,428 | expression | olympiad, subdomain-labelled, auto-verifiable | HF `KbsdJames/Omni-MATH` |
| **PutnamBench** | ~1,700 | formal (Lean/Isabelle/Coq) + informal | proof-heavy edge; some have definite values | HF / repo |
| **NuminaMath-CoT** | ~860k | mixed | huge stratification pool | HF `AI-MO/NuminaMath-CoT` |
| **IMO / IMO Shortlist** | archive | mixed (values + proofs) | the hardest, for the proof-edge probe | official/AoPS |

**Note on access.** These are public research datasets (HuggingFace). If offline in this environment, the
setter phase imports from a locally-cached snapshot; otherwise a one-time fetch to `exam/data/`. We do
NOT let an LLM *invent* 1000 problems+answers (wrong-answer risk) — we IMPORT canonical ones.

## 2. Stratification (what the 1000 is made of)

Sample 1000 to span **subject × difficulty**, so the result is diagnostic, not a single number:

- **Subject (≈ per our chapters):** number theory · combinatorics/counting · algebra · sequences &
  series · precalc/analysis · discrete geometry · probability. (Synthetic-geometry *proof* problems are
  capped — they probe the framework's edge, not its core.)
- **Difficulty bands:** GSM8K/prealgebra (floor) → AMC → AIME → olympiad/Putnam (ceiling). ~200 per band.
- **Answer-type:** ≥ 80% must have a **definite machine-checkable answer** (integer / closed form / finite
  set) so grading is automated and objective; ≤ 20% proof-with-value for the edge probe.

## 3. Architecture — 3 roles that scale (and stay cheap on quota)

The v1 exam (10 problems, `wf_ee1ea5c1-e8c`) uses one agent per role per problem. That does **not** scale
to 1000 (would be ~3000 agent calls). The 1000-scale design:

- **SETTER = an import + stratified-sample pipeline (deterministic, not an agent).** Pull from the
  corpora above, tag subject/difficulty/answer-type, hold out the canonical answer. `exam/setter.py`.
- **SOLVER = agents, BATCHED, framework-locked.** Each agent call solves a small batch (e.g. 5) problems,
  each with the mandatory structure: **(a) info-language translation, (b) locked-math solve, (c) answer,
  (d) tier, (e) hit_limit**. Batching ~5/call ⇒ ~200 solver calls for 1000. Workers = sonnet (quota).
- **GRADER = automated first, agent-audited second.**
  - *Automated correctness* (`exam/grade.py`): exact-match / sympy-equivalence of the solver's boxed
    answer vs the canonical answer — **free, objective, all 1000**.
  - *Framework-compliance audit* (agents, SAMPLED): a stratified sample (e.g. 150 of 1000) of solver
    transcripts is graded by an independent agent for `used_our_framework` + `translated_first` — because
    the founder's law is that our math must be *used*, not paraphrased. Report the compliance rate with
    its sampling bound (never claim 1000/1000 compliance from a 150 sample — disclose the cap).
  - *Benchmark spot-check* (agents, small sample): re-verify a sample of canonical answers to bound
    dataset error.

This keeps total agent calls to a few hundred (batched solve + sampled audit), all on subscription quota,
while grading correctness on all 1000 for free.

## 4. The translate-first law, enforced (the point of the whole exam)

Every solver output MUST contain, per problem:
1. **`info_translation`** — the problem restated in retained-distinction / readout terms (Rule 0).
2. **`locked_solve`** — the solution using ONLY framework math (D_ε/I_ε/FTCC, L_R, the operator set,
   finite-ε readouts, exact ℚ, regularization-as-finite-readout), with each step tied to the info-meaning.
3. **`answer` · `tier` · `hit_limit`**.
The compliance auditor fails any solve that reaches the answer by standard continuum machinery and only
*relabels* it — that is bypass, not use.

## 5. Metrics (what we report — diagnostic, tier-honest)

- **Accuracy** overall + per subject + per difficulty band (heatmap).
- **Framework-compliance rate** (sampled, with bound) — the fraction genuinely translated-first + locked-math.
- **Tier distribution** of correct answers (Th_coqc / finite_diagnostic / Dr) and **`hit_limit` map** —
  exactly which problem types push the framework to `+ℝ-Open` (its honest edge).
- **Benchmark-rejection list** (dataset answers the spot-check flagged).
- **Failure taxonomy** — feeds §6.

## 6. From exam → pipeline development (the real deliverable)

The exam is the measurement; the product is a better **interpret → translate → analyze → solve → verify**
pipeline. Each failure class becomes a pipeline upgrade:
- translation failures ⇒ sharpen the info-language restatement stage (a reusable "problem → retained-
  distinction" translator, extending METHOD Rule 0 + §7.0).
- analysis failures ⇒ a diagnosis stage (which discrete tool/operator the problem maps to).
- solve failures inside scope ⇒ new tool/lemma (candidate new Coq witness).
- `hit_limit` cases ⇒ honestly logged as the `+ℝ-Open` frontier, not forced.

## 7. Phasing

1. **v1 (running now):** 10 problems, full 3-agent, establishes the baseline + shakes out the roles.
2. **v2:** wire `exam/setter.py` (import + stratify), `exam/grade.py` (auto-grade), batched solver — run
   100 as a scaled pilot; validate automated grading vs agent grading agreement.
3. **v3:** full 1000, stratified, auto-graded + sampled compliance audit → the diagnostic report.
4. **v4:** feed the failure taxonomy into the pipeline; re-run to show improvement.

## 8. Guardrails (from this project's standing rules)

- No paid API — subscription quota only (batching keeps calls low).
- Every production step independently reviewed; benchmark answers double-checked.
- Tier-honest: disclose the compliance sampling cap; never overclaim; `hit_limit` is honest, not hidden.
- Handoff before each Workflow launch.
