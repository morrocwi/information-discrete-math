#!/usr/bin/env python3
"""Declaration Bound — correctness contract for the fooling-family verification.

The finite combinatorial core is proved axiom-free in formal/IDM_DeclarationBound.v; this test
locks the numerical half (the Sturm count reads off each bit; distinct strings give distinct
profiles) so a regression in the fooling family is caught in CI.

Run: PYTHONPATH=. python3 -m pytest tests/test_declaration_bound.py -q
"""

from __future__ import annotations

import pytest

np = pytest.importorskip("numpy")

from demos.verify_declaration_bound import (
    DELTA,
    check_bit_extraction,
    check_distinct_profiles,
    operator,
    sturm_count,
)


def test_bit_extraction_recovers_every_bit():
    r = check_bit_extraction(n=12, trials=300)
    assert r["ok"], "Sturm count failed to recover some bit b_i"
    # the observed separation must clear the Gershgorin guarantee 1/2 - 2*delta
    assert r["worst_margin"] >= r["guaranteed_margin"], (
        f"margin {r['worst_margin']} below guaranteed {r['guaranteed_margin']}")


def test_all_strings_give_distinct_profiles():
    r = check_distinct_profiles(m=8)
    assert r["collisions"] == 0, f"{r['collisions']} profile collisions — family not irreducible"
    assert r["distinct"] == r["strings"] == 256


def test_single_bit_flip_changes_the_profile():
    # a genuine discriminating check: flipping exactly one bit must change the count at that index
    n = 8
    base = [0] * n
    d0, e0 = operator(base)
    prof0 = [sturm_count(d0, e0, 2 * i + 0.5) for i in range(n)]
    for j in range(n):
        flipped = list(base)
        flipped[j] = 1
        d1, e1 = operator(flipped)
        prof1 = [sturm_count(d1, e1, 2 * i + 0.5) for i in range(n)]
        assert prof1 != prof0, f"flipping bit {j} left the profile unchanged"
        assert prof1[j] - prof0[j] == 1, f"bit {j} did not shift its own count by exactly 1"


def test_delta_is_nonzero_rational():
    # irreducibility hinges on a nonzero coupling; guard the constant
    assert 0 < DELTA < 0.25, "delta must be nonzero and keep the Gershgorin margin positive"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
