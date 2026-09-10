from fractions import Fraction

import pytest

from idm.finite_sample_chart import (
    contiguous_sample_chart_leading_term,
    scaled_taylor_noise_amplification,
    vandermonde_determinant,
    vandermonde_inverse_rows,
)


def test_vandermonde_exact_small_case():
    # det [[1,0,0],[1,1,1],[1,2,4]] = (1-0)(2-0)(2-1) = 2.
    assert vandermonde_determinant([0, 1, 2]) == 2


def test_vandermonde_inverse_rows_small_case():
    # Samples (y0,y1) at nodes (0,1) recover p(t)=a0+a1 t as
    # a0=y0 and a1=-y0+y1.
    assert vandermonde_inverse_rows([0, 1]) == [
        [Fraction(1), Fraction(0)],
        [Fraction(-1), Fraction(1)],
    ]


def test_scaled_taylor_noise_amplification_is_exact_induced_inf_norm():
    # V^{-1} rows have l1 norms 1 and 2. With h=1/2 and scales (1,3),
    # the two row amplification factors are 1 and 3*(1/h)*2=12.
    out = scaled_taylor_noise_amplification(
        nodes=[0, 1],
        spacing=Fraction(1, 2),
        scales=[1, 3],
    )
    assert out["status"] == "CERTIFIED"
    assert out["inverse_row_l1_norms"] == [1, 2]
    assert out["row_amplifications"] == [1, 12]
    assert out["dominant_order"] == 1
    assert out["kappa_inf"] == 12


def test_smaller_spacing_amplifies_high_order_reconstruction():
    large_h = scaled_taylor_noise_amplification(
        nodes=[0, 1, 2],
        spacing=1,
        scales=[1, 1, 1],
    )["kappa_inf"]
    small_h = scaled_taylor_noise_amplification(
        nodes=[0, 1, 2],
        spacing=Fraction(1, 10),
        scales=[1, 1, 1],
    )["kappa_inf"]
    assert small_h > large_h


def test_interpolation_conditioning_rejects_repeated_nodes_and_zero_spacing():
    with pytest.raises(ValueError):
        vandermonde_inverse_rows([0, 1, 1])
    with pytest.raises(ValueError):
        scaled_taylor_noise_amplification(nodes=[0, 1], spacing=0)


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
