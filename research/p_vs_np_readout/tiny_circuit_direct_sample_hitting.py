#!/usr/bin/env python3
"""Exact outer hitting support for a genuine tiny DeMorgan circuit class.

This is a finite calibration of the load-bearing ADC quantifier using actual
shared circuits rather than a hand-written heuristic DSL.

Domain
------
CNFs over variables x1,x2 are encoded by 9 clause-presence bits for

    (), (x1), (~x1), (x2), (~x2),
    (x1 v x2), (x1 v ~x2), (~x1 v x2), (~x1 v ~x2).

There are 2^9 = 512 encoded formulas.  The SAT target is computed exactly only
for constructing/checking this finite benchmark.  Local defect verification
itself uses only the candidate outputs on F,F|x=0,F|x=1 plus direct terminal
truth, matching the main refuter interface.

Candidate class
---------------
Inputs are the 9 encoding bits and their negations.  We enumerate every DAG
with at most two AND/OR gates, allowing gate 2 to reuse gate 1.  After semantic
deduplication this yields exactly 5,684 candidate Boolean functions.  The SAT
target is not realizable by this class.

Result
------
Two terminal boundary samples are forced: there is a wrong candidate hit only
by each one.  After those mandatory samples, 353 candidates remain.  No pair
of local restriction samples covers all 353 (best pair covers 349), while
three local samples do.  Therefore the minimum direct-sample hitting support
for this declared circuit class is exactly five states.

This is an exact finite diagnostic, not an asymptotic circuit lower bound.
"""
from __future__ import annotations

from itertools import product

Clause = tuple[int, ...]
Test = tuple

BANK: tuple[Clause, ...] = (
    (), (1,), (-1,), (2,), (-2,),
    (1, 2), (1, -2), (-1, 2), (-1, -2),
)
BANK_INDEX = {c: i for i, c in enumerate(BANK)}
N_FORMULAS = 1 << len(BANK)
ALL_FORMULA_BITS = (1 << N_FORMULAS) - 1


def clause_sat(clause: Clause, assignment: dict[int, bool]) -> bool:
    return any(
        (lit > 0 and assignment[abs(lit)]) or
        (lit < 0 and not assignment[abs(lit)])
        for lit in clause
    )


def sat_formula(mask: int) -> bool:
    for a1, a2 in product((False, True), repeat=2):
        a = {1: a1, 2: a2}
        if all(
            clause_sat(BANK[j], a)
            for j in range(len(BANK))
            if (mask >> j) & 1
        ):
            return True
    return False


def target_table() -> int:
    out = 0
    for mask in range(N_FORMULAS):
        if sat_formula(mask):
            out |= 1 << mask
    return out


def restrict_mask(mask: int, var: int, value: bool) -> int:
    sat_lit = var if value else -var
    false_lit = -sat_lit
    new: set[Clause] = set()
    for j, clause in enumerate(BANK):
        if not ((mask >> j) & 1):
            continue
        if not clause:
            new.add(())
            continue
        if sat_lit in clause:
            continue
        reduced = tuple(l for l in clause if l != false_lit)
        new.add(reduced)
    out = 0
    for clause in new:
        out |= 1 << BANK_INDEX[clause]
    return out


def literal_sources() -> list[int]:
    out: list[int] = []
    for bit in range(len(BANK)):
        table = 0
        for mask in range(N_FORMULAS):
            if (mask >> bit) & 1:
                table |= 1 << mask
        out.extend((table, ALL_FORMULA_BITS ^ table))
    return out


def enumerate_demorgan_at_most_two_gates() -> tuple[set[int], set[int]]:
    """Return distinct functions realizable with <=1 and <=2 AND/OR gates."""
    src = literal_sources()
    first_defs: list[tuple[int, int, str, int]] = []
    one = set(src)

    for a in range(len(src)):
        for b in range(a, len(src)):
            fa, fb = src[a], src[b]
            fand = fa & fb
            for_ = fa | fb
            one.add(fand)
            one.add(for_)
            first_defs.append((a, b, "AND", fand))
            first_defs.append((a, b, "OR", for_))

    two = set(one)
    for _a, _b, _op, first in first_defs:
        vals = src + [first]
        for i in range(len(vals)):
            for j in range(i, len(vals)):
                two.add(vals[i] & vals[j])
                two.add(vals[i] | vals[j])

    return one, two


def candidate_bit(table: int, mask: int) -> bool:
    return bool((table >> mask) & 1)


def tests() -> list[Test]:
    # At complete assignments the only canonical terminal formulas reachable
    # are TRUE (empty CNF, mask 0) and FALSE (contains empty clause, mask 1).
    out: list[Test] = [("B", 0), ("B", 1)]
    out.extend(
        ("I", mask, var)
        for mask in range(N_FORMULAS)
        for var in (1, 2)
    )
    return out


def is_defect(table: int, target: int, test: Test) -> bool:
    if test[0] == "B":
        mask = test[1]
        return candidate_bit(table, mask) != candidate_bit(target, mask)

    _, mask, var = test
    r0 = restrict_mask(mask, var, False)
    r1 = restrict_mask(mask, var, True)
    c = candidate_bit(table, mask)
    return c != (candidate_bit(table, r0) or candidate_bit(table, r1))


def coverage_masks(candidates: list[int], target: int) -> tuple[list[Test], list[int]]:
    ts: list[Test] = []
    covers: list[int] = []
    for test in tests():
        bits = 0
        for i, c in enumerate(candidates):
            if is_defect(c, target, test):
                bits |= 1 << i
        if bits:
            ts.append(test)
            covers.append(bits)
    return ts, covers


def exact_minimum_five(candidates: list[int], target: int) -> list[Test]:
    ts, covers = coverage_masks(candidates, target)
    full = (1 << len(candidates)) - 1

    # Identify candidates covered by exactly one test.  Their tests are forced.
    candidate_tests: list[list[int]] = [[] for _ in candidates]
    for ti, cover in enumerate(covers):
        x = cover
        while x:
            low = x & -x
            ci = low.bit_length() - 1
            candidate_tests[ci].append(ti)
            x -= low

    mandatory = {
        hitters[0]
        for hitters in candidate_tests
        if len(hitters) == 1
    }
    mandatory_tests = {ts[i] for i in mandatory}
    assert mandatory_tests == {("B", 0), ("B", 1)}, mandatory_tests

    remaining = full
    for i in mandatory:
        remaining &= ~covers[i]
    assert remaining.bit_count() == 353, remaining.bit_count()

    # Prove that two additional tests cannot finish the cover.
    local = [i for i in range(len(covers)) if i not in mandatory]
    best_pair = 0
    best_pair_tests: tuple[Test, Test] | None = None
    for pos, i in enumerate(local):
        ci = covers[i] & remaining
        for j in local[pos + 1:]:
            covered = (ci | (covers[j] & remaining)).bit_count()
            if covered > best_pair:
                best_pair = covered
                best_pair_tests = (ts[i], ts[j])
    assert best_pair == 349, (best_pair, best_pair_tests)
    assert best_pair < remaining.bit_count()

    # Exhibit three local tests that do finish the residual cover.
    witness_local = [
        ("I", 6, 1),
        ("I", 24, 2),
        ("I", 480, 1),
    ]
    chosen = list(mandatory_tests) + witness_local
    index = {t: i for i, t in enumerate(ts)}
    hit = 0
    for t in chosen:
        hit |= covers[index[t]]
    assert hit == full
    assert len(chosen) == 5
    return chosen


def main() -> None:
    target = target_table()
    # Exact self-reduction sanity check on the finite domain.
    for mask in range(N_FORMULAS):
        for var in (1, 2):
            lhs = candidate_bit(target, mask)
            rhs = (
                candidate_bit(target, restrict_mask(mask, var, False)) or
                candidate_bit(target, restrict_mask(mask, var, True))
            )
            assert lhs == rhs, (mask, var)

    one, two = enumerate_demorgan_at_most_two_gates()
    src = set(literal_sources())
    assert len(src) == 18
    assert len(one) == 308, len(one)
    assert len(two) == 5684, len(two)
    assert target not in two

    candidates = sorted(two)
    support = exact_minimum_five(candidates, target)

    print(f"encoded_formulas={N_FORMULAS} SAT_yes={target.bit_count()}")
    print(f"literal_sources={len(src)} <=1gate_functions={len(one)} <=2gate_functions={len(two)}")
    print("SAT target is not in the <=2-gate class")
    print("mandatory boundary samples: ('B',0), ('B',1)")
    print("after boundaries: 353 candidates remain")
    print("best two local samples cover 349/353 -> four total samples impossible")
    print(f"exact five-sample support={support}")
    print("tiny genuine-circuit direct-sample hitting: PASS")
    print("minimum support size = 5 for this declared finite class")
    print("tier=exact_finite_diagnostic; asymptotic unrestricted constructor=OPEN")
    print("SAT notin P/poly=NOT CLAIMED; P!=NP=NOT CLAIMED")


if __name__ == "__main__":
    main()
