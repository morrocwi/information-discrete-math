"""Finite algebra for converting contiguous Taylor-jet charts to sample-time charts.

This module is deliberately independent of any particular ODE/PDE. Suppose an
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

The module also exposes the exact infinity-norm amplification incurred when one first
interpolates samples back to Taylor coefficients and then applies declared row scales.
For one channel with sample vector y, nodes t_j, spacing h and scaled coefficients
z_n=s_n a_n,

    z = S D_h^{-1} V^{-1} y,

so the exact induced infinity norm is

    kappa_inf(h) = max_n |s_n| |h|^{-n} sum_j |(V^{-1})[n,j]|.

That formula is for the finite polynomial/interpolation operator itself. For an
analytic observation with a nonzero Taylor remainder, a separately certified sample
remainder must be added to measurement error before multiplying by kappa. This module
does not certify an ODE flow remainder, sample spacing, branch capture or continuum
interpretation.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Sequence


def _q(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def _poly_mul(a: Sequence[Fraction], b: Sequence[Fraction]) -> list[Fraction]:
    out = [Fraction(0) for _ in range(len(a) + len(b) - 1)]
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


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


def vandermonde_inverse_rows(nodes: Sequence[object]) -> list[list[Fraction]]:
    """Return exact rows of the inverse power-Vandermonde matrix.

    The matrix convention is `V[j,n] = t_j**n`. The returned row `n` therefore maps
    sample values at the declared nodes to the coefficient of `t**n` in the unique
    interpolation polynomial of degree `< len(nodes)`.
    """
    xs = [_q(x) for x in nodes]
    if not xs:
        raise ValueError("at least one sample node is required")
    if len(set(xs)) != len(xs):
        raise ValueError("sample nodes must be distinct")

    m = len(xs)
    rows = [[Fraction(0) for _ in range(m)] for _ in range(m)]
    for j, xj in enumerate(xs):
        # Lagrange basis L_j(t) = product_{k!=j}(t-x_k)/(x_j-x_k).
        coeff = [Fraction(1)]
        denom = Fraction(1)
        for k, xk in enumerate(xs):
            if k == j:
                continue
            coeff = _poly_mul(coeff, [-xk, Fraction(1)])
            denom *= xj - xk
        coeff = [c / denom for c in coeff]
        for n, c in enumerate(coeff):
            rows[n][j] = c
    return rows


def scaled_taylor_noise_amplification(
    *,
    nodes: Sequence[object],
    spacing: object,
    scales: Sequence[object] | None = None,
) -> dict:
    """Return the exact sample-to-scaled-Taylor infinity-norm amplification.

    Let `V[j,n]=nodes[j]**n`, `D_h=diag(h**n)` and `S=diag(scales[n])`.
    For samples of a degree-`m-1` polynomial at physical nodes `h*nodes[j]`, the
    coefficient recovery map followed by row scaling is

        S D_h^{-1} V^{-1}.

    This function returns its exact induced infinity norm. Therefore a sample error
    vector with `||e||_inf <= sigma` produces scaled-coefficient error at most
    `kappa_inf * sigma`. If an analytic-flow truncation/remainder contributes an
    additional sample-space radius `r_sample`, the same linear map gives the bound
    `kappa_inf * (sigma + r_sample)` after that remainder is independently certified.
    """
    xs = [_q(x) for x in nodes]
    if not xs:
        raise ValueError("at least one sample node is required")

    h = _q(spacing)
    if h == 0:
        raise ValueError("sample spacing must be nonzero")

    rows = vandermonde_inverse_rows(xs)
    m = len(xs)
    if scales is None:
        ss = [Fraction(1) for _ in range(m)]
    else:
        if len(scales) != m:
            raise ValueError("scales length must equal sample-node count")
        ss = [_q(s) for s in scales]

    h_abs = abs(h)
    row_l1 = [
        sum((abs(c) for c in row), Fraction(0))
        for row in rows
    ]
    row_amplifications = [
        abs(ss[n]) * row_l1[n] / (h_abs ** n)
        for n in range(m)
    ]
    kappa = max(row_amplifications)
    dominant_order = max(range(m), key=lambda n: row_amplifications[n])

    return {
        "status": "CERTIFIED",
        "node_count": m,
        "spacing": h,
        "scales": ss,
        "vandermonde_inverse_rows": rows,
        "inverse_row_l1_norms": row_l1,
        "row_amplifications": row_amplifications,
        "dominant_order": dominant_order,
        "kappa_inf": kappa,
        "reason": "exact induced infinity norm of S D_h^{-1} V^{-1}",
    }


def contiguous_sample_chart_leading_term(
    *,
    jet_determinant: object,
    channel_nodes: Sequence[Sequence[object]],
) -> dict:
    """Certify the exact leading factor for a contiguous-jet sample chart.

    `channel_nodes[s]` contains the sample nodes for one channel. A channel with `m`
    nodes is paired with Taylor orders `0,...,m-1`. The returned leading power is
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
