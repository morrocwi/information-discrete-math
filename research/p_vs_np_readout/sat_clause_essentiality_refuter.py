#!/usr/bin/env python3
"""Constructive essential-input refuter for clause-presence SAT encodings.

For n Boolean variables let the raw encoding have one bit for every
non-tautological clause.  A clause is represented by a vector in {-1,0,+1}^n:
0 means absent, +1 means x_i, -1 means ~x_i.  Thus the encoding has exactly
m=3^n clause-presence bits, including the empty clause.

Every one of these m input bits is essential for SAT.  Given a clause C, choose
an assignment a that falsifies every literal of C (arbitrary false values on
variables absent from C).  Let F_a be the n unit clauses fixing the variables
to a.  Then

    F_a             is SAT (indeed has the unique assignment a),
    F_a union {C}   is UNSAT,

and the two raw encodings differ in exactly the C bit.

Therefore any candidate circuit that does not syntactically mention input C
has identical output on this pair and is wrong on at least one member.  A
fan-in-2 straight-line DAG with s gates plus a possible direct-input output has
at most 2s+1 input-reference slots, so m essential bits imply

    m <= 2s+1.

This gives an oracle-free constructive LINEAR lower-bound baseline in the raw
encoding length m.  It is not superpolynomial and does not prove SAT notin
P/poly or P != NP.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import random

Clause = tuple[int, ...]
Formula = frozenset[int]  # clause indices present in the raw encoding


def all_clauses(n: int) -> list[Clause]:
    clauses: list[Clause] = []
    for states in product((-1, 0, 1), repeat=n):
        clause = tuple(
            (i + 1) if s == 1 else -(i + 1)
            for i, s in enumerate(states)
            if s != 0
        )
        clauses.append(clause)
    assert len(clauses) == 3 ** n
    assert len(set(clauses)) == len(clauses)
    return clauses


def falsifying_assignment(clause: Clause, n: int) -> dict[int, bool]:
    out = {i: False for i in range(1, n + 1)}
    for lit in clause:
        out[abs(lit)] = lit < 0
    return out


def unit_clause(value: bool, var: int) -> Clause:
    return (var,) if value else (-var,)


def essential_pair(clauses: list[Clause], clause_index: int, n: int) -> tuple[Formula, Formula, dict[int, bool]]:
    target_clause = clauses[clause_index]
    a = falsifying_assignment(target_clause, n)
    index = {c: i for i, c in enumerate(clauses)}
    base = frozenset(index[unit_clause(a[i], i)] for i in range(1, n + 1))
    assert clause_index not in base
    plus = frozenset(set(base) | {clause_index})
    assert base ^ plus == {clause_index}
    return base, plus, a


def clause_value(clause: Clause, a: dict[int, bool]) -> bool:
    return any(
        (lit > 0 and a[abs(lit)]) or
        (lit < 0 and not a[abs(lit)])
        for lit in clause
    )


def formula_value(formula: Formula, clauses: list[Clause], a: dict[int, bool]) -> bool:
    return all(clause_value(clauses[j], a) for j in formula)


def brute_sat(formula: Formula, clauses: list[Clause], n: int) -> bool:
    for bits in product((False, True), repeat=n):
        a = {i + 1: bits[i] for i in range(n)}
        if formula_value(formula, clauses, a):
            return True
    return False


@dataclass(frozen=True)
class Ref:
    kind: str  # "I" or "G"
    index: int


@dataclass(frozen=True)
class Gate:
    op: str  # "AND" or "OR"
    left: Ref
    right: Ref


@dataclass
class Program:
    gates: list[Gate]
    output: Ref

    def mentioned_inputs(self) -> set[int]:
        out: set[int] = set()
        for g in self.gates:
            for r in (g.left, g.right):
                if r.kind == "I":
                    out.add(r.index)
        if self.output.kind == "I":
            out.add(self.output.index)
        return out

    def evaluate(self, formula: Formula) -> bool:
        vals: list[bool] = []

        def deref(r: Ref) -> bool:
            if r.kind == "I":
                return r.index in formula
            if r.kind == "G":
                return vals[r.index]
            raise ValueError(r.kind)

        for i, g in enumerate(self.gates):
            assert g.left.kind != "G" or g.left.index < i
            assert g.right.kind != "G" or g.right.index < i
            a = deref(g.left)
            b = deref(g.right)
            vals.append(a and b if g.op == "AND" else a or b)
        return deref(self.output)


def random_program(m: int, s: int, rng: random.Random) -> Program:
    if s == 0:
        return Program([], Ref("I", rng.randrange(m)))
    gates: list[Gate] = []
    for i in range(s):
        refs = [Ref("I", j) for j in range(m)] + [Ref("G", j) for j in range(i)]
        left = rng.choice(refs)
        right = rng.choice(refs)
        op = rng.choice(("AND", "OR"))
        gates.append(Gate(op, left, right))
    return Program(gates, Ref("G", s - 1))


def refute_omitted_clause(program: Program, clauses: list[Clause], n: int) -> dict:
    mentioned = program.mentioned_inputs()
    omitted = next((j for j in range(len(clauses)) if j not in mentioned), None)
    if omitted is None:
        return {"status": "HOLD", "reason": "all clause bits syntactically mentioned"}

    base, plus, witness = essential_pair(clauses, omitted, n)
    c0 = program.evaluate(base)
    c1 = program.evaluate(plus)
    assert c0 == c1, "a syntactically absent input changed the candidate output"

    # Target labels are known by construction; brute SAT below is only an
    # independent finite sanity check and is not needed by the refuter.
    target_base = True
    target_plus = False
    assert formula_value(base, clauses, witness)
    assert not clause_value(clauses[omitted], witness)
    assert brute_sat(base, clauses, n) == target_base
    assert brute_sat(plus, clauses, n) == target_plus

    mismatch = "base-SAT" if c0 is False else "plus-UNSAT"
    return {
        "status": "REFUTED",
        "omitted_clause_index": omitted,
        "omitted_clause": clauses[omitted],
        "candidate_pair_value": c0,
        "mismatch": mismatch,
        "mentioned_inputs": len(mentioned),
        "gate_count": len(program.gates),
    }


def audit(n_max: int = 5, samples_per_n: int = 25) -> None:
    rng = random.Random(20260911)
    for n in range(1, n_max + 1):
        clauses = all_clauses(n)
        m = len(clauses)

        # Exhaustively verify essentiality construction for the declared small
        # finite resolutions.
        for j in range(m):
            base, plus, a = essential_pair(clauses, j, n)
            assert formula_value(base, clauses, a)
            assert not clause_value(clauses[j], a)
            assert brute_sat(base, clauses, n)
            assert not brute_sat(plus, clauses, n)

        # Test arbitrary shared straight-line programs safely below the slot
        # threshold.  The formal theorem covers the structural bound; these
        # programs exercise the concrete refuter.
        max_s = min(12, max(0, (m - 2) // 2))
        for _ in range(samples_per_n):
            s = rng.randrange(max_s + 1) if max_s else 0
            prog = random_program(m, s, rng)
            assert len(prog.mentioned_inputs()) <= 2 * s + 1
            assert m > 2 * s + 1
            out = refute_omitted_clause(prog, clauses, n)
            assert out["status"] == "REFUTED", (n, s, out)

        print(
            f"n={n} clause_bits=m={m} tested_programs={samples_per_n} "
            f"constructive_threshold: m>2s+1 => refuter"
        )


def main() -> None:
    audit()
    print("SAT clause-essentiality lineage refuter: PASS")
    print("every non-tautological clause-presence bit has an explicit SAT/UNSAT essential pair")
    print("sharing-aware structural consequence: m essential bits imply m <= 2s+1")
    print("therefore s >= (m-1)/2 in this raw encoding")
    print("tier=finite_diagnostic + formal structural kernel; lower bound is linear in input length")
    print("SAT notin P/poly=NOT CLAIMED; P!=NP=NOT CLAIMED")


if __name__ == "__main__":
    main()
