#!/usr/bin/env python3
"""Verify the Declaration Bound's irreducible fooling family — the numerical half.

The Declaration Bound (Sturm readout on symmetric tridiagonal operators): a threshold query
answered with Theta(1) retained state when *declared in advance*, but Theta(n) retained state when
*deferred* until after the record has streamed past. The finite, combinatorial core of that
separation is machine-checked axiom-free in `formal/IDM_DeclarationBound.v` (Coq 8.20). This script
verifies the one ingredient that lives in eigenvalue arithmetic rather than pure combinatorics, and
so is checked numerically here instead of in Coq:

    the irreducible fooling family's Sturm count at threshold sigma_i is exactly  i + b_i,

i.e. the count of eigenvalues below sigma_i reads off bit b_i of the input string. Together with the
Coq file's `profile_injective` (distinct strings -> distinct profiles) and `deferred_record_bits`
(2^n distinct records force some record of length >= n), this closes the argument.

Family (all off-diagonals nonzero -> irreducible): for an n-bit string b,
    diagonal_i     = 2*i + (1 - b_i),      off-diagonal = delta = 1/8  (rational, nonzero),
    threshold_i    = 2*i + 1/2,
Gershgorin separation guarantees |lambda - sigma_i| >= 1/2 - 2*delta = 1/4, so the sign-count is
unambiguous.

Tier: finite_diagnostic — a discrete rational-arithmetic verification on finite operators. It
confirms the model the Coq file assumes; it is not itself a continuum claim.

Run:  PYTHONPATH=. python3 demos/verify_declaration_bound.py
"""

from __future__ import annotations

import itertools

import numpy as np
from numpy.linalg import eigvalsh

DELTA = 0.125  # rational, nonzero: the family is irreducible (every off-diagonal entry present)


def operator(bits, delta: float = DELTA):
    """The symmetric-tridiagonal fooling operator for a bit string ``bits``."""
    n = len(bits)
    diagonal = np.array([2 * i + (1 - bits[i]) for i in range(n)], dtype=float)
    off = np.full(n - 1, delta)
    return diagonal, off


def sturm_count(diagonal, off, sigma: float) -> int:
    """#eigenvalues strictly below ``sigma``, from the signs of the LDL^T pivots — the same
    top-down Sturm recurrence the retained solver forms and (in the deferred regime) discards."""
    n = len(diagonal)
    count = 0
    s = diagonal[0] - sigma
    if s < 0:
        count += 1
    for i in range(n - 1):
        if s == 0.0:
            s = 1e-300
        s = (diagonal[i + 1] - sigma) - off[i] * off[i] / s
        if s < 0:
            count += 1
    return count


def dense_eigenvalues(diagonal, off):
    n = len(diagonal)
    matrix = np.diag(diagonal) + np.diag(off, 1) + np.diag(off, -1)
    return eigvalsh(matrix)


def check_bit_extraction(n: int = 12, trials: int = 300) -> dict:
    """Every bit is recovered by the Sturm count: nu(sigma_i) - i == b_i, over random strings."""
    ok = True
    worst_margin = float("inf")
    guaranteed = 0.5 - 2 * DELTA
    for t in range(trials):
        bits = np.random.default_rng(t).integers(0, 2, n)
        diagonal, off = operator(bits)
        lam = dense_eigenvalues(diagonal, off)
        for i in range(n):
            sigma = 2 * i + 0.5
            if sturm_count(diagonal, off, sigma) - i != bits[i]:
                ok = False
                break
            worst_margin = min(worst_margin, float(np.min(np.abs(lam - sigma))))
        if not ok:
            break
    return {"ok": ok, "trials": trials, "n": n,
            "worst_margin": worst_margin, "guaranteed_margin": guaranteed}


def check_distinct_profiles(m: int = 8) -> dict:
    """All 2^m strings give distinct query-response profiles (zero collisions) — the fooling
    family is irreducible, so >= 2^m terminal states are required => S >= m bits = Omega(n)."""
    seen = set()
    for bits in itertools.product([0, 1], repeat=m):
        diagonal, off = operator(list(bits))
        profile = tuple(sturm_count(diagonal, off, 2 * i + 0.5) for i in range(m))
        seen.add(profile)
    return {"m": m, "strings": 2 ** m, "distinct": len(seen), "collisions": 2 ** m - len(seen)}


def main() -> int:
    print("Declaration Bound — irreducible fooling family verification (finite_diagnostic)")
    print(f"  delta = {DELTA} (rational, nonzero; all off-diagonals present)\n")

    r1 = check_bit_extraction()
    status1 = "PASS" if r1["ok"] else "FAIL"
    print(f"check 1: nu(sigma_i) - i == b_i for every bit")
    print(f"  {status1}: {r1['trials']} random strings, n={r1['n']}, every bit recovered")
    print(f"  smallest |lambda - sigma| margin observed: {r1['worst_margin']:.4f}"
          f"   (theory guarantees >= 1/2 - 2*delta = {r1['guaranteed_margin']})\n")

    r2 = check_distinct_profiles()
    status2 = "PASS" if r2["collisions"] == 0 else "FAIL"
    print(f"check 2: all 2^{r2['m']} strings give distinct query-response profiles")
    print(f"  {status2}: {r2['strings']} strings -> {r2['distinct']} distinct profiles, "
          f"{r2['collisions']} collisions")
    print(f"  => at least 2^{r2['m']} terminal states required => S >= {r2['m']} bits = Omega(n)\n")

    print("The combinatorial consequences (profile injectivity; 2^n distinct records force a")
    print("record of length >= n; declared regime forgets the tail) are machine-checked axiom-free")
    print("in formal/IDM_DeclarationBound.v.")
    return 0 if (r1["ok"] and r2["collisions"] == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
