"""Fail-closed finite direct-sample branch certificate.

This module contains only finite-dimensional inequalities.  It is intended for a
square observation map S:B(z,r)->R^d on a convex infinity-norm ball.  A caller must
supply a fixed preconditioner A and a certified branch-wide defect

    q >= sup_{x in B} ||I - A DS(x)||_inf.

Suppose raw data are centered at y_obs with sensor radius sigma, while y_model is a
finite certified approximation to S(z) with model radius tau.  Put

    delta = ||y_obs-y_model||_inf + sigma + tau.

If

    q < 1
    and
    ||A||_inf * delta + q r <= r,

then, for every exact data vector y in the declared raw-data box, the Newton-like map

    T_y(x) = x - A(S(x)-y)

is a contraction that maps B into itself.  Banach's theorem therefore supplies one
unique root of S(x)=y *inside that declared local branch*.  No prior assumption that
the unknown state already belongs to B is used.

The same inequalities give

    ||x-z||_inf <= ||A||_inf/(1-q) * delta.

The theorem is local: it does not exclude additional roots outside B.  It also does
not manufacture the defect q, the forward-model radius tau, or a sensor model.  If any
required gate is absent or fails, the API returns HOLD.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Sequence


def _q(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def matrix_inf_norm(matrix: Sequence[Sequence[object]]) -> Fraction:
    rows = [[_q(v) for v in row] for row in matrix]
    if not rows or not rows[0]:
        raise ValueError("nonempty matrix required")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("rectangular matrix required")
    return max(sum((abs(v) for v in row), Fraction(0)) for row in rows)


def certified_direct_sample_branch(
    *,
    preconditioner: Sequence[Sequence[object]],
    jacobian_defect_bound: object,
    branch_radius: object,
    sample_center_discrepancy: object,
    sensor_radius: object,
    forward_model_radius: object,
) -> dict:
    """Certify a raw-data local branch and its retained-state radius.

    Parameters are exact or rationalizable finite quantities.  The discrepancy is
    ``||y_obs-y_model||_inf``; ``sensor_radius`` encloses exact data around ``y_obs``;
    ``forward_model_radius`` encloses ``S(z)`` around ``y_model``.
    """
    q = _q(jacobian_defect_bound)
    r = _q(branch_radius)
    d = _q(sample_center_discrepancy)
    sigma = _q(sensor_radius)
    tau = _q(forward_model_radius)
    if r <= 0:
        raise ValueError("branch_radius must be positive")
    if any(v < 0 for v in (q, d, sigma, tau)):
        raise ValueError("defect and uncertainty quantities must be nonnegative")

    a_norm = matrix_inf_norm(preconditioner)
    image_radius = d + sigma + tau

    if q >= 1:
        return {
            "status": "HOLD",
            "branch_certified": False,
            "state_radius": None,
            "q": q,
            "reason": "branch-wide preconditioned Jacobian defect is not below one",
        }

    self_map_lhs = a_norm * image_radius + q * r
    self_map_ok = self_map_lhs <= r
    inverse_factor = a_norm / (1 - q)
    state_radius = inverse_factor * image_radius
    data_budget = (1 - q) * r / a_norm if a_norm > 0 else None

    if not self_map_ok:
        return {
            "status": "HOLD",
            "branch_certified": False,
            "state_radius": None,
            "q": q,
            "preconditioner_norm": a_norm,
            "image_radius": image_radius,
            "branch_radius": r,
            "self_map_lhs": self_map_lhs,
            "data_budget": data_budget,
            "reason": "raw-data uncertainty does not map the declared branch into itself",
        }

    return {
        "status": "CERTIFIED",
        "branch_certified": True,
        "local_uniqueness": True,
        "q": q,
        "preconditioner_norm": a_norm,
        "inverse_factor": inverse_factor,
        "sample_center_discrepancy": d,
        "sensor_radius": sigma,
        "forward_model_radius": tau,
        "image_radius": image_radius,
        "branch_radius": r,
        "self_map_lhs": self_map_lhs,
        "data_budget": data_budget,
        "state_radius": state_radius,
        "reason": (
            "Banach contraction/self-map gates certify one unique solution inside the "
            "declared finite local sample branch for every data vector in the raw-data box"
        ),
    }
