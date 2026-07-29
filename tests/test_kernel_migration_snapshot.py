#!/usr/bin/env python3
"""Migration safety net (P1.7 Batch 0): a byte-identical golden snapshot of every kind's output.

Before any kind is migrated onto idm.kernel, this pins the CURRENT output of all 266 registered kinds
(computed from tests/test_properties.py's FIXTURES) into tests/golden/kind_outputs.json. Every later
migration batch must keep this test green — that is the automated "migration changed nothing observable"
guarantee. If a migration deliberately improves a kind's output (reviewed), the golden file is
regenerated in that same PR with the change called out.

Regenerate (only when an intended change is reviewed):
    PYTHONPATH=. python3 -c "import json,idm; import tests.test_properties as tp; \
        json.dump({k: idm.solve(dict(kind=k, **tp.FIXTURES[k])) for k in sorted(idm.kinds())}, \
                  open('tests/golden/kind_outputs.json','w'), indent=1, sort_keys=True)"

Run:
    PYTHONPATH=. python3 -m pytest tests/test_kernel_migration_snapshot.py -q
"""

from __future__ import annotations

import importlib.util
import json
import os

import pytest

import idm

_HERE = os.path.dirname(__file__)
_spec = importlib.util.spec_from_file_location("_migration_fixtures",
                                               os.path.join(_HERE, "test_properties.py"))
tp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tp)

_GOLDEN_PATH = os.path.join(_HERE, "golden", "kind_outputs.json")
with open(_GOLDEN_PATH, encoding="utf-8") as _f:
    _GOLDEN = json.load(_f)


def test_golden_covers_every_registered_kind():
    """No kind may be added or removed without updating the snapshot (a migration must not lose kinds)."""
    live = set(idm.kinds())
    snap = set(_GOLDEN)
    assert live == snap, {"only_live": sorted(live - snap), "only_snapshot": sorted(snap - live)}


@pytest.mark.parametrize("kind", sorted(_GOLDEN))
def test_kind_output_is_byte_identical_to_snapshot(kind):
    """Each kind's output on its fixture must match the pre-migration golden value exactly."""
    result = json.loads(json.dumps(idm.solve(dict(kind=kind, **tp.FIXTURES[kind]))))
    assert result == _GOLDEN[kind], f"{kind}: output drifted from the golden snapshot"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
