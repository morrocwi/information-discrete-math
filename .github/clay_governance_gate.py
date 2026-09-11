#!/usr/bin/env python3
"""Fail-closed governance gate for Clay-sensitive pull requests.

Usage:
    python .github/clay_governance_gate.py <base_sha> <head_sha>

The gate requires an auditable CLAY_GOVERNANCE_ACK.json update whenever a
claim/proof-sensitive path changes. High-impact changes may not mark Toledo as
not-required.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ACK = "CLAY_GOVERNANCE_ACK.json"

PROFILES = {
    "morrocwi/readout-problem-navier-stokes": {
        "sensitive_exact": {"README.md", "AGENTS.md", "CLAIMS.md", "CLAY_READ_FIRST.md", "CLAY_RESEARCH_TODO.md", "CLAY_MULTI_PROBLEM_FINITE_BRIDGE_PROGRAM.md"},
        "sensitive_prefixes": ("paper/", "verification/", "p_vs_np/"),
        "sensitive_contains": ("BRIDGE", "CLAIM"),
        "high_exact": {"CLAIMS.md", "CLAY_MULTI_PROBLEM_FINITE_BRIDGE_PROGRAM.md"},
        "high_prefixes": ("paper/", "verification/", "p_vs_np/"),
        "high_contains": ("BRIDGE", "CLAIM"),
    },
    "morrocwi/information-discrete-math": {
        "sensitive_exact": {"README.md", "AGENTS.md", "docs/UNIVERSAL_FINITE_OBSTRUCTION_UNIFORM_BRIDGE_KERNEL.md", "docs/DISCRETE_EPSILON_COMPLETION.md", "docs/FINITE_DIRECT_SAMPLE_BRANCH.md", "docs/FORMAL_COMPANIONS.md"},
        "sensitive_prefixes": ("formal/",),
        "sensitive_contains": ("P_VS_NP", "PVSNP", "p_vs_np", "BRIDGE", "CLAIM"),
        "high_exact": {"docs/UNIVERSAL_FINITE_OBSTRUCTION_UNIFORM_BRIDGE_KERNEL.md", "docs/DISCRETE_EPSILON_COMPLETION.md", "docs/FINITE_DIRECT_SAMPLE_BRANCH.md"},
        "high_prefixes": ("formal/",),
        "high_contains": ("P_VS_NP", "PVSNP", "p_vs_np", "BRIDGE", "CLAIM"),
    },
    "morrocwi/toledo": {
        "sensitive_exact": {"README.md", "AGENTS.md", "docs/CLAY_BRIDGE_PROGRAM_2026-09-11.md", "docs/EQ_CODE_SCHEME.md", "registry/SCHEMA.md", "registry/CANONICAL.json", "registry/CANONICAL_REGISTRY.json", "registry/CANONICAL_MAP.md", "registry/EQ_LIBRARY.md"},
        "sensitive_prefixes": ("coq/", "registry/"),
        "sensitive_contains": ("BRIDGE", "CLAIM"),
        "high_exact": {"docs/CLAY_BRIDGE_PROGRAM_2026-09-11.md", "registry/CANONICAL.json", "registry/CANONICAL_REGISTRY.json", "registry/CANONICAL_MAP.md", "registry/EQ_LIBRARY.md"},
        "high_prefixes": ("coq/", "registry/"),
        "high_contains": ("BRIDGE", "CLAIM"),
    },
}

TODO_STATUSES = {"updated", "reviewed-no-change"}
TOLEDO_STATUSES = {"updated", "issue-open", "not-required"}
CLAIM_EFFECTS = {"none", "documentation-only", "status-only", "statement-change", "formal-proof-change", "provenance-change"}


def hold(message: str) -> None:
    print(f"::error::CLAY GOVERNANCE HOLD: {message}")
    raise SystemExit(1)


def changed_files(base: str, head: str) -> list[str]:
    try:
        out = subprocess.check_output(["git", "diff", "--name-only", f"{base}...{head}"], text=True)
    except subprocess.CalledProcessError as exc:
        hold(f"cannot compute PR diff: {exc}")
    return [line.strip() for line in out.splitlines() if line.strip()]


def matches(path: str, exact: set[str], prefixes: tuple[str, ...], contains: tuple[str, ...]) -> bool:
    if path in exact or path.endswith(".v"):
        return True
    if any(path.startswith(prefix) for prefix in prefixes):
        return True
    upper = path.upper()
    return any(token.upper() in upper for token in contains)


def require_text(obj: dict, key: str, context: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        hold(f"{context}.{key} must be a non-empty string")
    return value.strip()


def main() -> None:
    if len(sys.argv) != 3:
        hold("usage: clay_governance_gate.py <base_sha> <head_sha>")

    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if repo not in PROFILES:
        hold(f"no governance profile for repository {repo!r}")

    files = changed_files(sys.argv[1], sys.argv[2])
    profile = PROFILES[repo]
    sensitive = [p for p in files if matches(p, profile["sensitive_exact"], profile["sensitive_prefixes"], profile["sensitive_contains"])]
    if not sensitive:
        print("Clay governance: no claim/proof-sensitive paths changed; PASS")
        return

    high = [p for p in sensitive if matches(p, profile["high_exact"], profile["high_prefixes"], profile["high_contains"])]
    print("Clay governance sensitive paths:")
    for path in sensitive:
        print(f"  - {path}")

    if ACK not in files:
        hold(f"{ACK} must be updated in the same PR when Clay-sensitive paths change")
    ack_path = Path(ACK)
    if not ack_path.exists():
        hold(f"{ACK} is missing from the checked-out head")
    try:
        ack = json.loads(ack_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        hold(f"cannot read valid JSON from {ACK}: {exc}")

    if ack.get("schema_version") != "1.0":
        hold(f"{ACK}.schema_version must be '1.0'")
    require_text(ack, "reviewed_at", ACK)
    require_text(ack, "scope", ACK)
    todo, toledo = ack.get("todo"), ack.get("toledo")
    if not isinstance(todo, dict) or not isinstance(toledo, dict):
        hold(f"{ACK} must contain object fields 'todo' and 'toledo'")

    todo_status = require_text(todo, "status", "todo")
    todo_evidence = require_text(todo, "evidence", "todo")
    toledo_status = require_text(toledo, "status", "toledo")
    toledo_evidence = require_text(toledo, "evidence", "toledo")
    claim_effect = require_text(ack, "claim_effect", ACK)

    if todo_status not in TODO_STATUSES:
        hold(f"todo.status must be one of {sorted(TODO_STATUSES)}")
    if toledo_status not in TOLEDO_STATUSES:
        hold(f"toledo.status must be one of {sorted(TOLEDO_STATUSES)}")
    if claim_effect not in CLAIM_EFFECTS:
        hold(f"claim_effect must be one of {sorted(CLAIM_EFFECTS)}")

    if high:
        if toledo_status == "not-required":
            hold("high-impact claim/formal/bridge changes require Toledo status 'updated' or 'issue-open'")
        if claim_effect in {"none", "documentation-only"}:
            hold("high-impact paths require a status, statement, formal-proof, or provenance claim_effect")

    print("Clay governance acknowledgement:")
    print(f"  scope: {ack['scope']}")
    print(f"  TODO: {todo_status} — {todo_evidence}")
    print(f"  Toledo: {toledo_status} — {toledo_evidence}")
    print(f"  claim_effect: {claim_effect}")
    print("Clay governance: PASS")


if __name__ == "__main__":
    main()
