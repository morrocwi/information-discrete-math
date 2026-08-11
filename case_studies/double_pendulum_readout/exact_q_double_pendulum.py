"""
Exact-Q (rational, fractions.Fraction) vs floating-point double pendulum comparison.

Model: stiff-spring (penalty) Cartesian double pendulum -- an IDM-honest reformulation.
Two masses r1, r2 in the plane, connected to a fixed pivot r0
and to each other by quartic penalty springs that push |r-q|^2 toward a fixed rational
l^2, instead of a hard SHAKE constraint (SHAKE's Newton-solved Lagrange multiplier is
generically an ALGEBRAIC IRRATIONAL given rational inputs -- it would silently reintroduce
R. The penalty-spring form uses only +,-,*,/ by fixed rational constants, so it stays
CLOSED over Q forever -- this is the actual finding worth reporting, not assumed up front).

No sqrt, no trig, anywhere. Angles never appear -- positions are tracked directly in Q^2.
Initial conditions are placed using exact rational points on the unit "circle" via a
Pythagorean triple (3,4,5), so l^2 is satisfied EXACTLY at t=0 without ever computing sqrt
or cos/sin of anything.

Integrator: velocity Verlet (symplectic, second-order), run twice on IDENTICAL equations --
once with fractions.Fraction (exact Q arithmetic) and once with Python float (standard
double precision) -- to measure how much the two diverge from each other over time. This is
the direct, falsifiable test of the claim under scrutiny: floating point injects its
own rounding-scale divergence that is indistinguishable, from the outside, from real
chaotic divergence; exact-Q arithmetic has no such artifact (any divergence it shows is a
property of the equations themselves, not of the numeric representation).
"""
from __future__ import annotations

import time
from fractions import Fraction as Fr


# ---------------------------------------------------------------------------
# Physical parameters (all exactly rational)
# ---------------------------------------------------------------------------
m1, m2 = Fr(1), Fr(1)
l1sq, l2sq = Fr(1), Fr(1)          # rod lengths squared -- rational, no sqrt ever needed
g = Fr(981, 100)                   # 9.81 as an exact rational (a finite decimal IS in Q)
K = Fr(20000)                      # penalty spring stiffness (rational). Larger K -> stiffer
                                    # (closer to the rigid-rod limit) but a stiffer spring
                                    # needs a smaller time step to stay stable -- the usual
                                    # penalty-method tradeoff, not something IDM changes.
tau = Fr(1, 4000)                  # discrete tick (exact rational time step)
N_STEPS = 4000                     # total steps simulated (== 1.0 time unit at this tau)
N_STEPS_EXACT = 250                # exact-Q run is far more expensive; capped separately
                                    # so the script finishes -- the cap itself is the finding


# ---------------------------------------------------------------------------
# Exact rational initial geometry via a Pythagorean triple (3,4,5):
# (3/5, -4/5) is an EXACT unit vector -- (3/5)^2+(4/5)^2 = 9/25+16/25 = 1 exactly.
# No angle, no cos/sin, no sqrt was computed to get this. This is the IDM-honest
# replacement for "theta1 = some angle" from the classical formulation.
# ---------------------------------------------------------------------------
def pivot_bob1(eps_num=0, eps_den=1):
    """r1 = l1 * (3/5, -4/5), optionally perturbed by a small exact rational eps."""
    return (Fr(3, 5) + Fr(eps_num, eps_den), Fr(-4, 5))


def bob1_bob2(eps_num=0, eps_den=1):
    """r2 relative offset from r1 -- a second exact rational unit vector, a different
    Pythagorean triple (5,12,13), so the second arm starts along a different direction."""
    return (Fr(5, 13) + Fr(eps_num, eps_den), Fr(-12, 13))


def make_initial_state(perturb_bob2=False):
    r0 = (Fr(0), Fr(0))
    r1 = pivot_bob1()
    dx2, dy2 = bob1_bob2(eps_num=(1 if perturb_bob2 else 0), eps_den=10_000_000)
    r2 = (r1[0] + dx2, r1[1] + dy2)
    v1 = (Fr(0), Fr(0))
    v2 = (Fr(0), Fr(0))
    return r0, r1, v1, r2, v2


# ---------------------------------------------------------------------------
# Forces -- pure rational polynomial arithmetic, no sqrt/trig anywhere.
# Quartic penalty: V(p,q) = (K/4)*(|p-q|^2 - l^2)^2  =>  F_p = -K*(|p-q|^2-l^2)*(p-q)
# ---------------------------------------------------------------------------
def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def norm_sq(v):
    return v[0] * v[0] + v[1] * v[1]


def spring_force_on_p(p, q, lsq, K_):
    d = sub(p, q)
    coeff = -K_ * (norm_sq(d) - lsq)
    return (coeff * d[0], coeff * d[1])


def forces(r0, r1, r2):
    f1_from_pivot = spring_force_on_p(r1, r0, l1sq, K)
    f1_from_bob2 = spring_force_on_p(r1, r2, l2sq, K)
    f2_from_bob1 = spring_force_on_p(r2, r1, l2sq, K)
    f1 = (f1_from_pivot[0] + f1_from_bob2[0], f1_from_pivot[1] + f1_from_bob2[1] - m1 * g)
    f2 = (f2_from_bob1[0], f2_from_bob1[1] - m2 * g)
    return f1, f2


def accel(f, m):
    return (f[0] / m, f[1] / m)


def velocity_verlet_step(r1, v1, r2, v2, r0):
    f1, f2 = forces(r0, r1, r2)
    a1, a2 = accel(f1, m1), accel(f2, m2)

    r1n = (r1[0] + v1[0] * tau + Fr(1, 2) * a1[0] * tau * tau,
           r1[1] + v1[1] * tau + Fr(1, 2) * a1[1] * tau * tau)
    r2n = (r2[0] + v2[0] * tau + Fr(1, 2) * a2[0] * tau * tau,
           r2[1] + v2[1] * tau + Fr(1, 2) * a2[1] * tau * tau)

    f1n, f2n = forces(r0, r1n, r2n)
    a1n, a2n = accel(f1n, m1), accel(f2n, m2)

    v1n = (v1[0] + Fr(1, 2) * (a1[0] + a1n[0]) * tau,
           v1[1] + Fr(1, 2) * (a1[1] + a1n[1]) * tau)
    v2n = (v2[0] + Fr(1, 2) * (a2[0] + a2n[0]) * tau,
           v2[1] + Fr(1, 2) * (a2[1] + a2n[1]) * tau)

    return r1n, v1n, r2n, v2n


# ---------------------------------------------------------------------------
# Run: exact Q (Fraction) simulation
# ---------------------------------------------------------------------------
def run_exact(n_steps, perturb_bob2=False, log_every=200, verbose=False):
    r0, r1, v1, r2, v2 = make_initial_state(perturb_bob2)
    trace = []
    t0 = time.time()
    for n in range(n_steps):
        step_t0 = time.time()
        r1, v1, r2, v2 = velocity_verlet_step(r1, v1, r2, v2, r0)
        step_dt = time.time() - step_t0
        if n % log_every == 0 or n == n_steps - 1:
            c1 = norm_sq(sub(r1, r0)) - l1sq
            c2 = norm_sq(sub(r2, r1)) - l2sq
            row = (n, float(r1[0]), float(r1[1]), float(r2[0]), float(r2[1]),
                   float(c1), float(c2),
                   r2[0].denominator.bit_length(), r2[1].denominator.bit_length(),
                   step_dt)
            trace.append(row)
            if verbose:
                print(f"  n={n:5d}  r2=({row[3]:+.6f},{row[4]:+.6f})  "
                      f"denom_bits={row[7]:6d}  this_step_time={step_dt:.4f}s")
    dt = time.time() - t0
    return trace, dt, (r1, v1, r2, v2)


# ---------------------------------------------------------------------------
# Run: floating-point simulation of the IDENTICAL equations (same K, tau, masses)
# ---------------------------------------------------------------------------
def make_initial_state_f(perturb_bob2=False):
    r0 = (0.0, 0.0)
    r1 = (3 / 5, -4 / 5)
    eps = (1 / 10_000_000) if perturb_bob2 else 0.0
    r2 = (r1[0] + 5 / 13 + eps, r1[1] - 12 / 13)
    return r0, r1, (0.0, 0.0), r2, (0.0, 0.0)


def forces_f(r0, r1, r2, m1f, m2f, gf, Kf, l1sqf, l2sqf):
    def sub_f(a, b):
        return (a[0] - b[0], a[1] - b[1])

    def nsq_f(v):
        return v[0] * v[0] + v[1] * v[1]

    def spring_f(p, q, lsq):
        d = sub_f(p, q)
        c = -Kf * (nsq_f(d) - lsq)
        return (c * d[0], c * d[1])

    f1a = spring_f(r1, r0, l1sqf)
    f1b = spring_f(r1, r2, l2sqf)
    f2a = spring_f(r2, r1, l2sqf)
    f1 = (f1a[0] + f1b[0], f1a[1] + f1b[1] - m1f * gf)
    f2 = (f2a[0], f2a[1] - m2f * gf)
    return f1, f2


def run_float(n_steps, perturb_bob2=False, log_every=200):
    m1f, m2f, gf, Kf, tauf = 1.0, 1.0, 9.81, 20000.0, 1.0 / 4000.0
    l1sqf, l2sqf = 1.0, 1.0
    r0, r1, v1, r2, v2 = make_initial_state_f(perturb_bob2)
    trace = []
    t0 = time.time()
    for n in range(n_steps):
        f1, f2 = forces_f(r0, r1, r2, m1f, m2f, gf, Kf, l1sqf, l2sqf)
        a1 = (f1[0] / m1f, f1[1] / m1f)
        a2 = (f2[0] / m2f, f2[1] / m2f)
        r1n = (r1[0] + v1[0] * tauf + 0.5 * a1[0] * tauf ** 2,
               r1[1] + v1[1] * tauf + 0.5 * a1[1] * tauf ** 2)
        r2n = (r2[0] + v2[0] * tauf + 0.5 * a2[0] * tauf ** 2,
               r2[1] + v2[1] * tauf + 0.5 * a2[1] * tauf ** 2)
        f1n, f2n = forces_f(r0, r1n, r2n, m1f, m2f, gf, Kf, l1sqf, l2sqf)
        a1n = (f1n[0] / m1f, f1n[1] / m1f)
        a2n = (f2n[0] / m2f, f2n[1] / m2f)
        v1n = (v1[0] + 0.5 * (a1[0] + a1n[0]) * tauf, v1[1] + 0.5 * (a1[1] + a1n[1]) * tauf)
        v2n = (v2[0] + 0.5 * (a2[0] + a2n[0]) * tauf, v2[1] + 0.5 * (a2[1] + a2n[1]) * tauf)
        r1, v1, r2, v2 = r1n, v1n, r2n, v2n
        if n % log_every == 0 or n == n_steps - 1:
            c1 = (r1[0] ** 2 + r1[1] ** 2) - l1sqf
            c2 = ((r2[0] - r1[0]) ** 2 + (r2[1] - r1[1]) ** 2) - l2sqf
            trace.append((n, r1[0], r1[1], r2[0], r2[1], c1, c2))
    dt = time.time() - t0
    return trace, dt, (r1, v1, r2, v2)


def run_exact_budgeted(wall_budget_s, perturb_bob2=False, log_every=5):
    """Run the exact-Q simulation until wall_budget_s elapses, logging every
    log_every steps. Returns however many steps it actually got through --
    the step count reached under a fixed time budget IS the honest
    representational-cost finding, not a number chosen in advance."""
    r0, r1, v1, r2, v2 = make_initial_state(perturb_bob2)
    trace = []
    t0 = time.time()
    n = 0
    while True:
        step_t0 = time.time()
        r1, v1, r2, v2 = velocity_verlet_step(r1, v1, r2, v2, r0)
        step_dt = time.time() - step_t0
        elapsed = time.time() - t0
        if n % log_every == 0:
            c1 = norm_sq(sub(r1, r0)) - l1sq
            row = (n, float(r1[0]), float(r1[1]), float(r2[0]), float(r2[1]),
                   float(c1), r2[0].denominator.bit_length(), step_dt, elapsed)
            trace.append(row)
            print(f"  n={n:4d}  r2=({row[3]:+.6f},{row[4]:+.6f})  "
                  f"constraint_err={row[5]:+.2e}  denom_bits={row[6]:6d}  "
                  f"this_step={step_dt:6.3f}s  elapsed={elapsed:6.1f}s")
        n += 1
        if elapsed > wall_budget_s:
            print(f"  [stopped: wall budget {wall_budget_s}s reached after {n} steps]")
            break
    return trace, n, (r1, v1, r2, v2)


if __name__ == "__main__":
    WALL_BUDGET = 45  # seconds, per run

    print("=" * 78)
    print("EXACT-Q (Fraction) double pendulum -- unperturbed, wall-time budgeted")
    print("=" * 78)
    exact_trace, n_reached, _ = run_exact_budgeted(WALL_BUDGET, perturb_bob2=False,
                                                     log_every=5)
    print(f"\n-> reached n={n_reached} steps within {WALL_BUDGET}s wall budget "
          f"(that is t={n_reached/4000:.4f} physical time units at tau=1/4000)\n")

    n_float = n_reached  # compare float over the SAME step count exact-Q actually reached
    print("=" * 78)
    print(f"FLOAT64 double pendulum -- unperturbed, SAME {n_float} steps, IDENTICAL equations")
    print("=" * 78)
    float_trace, float_dt, _ = run_float(n_float, perturb_bob2=False, log_every=max(1, n_float // 10))
    for row in float_trace:
        n, x1, y1, x2, y2, c1, c2 = row
        print(f"  n={n:4d}  r2=({x2:+.6f},{y2:+.6f})  constraint_err=({c1:+.2e},{c2:+.2e})")
    print(f"wall time: {float_dt:.5f}s for {n_float} steps "
          f"({float_dt/max(n_float,1)*1000:.4f} ms/step)\n")

    print("=" * 78)
    print("DIVERGENCE: exact-Q vs float64, SAME nominal initial condition, matched step count")
    print("=" * 78)
    exact_by_n = {row[0]: row for row in exact_trace}
    for row in float_trace:
        n = row[0]
        if n not in exact_by_n:
            continue
        erow = exact_by_n[n]
        dx2 = erow[3] - row[3]
        dy2 = erow[4] - row[4]
        drift = (dx2 ** 2 + dy2 ** 2) ** 0.5
        print(f"  n={n:4d}  |r2_exact - r2_float| = {drift:.3e}")

    print()
    print("=" * 78)
    print(f"CHAOS TEST: two exact-Q runs differing by 1e-7 in bob2 initial x, "
          f"{n_float} steps each")
    print("=" * 78)
    exact_a, na, _ = run_exact_budgeted(WALL_BUDGET / 2, perturb_bob2=False, log_every=10)
    exact_b, nb, _ = run_exact_budgeted(WALL_BUDGET / 2, perturb_bob2=True, log_every=10)
    a_by_n = {row[0]: row for row in exact_a}
    for row in exact_b:
        n = row[0]
        if n not in a_by_n:
            continue
        arow = a_by_n[n]
        dx2 = arow[3] - row[3]
        dy2 = arow[4] - row[4]
        sep = (dx2 ** 2 + dy2 ** 2) ** 0.5
        print(f"  n={n:4d}  exact-Q trajectory separation = {sep:.6e}  (started at 1e-7)")
