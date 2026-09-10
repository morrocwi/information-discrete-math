"""Fail-closed quantitative local inverse certificate.

This is a generic finite-dimensional theorem helper for EPSC-18.  It does not
compute an Navier-Stokes observability Jacobian by itself.

Let H:B subset R^n -> R^n be C^1 on a convex, already-selected symmetry slice,
and let A be a fixed preconditioner.  If a certified enclosure proves

    sup_{x in B} ||I - A DH(x)|| <= q < 1,

then for x,z in B,

    ||x-z|| <= ||A||/(1-q) * ||H(x)-H(z)||.

Thus if the true observation differs from measured data by at most sigma_meas
and the reconstructed state's forward residual is at most sigma_res, then

    rho <= ||A||/(1-q) * (sigma_meas + sigma_res),

provided both true and reconstructed states are certified to lie in the same
convex branch/symmetry slice B.  Branch/slice containment is an explicit input;
it is never inferred from rank saturation.
"""
from __future__ import annotations

import math


def _nn(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return value


def preconditioned_inverse_factor(*, preconditioner_norm: float, defect_bound: float) -> float:
    """Return ||A||/(1-q) for a certified q<1 Jacobian defect enclosure."""
    a = _nn("preconditioner_norm", preconditioner_norm)
    q = _nn("defect_bound", defect_bound)
    if q >= 1.0:
        raise ValueError("defect_bound must be strictly below 1 for certification")
    return a / (1.0 - q)


def certified_local_inverse_radius(
    *,
    measurement_radius: float,
    forward_residual_radius: float,
    preconditioner_norm: float,
    defect_bound: float,
) -> float:
    """Quantitative radius on a previously certified common branch/slice."""
    sigma = _nn("measurement_radius", measurement_radius) + _nn(
        "forward_residual_radius", forward_residual_radius
    )
    return preconditioned_inverse_factor(
        preconditioner_norm=preconditioner_norm, defect_bound=defect_bound
    ) * sigma


def certified_local_inverse_verdict(
    *,
    measurement_radius: float,
    forward_residual_radius: float,
    preconditioner_norm: float | None,
    defect_bound: float | None,
    branch_containment_certified: bool,
    symmetry_slice_certified: bool,
) -> dict:
    """Fail closed unless every local inverse obligation is supplied."""
    if not symmetry_slice_certified:
        return {
            "status": "HOLD",
            "radius": None,
            "reason": "symmetry slice/gauge is not certified",
            "tier": "conditional_certificate",
        }
    if not branch_containment_certified:
        return {
            "status": "HOLD",
            "radius": None,
            "reason": "true and reconstructed states are not certified in one convex inverse branch",
            "tier": "conditional_certificate",
        }
    if preconditioner_norm is None or defect_bound is None:
        return {
            "status": "HOLD",
            "radius": None,
            "reason": "preconditioned Jacobian enclosure is incomplete",
            "tier": "conditional_certificate",
        }
    try:
        radius = certified_local_inverse_radius(
            measurement_radius=measurement_radius,
            forward_residual_radius=forward_residual_radius,
            preconditioner_norm=preconditioner_norm,
            defect_bound=defect_bound,
        )
    except ValueError as exc:
        return {
            "status": "HOLD",
            "radius": None,
            "reason": str(exc),
            "tier": "conditional_certificate",
        }
    return {
        "status": "CERTIFIED",
        "radius": radius,
        "inverse_factor": preconditioned_inverse_factor(
            preconditioner_norm=preconditioner_norm, defect_bound=defect_bound
        ),
        "measurement_radius": float(measurement_radius),
        "forward_residual_radius": float(forward_residual_radius),
        "defect_bound": float(defect_bound),
        "preconditioner_norm": float(preconditioner_norm),
        "scope": "declared convex branch of a certified symmetry-fixed finite observation map",
        "tier": "conditional_certificate",
    }
