# Handoff — P1.7 migration planning (ultracode run)

**Written before launching the migration-planning Workflow, so a fresh AI can resume if this session dies.**
Date: 2026-07-27, Bangkok. Repo `/home/yaoharee-lt/ANSE.ASIA/information-discrete-math`, branch `main` (green: full suite 183 passed).

## Where we are

**Phase 1 of the IDM Symbolic Kernel v2 is COMPLETE** — all 6 pillars merged to main, each independently reviewed with a real soundness bug caught+fixed before merge:
- P1.1 expression kernel + number tower (PR #7)
- P1.2 assumption & domain engine (PR #8)
- P1.3 rewrite engine, domain-gated (PR #9)
- P1.6 numeric bridge, exact+certified ball eval (PR #10)
- P1.5 conditional solution objects (PR #11)
- P1.4 domain-parametrized polynomial tower (PR #12)

The kernel lives in `idm/kernel/` and is **additive** — the 259 registered kinds still compute through their old bespoke code; the kernel is a tested target, not yet the substrate. `idm.kinds()` == 259. Design + per-pillar specs + adversarial review are in `docs/symbolic_kernel_v2/`.

## What this run does (and why this shape)

**P1.7 = migrate the 258/259 kinds onto the shared kernel** so the codebase has ONE substrate, not seven (the exact concern REVIEW.md finding raised). This is a large multi-increment phase. Founder direction: *use ultracode, split into migration teams + a SEPARATE review team, watch RAM.*

**This first ultracode run is migration PLANNING, not concurrent code-editing**, deliberately:
- Concurrent workflow agents editing the shared repo (esp. `idm/solve.py`, where all ~259 kinds register) would collide — single-writer-per-file-group is a standing rule.
- Running per-batch tests inside many parallel agents would blow RAM (~1–2 GB free; the full suite alone is 5 min).

So the Workflow fans out by **kind-family** to produce a concrete, sequenced **migration playbook** (which handlers route to which kernel module, behavior-preservation strategy, file-ownership, per-kind test plan, what defers), with a **separate adversarial review team** checking it. The main loop then executes the batches **one at a time as normal reviewed PRs** (single-writer, scoped tests, byte-identical guarantee), which is RAM-safe and matches every kernel-pillar increment this session.

## Binding constraints for the migration itself

- **Behavior-preserving.** A migrated kind must return byte-identical output on the existing test fixtures (the 6 `symbolic_*` kinds especially), OR improve it only in a reviewed, tested way. `tests/test_properties.py` + `tests/test_idm_api.py` are the regression gates; the full suite is the final gate per batch group.
- **Additive-until-proven.** Route a kind through the kernel only when it's provably equivalent; otherwise keep the old path and defer, explicitly named (no silent "migrated" claim — the REVIEW.md finding).
- **Tier honesty.** No new `_COQ_BACKED` entries; reuse the 5 tiers; a kind's tier must not inflate on migration.
- **No new kinds.** Migration moves existing kinds onto the kernel; it does not add kind #260.
- **RAM.** Workers = sonnet; scoped tests per batch, full suite only once per batch-group at the end (standing "no repeated full-arc audits" rule).

## How to resume

- **Workflow run ID: `wf_ad2c356b-ed0`** (launched 2026-07-27) — resume with `Workflow({scriptPath: "…/idm-kernel-migration-plan-wf_ad2c356b-ed0.js", resumeFromRunId: "wf_ad2c356b-ed0"})`; inspect its `journal.jsonl` before assuming cached results are non-empty. The migration playbook is written to `docs/symbolic_kernel_v2/MIGRATION_PLAYBOOK.md` by the main loop after the run.
- Todolist: task **#21** (P1.7 migration). Phase-2/3 tasks (#22 deepen 20 ops, #23 differential testing) come after.

## Next concrete step after the workflow returns

Write the playbook to `docs/symbolic_kernel_v2/`, do an independent review, then execute **batch 1** (the safest/highest-value, disjoint-file batch) as a reviewed PR — verify byte-identical on fixtures + scoped tests, then the batch-group full suite once.
