"""Fail-closed finite direct-sample inequality gate.

This module deliberately stops at finite rational inequalities.  It does **not**
promote Banach fixed-point existence, uniqueness of a real root, or membership of an
unknown real state in a branch to a native finite theorem.

For a declared square observation map S on a branch B(z,r), a caller supplies a square
preconditioner A and a certified defect bound

    q >= sup_{x in B} ||I - A DS(x)||_inf.

For raw data centered at y_obs with sensor radius sigma and a finite approximation
y_model to S(z) with model radius tau, put

    delta = ||y_obs-y_model||_inf + sigma + tau.

The finite gate checks

    q < 1,
    ||A||_inf * delta + q r <= r.

These are exact finite/rational statements and yield the finite budgets

    data_budget = (1-q) r / ||A||_inf,
    conditional_radius = ||A||_inf/(1-q) * delta.

Interpreting those inequalities as proving that a real contraction has an attained
fixed point requires additional +R assumptions (in particular completeness/real
existence).  The API therefore returns ``FINITE_GATE_PASS`` rather than ``CERTIFIED``
and does not set ``branch_certified`` or ``local_uniqueness`` to true.

A finite-native caller may instead combine this gate with a separately supplied finite
witness/exclusion certificate over a declared finite state set.  A continuum/real-
analysis caller may attach Banach's theorem explicitly as a different tier.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Sequence


def _q(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def _rows(matrix: Sequence[Sequence[object]]) -> list[list[Fraction]]:
    rows = [[_q(v) for v in row] for row in matrix]
    if not rows or not rows[0]:
        raise ValueError("nonempty matrix required")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("rectangular matrix required")
    return rows


def matrix_inf_norm(matrix: Sequence[Sequence[object]]) -> Fraction:
    rows = _rows(matrix)
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
    """Evaluate the finite direct-sample self-map/contraction inequalities.

    Despite the historical function name, a passing result is *not* itself a native
    finite proof that a real root exists in the branch.  It returns a finite gate plus
    the radius that would follow after a separately justified existence/branch premise.
    """
    rows = _rows(preconditioner)
    if len(rows) != len(rows[0]):
        raise ValueError("preconditioner must be square")

    q = _q(jacobian_defect_bound)
    r = _q(branch_radius)
    d = _q(sample_center_discrepancy)
    sigma = _q(sensor_radius)
    tau = _q(forward_model_radius)
    if r <= 0:
        raise ValueError("branch_radius must be positive")
    if any(v < 0 for v in (q, d, sigma, tau)):
        raise ValueError("defect and uncertainty quantities must be nonnegative")

    a_norm = matrix_inf_norm(rows)
    image_radius = d + sigma + tau

    if q >= 1:
        return {
            "status": "HOLD",
            "finite_gate_pass": False,
            "branch_certified": False,
            "local_uniqueness": False,
            "state_radius": None,
            "q": q,
            "reason": "branch-wide preconditioned Jacobian defect is not below one",
        }

    self_map_lhs = a_norm * image_radius + q * r
    self_map_ok = self_map_lhs <= r
    inverse_factor = a_norm / (1 - q)
    conditional_state_radius = inverse_factor * image_radius
    data_budget = (1 - q) * r / a_norm if a_norm > 0 else None

    common = {
        "q": q,
        "preconditioner_norm": a_norm,
        "image_radius": image_radius,
        "branch_radius": r,
        "self_map_lhs": self_map_lhs,
        "data_budget": data_budget,
        "inverse_factor": inverse_factor,
        "conditional_state_radius": conditional_state_radius,
        "branch_certified": False,
        "local_uniqueness": False,
        "state_radius": None,
    }

    if not self_map_ok:
        return {
            **common,
            "status": "HOLD",
            "finite_gate_pass": False,
            "reason": "raw-data uncertainty does not satisfy the declared finite self-map inequality",
        }

    return {
        **common,
        "status": "FINITE_GATE_PASS",
        "finite_gate_pass": True,
        "sample_center_discrepancy": d,
        "sensor_radius": sigma,
        "forward_model_radius": tau,
        "real_analysis_tier": "+R-Open",
        "real_analysis_implication": (
            "If a complete real metric-space interpretation of the declared map/branch is separately "
            "granted and the derivative defect bound applies there, Banach's theorem would imply one "
            "local root and the displayed conditional_state_radius. This implication is not promoted "
            "to a native finite theorem by this helper."
        ),
        "reason": "exact finite q<1 and self-map budget inequalities pass; real root existence remains separately tiered",
    }
