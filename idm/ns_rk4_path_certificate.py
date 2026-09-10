"""Certified continuous-time enclosure for finite Fourier node tapes.

Each recorded float is treated as its exact IEEE-754 dyadic rational. Nodes are
then Leray-projected exactly and joined by a continuous piecewise-linear path.
For the unforced periodic incompressible Navier-Stokes equation, the residual
on each time cell is a degree-two polynomial in normalized cell time, so its
homogeneous H^-1 squared norm integrates exactly in Fraction arithmetic.

This is a finite path certificate. Combining the resulting A/B summaries with
the standard relative-energy theorem is an analytic (Dr-tier) continuum step.
No global regularity or DNS-adequacy claim is made.
"""
from __future__ import annotations

import math
from fractions import Fraction
from typing import Mapping, Sequence

Mode = tuple[int, int, int]
Vec = tuple[complex, complex, complex]
State = Mapping[Mode, Vec]
QComplex = tuple[Fraction, Fraction]
QVec = tuple[QComplex, QComplex, QComplex]

F = Fraction
ZERO: QComplex = (F(0), F(0))


def _qreal(x) -> Fraction:
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return F(x)
    if isinstance(x, float):
        if not math.isfinite(x):
            raise ValueError("all numeric inputs must be finite")
        return F.from_float(x)
    return F(x)


def _qc(z) -> QComplex:
    z = complex(z)
    if not math.isfinite(z.real) or not math.isfinite(z.imag):
        raise ValueError("state contains a non-finite complex component")
    return (F.from_float(float(z.real)), F.from_float(float(z.imag)))


def _cadd(a: QComplex, b: QComplex) -> QComplex:
    return (a[0] + b[0], a[1] + b[1])


def _csub(a: QComplex, b: QComplex) -> QComplex:
    return (a[0] - b[0], a[1] - b[1])


def _cscale(q: Fraction, a: QComplex) -> QComplex:
    return (q * a[0], q * a[1])


def _cmul(a: QComplex, b: QComplex) -> QComplex:
    return (a[0] * b[0] - a[1] * b[1],
            a[0] * b[1] + a[1] * b[0])


def _ci(a: QComplex) -> QComplex:
    return (-a[1], a[0])


def _re_a_conj_b(a: QComplex, b: QComplex) -> Fraction:
    return a[0] * b[0] + a[1] * b[1]


def _vadd(a: QVec, b: QVec) -> QVec:
    return tuple(_cadd(x, y) for x, y in zip(a, b))  # type: ignore[return-value]


def _zero_vec() -> QVec:
    return (ZERO, ZERO, ZERO)


def _project_exact(v: QVec, k: Mode) -> QVec:
    k2 = sum(x * x for x in k)
    if k2 == 0:
        raise ValueError("zero Fourier mode is not supported by this homogeneous H^-1 certificate")
    dot = ZERO
    for ki, zi in zip(k, v):
        dot = _cadd(dot, _cscale(F(ki), zi))
    return tuple(
        _csub(zi, _cscale(F(ki, k2), dot))
        for ki, zi in zip(k, v)
    )  # type: ignore[return-value]


def _validate_mode(k) -> Mode:
    k = tuple(int(x) for x in k)
    if len(k) != 3 or k == (0, 0, 0):
        raise ValueError("modes must be nonzero integer triples")
    return k  # type: ignore[return-value]


def capture_projected_node(state: State, *, K: int) -> dict[Mode, QVec]:
    """Capture one floating state as exact dyadic rationals and project exactly."""
    K = int(K)
    if K < 1:
        raise ValueError("K must be at least 1")
    out: dict[Mode, QVec] = {}
    for raw_k, raw_v in state.items():
        k = _validate_mode(raw_k)
        if max(abs(x) for x in k) > K:
            raise ValueError("state contains a mode outside the declared K cube")
        if len(raw_v) != 3:
            raise ValueError("each Fourier coefficient needs 3 complex components")
        out[k] = _project_exact(tuple(_qc(z) for z in raw_v), k)  # type: ignore[arg-type]
    return out


def _complete_support(nodes: list[dict[Mode, QVec]]) -> tuple[list[dict[Mode, QVec]], tuple[Mode, ...]]:
    support = sorted(set().union(*(n.keys() for n in nodes)))
    z = _zero_vec()
    return [{k: node.get(k, z) for k in support} for node in nodes], tuple(support)


def _node_divergence_exact(node: Mapping[Mode, QVec]) -> bool:
    for k, row in node.items():
        s = ZERO
        for ki, zi in zip(k, row):
            s = _cadd(s, _cscale(F(ki), zi))
        if s != ZERO:
            return False
    return True


def _convective_polynomial(a: Mapping[Mode, QVec], b: Mapping[Mode, QVec]):
    d = {
        k: tuple(_csub(zb, za) for za, zb in zip(a[k], b[k]))
        for k in a
    }
    raw: dict[Mode, list[QVec]] = {}
    for p, ap in a.items():
        dp = d[p]
        for q, aq in a.items():
            dq = d[q]
            out = (p[0] + q[0], p[1] + q[1], p[2] + q[2])

            s0 = ZERO
            s1 = ZERO
            for qi, z0, z1 in zip(q, ap, dp):
                s0 = _cadd(s0, _cscale(F(qi), z0))
                s1 = _cadd(s1, _cscale(F(qi), z1))
            if s0 == ZERO and s1 == ZERO:
                continue

            c0 = tuple(_ci(_cmul(s0, z)) for z in aq)
            c1 = tuple(
                _ci(_cadd(_cmul(s0, dz), _cmul(s1, z)))
                for z, dz in zip(aq, dq)
            )
            c2 = tuple(_ci(_cmul(s1, dz)) for dz in dq)

            coeffs = raw.setdefault(out, [_zero_vec(), _zero_vec(), _zero_vec()])
            coeffs[0] = _vadd(coeffs[0], c0)  # type: ignore[arg-type]
            coeffs[1] = _vadd(coeffs[1], c1)  # type: ignore[arg-type]
            coeffs[2] = _vadd(coeffs[2], c2)  # type: ignore[arg-type]

    mean = raw.pop((0, 0, 0), [_zero_vec(), _zero_vec(), _zero_vec()])
    mean_zero = all(z == ZERO for vec in mean for z in vec)
    projected = {
        k: [_project_exact(vec, k) for vec in coeffs]
        for k, coeffs in raw.items()
    }
    return projected, mean_zero


def _residual_polynomial(a: Mapping[Mode, QVec], b: Mapping[Mode, QVec],
                         *, h: Fraction, nu: Fraction):
    d = {
        k: tuple(_csub(zb, za) for za, zb in zip(a[k], b[k]))
        for k in a
    }
    conv, mean_zero = _convective_polynomial(a, b)
    residual: dict[Mode, list[QVec]] = {}
    for k in set(conv) | set(a):
        coeffs = list(conv.get(k, [_zero_vec(), _zero_vec(), _zero_vec()]))
        if k in a:
            k2 = sum(x * x for x in k)
            deriv = tuple(_cscale(F(1) / h, z) for z in d[k])
            visc0 = tuple(_cscale(nu * k2, z) for z in a[k])
            visc1 = tuple(_cscale(nu * k2, z) for z in d[k])
            coeffs[0] = _vadd(coeffs[0], _vadd(deriv, visc0))  # type: ignore[arg-type]
            coeffs[1] = _vadd(coeffs[1], visc1)  # type: ignore[arg-type]
        residual[k] = coeffs
    return residual, mean_zero


def _integrate_hminus1_squared(residual: Mapping[Mode, list[QVec]],
                               *, h: Fraction) -> Fraction:
    total = F(0)
    for k, coeffs in residual.items():
        k2 = sum(x * x for x in k)
        for comp in range(3):
            c = [coeffs[j][comp] for j in range(3)]
            for a in range(3):
                for b in range(3):
                    total += h * _re_a_conj_b(c[a], c[b]) / F(k2 * (a + b + 1))
    if total < 0:
        raise ArithmeticError("exact H^-1 squared residual integral became negative")
    return total


def _integrate_grad_linf_majorant(a: Mapping[Mode, QVec],
                                  b: Mapping[Mode, QVec],
                                  *, h: Fraction) -> Fraction:
    """Upper-bound int ||grad v||_infinity via a coefficientwise l1 majorant."""
    total = F(0)
    for k in a:
        k_l1 = sum(abs(x) for x in k)
        for za, zb in zip(a[k], b[k]):
            ea = abs(za[0]) + abs(za[1])
            eb = abs(zb[0]) + abs(zb[1])
            total += F(k_l1) * h * (ea + eb) / 2
    return total


def exp_upper_rational(x: Fraction, *, min_terms: int = 24) -> Fraction:
    """Exact rational upper bound for exp(x), x>=0, by Taylor+geometric tail."""
    x = _qreal(x)
    if x < 0:
        raise ValueError("x must be nonnegative")
    N = max(int(min_terms), math.ceil(float(x)) + 2)
    term = F(1)
    partial = term
    for n in range(1, N + 1):
        term = term * x / n
        partial += term
    next_term = term * x / (N + 1)
    q = x / (N + 2)
    if q >= 1:
        raise ArithmeticError("failed to obtain a convergent exponential tail majorant")
    return partial + next_term / (1 - q)


def sqrt_upper_decimal_rational(x: Fraction, *, digits: int = 18) -> Fraction:
    """Ceiling of sqrt(x) on a decimal grid, using integer arithmetic only."""
    x = _qreal(x)
    if x < 0:
        raise ValueError("x must be nonnegative")
    if x == 0:
        return F(0)
    if digits < 0:
        raise ValueError("digits must be nonnegative")
    D = 10 ** digits
    n = x.numerator * D * D
    q = x.denominator
    root_floor = math.isqrt(n // q)
    root_ceil = root_floor if root_floor * root_floor * q == n else root_floor + 1
    return F(root_ceil, D)


def certify_piecewise_linear_fourier_tape(
    tape: Sequence[State],
    *,
    K: int,
    dt,
    nu,
    initial_l2_error_upper=0.0,
    beta_decimal_digits: int = 18,
) -> dict:
    """Certify A/B summaries and a relative-energy terminal beta for a node tape.

    The finite quantities Abar, Bbar and exp(Abar) are certified by exact
    rational arithmetic. The transfer from this comparison-path residual to a
    Leray-Hopf solution is the standard analytic relative-energy theorem and is
    intentionally reported as a separate scope statement.
    """
    if len(tape) < 2:
        raise ValueError("tape must contain at least two nodes")
    K = int(K)
    h = _qreal(dt)
    viscosity = _qreal(nu)
    e0 = _qreal(initial_l2_error_upper)
    if K < 1 or h <= 0 or viscosity <= 0 or e0 < 0:
        raise ValueError("require K>=1, dt>0, nu>0, initial error>=0")

    nodes = [capture_projected_node(state, K=K) for state in tape]
    nodes, support = _complete_support(nodes)
    divergence_ok = all(_node_divergence_exact(n) for n in nodes)

    B = F(0)
    G = F(0)
    mean_zero = True
    for a, b in zip(nodes[:-1], nodes[1:]):
        residual, cell_mean_zero = _residual_polynomial(a, b, h=h, nu=viscosity)
        mean_zero = mean_zero and cell_mean_zero
        B += _integrate_hminus1_squared(residual, h=h)
        G += _integrate_grad_linf_majorant(a, b, h=h)

    A = 2 * G
    expA = exp_upper_rational(A)
    beta_sq = expA * (e0 * e0 + B / viscosity)
    beta = sqrt_upper_decimal_rational(beta_sq, digits=beta_decimal_digits)

    status = "CERTIFIED_SUMMARIES" if divergence_ok and mean_zero else "HOLD"
    reason = None if status == "CERTIFIED_SUMMARIES" else (
        "exact projected path failed divergence/zero-mean residual precondition"
    )
    return {
        "status": status,
        "tier": "finite_diagnostic",
        "reason": reason,
        "K": K,
        "nodes": len(nodes),
        "cells": len(nodes) - 1,
        "support_modes": len(support),
        "exact_divergence_free_nodes": divergence_ok,
        "exact_zero_mean_residual": mean_zero,
        "A_upper": float(A),
        "B_hminus1_squared_time_integral_upper": float(B),
        "exp_A_upper": float(expA),
        "terminal_l2_error_squared_upper": float(beta_sq),
        "terminal_l2_beta_upper": float(beta),
        "exact": {
            "A_upper": str(A),
            "B_upper": str(B),
            "exp_A_upper": str(expA),
            "terminal_l2_error_squared_upper": str(beta_sq),
            "terminal_l2_beta_decimal_upper": str(beta),
        },
        "scope": (
            "finite exact-dyadic piecewise-linear comparison-path certificate; "
            "continuum transfer requires the standard relative-energy theorem"
        ),
    }
