"""Exact minimal polynomial of a rational square matrix (pillar P1.4, on the Wave-5 tower).

The minimal polynomial ``m`` of ``A`` is the least-degree MONIC polynomial with ``m(A) = 0`` (the zero
matrix). It is found here by the classic linear-algebra construction, kept exact throughout:

    flatten I, A, A^2, ... into vectors of Q^{n*n} and find the smallest k for which
    I, A, ..., A^k are linearly DEPENDENT over Q (exact rational Gauss-Jordan elimination).

Because I, ..., A^{k-1} are (by minimality of k) linearly INDEPENDENT, any nontrivial dependency
relation among I, ..., A^k must have a nonzero coefficient on A^k, so normalizing that coefficient to 1
hands back the monic minimal polynomial directly — no separate "make it monic" step, and no float
anywhere. Cayley-Hamilton guarantees such a k exists with k <= n (n = matrix size), so the search never
needs to look past A^n.
"""

from __future__ import annotations

from fractions import Fraction as Q
from typing import List, Optional

from .coeffring import QRing
from .univariate import UPoly


def _to_square_fraction_matrix(matrix) -> List[List[Q]]:
    rows = [list(r) for r in matrix]
    n = len(rows)
    if n == 0 or any(len(r) != n for r in rows):
        raise ValueError("minimal_polynomial requires a square, non-empty matrix")
    return [[Q(x) for x in r] for r in rows]


def _matmul(a: List[List[Q]], b: List[List[Q]]) -> List[List[Q]]:
    n = len(a)
    return [[sum((a[i][t] * b[t][j] for t in range(n)), Q(0)) for j in range(n)] for i in range(n)]


def _identity(n: int) -> List[List[Q]]:
    return [[Q(1) if i == j else Q(0) for j in range(n)] for i in range(n)]


def _flatten(m: List[List[Q]]) -> List[Q]:
    return [x for row in m for x in row]


def _nullspace_vector(vectors: List[List[Q]]) -> Optional[List[Q]]:
    """Given ``k`` column vectors of equal length (as a list of ``k`` lists), return a nontrivial
    ``x`` (length ``k``, exact ``Fraction``) with ``sum(x[i] * vectors[i]) == 0`` — the zero vector —
    or ``None`` if the vectors are linearly independent (only the trivial null vector exists).

    Exact rational Gauss-Jordan elimination (full RREF), columns processed left to right so that, when
    the leading ``k-1`` columns are already known independent, any dependency is witnessed by the LAST
    column being the (leftmost, and here only) free column — giving a null vector whose last entry is
    the free variable, set to ``1``.
    """
    k = len(vectors)
    if k == 0:
        return None
    m = len(vectors[0])
    # M[row][col] = vectors[col][row]  (rows = the m coordinates, columns = the k vectors)
    M = [[vectors[c][r] for c in range(k)] for r in range(m)]

    pivot_cols: List[int] = []
    row = 0
    for col in range(k):
        piv = next((r for r in range(row, m) if M[r][col] != 0), None)
        if piv is None:
            continue                                   # col has no pivot relative to remaining rows
        M[row], M[piv] = M[piv], M[row]
        pivval = M[row][col]
        M[row] = [x / pivval for x in M[row]]
        for r in range(m):
            if r != row and M[r][col] != 0:
                f = M[r][col]
                M[r] = [M[r][j] - f * M[row][j] for j in range(k)]
        pivot_cols.append(col)
        row += 1
        if row == m:
            break

    free_cols = [c for c in range(k) if c not in pivot_cols]
    if not free_cols:
        return None                                    # full column rank: only the trivial null vector

    free_col = free_cols[0]
    x = [Q(0)] * k
    x[free_col] = Q(1)
    for i, pc in enumerate(pivot_cols):
        x[pc] = -M[i][free_col]
    return x


def eval_poly_at_matrix(p: UPoly, matrix) -> List[List[Q]]:
    """Evaluate ``p`` at the square matrix ``matrix`` by Horner's method, using matrix multiplication
    for ``x`` and ``c * I`` for each coefficient ``c``. Returns the resulting matrix (exact ``Fraction``
    entries). Used to back-check ``minimal_polynomial``: ``eval_poly_at_matrix(m, A)`` must be the zero
    matrix.
    """
    D = p.domain
    if not isinstance(D, QRing):
        raise ValueError(f"eval_poly_at_matrix requires a QRing polynomial; got {D!r}")
    a = _to_square_fraction_matrix(matrix)
    n = len(a)
    acc = [[Q(0)] * n for _ in range(n)]
    for c in reversed(p.coeffs):
        acc = _matmul(acc, a)
        acc = [[acc[i][j] + (c if i == j else Q(0)) for j in range(n)] for i in range(n)]
    return acc


def minimal_polynomial(matrix) -> UPoly:
    """The monic minimal polynomial of the square rational matrix ``matrix``, exact over Q.

    Finds the smallest ``k`` for which ``I, A, A^2, ..., A^k`` are linearly dependent (flattened to
    vectors, exact Gauss-Jordan elimination). The witnessing dependency relation, normalized so the
    coefficient on ``A^k`` is ``1``, is the monic minimal polynomial of degree ``k``.

    Raises ``ValueError`` if ``matrix`` is not square (or empty).
    """
    a = _to_square_fraction_matrix(matrix)
    n = len(a)

    powers = [_identity(n)]
    cur = powers[0]
    for _ in range(n):
        cur = _matmul(cur, a)
        powers.append(cur)
    vectors = [_flatten(p) for p in powers]                # vectors[i] = flatten(A^i), i = 0..n

    for k in range(1, n + 1):
        nv = _nullspace_vector(vectors[: k + 1])
        if nv is None:
            continue
        pivot = nv[k]
        if pivot == 0:
            raise RuntimeError(
                "internal error: expected a nonzero leading coefficient in the minimal-polynomial "
                "dependency relation (I, ..., A^{k-1} should have been independent)"
            )
        coeffs = [c / pivot for c in nv]                   # monic: coeffs[k] == 1
        return UPoly(coeffs, QRing())

    raise RuntimeError(
        "internal error: no dependency found among I, A, ..., A^n — Cayley-Hamilton violated"
    )


__all__ = ["minimal_polynomial", "eval_poly_at_matrix"]
