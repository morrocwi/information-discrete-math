#!/usr/bin/env python3
"""Adversarial testing (pillar P3): every registered kind, hit with hostile whole-problem inputs, must
uphold the solver contract — never an uncaught exception, always a well-formed result whose tier is
honest (no CERTIFIED / Th_coqc conjured from garbage).

Complements test_properties.py's per-fixture missing/garbage checks with a systematic, data-driven
sweep driven by tests/harness.py (adversarial_inputs / ADVERSARIAL_FILLS). Bounded to
len(kinds) * (1 + len(ADVERSARIAL_FILLS)) probes so it stays CI-fast.

Run: PYTHONPATH=. python3 -m pytest tests/test_adversarial_harness.py -q
"""

from __future__ import annotations

import importlib.util
import os
import sys

import pytest

_HERE = os.path.dirname(__file__)


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_HERE, filename))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod                  # register first: @dataclass resolves cls.__module__ here
    spec.loader.exec_module(mod)
    return mod


_h = _load("_p3_harness_adv", "harness.py")
_tp = _load("_p3_fixtures", "test_properties.py")
_PROBES = list(_h.adversarial_inputs(_tp.FIXTURES))


def test_every_registered_kind_has_a_fixture():
    # the sweep is only as complete as the fixture table; guard that they stay in lock-step
    import idm
    missing = sorted(set(idm.kinds()) - set(_tp.FIXTURES))
    assert not missing, f"kinds with no fixture (add one so the adversarial sweep covers them): {missing}"


def test_adversarial_sweep_never_crashes_and_stays_tier_honest():
    crashes, malformed, dishonest = [], [], []
    for kind, params, label in _PROBES:
        try:
            r = _h.run_kind(kind, params)
        except Exception as exc:                       # the solver must never let an exception escape
            crashes.append(f"{kind} [{label}] -> {type(exc).__name__}: {exc}")
            continue
        why = _h.result_well_formed(r)
        if why:
            malformed.append(f"{kind} [{label}] -> {why}")
        why_tier = _h.tier_is_honest(r)
        if why_tier:
            dishonest.append(f"{kind} [{label}] -> {why_tier}")
    assert not crashes, f"{len(crashes)} kinds crashed on adversarial input; first 5: {crashes[:5]}"
    assert not malformed, f"{len(malformed)} malformed results; first 5: {malformed[:5]}"
    assert not dishonest, f"{len(dishonest)} tier-dishonest results; first 5: {dishonest[:5]}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
