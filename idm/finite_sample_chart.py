"""Finite algebra for converting contiguous Taylor-jet charts to sample-time charts.

This module is deliberately independent of any particular ODE/PDE.  Suppose an
analytic finite-dimensional observation channel has a local expansion

    y_s(h t, x) = sum_{n>=0} a_{s,n}(x) (h t)^n.

If a square jet chart is formed by taking, for each channel s, the contiguous rows
D a_{s,0},...,D a_{s,r_s}, then sampling that channel at r_s+1 distinct nodes
`t_{s,j}` produces a sample-chart determinant whose lowest possible nonzero power of
h is

    p = sum_s r_s(r_s+1)/2,

with leading coefficient

    det(J_jet) * product_s det(V_s),

where V_s[j,n] = t_{s,j}^n.

The finite algebra below certifies only that leading coefficient.  To conclude that an
actual sample-time map is locally invertible for all sufficiently small nonzero h, the
caller must separately justify analyticity (or a suitable asymptotic expansion) and
that the declared jet determinant is the relevant square Jacobian minor.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Sequence


def _q(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def vandermonde_determinant(nodes: Sequence[object]) -> Fraction:
    """Return the exact Vandermonde determinant `prod_{i<j}(t_j-t_i)`.

    Distinctness is not required by this helper: repeated nodes correctly return zero.
    """
    xs = [_q(x) for x in nodes]
    out = Fraction(1)
    for i in range(len(xs)):
        for j in range(i + 1, len(xs)):
            out *= xs[j] - xs[i]
    return out


def contiguous_sample_chart_leading_term(
    *,
    jet_determinant: object,
    channel_nodes: Sequence[Sequence[object]],
) -> dict:
    """Certify the exact leading factor for a contiguous-jet sample chart.

    `channel_nodes[s]` contains the sample nodes for one channel.  A channel with `m`
    nodes is paired with Taylor orders `0,...,m-1`.  The returned leading power is
    therefore `sum_s m_s(m_s-1)/2`.

    The function fails closed when the declared square jet determinant is zero or any
    channel repeats a sample node, because then this leading-term route cannot certify
    a nonzero sample determinant.
    """
    det_jet = _q(jet_determinant)
    nodes = [list(group) for group in channel_nodes]
    if not nodes:
        raise ValueError("at least one observation channel is required")
    if any(len(group) == 0 for group in nodes):
        raise ValueError("every channel must contain at least one sample node")

    v_dets = [vandermonde_determinant(group) for group in nodes]
    power = sum(len(group) * (len(group) - 1) // 2 for group in nodes)
    leading = det_jet
    for d in v_dets:
        leading *= d

    if det_jet == 0:
        return {
            "status": "HOLD",
            "leading_power": power,
            "jet_determinant": det_jet,
            "vandermonde_determinants": v_dets,
            "leading_coefficient": Fraction(0),
            "reason": "declared jet determinant is zero",
        }
    if any(d == 0 for d in v_dets):
        return {
            "status": "HOLD",
            "leading_power": power,
            "jet_determinant": det_jet,
            "vandermonde_determinants": v_dets,
            "leading_coefficient": Fraction(0),
            "reason": "at least one channel repeats a sample node",
        }

    return {
        "status": "CERTIFIED",
        "leading_power": power,
        "jet_determinant": det_jet,
        "vandermonde_determinants": v_dets,
        "leading_coefficient": leading,
        "reason": "nonzero jet determinant and distinct per-channel sample nodes give a nonzero leading sample determinant coefficient",
    }
