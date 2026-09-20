"""
GENERATION-2 MECHANISM -- Staged/Hybrid DropSafe, derived from RSA-08's Entry-001
failure (logged DRIFT: exact/bounded certificate ALWAYS costs more than the
classical heuristic because it is invoked unconditionally on every candidate
whose residual cofactor exceeds the largest factor-base prime).

FAILURE -> CONSTRAINT -> NEW MECHANISM, per the reviewer's mandated cycle:
  Failure:    C_decision(prune) was paid on every candidate, most of which
              didn't need it (the heuristic's cheap size-check alone already
              resolves most candidates correctly).
  Constraint: C_decision(prune) < E[work saved] -- the certificate must only
              be bought when there is a real chance it changes the outcome.
  New mechanism (STAGED): use the classical heuristic's cheap bit-length check
              purely as a GATE deciding WHETHER to pay for the exact
              certificate -- not as the rejection rule itself (that was
              HEURISTIC's own unsafe move: rejecting on the size check alone,
              which produced real false rejects in Entry 001's baseline).
              STAGED never rejects on the size check alone: if the residual is
              small (heuristically "still plausible"), it just continues plain
              trial division (cheap, safe, unchanged). Only when the residual
              is heuristically "implausible" (large) does it pay for a
              certificate -- and ONLY a certified-prime residual is ever
              rejected. This should pay certificate cost on a small minority
              of candidates instead of on every one, while remaining exactly
              as safe (zero false rejects) as the original DropSafe.

This is explicitly checked against the classical baseline in every trial, and
is reported honestly if it fails to beat HEURISTIC too -- this is an attempt
to find computational content in the IDM programme's general readout-
conditioned pruning idea, not a defense of RSA-08's original formulation.

CORRECTION (code review, 2026-09-20): "certificate," "certified-prime," and
"exactly as safe" below all mean "safe conditional on the underlying
Miller-Rabin result being correct" -- Miller-Rabin is a PROBABILISTIC test
with a bounded, nonzero false-positive rate, not a deterministic proof.
"Zero false rejects (observed)" is the accurate claim.

PROPOSAL-adjacent scratch mechanism, not itself a Toledo object, not registered,
not canonical. No git mutation, no Toledo registration.
"""

import random


def sieve_primes(limit):
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if is_p[i]:
            for j in range(i * i, limit + 1, i):
                is_p[j] = False
    return [i for i, v in enumerate(is_p) if v]


def miller_rabin(n, rounds, rng, ops_counter):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            ops_counter['cert'] += 1
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(rounds):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        ops_counter['cert'] += 1
        if x == 1 or x == n - 1:
            continue
        composite = True
        for _ in range(r - 1):
            x = pow(x, 2, n)
            ops_counter['cert'] += 1
            if x == n - 1:
                composite = False
                break
        if composite:
            return False
    return True


def trial_divide_full(cofactor, factor_base, ops):
    exps = [0] * len(factor_base)
    for i, p in enumerate(factor_base):
        while cofactor % p == 0:
            cofactor //= p
            exps[i] += 1
            ops['div'] += 1
        ops['div'] += 1
    return cofactor == 1, exps


def trial_divide_heuristic(cofactor, factor_base, ops, prefix_len, bound_bits):
    exps = [0] * len(factor_base)
    for i in range(prefix_len):
        p = factor_base[i]
        while cofactor % p == 0:
            cofactor //= p
            exps[i] += 1
            ops['div'] += 1
        ops['div'] += 1
    if cofactor > 1 and cofactor.bit_length() > bound_bits:
        return 'REJECTED_EARLY', cofactor
    for i in range(prefix_len, len(factor_base)):
        p = factor_base[i]
        while cofactor % p == 0:
            cofactor //= p
            exps[i] += 1
            ops['div'] += 1
        ops['div'] += 1
    return ('SMOOTH' if cofactor == 1 else 'NOT_SMOOTH'), cofactor


def trial_divide_dropsafe_exact(cofactor, factor_base, ops, prefix_len, rng, mr_rounds=8):
    exps = [0] * len(factor_base)
    for i in range(prefix_len):
        p = factor_base[i]
        while cofactor % p == 0:
            cofactor //= p
            exps[i] += 1
            ops['div'] += 1
        ops['div'] += 1
    max_fb_prime = factor_base[-1]
    if cofactor > max_fb_prime:
        if miller_rabin(cofactor, mr_rounds, rng, ops):
            return 'DROPSAFE_CERTIFIED', cofactor
    for i in range(prefix_len, len(factor_base)):
        p = factor_base[i]
        while cofactor % p == 0:
            cofactor //= p
            exps[i] += 1
            ops['div'] += 1
        ops['div'] += 1
    return ('SMOOTH' if cofactor == 1 else 'NOT_SMOOTH'), cofactor


def trial_divide_staged(cofactor, factor_base, ops, prefix_len, bound_bits, rng, mr_rounds=8):
    """GENERATION-2: the certificate is a GATE-CONDITIONAL fallback, not an
    unconditional cost. Cheap size check first (bound_bits, same threshold as
    HEURISTIC uses, but never itself a rejection). Certificate only bought
    when the size check flags the residual as implausible; if the certificate
    doesn't confirm primality, fall through to safe full division -- NEVER
    reject without a proof, so this stays exactly as safe as DropSafe-exact."""
    exps = [0] * len(factor_base)
    for i in range(prefix_len):
        p = factor_base[i]
        while cofactor % p == 0:
            cofactor //= p
            exps[i] += 1
            ops['div'] += 1
        ops['div'] += 1
    max_fb_prime = factor_base[-1]
    if cofactor > max_fb_prime and cofactor.bit_length() > bound_bits:
        if miller_rabin(cofactor, mr_rounds, rng, ops):
            return 'DROPSAFE_CERTIFIED', cofactor
    for i in range(prefix_len, len(factor_base)):
        p = factor_base[i]
        while cofactor % p == 0:
            cofactor //= p
            exps[i] += 1
            ops['div'] += 1
        ops['div'] += 1
    return ('SMOOTH' if cofactor == 1 else 'NOT_SMOOTH'), cofactor


def run_trial(N, factor_base, num_candidates, prefix_len, bound_bits, seed=1234, mr_rounds=8):
    rng = random.Random(seed)
    root = int(N ** 0.5)
    candidates = [root + i for i in range(1, num_candidates + 1)]

    ops = {k: {'div': 0, 'cert': 0} for k in ('FULL', 'HEURISTIC', 'DROPSAFE_EXACT', 'STAGED')}
    counts = {k: {'smooth_found': 0, 'false_rejects': 0} for k in ('HEURISTIC', 'DROPSAFE_EXACT', 'STAGED')}
    ground_truth = 0

    for x in candidates:
        r = x * x - N
        is_smooth, _ = trial_divide_full(r, factor_base, ops['FULL'])
        ground_truth += is_smooth

        st_h, _ = trial_divide_heuristic(r, factor_base, ops['HEURISTIC'], prefix_len, bound_bits)
        if st_h == 'REJECTED_EARLY' and is_smooth:
            counts['HEURISTIC']['false_rejects'] += 1
        if st_h == 'SMOOTH':
            counts['HEURISTIC']['smooth_found'] += 1

        st_d, _ = trial_divide_dropsafe_exact(r, factor_base, ops['DROPSAFE_EXACT'], prefix_len, rng, mr_rounds)
        if st_d == 'DROPSAFE_CERTIFIED' and is_smooth:
            counts['DROPSAFE_EXACT']['false_rejects'] += 1
        if st_d == 'SMOOTH':
            counts['DROPSAFE_EXACT']['smooth_found'] += 1

        st_s, _ = trial_divide_staged(r, factor_base, ops['STAGED'], prefix_len, bound_bits, rng, mr_rounds)
        if st_s == 'DROPSAFE_CERTIFIED' and is_smooth:
            counts['STAGED']['false_rejects'] += 1
        if st_s == 'SMOOTH':
            counts['STAGED']['smooth_found'] += 1

    return ground_truth, ops, counts


def main():
    trials = [
        (1000003 * 1009837, 200, 4000, 6, 24),
        (10007 * 10009, 100, 3000, 5, 16),
        (99991 * 99989, 300, 6000, 8, 28),
    ]
    print("=" * 78)
    print("GENERATION-2 MECHANISM TEST -- STAGED DropSafe (gate-conditional certificate)")
    print("Derived from RSA-08's Entry-001 DRIFT failure as a constraint-driven redesign")
    print("=" * 78)
    for N, fb_limit, num_candidates, prefix_len, bound_bits in trials:
        fb = sieve_primes(fb_limit)[1:]
        gt, ops, counts = run_trial(N, fb, num_candidates, prefix_len, bound_bits)
        print(f"\n--- N={N} | fb_size={len(fb)} | candidates={num_candidates} | "
              f"prefix_len={prefix_len} | bound_bits={bound_bits} | ground_truth_smooth={gt} ---")
        full_total = ops['FULL']['div']
        for k in ('HEURISTIC', 'DROPSAFE_EXACT', 'STAGED'):
            total = ops[k]['div'] + ops[k]['cert']
            savings = 100 * (1 - total / full_total)
            print(f"{k:<15} div_ops={ops[k]['div']:>8}  cert_ops={ops[k]['cert']:>6}  "
                  f"total={total:>8}  savings_vs_FULL={savings:>6.1f}%  "
                  f"smooth_found={counts[k]['smooth_found']:>4}/{gt}  "
                  f"FALSE_REJECTS={counts[k]['false_rejects']}")
        heur_total = ops['HEURISTIC']['div'] + ops['HEURISTIC']['cert']
        staged_total = ops['STAGED']['div'] + ops['STAGED']['cert']
        exact_total = ops['DROPSAFE_EXACT']['div'] + ops['DROPSAFE_EXACT']['cert']
        print(f"STAGED vs HEURISTIC: {'STAGED CHEAPER' if staged_total < heur_total else 'HEURISTIC still cheaper'} "
              f"({staged_total} vs {heur_total})")
        print(f"STAGED vs DROPSAFE_EXACT: {'STAGED CHEAPER' if staged_total < exact_total else 'no improvement'} "
              f"({staged_total} vs {exact_total}), "
              f"cert_ops cut: {ops['DROPSAFE_EXACT']['cert']} -> {ops['STAGED']['cert']} "
              f"({100*(1-ops['STAGED']['cert']/max(1,ops['DROPSAFE_EXACT']['cert'])):.1f}% fewer certificate calls)")

    print("\n" + "=" * 78)
    print("READING THIS RESULT:")
    print("- STAGED's whole point is to only pay certificate cost on the SAME candidates")
    print("  HEURISTIC would have (unsafely) rejected -- so STAGED cert_ops should be much")
    print("  lower than DROPSAFE_EXACT's, while STAGED false_rejects should stay 0 (unlike")
    print("  HEURISTIC's real false rejects, and unlike DROPSAFE_EXACT's higher cost).")
    print("- If STAGED total ops < HEURISTIC total ops: this is a genuine candidate for")
    print("  'safe AND cheaper than the classical baseline' -- report as a live finding,")
    print("  not yet a theorem, and check whether real QS/NFS implementations already do")
    print("  this (early-abort-with-fallback-certificate is a documented technique too --")
    print("  disclose overlap honestly rather than claim novelty by default).")
    print("- If STAGED still loses to HEURISTIC: the constraint C_decision(prune) < ")
    print("  E[work saved] is still not met even with gating -- the next-generation")
    print("  mechanism to try is amortizing the certificate cost ACROSS a batch of")
    print("  flagged candidates (shared modular exponentiation bases, or a cheaper")
    print("  Fermat-only pre-screen before the full Miller-Rabin), not stopping here.")
    print("=" * 78)


if __name__ == '__main__':
    main()
