"""
PHASE 1 -- close the cheap headroom question with a real distribution, not n=1.

FROZEN PARAMETERS (declared BEFORE running, never adjusted after seeing results,
per review point 3 / 20 -- any post-hoc adjustment would be exactly the
"artifact amplification" / parameter-tuning failure mode flagged):
  PRIME_LIMIT   = 300      (factor-base prime bound, fixed)
  MARGIN        = 4        (target_relations = QR-filtered fb_size + MARGIN)
  K_REGIONS     = 10       (fixed)
  REGION_WIDTH  = 4000     (fixed)
  SLACK_BITS    = 6        (the CORRECTED value from Entry 008, not the original
                             flawed 3 -- reusing the already-diagnosed fix, not a
                             new tune)
  BIT_SIZE      = each held-out N is a product of two random ~17-bit primes
                  (matching the one instance that completed successfully in
                  Entry 008, ~34-bit N) -- chosen for tractable runtime, not
                  because it was seen to work well in previous ad-hoc runs on
                  THIS SPECIFIC script (it's the same order of magnitude as the
                  one prior completed trial, disclosed as the reason).
  N_INSTANCES   = 20
  SEED          = 20260920 (fixed, for reproducibility)

No parameter here is chosen after inspecting Phase 1's own output. If completion
rate is poor, that is reported as-is (a real finding about this action family),
not fixed by retroactively widening the window for failing instances only.
"""

import math
import random
import statistics


def is_probable_prime(n, rounds=20):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    rng = random.Random(12345)
    for _ in range(rounds):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def random_prime_near(bits, rng):
    while True:
        cand = rng.getrandbits(bits) | 1 | (1 << (bits - 1))
        if is_probable_prime(cand):
            return cand


def sieve_primes(limit):
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if is_p[i]:
            for j in range(i * i, limit + 1, i):
                is_p[j] = False
    return [i for i, v in enumerate(is_p) if v]


def legendre_symbol(a, p):
    a = a % p
    if a == 0:
        return 0
    ls = pow(a, (p - 1) // 2, p)
    return -1 if ls == p - 1 else ls


def mod_sqrt_bruteforce(a, p):
    a = a % p
    return [x for x in range(p) if (x * x) % p == a]


def full_trial_divide(cofactor, factor_base):
    exps = [0] * len(factor_base)
    ops = 0
    for i, p in enumerate(factor_base):
        while cofactor % p == 0:
            cofactor //= p
            exps[i] += 1
            ops += 1
        ops += 1
    return (cofactor == 1), ops


def sieve_region(N, factor_base, roots_per_prime, region_start, width, slack_bits):
    score = [0.0] * width
    sieve_updates = 0
    for p, rts in zip(factor_base, roots_per_prime):
        logp = math.log2(p)
        for r in rts:
            i0 = (r - region_start) % p
            for i in range(i0, width, p):
                score[i] += logp
                sieve_updates += 1
    verify_div_ops = 0
    relations_found = 0
    for i in range(width):
        x = region_start + i
        r = x * x - N
        threshold = r.bit_length() - slack_bits
        if score[i] >= threshold:
            is_smooth, ops = full_trial_divide(r, factor_base)
            verify_div_ops += ops
            if is_smooth:
                relations_found += 1
    return {'sieve_updates': sieve_updates, 'verify_div_ops': verify_div_ops,
            'relations_found': relations_found}


PRIME_LIMIT = 300
MARGIN = 4
K_REGIONS = 10
REGION_WIDTH = 4000
SLACK_BITS = 6
BIT_SIZE = 17
N_INSTANCES = 20
SEED = 20260920


def run_one_instance(N):
    root = int(N ** 0.5)
    all_odd = sieve_primes(PRIME_LIMIT)[1:]
    fb = [p for p in all_odd if legendre_symbol(N, p) == 1]
    if len(fb) < 3:
        return {'status': 'DEGENERATE_FACTOR_BASE'}
    roots_per_prime = [mod_sqrt_bruteforce(N, p) for p in fb]
    target = len(fb) + MARGIN

    regions = []
    for k in range(K_REGIONS):
        region_start = root + 1 + k * REGION_WIDTH
        r = sieve_region(N, fb, roots_per_prime, region_start, REGION_WIDTH, SLACK_BITS)
        r['cost'] = r['sieve_updates'] + r['verify_div_ops']
        regions.append(r)

    total_available = sum(r['relations_found'] for r in regions)
    if total_available < target:
        return {'status': 'INCOMPLETE', 'total_available': total_available, 'target': target}

    acc, naive_cost = 0, 0
    for r in regions:
        naive_cost += r['cost']
        acc += r['relations_found']
        if acc >= target:
            break

    def density(r):
        return r['relations_found'] / max(1, r['cost'])

    acc, oracle_cost = 0, 0
    for r in sorted(regions, key=density, reverse=True):
        oracle_cost += r['cost']
        acc += r['relations_found']
        if acc >= target:
            break

    headroom = 1 - (oracle_cost / naive_cost) if naive_cost > 0 else 0.0
    return {'status': 'COMPLETE', 'headroom': headroom, 'naive_cost': naive_cost,
            'oracle_cost': oracle_cost, 'fb_size': len(fb), 'target': target}


def main():
    print("=" * 78)
    print("PHASE 1 -- Oracle headroom DISTRIBUTION over N_INSTANCES=%d held-out semiprimes"
          % N_INSTANCES)
    print(f"FROZEN: PRIME_LIMIT={PRIME_LIMIT} MARGIN={MARGIN} K={K_REGIONS} "
          f"WIDTH={REGION_WIDTH} SLACK_BITS={SLACK_BITS} BIT_SIZE={BIT_SIZE} SEED={SEED}")
    print("=" * 78)

    rng = random.Random(SEED)
    results = []
    for i in range(N_INSTANCES):
        p = random_prime_near(BIT_SIZE, rng)
        q = random_prime_near(BIT_SIZE, rng)
        while q == p:
            q = random_prime_near(BIT_SIZE, rng)
        N = p * q
        res = run_one_instance(N)
        res['instance'] = i
        res['N'] = N
        results.append(res)
        status = res['status']
        extra = f"headroom={res['headroom']*100:.1f}%" if status == 'COMPLETE' else str(res)
        print(f"instance {i:>2}: N={N} status={status}  {extra if status=='COMPLETE' else ''}")

    complete = [r for r in results if r['status'] == 'COMPLETE']
    incomplete = [r for r in results if r['status'] != 'COMPLETE']

    print("\n" + "=" * 78)
    print(f"COMPLETION RATE: {len(complete)}/{N_INSTANCES} "
          f"({100*len(complete)/N_INSTANCES:.0f}%)")
    if incomplete:
        print(f"Incomplete instances (not silently dropped): "
              f"{[(r['instance'], r['status']) for r in incomplete]}")

    if complete:
        h = [r['headroom'] for r in complete]
        h_sorted = sorted(h)
        n = len(h_sorted)
        median = statistics.median(h_sorted)
        mean = statistics.mean(h_sorted)
        q1 = h_sorted[n // 4]
        q3 = h_sorted[(3 * n) // 4]
        print(f"\nHeadroom distribution over {n} complete instances (fraction, 0-1 scale):")
        print(f"  min={min(h_sorted):.4f}  Q1={q1:.4f}  median={median:.4f}  "
              f"Q3={q3:.4f}  max={max(h_sorted):.4f}  mean={mean:.4f}")
        print(f"  all values sorted: {[round(x, 4) for x in h_sorted]}")

        top_tail = [r for r in complete if r['headroom'] > 0.15]
        if top_tail:
            print(f"\nUpper-tail instances (headroom > 15%, flagged as SUSPECT per review "
                  f"point 4 -- audit before treating as signal): {[r['instance'] for r in top_tail]}")
            for r in top_tail:
                print(f"  instance {r['instance']}: N={r['N']}, headroom={r['headroom']*100:.1f}%, "
                      f"fb_size={r['fb_size']}, target={r['target']}, "
                      f"naive_cost={r['naive_cost']}, oracle_cost={r['oracle_cost']}")
        else:
            print("\nNo upper-tail outliers (>15% headroom) observed.")
    else:
        print("\nNO COMPLETE INSTANCES -- cannot report a distribution. This itself is a "
              "finding: frozen parameters do not reliably complete at this bit size within "
              "the frozen window; report as INCONCLUSIVE for Phase 1, do not retune post-hoc.")

    print("=" * 78)


if __name__ == '__main__':
    main()
