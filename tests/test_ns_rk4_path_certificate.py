import math

from idm.ns_retained import cube_modes, full_rk4_step, triads_by_output
from idm.ns_rk4_path_certificate import certify_piecewise_linear_fourier_tape


def _zero_state(K=1):
    return {k: (0j, 0j, 0j) for k in cube_modes(K)}


def _shear_state(K=1, amplitude=1.0):
    state = _zero_state(K)
    state[(1, 0, 0)] = (0j, -0.5j * amplitude, 0j)
    state[(-1, 0, 0)] = (0j, 0.5j * amplitude, 0j)
    return state


def _taylor_green_state(K=1):
    state = _zero_state(K)
    for kx in (-1, 1):
        for ky in (-1, 1):
            for kz in (-1, 1):
                state[(kx, ky, kz)] = (-1j * kx / 8.0, 1j * ky / 8.0, 0j)
    return state


def _rk4_tape(state, *, K, dt, nu, steps):
    modes = cube_modes(K)
    triads = triads_by_output(modes)
    out = [dict(state)]
    u = dict(state)
    for _ in range(steps):
        u = full_rk4_step(u, dt, nu, modes, triads)
        out.append(dict(u))
    return out


def test_zero_solution_gives_zero_continuous_time_residual_certificate():
    state = _zero_state()
    result = certify_piecewise_linear_fourier_tape(
        [state, state], K=1, dt=0.01, nu=0.1
    )
    assert result["status"] == "CERTIFIED_SUMMARIES"
    assert result["A_upper"] == 0.0
    assert result["B_hminus1_squared_time_integral_upper"] == 0.0
    assert result["terminal_l2_beta_upper"] == 0.0


def test_shear_rk4_tape_certificate_dominates_known_terminal_error():
    K, dt, nu, steps = 1, 0.01, 0.1, 5
    tape = _rk4_tape(_shear_state(K), K=K, dt=dt, nu=nu, steps=steps)
    result = certify_piecewise_linear_fourier_tape(
        tape, K=K, dt=dt, nu=nu
    )
    assert result["status"] == "CERTIFIED_SUMMARIES"
    assert result["exact_divergence_free_nodes"] is True
    assert result["exact_zero_mean_residual"] is True

    exact_amp = math.exp(-nu * dt * steps)
    exact = _shear_state(K, exact_amp)
    err_sq = 0.0
    for k in exact:
        for i in range(3):
            err_sq += abs(tape[-1][k][i] - exact[k][i]) ** 2
    actual_terminal_error = math.sqrt(err_sq)
    assert actual_terminal_error <= result["terminal_l2_beta_upper"]


def test_taylor_green_rk4_tape_produces_finite_exact_ab_enclosure():
    K, dt, nu, steps = 1, 0.01, 0.01, 5
    tape = _rk4_tape(_taylor_green_state(K), K=K, dt=dt, nu=nu, steps=steps)
    result = certify_piecewise_linear_fourier_tape(
        tape, K=K, dt=dt, nu=nu
    )
    assert result["status"] == "CERTIFIED_SUMMARIES"
    assert result["exact_divergence_free_nodes"] is True
    assert result["exact_zero_mean_residual"] is True
    assert result["A_upper"] > 0.0
    assert result["B_hminus1_squared_time_integral_upper"] > 0.0
    assert math.isfinite(result["terminal_l2_beta_upper"])
    assert result["terminal_l2_beta_upper"] > 0.0
    # The exact evidence is serialized as rational strings, not recomputed floats.
    assert "/" in result["exact"]["A_upper"]
    assert "/" in result["exact"]["B_upper"]
