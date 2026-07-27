#!/usr/bin/env python3
"""Exact ℚ linear solver — CAS-grade coverage of every rank case (pillar P2).

Where the older solve_linear handled only the square, unique case (HOLD otherwise), matrix_solve /
kernel.poly.linear_solve returns the COMPLETE solution set: unique, an infinite family (particular +
nullspace basis), or a reported inconsistency. Every returned vector is re-checked exactly with the
matvec certificate.

Run: PYTHONPATH=. python3 -m pytest tests/test_linsolve.py -q
"""

from __future__ import annotations

from fractions import Fraction as Q

import pytest

import idm
from idm.kernel.poly.linsolve import linear_solve, matvec, rref


def _zeros(n):
    return [Q(0)] * n


def test_unique_solution_square():
    A, b = [[2, 1, -1], [-3, -1, 2], [-2, 1, 2]], [8, -11, -3]
    sol = linear_solve(A, b)
    assert sol.status == "unique"
    assert sol.particular == [Q(2), Q(3), Q(-1)]
    assert sol.nullspace == []
    assert matvec(A, sol.particular) == [Q(x) for x in b]  # certificate


def test_infinite_solution_has_correct_nullspace():
    A, b = [[1, 1, 1], [2, 2, 2]], [6, 12]
    sol = linear_solve(A, b)
    assert sol.status == "infinite"
    assert sol.rank == 1
    assert len(sol.nullspace) == 2  # 3 vars - rank 1
    # particular solves the system; every nullspace vector solves the homogeneous system
    assert matvec(A, sol.particular) == [Q(6), Q(12)]
    for v in sol.nullspace:
        assert matvec(A, v) == _zeros(2)
    # a random combination particular + 3*v0 - 2*v1 must still solve A x = b
    combo = [sol.particular[i] + 3 * sol.nullspace[0][i] - 2 * sol.nullspace[1][i] for i in range(3)]
    assert matvec(A, combo) == [Q(6), Q(12)]


def test_inconsistent_system_reported_not_faked():
    sol = linear_solve([[1, 1], [1, 1]], [1, 2])
    assert sol.status == "inconsistent"
    assert not sol.is_solvable
    assert sol.particular is None
    assert sol.nullspace == []


def test_overdetermined_consistent_unique():
    A, b = [[1, 0], [0, 1], [1, 1]], [3, 4, 7]
    sol = linear_solve(A, b)
    assert sol.status == "unique"
    assert sol.particular == [Q(3), Q(4)]


def test_overdetermined_inconsistent():
    # three equations, two unknowns, last one contradicts the first two
    sol = linear_solve([[1, 0], [0, 1], [1, 1]], [3, 4, 999])
    assert sol.status == "inconsistent"


def test_underdetermined_wide():
    # one equation, three unknowns: a 2-parameter family
    A, b = [[1, 2, 3]], [6]
    sol = linear_solve(A, b)
    assert sol.status == "infinite"
    assert sol.rank == 1 and sol.num_vars == 3 and len(sol.nullspace) == 2
    assert matvec(A, sol.particular) == [Q(6)]


def test_exact_fraction_solution():
    # a system whose solution is genuinely fractional — no float creeps in
    A, b = [[3, 2], [1, -1]], [1, 1]
    sol = linear_solve(A, b)
    assert sol.status == "unique"
    assert sol.particular == [Q(3, 5), Q(-2, 5)]
    assert all(isinstance(x, Q) for x in sol.particular)


def test_rref_is_idempotent_and_exact():
    A = [[1, 2, 0], [0, 1, 3], [0, 0, 5]]   # upper-triangular, nonzero diagonal => full rank 3
    R1, p1 = rref(A)
    R2, p2 = rref(R1)
    assert R1 == R2 and p1 == p2  # RREF of an RREF is itself
    assert p1 == [0, 1, 2]        # full rank 3
    assert R1 == [[Q(1), Q(0), Q(0)], [Q(0), Q(1), Q(0)], [Q(0), Q(0), Q(1)]]  # -> identity


def test_rref_detects_rank_deficiency():
    # a genuinely rank-2 matrix (row3 = row1 + row2) must yield exactly 2 pivots
    _, pivots = rref([[2, 4, 6], [1, 1, 1], [3, 5, 7]])
    assert len(pivots) == 2


def test_shape_mismatch_raises():
    with pytest.raises(ValueError):
        linear_solve([[1, 2], [3, 4]], [1, 2, 3])  # b too long


# ---- the registered kind, end to end through idm.solve ----

def test_matrix_solve_kind_unique():
    r = idm.solve({"kind": "matrix_solve", "A": [[2, 1], [1, 3]], "b": [3, 5]})
    assert r["status"] == "ok" and r["value"]["solution_type"] == "unique" and r["tier"] == "exact"
    assert r["value"]["particular"][0]["exact"] == "4/5" and r["value"]["particular"][1]["exact"] == "7/5"


def test_matrix_solve_kind_infinite():
    r = idm.solve({"kind": "matrix_solve", "A": [[1, 1, 1], [2, 2, 2]], "b": [6, 12]})
    assert r["status"] == "ok" and r["value"]["solution_type"] == "infinite"
    assert r["value"]["rank"] == 1 and len(r["value"]["nullspace"]) == 2


def test_matrix_solve_kind_inconsistent_holds():
    r = idm.solve({"kind": "matrix_solve", "A": [[1, 1], [1, 1]], "b": [1, 2]})
    assert r["status"] == "HOLD" and r["value"]["solution_type"] == "inconsistent"


def test_matrix_solve_kind_missing_field_holds_not_crash():
    r = idm.solve({"kind": "matrix_solve", "A": [[1, 1]]})  # no b
    assert r["status"] == "HOLD"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
