#!/usr/bin/env python3
"""Exact finite SAT completion diagnostic through the Readout-Universe lens.

This file is deliberately restricted:

* finite CNF only;
* exact Boolean arithmetic only;
* maker constructs either a SAT witness or a DPLL-style UNSAT subcube cover;
* checker independently verifies the returned object;
* no claim about unrestricted polynomial-time SAT algorithms is made.

The purpose is to instantiate the generic finite completion theorem:

    complete cover + local obstruction on every cell -> exact NO readout.

A cell is a partial assignment (subcube).  It is locally rejected when one
clause is already falsified by every total assignment extending that subcube.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable, Sequence

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Cube = tuple[bool | None, ...]
Assignment = tuple[bool, ...]


SAT_BASE: CNF = (
    (-1, -3, -4),
    (-1, -3, 4),
    (-1, -2, -4),
    (-1, 3, 4),
    (1, -2, -3),
    (1, 2, 3),
    (1, 2, 4),
    (1, 3, -4),
)

UNSAT_BASE: CNF = (
    (-1, -2, -3),
    (-1, -2, 3),
    (1, -2, -4),
    (1, -2, 4),
    (2, -3, -4),
    (2, -3, 4),
    (2, 3, -4),
    (2, 3, 4),
)


def variable_count(cnf: CNF) -> int:
    return max((abs(lit) for clause in cnf for lit in clause), default=0)


def literal_value(lit: int, assignment: Sequence[bool]) -> bool:
    value = bool(assignment[abs(lit) - 1])
    return value if lit > 0 else not value


def clause_value(clause: Clause, assignment: Assignment) -> bool:
    return any(literal_value(lit, assignment) for lit in clause)


def formula_value(cnf: CNF, assignment: Assignment) -> bool:
    return all(clause_value(clause, assignment) for clause in cnf)


def cube_extends(cube: Cube, assignment: Assignment) -> bool:
    return all(bit is None or bit == assignment[i] for i, bit in enumerate(cube))


def cube_falsifies_clause(cube: Cube, clause: Clause) -> bool:
    """True iff every total extension of cube falsifies this clause.

    A clause is forced false exactly when every literal's variable is assigned
    in the cube and every literal evaluates false there.
    """
    for lit in clause:
        bit = cube[abs(lit) - 1]
        if bit is None:
            return False
        lit_true = bit if lit > 0 else not bit
        if lit_true:
            return False
    return True


@dataclass(frozen=True)
class Leaf:
    cube: Cube
    falsified_clause: int


@dataclass(frozen=True)
class Split:
    cube: Cube
    var: int  # zero-based variable index
    low: "Certificate"
    high: "Certificate"


Certificate = Leaf | Split


def _first_falsified_clause(cnf: CNF, cube: Cube) -> int | None:
    for i, clause in enumerate(cnf):
        if cube_falsifies_clause(cube, clause):
            return i
    return None


def _full_assignment(cube: Cube) -> Assignment | None:
    if any(bit is None for bit in cube):
        return None
    return tuple(bool(bit) for bit in cube)


def construct(cnf: CNF, cube: Cube | None = None) -> tuple[str, Assignment | Certificate]:
    """Return ('SAT', witness) or ('UNSAT', exact split certificate)."""
    n = variable_count(cnf)
    if cube is None:
        cube = (None,) * n
    if len(cube) != n:
        raise ValueError("cube length does not match formula variable count")

    bad = _first_falsified_clause(cnf, cube)
    if bad is not None:
        return "UNSAT", Leaf(cube=cube, falsified_clause=bad)

    full = _full_assignment(cube)
    if full is not None:
        if formula_value(cnf, full):
            return "SAT", full
        raise AssertionError("full non-satisfying assignment should falsify a clause")

    var = cube.index(None)
    low_cube = list(cube)
    low_cube[var] = False
    high_cube = list(cube)
    high_cube[var] = True

    low_status, low_obj = construct(cnf, tuple(low_cube))
    if low_status == "SAT":
        return low_status, low_obj
    high_status, high_obj = construct(cnf, tuple(high_cube))
    if high_status == "SAT":
        return high_status, high_obj

    return (
        "UNSAT",
        Split(
            cube=cube,
            var=var,
            low=low_obj,  # type: ignore[arg-type]
            high=high_obj,  # type: ignore[arg-type]
        ),
    )


def _child_cube(parent: Cube, var: int, value: bool) -> Cube:
    if not (0 <= var < len(parent)) or parent[var] is not None:
        raise ValueError("invalid split variable")
    out = list(parent)
    out[var] = value
    return tuple(out)


def verify_certificate(cnf: CNF, cert: Certificate, expected_cube: Cube | None = None) -> bool:
    """Independent structural checker for a DPLL/subcube rejection cover."""
    n = variable_count(cnf)
    if expected_cube is None:
        expected_cube = (None,) * n
    if cert.cube != expected_cube:
        return False

    if isinstance(cert, Leaf):
        i = cert.falsified_clause
        return 0 <= i < len(cnf) and cube_falsifies_clause(cert.cube, cnf[i])

    if not (0 <= cert.var < n) or cert.cube[cert.var] is not None:
        return False
    try:
        low_cube = _child_cube(cert.cube, cert.var, False)
        high_cube = _child_cube(cert.cube, cert.var, True)
    except ValueError:
        return False
    return verify_certificate(cnf, cert.low, low_cube) and verify_certificate(
        cnf, cert.high, high_cube
    )


def leaves(cert: Certificate) -> list[Leaf]:
    if isinstance(cert, Leaf):
        return [cert]
    return leaves(cert.low) + leaves(cert.high)


def verify_cover_by_enumeration(cnf: CNF, cert: Certificate) -> bool:
    """Finite diagnostic: enumerate assignment space and check cover + rejection."""
    n = variable_count(cnf)
    ls = leaves(cert)
    for bits in product((False, True), repeat=n):
        assignment = tuple(bits)
        covering = [leaf for leaf in ls if cube_extends(leaf.cube, assignment)]
        if not covering:
            return False
        if not any(
            cube_falsifies_clause(leaf.cube, cnf[leaf.falsified_clause])
            for leaf in covering
        ):
            return False
    return True


def verify_sat_witness(cnf: CNF, witness: Assignment) -> bool:
    return len(witness) == variable_count(cnf) and formula_value(cnf, witness)


def _corrupt_first_leaf(cert: Certificate, clause_count: int) -> Certificate:
    """Negative control: replace one valid leaf's clause index by an invalid one."""
    if isinstance(cert, Leaf):
        return Leaf(cert.cube, clause_count)
    return Split(cert.cube, cert.var, _corrupt_first_leaf(cert.low, clause_count), cert.high)


def run_fixture() -> dict:
    sat_status, sat_obj = construct(SAT_BASE)
    unsat_status, unsat_obj = construct(UNSAT_BASE)

    assert sat_status == "SAT"
    assert isinstance(sat_obj, tuple)
    assert verify_sat_witness(SAT_BASE, sat_obj)

    assert unsat_status == "UNSAT"
    assert isinstance(unsat_obj, (Leaf, Split))
    assert verify_certificate(UNSAT_BASE, unsat_obj)
    assert verify_cover_by_enumeration(UNSAT_BASE, unsat_obj)

    corrupted = _corrupt_first_leaf(unsat_obj, len(UNSAT_BASE))
    assert not verify_certificate(UNSAT_BASE, corrupted)

    return {
        "sat_witness": sat_obj,
        "unsat_leaf_count": len(leaves(unsat_obj)),
        "unsat_certificate_verified": True,
        "exhaustive_cover_verified": True,
        "corrupted_certificate_rejected": True,
        "tier": "finite_diagnostic",
        "scope": "DPLL/subcube completion only; no unrestricted SAT lower bound",
    }


if __name__ == "__main__":
    print(run_fixture())
