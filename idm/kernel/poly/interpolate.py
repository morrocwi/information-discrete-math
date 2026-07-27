"""Exact polynomial interpolation over ℚ (pillar P1.4, Wave 5).

Given ``n`` points ``(x_i, y_i)`` with DISTINCT rational ``x_i``, there is a UNIQUE polynomial of
degree ``< n`` passing through all of them. This module builds it two ways — :func:`lagrange` (the
Lagrange basis form) and :func:`newton` (Newton divided differences) — both EXACT over
``fractions.Fraction`` via the domain-parametrized :mod:`univariate` ring operations (``add``,
``mul``). Because the interpolating polynomial of bounded degree through a fixed point set is
unique, ``lagrange(points) == newton(points)`` for any valid input: two independently-derived
constructions landing on the identical ``UPoly`` is itself the correctness check, on top of exact
evaluation back through the source points.

No float anywhere. A duplicate ``x_i`` (division by zero in either construction) or an empty point
list raises ``ValueError`` rather than returning a wrong or degenerate answer.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple

from .coeffring import QRing
from .univariate import UPoly, add, mul


def _validate_points(points: Sequence[Tuple], D) -> List[Tuple]:
    """Normalize every (x, y) pair into the domain and check the DISTINCT-x_i precondition."""
    if not points:
        raise ValueError("interpolate: need at least one point, got an empty list")
    pts = [(D.normalize(x), D.normalize(y)) for x, y in points]
    xs = [x for x, _ in pts]
    if len(set(xs)) != len(xs):
        raise ValueError(f"interpolate: duplicate x_i values are not allowed, got x's {xs}")
    return pts


def lagrange(points: Sequence[Tuple]) -> UPoly:
    """The Lagrange-basis interpolating polynomial through ``points`` over ℚ.

    ``P(x) = Σ_i y_i · L_i(x)`` where ``L_i(x) = Π_{j≠i} (x - x_j) / (x_i - x_j)`` — built by
    forming each numerator polynomial ``Π_{j≠i} (x - x_j)`` with the exact ring ``mul``, dividing by
    the scalar denominator ``Π_{j≠i} (x_i - x_j)``, and summing with the exact ring ``add``. Raises
    ``ValueError`` on an empty or duplicate-x_i input (the same message as :func:`newton`).
    """
    D = QRing()
    pts = _validate_points(points, D)
    n = len(pts)
    xs = [x for x, _ in pts]
    ys = [y for _, y in pts]

    result = UPoly([D.zero()], D)
    for i in range(n):
        numer = UPoly([D.one()], D)                  # running Π_{j≠i} (x - x_j)
        denom = D.one()                               # running Π_{j≠i} (x_i - x_j)
        for j in range(n):
            if j == i:
                continue
            numer = mul(numer, UPoly([D.neg(xs[j]), D.one()], D))   # ×(x - x_j)
            denom = D.mul(denom, D.add(xs[i], D.neg(xs[j])))         # ×(x_i - x_j)
        coeff = D.div(ys[i], denom)                   # y_i / Π (x_i - x_j)  — denom ≠ 0: x_i distinct
        result = add(result, mul(UPoly([coeff], D), numer))
    return result


def newton(points: Sequence[Tuple]) -> UPoly:
    """The Newton divided-difference interpolating polynomial through ``points`` over ℚ.

    Builds the divided-difference table ``f[x_i], f[x_i,x_{i+1}], …`` and assembles
    ``P(x) = Σ_k c_k · Π_{i<k} (x - x_i)`` with ``c_k = f[x_0,…,x_k]``, using the exact ring ``add``/
    ``mul`` throughout (never evaluating the running product except symbolically). Raises
    ``ValueError`` on an empty or duplicate-x_i input (the same message as :func:`lagrange`).
    """
    D = QRing()
    pts = _validate_points(points, D)
    n = len(pts)
    xs = [x for x, _ in pts]
    ys = [y for _, y in pts]

    # table[k][i] = f[x_i, x_{i+1}, ..., x_{i+k}]; only the leading diagonal table[k][0] is needed.
    table = [list(ys)]
    for k in range(1, n):
        prev = table[k - 1]
        cur = []
        for i in range(n - k):
            num = D.add(prev[i + 1], D.neg(prev[i]))
            den = D.add(xs[i + k], D.neg(xs[i]))       # ≠ 0: x_i distinct (checked above)
            cur.append(D.div(num, den))
        table.append(cur)
    coeffs = [table[k][0] for k in range(n)]

    result = UPoly([D.zero()], D)
    running_product = UPoly([D.one()], D)              # Π_{i<k} (x - x_i), starts as the empty product 1
    for k in range(n):
        result = add(result, mul(UPoly([coeffs[k]], D), running_product))
        if k < n - 1:
            running_product = mul(running_product, UPoly([D.neg(xs[k]), D.one()], D))
    return result


__all__ = ["lagrange", "newton"]
