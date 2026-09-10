"""Exact finite helper for preconditioned row-variation inverse radii.

This module is domain-neutral.  Given a fixed finite point preconditioner ``A`` and
certified bounds

    ||J_j(x)-J_j(x0)||_1 <= H_j ||x-x0||_infinity,

it evaluates the rigorous slope

    S = max_i sum_j |A_ij| H_j.

Hence a state radius ``r = q_target / S`` guarantees

    ||A(J(x)-J(x0))||_infinity <= q_target.

When ``A=J(x0)^{-1}``, this is the local ``||I-AJ(x)||`` defect used by finite
inverse/contraction certificates.  The caller is responsible for proving the supplied
row-variation bounds and any required branch/symmetry containment.  No sampled or
floating derivative is promoted to a certificate here.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Sequence


Q = Fraction


def _q(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def _matrix_shape(M: Sequence[Sequence[object]]) -> tuple[int, int]:
    rows = len(M)
    cols = len(M[0]) if rows else 0
    if any(len(row) != cols for row in M):
        raise ValueError("ragged matrix")
    return rows, cols


def preconditioner_infinity_norm(A: Sequence[Sequence[object]]) -> Fraction:
    rows, _ = _matrix_shape(A)
    if rows == 0:
        return Fraction(0)
    return max(
        sum((abs(_q(value)) for value in row), Fraction(0))
        for row in A
    )


def preconditioned_row_variation_radius(
    *,
    preconditioner: Sequence[Sequence[object]],
    jacobian_row_variation_per_state_radius: Sequence[object],
    target_defect: object = Fraction(1, 2),
) -> dict:
    """Return an exact radius from row-wise Jacobian-variation bounds.

    ``preconditioner`` must be square ``n x n`` and the variation sequence must have
    length ``n``.  Entry ``H_j`` must be a certified nonnegative bound satisfying
    ``||J_j(x)-J_j(x0)||_1 <= H_j ||x-x0||_infinity`` on the caller's declared box.

    The returned slope is

        S = max_i sum_j |A_ij| H_j.

    For ``0 < target_defect < 1`` and ``S > 0``, the exact rational radius
    ``target_defect / S`` guarantees the requested preconditioned defect.  If all
    supplied variation bounds vanish, ``radius=None`` records that this inequality
    itself imposes no finite radius limit.
    """
    n, m = _matrix_shape(preconditioner)
    if n == 0 or n != m:
        raise ValueError("preconditioner must be a nonempty square matrix")

    variations = [_q(x) for x in jacobian_row_variation_per_state_radius]
    if len(variations) != n:
        raise ValueError("variation-bound length must match preconditioner dimension")
    if any(x < 0 for x in variations):
        raise ValueError("Jacobian row variation bounds must be nonnegative")

    target = _q(target_defect)
    if not (0 < target < 1):
        raise ValueError("target_defect must lie strictly between zero and one")

    weighted = [
        sum(
            (abs(_q(preconditioner[i][j])) * variations[j] for j in range(n)),
            Fraction(0),
        )
        for i in range(n)
    ]
    slope = max(weighted)
    a_norm = preconditioner_infinity_norm(preconditioner)

    if slope == 0:
        return {
            "status": "CERTIFIED",
            "defect_slope": Fraction(0),
            "target_defect": target,
            "radius": None,
            "preconditioner_infinity_norm": a_norm,
            "reason": "supplied Jacobian row variation is zero; this bound imposes no finite radius limit",
        }

    return {
        "status": "CERTIFIED",
        "defect_slope": slope,
        "target_defect": target,
        "radius": target / slope,
        "preconditioner_infinity_norm": a_norm,
        "reason": "exact row-weighted preconditioner bound certifies the requested local defect",
    }
