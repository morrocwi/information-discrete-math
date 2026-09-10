"""Relative-energy adapter from a finite Fourier path to a Leray-Hopf solution.

This module supplies the analytic form of the bridge isolated as PROP-EPSC-12.
It does NOT certify a raw RK4 tape by itself.  It consumes certified upper
bounds on two finite-path quantities:

    A = 2 * int_0^T ||grad v(t)||_infinity dt
    B = int_0^T ||r(t)||_{H^{-1}}^2 dt

where the smooth divergence-free comparison path v satisfies

    v_t + P[(v.grad)v] - nu Delta v = P f + r.

For any Leray-Hopf solution u of the same forced problem, the standard relative
energy inequality gives

    ||u(T)-v(T)||_2^2
      <= exp(A) * ( ||u0-v(0)||_2^2 + B/nu ).

If v(T) is supported in the retained Fourier cube, this is immediately also an
upper bound on ||(I-P_K)u(T)||_2.

Thus the *mathematical adapter theorem* is finite/computable once A and B are
certified.  What remains for a concrete numerical RK4 run is to construct a
continuous-time interpolation and rigorously bound A and B over every time
cell.  That numerical enclosure step remains fail-closed.

Claim tier: Dr (standard relative-energy / weak-strong-stability argument),
until separately formalised.  No global regularity, uniqueness, or Clay claim.
"""
from __future__ import annotations

import math
from typing import Mapping

Mode = tuple[int, int, int]
Vec = tuple[complex, complex, complex]
State = Mapping[Mode, Vec]


def _nonnegative(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return value


def _positive(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def _vnorm2(v: Vec) -> float:
    return float(sum(abs(z) ** 2 for z in v))


def _project(v: Vec, k: Mode) -> Vec:
    k2 = float(sum(x * x for x in k))
    if k2 == 0.0:
        return v
    dot = sum(k[i] * v[i] for i in range(3))
    return tuple(v[i] - k[i] * dot / k2 for i in range(3))  # type: ignore[return-value]


def relative_energy_adapter_bounds(
    *,
    nu: float,
    initial_l2_error_upper: float,
    grad_linf_time_integral_upper: float,
    residual_hminus1_l2_squared_integral_upper: float,
) -> dict:
    """Certified-summary relative-energy bounds.

    Parameters are directional upper bounds.  Define

        A = 2 int ||grad v||_inf,
        B = int ||r||_{H^-1}^2.

    Then

        E_inf^2 = exp(A) * (e0^2 + B/nu)

    bounds sup_t ||u-v||_2^2 on [0,T].  The same estimate at terminal time is
    ``terminal_l2_error_upper``.

    We also return a conservative integrated H1-error bound obtained from the
    absorbed relative-energy inequality:

        nu int ||grad(u-v)||_2^2
            <= e0^2 + A E_inf^2 + B/nu.
    """
    nu = _positive("nu", nu)
    e0 = _nonnegative("initial_l2_error_upper", initial_l2_error_upper)
    Gint = _nonnegative(
        "grad_linf_time_integral_upper", grad_linf_time_integral_upper
    )
    B = _nonnegative(
        "residual_hminus1_l2_squared_integral_upper",
        residual_hminus1_l2_squared_integral_upper,
    )
    A = 2.0 * Gint
    # Fail rather than overflow silently; an unusably large exponential is not
    # a certificate the implementation should pretend to evaluate.
    if A > 700.0:
        return {
            "status": "HOLD",
            "tier": "conditional_certificate",
            "reason": "relative-energy exponential exceeds safe finite evaluation range",
            "A_upper": A,
            "B_upper": B,
        }

    e_inf_sq = math.exp(A) * (e0 * e0 + B / nu)
    e_inf = math.sqrt(e_inf_sq)
    grad_error_sq_integral = (e0 * e0 + A * e_inf_sq + B / nu) / nu

    return {
        "status": "CERTIFIED_BOUND",
        "tier": "conditional_certificate",
        "A_upper": A,
        "B_upper": B,
        "sup_l2_error_squared_upper": e_inf_sq,
        "sup_l2_error_upper": e_inf,
        "terminal_l2_error_upper": e_inf,
        "grad_error_l2_time_squared_upper": grad_error_sq_integral,
        "grad_error_l2_time_upper": math.sqrt(grad_error_sq_integral),
    }


def k_supported_terminal_tail_beta(*, adapter_result: Mapping) -> dict:
    """Turn a full L2 adapter error into a terminal omitted-tail certificate.

    If the comparison path v(T) is supported in P_K, then

        (I-P_K)u(T) = (I-P_K)(u(T)-v(T)),

    so the terminal Fourier tail is at most ||u(T)-v(T)||_2.
    """
    if adapter_result.get("status") != "CERTIFIED_BOUND":
        return {
            "status": "HOLD",
            "tier": "conditional_certificate",
            "beta": None,
            "reason": "adapter bound is not certified",
        }
    beta = _nonnegative(
        "terminal_l2_error_upper", float(adapter_result["terminal_l2_error_upper"])
    )
    return {
        "status": "CERTIFIED_BOUND",
        "tier": "conditional_certificate",
        "beta": beta,
        "reason": "comparison path terminal state is assumed P_K-supported",
    }


def retained_energy_tape_from_adapter(
    *,
    comparison_terminal_l2_norm: float,
    comparison_grad_l2_time_norm: float,
    adapter_result: Mapping,
) -> dict:
    """Directional continuum energy-tape bounds implied by an adapter result.

    If v is P_K-supported and E bounds ||u-v||_Linf_tL2, then

        ||P_K u(T)||_2 >= max(0, ||v(T)||_2 - E).

    If Z bounds ||grad(u-v)||_L2_t, then

        ||grad P_K u||_L2_t >= max(0, ||grad v||_L2_t - Z).

    The latter yields the retained viscous-dissipation lower bound after
    multiplying the squared norm by nu outside this helper.
    """
    vT = _nonnegative("comparison_terminal_l2_norm", comparison_terminal_l2_norm)
    vgrad = _nonnegative(
        "comparison_grad_l2_time_norm", comparison_grad_l2_time_norm
    )
    if adapter_result.get("status") != "CERTIFIED_BOUND":
        return {
            "status": "HOLD",
            "tier": "conditional_certificate",
            "reason": "adapter bound is not certified",
        }
    E = _nonnegative(
        "sup_l2_error_upper", float(adapter_result["sup_l2_error_upper"])
    )
    Z = _nonnegative(
        "grad_error_l2_time_upper",
        float(adapter_result["grad_error_l2_time_upper"]),
    )
    return {
        "status": "CERTIFIED_BOUND",
        "tier": "conditional_certificate",
        "retained_terminal_l2_norm_lower": max(0.0, vT - E),
        "retained_grad_l2_time_norm_lower": max(0.0, vgrad - Z),
    }


def fourier_grad_linf_upper(state: State, *, kappa0: float = 1.0) -> float:
    """Finite Fourier upper bound on ||grad v||_infinity at one time.

    Operator norm <= Frobenius norm <= sum_k |k| |v_hat_k|_2.
    This is conservative but uses only finite coefficient records.
    """
    kappa0 = _positive("kappa0", kappa0)
    total = 0.0
    for k, v in state.items():
        kmag = kappa0 * math.sqrt(sum(int(x) * int(x) for x in k))
        total += kmag * math.sqrt(_vnorm2(v))
    return total


def finite_galerkin_nonlinear_residual_hminus1(
    state: State,
    *,
    K: int,
    kappa0: float = 1.0,
) -> dict:
    """Snapshot H^-1 norm of the exact-Galerkin unresolved nonlinear residual.

    For a K-supported Fourier state v, the quadratic convective term has support
    inside the 2K cube.  The projected K-Galerkin ODE removes all output modes
    outside K.  Their Leray-projected convolution is exactly the semidiscrete
    residual r_K=(I-P_K)P[(v.grad)v] for the unforced exact Galerkin path.

    This function computes that finite snapshot residual.  A trajectory-level
    adapter still needs a certified upper bound on its time integral.
    """
    K = int(K)
    if K < 1:
        raise ValueError("K must be at least 1")
    kappa0 = _positive("kappa0", kappa0)
    support = {tuple(map(int, k)): v for k, v in state.items()}
    for k in support:
        if len(k) != 3 or max(abs(x) for x in k) > K:
            raise ValueError("state contains a mode outside the declared K cube")

    residual: dict[Mode, Vec] = {}
    keys = tuple(support)
    for p in keys:
        up = support[p]
        for q in keys:
            uq = support[q]
            out = (p[0] + q[0], p[1] + q[1], p[2] + q[2])
            if out == (0, 0, 0) or max(abs(x) for x in out) <= K:
                continue
            qdot = q[0] * up[0] + q[1] * up[1] + q[2] * up[2]
            term = (1j * qdot * uq[0], 1j * qdot * uq[1], 1j * qdot * uq[2])
            old = residual.get(out, (0j, 0j, 0j))
            residual[out] = (
                old[0] + term[0],
                old[1] + term[1],
                old[2] + term[2],
            )

    projected = {k: _project(v, k) for k, v in residual.items()}
    hminus1_sq = 0.0
    l2_sq = 0.0
    for k, v in projected.items():
        amp_sq = _vnorm2(v)
        k2 = (kappa0 * kappa0) * float(sum(x * x for x in k))
        l2_sq += amp_sq
        hminus1_sq += amp_sq / k2

    return {
        "K": K,
        "residual_modes": len(projected),
        "residual_l2_norm": math.sqrt(l2_sq),
        "residual_hminus1_norm": math.sqrt(hminus1_sq),
        "residual_hminus1_squared": hminus1_sq,
        "tier": "finite_diagnostic",
        "scope": "snapshot exact-Galerkin unresolved nonlinear residual",
    }
