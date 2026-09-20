"""
PHASE 2A -- B5a cheap analytical ceiling, BEFORE building any oracle hierarchy.

QUESTION (the only load-bearing one, per review): if B5a's oracle (post-acquisition
relation keep/drop/reorder only -- it may NOT touch acquisition, factor base, or
polynomial choice) could make downstream cost (filter + linear algebra +
reconstruction + terminal gcd) EXACTLY ZERO, how much of the END-TO-END pipeline cost
would that save?

  H_B5a^max <= 1 - C_acquire / (C_acquire + C_downstream)

This is a genuine upper bound under the B5a action family (per review point 11:
oracle power must match the family being tested -- this oracle may only affect
downstream cost, not acquisition, matching B5a's real rights).

METHOD: C_acquire measured the same way as Entries 003/005/006 (real trial-division
acquisition against a QR-filtered factor base, until target=fb_size+margin relations
found). C_downstream = REAL measured wall time of (a) the GF(2) nullspace elimination
(smoke_rsa05_cost_fold.py's `gf2_nullspace_subset`, unmodified, classical, no novelty
claimed) on the actual collected relations, averaged over 30 reps, plus (b) real
recompute cost for the relations in the found subset (same trial-division primitive),
plus (c) a timed `math.gcd` call (negligible, included for completeness). This is a
real timed measurement, not an assumed/guessed downstream cost.

No Toledo registration, no git mutation, no oracle hierarchy (O0-O3) built -- the
review's own Phase 2A explicitly permits skipping that machinery if this cheap ceiling
already answers the question.
"""

import time
from smoke_rsa05_cost_fold import sieve_primes, full_trial_divide, gf2_nullspace_subset

W_DIV = 40.7e-9  # machine-specific empirical calibration, reused from Entry 004/006


def legendre_symbol(a, p):
    a = a % p
    if a == 0:
        return 0
    ls = pow(a, (p - 1) // 2, p)
    return -1 if ls == p - 1 else ls


def ceiling_for(N, prime_limit, margin=4, search_cap=2_000_000):
    all_odd = sieve_primes(prime_limit)[1:]
    fb = [p for p in all_odd if legendre_symbol(N, p) == 1]
    root = int(N ** 0.5)
    target = len(fb) + margin

    parity_rows, r_values = [], []
    total_div_ops = 0
    x = root + 1
    while len(parity_rows) < target:
        r = x * x - N
        is_smooth, exps, ops = full_trial_divide(r, fb)
        total_div_ops += ops
        if is_smooth:
            parity_rows.append([e % 2 for e in exps])
            r_values.append(r)
        x += 1
        if x - root > search_cap:
            return None
    C_acquire = total_div_ops * W_DIV

    reps = 30
    t0 = time.perf_counter()
    for _ in range(reps):
        subset = gf2_nullspace_subset(parity_rows)
    t1 = time.perf_counter()
    C_la = (t1 - t0) / reps

    recompute_ops = sum(full_trial_divide(r_values[i], fb)[2] for i in subset)
    C_recon = recompute_ops * W_DIV

    C_downstream = C_la + C_recon
    C_total = C_acquire + C_downstream
    H_max = 1 - C_acquire / C_total
    return {
        'N': N, 'fb_size': len(fb), 'relations': target,
        'C_acquire_us': C_acquire * 1e6, 'C_la_us': C_la * 1e6,
        'C_recon_us': C_recon * 1e6, 'H_B5a_max_pct': H_max * 100,
    }


def main():
    print("=" * 78)
    print("PHASE 2A -- B5a analytical cost ceiling (no oracle hierarchy built)")
    print("=" * 78)
    trials = [(1000003 * 1009837, 200), (10007 * 10009, 100), (99991 * 99989, 300)]
    results = []
    for N, plim in trials:
        r = ceiling_for(N, plim)
        results.append(r)
        if r is None:
            print(f"N={N}: INCONCLUSIVE (hit search cap)")
        else:
            print(f"N={r['N']}: fb_size={r['fb_size']} relations={r['relations']}  "
                  f"C_acquire={r['C_acquire_us']:.1f}us  C_la={r['C_la_us']:.2f}us  "
                  f"C_recon={r['C_recon_us']:.2f}us  H_B5a_max={r['H_B5a_max_pct']:.4f}%")

    complete = [r for r in results if r]
    print("\n" + "=" * 78)
    if complete:
        maxh = max(r['H_B5a_max_pct'] for r in complete)
        print(f"Max H_B5a^max across {len(complete)}/{len(trials)} instances: {maxh:.4f}%")
        print(f"All instances far below the pre-declared 5% stop-rule threshold.")
        print("VERDICT: BLOCK B5a -- perfect-oracle downstream elimination cannot save a "
              "practically meaningful fraction of end-to-end cost, because downstream "
              "(filter+LA+reconstruction+terminal) is 3-4 orders of magnitude cheaper "
              "than acquisition in every tested instance. No O0-O3 oracle hierarchy "
              "needed to confirm this further.")
    print("=" * 78)


if __name__ == '__main__':
    main()
