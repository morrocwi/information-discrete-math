from fractions import Fraction

import pytest

from idm.finite_feasible_set import (
    certify_finite_feasible_set,
    conditional_inverse_feasible_bound,
    inf_distance,
)


def test_inf_distance_exact():
    assert inf_distance([0, Fraction(1, 2)], [Fraction(1, 3), 1]) == Fraction(1, 2)


def test_exact_finite_feasible_set_and_witness_radius():
    records = [[0, 0], [1, 0], [2, 0]]
    readouts = [[0, 0], [1, 1], [3, 3]]
    out = certify_finite_feasible_set(
        records=records,
        readouts=readouts,
        observation=[Fraction(1, 2), Fraction(1, 2)],
        measurement_radius=Fraction(1, 2),
    )
    assert out["status"] == "CERTIFIED_FINITE_SET"
    assert out["finite_native"] is True
    assert out["feasible_indices"] == [0, 1]
    assert out["feasible_count"] == 2
    assert out["witness_index"] == 0
    assert out["witness_state_radius"] == 1
    assert out["feasible_diameter"] == 1


def test_model_radius_is_part_of_finite_box():
    out = certify_finite_feasible_set(
        records=[[0], [1]],
        readouts=[[0], [1]],
        observation=[Fraction(3, 4)],
        measurement_radius=Fraction(1, 8),
        model_radius=Fraction(1, 8),
    )
    assert out["feasible_indices"] == [1]
    assert out["effective_readout_radius"] == Fraction(1, 4)


def test_empty_finite_feasible_set_holds():
    out = certify_finite_feasible_set(
        records=[[0], [1]],
        readouts=[[0], [1]],
        observation=[10],
        measurement_radius=0,
    )
    assert out["status"] == "HOLD"
    assert out["feasible_count"] == 0


def test_explicit_witness_must_be_feasible():
    with pytest.raises(ValueError, match="feasible"):
        certify_finite_feasible_set(
            records=[[0], [1]],
            readouts=[[0], [1]],
            observation=[0],
            measurement_radius=0,
            witness_index=1,
        )


def test_conditional_pairwise_bound_is_finite_arithmetic():
    out = conditional_inverse_feasible_bound(
        inverse_factor=Fraction(3, 2),
        effective_readout_radius=Fraction(1, 10),
    )
    assert out["status"] == "FINITE_BOUND"
    assert out["feasible_diameter_upper_bound"] == Fraction(3, 10)
