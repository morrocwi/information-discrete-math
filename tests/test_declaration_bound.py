#!/usr/bin/env python3
"""Declaration Bound — correctness contract for the q-ary fooling-family verification.

The finite combinatorial core is proved axiom-free in formal/IDM_DeclarationBound.v; this test locks
the numerical half (the q-ary extraction identity #below sigma(i,r) = i + [a_i <= r] reads off each
symbol; distinct strings give distinct profiles) so a regression in the fooling family is caught in CI.

Run: PYTHONPATH=. python3 -m pytest tests/test_declaration_bound.py -q
"""

from __future__ import annotations

import itertools

import pytest

np = pytest.importorskip("numpy")

from demos.verify_declaration_bound import (
    DELTA,
    build_operator,
    check_distinct_profiles,
    check_extraction,
    predicted_count,
    response_profile,
    sigma,
)


def test_extraction_recovers_every_symbol_binary():
    # q=2 is the sharp base case: the count reads off each bit
    r = check_extraction(itertools.product(range(2), repeat=8), q=2)
    assert r["cases"] == 256 and r["queries"] == 256 * 8 * 1
    assert r["min_margin"] >= 0.5 - 2 * DELTA          # Gershgorin guarantee


def test_extraction_recovers_every_symbol_qary():
    # q=4, exhaustive n=4: every symbol recovered by its q-1 thresholds
    r = check_extraction(itertools.product(range(4), repeat=4), q=4)
    assert r["cases"] == 256 and r["queries"] == 256 * 4 * 3
    assert r["min_margin"] >= 0.5 - 2 * DELTA


def test_all_qary_strings_give_distinct_profiles():
    r = check_distinct_profiles(n=4, q=4)
    assert r["collisions"] == 0, "profile collisions — family not irreducible"
    assert r["distinct"] == r["strings"] == 4 ** 4     # q^n distinct profiles


def test_single_symbol_change_shifts_its_own_thresholds():
    # discriminating: raising a_j by one flips exactly the thresholds r < a_j at position j
    n, q = 5, 4
    base = [0] * n
    prof0 = response_profile(base, q)
    per = q - 1
    for j in range(n):
        bumped = list(base)
        bumped[j] = 2                                   # symbol 0 -> 2
        prof1 = response_profile(bumped, q)
        assert prof1 != prof0, f"changing symbol {j} left the profile unchanged"
        # at position j, thresholds r=0,1 (< 2) now count one fewer 'a_i <= r'
        seg0 = prof0[j * per:(j + 1) * per]
        seg1 = prof1[j * per:(j + 1) * per]
        assert seg1[0] == seg0[0] - 1 and seg1[1] == seg0[1] - 1


def test_predicted_count_matches_identity():
    # the extraction identity is exactly i + [a_i <= r]
    a = [3, 0, 2, 1]
    assert predicted_count(a, 0, 3) == 0 + 1            # a_0=3 <= 3
    assert predicted_count(a, 0, 2) == 0 + 0            # a_0=3 > 2
    assert predicted_count(a, 2, 2) == 2 + 1            # a_2=2 <= 2


def test_delta_is_nonzero_rational():
    assert 0 < DELTA < 0.25, "delta must be nonzero and keep the Gershgorin margin positive"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
