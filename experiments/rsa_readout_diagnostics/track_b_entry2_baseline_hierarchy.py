"""
TRACK B, ENTRY 2 -- Baseline hierarchy B0/B1/B2 on the SAME candidate stream,
before any IDM mechanism is proposed. Per review mandate: strong baseline first,
measurement before mechanism, attribution before novelty.

B0 = naive trial division, unfiltered factor base (what Entries 001-004 used --
     now DISCLOSED as the weak baseline it is).
B1 = QR-filtered trial division (classical, Entry 005's finding).
B2 = SIMPLIFIED QS-LIKE SIEVE. Explicitly labeled SIMPLIFIED, not STANDARD:
     - single polynomial (x^2 - N), no multiple-polynomial (MPQS) variation
     - log2(p)-weighted array accumulation over an interval, first-power roots
       only (no p^2/p^3 power contributions -- a real implementation adds
       those too; omitted here and disclosed as a simplification)
     - a single global threshold (bit_length(cofactor) - slack), not the
       calibrated per-position threshold real implementations tune
     - no large-prime variation, no duplicate/singleton relation handling
     This is a mechanics audit, not just a name: factor-base construction (B1's
     QR filter), modular roots (brute-force sqrt mod p, fine at this scale),
     sieve interval, log-score accumulation, thresholding, and a verification
     pass (full trial division, ONLY on flagged candidates) are all present.
     What's missing is disclosed above, not hidden.

COST VECTOR (kept apart, not collapsed to a premature scalar):
  N_div        = division/modulo operations (B0/B1 acquisition, B2 verification)
  N_sieve      = sieve-array score updates (B2 only)
  N_relations  = smooth relations found
  N_candidates = candidates examined/covered
Calibration weights are machine-specific empirical measurements, stated as such,
not universal constants.

No Toledo registration, no git mutation. Disposable diagnostic.
"""

import math
import timeit


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
    """Brute-force modular square root -- fine at this scale (p < few hundred).
    Not a Toledo object; standard number-theoretic primitive."""
    a = a % p
    roots = [x for x in range(p) if (x * x) % p == a]
    return roots


def full_trial_divide(cofactor, factor_base):
    exps = [0] * len(factor_base)
    ops = 0
    for i, p in enumerate(factor_base):
        while cofactor % p == 0:
            cofactor //= p
            exps[i] += 1
            ops += 1
        ops += 1
    return (cofactor == 1), exps, ops


# ---------------------------------------------------------------------------
# B0 / B1: candidate-by-candidate trial division (identical mechanics, only
# the factor base differs)
# ---------------------------------------------------------------------------
def run_trial_division_baseline(N, factor_base, target_relations, max_candidates):
    root = int(N ** 0.5)
    x = root + 1
    total_div_ops = 0
    candidates_examined = 0
    found = 0
    while found < target_relations:
        r = x * x - N
        is_smooth, _, ops = full_trial_divide(r, factor_base)
        total_div_ops += ops
        candidates_examined += 1
        if is_smooth:
            found += 1
        x += 1
        if candidates_examined >= max_candidates:
            return None
    return {'candidates_examined': candidates_examined, 'div_ops': total_div_ops,
            'relations_found': found}


# ---------------------------------------------------------------------------
# B2: SIMPLIFIED QS-LIKE SIEVE
# ---------------------------------------------------------------------------
def run_sieve_baseline(N, factor_base, target_relations, max_interval, slack_bits=3):
    root = int(N ** 0.5)
    start = root + 1

    roots_per_prime = []
    for p in factor_base:
        rts = mod_sqrt_bruteforce(N, p)
        roots_per_prime.append(rts)

    interval = min(4000, max_interval)
    while True:
        score = [0.0] * interval
        sieve_updates = 0
        for p, rts in zip(factor_base, roots_per_prime):
            logp = math.log2(p)
            for r in rts:
                # first index i in [0, interval) with (start+i) % p == r
                i0 = (r - start) % p
                for i in range(i0, interval, p):
                    score[i] += logp
                    sieve_updates += 1

        verify_div_ops = 0
        found_relations = []
        for i in range(interval):
            x = start + i
            r = x * x - N
            threshold = r.bit_length() - slack_bits
            if score[i] >= threshold:
                is_smooth, exps, ops = full_trial_divide(r, factor_base)
                verify_div_ops += ops
                if is_smooth:
                    found_relations.append((x, exps))
                    if len(found_relations) >= target_relations:
                        break

        if len(found_relations) >= target_relations or interval >= max_interval:
            return {
                'interval_used': interval,
                'sieve_updates': sieve_updates,
                'verify_div_ops': verify_div_ops,
                'relations_found': len(found_relations),
                'candidates_covered': interval,
                'flagged_for_verification': (verify_div_ops > 0),
            }
        interval = min(interval * 2, max_interval)


def calibrate():
    N_sample, cof_sample, p_sample = 9998000099, 99990001, 293

    def one_div():
        return cof_sample % p_sample

    def one_sieve_update():
        arr[0] += 4.87  # representative log2(p) magnitude add

    arr = [0.0]
    reps = 300_000
    t_div = timeit.timeit(one_div, number=reps) / reps
    t_sieve = timeit.timeit(one_sieve_update, number=reps) / reps
    return t_div, t_sieve


def main():
    print("=" * 78)
    print("TRACK B ENTRY 2 -- Baseline hierarchy B0 (naive) / B1 (QR-filtered) /")
    print("B2 (SIMPLIFIED QS-LIKE sieve). Measurement before mechanism.")
    print("=" * 78)

    w_div, w_sieve = calibrate()
    print(f"\nCALIBRATION (machine-specific empirical, this run): "
          f"1 division-op = {w_div*1e9:.1f}ns, 1 sieve-update = {w_sieve*1e9:.1f}ns "
          f"(ratio: 1 div = {w_div/w_sieve:.2f} sieve-updates in wall-time)")

    trials = [
        (1000003 * 1009837, 200),
        (10007 * 10009, 100),
        (99991 * 99989, 300),
    ]

    for N, prime_limit in trials:
        print(f"\n{'='*78}\nN={N} | prime_limit={prime_limit}\n{'='*78}")
        all_odd = sieve_primes(prime_limit)[1:]
        qr_fb = [p for p in all_odd if legendre_symbol(N, p) == 1]

        target_b0 = len(all_odd) + 4
        target_b1 = len(qr_fb) + 4
        target_b2 = len(qr_fb) + 4  # B2 uses the same QR-filtered factor base as B1

        b0 = run_trial_division_baseline(N, all_odd, target_b0, max_candidates=300_000)
        b1 = run_trial_division_baseline(N, qr_fb, target_b1, max_candidates=300_000)
        b2 = run_sieve_baseline(N, qr_fb, target_b2, max_interval=200_000)

        print(f"factor_base sizes: B0(unfiltered)={len(all_odd)}  B1/B2(QR-filtered)={len(qr_fb)}")

        if b0:
            cost_b0 = b0['div_ops'] * w_div
            print(f"B0 naive:        candidates={b0['candidates_examined']:>7}  "
                  f"div_ops={b0['div_ops']:>8}  calibrated_time={cost_b0*1e6:>9.1f}us")
        else:
            print("B0 naive: INCONCLUSIVE (hit candidate cap)")

        if b1:
            cost_b1 = b1['div_ops'] * w_div
            print(f"B1 QR-filtered:  candidates={b1['candidates_examined']:>7}  "
                  f"div_ops={b1['div_ops']:>8}  calibrated_time={cost_b1*1e6:>9.1f}us")
        else:
            print("B1 QR-filtered: INCONCLUSIVE (hit candidate cap)")

        cost_b2 = b2['sieve_updates'] * w_sieve + b2['verify_div_ops'] * w_div
        print(f"B2 SIMPLIFIED sieve: candidates_covered={b2['candidates_covered']:>7}  "
              f"sieve_updates={b2['sieve_updates']:>8}  verify_div_ops={b2['verify_div_ops']:>6}  "
              f"relations_found={b2['relations_found']}/{target_b2}  "
              f"calibrated_time={cost_b2*1e6:>9.1f}us")

        if b1 and b2['relations_found'] >= target_b2:
            print(f"B2/B1 calibrated-time ratio: {cost_b2/cost_b1:.3f}  "
                  f"({'B2 (sieve) cheaper' if cost_b2 < cost_b1 else 'B1 (trial division) still cheaper'})")
        if b0 and b2['relations_found'] >= target_b2:
            print(f"B2/B0 calibrated-time ratio: {cost_b2/cost_b0:.3f}")

        # bottleneck decomposition for B2 (the strongest baseline)
        total = b2['sieve_updates'] * w_sieve + b2['verify_div_ops'] * w_div
        if total > 0:
            print(f"B2 bottleneck decomposition: sieve-phase={100*b2['sieve_updates']*w_sieve/total:.1f}%  "
                  f"verify-phase={100*b2['verify_div_ops']*w_div/total:.1f}%")

    print("\n" + "=" * 78)
    print("READING THIS RESULT -- required question: after moving from trial")
    print("division to a sieve, WHERE DID THE BOTTLENECK MOVE? Read the")
    print("'bottleneck decomposition' line above per trial BEFORE proposing any")
    print("next mechanism -- do not guess ahead of the measurement.")
    print("=" * 78)


if __name__ == '__main__':
    main()
