#!/usr/bin/env python3
"""Exact finite witness for the SAT Intervention Quotient research lane.

This script verifies the binary family described in SAT_INTERVENTION_QUOTIENT.md:

    F_b = AND_i (x_i)       if b_i = 1
                  (not x_i) if b_i = 0

All F_b are satisfiable, but the fixed intervention query rho_i := {x_i=True}
returns SAT(F_b|rho_i) = b_i.  Hence the all-intervention signature is exactly
b and there are 2^m distinct signatures.

The result is an exact finite combinatorial fixture.  It is NOT a P-vs-NP
separation; its role is to instantiate the Declaration-Bound injectivity
pattern on SAT residual queries.
"""

from __future__ import annotations

import argparse
import itertools
from typing import Dict, Iterable, Sequence, Tuple

Clause = Tuple[int, ...]
CNF = Tuple[Clause, ...]


def unit_family(bits: Sequence[bool]) -> CNF:
    """Return F_b as a unit CNF."""
    return tuple(((i,) if bit else (-i,)) for i, bit in enumerate(bits, start=1))


def restrict_cnf(cnf: CNF, assignment: Dict[int, bool]) -> CNF:
    """Apply a partial assignment exactly; an empty clause denotes contradiction."""
    out = []
    for clause in cnf:
        satisfied = False
        residual = []
        for lit in clause:
            var = abs(lit)
            if var not in assignment:
                residual.append(lit)
                continue
            value = assignment[var]
            lit_value = value if lit > 0 else (not value)
            if lit_value:
                satisfied = True
                break
            # otherwise the literal is false and is omitted
        if not satisfied:
            out.append(tuple(residual))
    return tuple(out)


def sat_exact(cnf: CNF) -> bool:
    """Brute-force SAT, used only as an exact finite checker."""
    if any(len(clause) == 0 for clause in cnf):
        return False
    variables = sorted({abs(lit) for clause in cnf for lit in clause})
    for values in itertools.product((False, True), repeat=len(variables)):
        a = dict(zip(variables, values))
        ok = True
        for clause in cnf:
            if not any((a[abs(lit)] if lit > 0 else not a[abs(lit)]) for lit in clause):
                ok = False
                break
        if ok:
            return True
    return True if not cnf else False


def intervention_signature(cnf: CNF, m: int) -> Tuple[bool, ...]:
    """Fixed query family rho_i={x_i=True}, i=1..m."""
    return tuple(sat_exact(restrict_cnf(cnf, {i: True})) for i in range(1, m + 1))


def verify_m(m: int) -> dict:
    signatures = {}
    for bits in itertools.product((False, True), repeat=m):
        cnf = unit_family(bits)
        assert sat_exact(cnf), (m, bits, cnf)
        sig = intervention_signature(cnf, m)
        assert sig == bits, (m, bits, sig)
        if sig in signatures:
            raise AssertionError(("signature collision", m, bits, signatures[sig]))
        signatures[sig] = bits

    expected = 2**m
    assert len(signatures) == expected
    return {
        "m": m,
        "formulas": expected,
        "distinct_intervention_signatures": len(signatures),
        "all_top_level_sat": True,
        "worst_case_binary_record_lower_bound_bits": m,
        "status": "exact_finite_fixture",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--max-m", type=int, default=8)
    args = p.parse_args()
    if args.max_m < 1:
        raise SystemExit("--max-m must be >= 1")

    print("SAT intervention quotient exact witness")
    print("claim boundary: restricted deferred-query retained-state lower bound; not P != NP")
    for m in range(1, args.max_m + 1):
        print(verify_m(m))
    print("PASS")


if __name__ == "__main__":
    main()
