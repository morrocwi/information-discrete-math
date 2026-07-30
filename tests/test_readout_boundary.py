from fractions import Fraction

import pytest

from idm.readout_boundary import (
    Decision,
    Enclosure,
    certify_threshold,
    determinant_collision,
    exact_det2x2,
    parse_decimal_readout,
    round_integer_to_binary_precision,
)


def test_decimal_token_is_exact_and_keeps_scale():
    readout = parse_decimal_readout("0.350")
    assert readout.numerator == 350
    assert readout.scale == 3
    assert readout.value == Fraction(7, 20)


def test_scientific_decimal_token_is_exact():
    readout = parse_decimal_readout("1.20e-2")
    assert readout.numerator == 120
    assert readout.scale == 4
    assert readout.value == Fraction(3, 250)


def test_nonfinite_tokens_are_rejected():
    for token in ("NaN", "Infinity", "-Infinity"):
        with pytest.raises(ValueError):
            parse_decimal_readout(token)


def test_operational_threshold_certificate():
    assert certify_threshold(Fraction(11, 10), Fraction(1, 20), 1) is Decision.ABOVE
    assert certify_threshold(Fraction(9, 10), Fraction(1, 20), 1) is Decision.BELOW
    assert certify_threshold(Fraction(1), Fraction(0), 1) is Decision.EQUAL
    assert certify_threshold(Fraction(1), Fraction(1, 20), 1) is Decision.UNCERTIFIED


def test_enclosure_rejects_negative_radius():
    with pytest.raises(ValueError):
        Enclosure.around(0, -1)


def test_exact_determinant_witness():
    n = 10**8
    assert exact_det2x2(n, n - 1, n + 1, n) == 1
    assert float(n) * float(n) - float(n - 1) * float(n + 1) == 0.0


@pytest.mark.parametrize("precision", [3, 4, 8, 24, 53])
def test_precision_parametric_collision(precision):
    assert determinant_collision(precision) == (1, 0)


def test_ties_to_even_integer_rounding():
    # At precision 4, 31 lies halfway between 30 and 32; the even significand is 32.
    assert round_integer_to_binary_precision(31, 4) == 32
