"""
TRACK B, ENTRY 1 -- Relation-Acquisition mechanism search, boundary A
(candidate generation / factor-base construction).

QUESTION: "do we create candidates/test divisors the terminal factor certificate
has no chance of ever using?"

MECHANISM UNDER TEST: quadratic-residue (QR) factor-base restriction.
  For a relation x^2 - N to be divisible by an odd prime p (p not dividing x),
  N must be a quadratic residue mod p (Legendre symbol (N|p) = 1). Primes
  where N is a non-residue can NEVER appear in ANY relation's factorization,
  for ANY x -- trial-dividing by them is provably wasted work, not merely
  usually-wasted.

LABEL: CLASSICAL. This is textbook Quadratic-Sieve/Dixon factor-base
construction (used in every real implementation) -- explicitly NOT presented
as an IDM contribution. It is measured here to (a) establish the true
classical baseline strength before any IDM claim is entertained on top of it,
and (b) check whether earlier smoke tests in this research line (which all
used an UNFILTERED factor base) were comparing against a weaker classical
control than real implementations use -- a methodological correction, not a
new algorithm.

No Toledo registration, no git mutation. Disposable diagnostic.
"""


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


def acquire_relations(N, factor_base, target_relations, max_candidates=300_000):
    root = int(N ** 0.5)
    x = root + 1
    total_ops = 0
    candidates_examined = 0
    found = 0
    while found < target_relations:
        r = x * x - N
        is_smooth, _, ops = full_trial_divide(r, factor_base)
        total_ops += ops
        candidates_examined += 1
        if is_smooth:
            found += 1
        x += 1
        if candidates_examined >= max_candidates:
            return None
    return {'candidates_examined': candidates_examined, 'total_div_ops': total_ops,
            'relations_found': found}


def run(N, prime_limit, margin=4):
    all_odd_primes = sieve_primes(prime_limit)[1:]  # drop 2
    qr_primes = [p for p in all_odd_primes if legendre_symbol(N, p) == 1]

    print(f"\n--- N={N} | prime_limit={prime_limit} | "
          f"all_odd_primes={len(all_odd_primes)} | QR-primes={len(qr_primes)} "
          f"({100*len(qr_primes)/len(all_odd_primes):.1f}% of all_odd_primes, "
          f"theory predicts ~50%) ---")

    target_unfiltered = len(all_odd_primes) + margin
    target_filtered = len(qr_primes) + margin

    r_unfiltered = acquire_relations(N, all_odd_primes, target_unfiltered)
    r_filtered = acquire_relations(N, qr_primes, target_filtered)

    if r_unfiltered is None or r_filtered is None:
        print("  one arm hit max_candidates -- INCONCLUSIVE for this N, skipping ratio")
        return

    print(f"  UNFILTERED (naive, all odd primes): target={target_unfiltered} relations, "
          f"candidates_examined={r_unfiltered['candidates_examined']}, "
          f"total_div_ops={r_unfiltered['total_div_ops']}")
    print(f"  QR-FILTERED (classical, correct):   target={target_filtered} relations, "
          f"candidates_examined={r_filtered['candidates_examined']}, "
          f"total_div_ops={r_filtered['total_div_ops']}")
    ratio_ops = r_unfiltered['total_div_ops'] / r_filtered['total_div_ops']
    ratio_cand = r_unfiltered['candidates_examined'] / r_filtered['candidates_examined']
    print(f"  UNFILTERED is {ratio_ops:.2f}x more division work and "
          f"{ratio_cand:.2f}x more candidates examined than QR-FILTERED "
          f"to reach ITS OWN (larger) target.")


def main():
    print("=" * 78)
    print("TRACK B ENTRY 1 -- QR-restricted factor base (CLASSICAL baseline)")
    print("Quantifying a known classical optimization all prior smoke tests in this")
    print("research line did NOT use (they used an unfiltered factor base)")
    print("=" * 78)
    for N, prime_limit in [(1000003 * 1009837, 200), (10007 * 10009, 100), (99991 * 99989, 300)]:
        run(N, prime_limit)

    print("\n" + "=" * 78)
    print("READING THIS RESULT:")
    print("- If QR-filtering is confirmed ~50% factor-base reduction and meaningfully")
    print("  lower total div_ops even at ITS OWN smaller (easier) target: every smoke")
    print("  test run so far in this research line (RSA-08, RSA-04, RSA-05, Gen-2) used")
    print("  an unfiltered factor base and is therefore NOT compared against the real")
    print("  classical practitioner baseline -- a methodological gap, disclosed here,")
    print("  not hidden. It does not invalidate the qualitative DRIFT/BLOCK verdicts")
    print("  already reached (both arms in each of those tests used the SAME unfiltered")
    print("  factor base, so the internal A-vs-B comparisons were still fair), but the")
    print("  absolute 'HEURISTIC beats everything' baseline itself is now known to be a")
    print("  weaker classical control than what real implementations use.")
    print("- This motivates Track B Entry 2: rerun the RSA-08 family Pareto comparison")
    print("  against a QR-filtered baseline. If DropSafe/STAGED remain far behind, the")
    print("  BLOCK verdict strengthens (worse relative to a STRONGER classical control).")
    print("  If the gap narrows, that itself is new information worth investigating.")
    print("=" * 78)


if __name__ == '__main__':
    main()
