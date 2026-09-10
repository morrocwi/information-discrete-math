from fractions import Fraction

from idm.finite_interval_inverse import (
    Interval,
    certified_interval_inverse_factor,
    interval_matrix_from_mid_radius,
    preconditioned_defect_bound,
)


def test_exact_linear_inverse_has_zero_defect():
    # J = diag(2,4), A = diag(1/2,1/4).
    J = interval_matrix_from_mid_radius(
        [[2, 0], [0, 4]],
        [[0, 0], [0, 0]],
    )
    A = [[Fraction(1, 2), 0], [0, Fraction(1, 4)]]
    out = certified_interval_inverse_factor(preconditioner=A, jacobian_interval=J)
    assert out["status"] == "CERTIFIED"
    assert out["q"] == 0
    assert out["preconditioner_norm"] == Fraction(1, 2)
    assert out["factor"] == Fraction(1, 2)


def test_small_interval_uncertainty_remains_certified():
    J = interval_matrix_from_mid_radius(
        [[2, 0], [0, 2]],
        [[Fraction(1, 10), 0], [0, Fraction(1, 10)]],
    )
    A = [[Fraction(1, 2), 0], [0, Fraction(1, 2)]]
    # I-AJ has diagonal interval [-1/20,1/20].
    q = preconditioned_defect_bound(preconditioner=A, jacobian_interval=J)
    assert q == Fraction(1, 20)
    out = certified_interval_inverse_factor(preconditioner=A, jacobian_interval=J)
    assert out["status"] == "CERTIFIED"
    assert out["factor"] == Fraction(10, 19)


def test_large_uncertainty_fails_closed():
    J = interval_matrix_from_mid_radius(
        [[1]],
        [[2]],
    )
    out = certified_interval_inverse_factor(
        preconditioner=[[1]],
        jacobian_interval=J,
    )
    assert out["status"] == "HOLD"
    assert out["q"] == 2
    assert out["factor"] is None


def test_interval_product_handles_signs_exactly():
    a = Interval(Fraction(-2), Fraction(3))
    b = Interval(Fraction(-5), Fraction(-1))
    c = a * b
    assert c.lo == Fraction(-15)
    assert c.hi == Fraction(10)
