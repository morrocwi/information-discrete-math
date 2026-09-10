from fractions import Fraction

from idm.finite_interval_inverse import preconditioned_row_variation_radius


def test_exact_preconditioner_row_variation_radius():
    # A is an exact point preconditioner. H_j bounds the l1 variation of
    # Jacobian row j per unit state infinity-radius.
    A = [
        [Fraction(1, 2), Fraction(1, 4)],
        [Fraction(-1, 3), Fraction(2, 3)],
    ]
    H = [Fraction(3), Fraction(5)]
    out = preconditioned_row_variation_radius(
        preconditioner=A,
        jacobian_row_variation_per_state_radius=H,
        target_defect=Fraction(1, 2),
    )

    # weighted slopes: row0=1/2*3+1/4*5=11/4;
    # row1=1/3*3+2/3*5=13/3, so S=13/3 and r=(1/2)/S=3/26.
    assert out["status"] == "CERTIFIED"
    assert out["defect_slope"] == Fraction(13, 3)
    assert out["radius"] == Fraction(3, 26)
    assert out["preconditioner_infinity_norm"] == Fraction(1)


def test_zero_variation_has_no_finite_radius_limit():
    out = preconditioned_row_variation_radius(
        preconditioner=[[1, 0], [0, 1]],
        jacobian_row_variation_per_state_radius=[0, 0],
    )
    assert out["status"] == "CERTIFIED"
    assert out["radius"] is None
    assert out["defect_slope"] == 0


def test_dimension_mismatch_fails_closed_by_exception():
    try:
        preconditioned_row_variation_radius(
            preconditioner=[[1, 0], [0, 1]],
            jacobian_row_variation_per_state_radius=[1],
        )
    except ValueError as exc:
        assert "length" in str(exc)
    else:
        raise AssertionError("dimension mismatch should raise ValueError")
