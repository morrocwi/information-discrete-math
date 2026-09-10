"""Rigorous spectral tail certificates for Navier--Stokes readouts.

This module closes a nontrivial part of Toledo target PROP-EPSC-04 without
claiming the 3-D Navier--Stokes Millennium problem.

The key distinction is the target norm.

1. Terminal/full-state completion from finite Fourier records alone is
   non-identifiable without additional regularity or budget information.
2. For Leray--Hopf solutions on the 2*pi-periodic torus, viscosity plus the
   energy inequality gives an unconditional computable tail certificate in
   the spacetime norm L2(0,T;L2_x).
3. A terminal-time certificate is available conditionally from any verified
   H^s bound at that time.

Fourier normalization used here:
    ||u||_L2^2 = sum_k |u_hat_k|^2,
    ||grad u||_L2^2 = sum_k |k|^2 |u_hat_k|^2.
The current IDM Navier--Stokes mode recurrence uses the same kappa0=1
normalization.  For a different periodic box, pass the physical fundamental
wavenumber kappa0.

Claim tiers:
- finite helper algebra: exact/finite_diagnostic;
- Leray spacetime estimate: standard analytic derivation (Dr until a separate
  formal proof is registered);
- arbitrary terminal 3-D completion: OPEN unless a pointwise H^s bound is
  separately certified.
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


def omitted_wavenumber_floor(K: int, *, kappa0: float = 1.0) -> float:
    """Smallest Euclidean wavenumber outside the cube ||k||_inf <= K.

    Every omitted integer mode has at least one coordinate of magnitude K+1,
    hence |k|_2 >= K+1.  Multiplying by kappa0 handles a physical periodic box.
    """
    K = int(K)
    if K < 0:
        raise ValueError("K must be nonnegative")
    kappa0 = _positive("kappa0", kappa0)
    return kappa0 * (K + 1)


def conditional_hs_tail_beta(
    *,
    K: int,
    hs_norm_bound: float,
    s: float = 1.0,
    kappa0: float = 1.0,
) -> float:
    """Conditional terminal L2-tail certificate from a verified H^s seminorm.

    If || |nabla|^s u(T) ||_2 <= M_s, then

        ||(I-P_K)u(T)||_2 <= M_s / kappa_{K+1}^s.

    This is rigorous once ``hs_norm_bound`` is itself a proved/certified bound.
    It does not supply that 3-D pointwise regularity bound.
    """
    M = _nonnegative("hs_norm_bound", hs_norm_bound)
    s = _positive("s", s)
    kmin = omitted_wavenumber_floor(K, kappa0=kappa0)
    return M / (kmin ** s)


def leray_unforced_spacetime_tail_beta(
    *,
    K: int,
    nu: float,
    initial_l2_norm: float,
    kappa0: float = 1.0,
) -> float:
    """Unforced Leray--Hopf L2_t L2_x tail certificate.

    For a Leray--Hopf solution of unforced incompressible Navier--Stokes,

      1/2 ||u(t)||_2^2 + nu int_0^t ||grad u||_2^2 ds
          <= 1/2 ||u_0||_2^2.

    Since all modes outside ||k||_inf<=K satisfy |k|>=kappa_{K+1},

      ||(I-P_K)u||_{L2(0,T;L2)}
          <= ||u_0||_2 / (sqrt(2 nu) kappa_{K+1}).

    The right-hand side is finite, computable from declared input data, and
    tends to zero like 1/K.  It does not control a prescribed terminal time.
    """
    nu = _positive("nu", nu)
    u0 = _nonnegative("initial_l2_norm", initial_l2_norm)
    kmin = omitted_wavenumber_floor(K, kappa0=kappa0)
    return u0 / (math.sqrt(2.0 * nu) * kmin)


def leray_forced_spacetime_tail_beta(
    *,
    K: int,
    nu: float,
    initial_l2_norm: float,
    forcing_l2_hminus1_norm: float,
    kappa0: float = 1.0,
) -> float:
    """Forced Leray--Hopf L2_t L2_x tail certificate.

    Assume f in L2(0,T;H^{-1}) and write F=||f||_{L2_t H^{-1}}.  Young's
    inequality in the energy inequality yields

      int_0^T ||grad u||_2^2 dt
          <= ||u_0||_2^2/nu + F^2/nu^2.

    Therefore

      ||(I-P_K)u||_{L2_t L2_x}
          <= (1/kappa_{K+1})
             sqrt(||u_0||_2^2/nu + F^2/nu^2).

    This deliberately uses a slightly weaker bound than the unforced formula
    so the assumptions are explicit and fail-closed.
    """
    nu = _positive("nu", nu)
    u0 = _nonnegative("initial_l2_norm", initial_l2_norm)
    F = _nonnegative("forcing_l2_hminus1_norm", forcing_l2_hminus1_norm)
    kmin = omitted_wavenumber_floor(K, kappa0=kappa0)
    return math.sqrt((u0 * u0) / nu + (F * F) / (nu * nu)) / kmin


def time_average_tail_beta(*, spacetime_beta: float, duration: float) -> float:
    """Lift an L2_t L2_x certificate to a time-averaged-field L2 certificate.

    For ubar = (1/T) int_0^T u(t) dt,

      ||(I-P_K)ubar||_2 <= spacetime_beta / sqrt(T)

    by Cauchy--Schwarz.
    """
    beta = _nonnegative("spacetime_beta", spacetime_beta)
    T = _positive("duration", duration)
    return beta / math.sqrt(T)


def lipschitz_readout_tail_beta(
    *,
    state_beta: float,
    lipschitz_constant: float,
) -> float:
    """Push a certified state-space tail bound through a Lipschitz readout."""
    beta = _nonnegative("state_beta", state_beta)
    L = _nonnegative("lipschitz_constant", lipschitz_constant)
    return L * beta


def finite_spectral_tail_and_hs(
    state: State,
    *,
    K: int,
    s: float = 1.0,
    kappa0: float = 1.0,
) -> dict:
    """Finite checker for the spectral inequality used by the analytic proof.

    ``state`` may contain modes beyond K.  The function computes the actual
    finite tail and the finite H^s seminorm, then reports the theorem-side
    bound M_s/kappa_{K+1}^s.  This is a finite diagnostic of the algebraic core,
    not a replacement for the Leray energy inequality.
    """
    s = _positive("s", s)
    kappa0 = _positive("kappa0", kappa0)
    kmin = omitted_wavenumber_floor(K, kappa0=kappa0)
    tail_sq = 0.0
    hs_sq = 0.0
    for k, v in state.items():
        if len(k) != 3 or len(v) != 3:
            raise ValueError("state must map 3-D integer modes to 3-vectors")
        amp_sq = sum(abs(z) ** 2 for z in v)
        k_euclid = kappa0 * math.sqrt(sum(int(x) * int(x) for x in k))
        hs_sq += (k_euclid ** (2.0 * s)) * amp_sq
        if max(abs(int(x)) for x in k) > int(K):
            tail_sq += amp_sq
    actual = math.sqrt(tail_sq)
    hs = math.sqrt(hs_sq)
    bound = hs / (kmin ** s)
    return {
        "actual_tail_l2": actual,
        "hs_seminorm": hs,
        "bound": bound,
        "passes": actual <= bound + 1e-14 * max(1.0, actual, bound),
        "tier": "finite_diagnostic",
    }


def terminal_nonidentifiability_witness(*, K: int, amplitude: float = 1.0) -> dict:
    """Construct the elementary high-mode witness behind the terminal no-go.

    The retained record P_K is unchanged by adding a conjugate pair at
    q=(K+1,0,0) with velocity perpendicular to q.  The tail amplitude can be
    scaled arbitrarily.  Therefore finite retained coefficients alone cannot
    provide a universal terminal-tail beta_K over an unrestricted L2 class.
    """
    K = int(K)
    if K < 0:
        raise ValueError("K must be nonnegative")
    A = _nonnegative("amplitude", amplitude)
    q = (K + 1, 0, 0)
    uq: Vec = (0j, complex(A), 0j)
    umq: Vec = (0j, complex(A), 0j)
    coefficient_tail_l2 = math.sqrt(2.0) * A
    return {
        "K": K,
        "q": q,
        "minus_q": (-q[0], -q[1], -q[2]),
        "u_hat_q": uq,
        "u_hat_minus_q": umq,
        "divergence_free": True,
        "retained_projection_change_l2": 0.0,
        "coefficient_tail_l2": coefficient_tail_l2,
        "claim": (
            "finite terminal Fourier records do not identify the omitted tail "
            "without an additional admissible-class bound"
        ),
    }
