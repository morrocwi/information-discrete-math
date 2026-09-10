from fractions import Fraction

from idm.finite_interval_inverse import interval_matrix_from_mid_radius
from idm.finite_measurement_inverse import certified_branch_chart_state_radius


def test_chart_noise_propagates_on_certified_branch():
    # H'(x) is enclosed by diag(2,2) +/- 0.1; A=diag(1/2,1/2).
    J = interval_matrix_from_mid_radius(
        [[2, 0], [0, 2]],
        [[Fraction(1, 10), 0], [0, Fraction(1, 10)]],
    )
    A = [[Fraction(1, 2), 0], [0, Fraction(1, 2)]]
    out = certified_branch_chart_state_radius(
        preconditioner=A,
        jacobian_interval=J,
        measurement_radius=Fraction(1, 100),
        forward_residual_radius=Fraction(1, 200),
        branch_certified=True,
    )
    assert out["status"] == "CERTIFIED"
    assert out["q"] == Fraction(1, 20)
    assert out["factor"] == Fraction(10, 19)
    assert out["image_radius"] == Fraction(3, 200)
    assert out["state_radius"] == Fraction(3, 380)


def test_missing_branch_fails_closed_even_with_good_jacobian():
    J = interval_matrix_from_mid_radius([[1]], [[0]])
    out = certified_branch_chart_state_radius(
        preconditioner=[[1]],
        jacobian_interval=J,
        measurement_radius=Fraction(1, 1000),
        branch_certified=False,
    )
    assert out["status"] == "HOLD"
    assert out["state_radius"] is None
    assert "branch" in out["reason"]


def test_bad_interval_inverse_fails_closed():
    J = interval_matrix_from_mid_radius([[1]], [[2]])
    out = certified_branch_chart_state_radius(
        preconditioner=[[1]],
        jacobian_interval=J,
        measurement_radius=Fraction(1, 1000),
        branch_certified=True,
    )
    assert out["status"] == "HOLD"
    assert out["state_radius"] is None
    assert out["q"] == 2


def test_negative_uncertainty_is_rejected():
    J = interval_matrix_from_mid_radius([[1]], [[0]])
    try:
        certified_branch_chart_state_radius(
            preconditioner=[[1]],
            jacobian_interval=J,
            measurement_radius=-1,
            branch_certified=True,
        )
    except ValueError as exc:
        assert "nonnegative" in str(exc)
    else:
        raise AssertionError("negative uncertainty radius should be rejected")
