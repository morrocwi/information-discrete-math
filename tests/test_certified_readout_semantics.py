from fractions import Fraction

from idm import certified as cr


def test_geometric_is_target_certified():
    out = cr.geom_series(Fraction(1, 3), Fraction(1, 10**12))
    assert out.status == cr.CERTIFIED
    assert out.certified
    assert not out.stable
    assert abs(out.q - Fraction(3, 2)) <= out.bound


def test_exponential_is_exact_rational_target_certificate():
    out = cr.exp("0.4", "1e-20")
    assert out.status == cr.CERTIFIED
    assert isinstance(out.q, Fraction)
    assert isinstance(out.bound, Fraction)
    assert out.bound <= Fraction(1, 10**20)


def test_simpson_refuses_inexact_node_values():
    out = cr.simpson(lambda x: float(x) ** 2, 0, 1, "1e-6", d4_bound=0)
    assert out.status == cr.HOLD


def test_simpson_certifies_exact_rational_polynomial():
    out = cr.simpson(lambda x: x**2, 0, 3, Fraction(1, 10**9), d4_bound=0)
    assert out.status == cr.CERTIFIED
    assert out.q == 9
    assert out.bound == 0


def test_apriori_richardson_is_not_promoted_to_target_certificate():
    out = cr.richardson_apriori_certified(Fraction(1, 10**8), 2, Fraction(1, 10**6))
    assert out.status == cr.STABLE
    assert out.stable
    assert not out.certified


def test_integral_refinement_is_stability_only():
    out = cr.integral(lambda x: x*x, 0, 1, "1e-6")
    assert out.status == cr.STABLE
    assert out.stable
    assert not out.certified
