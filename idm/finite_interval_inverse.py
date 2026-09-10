"""Exact finite rational interval core for local inverse certificates.

This module deliberately contains no continuum object and no floating interval guess.
All interval endpoints and preconditioner entries are ``fractions.Fraction`` values.
It supports two complementary finite certification routes:

1. an explicit interval preconditioner ``A`` with

       M(B) = I - A J(B),    q = ||M(B)||_infinity,

   which certifies an inverse factor when ``q < 1``; and

2. a conservative row-aware Cramer/Hadamard route for an exactly invertible center
   Jacobian when a positive lower bound on ``|det J0|`` and finite row/Hessian
   majorants are available.

The caller remains responsible for constructing valid interval or derivative
majorants and for certifying any required common branch/symmetry slice.  Sampled
Jacobians are never silently promoted to certified intervals.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence


Q = Fraction


def _q(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


@dataclass(frozen=True)
class Interval:
    lo: Fraction
    hi: Fraction

    def __post_init__(self) -> None:
        lo, hi = _q(self.lo), _q(self.hi)
        if lo > hi:
            raise ValueError("interval lower endpoint exceeds upper endpoint")
        object.__setattr__(self, "lo", lo)
        object.__setattr__(self, "hi", hi)

    @classmethod
    def point(cls, x) -> "Interval":
        q = _q(x)
        return cls(q, q)

    def __add__(self, other) -> "Interval":
        other = other if isinstance(other, Interval) else Interval.point(other)
        return Interval(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __neg__(self) -> "Interval":
        return Interval(-self.hi, -self.lo)

    def __sub__(self, other) -> "Interval":
        return self + (-other if isinstance(other, Interval) else -Interval.point(other))

    def __rsub__(self, other) -> "Interval":
        return Interval.point(other) - self

    def __mul__(self, other) -> "Interval":
        other = other if isinstance(other, Interval) else Interval.point(other)
        vals = (
            self.lo * other.lo,
            self.lo * other.hi,
            self.hi * other.lo,
            self.hi * other.hi,
        )
        return Interval(min(vals), max(vals))

    __rmul__ = __mul__

    def abs_upper(self) -> Fraction:
        return max(abs(self.lo), abs(self.hi))


def _matrix_shape(M: Sequence[Sequence[object]]) -> tuple[int, int]:
    rows = len(M)
    cols = len(M[0]) if rows else 0
    if any(len(r) != cols for r in M):
        raise ValueError("ragged matrix")
    return rows, cols


def point_matrix(M: Sequence[Sequence[object]]) -> list[list[Interval]]:
    return [[Interval.point(x) for x in row] for row in M]


def interval_matrix_from_mid_radius(
    midpoint: Sequence[Sequence[object]],
    radius: Sequence[Sequence[object]],
) -> list[list[Interval]]:
    """Construct exact intervals ``[mid-rad, mid+rad]`` entrywise."""
    sm = _matrix_shape(midpoint)
    sr = _matrix_shape(radius)
    if sm != sr:
        raise ValueError("midpoint/radius shape mismatch")
    out: list[list[Interval]] = []
    for mrow, rrow in zip(midpoint, radius):
        row = []
        for m, r in zip(mrow, rrow):
            m, r = _q(m), _q(r)
            if r < 0:
                raise ValueError("interval radius must be nonnegative")
            row.append(Interval(m - r, m + r))
        out.append(row)
    return out


def left_multiply_point_interval(
    A: Sequence[Sequence[object]],
    J: Sequence[Sequence[Interval]],
) -> list[list[Interval]]:
    """Exact interval enclosure of ``A*J`` for point rational ``A``."""
    ra, ca = _matrix_shape(A)
    rj, cj = _matrix_shape(J)
    if ca != rj:
        raise ValueError("matrix dimension mismatch")
    out = [[Interval.point(0) for _ in range(cj)] for _ in range(ra)]
    for i in range(ra):
        for k in range(ca):
            aik = _q(A[i][k])
            if aik == 0:
                continue
            for j in range(cj):
                out[i][j] = out[i][j] + aik * J[k][j]
    return out


def identity_minus(AJ: Sequence[Sequence[Interval]]) -> list[list[Interval]]:
    n, m = _matrix_shape(AJ)
    if n != m:
        raise ValueError("I-AJ requires a square product")
    return [
        [Interval.point(1 if i == j else 0) - AJ[i][j] for j in range(n)]
        for i in range(n)
    ]


def interval_matrix_infinity_norm_upper(M: Sequence[Sequence[Interval]]) -> Fraction:
    """Rigorous induced infinity-norm upper bound from entry intervals."""
    _matrix_shape(M)
    if not M:
        return Fraction(0)
    return max(sum((x.abs_upper() for x in row), Fraction(0)) for row in M)


def point_matrix_infinity_norm(A: Sequence[Sequence[object]]) -> Fraction:
    _matrix_shape(A)
    if not A:
        return Fraction(0)
    return max(sum((abs(_q(x)) for x in row), Fraction(0)) for row in A)


def preconditioned_defect_bound(
    *,
    preconditioner: Sequence[Sequence[object]],
    jacobian_interval: Sequence[Sequence[Interval]],
) -> Fraction:
    """Return exact ``q >= sup ||I-AJ||_infinity`` for the supplied interval matrix."""
    AJ = left_multiply_point_interval(preconditioner, jacobian_interval)
    defect = identity_minus(AJ)
    return interval_matrix_infinity_norm_upper(defect)


def certified_interval_inverse_factor(
    *,
    preconditioner: Sequence[Sequence[object]],
    jacobian_interval: Sequence[Sequence[Interval]],
) -> dict:
    """Fail closed unless the exact rational interval defect satisfies ``q < 1``."""
    q = preconditioned_defect_bound(
        preconditioner=preconditioner,
        jacobian_interval=jacobian_interval,
    )
    if q >= 1:
        return {
            "status": "HOLD",
            "q": q,
            "factor": None,
            "reason": "preconditioned interval Jacobian defect is not strictly below one",
        }
    a_norm = point_matrix_infinity_norm(preconditioner)
    return {
        "status": "CERTIFIED",
        "q": q,
        "preconditioner_norm": a_norm,
        "factor": a_norm / (1 - q),
        "reason": "exact rational interval enclosure satisfies q<1",
    }


def rowwise_hadamard_inverse_bound(
    *,
    jacobian_row_l1_bounds: Sequence[object],
    determinant_abs_lower_bound: object = 1,
) -> dict:
    """Bound ``||J0^{-1}||_infinity`` from finite row bounds and ``|det J0|``.

    Suppose ``J0`` is an ``n x n`` invertible matrix, ``R_j`` satisfies
    ``||J0[j,*]||_2 <= ||J0[j,*]||_1 <= R_j``, and a certified positive number
    ``d`` satisfies ``|det J0| >= d``.  Hadamard applied to a cofactor that deletes
    row ``j`` gives

        |cof_{j i}(J0)| <= product_{k != j} R_k.

    Cramer's formula therefore gives a column-dependent entry bound

        |(J0^{-1})_{i j}| <= product_{k != j} R_k / d.

    Summing over columns yields the returned induced-infinity-norm bound.  No claim
    is made that this conservative estimate is sharp.
    """
    rows = [_q(x) for x in jacobian_row_l1_bounds]
    if not rows:
        raise ValueError("at least one Jacobian row bound is required")
    if any(x <= 0 for x in rows):
        raise ValueError("Jacobian row bounds must be strictly positive")
    det_lb = _q(determinant_abs_lower_bound)
    if det_lb <= 0:
        raise ValueError("determinant absolute lower bound must be strictly positive")

    product_all = Fraction(1)
    for x in rows:
        product_all *= x
    column_entry_bounds = [(product_all / rows[j]) / det_lb for j in range(len(rows))]
    inverse_inf_bound = sum(column_entry_bounds, Fraction(0))
    return {
        "status": "CERTIFIED",
        "column_entry_bounds": column_entry_bounds,
        "inverse_infinity_norm_bound": inverse_inf_bound,
        "determinant_abs_lower_bound": det_lb,
    }


def rowwise_hadamard_local_radius(
    *,
    jacobian_row_l1_bounds: Sequence[object],
    jacobian_row_variation_per_state_radius: Sequence[object],
    determinant_abs_lower_bound: object = 1,
    target_defect: object = Fraction(1, 2),
) -> dict:
    """Return an exact positive radius guaranteeing a chosen preconditioned defect.

    In addition to the hypotheses of :func:`rowwise_hadamard_inverse_bound`, assume
    that on the independently declared branch/box

        ||J_j(x)-J_j(x0)||_1 <= H_j * ||x-x0||_infinity.

    With ``A=J0^{-1}``, the row-aware cofactor estimate gives

        ||I-A J(x)||_infinity
        = ||A(J0-J(x))||_infinity
        <= r * sum_j C_j H_j,

    where ``C_j`` is the certified column-entry bound for ``A``.  Thus
    ``r = target_defect / sum_j C_j H_j`` guarantees the requested defect.

    This helper certifies only the finite norm inequality.  Branch containment and
    validity of the supplied derivative majorants remain caller obligations.
    """
    variations = [_q(x) for x in jacobian_row_variation_per_state_radius]
    if len(variations) != len(jacobian_row_l1_bounds):
        raise ValueError("row-bound and variation-bound lengths must match")
    if any(x < 0 for x in variations):
        raise ValueError("Jacobian row variation bounds must be nonnegative")
    target = _q(target_defect)
    if not (0 < target < 1):
        raise ValueError("target_defect must lie strictly between zero and one")

    inv = rowwise_hadamard_inverse_bound(
        jacobian_row_l1_bounds=jacobian_row_l1_bounds,
        determinant_abs_lower_bound=determinant_abs_lower_bound,
    )
    slope = sum(
        (c * h for c, h in zip(inv["column_entry_bounds"], variations)),
        Fraction(0),
    )
    if slope == 0:
        return {
            **inv,
            "status": "CERTIFIED",
            "defect_slope": Fraction(0),
            "target_defect": target,
            "radius": None,
            "reason": "supplied Jacobian variation is zero; the bound imposes no finite radius limit",
        }

    return {
        **inv,
        "status": "CERTIFIED",
        "defect_slope": slope,
        "target_defect": target,
        "radius": target / slope,
        "reason": "row-aware Cramer/Hadamard bound certifies the requested local defect",
    }
