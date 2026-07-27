# Handoff — IDM Symbolic Kernel v2 (ultracode design run)

**Written before launching the ultracode Workflow, so a fresh AI can resume if this session dies.**
Date: 2026-07-27, Bangkok. Repo: `/home/yaoharee-lt/ANSE.ASIA/information-discrete-math` (`morrocwi/information-discrete-math`), branch `main`.

## What is being attempted, and why (founder's own request)

The founder's verdict on IDM today: **solver surface is very broad (258 registered problem kinds), but the symbolic core is still a "small CAS".** What makes Mathematica / Maple / SymPy / SageMath "big" is **not the number of commands** — it is a **deep symbolic kernel that ties every command together**. So the next work is **NOT kind #259**. It is:

> **IDM Symbolic Kernel v2: expression + domains + assumptions + conditional rewriting** — collapse the 258 handlers onto ONE shared kernel, turning a broad Math-Solver into a real CAS.

Current reality (confirmed): `idm/symbolic.py` is 306 lines — a tuple expression tree (`("add",[...])`, `("mul",[...])`), `Q` rationals, symbols + `+ * ^` and a handful of functions (sin/cos/tan/exp/log/sqrt); `simplify`/`integrate` are basic rule sets. Each `idm/*.py` module largely computes on its own, not on a shared symbolic object.

## Founder's sequencing (do NOT reorder)

- **Phase 1 (this design run targets it) — become a CAS kernel.** Six pillars, built FIRST, and the existing 258 kinds migrated onto them. **Rule: do not add many new kinds during Phase 1.**
  1. Expression kernel (immutable tree, canonical order, structural hash, exact ℤ/ℚ/algebraic/ℂ number tower, symbols+assumptions, equations/inequalities/logic, sets/intervals/domains, piecewise, undefined/∞/complex-∞, derivative/integral/sum/limit as nodes, matrix/vector/tensor symbolic).
  2. Assumption & domain engine (every module consumes the same assumptions; results carry conditions).
  3. Pattern-match & rewrite engine (wildcards, seq/typed/conditional, comm+assoc matching, priority, loop detection, cost function, transformation trace, domain-gated identities).
  4. Polynomial / algebra domain tower (poly objects, factorization, resultant/discriminant, Gröbner, number fields, finite fields, domain-parametrized ℤ[x]/ℚ[x]/GF(p)[x]/…).
  5. Conditional solution objects (solution set + conditions + exceptional parameters, not a bare root list; no dropped/spurious roots).
  6. Unified exact/certified numeric types + coercion tower (never silent exact→float; maps onto IDM tiers exact / certified-enclosure / finite_diagnostic / HOLD).
- **Phase 2** — deepen ~20 core ops (simplify, factor, expand, cancel, solve, reduce, integrate, differentiate, limit, series, sum, product, dsolve, matrix_solve, eigenvalues, groebner, resultant, minpoly, refine, verify) to CAS-grade: cross-domain, assumption-aware, condition-carrying, back-verifiable. **20 deep > 500 wrappers.**
- **Phase 3** — differential + adversarial testing (unit, algebraic-identity, randomized, differential-vs-SymPy/Sage/Mathematica as *comparator not authority*, boundary, singular, branch-cut, large-expr, resource-limit, HOLD-correctness). Gate on: no confidently-wrong answers, conditions complete, no dropped/added roots, no illegal cross-branch simplification, HOLD when evidence insufficient.

Target ladder: **A** = CAS-grade kernel; **B** = parity with SymPy core; **C** = IDM's own edge (certificate-first, ACCEPT/HOLD, explicit epistemic tier, resource ledger, exact→certified transition, readout lineage, no silent guessing, RCP acceleration). Do NOT frame the goal as "clone Mathematica".

## Readout-first constraints (binding — this is IDM)

Every kernel object is a **finite discrete rational readout**; the continuum (ℝ-completeness, a point of zero size, actual ∞) is a **non-readout** and must never be silently injected. Keep the tier discipline (`Th_coqc` / exact / `finite_diagnostic` / `+ℝ-Open` / `Dr`). Branch-cut / domain correctness is not optional: `sqrt(x^2)→abs(x)` only under the right assumption; `log(ab)=log a+log b`, `sqrt(ab)=√a√b`, `(x^a)^b=x^(ab)` only in safe domains — otherwise `HOLD` or `Piecewise`. The framework's own reference: `textbook/INFORMATION_DISCRETE_MATHEMATICS.md` (the `information-discrete-math` skill is NOT installed this session — read the textbook directly).

## What this ultracode run does (design, not mass code)

A Workflow that: (Ground) maps the current `idm` symbolic state factually → (Design) 6 parallel pillar-design agents produce architecture + public interface contracts + migration notes, each readout-tier-consistent → (Synthesize) one agent merges into a unified architecture doc + concrete `idm/kernel/…` module layout + phased implementation todolist + a v0 skeleton spec for the expression kernel + the 258-kind migration order → (Review) an adversarial agent checks overclaim / tier-consistency / branch-cut stance / feasibility / RAM realism / that it truly unifies (not a 259th kind). Workers run on **sonnet** (founder rule: workflow workers = sonnet; watch RAM). Outputs are **markdown design specs**; the main loop writes them under `docs/symbolic_kernel_v2/` and presents the plan to the founder BEFORE any kernel code is written (plan-before-code).

## How to resume

- **Workflow run ID: `wf_280faa5e-7a7`** (launched 2026-07-27). Script:
  `~/.claude/projects/-home-yaoharee-lt-ANSE-ASIA-information-discrete-math/8b2f7d4f-a9d2-454d-bf0c-68f2c732d997/workflows/scripts/idm-symbolic-kernel-v2-design-wf_280faa5e-7a7.js`.
  Resume with `Workflow({scriptPath, resumeFromRunId: "wf_280faa5e-7a7"})`. Inspect the run's `journal.jsonl` (in its transcript dir) before assuming cached results are non-empty. Check `docs/symbolic_kernel_v2/` for design docs already written by the main loop.
- Todolist: tasks **#14** (this design run) and **#15–#23** (the six pillars + migrate + Phase 2 + Phase 3).

## What NOT to do

- Do NOT add new problem kinds (no kind #259) during Phase 1.
- Do NOT write the full kernel implementation from this run — this run PLANS; implementation is a later, reviewed increment.
- Do NOT inject the continuum silently or simplify across branch cuts without domain conditions.
- Do NOT touch unrelated uncommitted work; do NOT self-merge without review (repo rule: PR + independent review before merge).
- Do NOT re-run heavy benchmarks/full-suite repeatedly (RAM ~1–2 GB free; workflow agents are light readers — keep it that way).

## Next concrete step after the workflow returns

Write the returned architecture / todolist / skeleton / review to `docs/symbolic_kernel_v2/`, do an independent adversarial review, then present the Phase-1 plan + todolist to the founder for go-ahead before implementing the expression kernel (P1.1) first.
