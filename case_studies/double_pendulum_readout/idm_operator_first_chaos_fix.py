"""
IDM re-read of the "no chaos seen" result -- operator-first fix, not empirical hunting.

The problem with the previous run, seen through information-discrete-math:

"Sensitivity to initial conditions" (a positive Lyapunov exponent) is normally DEFINED as
a continuum limit: lambda = lim_{t->inf} lim_{eps->0} (1/t) ln(|delta(t)|/|delta(0)|). That
definition needs I2 (t->inf) AND a limit that "lands" (I1) -- it is a non-readout in its
idealized form. Chasing it by empirically trying different initial conditions until
something "looks chaotic" is chasing that non-readout indirectly (trial-and-error toward an
asymptotic property), which is exactly the kind of blind search the operator-first
discipline warns against ("Operator-first: information is the central axis... put the
operator early").

The IDM-honest fix: a discrete step map F: state -> state (the bounded Verlet step, already
built) HAS a well-defined, fully FINITE local linearization at any given state -- its
one-step Jacobian J = DF(state), an 8x8 matrix computable by finite differences (a genuinely
finite operation, not a limit: h is a fixed, declared, small rational/float, not sent to
zero). The eigenvector of J's dominant |eigenvalue| IS the locally-expanding direction --
not asymptotic, not a limit, a real number you can compute right now from the operator
itself. Perturbing along THAT direction (found by power iteration -- itself a finite
discrete iterative process, not a continuum limit either: iterate a fixed integer number of
times and stop, per IDM's own discrete-ladder discipline) tests the map's actual local
expansion structure directly, instead of hoping a random direction eventually rotates into
alignment with it.

This is the fix: compute the operator, don't grope for it.
"""
from __future__ import annotations

import math

import exact_q_double_pendulum as base
import exact_q_bounded_double_pendulum as bq


# ---------------------------------------------------------------------------
# A reusable single-step float map: state (8-vector) -> state (8-vector)
# state = (r1x, r1y, v1x, v1y, r2x, r2y, v2x, v2y)
# ---------------------------------------------------------------------------
M1F, M2F, GF, KF, TAUF = 1.0, 1.0, 9.81, 20000.0, 1.0 / 4000.0
L1SQF, L2SQF = 1.0, 1.0


def step_map(state):
    r1 = (state[0], state[1]); v1 = (state[2], state[3])
    r2 = (state[4], state[5]); v2 = (state[6], state[7])
    r0 = (0.0, 0.0)
    f1, f2 = base.forces_f(r0, r1, r2, M1F, M2F, GF, KF, L1SQF, L2SQF)
    a1 = (f1[0] / M1F, f1[1] / M1F)
    a2 = (f2[0] / M2F, f2[1] / M2F)
    r1n = (r1[0] + v1[0] * TAUF + 0.5 * a1[0] * TAUF ** 2,
           r1[1] + v1[1] * TAUF + 0.5 * a1[1] * TAUF ** 2)
    r2n = (r2[0] + v2[0] * TAUF + 0.5 * a2[0] * TAUF ** 2,
           r2[1] + v2[1] * TAUF + 0.5 * a2[1] * TAUF ** 2)
    f1n, f2n = base.forces_f(r0, r1n, r2n, M1F, M2F, GF, KF, L1SQF, L2SQF)
    a1n = (f1n[0] / M1F, f1n[1] / M1F)
    a2n = (f2n[0] / M2F, f2n[1] / M2F)
    v1n = (v1[0] + 0.5 * (a1[0] + a1n[0]) * TAUF, v1[1] + 0.5 * (a1[1] + a1n[1]) * TAUF)
    v2n = (v2[0] + 0.5 * (a2[0] + a2n[0]) * TAUF, v2[1] + 0.5 * (a2[1] + a2n[1]) * TAUF)
    return [r1n[0], r1n[1], v1n[0], v1n[1], r2n[0], r2n[1], v2n[0], v2n[1]]


def run_n(state, n):
    for _ in range(n):
        state = step_map(state)
    return state


def initial_state_vec(perturb_bob2=False):
    r0, r1, v1, r2, v2 = base.make_initial_state_f(perturb_bob2)
    return [r1[0], r1[1], v1[0], v1[1], r2[0], r2[1], v2[0], v2[1]]


# ---------------------------------------------------------------------------
# Finite-difference Jacobian of ONE step_map application at a given state
# (h is a fixed, declared, finite constant -- never sent to zero)
# ---------------------------------------------------------------------------
def jacobian(state, h=1e-6):
    n = len(state)
    J = [[0.0] * n for _ in range(n)]
    for j in range(n):
        sp = list(state); sp[j] += h
        sm = list(state); sm[j] -= h
        fp = step_map(sp)
        fm = step_map(sm)
        for i in range(n):
            J[i][j] = (fp[i] - fm[i]) / (2 * h)
    return J


def mat_vec(J, v):
    return [sum(J[i][j] * v[j] for j in range(len(v))) for i in range(len(J))]


def norm(v):
    return math.sqrt(sum(x * x for x in v))


def power_iteration(J, iters=200, seed=None):
    """Finite, declared number of iterations -- not a limit. Returns (dominant
    eigenvector estimate, its Rayleigh-quotient eigenvalue estimate)."""
    n = len(J)
    v = seed or [1.0] * n
    v = [x / norm(v) for x in v]
    for _ in range(iters):
        w = mat_vec(J, v)
        wn = norm(w)
        if wn == 0:
            break
        v = [x / wn for x in w]
    Jv = mat_vec(J, v)
    eigval_rayleigh = sum(a * b for a, b in zip(v, Jv))
    return v, eigval_rayleigh


if __name__ == "__main__":
    BURN_IN = 500
    print("=" * 78)
    print(f"Step 1: burn in {BURN_IN} steps from the base IC (move off the special")
    print("        symmetric starting configuration before probing the local operator)")
    print("=" * 78)
    state0 = initial_state_vec(perturb_bob2=False)
    state_burned = run_n(state0, BURN_IN)
    print(f"  state after burn-in: r1=({state_burned[0]:+.6f},{state_burned[1]:+.6f})  "
          f"r2=({state_burned[4]:+.6f},{state_burned[5]:+.6f})")

    print()
    print("=" * 78)
    print("Step 2: compute the ONE-STEP JACOBIAN of the discrete map at this state")
    print("        (finite differences, h=1e-6, a fixed declared constant)")
    print("=" * 78)
    J = jacobian(state_burned, h=1e-6)

    print()
    print("=" * 78)
    print("Step 3: power iteration (200 fixed iterations) for the dominant")
    print("        |eigenvalue| direction of J -- the LOCALLY fastest-expanding")
    print("        perturbation direction, computed directly, not guessed")
    print("=" * 78)
    v_dom, eigval = power_iteration(J, iters=200)
    print(f"  dominant eigenvalue estimate (per-step growth factor): {eigval:.6f}")
    print(f"  (>1 means THIS state locally expands perturbations along this "
          f"direction every step;")
    print(f"   <1 means it locally contracts -- exactly what the earlier arbitrary")
    print(f"   +x-only perturbation direction apparently hit)")
    print(f"  dominant eigenvector: {[f'{x:+.4f}' for x in v_dom]}")
    print(f"    (order: r1x,r1y,v1x,v1y,r2x,r2y,v2x,v2y)")

    print()
    print("=" * 78)
    print("Step 4: perturb the burned-in state along the DOMINANT direction (not +x),")
    print("        magnitude 1e-7 as before, run bounded-exact-Q forward, measure")
    print("        separation -- this is the operator-informed test, not a guess")
    print("=" * 78)
    eps = 1e-7
    state_a = state_burned
    state_b = [s + eps * d for s, d in zip(state_burned, v_dom)]

    def to_bq_parts(state):
        r1 = (bq.base.Fr(state[0]).limit_denominator(10**12), bq.base.Fr(state[1]).limit_denominator(10**12))
        v1 = (bq.base.Fr(state[2]).limit_denominator(10**12), bq.base.Fr(state[3]).limit_denominator(10**12))
        r2 = (bq.base.Fr(state[4]).limit_denominator(10**12), bq.base.Fr(state[5]).limit_denominator(10**12))
        v2 = (bq.base.Fr(state[6]).limit_denominator(10**12), bq.base.Fr(state[7]).limit_denominator(10**12))
        return r1, v1, r2, v2

    r0 = (bq.base.Fr(0), bq.base.Fr(0))
    r1a, v1a, r2a, v2a = to_bq_parts(state_a)
    r1b, v1b, r2b, v2b = to_bq_parts(state_b)

    N_FORWARD = 2000
    LOG_EVERY = 100
    print(f"  running {N_FORWARD} bounded-exact-Q steps from the perturbed pair...")
    for n in range(N_FORWARD):
        r1a, v1a, r2a, v2a = bq.velocity_verlet_step_bounded(r1a, v1a, r2a, v2a, r0)
        r1b, v1b, r2b, v2b = bq.velocity_verlet_step_bounded(r1b, v1b, r2b, v2b, r0)
        if n % LOG_EVERY == 0 or n == N_FORWARD - 1:
            dx2 = float(r2a[0]) - float(r2b[0])
            dy2 = float(r2a[1]) - float(r2b[1])
            sep = math.sqrt(dx2 ** 2 + dy2 ** 2)
            ratio = sep / eps
            print(f"    n={n:4d}  separation={sep:.4e}  (ratio to initial eps: {ratio:8.3f}x)")
