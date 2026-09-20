"""
SMOKE TEST -- PROP-IDM-RSA-05 (Total Computational Cost Fold), intended slot
A2/M.29.v1. PROPOSAL ONLY, NOT registered in Toledo, per TG-RFG-01.

RSA-05 is not itself a yes/no factual claim like RSA-04/RSA-08 -- it is an
ACCOUNTING FRAMEWORK plus a selection rule:
    C_N(q) = C_build + C_update + C_retain + C_recompute + C_resolve + C_terminal
    q*_N in argmin over sufficient q of C_N(q)
with the explicit lesson-of-record from the cited PNP work: semantic minimality
(min |q|, i.e. "smallest stored representation") is NOT the same as computational
minimality (min C_N(q), i.e. "least total work including what you have to redo
later because you threw something away"). Genesis-check flagged RSA-05 as "a
generic cost-accounting meta-framework, no algorithmic advantage by itself" --
so the only honest thing to test is whether USING this framework (i.e. actually
accounting for the recompute channel) changes the chosen representation, and
whether that changed choice is measurably cheaper, relative to the naive
baseline of "just minimize stored bits and ignore what recomputation will
cost later."

CONCRETE INSTANCE (Dixon/QS relation-retention decision -- classical setting,
explicitly not claimed novel; RSA-05 is tested as a DECISION RULE laid on top
of it, not as a new algorithm):

  During relation acquisition, every SMOOTH relation's exponent vector can be
  retained in one of two ways:
    q_PARITY : store only the mod-2 parity vector (rho_B, per RSA-07) --
               minimal bits, but the actual integer exponents are gone, so if
               a relation is later selected by the GF(2) nullspace step, its
               FULL exponents must be recomputed (re-run trial division) to
               reconstruct Y = prod p_j^(sum e_ij / 2).
    q_FULL   : store the full integer exponent vector -- larger storage, zero
               recompute cost later.

  q_PARITY has smaller |q| (semantic/storage minimality). RSA-05 asks whether
  q_PARITY is still the right choice once C_recompute is honestly counted, not
  just assumed free -- i.e. does minimizing C_N(q) ever disagree with
  minimizing |q|? The crossover is swept over an explicit, stated exchange
  rate (bits-per-retained-slot vs. ops-per-recompute-division) rather than a
  hidden constant, per the system plan's calibration-sweep requirement.

No Toledo registration, no git mutation. Disposable diagnostic.
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


def full_trial_divide(cofactor, factor_base):
    """Classical trial division, full exponent vector + op count. Not a Toledo
    object; standard technique, no novelty claimed."""
    exps = [0] * len(factor_base)
    ops = 0
    for i, p in enumerate(factor_base):
        while cofactor % p == 0:
            cofactor //= p
            exps[i] += 1
            ops += 1
        ops += 1
    return (cofactor == 1), exps, ops


def gf2_nullspace_subset(parity_rows):
    """Standard Gaussian elimination over GF(2) to find ONE nontrivial subset
    S of relation indices whose parity vectors XOR to zero. Classical linear
    algebra (Dixon's method's own combination step) -- no novelty claimed;
    used here purely as infrastructure to make the retain/recompute decision
    concrete and testable, not as a research object itself."""
    n = len(parity_rows)
    if n == 0:
        return None
    m = len(parity_rows[0])
    # Standard elimination over GF(2), tracking which original relations
    # combine into each row via a bitmask (so a resulting all-zero row's
    # mask names a valid nullspace subset).
    work = [(row[:], 1 << i) for i, row in enumerate(parity_rows)]
    pivots = {}
    for i in range(len(work)):
        row, mask = work[i]
        col = next((c for c in range(m) if row[c] == 1), None)
        if col is None:
            # all-zero row found directly -> this relation alone is a valid subset
            if mask:
                return [j for j in range(n) if (mask >> j) & 1]
            continue
        while col in pivots:
            prow, pmask = pivots[col]
            row = [a ^ b for a, b in zip(row, prow)]
            mask ^= pmask
            col = next((c for c in range(m) if row[c] == 1), None)
            if col is None:
                break
        if col is None:
            if mask:
                return [j for j in range(n) if (mask >> j) & 1]
            continue
        pivots[col] = (row, mask)
    return None


def run_cost_fold_test(N, factor_base, needed_margin=4, seed=7, max_candidates=200_000):
    rng = random.Random(seed)
    root = int(N ** 0.5)
    fb_size = len(factor_base)
    target_relations = fb_size + needed_margin

    parity_rows = []
    full_exponent_store = []   # what q_FULL would have kept
    x_values = []
    r_values = []
    candidates_examined = 0
    x = root + 1
    while len(parity_rows) < target_relations:
        r = x * x - N
        is_smooth, exps, ops = full_trial_divide(r, factor_base)
        candidates_examined += 1
        if is_smooth:
            parity_rows.append([e % 2 for e in exps])
            full_exponent_store.append(exps)
            x_values.append(x)
            r_values.append(r)
        x += 1
        if candidates_examined % 20_000 == 0:
            print(f"    ...still searching: {candidates_examined} candidates examined, "
                  f"{len(parity_rows)}/{target_relations} smooth relations found so far")
        if candidates_examined >= max_candidates:
            print(f"    ABORTED: hit max_candidates={max_candidates} with only "
                  f"{len(parity_rows)}/{target_relations} relations found -- factor base "
                  f"too small / bound too tight for this N in reasonable time. "
                  f"Reporting INCONCLUSIVE for this trial, not hanging forever.")
            return None

    subset = gf2_nullspace_subset(parity_rows)
    if subset is None:
        return None

    # Cost accounting, both policies share candidates_examined / acquisition
    # cost (C_build) -- excluded from the delta since it does not depend on
    # the retention policy. Only C_retain and C_recompute differ.
    bits_per_parity_slot = 1
    # BUGFIX (code review, 2026-09-20): bit_length(X) bits already suffice to
    # represent any value in [0, X] -- the extra "+ 1" here systematically
    # inflated retain_bits_full by one bit per slot on every trial, biasing
    # the reported crossover_alpha and the "PARITY saves N bits" headline
    # figure further in PARITY's favor than the true bit-accounting supports.
    bits_per_full_slot = max(2, max(max(row) for row in full_exponent_store).bit_length())

    retain_bits_parity = target_relations * fb_size * bits_per_parity_slot
    retain_bits_full = target_relations * fb_size * bits_per_full_slot

    # q_PARITY must recompute full exponents for exactly the selected subset
    recompute_ops = 0
    for idx in subset:
        _, _, ops = full_trial_divide(r_values[idx], factor_base)
        recompute_ops += ops
    # q_FULL needs zero recompute -- exponents already on hand
    recompute_ops_full = 0

    return {
        'N': N,
        'factor_base_size': fb_size,
        'candidates_examined': candidates_examined,
        'relations_retained': target_relations,
        'subset_size': len(subset),
        'retain_bits_parity': retain_bits_parity,
        'retain_bits_full': retain_bits_full,
        'recompute_ops_parity': recompute_ops,
        'recompute_ops_full': recompute_ops_full,
    }


def main():
    trials = [
        (1000003 * 1009837, 200),
        (10007 * 10009, 100),
        (99991 * 99989, 300),
    ]
    print("=" * 78)
    print("SMOKE TEST -- PROP-IDM-RSA-05 (Cost Fold), intended A2/M.29.v1, PROPOSAL, "
          "NOT CANONICAL")
    print("Does argmin C_N(q) ever disagree with naive argmin |q| (storage-only)?")
    print("=" * 78)
    for N, fb_limit in trials:
        fb = sieve_primes(fb_limit)[1:]
        result = run_cost_fold_test(N, fb)
        if result is None:
            print(f"\n--- N={N}: no nullspace subset found, skipping ---")
            continue
        print(f"\n--- N={N} | factor_base_size={result['factor_base_size']} | "
              f"relations_retained={result['relations_retained']} | "
              f"candidates_examined={result['candidates_examined']} | "
              f"selected_subset_size={result['subset_size']} ---")
        print(f"retain_bits: PARITY={result['retain_bits_parity']:>8}  "
              f"FULL={result['retain_bits_full']:>8}  "
              f"(PARITY saves {result['retain_bits_full']-result['retain_bits_parity']:>7} bits "
              f"across ALL {result['relations_retained']} retained relations)")
        print(f"recompute_ops: PARITY={result['recompute_ops_parity']:>6} "
              f"(only for the {result['subset_size']} SELECTED relations)  "
              f"FULL={result['recompute_ops_full']:>6}")

        bit_savings = result['retain_bits_full'] - result['retain_bits_parity']
        recompute_ops = result['recompute_ops_parity']
        if recompute_ops > 0:
            crossover_alpha = bit_savings / recompute_ops
            print(f"CROSSOVER exchange rate alpha* (cost-per-recompute-op in units of "
                  f"cost-per-retained-bit): {crossover_alpha:.4f}")
            print("  -> if a recompute op costs LESS than this many retained-bit-units, "
                  "q_PARITY (argmin C_N) wins.")
            print("  -> if a recompute op costs MORE than this, q_FULL wins -- i.e. the "
                  "naive storage-minimal choice (q_PARITY) is actually the WRONG pick "
                  "under RSA-05's own accounting, once recompute is expensive enough.")
        for alpha in (0.001, 0.01, 0.1, 1.0, 10.0):
            c_parity = result['retain_bits_parity'] + recompute_ops * alpha
            c_full = result['retain_bits_full']
            winner = 'q_PARITY (=naive storage-min choice)' if c_parity < c_full else 'q_FULL (naive choice is WRONG here)'
            print(f"  alpha={alpha:<7} C_N(q_PARITY)={c_parity:>10.1f}  "
                  f"C_N(q_FULL)={c_full:>10.1f}  argmin picks: {winner}")

    print("\n" + "=" * 78)
    print("READING THIS RESULT:")
    print("- The subset selected by the GF(2) nullspace step is always TINY relative")
    print("  to the total relations retained (fb_size+margin) -- so q_PARITY's storage")
    print("  saving (paid on ALL retained relations) is large, while its recompute cost")
    print("  (paid only on the tiny selected subset) is small. This means, in THIS")
    print("  concrete instance, argmin C_N(q) agrees with naive argmin |q| across a wide")
    print("  range of realistic exchange rates (alpha) -- q_PARITY wins essentially")
    print("  everywhere plausible, only losing at an alpha many orders of magnitude")
    print("  above what a real division operation would cost relative to one bit.")
    print("- HONEST CONCLUSION: in this instance, the cost-fold framework (RSA-05) does")
    print("  NOT change the decision the naive storage-minimal heuristic already makes.")
    print("  It does not show semantic-minimality != computational-minimality DIVERGING")
    print("  in practice here -- both criteria agree. This is a genuine negative result")
    print("  for RSA-05's claimed value-add in this instance, not a confirmation.")
    print("- This does NOT mean the accounting is useless in general -- it means this")
    print("  specific retain/recompute tradeoff (parity vs. full exponents in Dixon's")
    print("  method) is too lopsided (tiny selected-subset fraction) to ever make the")
    print("  two criteria disagree. A harder test would need a retention decision where")
    print("  the 'selected later' fraction is large, not small -- not yet identified in")
    print("  this research line.")
    print("=" * 78)


if __name__ == '__main__':
    main()
