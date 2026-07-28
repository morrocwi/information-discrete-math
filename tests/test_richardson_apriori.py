"""Richardson A-PRIORI stability certificate (THEOREM.md open #1).

`richardson_certified` is a-posteriori — it watches the actual refinement gaps and checks they
contract.  The a-priori certificate instead reads the contraction ratio off the method ORDER: an
order-p method under step halving has column-gap ratio ρ = 2^(−p), a constant known before any
refinement is computed.  Then `refine_stable` bounds all further disagreement by g/(1−ρ) from a single
gap.  The Coq side is machine-checked axiom-free in formal/IDM_Apriori.v (richardson_ratio,
richardson_apriori_contracts, richardson_apriori_stable); these tests run the numerics and confirm the
a-priori ρ genuinely envelopes what an order-p method actually does.

Pure-Python (no numpy) so the core compute job runs it.
"""

from fractions import Fraction as Q

import idm  # noqa: F401  (activates the bridge so idm.certified re-exports resolve)
from idm.certified import (
    richardson_apriori_ratio,
    richardson_apriori_bound,
    richardson_apriori_certified,
)


# --------------------------------------------------------------------------- #
#  1. The a-priori ratio is exact and matches the Coq richardson_ratio.        #
# --------------------------------------------------------------------------- #
def test_apriori_ratio_is_exact_power_of_two():
    assert richardson_apriori_ratio(1) == Q(1, 2)
    assert richardson_apriori_ratio(2) == Q(1, 4)
    assert richardson_apriori_ratio(3) == Q(1, 8)
    assert richardson_apriori_ratio(4) == Q(1, 16)


def test_order_below_one_is_rejected():
    import pytest
    with pytest.raises(ValueError):
        richardson_apriori_ratio(0)


# --------------------------------------------------------------------------- #
#  2. The a-priori bound is exactly the refine_stable constant g/(1−ρ).        #
# --------------------------------------------------------------------------- #
def test_apriori_bound_is_refine_stable_constant():
    g = Q(3, 1000)
    for order in (1, 2, 3):
        rho = richardson_apriori_ratio(order)
        assert richardson_apriori_bound(g, order) == g / (1 - rho)


# --------------------------------------------------------------------------- #
#  3. CERTIFIED / HOLD gating on the a-priori bound vs ε.                       #
# --------------------------------------------------------------------------- #
def test_certified_when_bound_within_eps_else_hold():
    tiny = richardson_apriori_certified(Q(1, 10 ** 9), 2, Q(1, 10 ** 6))
    assert tiny.status == "CERTIFIED" and tiny.bound <= Q(1, 10 ** 6)
    big = richardson_apriori_certified(Q(1, 2), 2, Q(1, 10 ** 6))
    assert big.status == "HOLD" and big.bound > Q(1, 10 ** 6)


# --------------------------------------------------------------------------- #
#  4. The a-priori ρ genuinely ENVELOPES a real order-2 method.                #
#     Trapezoid of a smooth integrand has error ~ C·h², so under step halving  #
#     the successive-gap ratio → 1/4 = ρ(order 2).  The a-priori ρ must be an   #
#     UPPER bound on the observed asymptotic ratio (never smaller), and the     #
#     a-priori tail bound from one gap must actually contain the true remaining #
#     disagreement.  This is the honesty check on "order p ⇒ ρ = 2^(−p)".      #
# --------------------------------------------------------------------------- #
def _trapezoid(f, a, b, n):
    h = (b - a) / n
    return h * (f(a) / 2 + f(b) / 2 + sum(f(a + i * h) for i in range(1, n)))


def test_apriori_ratio_envelopes_order2_trapezoid():
    f = lambda x: x ** 3 - 2.0 * x ** 2 + 1.0        # smooth ⇒ trapezoid is order 2
    a, b = 0.0, 1.0
    vals = [_trapezoid(f, a, b, 8 * 2 ** j) for j in range(9)]
    gaps = [abs(vals[i + 1] - vals[i]) for i in range(len(vals) - 1)]
    # observed tail contraction ratios
    tail = gaps[len(gaps) // 2:]
    ratios = [tail[i + 1] / tail[i] for i in range(len(tail) - 1) if tail[i] > 0]
    rho = float(richardson_apriori_ratio(2))          # = 0.25
    # the a-priori ρ envelopes the observed asymptotic ratio (small slack for finite-h)
    assert max(ratios) <= rho * 1.05, (max(ratios), rho)
    # and the a-priori bound from a single mid gap actually contains the true remaining disagreement
    N = len(gaps) // 2
    true_remaining = sum(gaps[N:])
    apriori = richardson_apriori_bound(gaps[N], 2)     # gap_N / (1 − 1/4)
    assert true_remaining <= float(apriori) + 1e-15, (true_remaining, float(apriori))
