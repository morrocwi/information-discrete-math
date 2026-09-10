from fractions import Fraction

import pytest

from idm.finite_interval_inverse import (
    rowwise_hadamard_inverse_bound,
    rowwise_hadamard_local_radius,
)


def test_exact_diagonal_two_by_two_bound():
    # J0=diag(2,3): row bounds are exact and |det J0|=6.
    out = rowwise_hadamard_inverse_bound(
        jacobian_row_l1_bounds=[2, 3],
        determinant_abs_lower_bound=6,
    )
    assert out["status"] == "CERTIFIED"
    assert out["column_entry_bounds"] == [Fraction(1, 2), Fraction(1, 3)]
    # This is a safe row-sum bound. It need not be sharp: actual ||J0^-1||_inf=1/2.
    assert out["inverse_infinity_norm_bound"] == Fraction(5, 6)


def test_rowwise_radius_is_exact_fraction():
    # With H=(1,2), slope=(1/2)*1+(1/3)*2=7/6.
    # Requiring q<=1/2 gives r=(1/2)/(7/6)=3/7.
    out = rowwise_hadamard_local_radius(
        jacobian_row_l1_bounds=[2, 3],
        jacobian_row_variation_per_state_radius=[1, 2],
        determinant_abs_lower_bound=6,
        target_defect=Fraction(1, 2),
    )
    assert out["defect_slope"] == Fraction(7, 6)
    assert out["radius"] == Fraction(3, 7)
    assert out["defect_slope"] * out["radius"] == Fraction(1, 2)


def test_zero_variation_has_no_finite_radius_limit_from_this_bound():
    out = rowwise_hadamard_local_radius(
        jacobian_row_l1_bounds=[2],
        jacobian_row_variation_per_state_radius=[0],
        determinant_abs_lower_bound=2,
    )
    assert out["status"] == "CERTIFIED"
    assert out["defect_slope"] == 0
    assert out["radius"] is None


def test_rejects_invalid_certificate_inputs():
    with pytest.raises(ValueError):
        rowwise_hadamard_inverse_bound(jacobian_row_l1_bounds=[])
    with pytest.raises(ValueError):
        rowwise_hadamard_inverse_bound(jacobian_row_l1_bounds=[1, 0])
    with pytest.raises(ValueError):
        rowwise_hadamard_inverse_bound(
            jacobian_row_l1_bounds=[1], determinant_abs_lower_bound=0
        )
    with pytest.raises(ValueError):
        rowwise_hadamard_local_radius(
            jacobian_row_l1_bounds=[1, 1],
            jacobian_row_variation_per_state_radius=[1],
        )
    with pytest.raises(ValueError):
        rowwise_hadamard_local_radius(
            jacobian_row_l1_bounds=[1],
            jacobian_row_variation_per_state_radius=[-1],
        )
    with pytest.raises(ValueError):
        rowwise_hadamard_local_radius(
            jacobian_row_l1_bounds=[1],
            jacobian_row_variation_per_state_radius=[1],
            target_defect=1,
        )
