#!/usr/bin/env python3
"""Exact finite diagnostic for Adaptive Defect Capture (ADC).

For a candidate SAT predictor C and a finite support of local restriction-state
certificates z, define

    q_C(mu) = Pr_{z~mu}[ z is NOT a verified local/boundary defect ].

Thus 1-q is the capture probability.  If q<1 a defect exists.  If
1-q >= 1/p and sampling + verification costs kappa per trial, independent
sampling has expected refuter work at most kappa*p.

All arithmetic below uses Fraction.  The fixture enumerates a tiny restriction
tree only as a finite diagnostic.  Exhaustive support construction, or putting
a point mass on an already-found defect, is explicitly NOT an asymptotic
refuter construction.
"""
from __future__ import annotations

from fractions import Fraction

from sat_one_sided_audit import normalize, restrict, brute_sat
from sat_circuit_refuter_certificate import (
    local_defect_certificate,
    verify_refuter_certificate,
    const_false,
    const_true,
    no_empty_clause,
)


def enumerate_restriction_states(cnf, remaining):
    """Unique normalized states of one complete finite restriction tree."""
    seen = set()
    stack = [(normalize(cnf), tuple(remaining))]
    while stack:
        f, rem = stack.pop()
        state = (f, rem)
        if state in seen:
            continue
        seen.add(state)
        if rem:
            v = rem[0]
            tail = rem[1:]
            stack.append((normalize(restrict(f, v, False)), tail))
            stack.append((normalize(restrict(f, v, True)), tail))
    return sorted(seen, key=repr)


def exact_capture(candidate, support, integer_weights=None):
    if integer_weights is None:
        integer_weights = [1] * len(support)
    if len(integer_weights) != len(support):
        raise ValueError("weight/support length mismatch")
    if any(w < 0 for w in integer_weights):
        raise ValueError("weights must be nonnegative")

    total = sum(integer_weights)
    if total <= 0:
        return {"status": "HOLD", "reason": "zero total mass"}

    rows = []
    hit = 0
    for state, w in zip(support, integer_weights):
        f, rem = state
        cert = local_defect_certificate(f, rem)
        defect = verify_refuter_certificate(candidate, cert)
        rows.append((state, w, defect))
        if defect:
            hit += w

    miss = total - hit
    q = Fraction(miss, total)
    eps = Fraction(hit, total)
    assert q + eps == 1

    return {
        "status": "CERTIFIED",
        "total_mass": total,
        "hit_mass": hit,
        "miss_mass": miss,
        "q": q,
        "capture": eps,
        "expected_trials": None if hit == 0 else Fraction(total, hit),
        "rows": rows,
    }


def point_mass_guard(candidate, support):
    """Show why a point mass on a known defect is mathematically valid but vacuous."""
    for i, state in enumerate(support):
        cert = local_defect_certificate(*state)
        if verify_refuter_certificate(candidate, cert):
            weights = [0] * len(support)
            weights[i] = 1
            r = exact_capture(candidate, support, weights)
            assert r["q"] == 0 and r["capture"] == 1
            return r
    return None


def main():
    sat_formula = normalize(((1, 2), (-1, 2)))
    unsat_formula = normalize(((1,), (-1,)))

    cases = [
        ("exact-on-sat", sat_formula, (1, 2), brute_sat),
        ("constant-false-on-sat", sat_formula, (1, 2), const_false),
        ("constant-true-on-unsat", unsat_formula, (1, 2), const_true),
        ("cheap-no-empty-clause", unsat_formula, (1, 2), no_empty_clause),
    ]

    for name, f, rem, candidate in cases:
        support = enumerate_restriction_states(f, rem)
        r = exact_capture(candidate, support)
        print(
            f"{name}: states={len(support)} hit={r['hit_mass']} "
            f"miss={r['miss_mass']} q={r['q']} capture={r['capture']} "
            f"Etrials={r['expected_trials']}"
        )
        if name == "exact-on-sat":
            assert r["q"] == 1
            assert r["hit_mass"] == 0
        else:
            assert r["q"] < 1
            assert r["hit_mass"] > 0

    bad_support = enumerate_restriction_states(unsat_formula, (1, 2))
    vacuous = point_mass_guard(no_empty_clause, bad_support)
    assert vacuous is not None and vacuous["q"] == 0

    print("adaptive defect capture: PASS")
    print("exact gate: q<1 iff this finite weighted support assigns positive mass to a verified defect")
    print("quantitative: expected independent trials = 1/(1-q) when capture probability is fixed")
    print("NO-GO: point mass on an already-found defect is vacuous and is not an adaptive construction theorem")
    print("OPEN: construct efficiently samplable mu_C from circuit lineage with 1-q_C >= 1/poly(n)")
    print("tier=finite_diagnostic; P!=NP=NOT CLAIMED")


if __name__ == "__main__":
    main()
