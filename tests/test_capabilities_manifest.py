"""Regeneration gate for capabilities.json.

capabilities.json is a *generated* artifact (tools/gen_capabilities.py reads
it straight off the live idm.solve registry). These tests fail if the
checked-in file ever drifts from what the registry + generator actually
produce — e.g. a new @kind(...) is added to idm/solve.py but nobody reran
the generator, or the checked-in file was hand-edited.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import idm

REPO_ROOT = Path(__file__).resolve().parent.parent
CAPABILITIES_PATH = REPO_ROOT / "capabilities.json"
GENERATOR_PATH = REPO_ROOT / "tools" / "gen_capabilities.py"


def _load_manifest() -> dict:
    with CAPABILITIES_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def test_total_problem_kinds_matches_registry():
    manifest = _load_manifest()
    assert manifest["project"]["total_problem_kinds"] == len(idm.kinds())


def test_domain_union_covers_every_kind_exactly_once():
    manifest = _load_manifest()
    live_kinds = set(idm.kinds())

    seen: list[str] = []
    for domain, info in manifest["domains"].items():
        seen.extend(info["kinds"])
        assert info["count"] == len(info["kinds"]), (
            f"domain {domain!r}: count field ({info['count']}) does not match "
            f"len(kinds) ({len(info['kinds'])})"
        )

    # no kind missing, none duplicated across (or within) domains
    assert set(seen) == live_kinds, (
        f"missing from manifest: {live_kinds - set(seen)}; "
        f"in manifest but not in idm.kinds(): {set(seen) - live_kinds}"
    )
    assert len(seen) == len(set(seen)), "a kind appears in more than one domain"
    assert len(seen) == len(live_kinds) == 265, (
        "expected the full 265-kind registry; if this repo has grown the "
        "registry, this constant (and the task's grounding facts) needs an "
        "update alongside the manifest"
    )


def test_regenerating_reproduces_the_file_byte_identically():
    """The regeneration gate: `python tools/gen_capabilities.py --check`
    must exit 0 — i.e. capabilities.json is exactly what the generator
    would write today, from the current registry. A drifted or
    hand-edited file fails this."""
    result = subprocess.run(
        [sys.executable, str(GENERATOR_PATH), "--out", str(CAPABILITIES_PATH), "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "capabilities.json is stale relative to tools/gen_capabilities.py "
        f"+ the live registry; rerun the generator to refresh it.\n"
        f"stdout={result.stdout}\nstderr={result.stderr}"
    )
