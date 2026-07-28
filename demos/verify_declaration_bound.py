#!/usr/bin/env python3
"""Verify the Declaration Bound's irreducible q-ary fooling family — the numerical half.

The Declaration Bound is a **bit-accurate** retained-state separation for a deferred spectral query
on symmetric tridiagonal operators. Retained state is measured in bits / machine words, never in an
undefined "number of scalars" (a running counter already costs Theta(log n) bits):

    declared query  (the threshold is known BEFORE the diagonal streams past) : Theta(1) retained bits
    deferred query  (the threshold is asked only AFTER the record has passed)  : Theta(n log q) bits

For an alphabet of size q and q = n this is a sharp Theta(1) vs Theta(n) separation in machine words.
The finite, combinatorial core (distinct strings force a long record) is machine-checked axiom-free in
`formal/IDM_DeclarationBound.v` (Coq 8.20). This script verifies the one ingredient that lives in
eigenvalue arithmetic rather than pure combinatorics — the **q-ary extraction identity**:

    #{eigenvalues below sigma(i, r)}  =  i + [a_i <= r]      (Sturm/inertia sign-count),

so the q-1 threshold queries at position i read off the symbol a_i of the input string a in {0..q-1}^n.

Family (all off-diagonals nonzero -> irreducible): for an n-symbol q-ary string a, with M = q + 2,
    diagonal_i   = M*i + a_i,      off-diagonal = delta = 1/16  (rational, nonzero),
    threshold    = sigma(i, r) = M*i + r + 0.5   for r in {0, ..., q-2}.
Gershgorin separation guarantees |lambda - sigma| >= 1/2 - 2*delta = 7/16, so the sign-count is
unambiguous.

The classical constant-*register* Sturm property (two running scalars suffice for a *declared* query)
is real and is stated as such — it is NOT identified with constant *bits*; that conflation is exactly
the correction this revised q-ary family makes precise.

Tier: finite_diagnostic — a discrete rational-arithmetic verification on finite operators. It confirms
the model the Coq file assumes; it is not itself a continuum claim.

Run:  PYTHONPATH=. python3 demos/verify_declaration_bound.py
"""

from __future__ import annotations

import itertools
import math
import random

import numpy as np
from numpy.linalg import eigvalsh

DELTA = 1.0 / 16.0  # rational, nonzero: the family is irreducible (every off-diagonal entry present)


def build_operator(a, q: int, delta: float = DELTA):
    """The symmetric-tridiagonal fooling operator for a q-ary string ``a`` (entries in ``0..q-1``)."""
    n = len(a)
    spacing = q + 2
    diagonal = np.array([spacing * i + a[i] for i in range(n)], dtype=float)
    matrix = np.diag(diagonal)
    if n > 1:
        off = np.full(n - 1, delta)
        matrix += np.diag(off, 1) + np.diag(off, -1)
    return matrix


def sigma(i: int, r: int, q: int) -> float:
    return (q + 2) * i + r + 0.5


def predicted_count(a, i: int, r: int) -> int:
    """The extraction identity: #eigenvalues below sigma(i,r) is exactly ``i + [a_i <= r]``."""
    return i + int(a[i] <= r)


def check_extraction(vectors, q: int):
    """Confirm the extraction identity against a dense symmetric eigensolve, over ``vectors``."""
    cases = queries = 0
    min_margin = math.inf
    for a in vectors:
        a = list(a)
        eig = eigvalsh(build_operator(a, q))
        for i in range(len(a)):
            for r in range(q - 1):
                s = sigma(i, r, q)
                observed = int(np.count_nonzero(eig < s))
                if observed != predicted_count(a, i, r):
                    raise AssertionError(f"extraction failed: a={tuple(a)}, i={i}, r={r}, "
                                         f"observed={observed}, expected={predicted_count(a, i, r)}")
                min_margin = min(min_margin, float(np.min(np.abs(eig - s))))
                queries += 1
        cases += 1
    return {"cases": cases, "queries": queries, "min_margin": min_margin}


def response_profile(a, q: int):
    eig = eigvalsh(build_operator(list(a), q))
    return tuple(int(np.count_nonzero(eig < sigma(i, r, q)))
                 for i in range(len(a)) for r in range(q - 1))


def check_distinct_profiles(n: int, q: int):
    """All q^n strings give distinct query-response profiles (zero collisions) — the family is
    irreducible, so >= q^n terminal states are required => S >= n*log2(q) bits = Omega(n log q)."""
    seen = {}
    for a in itertools.product(range(q), repeat=n):
        p = response_profile(a, q)
        if p in seen:
            raise AssertionError(f"profile collision: {seen[p]} and {a}")
        seen[p] = a
    return {"strings": q ** n, "distinct": len(seen), "collisions": 0}


def main() -> int:
    print("Declaration Bound — q-ary irreducible fooling family (finite_diagnostic, bit-accurate)")
    print(f"  delta = {DELTA} (rational, nonzero); margin >= 1/2 - 2*delta = {0.5 - 2 * DELTA}\n")

    ex = check_extraction(itertools.product(range(4), repeat=5), q=4)
    print("check 1 — extraction  #below sigma(i,r) = i + [a_i <= r]  (exhaustive n=5, q=4)")
    print(f"  PASS: {ex['cases']} strings, {ex['queries']} queries, every symbol recovered\n")

    pr = check_distinct_profiles(n=4, q=4)
    print("check 2 — distinct profiles (exhaustive n=4, q=4)")
    print(f"  PASS: {pr['strings']} strings -> {pr['distinct']} distinct profiles, {pr['collisions']} collisions")
    print("  => >= q^n terminal states => deferred S >= n*log2(q) = Omega(n log q) bits\n")

    rng = random.Random(20260728)
    n = qv = 32
    vectors = [[rng.randrange(qv) for _ in range(n)] for _ in range(200)]
    rn = check_extraction(vectors, q=qv)
    print(f"check 3 — extraction on random large cases (n={n}, q={qv})")
    print(f"  PASS: {rn['cases']} cases, {rn['queries']} queries; min |lambda - sigma| "
          f"= {min(ex['min_margin'], rn['min_margin']):.4f} (>= 7/16 guaranteed)\n")

    print("Resource model (bit-accurate): declared query = Theta(1) retained bits; deferred query =")
    print("Theta(n log q) bits; q = n => Theta(1) vs Theta(n) machine words. The classical constant-")
    print("REGISTER Sturm property (declared query) is separate and is NOT a constant-BIT claim.")
    print("The combinatorial core (distinct strings force a length->=n record) is machine-checked")
    print("axiom-free in formal/IDM_DeclarationBound.v.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
