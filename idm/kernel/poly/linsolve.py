"""Exact rational linear-system solver ``A x = b`` (pillar P2, CAS-grade).

Gaussian elimination to reduced row-echelon form over ℚ, kept exact with ``fractions.Fraction``
throughout — no float, no pivoting-for-stability heuristics (exact arithmetic needs none; the pivot
is chosen only to be nonzero). The result is a COMPLETE description of the solution set, not just one
vector, so every rank case is handled honestly:

  * ``unique``       — full column rank: exactly one solution, returned as an exact ℚ vector.
  * ``infinite``     — consistent but rank-deficient: a particular solution plus a basis of the
                       homogeneous nullspace, so ``x = particular + Σ tᵢ·basisᵢ`` is the full set.
  * ``inconsistent`` — no solution (a pivot in the augmented column): reported, never faked.

The design mirrors the rest of the tower: exact ℚ, a structured verdict object, and a certificate
that a caller can re-check (``A·particular == b`` and ``A·basisᵢ == 0``).
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from typing import List, Optional, Sequence


@dataclass(frozen=True)
class LinearSolution:
    """The complete solution set of ``A x = b`` over ℚ.

    ``status`` is ``"unique"``, ``"infinite"`` or ``"inconsistent"``.  For ``unique`` the single
    solution is ``particular`` and ``nullspace`` is empty; for ``infinite`` the solution set is
    ``{particular + Σ tᵢ·nullspace[i] : tᵢ ∈ ℚ}``; for ``inconsistent`` both are ``None``/empty.
    ``rank`` and ``num_vars`` describe the coefficient matrix.
    """

    status: str
    particular: Optional[List[Q]]
    nullspace: List[List[Q]]
    rank: int
    num_vars: int

    @property
    def is_solvable(self) -> bool:
        return self.status != "inconsistent"


def _as_q_matrix(matrix: Sequence[Sequence[object]]) -> List[List[Q]]:
    rows = [list(r) for r in matrix]
    if not rows:
        raise ValueError("linear_solve requires a non-empty coefficient matrix")
    width = len(rows[0])
    if width == 0 or any(len(r) != width for r in rows):
        raise ValueError("linear_solve requires a rectangular, non-empty coefficient matrix")
    return [[Q(x) for x in r] for r in rows]


def _as_q_vector(vector: Sequence[object]) -> List[Q]:
    return [Q(x) for x in vector]


def rref(matrix: Sequence[Sequence[object]]):
    """Reduced row-echelon form over ℚ (exact).  Returns ``(R, pivots)`` where ``R`` is the RREF as a
    fresh list-of-lists of ``Fraction`` and ``pivots`` lists the pivot column index of each nonzero
    row, in order.  The input is not mutated."""
    R = [row[:] for row in _as_q_matrix(matrix)]
    rows = len(R)
    cols = len(R[0])
    pivots: List[int] = []
    r = 0
    for c in range(cols):
        # find a nonzero pivot at or below row r in column c
        pivot_row = next((i for i in range(r, rows) if R[i][c] != 0), None)
        if pivot_row is None:
            continue
        R[r], R[pivot_row] = R[pivot_row], R[r]
        # normalise the pivot row so the pivot is 1
        inv = Q(1) / R[r][c]
        R[r] = [x * inv for x in R[r]]
        # clear the pivot column in every other row
        for i in range(rows):
            if i != r and R[i][c] != 0:
                factor = R[i][c]
                R[i] = [a - factor * b for a, b in zip(R[i], R[r])]
        pivots.append(c)
        r += 1
        if r == rows:
            break
    return R, pivots


def linear_solve(matrix: Sequence[Sequence[object]], rhs: Sequence[object]) -> LinearSolution:
    """Solve ``A x = b`` exactly over ℚ and return the full solution set as a :class:`LinearSolution`.

    ``matrix`` is ``A`` (m×n, any shape); ``rhs`` is ``b`` (length m).  Raises ``ValueError`` on a
    shape mismatch; otherwise never raises — an unsolvable system is reported as ``inconsistent``.
    """
    A = _as_q_matrix(matrix)
    b = _as_q_vector(rhs)
    m = len(A)
    n = len(A[0])
    if len(b) != m:
        raise ValueError(f"right-hand side has length {len(b)}, expected {m} (one per equation)")

    # Row-reduce the augmented matrix [A | b].
    augmented = [A[i] + [b[i]] for i in range(m)]
    R, pivots = rref(augmented)

    # Inconsistent iff some pivot sits in the augmented (last) column: a row 0…0 | 1.
    if n in pivots:
        return LinearSolution("inconsistent", None, [], rank=len(pivots) - 1, num_vars=n)

    rank = len(pivots)
    pivot_set = set(pivots)
    free_cols = [c for c in range(n) if c not in pivot_set]

    # Particular solution: free variables = 0, pivot variables read off the augmented column.
    particular = [Q(0)] * n
    for row_idx, pc in enumerate(pivots):
        particular[pc] = R[row_idx][n]

    if not free_cols:
        return LinearSolution("unique", particular, [], rank=rank, num_vars=n)

    # Homogeneous nullspace basis: one basis vector per free column (that free var = 1, others = 0).
    nullspace: List[List[Q]] = []
    for fc in free_cols:
        vec = [Q(0)] * n
        vec[fc] = Q(1)
        for row_idx, pc in enumerate(pivots):
            vec[pc] = -R[row_idx][fc]
        nullspace.append(vec)

    return LinearSolution("infinite", particular, nullspace, rank=rank, num_vars=n)


def matvec(matrix: Sequence[Sequence[object]], vector: Sequence[object]) -> List[Q]:
    """Exact ``A·x`` over ℚ — the certificate helper a caller uses to re-check a returned solution."""
    A = _as_q_matrix(matrix)
    x = _as_q_vector(vector)
    if len(x) != len(A[0]):
        raise ValueError("vector length must match the number of columns")
    return [sum((A[i][j] * x[j] for j in range(len(x))), Q(0)) for i in range(len(A))]


__all__ = ["LinearSolution", "rref", "linear_solve", "matvec"]
