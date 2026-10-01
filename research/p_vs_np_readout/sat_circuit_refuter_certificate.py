#!/usr/bin/env python3
"""Local, oracle-free refuter certificates for SAT candidates.

A candidate C over normalized CNF restriction states is globally compatible
with SAT only if it satisfies two finite local conditions:

  INTERNAL: C(F,rem) = C(F|x=0,tail) OR C(F|x=1,tail)
  BOUNDARY: when rem is empty, C(F,()) equals direct syntactic leaf truth.

A certificate contains only one state (plus its next split variable when
internal).  Verification evaluates C at at most three states and never calls a
SAT solver.  Exhaustive search is used only in the finite diagnostic to show
that any wrong root labeling of a complete restriction tree exposes such a
certificate somewhere.

This is a certificate/checker and localization diagnostic, not an efficient
algorithm for finding a defect in arbitrary circuits and not a P != NP proof.
"""
from __future__ import annotations

from typing import Callable

from sat_one_sided_audit import normalize, restrict, leaf_truth, brute_sat

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Candidate = Callable[[CNF, tuple[int, ...]], bool]


def local_defect_certificate(cnf: CNF, remaining: tuple[int, ...]) -> dict:
    f = normalize(cnf)
    rem = tuple(remaining)
    if rem:
        return {"kind": "internal", "cnf": f, "remaining": rem, "variable": rem[0]}
    return {"kind": "boundary", "cnf": f, "remaining": rem}


def verify_refuter_certificate(candidate: Candidate, cert: dict) -> bool:
    try:
        f = normalize(tuple(tuple(c) for c in cert["cnf"]))
        rem = tuple(cert["remaining"])
    except Exception:
        return False

    kind = cert.get("kind")
    c = bool(candidate(f, rem))

    if kind == "boundary":
        return rem == () and c != leaf_truth(f)

    if kind != "internal" or not rem:
        return False
    v = cert.get("variable")
    if v != rem[0]:
        return False
    tail = rem[1:]
    f0 = normalize(restrict(f, v, False))
    f1 = normalize(restrict(f, v, True))
    c0 = bool(candidate(f0, tail))
    c1 = bool(candidate(f1, tail))
    return c != (c0 or c1)


def find_refuter_exhaustive(cnf: CNF, remaining: tuple[int, ...], candidate: Candidate):
    """Finite diagnostic only: depth-first search for one local certificate."""
    f = normalize(cnf)
    rem = tuple(remaining)
    cert = local_defect_certificate(f, rem)
    if verify_refuter_certificate(candidate, cert):
        return cert
    if not rem:
        return None
    v = rem[0]
    tail = rem[1:]
    left = find_refuter_exhaustive(restrict(f, v, False), tail, candidate)
    if left is not None:
        return left
    return find_refuter_exhaustive(restrict(f, v, True), tail, candidate)


def root_truth(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    return brute_sat(normalize(cnf), tuple(remaining))


def const_false(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    return False


def const_true(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    return True


def no_empty_clause(cnf: CNF, remaining: tuple[int, ...]) -> bool:
    return not any(len(c) == 0 for c in normalize(cnf))


def main() -> None:
    sat_formula = normalize(((1, 2), (-1, 2)))
    unsat_formula = normalize(((1,), (-1,)))

    fixtures = [
        ("exact-sat", sat_formula, (1, 2), brute_sat, False),
        ("exact-unsat", unsat_formula, (1, 2), brute_sat, False),
        ("constant-false-on-sat", sat_formula, (1, 2), const_false, True),
        ("constant-true-on-unsat", unsat_formula, (1, 2), const_true, True),
        ("cheap-no-empty-clause", unsat_formula, (1, 2), no_empty_clause, True),
    ]

    for name, f, rem, candidate, expect_defect in fixtures:
        cert = find_refuter_exhaustive(f, rem, candidate)
        wrong_at_root = bool(candidate(f, rem)) != root_truth(f, rem)
        if expect_defect:
            assert cert is not None, (name, "expected defect")
            assert verify_refuter_certificate(candidate, cert), (name, cert)
        else:
            assert cert is None, (name, cert)
        if wrong_at_root:
            assert cert is not None, (name, "wrong root must localize")
        print(
            f"{name}: wrong_root={wrong_at_root} "
            f"certificate={cert} verified={cert is not None and verify_refuter_certificate(candidate, cert)}"
        )

    # Tampering guard: the same state with a wrong split variable is rejected.
    good = find_refuter_exhaustive(unsat_formula, (1, 2), no_empty_clause)
    assert good is not None
    if good["kind"] == "internal":
        bad = dict(good)
        bad["variable"] = 99
        assert not verify_refuter_certificate(no_empty_clause, bad)

    print("SAT circuit refuter certificate: PASS")
    print("certificate verification uses <=3 candidate evaluations and direct leaf truth only")
    print("finding a certificate for every polynomial-size candidate remains OPEN")
    print("tier=finite_diagnostic; P!=NP=NOT CLAIMED")


if __name__ == "__main__":
    main()
