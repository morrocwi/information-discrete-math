"""Finite branch-conditioned chart-uncertainty to state-radius adapter.

This module contains no continuum object and assumes no completed infinity.  It is the
measurement-side companion to :mod:`idm.finite_interval_inverse`.

Given a finite local observation chart H on a *separately certified common branch* B,
a fixed preconditioner A, and an interval enclosure J(B) of DH, the exact finite gate

    q = ||I - A J(B)||_infinity < 1

implies an inverse factor

    alpha = ||A||_infinity / (1-q).

If chart data y has certified radius sigma around H(x), and a reconstruction candidate
z in the same branch has certified forward residual tau around y, then

    ||x-z||_infinity <= alpha * (sigma + tau).

The branch hypothesis is intentionally not inferred by this helper.  If the inverse
gate fails, the result is HOLD.  Raw-sensor-to-chart conversion, branch capture and any
outer/continuum adapter remain separate caller obligations.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Sequence

from .finite_interval_inverse import Interval, certified_interval_inverse_factor


def _q(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def certified_branch_chart_state_radius(
    *,
    preconditioner: Sequence[Sequence[object]],
    jacobian_interval: Sequence[Sequence[Interval]],
    measurement_radius: object,
    forward_residual_radius: object = 0,
    branch_certified: bool,
) -> dict:
    """Return a fail-closed finite state radius from chart uncertainty.

    Parameters
    ----------
    preconditioner, jacobian_interval:
        Inputs to the exact finite interval inverse gate.
    measurement_radius:
        Certified infinity-norm radius ``sigma`` for ``y-H(x)``.
    forward_residual_radius:
        Certified infinity-norm radius ``tau`` for ``H(z)-y``.
    branch_certified:
        Must be true only when both the unknown true state and the candidate are
        independently certified to lie in the same declared local inverse branch.

    Returns
    -------
    dict
        ``CERTIFIED`` with exact ``state_radius`` when both branch and q<1 gates pass;
        otherwise ``HOLD``.  The helper does not manufacture branch membership.
    """
    sigma = _q(measurement_radius)
    tau = _q(forward_residual_radius)
    if sigma < 0 or tau < 0:
        raise ValueError("uncertainty radii must be nonnegative")

    if not branch_certified:
        return {
            "status": "HOLD",
            "state_radius": None,
            "reason": "common inverse branch has not been independently certified",
        }

    inv = certified_interval_inverse_factor(
        preconditioner=preconditioner,
        jacobian_interval=jacobian_interval,
    )
    if inv["status"] != "CERTIFIED":
        return {
            **inv,
            "state_radius": None,
            "measurement_radius": sigma,
            "forward_residual_radius": tau,
            "reason": "finite interval inverse gate did not certify q<1",
        }

    image_radius = sigma + tau
    return {
        **inv,
        "status": "CERTIFIED",
        "measurement_radius": sigma,
        "forward_residual_radius": tau,
        "image_radius": image_radius,
        "state_radius": inv["factor"] * image_radius,
        "branch_certified": True,
        "reason": "same-branch chart uncertainty propagated through a certified finite inverse factor",
    }
