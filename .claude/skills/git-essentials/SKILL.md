---
name: git-essentials
description: Essential git workflow for information-discrete-math — load before any commit, push, branch, or PR in this repo. Encodes branch→PR→adversarial-reviewer→CI-green→merge (never push main), the additive-golden-snapshot rule, the CHANGELOG [Unreleased] habit, single-sourced counts, and regeneration gates that must be run before committing.
---

# Git essentials — information-discrete-math

This repo's CI is a wall of byte-identity and consistency gates. Git discipline here means
never committing a diff those gates will reject — and never "fixing" a gate by hardcoding
what it exists to prevent.

## The merge path (non-negotiable)

**Branch → PR → adversarial reviewer → CI green → merge. Never push `main` directly.**
The reviewer pass (correctness, HOLD-not-hang, no float leak) comes before merge; the
founder merges reviewer-clean CI-green PRs. Open PRs as drafts until gates pass.

## Before every commit — regenerate, don't hand-edit

- `capabilities.json` is **generated** (`python3 tools/gen_capabilities.py`); CI requires it
  byte-identical to a fresh regen. Never hand-edit it — regenerate and commit the output.
- The golden snapshot `tests/golden/kind_outputs.json` may only change **additively** when
  adding a kind. If any existing kind's bytes changed in your diff, you changed behavior:
  stop and understand why before committing.
- Counts are **single-sourced**: the kind count comes from `len(idm.kinds())` and the
  doc-scan gate (`test_kind_count_is_single_sourced_across_docs`) fails CI listing every doc
  with a stale total. Update exactly those docs; never introduce a new hardcoded count.
  Same spirit for the theorem count vs `formal/verify.sh`.
- Run the affected suites locally (property/golden/differential/adversarial as touched);
  run `bash formal/verify.sh` only if you touched Coq.

## What belongs in the commit

- A **CHANGELOG entry under `## [Unreleased]`** for any notable change, tier-honest
  (`Th_coqc` / `exact` / `finite_diagnostic` / `+ℝ-Open` — never dressed up).
- Regenerated artifacts (`capabilities.json`, golden snapshot) in the **same commit** as
  the code that changes them, so no commit in history is gate-red.
- Plugin version sync: if you bump the package version, check the Claude Code plugin
  version too — it has been left frozen before (see CHANGELOG 1.5.1).

## Commit messages

Name the kind/gate/doc touched and the verification run, e.g.
`kind: add <name> (exact) + fixture + additive golden regen`,
`gates: fix doc-scan stale counts after <change>`,
`changelog: [Unreleased] entry for <change>`.

## Branch, push, PR mechanics

- `git fetch origin <branch>` for specific branches; `git push -u origin <branch>`; retry
  only network failures up to 4× with backoff (2s, 4s, 8s, 16s).
- After pushing, open a **draft PR** if none is open for the branch. PR body: what gates
  were run locally and their exit status, the tier of each claim, and (for kinds) a note
  that the golden diff is additive.
- Never force-push a shared branch. If a PR merged and follow-up work is needed, restart
  the branch from the latest default branch — never stack on merged history.
