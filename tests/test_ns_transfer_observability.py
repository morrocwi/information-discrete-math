import itertools
import math

from idm.ns_transfer_observability import (
    boundary_old_triad_witness,
    integrated_shell_transfer,
    integrated_shell_transfer_radius,
    shell_transfer_from_jet,
    triad_reduced_r_estimate,
    triad_reduced_r_radius,
)


def test_transfer_from_shell_jet_and_conservation_example():
    I = (1.0, 2.0, 3.0)
    s = (1, 2, 3)
    nu = 0.01
    T = (0.25, -0.10, -0.15)
    dI = tuple(Ti - 2 * nu * si * Ii for Ti, si, Ii in zip(T, s, I))
    got = shell_transfer_from_jet(
        I, dI, viscosity=nu, shell_squared_radii=s
    )
    assert all(math.isclose(a, b, abs_tol=1e-15) for a, b in zip(got, T))
    assert math.isclose(sum(got), 0.0, abs_tol=1e-15)


def test_integrated_balance_and_radius():
    got = integrated_shell_transfer(
        (1.0,), (0.9,), (0.95,), viscosity=0.1, shell_squared_radii=(2,)
    )
    assert math.isclose(got[0], 0.28, abs_tol=1e-15)

    rad = integrated_shell_transfer_radius(
        (0.01,), (0.02,), (0.03,), viscosity=0.1, shell_squared_radii=(2,)
    )
    assert math.isclose(rad[0], 0.042, abs_tol=1e-15)


def test_triad_quantitative_inverse_radius():
    nu = 1 / 200
    x = 1.0
    r = 1.0
    ca = 3 / 10
    j = 2 * ca * r - 2 * nu * x
    dx = 1 / 1000
    dj = -1 / 2000

    r_hat = triad_reduced_r_estimate(
        shell_energy_x=x + dx,
        shell_energy_derivative_a=j + dj,
        viscosity=nu,
    )
    bound = triad_reduced_r_radius(
        shell_energy_x_radius=abs(dx),
        shell_energy_derivative_a_radius=abs(dj),
        viscosity=nu,
    )
    assert abs(r_hat - r) <= bound + 1e-15
    assert math.isclose(bound, 17 / 20000, rel_tol=0.0, abs_tol=1e-15)


def test_constructive_boundary_triad_witness_through_N8():
    for N in range(2, 9):
        for k in itertools.product(range(-N, N + 1), repeat=3):
            if k == (0, 0, 0) or max(abs(v) for v in k) != N:
                continue
            p, q = boundary_old_triad_witness(k, N)
            assert max(abs(v) for v in p) <= N - 1
            assert max(abs(v) for v in q) <= N
