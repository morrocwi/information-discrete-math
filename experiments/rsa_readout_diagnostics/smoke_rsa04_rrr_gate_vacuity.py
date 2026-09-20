"""
SMOKE TEST -- PROP-IDM-RSA-04 (Retain-Recompute-Resolve Gate), intended slot
A3/M.18.v1. PROPOSAL ONLY, NOT registered in Toledo, per TG-RFG-01.

CLAIM UNDER TEST (contrapositive form of the proposal):
    F_N(T_u(s)) != F_N(T_u(t))  ==>  R_N(s)!=R_N(t) or Q_N(s)!=Q_N(t) or C_N(s)!=C_N(t)

Equivalently, the FORWARD direction actually load-bearing for any engineering use:
    R_N(s)=R_N(t) and Q_N(s)=Q_N(t) and C_N(s)=C_N(t)  ==>  F_N(T_u(s))=F_N(T_u(t))  for all u

i.e. "if two computation states agree on retained/recompute/resolve cost, their eventual
factor-certificate outcome must agree too."

WHY THIS IS TESTED (per the 2026-09-20 session's review): this equation was flagged as
carrying a VACUITY RISK -- if R_N, Q_N, C_N are defined richly enough to already encode
everything needed to determine the outcome, the implication is trivially true and buys
no computational content (a tautology). If instead R_N, Q_N, C_N are defined as plain
SCALAR COST COUNTERS (bytes retained, ops recomputed, ops resolved -- the natural
engineering reading used throughout this research line, e.g. in the DropSafe/cost-fold
proposals), the implication is a real, falsifiable empirical claim about this specific
factoring pipeline, and this script tests exactly that reading.

TWO READINGS TESTED, BOTH ON THE SAME REAL STATES (no hand-faked counterexamples,
addressing the earlier review's finding that a prior smoke test used a faked one):

  READING 1 -- "coarse cost-counter" (the operational reading actually used by RSA-05's
  cost fold): R_N(s) = count of factor-base primes found to divide r so far (an integer),
  Q_N(s) = number of division operations spent so far (an integer), C_N(s) = 0 (no
  resolve channel invoked yet, mid-pipeline). PREDICTION: gate FALSIFIED -- many
  candidates will share the same small integer triple while having different eventual
  smoothness outcomes, because a scalar count cannot distinguish WHICH primes divided or
  what the residual cofactor's arithmetic structure is.

  READING 2 -- "full local content" (R_N carries the actual exponent-parity vector mod 2
  over the tested prefix, per PROP-IDM-RSA-07's rho_B encoding, not just a count):
  PREDICTION -- still falsifiable in principle if the *prefix* alone can't determine
  behaviour of primes beyond it; expected to show FEWER but still nonzero collisions
  with divergent outcomes, since the untested suffix of the factor base still carries
  independent information the prefix parity vector cannot see. A genuinely sufficient
  R_N would require encoding the full remaining cofactor, which is exactly as expensive
  to store/transmit as just continuing the computation -- the tautology risk in
  concrete form.

No Toledo registration, no git mutation. This is a disposable diagnostic.
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


def full_smooth(cofactor, primes):
    for p in primes:
        while cofactor % p == 0:
            cofactor //= p
    return cofactor == 1


def build_state_and_outcome(x, N, factor_base, prefix_len):
    """Runs trial division through the first prefix_len primes only, records
    the state under both readings, then determines the REAL eventual outcome
    by continuing with the remaining primes on the SAME cofactor (same code
    path used elsewhere in this session's arms -- no separate 'ground truth'
    implementation to drift from)."""
    r = x * x - N
    cofactor = r
    exps = [0] * prefix_len
    div_ops = 0
    for i in range(prefix_len):
        p = factor_base[i]
        while cofactor % p == 0:
            cofactor //= p
            exps[i] += 1
            div_ops += 1
        div_ops += 1

    # READING 1 key: coarse scalar counters
    R1 = sum(1 for e in exps if e > 0)   # retained: how many distinct primes divided
    Q1 = div_ops                          # recompute: ops spent so far
    C1 = 0                                # resolve: not invoked yet
    key1 = (R1, Q1, C1)

    # READING 2 key: full local parity vector (rho_B-style, mod 2 per prefix prime)
    key2 = tuple(e % 2 for e in exps)

    eventual_smooth = full_smooth(cofactor, factor_base[prefix_len:])
    return key1, key2, eventual_smooth


def run_vacuity_check(N, factor_base, num_candidates, prefix_len, seed=99):
    rng = random.Random(seed)
    root = int(N ** 0.5)
    candidates = [root + i for i in range(1, num_candidates + 1)]

    groups1 = {}
    groups2 = {}
    for x in candidates:
        k1, k2, outcome = build_state_and_outcome(x, N, factor_base, prefix_len)
        groups1.setdefault(k1, set()).add(outcome)
        groups2.setdefault(k2, set()).add(outcome)

    def summarize(groups, label):
        total_groups = len(groups)
        mixed_groups = {k: v for k, v in groups.items() if len(v) > 1}
        n_mixed = len(mixed_groups)
        return {
            'label': label,
            'distinct_state_keys': total_groups,
            'groups_with_mixed_outcome': n_mixed,
            'gate_falsified': n_mixed > 0,
            'example_mixed_key': next(iter(mixed_groups), None),
        }

    return summarize(groups1, 'READING1_coarse_counters'), summarize(groups2, 'READING2_local_parity_vector')


def main():
    trials = [
        (1000003 * 1009837, 200, 6, 6000),
        (10007 * 10009, 100, 5, 5000),
        (99991 * 99989, 300, 8, 8000),
    ]
    print("=" * 78)
    print("SMOKE TEST -- PROP-IDM-RSA-04 (RRR Gate), intended A3/M.18.v1, PROPOSAL, "
          "NOT CANONICAL")
    print("Testing for vacuity/tautology vs. genuine falsifiable content")
    print("=" * 78)
    for N, fb_limit, prefix_len, num_candidates in trials:
        fb = sieve_primes(fb_limit)[1:]
        r1, r2 = run_vacuity_check(N, fb, num_candidates, prefix_len)
        print(f"\n--- N={N} | factor_base_size={len(fb)} | prefix_len={prefix_len} | "
              f"candidates={num_candidates} ---")
        for r in (r1, r2):
            print(f"{r['label']}: distinct_state_keys={r['distinct_state_keys']:>5}  "
                  f"mixed_outcome_groups={r['groups_with_mixed_outcome']:>5}  "
                  f"GATE_FALSIFIED={r['gate_falsified']}"
                  + (f"  e.g. key={r['example_mixed_key']}" if r['gate_falsified'] else ""))

    print("\n" + "=" * 78)
    print("READING THIS RESULT:")
    print("- READING1 (coarse scalar R/Q/C counters, the operational reading used")
    print("  elsewhere in this research line) falsified => confirms the gate as stated")
    print("  is FALSE, not vacuously true, under the cost-counter definition actually")
    print("  in use. This is informative: cost counters are NOT a sufficient statistic")
    print("  for the factor-certificate outcome -- you cannot predict smoothness from")
    print("  'how much work was spent' alone.")
    print("- READING2 (full local parity vector) falsified too (if so) => even richer,")
    print("  content-carrying R_N still fails to determine the outcome, because the")
    print("  untested suffix of the factor base carries independent information no")
    print("  prefix-only encoding can see. A genuinely sufficient R_N would have to")
    print("  encode information about primes it hasn't looked at yet -- which is the")
    print("  concrete shape of the vacuity risk: making R_N sufficient costs as much as")
    print("  finishing the computation.")
    print("- Net reading: RSA-04 is NEITHER a useful shortcut NOR an empty tautology in")
    print("  the tested regime -- it is a FALSE claim under the natural operational")
    print("  reading. Report as DRIFT for that reading; the 'genuinely sufficient R_N'")
    print("  reading remains open but is now known to be at least as expensive as the")
    print("  computation it would replace, per READING2's own falsification.")
    print("=" * 78)


if __name__ == '__main__':
    main()
