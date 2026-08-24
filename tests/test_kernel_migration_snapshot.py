#!/usr/bin/env python3
"""Golden-output safety net for registered solver kinds.

Most kinds remain byte-identical to the historical snapshot. A small, explicitly reviewed set is allowed
to change when the purpose of a PR is to correct evidence semantics; those kinds receive stronger semantic
assertions below instead of silently regenerating the entire golden file.
"""

from __future__ import annotations

import importlib.util
import json
import os

import pytest

import idm

_HERE = os.path.dirname(__file__)
_spec = importlib.util.spec_from_file_location(
    "_migration_fixtures", os.path.join(_HERE, "test_properties.py")
)
tp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tp)

_GOLDEN_PATH = os.path.join(_HERE, "golden", "kind_outputs.json")
with open(_GOLDEN_PATH, encoding="utf-8") as _file:
    _GOLDEN = json.load(_file)

# Deliberate output migrations in the readout-certification revision.
_INTENTIONAL_EVIDENCE_MIGRATIONS = {
    "certified_limit",
    "exp",
    "geometric_series",
}


def test_golden_covers_every_registered_kind():
    live = set(idm.kinds())
    snapshot = set(_GOLDEN)
    assert live == snapshot, {
        "only_live": sorted(live - snapshot),
        "only_snapshot": sorted(snapshot - live),
    }


@pytest.mark.parametrize("kind", sorted(_GOLDEN))
def test_kind_output_is_byte_identical_or_reviewed_evidence_migration(kind):
    result = json.loads(json.dumps(idm.solve(dict(kind=kind, **tp.FIXTURES[kind]))))

    if kind == "certified_limit":
        assert result["status"] == "ok"
        assert result["evidence_status"] == "STABLE"
        assert result["tier"] == "finite_diagnostic"
        assert result["bound"] is not None
        return
    if kind == "exp":
        assert result["status"] == "CERTIFIED"
        assert result["tier"] == "finite_diagnostic"
        assert result["bound"] is not None
        return
    if kind == "geometric_series":
        assert result["status"] == "CERTIFIED"
        assert result["tier"] == "Th_coqc"
        assert result["bound"] is not None
        assert "coq_theorem" in result
        return

    assert kind not in _INTENTIONAL_EVIDENCE_MIGRATIONS
    assert result == _GOLDEN[kind], f"{kind}: output drifted from the golden snapshot"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
