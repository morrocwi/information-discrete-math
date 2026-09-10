import math

from idm.certified_local_inverse import (
    certified_local_inverse_radius,
    certified_local_inverse_verdict,
    preconditioned_inverse_factor,
)


def test_linear_case_q_zero():
    # H(x)=2x, A=1/2 gives I-A DH=0 and factor=1/2.
    factor = preconditioned_inverse_factor(preconditioner_norm=0.5, defect_bound=0.0)
    assert factor == 0.5
    radius = certified_local_inverse_radius(
        measurement_radius=0.02,
        forward_residual_radius=0.01,
        preconditioner_norm=0.5,
        defect_bound=0.0,
    )
    assert math.isclose(radius, 0.015, rel_tol=0.0, abs_tol=1e-15)


def test_defect_inflates_radius():
    radius = certified_local_inverse_radius(
        measurement_radius=0.02,
        forward_residual_radius=0.01,
        preconditioner_norm=0.5,
        defect_bound=0.25,
    )
    assert math.isclose(radius, 0.02, rel_tol=0.0, abs_tol=1e-15)


def test_fail_closed_on_missing_slice_or_branch():
    kw = dict(
        measurement_radius=0.01,
        forward_residual_radius=0.0,
        preconditioner_norm=1.0,
        defect_bound=0.1,
    )
    assert certified_local_inverse_verdict(
        **kw, branch_containment_certified=True, symmetry_slice_certified=False
    )["status"] == "HOLD"
    assert certified_local_inverse_verdict(
        **kw, branch_containment_certified=False, symmetry_slice_certified=True
    )["status"] == "HOLD"


def test_fail_closed_when_q_not_below_one():
    out = certified_local_inverse_verdict(
        measurement_radius=0.01,
        forward_residual_radius=0.0,
        preconditioner_norm=1.0,
        defect_bound=1.0,
        branch_containment_certified=True,
        symmetry_slice_certified=True,
    )
    assert out["status"] == "HOLD"


def test_certified_when_all_obligations_are_explicit():
    out = certified_local_inverse_verdict(
        measurement_radius=0.01,
        forward_residual_radius=0.002,
        preconditioner_norm=1.5,
        defect_bound=0.2,
        branch_containment_certified=True,
        symmetry_slice_certified=True,
    )
    assert out["status"] == "CERTIFIED"
    assert math.isclose(out["radius"], 0.0225, rel_tol=0.0, abs_tol=1e-15)
