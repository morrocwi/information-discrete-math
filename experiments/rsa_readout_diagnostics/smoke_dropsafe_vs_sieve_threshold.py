"""
SMOKE TEST — DropSafe (PROP-IDM-RSA-08, intended slot A3/M.20.v1) vs classical
early-abort / sieve-threshold heuristic, on Dixon-style smooth-relation acquisition.

STATUS BANNER (mandatory, per Toledo EQUATION_SOURCE_POLICY.md / TG-RFG-01):
  PROP-IDM-RSA-08 is PROPOSAL ONLY. It is NOT registered in Toledo. Its intended slot
  A3/M.20.v1 is a reservation target, not an assigned code. Nothing in this script's
  output may be cited as a canonical Toledo equation or a proved theorem.

CORRECTION (code review, 2026-09-20): the "certificate" below is Miller-Rabin, a
PROBABILISTIC primality test with a bounded, nonzero false-positive rate -- NOT a
deterministic proof. Comments/output below describing it as "exact," "proof-carrying,"
or "provably safe" mean "safe conditional on the Miller-Rabin result being correct,"
not "mathematically proven with certainty." "0 false rejects observed" is the accurate
claim; "proven error bound = 0" was not and has been corrected in the printed output.

WHAT THIS TESTS
  The bottleneck identified in prior smoke tests is smooth-relation ACQUISITION, not
  gcd or linear algebra. The exact question this script targets (per the 2026-09-20
  session's narrowed falsification target):

      Does an IDM-style "DropSafe" early-rejection rule reduce the TOTAL WORK of
      smooth-relation acquisition relative to a classical sieve/early-abort
      heuristic, WITHOUT just moving cost from "storage" to "recomputation", and
      WITHOUT ever incorrectly dropping a candidate that was actually smooth
      (a false reject is a correctness violation, not a tradeoff)?

THREE ARMS, SAME CODE PATH (shared relation generator + shared factor base):
  A. FULL       — baseline: full trial division against the whole factor base, no
                  early exit. This is the reference for correctness (ground truth).
  B. HEURISTIC  — classical numeric-threshold early abort (Pomerance-style): after
                  dividing by a prefix of the factor base, bail out if the residual
                  cofactor already exceeds a size bound that makes full smoothness
                  implausible within budget. This is a HEURISTIC: it can be tuned to
                  never false-reject on THIS factor base/bound combination, but the
                  criterion itself is not a certificate — it is a size guess.
  C. DROPSAFE   — the IDM-style EXACT criterion: at any point where the residual
                  cofactor is a probable prime STRICTLY GREATER than the largest
                  factor-base prime, no further division can ever reduce it to 1
                  (its only prime factor is itself, which is outside the factor
                  base) — so DropSafe_N(candidate | state) holds with a PROOF-CARRYING
                  witness (a primality certificate), not a size guess. This is
                  reported as an exact analogue of what real QS/GNFS implementations
                  already call "early abort with a primality check" — the adversarial
                  hypothesis is that this DropSafe formalization is NOT NEW, it is a
                  restatement of a known implementation trick, and should show ZERO
                  false rejects and comparable-or-worse total operation count to a
                  well-tuned heuristic, not a growth-law improvement.

COST MODEL (measured, not modeled): every modular division/modulo operation against
a factor-base prime is one unit of "division work". Every Miller-Rabin round on the
cofactor is one unit of "certificate work". Both are counted separately so a result
can never hide a cost shift behind an aggregate number (this is the R_N/Q_N/C_N
attribution discipline from the synthesized system plan).

This script performs NO Toledo registration, NO git mutation, and is not part of any
canonical claim. It is a disposable diagnostic; failure is a valid, reportable result.
"""

import random

# ---------------------------------------------------------------------------
# Deterministic PRNG seeding note: no Math.random()/Date.now() ban applies here
# (this is a plain Python script run directly, not a Workflow script). Seeded
# explicitly below for reproducibility.
# ---------------------------------------------------------------------------

def sieve_primes(limit):
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if is_p[i]:
            for j in range(i * i, limit + 1, i):
                is_p[j] = False
    return [i for i, v in enumerate(is_p) if v]


def miller_rabin(n, rounds, rng, ops_counter):
    """Probable-primality test. Each modular exponentiation round counted as
    'certificate work' via ops_counter['cert']. Not a Toledo object — standard
    Miller-Rabin, cited as classical, no novelty claimed."""
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
    """Arm A: full trial division against the entire factor base. No early exit.
    Returns (is_smooth, exponent_vector)."""
    exps = [0] * len(factor_base)
    for i, p in enumerate(factor_base):
        while cofactor % p == 0:
            cofactor //= p
            exps[i] += 1
            ops['div'] += 1
        ops['div'] += 1  # the failing trial that ends the while-loop for this prime
    return cofactor == 1, exps


def trial_divide_heuristic(cofactor, factor_base, ops, prefix_len, bound_bits):
    """Arm B: classical numeric-threshold early abort. Divide by the first
    prefix_len primes; if the residual's bit length still exceeds bound_bits,
    reject early (HEURISTIC — a size guess, not a certificate). Otherwise
    continue trial division over the remaining primes."""
    exps = [0] * len(factor_base)
    for i in range(prefix_len):
        p = factor_base[i]
        while cofactor % p == 0:
            cofactor //= p
            exps[i] += 1
            ops['div'] += 1
        ops['div'] += 1
    if cofactor > 1 and cofactor.bit_length() > bound_bits:
        return 'REJECTED_EARLY', exps, cofactor
    for i in range(prefix_len, len(factor_base)):
        p = factor_base[i]
        while cofactor % p == 0:
            cofactor //= p
            exps[i] += 1
            ops['div'] += 1
        ops['div'] += 1
    return ('SMOOTH' if cofactor == 1 else 'NOT_SMOOTH'), exps, cofactor


def trial_divide_dropsafe(cofactor, factor_base, ops, prefix_len, rng, mr_rounds=8):
    """Arm C: IDM DropSafe -- exact certificate-based early rejection.
    After the same prefix as the heuristic arm, if the residual cofactor is a
    probable prime strictly greater than the largest factor-base prime, its
    ONLY possible remaining factor is itself, which lies outside the factor
    base -- so it is EXACTLY, provably impossible to reach cofactor==1 by
    further division. This is DropSafe_N(candidate | state) with the
    primality certificate AS the finite witness (ties back to A3/M.01
    witness_sound's shape: a witness that must be checkable, not guessed)."""
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
            # certified: cofactor's only factor is itself, and it's outside the
            # factor base -> exact, proof-carrying DropSafe verdict.
            return 'DROPSAFE_CERTIFIED', exps, cofactor
    for i in range(prefix_len, len(factor_base)):
        p = factor_base[i]
        while cofactor % p == 0:
            cofactor //= p
            exps[i] += 1
            ops['div'] += 1
        ops['div'] += 1
    return ('SMOOTH' if cofactor == 1 else 'NOT_SMOOTH'), exps, cofactor


def trial_divide_dropsafe_bounded(cofactor, factor_base, ops, prefix_len, rng, mr_rounds):
    """Arm D: BOUNDED-ERROR DropSafe variant -- 'trade safety a little bit'.

    Same certificate mechanism as Arm C (a probable-primality witness on the
    residual cofactor licenses an early, provably-motivated rejection), but
    with FEWER Miller-Rabin rounds. This is not a numeric-threshold guess like
    Arm B -- it is the SAME exact mechanism with a smaller, but STATED and
    computable, worst-case error probability: for a composite n and k
    independent random Miller-Rabin witnesses, the probability that ALL k
    rounds falsely report 'probably prime' is bounded above by 4^-k (the
    standard Monier-Rabin bound), independent of the numeric size of n.

    This is the honest middle ground the review flagged as untested: unlike
    Arm B's threshold (no probabilistic guarantee, and it DID false-reject
    smooth candidates in the earlier run), this arm's false-reject probability
    is quantified and shrinks geometrically with mr_rounds, at a correctly
    modelled, reportable division of cert cost vs error-bound tradeoff.
    """
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
            return 'DROPSAFE_CERTIFIED', exps, cofactor
    for i in range(prefix_len, len(factor_base)):
        p = factor_base[i]
        while cofactor % p == 0:
            cofactor //= p
            exps[i] += 1
            ops['div'] += 1
        ops['div'] += 1
    return ('SMOOTH' if cofactor == 1 else 'NOT_SMOOTH'), exps, cofactor


def run_smoke_test(N, factor_base, num_candidates, prefix_len, bound_bits, seed=1234,
                    bounded_rounds=(1, 2, 4)):
    rng = random.Random(seed)
    root = int(N ** 0.5)
    candidates = [root + i for i in range(1, num_candidates + 1)]

    ops_full = {'div': 0, 'cert': 0}
    ops_heur = {'div': 0, 'cert': 0}
    ops_drop = {'div': 0, 'cert': 0}
    ops_bounded = {k: {'div': 0, 'cert': 0} for k in bounded_rounds}

    ground_truth_smooth = []
    heur_false_reject = 0
    heur_smooth_found = 0
    drop_false_reject = 0
    drop_smooth_found = 0
    bounded_false_reject = {k: 0 for k in bounded_rounds}
    bounded_smooth_found = {k: 0 for k in bounded_rounds}

    for x in candidates:
        r = x * x - N

        # A. FULL (ground truth)
        is_smooth, _ = trial_divide_full(r, factor_base, ops_full)
        ground_truth_smooth.append(is_smooth)

        # B. HEURISTIC
        status_b, _, _ = trial_divide_heuristic(r, factor_base, ops_heur, prefix_len, bound_bits)
        if status_b == 'REJECTED_EARLY' and is_smooth:
            heur_false_reject += 1
        if status_b == 'SMOOTH':
            heur_smooth_found += 1

        # C. DROPSAFE (exact-strength certificate, mr_rounds=8)
        status_c, _, _ = trial_divide_dropsafe(r, factor_base, ops_drop, prefix_len, rng)
        if status_c == 'DROPSAFE_CERTIFIED' and is_smooth:
            drop_false_reject += 1  # would be a CORRECTNESS BUG, not just a cost issue
        if status_c == 'SMOOTH':
            drop_smooth_found += 1

        # D. DROPSAFE_BOUNDED -- same mechanism, fewer rounds, quantified error bound
        for k in bounded_rounds:
            status_d, _, _ = trial_divide_dropsafe_bounded(r, factor_base, ops_bounded[k], prefix_len, rng, k)
            if status_d == 'DROPSAFE_CERTIFIED' and is_smooth:
                bounded_false_reject[k] += 1
            if status_d == 'SMOOTH':
                bounded_smooth_found[k] += 1

    total_smooth = sum(ground_truth_smooth)

    result = {
        'N': N,
        'num_candidates': num_candidates,
        'factor_base_size': len(factor_base),
        'ground_truth_smooth_count': total_smooth,
        'FULL':      {'div_ops': ops_full['div'], 'cert_ops': ops_full['cert']},
        'HEURISTIC': {'div_ops': ops_heur['div'], 'cert_ops': ops_heur['cert'],
                      'smooth_found': heur_smooth_found, 'false_rejects': heur_false_reject},
        'DROPSAFE':  {'div_ops': ops_drop['div'], 'cert_ops': ops_drop['cert'],
                      'smooth_found': drop_smooth_found, 'false_rejects': drop_false_reject},
        'DROPSAFE_BOUNDED': {},
    }
    for k in bounded_rounds:
        result['DROPSAFE_BOUNDED'][k] = {
            'div_ops': ops_bounded[k]['div'],
            'cert_ops': ops_bounded[k]['cert'],
            'smooth_found': bounded_smooth_found[k],
            'false_rejects': bounded_false_reject[k],
            'theoretical_worst_case_error_bound': 4.0 ** (-k),
        }
    return result


def main():
    trials = [
        # (N, factor_base_limit, num_candidates, prefix_len, bound_bits)
        (1000003 * 1009837, 200, 4000, 6, 24),
        (10007 * 10009, 100, 3000, 5, 16),
        (99991 * 99989, 300, 6000, 8, 28),
    ]
    print("=" * 78)
    print("SMOKE TEST -- PROP-IDM-RSA-08 (DropSafe, PROPOSAL, intended A3/M.20.v1, "
          "NOT CANONICAL)")
    print("vs classical numeric-threshold early-abort heuristic")
    print("=" * 78)
    for N, fb_limit, num_candidates, prefix_len, bound_bits in trials:
        fb = sieve_primes(fb_limit)[1:]  # drop 2 (r = x^2 - N is handled as-is; keep simple)
        result = run_smoke_test(N, fb, num_candidates, prefix_len, bound_bits)
        print(f"\n--- N={N} | factor_base_size={result['factor_base_size']} | "
              f"candidates={num_candidates} | prefix_len={prefix_len} | bound_bits={bound_bits} ---")
        print(f"ground truth smooth count (FULL, reference): {result['ground_truth_smooth_count']}")
        print(f"FULL       div_ops={result['FULL']['div_ops']:>8}  cert_ops={result['FULL']['cert_ops']:>6}")
        h = result['HEURISTIC']
        print(f"HEURISTIC  div_ops={h['div_ops']:>8}  cert_ops={h['cert_ops']:>6}  "
              f"smooth_found={h['smooth_found']:>4}  FALSE_REJECTS={h['false_rejects']}")
        d = result['DROPSAFE']
        print(f"DROPSAFE(exact,8rd) div_ops={d['div_ops']:>8}  cert_ops={d['cert_ops']:>6}  "
              f"smooth_found={d['smooth_found']:>4}  FALSE_REJECTS={d['false_rejects']}")
        savings_h = 100 * (1 - h['div_ops'] / result['FULL']['div_ops'])
        total_d = d['div_ops'] + d['cert_ops']
        total_h = h['div_ops'] + h['cert_ops']
        savings_d_total = 100 * (1 - total_d / result['FULL']['div_ops'])
        print(f"HEURISTIC total-op savings vs FULL: {savings_h:.1f}%  "
              f"(false_rejects={h['false_rejects']}, NO error bound stated)")
        # BUGFIX (code review, 2026-09-20): the certificate is Miller-Rabin, a
        # PROBABILISTIC primality test (bounded, nonzero false-positive rate),
        # not a deterministic proof -- "PROVEN error bound = 0" overstated the
        # guarantee. Corrected to describe what was actually observed.
        print(f"DROPSAFE(exact) TOTAL savings vs FULL: {savings_d_total:.1f}%  "
              f"(false_rejects={d['false_rejects']} observed; Miller-Rabin is "
              f"probabilistic, not a deterministic proof -- see calibrate_costs.py "
              f"for the round count used)")
        print(f"DROPSAFE(exact) total ops ({total_d}) vs HEURISTIC total ops ({total_h}): "
              f"{'DROPSAFE cheaper' if total_d < total_h else 'HEURISTIC cheaper or tied'}")

        print(f"\n{'rounds':>7} {'div_ops':>9} {'cert_ops':>9} {'total_ops':>10} "
              f"{'savings_vs_FULL':>16} {'false_rejects':>14} {'worst_case_bound':>17}")
        for k, b in result['DROPSAFE_BOUNDED'].items():
            tot = b['div_ops'] + b['cert_ops']
            sav = 100 * (1 - tot / result['FULL']['div_ops'])
            print(f"{k:>7} {b['div_ops']:>9} {b['cert_ops']:>9} {tot:>10} "
                  f"{sav:>15.1f}% {b['false_rejects']:>14} {b['theoretical_worst_case_error_bound']:>17.6f}")
        cheapest_k = min(result['DROPSAFE_BOUNDED'], key=lambda k: result['DROPSAFE_BOUNDED'][k]['div_ops'] + result['DROPSAFE_BOUNDED'][k]['cert_ops'])
        cheapest_tot = result['DROPSAFE_BOUNDED'][cheapest_k]['div_ops'] + result['DROPSAFE_BOUNDED'][cheapest_k]['cert_ops']
        print(f"cheapest bounded variant: rounds={cheapest_k}, total_ops={cheapest_tot}  "
              f"vs HEURISTIC total_ops={total_h}: "
              f"{'BOUNDED cheaper' if cheapest_tot < total_h else 'HEURISTIC still cheaper or tied'}")

    print("\n" + "=" * 78)
    print("READING THIS RESULT (readout-not-truth discipline -- state, don't spin):")
    print("- If DROPSAFE false_rejects > 0 anywhere above: the 'exact certificate' claim")
    print("  is FALSIFIED as stated -- report as DRIFT, do not re-tune silently to hide it.")
    print("- If DROPSAFE total ops (div+cert) are NOT below HEURISTIC's total ops: the")
    print("  IDM formalization bought no measurable advantage over the classical")
    print("  heuristic here -- it merely renamed 'early abort' with a primality check,")
    print("  which is itself a KNOWN classical implementation trick (not novel).")
    print("- A win only counts if DROPSAFE's TOTAL cost (not div_ops alone) beats a")
    print("  FAIRLY TUNED heuristic at the SAME false_reject rate (0, here).")
    print("=" * 78)


if __name__ == '__main__':
    main()
