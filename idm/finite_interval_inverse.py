"""Exact finite rational interval core for local inverse certificates.

This module deliberately contains no continuum object and no floating interval guess.
All interval endpoints and preconditioner entries are ``fractions.Fraction`` values.
It evaluates a finite preconditioned Jacobian enclosure

    M(B) = I - A J(B)

and returns the induced infinity-norm bound

    q = ||M(B)||_infinity.

If q < 1, the usual finite-dimensional contraction/inverse estimate can be used on
an independently certified common branch/symmetry slice.  The caller is responsible
for constructing a valid interval enclosure J(B); this module never promotes sampled
Jacobians to certified intervals.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence


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
    """Construct exact intervals [mid-rad, mid+rad] entrywise."""
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
    """Exact interval enclosure of A*J for point rational A."""
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
    """Return exact q >= sup ||I-AJ||_infinity for the supplied interval matrix."""
    AJ = left_multiply_point_interval(preconditioner, jacobian_interval)
    defect = identity_minus(AJ)
    return interval_matrix_infinity_norm_upper(defect)


def certified_interval_inverse_factor(
    *,
    preconditioner: Sequence[Sequence[object]],
    jacobian_interval: Sequence[Sequence[Interval]],
) -> dict:
    """Fail closed unless the exact rational interval defect satisfies q<1."""
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
