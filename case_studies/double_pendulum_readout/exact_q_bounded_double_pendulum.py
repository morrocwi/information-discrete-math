"""
Bounded-precision Q (rational, declared truncation every step) double pendulum.

Fixes the failure found in exact_q_double_pendulum.py: unbounded fractions.Fraction
arithmetic blows up in denominator size (~9x per 2 steps, confirmed independent of spring
stiffness) and becomes computationally dead within ~8-10 steps -- too short a window to see
any chaos-vs-rounding comparison develop.

The fix information-discrete-math itself permits (its own README: "R = a *readout* of the
discrete (Bishop regular Cauchy sequences of Q); only finite Q-approximants ever appear"):
after every Verlet step, truncate each coordinate to a BOUNDED-DENOMINATOR rational
approximant via continued-fraction convergents (Python's Fraction.limit_denominator --
literally "the closest rational with denominator <= N", a real, well-defined operation, not
an approximation hack). This is declared and constant every step (not silent, not
accumulating without bound) -- the honest difference from float is WHEN rounding happens:
float rounds after every single elementary +,-,*,/ ; this design does full exact arithmetic
WITHIN a step (all the intermediate force/acceleration computation is exact), and only
truncates ONCE per step, to a declared, fixed precision budget.

MAX_DENOM is chosen comparable to float64's representable precision (~15-17 significant
decimal digits, i.e. denominators up to roughly 10^15-10^18 for numbers of order 1) so the
comparison to float is apples-to-apples in stated precision, not just "we used more digits".
"""
from __future__ import annotations

import time
from fractions import Fraction as Fr

import exact_q_double_pendulum as base


MAX_DENOM = 10 ** 15  # declared precision budget -- comparable to float64's ~15-17 sig figs


def truncate(v, max_denom=MAX_DENOM):
    return (v[0].limit_denominator(max_denom), v[1].limit_denominator(max_denom))


def velocity_verlet_step_bounded(r1, v1, r2, v2, r0, max_denom=MAX_DENOM):
    """Identical physics to base.velocity_verlet_step, but truncates positions AND
    velocities to a bounded-denominator rational approximant once at the end of the step
    -- declared precision, applied openly, every step, per IDM's own R-as-readout allowance."""
    r1n, v1n, r2n, v2n = base.velocity_verlet_step(r1, v1, r2, v2, r0)
    return truncate(r1n, max_denom), truncate(v1n, max_denom), \
           truncate(r2n, max_denom), truncate(v2n, max_denom)


def run_bounded(n_steps, perturb_bob2=False, log_every=200, max_denom=MAX_DENOM):
    r0, r1, v1, r2, v2 = base.make_initial_state(perturb_bob2)
    trace = []
    t0 = time.time()
    max_bits_seen = 0
    for n in range(n_steps):
        r1, v1, r2, v2 = velocity_verlet_step_bounded(r1, v1, r2, v2, r0, max_denom)
        bits = max(r2[0].denominator.bit_length(), r2[1].denominator.bit_length())
        max_bits_seen = max(max_bits_seen, bits)
        if n % log_every == 0 or n == n_steps - 1:
            c1 = base.norm_sq(base.sub(r1, r0)) - base.l1sq
            c2 = base.norm_sq(base.sub(r2, r1)) - base.l2sq
            trace.append((n, float(r1[0]), float(r1[1]), float(r2[0]), float(r2[1]),
                          float(c1), float(c2), bits))
    dt = time.time() - t0
    return trace, dt, max_bits_seen, (r1, v1, r2, v2)


if __name__ == "__main__":
    N_STEPS = 3000
    LOG_EVERY = 200

    print("=" * 78)
    print(f"BOUNDED EXACT-Q (declared truncation, max_denom={MAX_DENOM:.0e}) "
          f"-- unperturbed, {N_STEPS} steps")
    print("=" * 78)
    bq_trace, bq_dt, bq_maxbits, _ = run_bounded(N_STEPS, perturb_bob2=False,
                                                   log_every=LOG_EVERY)
    for row in bq_trace:
        n, x1, y1, x2, y2, c1, c2, bits = row
        print(f"  n={n:5d}  r2=({x2:+.9f},{y2:+.9f})  "
              f"constraint=({c1:+.2e},{c2:+.2e})  denom_bits={bits:4d}")
    print(f"wall time: {bq_dt:.2f}s for {N_STEPS} steps "
          f"({bq_dt/N_STEPS*1000:.3f} ms/step), max denom_bits ever seen={bq_maxbits}\n")

    print("=" * 78)
    print(f"FLOAT64 -- unperturbed, SAME {N_STEPS} steps, IDENTICAL equations")
    print("=" * 78)
    float_trace, float_dt, _ = base.run_float(N_STEPS, perturb_bob2=False,
                                                log_every=LOG_EVERY)
    for row in float_trace:
        n, x1, y1, x2, y2, c1, c2 = row
        print(f"  n={n:5d}  r2=({x2:+.9f},{y2:+.9f})  constraint=({c1:+.2e},{c2:+.2e})")
    print(f"wall time: {float_dt:.4f}s for {N_STEPS} steps "
          f"({float_dt/N_STEPS*1000:.4f} ms/step)\n")

    print("=" * 78)
    print("DIVERGENCE: bounded-exact-Q vs float64, SAME nominal initial condition")
    print("(both start from the SAME exact rational IC -- any gap here is pure")
    print(" numeric-representation artifact, not a real physical difference)")
    print("=" * 78)
    bq_by_n = {row[0]: row for row in bq_trace}
    for row in float_trace:
        n = row[0]
        if n not in bq_by_n:
            continue
        b = bq_by_n[n]
        dx2, dy2 = b[3] - row[3], b[4] - row[4]
        drift = (dx2 ** 2 + dy2 ** 2) ** 0.5
        print(f"  n={n:5d}  |r2_boundedQ - r2_float| = {drift:.3e}")

    print()
    print("=" * 78)
    print(f"CHAOS TEST: two bounded-exact-Q runs differing by 1e-7 in bob2 initial x, "
          f"{N_STEPS} steps")
    print("=" * 78)
    a_trace, _, _, _ = run_bounded(N_STEPS, perturb_bob2=False, log_every=LOG_EVERY)
    b_trace, _, _, _ = run_bounded(N_STEPS, perturb_bob2=True, log_every=LOG_EVERY)
    for (a, b) in zip(a_trace, b_trace):
        n = a[0]
        dx2, dy2 = a[3] - b[3], a[4] - b[4]
        sep = (dx2 ** 2 + dy2 ** 2) ** 0.5
        print(f"  n={n:5d}  boundedQ trajectory separation = {sep:.6e}  (started at 1e-7)")

    print()
    print("=" * 78)
    print(f"CHAOS TEST (control): SAME perturbation, float64, {N_STEPS} steps")
    print("=" * 78)
    fa_trace, _, _ = base.run_float(N_STEPS, perturb_bob2=False, log_every=LOG_EVERY)
    fb_trace, _, _ = base.run_float(N_STEPS, perturb_bob2=True, log_every=LOG_EVERY)
    for (a, b) in zip(fa_trace, fb_trace):
        n = a[0]
        dx2, dy2 = a[3] - b[3], a[4] - b[4]
        sep = (dx2 ** 2 + dy2 ** 2) ** 0.5
        print(f"  n={n:5d}  float64 trajectory separation  = {sep:.6e}  (started at 1e-7)")
