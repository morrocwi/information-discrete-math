"""Multi-dimensional quadrature by the SAME finite-stability certificate (THEOREM.md open #2).

`refine_stable` (formal/IDM_Certified.v) is a theorem about a SCALAR gap sequence — it is
dimension-agnostic.  So multi-D quadrature needs no new theorem: a tensor-product trapezoid refined
n→2n on every axis produces exactly such a sequence, and the identical gap-contraction certificate
applies.  For a smooth integrand the tensor trapezoid is order-2 per axis, so halving all axes
contracts the gaps by ρ→1/4 — the a-priori ratio of the Richardson certificate (order 2).

These tests run the real numerics: certified n-D readouts match the exact value, the exact-under-
refinement case certifies with bound 0, a singular integrand HOLDs, and the observed contraction
ratio sits at the a-priori 1/4 envelope.

Needs mpmath (the certified quadrature backend); pure-Python otherwise so the core compute job runs it.
"""

import pytest

import idm  # noqa: F401  (activates the bridge)
mp = pytest.importorskip("mpmath")
from idm.certified import integral_nd, richardson_apriori_ratio


# --------------------------------------------------------------------------- #
#  1. Contracting path: a genuinely order-2 integrand certifies to the exact    #
#     value within the stable bound.                                            #
# --------------------------------------------------------------------------- #
def test_2d_contracting_certifies_correct_value():
    # ∫∫ x²y² over [0,1]² = (1/3)(1/3) = 1/9
    r = integral_nd(lambda p: p[0] ** 2 * p[1] ** 2, [(0, 1), (0, 1)], mp.mpf(10) ** -4)
    assert r.certified
    assert abs(r.q - mp.mpf(1) / 9) <= max(r.bound, mp.mpf(10) ** -3)


def test_3d_contracting_certifies_correct_value():
    # ∫∫∫ (x²+y²+z²) over unit cube = 1
    r = integral_nd(lambda p: p[0] ** 2 + p[1] ** 2 + p[2] ** 2, [(0, 1)] * 3,
                    mp.mpf(10) ** -3, n0=4, refines=5)
    assert r.certified
    assert abs(r.q - 1) <= max(r.bound, mp.mpf(10) ** -2)


# --------------------------------------------------------------------------- #
#  2. Exact path: a tensor trapezoid integrates a (bi)linear form exactly, so   #
#     the gaps hit 0 — the readout is certified with bound 0, not spuriously    #
#     HELD.                                                                      #
# --------------------------------------------------------------------------- #
def test_bilinear_is_exact_under_refinement():
    # ∫∫ xy over [0,1]×[0,2] = 1, integrated exactly by the tensor trapezoid
    r = integral_nd(lambda p: p[0] * p[1], [(0, 1), (0, 2)], mp.mpf(10) ** -6)
    assert r.certified
    assert r.bound == 0
    assert abs(r.q - 1) <= mp.mpf(10) ** -6


# --------------------------------------------------------------------------- #
#  3. HOLD discipline: a singular integrand has no stable plateau → no value.    #
# --------------------------------------------------------------------------- #
def test_pole_holds():
    r = integral_nd(lambda p: 1 / (p[0] - mp.mpf("0.5")), [(0, 1), (0, 1)], mp.mpf(10) ** -4)
    assert r.status == "HOLD"


def test_zero_tolerance_holds():
    r = integral_nd(lambda p: p[0] + p[1], [(0, 1), (0, 1)], 0)
    assert r.status == "HOLD"


# --------------------------------------------------------------------------- #
#  4. The multi-D order-2 tensor trapezoid contracts at the a-priori 1/4 ratio   #
#     (the same envelope as the 1-D Richardson certificate) — halving ALL axes. #
# --------------------------------------------------------------------------- #
def test_observed_ratio_matches_apriori_quarter():
    from certified_readout import _tensor_trapezoid
    f = lambda p: mp.e ** (p[0] + p[1])              # smooth, non-polynomial ⇒ genuine order-2 error
    box = [(0, 1), (0, 1)]
    vals = [_tensor_trapezoid(f, box, 4 * 2 ** j) for j in range(6)]
    gaps = [abs(vals[i + 1] - vals[i]) for i in range(len(vals) - 1)]
    tail = gaps[len(gaps) // 2:]
    ratios = [float(tail[i + 1] / tail[i]) for i in range(len(tail) - 1) if tail[i] > 0]
    rho = float(richardson_apriori_ratio(2))         # 0.25
    assert max(ratios) <= rho * 1.05, (max(ratios), rho)
