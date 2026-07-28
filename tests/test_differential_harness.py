#!/usr/bin/env python3
"""Differential testing (pillar P3): every registered kind's answer, cross-checked against an
independent oracle (sympy / arithmetic) over many random valid inputs.

A disagreement here is a real correctness bug — this is the same discipline that caught the
rational_limit pole-sign and groebner duplicate-leading-monomial defects during P2 review. The
oracle registry lives in tests/harness.py (DIFFERENTIAL_CASES); adding a kind is one entry.

Run: PYTHONPATH=. python3 -m pytest tests/test_differential_harness.py -q
"""

from __future__ import annotations

import importlib.util
import os
import random
import sys

import pytest

_HERE = os.path.dirname(__file__)


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_HERE, filename))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod                  # register first: @dataclass resolves cls.__module__ here
    spec.loader.exec_module(mod)
    return mod


_h = _load("_p3_harness", "harness.py")

# a fixed seed makes the whole differential sweep reproducible bit-for-bit
_SEED = 20260728


@pytest.mark.parametrize("case", _h.DIFFERENTIAL_CASES, ids=lambda c: c.kind)
def test_kind_agrees_with_oracle(case):
    rng = random.Random(_SEED)
    mismatches = []
    compared = 0
    for _ in range(case.n_cases):
        problem = case.generate(rng)
        params = {k: v for k, v in problem.items() if not k.startswith("_")}
        try:
            expected = case.oracle(problem)
        except Exception:                       # an oracle that itself errors is not a solver finding
            continue
        if expected == "SKIP":
            continue
        result = _h.run_kind(case.kind, params)
        verdict = case.agree(result, expected)
        if verdict == "SKIP":
            continue
        compared += 1
        if not verdict:
            mismatches.append({"params": params,
                               "got": result.get("value", result.get("status")),
                               "expected": str(expected)})
    assert compared > 0, f"{case.kind}: no cases actually compared (oracle skipped everything)"
    assert not mismatches, (
        f"{case.kind}: {len(mismatches)}/{compared} differed from the oracle; first: {mismatches[0]}")
