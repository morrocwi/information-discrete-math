"""
TRACK C, ENTRY 1 -- Layer A: ORACLE HEADROOM for readout-conditioned routing.

main.hub-INSPIRED EXPERIMENTAL FRAMING (not a Toledo object, not canonical, not
claimed to derive from main.hub as prior art -- an analogy used to generate a
testable hypothesis, per review point 18):

  s_t  = retained computational state (relations found so far, regions sieved)
  Q    = terminal readout requirement (enough relations for a GF(2) nullspace)
  a_t  = next action (WHICH region to sieve next, from a finite action set)
  Pi   = routing policy choosing a_t from s_t
  T    = state transition (sieve the chosen region, update s_t)

QUESTION (Layer A only -- do NOT build a policy yet, per review's mandated
order): if an OMNISCIENT oracle could see the true smoothness yield of every
candidate region in advance and always sieve the best-yielding region first,
how much total sieve-work would that save vs. the FIXED naive schedule (sieve
regions in index order)? If this number is tiny, there is no headroom and any
router built later is guaranteed worthless before it is even built.

HARNESS (SIMPLIFIED, disclosed): a single polynomial x^2-N (no true MPQS/SIQS
multiple polynomials -- that is a materially larger engineering lift). The
"action set" is K contiguous, non-overlapping candidate regions of fixed
width W starting just past sqrt(N). Regions differ in yield only through the
natural residue-density noise of which x happen to land smooth -- NOT through
any structural difference the field's multiple-polynomial techniques exploit.
This is explicitly a MINIMAL, DEGENERATE routing testbed, not a claim that
real MPQS-style polynomial-switching headroom is being measured.

ORACLE (retrospective only, not an online policy):
  1. Fully sieve+verify ALL K regions (this is the finite-model "oracle" pass
     -- looking at the full outcome is only valid for measuring HEADROOM, and
     is explicitly NOT usable online, per review point 10/11).
  2. Compute, for each region, (relations found, sieve_updates spent, verify
     div_ops spent).
  3. Oracle schedule: sort regions by relations-per-sieve-update descending,
     take regions in that order until the target relation count is reached.
  4. Naive/fixed schedule P0: take regions in index order until target
     reached.
  5. Headroom = 1 - (oracle cost / naive cost), on the SAME K regions, same
     factor base, same instance.

No Toledo registration, no git mutation, no claim of MPQS-level generality.
"""

import math


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


def sieve_region(N, factor_base, roots_per_prime, region_start, width, slack_bits=6):
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
    return {
        'sieve_updates': sieve_updates,
        'verify_div_ops': verify_div_ops,
        'relations_found': relations_found,
    }


def run_instance(N, prime_limit, K, width, target_relations):
    root = int(N ** 0.5)
    all_odd = sieve_primes(prime_limit)[1:]
    fb = [p for p in all_odd if legendre_symbol(N, p) == 1]
    roots_per_prime = [mod_sqrt_bruteforce(N, p) for p in fb]

    regions = []
    for k in range(K):
        region_start = root + 1 + k * width
        r = sieve_region(N, fb, roots_per_prime, region_start, width)
        r['index'] = k
        r['cost'] = r['sieve_updates'] + r['verify_div_ops']  # units disclosed below
        regions.append(r)

    total_relations_available = sum(r['relations_found'] for r in regions)
    if total_relations_available < target_relations:
        return None  # not enough headroom data in this finite window, report honestly

    # P0: fixed/naive order (index order)
    acc = 0
    naive_cost = 0
    naive_regions_used = 0
    for r in regions:
        naive_cost += r['cost']
        acc += r['relations_found']
        naive_regions_used += 1
        if acc >= target_relations:
            break

    # Oracle: sort by yield density (relations per unit cost), descending
    def yield_density(r):
        return r['relations_found'] / max(1, r['cost'])

    oracle_order = sorted(regions, key=yield_density, reverse=True)
    acc = 0
    oracle_cost = 0
    oracle_regions_used = 0
    for r in oracle_order:
        oracle_cost += r['cost']
        acc += r['relations_found']
        oracle_regions_used += 1
        if acc >= target_relations:
            break

    headroom = 1 - (oracle_cost / naive_cost) if naive_cost > 0 else 0.0

    return {
        'K': K, 'width': width, 'target_relations': target_relations,
        'fb_size': len(fb),
        'total_relations_available': total_relations_available,
        'naive_cost': naive_cost, 'naive_regions_used': naive_regions_used,
        'oracle_cost': oracle_cost, 'oracle_regions_used': oracle_regions_used,
        'headroom_fraction': headroom,
        'per_region_yield': [(r['index'], r['relations_found'], r['cost']) for r in regions],
    }


def main():
    print("=" * 78)
    print("TRACK C ENTRY 1 -- Layer A: Oracle Headroom for region-choice routing")
    print("(main.hub-inspired framing; SIMPLIFIED single-polynomial testbed)")
    print("=" * 78)
    trials = [
        (1000003 * 1009837, 200, 8, 15000, 28),
        (10007 * 10009, 100, 8, 20000, 15),
        (99991 * 99989, 300, 10, 4000, 38),
    ]
    for N, prime_limit, K, width, target in trials:
        print(f"\n--- N={N} | K_regions={K} | width={width} | target_relations={target} ---")
        result = run_instance(N, prime_limit, K, width, target)
        if result is None:
            print("  INCONCLUSIVE: not enough total relations across all K regions to "
                  "reach target -- widen K/width before drawing a headroom conclusion "
                  "for this instance (not silently skipped, reported).")
            continue
        print(f"  fb_size={result['fb_size']}  "
              f"total_relations_available_in_window={result['total_relations_available']}")
        print(f"  P0 (naive, index order):  regions_used={result['naive_regions_used']}/{K}  "
              f"cost={result['naive_cost']}")
        print(f"  Oracle (best-yield-first): regions_used={result['oracle_regions_used']}/{K}  "
              f"cost={result['oracle_cost']}")
        print(f"  HEADROOM = {result['headroom_fraction']*100:.1f}%  "
              f"(fraction of P0's cost the oracle could have avoided)")
        print(f"  per-region (index, relations_found, cost): {result['per_region_yield']}")

    print("\n" + "=" * 78)
    print("READING THIS RESULT (Layer A verdict only -- no policy built yet):")
    print("- Headroom near 0%: this action set (region choice within ONE polynomial)")
    print("  has essentially no exploitable variance -- a router here is a dead end")
    print("  regardless of how clever the policy is. Per review point 11: DROP this")
    print("  action family, do not proceed to Layer B/C.")
    print("- Headroom substantial (e.g. >=15-20%) and CONSISTENT across instances:")
    print("  there is a real gap between fixed schedule and ideal routing worth")
    print("  investigating at Layer B (can this be predicted online, without the")
    print("  oracle's retrospective knowledge?).")
    print("- Caveat already flagged: this testbed's 'regions' differ only by residue")
    print("  noise, not by a structurally distinct polynomial/lattice choice -- even a")
    print("  positive headroom number here is a WEAK proxy for real MPQS/SIQS-style")
    print("  polynomial-switching headroom, which would need an actually different,")
    print("  larger engineering lift to test properly.")
    print("=" * 78)


if __name__ == '__main__':
    main()
