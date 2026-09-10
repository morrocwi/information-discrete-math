from fractions import Fraction

from idm.finite_sample_chart import (
    contiguous_sample_chart_leading_term,
    vandermonde_determinant,
)


def test_vandermonde_exact_small_case():
    # det [[1,0,0],[1,1,1],[1,2,4]] = (1-0)(2-0)(2-1) = 2.
    assert vandermonde_determinant([0, 1, 2]) == 2


def test_n1_style_two_24_sample_channels_have_power_552():
    out = contiguous_sample_chart_leading_term(
        jet_determinant=Fraction(3, 7),
        channel_nodes=[list(range(24)), list(range(24)), [0]],
    )
    assert out["status"] == "CERTIFIED"
    assert out["leading_power"] == 552
    assert all(d != 0 for d in out["vandermonde_determinants"])
    assert out["leading_coefficient"] != 0


def test_repeated_node_fails_closed():
    out = contiguous_sample_chart_leading_term(
        jet_determinant=1,
        channel_nodes=[[0, 1, 1], [0]],
    )
    assert out["status"] == "HOLD"
    assert out["leading_coefficient"] == 0


def test_zero_jet_determinant_fails_closed():
    out = contiguous_sample_chart_leading_term(
        jet_determinant=0,
        channel_nodes=[[0, 1], [2]],
    )
    assert out["status"] == "HOLD"
    assert out["leading_coefficient"] == 0
