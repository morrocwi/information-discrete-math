from fractions import Fraction

import pytest

from idm.finite_sample_branch import certified_direct_sample_branch, matrix_inf_norm


def test_matrix_inf_norm_exact():
    A = [[Fraction(1, 2), -1], [Fraction(1, 3), Fraction(1, 3)]]
    assert matrix_inf_norm(A) == Fraction(3, 2)


def test_direct_sample_branch_certifies_contraction_self_map():
    # ||A||_inf=1, q=1/4, r=1.  Total raw image uncertainty=1/2, so
    # 1*(1/2)+(1/4)*1=3/4 <= 1 and the branch is certified.
    out = certified_direct_sample_branch(
        preconditioner=[[1, 0], [0, 1]],
        jacobian_defect_bound=Fraction(1, 4),
        branch_radius=1,
        sample_center_discrepancy=Fraction(1, 8),
        sensor_radius=Fraction(1, 8),
        forward_model_radius=Fraction(1, 4),
    )
    assert out["status"] == "CERTIFIED"
    assert out["branch_certified"] is True
    assert out["local_uniqueness"] is True
    assert out["inverse_factor"] == Fraction(4, 3)
    assert out["state_radius"] == Fraction(2, 3)
    assert out["state_radius"] <= out["branch_radius"]


def test_direct_sample_branch_holds_when_q_not_below_one():
    out = certified_direct_sample_branch(
        preconditioner=[[1]],
        jacobian_defect_bound=1,
        branch_radius=1,
        sample_center_discrepancy=0,
        sensor_radius=0,
        forward_model_radius=0,
    )
    assert out["status"] == "HOLD"
    assert out["branch_certified"] is False


def test_direct_sample_branch_holds_when_data_box_too_large():
    out = certified_direct_sample_branch(
        preconditioner=[[2]],
        jacobian_defect_bound=Fraction(1, 4),
        branch_radius=1,
        sample_center_discrepancy=Fraction(1, 2),
        sensor_radius=Fraction(1, 2),
        forward_model_radius=0,
    )
    assert out["status"] == "HOLD"
    assert out["branch_certified"] is False
    assert out["self_map_lhs"] > out["branch_radius"]


def test_invalid_negative_uncertainty_fails_closed():
    with pytest.raises(ValueError):
        certified_direct_sample_branch(
            preconditioner=[[1]],
            jacobian_defect_bound=Fraction(1, 2),
            branch_radius=1,
            sample_center_discrepancy=-1,
            sensor_radius=0,
            forward_model_radius=0,
        )
