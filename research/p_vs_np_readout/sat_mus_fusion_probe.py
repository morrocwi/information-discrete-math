#!/usr/bin/env python3
"""Exact SAT-specific Fusion probe via minimal UNSAT cores.

Focus
-----
This diagnostic stays on the unrestricted-SAT circuit lower-bound lane.  It
asks whether the Fusion/Horn burden can see nontrivial structure in SAT itself,
not in a proxy language.

A fixed clause bank B=(C_0,...,C_{m-1}) induces an m-bit SAT subfunction

    SAT_B(z)=1  iff  the selected clauses {C_i : z_i=1} are satisfiable.

The positive sets of SAT_B form a simplicial complex.  Its minimal nonfaces
are precisely the minimal UNSAT cores (MUSs), so exactly

    SAT_B(z) = AND_{M in MUS(B)} OR_{i in M} NOT z_i.

Thus a bank with r MUSs has an explicit DeMorgan implementation with at most
r-1 AND gates (the MUS clauses themselves are OR-only).

This file exhibits a concrete five-clause bank for which Fusion cover
complexity rho is EXACTLY 2:

  * lower bound: exhaust every possible one-rule Horn/Fusion cover by an exact
    disjoint-parent criterion; no one-rule cover exists;
  * upper bound: the bank has exactly three MUSs, whose canonical CNF
    implementation has two AND gates; the two induced lineage pairs are
    independently checked by Horn closure to derive bottom at every positive
    SAT input.

The result is a finite SAT-specific post-input-coverage calibration.  It is
NOT an asymptotic lower bound, SAT notin P/poly, or P != NP proof.
"""
from __future__ import annotations

from itertools import product
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from fusion_horn_exact import (
    horn_closure,
    literal_generators,
    pointset_all,
)

Clause = tuple[int, ...]


def clause_true(clause: Clause, assignment: tuple[bool, ...]) -> bool:
    return any(
        (lit > 0 and assignment[abs(lit) - 1])
        or (lit < 0 and not assignment[abs(lit) - 1])
        for lit in clause
    )


def sat_target(bank: tuple[Clause, ...], semantic_vars: int) -> int:
    m = len(bank)
    out = 0
    for mask in range(1 << m):
        yes = False
        for a in product((False, True), repeat=semantic_vars):
            if all(
                clause_true(bank[i], a)
                for i in range(m)
                if (mask >> i) & 1
            ):
                yes = True
                break
        if yes:
            out |= 1 << mask
    return out


def minimal_unsat_cores(A: int, m: int) -> list[int]:
    mus: list[int] = []
    for mask in range(1, 1 << m):
        if (A >> mask) & 1:
            continue
        minimal = True
        for i in range(m):
            if (mask >> i) & 1:
                parent = mask & ~(1 << i)
                if ((A >> parent) & 1) == 0:
                    minimal = False
                    break
        if minimal:
            mus.append(mask)
    return mus


def truth_table_not_all_selected(m: int, core: int) -> int:
    """OR_{i in core} NOT z_i over all 2^m selection inputs."""
    out = 0
    for z in range(1 << m):
        if (z & core) != core:
            out |= 1 << z
    return out


def mus_cnf_lineage_pairs(A: int, m: int, mus: list[int]) -> list[tuple[int, int]]:
    """Sequentially AND the OR-only MUS clauses and return negative-slice pairs."""
    assert mus
    gamma = pointset_all(m)
    U = gamma ^ A
    terms = [truth_table_not_all_selected(m, core) for core in mus]
    cur = terms[0]
    pairs: list[tuple[int, int]] = []
    for term in terms[1:]:
        pairs.append((cur & U, term & U))
        cur &= term
    assert cur == A, "MUS CNF must equal SAT_B exactly"
    return pairs


def localize(global_subset: int, points: list[int]) -> int:
    out = 0
    for j, p in enumerate(points):
        if (global_subset >> p) & 1:
            out |= 1 << j
    return out


def initial_seed_sets(A: int, m: int):
    """Return U points and literal seed sets for each positive input."""
    gamma = pointset_all(m)
    U = gamma ^ A
    points = [x for x in range(1 << m) if (U >> x) & 1]
    generators = literal_generators(m)
    rows: list[tuple[int, list[int]]] = []
    for a in range(1 << m):
        if ((A >> a) & 1) == 0:
            continue
        seeds = [
            localize(B & U, points)
            for B in generators
            if (B >> a) & 1
        ]
        rows.append((a, seeds))
    return U, points, rows


def rho_zero(A: int, m: int) -> bool:
    """No fusion rule is needed iff every positive seed closure already has bottom."""
    _U, _points, rows = initial_seed_sets(A, m)
    return all(0 in seeds for _a, seeds in rows)


def one_rule_cover(A: int, m: int):
    """Exact search for a one-rule Fusion/Horn cover.

    With one Horn rule E,H -> E intersect H, bottom can be newly derived only
    when E and H are disjoint.  For a positive point whose initial closure does
    not already contain bottom, E belongs to that closure iff E contains one
    literal seed; similarly for H.

    We exhaust E.  Given E, the largest possible disjoint H is U\E.  If that
    complement does not contain a seed for some positive point, no smaller
    disjoint H can work.  Hence this is exhaustive over every possible one-rule
    cover without enumerating semi-filters.
    """
    _U, points, rows = initial_seed_sets(A, m)
    k = len(points)
    full = (1 << k) - 1
    relevant = [seeds for _a, seeds in rows if 0 not in seeds]
    if not relevant:
        return None

    for E in range(1 << k):
        if not all(any((s & ~E) == 0 for s in seeds) for seeds in relevant):
            continue
        H = full ^ E
        if all(any((s & ~H) == 0 for s in seeds) for seeds in relevant):
            return E, H
    return None


def check_horn_cover(A: int, m: int, pairs: list[tuple[int, int]]) -> None:
    gamma = pointset_all(m)
    U = gamma ^ A
    gens = literal_generators(m)
    for a in range(1 << m):
        if (A >> a) & 1:
            closure = horn_closure(a, U, gens, tuple(pairs))
            assert 0 in closure, (a, pairs, closure)


def main() -> None:
    # Two semantic variables; five clause-selection input bits.
    # C0=x1, C1=~x1, C2=x2, C3=(x1 v x2), C4=(x1 v ~x2).
    # This bank has three overlapping minimal UNSAT cores.
    bank: tuple[Clause, ...] = (
        (1,),
        (-1,),
        (2,),
        (1, 2),
        (1, -2),
    )
    m = len(bank)
    A = sat_target(bank, semantic_vars=2)
    gamma = pointset_all(m)
    U = gamma ^ A
    mus = minimal_unsat_cores(A, m)

    expected_mus = [0b00011, 0b10110, 0b11010]
    assert mus == expected_mus, (mus, expected_mus)
    assert U.bit_count() == 11

    # Lower bound rho >= 2.
    assert not rho_zero(A, m)
    assert one_rule_cover(A, m) is None

    # Upper bound rho <= 2, supplied by the actual two-AND MUS-CNF lineage.
    pairs = mus_cnf_lineage_pairs(A, m, mus)
    assert len(pairs) == 2
    check_horn_cover(A, m, pairs)

    print("SAT minimal-UNSAT-core Fusion probe: PASS")
    print(f"clause_bits={m} positives={A.bit_count()} negatives={U.bit_count()}")
    print(f"MUS_masks={[bin(x) for x in mus]}")
    print("one-rule cover: EXHAUSTED / NONE")
    print(f"two-rule lineage cover: VERIFIED pairs={pairs}")
    print("exact Fusion cover complexity rho(SAT_B)=2")
    print("interpretation: SAT-specific post-coverage closure debt is nontrivial already at five clause bits")
    print("next target: a scalable MUS family with superlinear/superpolynomial rho; still OPEN")
    print("tier=exact_finite_diagnostic; SAT notin P/poly=NOT CLAIMED; P!=NP=NOT CLAIMED")


if __name__ == "__main__":
    main()
